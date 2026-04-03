#!/usr/bin/env python3
"""
EcoCompute AI - Phi-3-mini Energy Efficiency Benchmark
======================================================
Purpose: Find the exact "crossover point" for quantization energy efficiency
Target Model: microsoft/Phi-3-mini-4k-instruct (3.8B parameters)

This fills the gap between:
- TinyLlama-1.1B (4-bit is 26% WORSE)
- Qwen2-1.5B (4-bit is 29% WORSE)  
- Qwen2-7B (4-bit is 11% BETTER)

Expected: Phi-3-mini (3.8B) should be near the crossover point
"""

import torch
import pynvml
import time
import threading
import pandas as pd
import re
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

torch.manual_seed(42)
torch.cuda.manual_seed_all(42)

# ==================== Configuration ====================
MODEL_ID = "./phi3-mini"  # Local path
MODEL_NAME = "Phi-3-mini-3.8B"
PROMPT = "Explain the importance of Green AI and sustainable machine learning in 200 words."
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
def run_benchmark(config_name, model_kwargs):
    print(f"\n🚀 {MODEL_NAME} | {config_name}")
    print("-" * 50)
    auditor = EnergyAuditor()
    
    print("   📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    print("   📥 Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, 
        device_map="auto", 
        trust_remote_code=True,
        **model_kwargs
    )
    
    # Get model memory footprint
    mem_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    mem_gb = mem_bytes / (1024**3)
    print(f"   📊 Model memory: {mem_gb:.2f} GB")
    
    inputs = tokenizer(PROMPT, return_tensors="pt").to("cuda")
    
    # Warmup
    print("   🔥 Warming up...")
    with torch.no_grad():
        _ = model.generate(**inputs, max_new_tokens=20, pad_token_id=tokenizer.eos_token_id)
    torch.cuda.synchronize()
    
    # Benchmark
    print(f"   ⏱️ Running {TEST_SAMPLES} samples...")
    auditor.start()
    start = time.time()
    total_tokens = 0
    
    with torch.no_grad():
        for i in range(TEST_SAMPLES):
            out = model.generate(
                **inputs, 
                max_new_tokens=MAX_NEW_TOKENS, 
                do_sample=True, 
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
            total_tokens += len(out[0]) - len(inputs['input_ids'][0])
            print(f"      Sample {i+1}/{TEST_SAMPLES} done")
    
    torch.cuda.synchronize()
    duration = time.time() - start
    joules, avg_w, peak_w = auditor.stop()
    
    # Cleanup
    del model
    torch.cuda.empty_cache()
    
    tps = total_tokens / duration if duration > 0 else 0
    jpk = (joules / total_tokens) * 1000 if total_tokens > 0 else 0
    latency_ms = 1000 / tps if tps > 0 else 0
    edp = jpk * (latency_ms / 1000)  # Energy-Delay Product
    
    print(f"\n   ✅ Results:")
    print(f"      Throughput:    {tps:.2f} tokens/sec")
    print(f"      Latency:       {latency_ms:.2f} ms/token")
    print(f"      Avg Power:     {avg_w:.2f} W")
    print(f"      Peak Power:    {peak_w:.2f} W")
    print(f"      Energy:        {jpk:.2f} J/1k tokens")
    print(f"      EDP:           {edp:.2f} J·s/1k tokens")
    
    return {
        "Model": MODEL_NAME,
        "Config": config_name,
        "Parameters": "3.8B",
        "Memory_GB": round(mem_gb, 2),
        "Tokens_per_sec": round(tps, 2),
        "Latency_ms": round(latency_ms, 2),
        "Avg_Watts": round(avg_w, 2),
        "Peak_Watts": round(peak_w, 2),
        "J_per_1k_Tokens": round(jpk, 2),
        "EDP": round(edp, 2)
    }

# ==================== Main ====================
if __name__ == "__main__":
    print("=" * 60)
    print("⚡ EcoCompute AI - Phi-3-mini Energy Benchmark")
    print("=" * 60)
    print("🎯 Goal: Find the quantization energy efficiency crossover point")
    print("=" * 60)
    
    gpu = get_gpu_info()
    print(f"\n📊 GPU: {gpu['name']} | {gpu['total_gb']} GB")
    print(f"📊 PyTorch: {torch.__version__}")
    print(f"📊 CUDA: {torch.version.cuda}")
    
    # Measure idle power
    print("\n📊 Measuring idle power...")
    idle = measure_idle_power()
    print(f"   Idle Power: {idle:.2f} W")
    
    results = []
    
    # Test 1: FP16
    print("\n" + "=" * 60)
    print("📌 TEST 1: FP16 (Baseline)")
    print("=" * 60)
    
    fp16_result = run_benchmark(
        "FP16",
        {"torch_dtype": torch.float16}
    )
    results.append(fp16_result)
    
    print(f"\n⏳ Cooling down for {COOLDOWN_SECONDS} seconds...")
    time.sleep(COOLDOWN_SECONDS)
    
    # Test 2: 4-bit NF4
    print("\n" + "=" * 60)
    print("📌 TEST 2: 4-bit NF4 (bitsandbytes)")
    print("=" * 60)
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4"
    )
    
    nf4_result = run_benchmark(
        "4-bit NF4",
        {"quantization_config": bnb_config}
    )
    results.append(nf4_result)
    
    # Create results DataFrame
    df = pd.DataFrame(results)
    
    # Analysis
    print("\n" + "=" * 60)
    print("📊 COMPARISON ANALYSIS")
    print("=" * 60)
    
    fp16_energy = fp16_result['J_per_1k_Tokens']
    nf4_energy = nf4_result['J_per_1k_Tokens']
    energy_change = ((nf4_energy - fp16_energy) / fp16_energy) * 100
    
    fp16_tps = fp16_result['Tokens_per_sec']
    nf4_tps = nf4_result['Tokens_per_sec']
    tps_change = ((nf4_tps - fp16_tps) / fp16_tps) * 100
    
    fp16_power = fp16_result['Avg_Watts']
    nf4_power = nf4_result['Avg_Watts']
    power_change = ((nf4_power - fp16_power) / fp16_power) * 100
    
    fp16_edp = fp16_result['EDP']
    nf4_edp = nf4_result['EDP']
    edp_change = ((nf4_edp - fp16_edp) / fp16_edp) * 100
    
    print(f"\n📈 Throughput Change:  {tps_change:+.1f}%")
    print(f"📈 Power Change:       {power_change:+.1f}%")
    print(f"📈 Energy Change:      {energy_change:+.1f}%")
    print(f"📈 EDP Change:         {edp_change:+.1f}%")
    
    print("\n" + "-" * 60)
    if energy_change < 0:
        print(f"✅ 4-bit quantization SAVES {abs(energy_change):.1f}% energy on Phi-3-mini!")
        print("   → Crossover point is BELOW 3.8B parameters")
    else:
        print(f"⚠️ 4-bit quantization INCREASES energy by {energy_change:.1f}% on Phi-3-mini!")
        print("   → Crossover point is ABOVE 3.8B parameters")
    print("-" * 60)
    
    # Context with previous results
    print("\n" + "=" * 60)
    print("📊 CROSSOVER POINT ANALYSIS (All Models)")
    print("=" * 60)
    print("""
| Model           | Params | 4-bit Energy Change | Status      |
|-----------------|--------|---------------------|-------------|
| TinyLlama       | 1.1B   | +26.5%              | ⚠️ Worse    |
| Qwen2           | 1.5B   | +29.4%              | ⚠️ Worse    |
| Phi-3-mini      | 3.8B   | {:+.1f}%              | {} |
| Qwen2           | 7B     | -11.4%              | ✅ Better   |
""".format(energy_change, "✅ Better" if energy_change < 0 else "⚠️ Worse"))
    
    # Save results
    gpu_safe = re.sub(r'[^\w]', '_', gpu['name'])
    filename = f"phi3_mini_benchmark_{gpu_safe}.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Results saved to {filename}")
    
    # Raw data table
    print("\n" + "=" * 60)
    print("📊 RAW DATA")
    print("=" * 60)
    print(df.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("🎉 Benchmark Complete!")
    print("=" * 60)
