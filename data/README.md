# EcoCompute AI ‚Ä?Benchmark Dataset

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18900289.svg)](https://doi.org/10.5281/zenodo.18900289)
[![GitHub Release](https://img.shields.io/github/v/release/hongping-zh/ecocompute-ai)](https://github.com/hongping-zh/ecocompute-ai/releases)

## üì• Quick Download

| File | Size | Description | Download |
|------|------|-------------|----------|
| **Complete Dataset** | ~2.5 MB | All benchmark data (metadata + raw results) | [üì¶ Download ZIP](https://github.com/hongping-zh/ecocompute-ai/releases/latest) |
| **Metadata (English)** | ~10 KB | Dataset documentation and core findings | [üìÑ Download](https://github.com/hongping-zh/ecocompute-ai/blob/main/data/QUANTIZATION_ENERGY_COMPLETE_DATASET_2026-03-06_EN.md) |
| **A800 Results** | ~500 KB | Large model benchmarks (7B-14B) | [üìÅ Browse](https://github.com/hongping-zh/ecocompute-ai/tree/main/data/a800_results) |

## üìä Dataset Overview

Systematic energy efficiency benchmarks for **NF4** and **INT8** quantization across small-to-medium language models (0.5B‚Ä?4B parameters) on multiple NVIDIA GPU architectures.

### Hardware Platforms

| GPU | Architecture | Memory | Bandwidth | Models Tested |
|-----|-------------|--------|-----------|---------------|
| **RTX 4090D** | Ada Lovelace | 24 GB GDDR6X | 1,008 GB/s | 0.5B‚Ä?B |
| **RTX 5090** | Blackwell | 32 GB GDDR7 | 1,792 GB/s | 0.5B‚Ä?B |
| **A800 80GB** | Ampere | 80 GB HBM2e | 2,039 GB/s | 7B‚Ä?4B |

### Models Covered

**Small Models (RTX 4090D/5090):**
- Qwen2-0.5B-Instruct (494M params)
- TinyLlama-1.1B-Chat-v1.0 (1.1B params)
- Qwen2-1.5B-Instruct (1.54B params)
- Qwen2.5-3B-Instruct (3.09B params)

**Large Models (A800 80GB):**
- Mistral-7B-v0.1 (7B params)
- Yi-1.5-9B (9B params)
- Qwen2.5-14B (14B params)

### Quantization Configurations

- **FP16** (baseline)
- **NF4** (4-bit NormalFloat via bitsandbytes)
- **INT8 Default** (`llm_int8_threshold=6.0`)
- **INT8 Pure** (`llm_int8_threshold=0.0`)
- **NF4 DQ** (NF4 with double quantization)

## üî¨ Key Findings

1. **Small-Model Quantization Paradox**: NF4 increases energy by 25‚Ä?6% for models <3B parameters, despite 75% memory reduction
2. **Parameter-Dependent Gradient**: Energy overhead decreases from +56% (0.5B) ‚Ü?+25% (3.0B)
3. **INT8 Inefficiency**: 4.6√ó worse than NF4 for small models (+142% vs +31% energy overhead)
4. **Cross-Generational Shift**: Break-even threshold shifts from 4.2B (Ada) to 5.2B (Blackwell)
5. **Large Model Efficiency**: NF4 achieves near-FP16 energy for 7B+ models with minimal perplexity degradation

## üìà Interactive Visualization

Explore the data interactively at: **https://hongping-zh.github.io/ecocompute-dynamic-eval/**

## üöÄ Quick Start

### Load Data in Python

```python
import pandas as pd

# Load metadata
url = "https://raw.githubusercontent.com/hongping-zh/ecocompute-ai/main/data/QUANTIZATION_ENERGY_COMPLETE_DATASET_2026-03-06_EN.md"
# Parse markdown tables or download CSV exports from dashboard

# Example: Filter NF4 results for small models
df = pd.read_csv("path/to/exported_data.csv")
nf4_small = df[(df['precision'] == 'NF4') & (df['params'] < 3)]
print(nf4_small[['model', 'energy_per_1k_tokens', 'delta_energy_pct']])
```

### Reproduce Benchmarks

```bash
git clone https://github.com/hongping-zh/ecocompute-ai.git
cd ecocompute-ai
pip install -r requirements.txt
python benchmark.py --model TinyLlama-1.1B --precision fp16 nf4 int8
```

## üìã Data Quality

- **Coefficient of Variation (CV)** < 2% for majority of measurements
- **Repeated trials**: n=2 independent runs for key configurations
- **Power monitoring**: NVML at 10 Hz, cross-validated against wall-power meter (r=0.94)
- **Statistical rigor**: Mean ¬± SD reported for all repeated experiments

## üìñ Citation

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

**For the research paper:**
```bibtex
@article{zhang2026quantization,
  author  = {Hongping Zhang},
  title   = {The Quantization Efficiency Paradox: A Systematic Review and Empirical Study 
             across NVIDIA Ada and Blackwell Architectures},
  journal = {arXiv preprint},
  year    = {2026},
  note    = {arXiv:XXXX.XXXXX}
}
```

## üìÑ License

This dataset is released under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**You are free to:**
- ‚ú?Share ‚Ä?copy and redistribute the material
- ‚ú?Adapt ‚Ä?remix, transform, and build upon the material
- ‚ú?Use for any purpose, including commercially

**Under the condition:**
- üìù **Attribution** ‚Ä?You must give appropriate credit and indicate if changes were made

## üîó Related Resources

- **Interactive Dashboard**: https://hongping-zh.github.io/ecocompute-dynamic-eval/
- **GitHub Repository**: https://github.com/hongping-zh/ecocompute-ai
- **Research Paper**: [Coming soon on arXiv]
- **HuggingFace Transformers Docs**: [Energy Efficiency Guide](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)

## üìß Contact

- **Author**: Hongping Zhang
- **GitHub**: [@hongping-zh](https://github.com/hongping-zh)
- **Issues**: [Report data issues](https://github.com/hongping-zh/ecocompute-ai/issues)

---

**Last Updated**: March 7, 2026 | **Version**: 1.0.0
