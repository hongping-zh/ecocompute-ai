# PR: Add EcoCompute AI Calculator to awesome-green-ai

## Target Repository
https://github.com/samuelrince/awesome-green-ai

## PR Title
`Add EcoCompute AI Calculator with RTX 5090 benchmark data`

## PR Description

### What is EcoCompute AI?

[EcoCompute AI Calculator](https://hongping-zh.github.io/ecocompute-ai/calculator/) is a free, open-source tool for estimating the carbon footprint of LLM training and inference.

**Key Features:**
- Real-time cost, time, and carbon footprint estimation
- Support for multiple GPU types (A100, H100, RTX 5090, etc.)
- **NEW**: Quantization selector with smart energy warnings
- Based on real benchmark data from RTX 5090 (Blackwell)

### Why Add This?

We conducted the **first public energy efficiency benchmark on RTX 5090** and discovered a significant finding:

> **4-bit quantization increases energy consumption by 26-29% for small models (<3B parameters)**

This challenges the common assumption that quantization always saves energy.

### Benchmark Data (RTX 5090)

| Model | FP16 Energy | 4-bit Energy | Change |
|-------|-------------|--------------|--------|
| TinyLlama-1.1B | 1659 J/1k tok | 2098 J/1k tok | **+26.5%** ⚠️ |
| Qwen2-1.5B | 2411 J/1k tok | 3120 J/1k tok | **+29.4%** ⚠️ |
| Qwen2-7B | 5509 J/1k tok | 4878 J/1k tok | **-11.4%** ✅ |

### Links

- **Calculator**: https://hongping-zh.github.io/ecocompute-ai/calculator/
- **GitHub**: https://github.com/hongping-zh/ecocompute-ai
- **Full Benchmark Report**: Available in repository

---

## Suggested Addition to README.md

### Location: Under "Calculation Tools" section

```markdown
- [EcoCompute AI Calculator](https://hongping-zh.github.io/ecocompute-ai/calculator/) - LLM carbon footprint calculator with real RTX 5090 benchmark data and quantization energy warnings.
```

### Alternative (with more detail):

```markdown
- [EcoCompute AI](https://github.com/hongping-zh/ecocompute-ai) - Open-source LLM carbon footprint calculator featuring:
  - Real-time training/inference cost estimation
  - RTX 5090 (Blackwell) energy benchmark data
  - Smart quantization warnings (4-bit increases energy for <3B models)
```

---

## Why This Fits awesome-green-ai

1. **Calculation Tool**: Directly fits the "Calculation Tools" category
2. **Novel Data**: First public RTX 5090 energy benchmarks
3. **Actionable Insights**: Quantization energy trade-offs
4. **Open Source**: MIT licensed, community-friendly
5. **Active Development**: Regular updates with new GPU data

---

## Checklist Before Submitting

- [ ] Fork `samuelrince/awesome-green-ai`
- [ ] Edit `README.md` to add EcoCompute AI under "Calculation Tools"
- [ ] Create PR with above description
- [ ] Wait for review

---

## Alternative PR Targets

| Repository | Fit | Notes |
|------------|-----|-------|
| **samuelrince/awesome-green-ai** | ⭐⭐⭐⭐⭐ | Best fit - Calculation Tools |
| **mlco2/impact** | ⭐⭐⭐ | Could add link to our benchmark data |
| **Green-Software-Foundation/awesome-green-software** | ⭐⭐⭐ | Broader scope, still relevant |

---

*Prepared for PR submission on January 30, 2026*
