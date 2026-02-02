#!/usr/bin/env python3
"""
Full Benchmark Suite Runner
===========================
This script runs the complete benchmark suite for all models and configurations.

Usage:
    python run_full_benchmark.py --output ../data/benchmark_results.csv

Requirements:
    pip install torch transformers bitsandbytes pynvml pandas numpy

Author: Hongping Zhang
License: MIT
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Models to benchmark
MODELS = [
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "Qwen/Qwen2-1.5B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2-7B-Instruct",
]

# Configurations to test
CONFIGS = ["fp16", "nf4"]

# Benchmark parameters
ITERATIONS = 10
WARMUP = 3
MAX_TOKENS = 512


def run_benchmark(model: str, config: str, output_file: str, idle_power: float = None):
    """Run benchmark for a single model/config combination."""
    cmd = [
        sys.executable,
        "energy_benchmark.py",
        "--model", model,
        "--config", config,
        "--iterations", str(ITERATIONS),
        "--warmup", str(WARMUP),
        "--max-tokens", str(MAX_TOKENS),
        "--output", output_file,
    ]
    
    if idle_power is not None:
        cmd.extend(["--idle-power", str(idle_power)])
    
    print(f"\n{'='*60}")
    print(f"Running: {model} ({config})")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run Full Benchmark Suite")
    parser.add_argument("--output", type=str, default="../data/full_benchmark_results.csv",
                        help="Output CSV file")
    parser.add_argument("--idle-power", type=float, default=None,
                        help="Pre-measured idle power (W)")
    parser.add_argument("--models", type=str, nargs="+", default=None,
                        help="Specific models to benchmark (default: all)")
    parser.add_argument("--configs", type=str, nargs="+", default=None,
                        help="Specific configs to test (default: all)")
    
    args = parser.parse_args()
    
    models = args.models if args.models else MODELS
    configs = args.configs if args.configs else CONFIGS
    
    print(f"\n{'#'*60}")
    print(f"# EcoCompute-AI Full Benchmark Suite")
    print(f"# Started: {datetime.now().isoformat()}")
    print(f"# Models: {len(models)}")
    print(f"# Configs: {len(configs)}")
    print(f"# Total runs: {len(models) * len(configs)}")
    print(f"{'#'*60}")
    
    successful = 0
    failed = 0
    
    for model in models:
        for config in configs:
            success = run_benchmark(model, config, args.output, args.idle_power)
            if success:
                successful += 1
            else:
                failed += 1
                print(f"WARNING: Benchmark failed for {model} ({config})")
    
    print(f"\n{'#'*60}")
    print(f"# Benchmark Complete")
    print(f"# Successful: {successful}")
    print(f"# Failed: {failed}")
    print(f"# Results saved to: {args.output}")
    print(f"{'#'*60}")


if __name__ == "__main__":
    main()
