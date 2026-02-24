# Perplexity (PPL) Accuracy Assessment Data

## Purpose

Measure accuracy impact of different INT8 quantization configurations to complement energy benchmarks.

## Key Finding

| Configuration | Perplexity | Δ vs FP16 | Energy Δ vs FP16 |
|---|---|---|---|
| FP16 (baseline) | 11.16 | — | — |
| INT8 Default (threshold=6.0) | 11.20 | **+0.33%** | +32.7% |
| INT8 Pure (threshold=0.0) | 14.00 | **+25.38%** | −3.1% |

**Conclusion:** Default INT8's energy overhead (+32.7%) is the cost of preserving accuracy (+0.33% PPL). Pure INT8 (threshold=0.0) is **not recommended** — marginal energy savings (−3.1%) do not justify the accuracy degradation (+25% PPL).

## Files

| File | Description |
|---|---|
| `ppl_yi1.5_6b_wikitext2_20260224.json` | Full results with metadata |
| `ppl_yi1.5_6b_wikitext2_20260224.csv` | Results in CSV format |
| `quick_ppl_test.py` | Test script (in `benchmarks/`) |

## Methodology

- **Model**: Yi-1.5-6B
- **Dataset**: WikiText-2 (test split, 50 samples, text > 100 chars)
- **Hardware**: RTX 4090D (AutoDL)
- **Evaluation**: Truncated to 512 tokens, cross-entropy loss averaged over all tokens
- **Date**: 2026-02-24

## Related

- **Energy benchmarks**: `rtx5090_benchmark_results.csv`, `t4_benchmark_results.csv`
- **GitHub Issue**: [bitsandbytes#1867](https://github.com/bitsandbytes-foundation/bitsandbytes/issues/1867)
- **Interactive dashboard**: [ecocompute-dynamic-eval](https://hongping-zh.github.io/ecocompute-dynamic-eval/)
