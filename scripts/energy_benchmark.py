#!/usr/bin/env python3
"""
Energy Benchmark Script for LLM Inference
==========================================
This script measures energy consumption of LLM inference with different quantization configurations.

Usage:
    python energy_benchmark.py --model "TinyLlama/TinyLlama-1.1B-Chat-v1.0" --config fp16
    python energy_benchmark.py --model "Qwen/Qwen2-1.5B-Instruct" --config nf4

Requirements:
    pip install torch transformers bitsandbytes pynvml pandas numpy

Author: Hongping Zhang
License: MIT
"""

import argparse
import time
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import numpy as np
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    print("Warning: pynvml not available. Power measurements will be disabled.")


class PowerMonitor:
    """NVML-based GPU power monitoring."""
    
    def __init__(self, device_index: int = 0, sampling_interval_ms: int = 100):
        self.device_index = device_index
        self.sampling_interval_ms = sampling_interval_ms
        self.power_readings: List[float] = []
        self.is_monitoring = False
        self._handle = None
        
        if NVML_AVAILABLE:
            pynvml.nvmlInit()
            self._handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
    
    def get_power(self) -> float:
        """Get current GPU power in watts."""
        if not NVML_AVAILABLE or self._handle is None:
            return 0.0
        power_mw = pynvml.nvmlDeviceGetPowerUsage(self._handle)
        return power_mw / 1000.0  # Convert mW to W
    
    def get_idle_power(self, duration_seconds: int = 10) -> float:
        """Measure idle power over specified duration."""
        readings = []
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            readings.append(self.get_power())
            time.sleep(self.sampling_interval_ms / 1000.0)
        return np.mean(readings) if readings else 0.0
    
    def start_monitoring(self):
        """Start power monitoring."""
        self.power_readings = []
        self.is_monitoring = True
    
    def record_power(self):
        """Record current power reading."""
        if self.is_monitoring:
            self.power_readings.append(self.get_power())
    
    def stop_monitoring(self) -> Tuple[float, float]:
        """Stop monitoring and return (mean_power, std_power)."""
        self.is_monitoring = False
        if not self.power_readings:
            return 0.0, 0.0
        return np.mean(self.power_readings), np.std(self.power_readings)
    
    def cleanup(self):
        """Cleanup NVML resources."""
        if NVML_AVAILABLE:
            pynvml.nvmlShutdown()


def load_model(model_name: str, config: str, device: str = "cuda") -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load model with specified quantization configuration."""
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    if config.lower() == "fp16":
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map=device,
            trust_remote_code=True
        )
    elif config.lower() == "nf4":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map=device,
            trust_remote_code=True
        )
    elif config.lower() == "int8":
        bnb_config = BitsAndBytesConfig(load_in_8bit=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map=device,
            trust_remote_code=True
        )
    else:
        raise ValueError(f"Unknown config: {config}. Supported: fp16, nf4, int8")
    
    model.eval()
    return model, tokenizer


def run_inference(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    max_new_tokens: int = 512
) -> Tuple[str, int, float]:
    """Run inference and return (output, num_tokens, elapsed_time)."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    torch.cuda.synchronize()
    start_time = time.perf_counter()
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id
        )
    
    torch.cuda.synchronize()
    elapsed_time = time.perf_counter() - start_time
    
    generated_tokens = outputs.shape[1] - inputs["input_ids"].shape[1]
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return output_text, generated_tokens, elapsed_time


def benchmark_model(
    model_name: str,
    config: str,
    num_iterations: int = 10,
    warmup_iterations: int = 3,
    max_new_tokens: int = 512,
    prompt: str = "Explain the concept of energy efficiency in computing:",
    idle_power: Optional[float] = None
) -> Dict:
    """Run complete benchmark for a model configuration."""
    
    print(f"\n{'='*60}")
    print(f"Benchmarking: {model_name} ({config})")
    print(f"{'='*60}")
    
    # Initialize power monitor
    power_monitor = PowerMonitor()
    
    # Measure idle power if not provided
    if idle_power is None:
        print("Measuring idle power (10 seconds)...")
        idle_power = power_monitor.get_idle_power(10)
        print(f"Idle power: {idle_power:.2f} W")
    
    # Load model
    print(f"Loading model...")
    model, tokenizer = load_model(model_name, config)
    
    # Thermal stabilization
    print("Thermal stabilization (30 seconds)...")
    time.sleep(30)
    
    # Warmup
    print(f"Running {warmup_iterations} warmup iterations...")
    for i in range(warmup_iterations):
        _, _, _ = run_inference(model, tokenizer, prompt, max_new_tokens)
        print(f"  Warmup {i+1}/{warmup_iterations} complete")
    
    # Benchmark iterations
    print(f"Running {num_iterations} benchmark iterations...")
    results = []
    
    for i in range(num_iterations):
        # Start power monitoring
        power_monitor.start_monitoring()
        
        # Run inference with power sampling
        start_time = time.perf_counter()
        _, num_tokens, elapsed_time = run_inference(model, tokenizer, prompt, max_new_tokens)
        
        # Sample power during inference
        while time.perf_counter() - start_time < elapsed_time:
            power_monitor.record_power()
            time.sleep(0.1)  # 10 Hz sampling
        
        mean_power, std_power = power_monitor.stop_monitoring()
        
        # Calculate metrics
        throughput = num_tokens / elapsed_time  # tokens/second
        energy_per_1k = (mean_power - idle_power) * elapsed_time / num_tokens * 1000  # J per 1k tokens
        
        results.append({
            "iteration": i + 1,
            "num_tokens": num_tokens,
            "elapsed_time": elapsed_time,
            "throughput": throughput,
            "mean_power": mean_power,
            "std_power": std_power,
            "energy_per_1k_tokens": energy_per_1k
        })
        
        print(f"  Iteration {i+1}/{num_iterations}: {throughput:.2f} tok/s, {mean_power:.2f} W, {energy_per_1k:.2f} J/1k tok")
    
    # Aggregate results
    df = pd.DataFrame(results)
    
    summary = {
        "model": model_name,
        "config": config,
        "throughput_mean": df["throughput"].mean(),
        "throughput_std": df["throughput"].std(),
        "power_mean": df["mean_power"].mean(),
        "power_std": df["mean_power"].std(),
        "energy_per_1k_tokens_mean": df["energy_per_1k_tokens"].mean(),
        "energy_per_1k_tokens_std": df["energy_per_1k_tokens"].std(),
        "idle_power": idle_power,
        "num_iterations": num_iterations,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\nSummary:")
    print(f"  Throughput: {summary['throughput_mean']:.2f} ± {summary['throughput_std']:.2f} tok/s")
    print(f"  Power: {summary['power_mean']:.2f} ± {summary['power_std']:.2f} W")
    print(f"  Energy: {summary['energy_per_1k_tokens_mean']:.2f} ± {summary['energy_per_1k_tokens_std']:.2f} J/1k tok")
    
    # Cleanup
    del model
    torch.cuda.empty_cache()
    power_monitor.cleanup()
    
    return summary, df


def main():
    parser = argparse.ArgumentParser(description="Energy Benchmark for LLM Inference")
    parser.add_argument("--model", type=str, required=True, help="Model name or path")
    parser.add_argument("--config", type=str, default="fp16", choices=["fp16", "nf4", "int8"],
                        help="Quantization configuration")
    parser.add_argument("--iterations", type=int, default=10, help="Number of benchmark iterations")
    parser.add_argument("--warmup", type=int, default=3, help="Number of warmup iterations")
    parser.add_argument("--max-tokens", type=int, default=512, help="Maximum new tokens to generate")
    parser.add_argument("--output", type=str, default="benchmark_results.csv", help="Output CSV file")
    parser.add_argument("--idle-power", type=float, default=None, help="Pre-measured idle power (W)")
    
    args = parser.parse_args()
    
    summary, detailed_results = benchmark_model(
        model_name=args.model,
        config=args.config,
        num_iterations=args.iterations,
        warmup_iterations=args.warmup,
        max_new_tokens=args.max_tokens,
        idle_power=args.idle_power
    )
    
    # Save results
    output_path = Path(args.output)
    
    # Append to CSV
    file_exists = output_path.exists()
    with open(output_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(summary)
    
    print(f"\nResults saved to {output_path}")
    
    # Save detailed results
    detailed_path = output_path.with_suffix(".detailed.csv")
    detailed_results.to_csv(detailed_path, index=False)
    print(f"Detailed results saved to {detailed_path}")


if __name__ == "__main__":
    main()
