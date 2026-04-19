# When Does Quantization Save Energy? - Research Summary

**Technical Report | April 19, 2026 | Hongping Zhang**

---

## 📋 Executive Summary

This study challenges the conventional wisdom that quantization always saves energy in large language model (LLM) inference. Through systematic empirical measurements across 360+ configurations on four GPU architectures (Turing, Ampere, Ada Lovelace, Blackwell), we discover a **quantization-energy crossover effect**: quantization actually **increases** energy consumption for models below a hardware-specific threshold (~3.4B parameters), while reducing energy for larger models.

**Key Finding**: The crossover threshold is **architecture-independent**, validated across NVIDIA Turing (Tesla T4), Ampere (RTX 4090D), Ada Lovelace (RTX 5090), and Ampere (A800 80GB) architectures.

---

## 🎯 Core Research Questions

### Primary Question
**When does quantization actually save energy in LLM inference?**

### Secondary Questions
1. How does the energy efficiency of quantization vary with model size?
2. Does this relationship hold across different GPU architectures?
3. What are the practical implications for LLM deployment?

---

## 🔬 Methodology

### Experimental Design

**Hardware Coverage**:
- Tesla T4 (Turing, 70W, 16GB)
- RTX 4090D (Ada Lovelace, 425W, 24GB)
- RTX 5090 (Blackwell, 575W, 32GB)
- A800 80GB (Ampere, 400W, 80GB)

**Model Coverage**:
- Model sizes: 0.5B to 14B parameters
- Architectures: Qwen2, TinyLlama, Mistral, Yi-1.5
- Precisions: FP16, NF4, INT8 (default), INT8 (pure bnb), FP8

**Measurement Protocol**:
- Power sampling: NVML API at 10Hz (100ms intervals)
- Warm-up: 3 iterations to stabilize GPU state
- Measurement: 10 independent runs per configuration
- Quality control: CV < 2% across all measurements
- Signal-to-noise ratio: 12:1 to 28:1

**Total Configurations**: 360+ experimental configurations

---

## 📊 Key Findings

### 1. The Quantization-Energy Crossover Effect

**Discovery**: Energy impact of quantization is **non-monotonic** with model size.

| Model Size Range | NF4 Energy Impact | INT8 Energy Impact |
|------------------|-------------------|-------------------|
| **< 3.4B params** | +25% to +55% (increase) | +30% to +60% (increase) |
| **3.4B - 5B params** | ±10% (neutral) | +15% to +25% (increase) |
| **> 5B params** | -15% to -23% (decrease) | +10% to +20% (increase) |

**Implication**: For small models (<3.4B), **FP16 is more energy-efficient** than quantization.

### 2. Architecture-Independent Crossover Threshold

**Validation**: The crossover threshold (~3.4B parameters for NF4) is consistent across:

- **Turing (Tesla T4)**: NF4 +27.7% energy vs FP16 for 3B model
- **Ada Lovelace (RTX 4090D)**: NF4 -8% to -35% energy for 6B-7B models
- **Blackwell (RTX 5090)**: NF4 +40% energy vs FP16 for 3B model
- **Ampere (A800)**: Consistent pattern observed

**Conclusion**: The crossover threshold is a **fundamental property** of the quantization-energy tradeoff, not architecture-specific.

### 3. INT8 is Consistently Worse Than NF4

**Finding**: INT8 quantization consistently underperforms NF4 in energy efficiency.

| Architecture | INT8 vs FP16 | NF4 vs FP16 |
|--------------|--------------|-------------|
| Tesla T4 (3B) | +34.5% | +27.7% |
| RTX 4090D (6B-7B) | +17% to +33% | -8% to -35% |
| RTX 5090 (3B) | +50% | +40% |

**Recommendation**: Avoid INT8 for energy efficiency; use NF4 instead.

### 4. FP8 Software Crisis

**Finding**: FP8 shows severe energy overhead due to software implementation immaturity.

| Architecture | FP8 vs FP16 |
|--------------|--------------|
| RTX 5090 (3B) | +701% |
| Tesla T4 (3B) | +79.5% |

**Cause**: Software dequantization overhead dominates potential hardware benefits.

### 5. Batch Size Optimization

**Finding**: Energy efficiency improves with larger batch sizes.

| Batch Size | Energy Reduction (FP16) |
|------------|--------------------------|
| BS=1 | Baseline |
| BS=8 | -23% |
| BS=16 | -28% |
| BS=32 | -32% |

**Recommendation**: Use batch size 16-32 for optimal energy efficiency.

---

## 🎯 Practical Recommendations

### For LLM Deployment

**< 3.4B Models**:
- ✅ Use FP16 (avoid quantization)
- ❌ Avoid NF4 (increases energy)
- ❌ Avoid INT8 (worse than NF4)
- ❌ Avoid FP8 (severe overhead)

**3.4B - 5B Models**:
- ⚠️ Evaluate case-by-case
- ⚠️ FP16 often better for energy
- ✅ Consider NF4 if memory constrained

**> 5B Models**:
- ✅ Use NF4 quantization
- ❌ Avoid INT8 (consistently worse)
- ❌ Avoid FP8 (severe overhead)

**General Best Practices**:
- Use batch size 16-32 for optimal efficiency
- Prioritize NF4 over INT8 for quantization
- Monitor actual energy consumption, don't assume

### For Benchmark Designers

**Recommendations for MLPerf and other benchmarks**:
1. **Report energy alongside performance** - throughput alone is misleading
2. **Include model size in metadata** - crossover threshold depends on it
3. **Document hardware generation** - energy behavior varies across architectures
4. **Consider energy-per-token metric** - more granular than system-level power
5. **Don't assume quantization = efficiency** - verify with measurements

---

## 📈 Impact & Validation

### Academic Validation
- **Hugging Face Integration**: Featured in [Hugging Face Optimum official documentation](https://huggingface.co/docs/optimum/concept_guides/quantization#energy-efficiency-in-practice) (PR #2410, merged March 2026)
- **MLCommons Power WG**: Invited discussion ([Issue #2558](https://github.com/mlcommons/inference/issues/2558))
- **Community Recognition**: FP8 energy anomaly confirmed by [torchao maintainers](https://github.com/pytorch/ao/issues/4094)

### Data Availability
- **Zenodo Dataset**: [DOI 10.5281/zenodo.19647290](https://doi.org/10.5281/zenodo.19647290) (v1.1.0)
- **GitHub Repository**: https://github.com/hongping-zh/ecocompute-ai
- **Interactive Dashboard**: https://hongping-zh.github.io/
- **Hugging Face Mirror**: https://huggingface.co/datasets/hongpingzhang/ecocompute-energy-efficiency

### Reproducibility
- **Raw Data**: All 360+ configurations publicly available
- **Measurement Scripts**: Open-source with NVML integration
- **Quality Metrics**: CV < 2%, SNR 12:1 to 28:1
- **Docker Environment**: Reproducible setup provided

---

## 🔮 Future Work

### Short Term
- Extend to AMD ROCm and Intel Level Zero
- Add training energy profiling
- Multi-GPU distributed inference

### Long Term
- System-level + GPU-level unified framework
- Real-time energy monitoring dashboard
- Integration with MLPerf official tooling

---

## 📚 Citation

If you use this research in your work, please cite:

```bibtex
@misc{zhang2026quantization,
  title={When Does Quantization Save Energy? An Empirical Study of the Energy-Efficiency Crossover Effect Across GPU Generations},
  author={Zhang, Hongping},
  year={2026},
  publisher={Zenodo},
  doi={10.5281/zenodo.19647290},
  url={https://doi.org/10.5281/zenodo.19647290},
  note={Featured in Hugging Face Optimum Documentation}
}
```

**APA Format**:
Zhang, H. (2026). *When Does Quantization Save Energy? An Empirical Study of the Energy-Efficiency Crossover Effect Across GPU Generations*. Zenodo. https://doi.org/10.5281/zenodo.19647290

---

## 📞 Contact & Collaboration

**Author**: Hongping Zhang  
**Email**: zhanghongping1982@gmail.com  
**Website**: https://hongping-zh.github.io/  
**GitHub**: https://github.com/hongping-zh/ecocompute-ai

**Open to Collaboration**:
- ✅ Academic research partnerships
- ✅ Industry validation studies
- ✅ Benchmark design consultations
- ✅ Open-source contributions

---

## 📄 Full Paper

The complete research paper is available at:
`When Does Quantization Save Energy An Empirical Study of the.pdf`

For data, code, and interactive visualizations, visit:
- **GitHub**: https://github.com/hongping-zh/ecocompute-ai
- **Zenodo**: https://doi.org/10.5281/zenodo.19647290
- **Dashboard**: https://hongping-zh.github.io/

---

**Last Updated**: April 19, 2026  
**Version**: Technical Report v1.0  
**Status**: Preprint - Under Review
