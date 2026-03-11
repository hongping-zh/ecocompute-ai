---
title: 'EcoCompute-AI: A Toolkit for Energy-Aware Profiling of Quantized Language Models'
tags:
  - Python
  - energy efficiency
  - quantization
  - language models
  - GPU profiling
  - Green AI
authors:
  - name: Hongping Zhang
    orcid: 0009-0000-2529-4613
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 8 March 2026
bibliography: paper.bib
---

# Summary

EcoCompute-AI is an open-source Python toolkit for measuring and analyzing the energy consumption of quantized language models on NVIDIA GPUs. As quantization techniques such as 4-bit NormalFloat (NF4) and 8-bit integer (INT8) become standard practice for deploying large language models, understanding their energy implications is critical for sustainable AI development. The toolkit provides automated energy profiling at 10 Hz via NVML, built-in statistical validation, and interactive visualization, enabling researchers and practitioners to make evidence-based decisions about quantization strategies. It has been validated through 93+ systematic measurements across 5 models (0.5B–7B parameters), 4 quantization methods, and 3 NVIDIA GPU architectures (Blackwell, Ada Lovelace, Ampere), revealing previously undocumented energy trade-offs in small-model quantization [@zhang2026quantization].

# Statement of Need

The promise of reduced memory footprint and faster inference has driven widespread adoption of model quantization, particularly 4-bit NormalFloat (NF4) and 8-bit integer (INT8) formats via libraries such as bitsandbytes [@dettmers2022bitsandbytes; @dettmers2023qlora]. However, current energy measurement techniques in machine learning remain limited:

1. **Coarse granularity**: Tools such as CodeCarbon [@codecarbon] and experiment-impact-tracker [@henderson2020towards] measure system-wide energy consumption but cannot isolate GPU-level costs for specific model configurations or quantization formats.

2. **Lack of quantization support**: There are no standardized energy benchmarks for quantized inference. MLPerf benchmarks [@reddi2020mlperf] report only throughput and latency.

3. **Low statistical rigor**: Most profiling tools report single-run results without confidence intervals or standardized protocols, making it difficult to distinguish signal from noise in energy comparisons.

4. **No cross-architecture analysis**: Existing solutions do not support systematic energy-efficiency comparisons across GPU generations (e.g., Ada Lovelace vs. Blackwell).

EcoCompute-AI addresses these gaps by providing a specialized toolkit for profiling quantized language models in a controlled and reproducible manner. The software enables researchers to:

- **Parameter-dependent scaling plots**: Visualize how energy efficiency scales with model size across quantization methods.
- **Precision comparison heatmaps**: Compare FP16, NF4, and INT8 energy profiles across multiple models in a single view.
- **Cross-architecture analysis**: Overlay results from different GPU generations to identify architecture-specific trade-offs.

An interactive dashboard is available at [https://hongping-zh.github.io/ecocompute-dynamic-eval/](https://hongping-zh.github.io/ecocompute-dynamic-eval/) and can also be deployed locally with custom datasets.

# Key Features

- **Automated profiling**: Single-command measurement of the energy of any Hugging Face model.
- **Statistical rigor**: Built-in support for repeated trials (n=10 default) with confidence intervals and coefficient of variation reporting.
- **Quantization-aware**: Native support for NF4 (via bitsandbytes) and INT8 formats, including pure vs. mixed-precision INT8.
- **Cross-platform**: Supports NVIDIA GPUs with NVML (Volta, Turing, Ampere, Ada, Blackwell).
- **Reproducible**: Docker image and documented protocol ensure identical results across environments.
- **Extensible**: Modular architecture allows straightforward addition of new hardware platforms and quantization methods.

# Usage Example

A minimal example of profiling a quantized model:

```python
from ecocompute import EnergyProfiler, compare_precisions

# Profile a single model-precision combination
profiler = EnergyProfiler(
    model_name="Qwen/Qwen2-1.5B",
    precision="nf4",
    device="cuda:0"
)
results = profiler.run()

print(f"Throughput: {results['throughput']:.2f} tokens/s")
print(f"Energy: {results['energy']:.0f} J/1k tokens")
print(f"CV: {results['cv_percent']:.1f}%")

# Compare all precision modes
comparison = compare_precisions(
    model_name="Qwen/Qwen2-1.5B",
    precisions=["fp16", "nf4", "int8"],
    num_trials=2
)

# Export results
comparison.to_csv("qwen2_1.5b_comparison.csv")
```

For advanced usage, such as custom workloads and batch-size sweeps, refer to the [documentation](https://github.com/hongping-zh/ecocompute-ai/blob/main/README.md).

# Community Impact

EcoCompute-AI serves multiple research communities:

1. **Green AI researchers**: Provides standardized energy metrics for assessing the environmental impact of quantization methods.
2. **Model developers**: Enables data-driven decisions about precision trade-offs during deployment.
3. **Hardware architects**: Supplies empirical data to inform the design of energy-efficient inference accelerators.
4. **Educators**: Offers ready-made materials for teaching sustainable machine learning practices.

Using the toolkit, we have generated a dataset of 93+ measurements covering 5 models, 4 quantization methods, and 3 GPU architectures. The dataset is publicly available on the [Hugging Face Hub](https://huggingface.co/datasets/hongpingzhang/ecocompute-energy-efficiency) and archived on [Zenodo](https://zenodo.org/records/18900289). The accompanying research paper is available on arXiv [@zhang2026quantization].

# Comparison with Existing Tools

| Feature | EcoCompute-AI | CodeCarbon | MLPerf | experiment-impact-tracker |
|---------|---------------|------------|--------|---------------------------|
| GPU-specific profiling | ✓ | ✗ | ✓ | ✗ |
| Quantization support | ✓ | ✗ | ✗ | ✗ |
| Statistical validation | ✓ | ✗ | ✗ | ✗ |
| Per-token metrics | ✓ | ✗ | ✗ | ✗ |
| Interactive dashboard | ✓ | ✗ | ✗ | ✗ |

# Future Directions

Planned improvements include:

- Support for AMD GPUs via ROCm.
- Integration with MLflow for experiment tracking.
- Automated energy-optimal hyperparameter tuning.
- Extension to encoder-decoder and mixture-of-experts architectures.

# Acknowledgements

We thank the developers of bitsandbytes, Hugging Face Transformers, and the NVIDIA NVML library, whose tools made this work possible. We also thank the open-source community for their feedback during development.

# References
