# Analysis and Benchmark Scripts

This directory contains Python scripts for running benchmarks and analyzing results.

## Scripts

### `energy_benchmark.py`
Main benchmarking script for measuring LLM inference energy consumption.

**Usage:**
```bash
python energy_benchmark.py \
    --model "Qwen/Qwen2-1.5B-Instruct" \
    --config nf4 \
    --iterations 10 \
    --warmup 3 \
    --max-tokens 512 \
    --output results.csv
```

**Arguments:**
- `--model`: Hugging Face model name or local path
- `--config`: Quantization config (fp16, nf4, int8)
- `--iterations`: Number of benchmark iterations (default: 10)
- `--warmup`: Number of warmup iterations (default: 3)
- `--max-tokens`: Maximum tokens to generate (default: 512)
- `--output`: Output CSV file path
- `--idle-power`: Pre-measured idle power in Watts (optional)

### `analyze_results.py`
Results analysis and visualization script.

**Usage:**
```bash
python analyze_results.py \
    --data ../data/rtx5090_benchmark_results.csv \
    --output ../figures/
```

**Outputs:**
- `fig1_energy_comparison.pdf/png`: Energy comparison bar chart
- `fig2_energy_trend.pdf/png`: Energy trend with model size
- `fig3_power_throughput.pdf/png`: Power and throughput comparison
- `table_results.tex`: LaTeX table for paper

### `roofline_analysis.py`
Theoretical framework implementation using Roofline model.

**Usage:**
```bash
# Basic analysis
python roofline_analysis.py --gpu rtx5090 --model qwen2-1.5b

# With detailed case study
python roofline_analysis.py --gpu rtx5090 --model qwen2-1.5b --case-study
```

**Features:**
- Arithmetic intensity calculation
- De-quantization overhead estimation
- Crossover point prediction
- Multi-GPU comparison visualization

### `run_full_benchmark.py`
Automated full benchmark suite runner.

**Usage:**
```bash
# Run all models and configs
python run_full_benchmark.py --output ../data/full_results.csv

# Run specific models
python run_full_benchmark.py \
    --models "Qwen/Qwen2-1.5B-Instruct" "Qwen/Qwen2-7B-Instruct" \
    --configs fp16 nf4
```

## Requirements

```
torch>=2.0.0
transformers>=4.35.0
bitsandbytes>=0.41.0
pynvml>=11.0.0
pandas>=1.5.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
```

## Notes

- NVML (pynvml) is required for power measurements
- CUDA-capable GPU required for benchmarks
- Sufficient VRAM needed for FP16 models (varies by model size)
- Thermal stabilization period recommended before measurements
