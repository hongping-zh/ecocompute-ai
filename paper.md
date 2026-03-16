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

<<<<<<< HEAD
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
=======
EcoCompute-AI is an open-source Python toolkit for measuring and analyzing the energy consumption of quantized language models on NVIDIA GPUs. As quantization techniques (4-bit NormalFloat, 8-bit integer) become standard practice for deploying large language models, understanding their energy implications is critical for sustainable AI development. This toolkit provides automated energy profiling, statistical validation, and interactive visualization capabilities, enabling researchers and practitioners to make evidence-based decisions about quantization strategies. The software has been validated through systematic benchmarking of models ranging from 0.5B to 3B parameters on NVIDIA Ada Lovelace and Blackwell architectures, revealing previously undocumented energy trade-offs in small-model quantization [@zhang2026quantization].

# Statement of Need

The ability to achieve expected memory footprint and faster inference speed has led to the adoption of model quantization and in particular 4-bit NormalFloat (NF4) and 8-bit integer (INT8) formats, which have become widely used throughout through the use of libraries such as bitsandbytes [@dettmers2022bitsandbytes; @dettmers2023qlora]. Current energy measurement techniques in machine learning processes are, however, very limited:

1. **Coarse granularity**: Coarse granularity tools, such as CodeCarbon [@codecarbon] or experiment-impact-tracker [@henderson2020towards], quantify the energy used by the system as a whole, and they are not able to break down the consumption of specific models or specific precisions of the model (specifically, GPU).

2. **Lack of quantization support**: Lack of standardized energy measures of quantized inference. MLPerf benchmarks [@reddi2020mlperf] only present throughput and latency measurements.

3. **Low statistical rigor**: Most profiling instruments have single-run results with no confidence interval and no reproducible protocols that prevent it being easy to tell signal and noise in the energy comparison.

4. **No cross-architecture analysis**: Solutions on the market do not support a systematic comparison of energy efficiency between the GPU generations (e.g. Ada Lovelace and Blackwell).

EcoCompute-AI tries to fill these gaps by offering a highly specialized set of tools to profile the quantized language models in controlled and reproducible manner with an energy factor. The software allows the researcher to:

- **Parameter-dependent gradient plots**: Plots of gradient with parameter changes across model size systematically.
- **Precision comparison heatmaps**: Comparative heatmaps on precisions of FP16, NF4, and INT8 in as many models as possible.
- **Cross-architecture analysis**: The overlay of various generations of GPUs.

The dashboard is installed at the following location [https://hongping-zh.github.io/ecocompute-dynamic-eval/](https://hongping-zh.github.io/ecocompute-dynamic-eval/) and may be applied locally to use custom datasets.
>>>>>>> 7da007bcb1f87f31237b0c806f8781b40e0bef1d

# Key Features

- **Automated profiling**: Single-command measurement of the energy of any Hugging Face model.
<<<<<<< HEAD
- **Statistical rigor**: Built-in support for repeated trials (n=10 default) with confidence intervals and coefficient of variation reporting.
- **Quantization-aware**: Native support for NF4 (via bitsandbytes) and INT8 formats, including pure vs. mixed-precision INT8.
- **Cross-platform**: Supports NVIDIA GPUs with NVML (Volta, Turing, Ampere, Ada, Blackwell).
- **Reproducible**: Docker image and documented protocol ensure identical results across environments.
- **Extensible**: Modular architecture allows straightforward addition of new hardware platforms and quantization methods.

# Usage Example

A minimal example of profiling a quantized model:
=======
- **Statistical rigor**: Built-in support on repeated trials and quantification of uncertainty.
- **Quantization-aware**: Native support of NF4 (through bitsandbytes) and INT8 formats.
- **Cross-platform**: Supports NVIDIA GPUs with NVML (Volta, Turing, Ampere, Ada, Blackwell).
- **Reproducible**: Docker image and described protocol means that one can produce identical results in either environment.
- **Extensible**: Modular architecture enables effortlessly incorporation of novel compute or hardware platforms as well as additional quantification theories.

# Usage Example

The simplest model of a profiled quantized model:
>>>>>>> 7da007bcb1f87f31237b0c806f8781b40e0bef1d

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

<<<<<<< HEAD
EcoCompute-AI serves multiple research communities:

1. **Green AI researchers**: Provides standardized energy metrics for assessing the environmental impact of quantization methods.
2. **Model developers**: Enables data-driven decisions about precision trade-offs during deployment.
3. **Hardware architects**: Supplies empirical data to inform the design of energy-efficient inference accelerators.
4. **Educators**: Offers ready-made materials for teaching sustainable machine learning practices.

Using the toolkit, we have generated a dataset of 93+ measurements covering 5 models, 4 quantization methods, and 3 GPU architectures. The dataset is publicly available on the [Hugging Face Hub](https://huggingface.co/datasets/hongpingzhang/ecocompute-energy-efficiency) and archived on [Zenodo](https://zenodo.org/records/18900289). The accompanying research paper is available on arXiv [@zhang2026quantization].
=======
The EcoCompute-AI can be used by many research communities:

1. **Green AI researchers**: Reporters give standardized measures to assess the environmental effect of quantization methods.
2. **Model developers**: Allows making decisions that are driven by data regarding precision trade-offs on deployment.
3. **Hardware architects**: Provides empirical information to work how to design inference accelerator that is energy efficient.
4. **Educators**: Educators can use these materials to instruct students on sustainable machine learning.

A dataset of more than 200 individual measurements has already been generated with the toolkit evaluating 12 model-precision combinations on two different GPU architectures, and therefore benchmarking them. The research paper that was presented together with the study is now accessible in arXiv [@zhang2026quantization], and the raw data can be accessed publicly in the GitHub repository.
>>>>>>> 7da007bcb1f87f31237b0c806f8781b40e0bef1d

# Comparison with Existing Tools

| Feature | EcoCompute-AI | CodeCarbon | MLPerf | experiment-impact-tracker |
|---------|---------------|------------|--------|---------------------------|
| GPU-specific profiling | ✓ | ✗ | ✓ | ✗ |
| Quantization support | ✓ | ✗ | ✗ | ✗ |
| Statistical validation | ✓ | ✗ | ✗ | ✗ |
| Per-token metrics | ✓ | ✗ | ✗ | ✗ |
| Interactive dashboard | ✓ | ✗ | ✗ | ✗ |

# Future Directions

<<<<<<< HEAD
Planned improvements include:

- Support for AMD GPUs via ROCm.
- Integration with MLflow for experiment tracking.
- Automated energy-optimal hyperparameter tuning.
- Extension to encoder-decoder and mixture-of-experts architectures.

# Acknowledgements

We thank the developers of bitsandbytes, Hugging Face Transformers, and the NVIDIA NVML library, whose tools made this work possible. We also thank the open-source community for their feedback during development.
=======
Proposed improvements will involve:

- Support for AMD GPUs (via ROCm)
- MLflow experiment tracking by integration.
- Automated energy-optimal hyperparameter tuning.
- Extensions to the encoder-decoder and mix of experts designs.

# Acknowledgements

Much of this would not have been possible without the tools developed by the designers behind the bitsandbytes and Hugging Face Transformers, and the creators of the NVIDIA NVML. We also embrace the open-source community to get a response to development.
>>>>>>> 7da007bcb1f87f31237b0c806f8781b40e0bef1d

# References
