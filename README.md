# EcoCompute — LLM Energy Efficiency Benchmark & Advisor

<p align="center">
  <a href="https://clawhub.ai/hongping-zh/ecocompute">
    <img src="https://img.shields.io/badge/Try%20it%20now-EcoLobster%20Advisor-brightgreen?style=for-the-badge&logo=lighthouse" alt="Try EcoCompute on ClawHub"/>
  </a>
  <a href="https://zenodo.org/records/19647290">
    <img src="https://img.shields.io/badge/Dataset-Zenodo%20v1.1.0-blue?style=for-the-badge&logo=zenodo" alt="Zenodo Dataset"/>
  </a>
  <a href="https://huggingface.co/datasets/hongpingzhang/ecocompute-energy-efficiency">
    <img src="https://img.shields.io/badge/HF%20Dataset-EcoCompute-yellow?style=for-the-badge&logo=huggingface" alt="HuggingFace Dataset"/>
  </a>
  <a href="https://hongping-zh.github.io/ecocompute-dynamic-eval/">
    <img src="https://img.shields.io/badge/Dashboard-Live-ff69b4?style=for-the-badge" alt="Live Dashboard"/>
  </a>
  <a href="https://huggingface.co/docs/optimum/concept_guides/quantization">
    <img src="https://img.shields.io/badge/Referenced%20by-HF%20Optimum-orange?style=for-the-badge" alt="HF Optimum"/>
  </a>
</p>

<p align="center">
  <b>When does quantization save energy?</b><br/>
  A systematic empirical study of LLM quantization energy efficiency across 4 GPU architectures and 360+ measured configurations.
</p>

<p align="center">
  <a href="https://clawhub.ai/hongping-zh/ecocompute"><b>🦞 Try the interactive advisor (EcoLobster) →</b></a>
</p>

---

## Quick Findings

- **Crossover threshold is architecture-dependent**: NF4 saves energy only above 4.2B (Ada) / 5.2B (Blackwell) / 3.4B (Turing) parameters.
- **INT8 default is a trap**: `load_in_8bit=True` increases energy by 17–147% vs FP16. Fix: set `llm_int8_threshold=0.0`.
- **FP8 paradox**: torchao FP8 on Blackwell shows +158% to +701% energy overhead vs FP16 (confirmed by upstream maintainers).
- **Batch size matters most**: BS=1→64 reduces energy/request by 95.7% on A800.n helps make AI more sustainable.
