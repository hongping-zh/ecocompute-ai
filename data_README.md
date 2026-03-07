# EcoCompute AI — Benchmark Data

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Overview

This directory contains the complete benchmark dataset for the **EcoCompute** project — a systematic study of energy efficiency implications of quantization (NF4, INT8) for small language models (0.5B–14B parameters) across multiple NVIDIA GPU architectures.

## Dataset Contents

| File | Description |
|------|-------------|
| `QUANTIZATION_ENERGY_COMPLETE_DATASET_2026-03-06.md` | Complete dataset metadata: experimental configurations, raw measurements, core findings, and data quality assessment |
| `a800_results/` | Large model benchmark data (7B–14B): Mistral-7B, Yi-1.5-9B, Qwen2.5-14B on NVIDIA A800 80GB |

## Hardware Platforms

| GPU | Architecture | Memory | Bandwidth | Models Tested |
|-----|-------------|--------|-----------|---------------|
| RTX 4090D | Ada Lovelace | 24 GB GDDR6X | 1,008 GB/s | 0.5B–3B |
| RTX 5090 | Blackwell | 32 GB GDDR7 | 1,792 GB/s | 0.5B–3B |
| A800 80GB | Ampere | 80 GB HBM2e | 2,039 GB/s | 7B–14B |

## Key Findings

1. **Small-Model Quantization Paradox**: NF4 quantization increases energy by 25–56% for models under 3B parameters, despite 75% memory reduction
2. **Parameter-Dependent Gradient**: Energy overhead decreases from +56% (0.5B) to +25% (3.0B)
3. **INT8 Inefficiency**: 4.6× worse than NF4 for small models (+142% vs +31%)
4. **Cross-Generational Shift**: Break-even threshold shifts from 4.2B (Ada) to 5.2B (Blackwell)
5. **Large Model Efficiency**: NF4 achieves near-FP16 energy for 7B+ models with minimal perplexity degradation

## Data Quality

- Coefficient of Variation (CV) < 2% for majority of measurements
- n=2 independent runs for key configurations
- NVML power sampling at 10 Hz, cross-validated against wall-power meter (r=0.94)

## Interactive Dashboard

Explore the data interactively at:
**https://hongping-zh.github.io/ecocompute-dynamic-eval/**

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{zhang2026ecocompute,
  author       = {Hongping Zhang},
  title        = {EcoCompute: Energy Efficiency Benchmark for Quantized Language Models},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/hongping-zh/ecocompute-ai}},
  note         = {Benchmark dataset covering NF4/INT8 quantization energy efficiency
                  across NVIDIA Ada Lovelace, Blackwell, and Ampere architectures}
}
```

## License

This dataset is released under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt this data for any purpose, provided you give appropriate credit.

## Contact

- **Author**: Hongping Zhang
- **GitHub**: [@hongping-zh](https://github.com/hongping-zh)
- **Repository**: https://github.com/hongping-zh/ecocompute-ai
