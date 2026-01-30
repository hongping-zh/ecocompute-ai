# RTX 5090 Energy Benchmark Data

This directory contains the benchmark scripts and results from our RTX 5090 energy efficiency experiments.

## Key Finding: The Quantization Efficiency Paradox

4-bit NF4 quantization **increases** energy consumption for models < 5B parameters on RTX 5090.

| Model | Parameters | FP16 (J/1k tokens) | NF4 (J/1k tokens) | Δ Energy |
|-------|------------|-------------------|-------------------|----------|
| TinyLlama | 1.1B | 1,659 | 2,098 | +26.5% |
| Qwen2 | 1.5B | 2,411 | 3,120 | +29.4% |
| Qwen2.5 | 3B | 3,383 | 3,780 | +11.7% |
| Qwen2 | 7B | 5,509 | 4,878 | **-11.4%** |

## Hardware

- GPU: NVIDIA GeForce RTX 5090 (Blackwell, sm_120)
- VRAM: 32 GB GDDR7
- TDP: 575 W
- PyTorch: 2.10.0+cu128
- CUDA: 12.8

## Scripts

- `bench_phi3_mini.py` - Benchmark script for Phi-3-mini
- `bench_power_limit.py` - Power limit experiment script

## Dataset

Full benchmark data available on Hugging Face:
https://huggingface.co/datasets/hongpingzhang/rtx5090-energy-benchmark
