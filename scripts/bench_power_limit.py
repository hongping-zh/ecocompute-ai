#!/usr/bin/env python3
"""
EcoCompute AI - Power-Limited Energy Efficiency Experiment
==========================================================
This script tests the "Energy Efficiency Crossover Point" hypothesis:
Does limiting GPU power change when 4-bit quantization becomes beneficial?

Experiment Design:
- Run benchmarks at multiple power limits (575W, 300W, 150W)
- Compare FP16 vs 4-bit NF4 at each power level
- Observe if the "crossover point" shifts with power constraints
"""

import torch
import pynvml
import time
import threading
import pandas as pd
import subprocess
import re
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

torch.manual_seed(42)
torch.cuda.manual_seed_all(42)

# ==================== Configuration ====================
POWER_LIMITS = [None, 300, 150]  # None = default (no limit), then 300W, 150W
MODELS = [
    ("TinyLlama/TinyLlama-1.1B-Chat-v1.0", "TinyLlama-1.1B"),
    ("Qwen/Qwen2-7B", "Qwen2-7B")
]
PROMPT = "Explain the importance of Green AI in 200 words."
MAX_NEW_TOKENS = 256
TEST_SAMPLES = 10
COOLDOWN_SECONDS = 15

# ==================== Energy Auditor ====================
class EnergyAuditor:
    def __init__(self, gpu_index=0, interval=0.1):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
        name = pynvml.nvmlDeviceGetName(self.handle)
        self.gpu_name = name.decode('utf-8') if isinstance(name, bytes) else name
        self.interval = interval
        self.measurements = []
        self.is_monitoring = False

    def _sample(self):
        while self.is_monitoring:
            power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0
            self.measurements.append({"t": time.time(), "p": power})
            time.sleep(self.interval)

    def start(self):
        self.measurements = []
        self.is_monitoring = True
        self.thread = threading.Thread(target=self._sample, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_monitoring = False
        self.thread.join(timeout=2.0)
        if len(self.measurements) < 2:
            return 0, 0, 0
        df = pd.DataFrame(self.measurements)
        df['dt'] = df['t'].diff().fillna(0)
        df['p_avg'] = (df['p'] + df['p'].shift(1).fillna(df['p'].iloc[0])) / 2
        total_joules = (df['p_avg'] * df['dt']).sum()
        return total_joules, df['p'].mean(), df['p'].max()

# ==================== Power Limit Control ====================
def get_default_power_limit():
    """Get the default power limit of the GPU"""
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    # Get default power limit in milliwatts
    default_limit = pynvml.nvmlDeviceGetPowerManagementDefaultLimit(handle)
    return default_limit // 1000  # Convert to watts

def set_power_limit(watts):
    """Set GPU power limit using nvidia-smi"""
    if watts is None:
        watts = get_default_power_limit()
    try:
        result = subprocess.run(
            ['nvidia-smi', '-pl', str(watts)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"   ✅ Power limit set to {watts}W")
            return True
        else:
            print(f"   ⚠️ Failed to set power limit: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ⚠️ Error setting power limit: {e}")
        return False

def get_current_power_limit():
    """Get current power limit"""
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle)
    return limit // 1000

# ==================== GPU Info ====================
def get_gpu_info():
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    name = pynvml.nvmlDeviceGetName(handle)
    name = name.decode('utf-8') if isinstance(name, bytes) else name
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return {"name": name, "total_gb": round(mem.total/(1024**3), 2)}

def measure_idle_power(duration=5):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    readings = []
    for _ in range(int(duration / 0.1)):
        readings.append(pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0)
        time.sleep(0.1)
    return sum(readings) / len(readings)

# ==================== Benchmark ====================
def run_benchmark(model_id, model_name, config_name, model_kwargs, power_limit):
    print(f"\n   🚀 {model_name} | {config_name}")
    auditor = EnergyAuditor()
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_id, device_map="auto", **model_kwargs
    )
    
    inputs = tokenizer(PROMPT, return_tensors="pt").to("cuda")
    
    # Warmup
    with torch.no_grad():
        _ = model.generate(**inputs, max_new_tokens=20)
    torch.cuda.synchronize()
    
    # Benchmark
    auditor.start()
    start = time.time()
    total_tokens = 0
    
    with torch.no_grad():
        for i in range(TEST_SAMPLES):
            out = model.generate(
                **inputs, 
                max_new_tokens=MAX_NEW_TOKENS, 
                do_sample=True, 
                temperature=0.7
            )
            total_tokens += len(out[0]) - len(inputs['input_ids'][0])
    
    torch.cuda.synchronize()
    duration = time.time() - start
    joules, avg_w, peak_w = auditor.stop()
    
    # Cleanup
    del model
    torch.cuda.empty_cache()
    
    tps = total_tokens / duration if duration > 0 else 0
    jpk = (joules / total_tokens) * 1000 if total_tokens > 0 else 0
    
    print(f"      ✅ {tps:.2f} tok/s | {avg_w:.2f}W avg | {jpk:.2f} J/1k tokens")
    
    return {
        "Power_Limit": f"{power_limit}W" if power_limit else "Default",
        "Model": model_name,
        "Config": config_name,
        "Tokens/sec": round(tps, 2),
        "Avg_Watts": round(avg_w, 2),
        "Peak_Watts": round(peak_w, 2),
        "J/1k_Tokens": round(jpk, 2)
    }

# ==================== Main ====================
if __name__ == "__main__":
    print("=" * 60)
    print("⚡ EcoCompute AI - Power-Limited Efficiency Experiment")
    print("=" * 60)
    
    gpu = get_gpu_info()
    default_power = get_default_power_limit()
    
    print(f"\n📊 GPU: {gpu['name']} | {gpu['total_gb']} GB")
    print(f"📊 Default Power Limit: {default_power}W")
    print(f"📊 PyTorch: {torch.__version__}")
    
    all_results = []
    
    for power_limit in POWER_LIMITS:
        print("\n" + "=" * 60)
        if power_limit is None:
            print(f"🔋 Testing at DEFAULT Power ({default_power}W)")
            actual_limit = default_power
        else:
            print(f"🔋 Testing at {power_limit}W Power Limit")
            actual_limit = power_limit
        print("=" * 60)
        
        # Set power limit
        set_power_limit(power_limit if power_limit else default_power)
        time.sleep(5)  # Wait for power to stabilize
        
        # Measure idle power at this limit
        idle = measure_idle_power()
        print(f"   📊 Idle Power: {idle:.2f}W")
        
        for model_id, model_name in MODELS:
            # FP16 test
            result = run_benchmark(
                model_id, model_name, "FP16",
                {"torch_dtype": torch.float16},
                actual_limit
            )
            all_results.append(result)
            
            print(f"   ⏳ Cooling {COOLDOWN_SECONDS}s...")
            time.sleep(COOLDOWN_SECONDS)
            
            # 4-bit test
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4"
            )
            result = run_benchmark(
                model_id, model_name, "4-bit NF4",
                {"quantization_config": bnb_config},
                actual_limit
            )
            all_results.append(result)
            
            print(f"   ⏳ Cooling {COOLDOWN_SECONDS}s...")
            time.sleep(COOLDOWN_SECONDS)
    
    # Restore default power limit
    print("\n🔄 Restoring default power limit...")
    set_power_limit(default_power)
    
    # Create results DataFrame
    df = pd.DataFrame(all_results)
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 COMPLETE RESULTS - Power-Limited Experiment")
    print("=" * 60)
    print(df.to_string(index=False))
    
    # Calculate energy savings for each power level
    print("\n" + "=" * 60)
    print("📈 ENERGY EFFICIENCY ANALYSIS")
    print("=" * 60)
    
    for pl in df['Power_Limit'].unique():
        print(f"\n🔋 Power Limit: {pl}")
        pl_data = df[df['Power_Limit'] == pl]
        
        for model in pl_data['Model'].unique():
            model_data = pl_data[pl_data['Model'] == model]
            fp16_energy = model_data[model_data['Config'] == 'FP16']['J/1k_Tokens'].values[0]
            nf4_energy = model_data[model_data['Config'] == '4-bit NF4']['J/1k_Tokens'].values[0]
            savings = ((fp16_energy - nf4_energy) / fp16_energy) * 100
            
            emoji = "✅" if savings > 0 else "⚠️"
            print(f"   {emoji} {model}: {savings:+.1f}% energy {'saved' if savings > 0 else 'increase'} with 4-bit")
    
    # Save results
    gpu_safe = re.sub(r'[^\w]', '_', gpu['name'])
    filename = f"power_limit_experiment_{gpu_safe}.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Results saved to {filename}")
    
    print("\n" + "=" * 60)
    print("🎉 Experiment Complete!")
    print("=" * 60)
