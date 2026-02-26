# A800 Large Model Benchmark Results

**GPU**: NVIDIA A800-SXM4-80GB (Ampere architecture)  
**Date**: February 26, 2026  
**Models**: 3 large models (7B-14B parameters)  
**Configurations**: 5 quantization configs per model  
**Total**: 30 JSON files + 1 CSV summary

## Models Tested

1. **Mistral-7B-v0.1** (7B parameters)
2. **Yi-1.5-9B** (9B parameters)
3. **Qwen2.5-14B** (14B parameters)

## Quantization Configurations

- **FP16**: Baseline (no quantization)
- **INT8 Default**: `load_in_8bit=True, llm_int8_threshold=6.0`
- **INT8 Pure**: `load_in_8bit=True, llm_int8_threshold=0.0`
- **NF4**: `load_in_4bit=True, bnb_4bit_quant_type="nf4"`
- **NF4 DQ**: `load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True`

## Metrics

### Energy Benchmarks
- Energy per 1000 tokens (J/1k)
- Throughput (tokens/second)
- Average power draw (Watts)
- Coefficient of variation (CV%)
- 10 iterations per configuration

### Perplexity Benchmarks
- WikiText-2-raw-v1 test set
- Full dataset evaluation
- Max sequence length: model's max context length (chunked)

## Key Findings

### 1. NF4 Offers Best Energy-Accuracy Tradeoff
- **Mistral-7B**: 4,222 J/1k (-4.1% vs FP16), PPL 4.781 (+0.113 vs FP16)
- **Yi-1.5-9B**: 5,363 J/1k (-1.5% vs FP16), PPL 5.091 (-0.641 vs FP16)
- **Qwen2.5-14B**: 7,545 J/1k (+2.5% vs FP16), PPL 4.898 (+0.305 vs FP16)

### 2. INT8 Default Has Highest Energy Consumption
- **Mistral-7B**: 10,162 J/1k (+130.8% vs FP16)
- **Yi-1.5-9B**: 11,826 J/1k (+117.2% vs FP16)
- **Qwen2.5-14B**: 15,266 J/1k (+107.5% vs FP16)

### 3. INT8 Pure Better Than INT8 Default
- 35-40% lower energy than INT8 Default
- Still higher than FP16/NF4
- Example (Qwen2.5-14B): 9,807 J/1k vs 15,266 J/1k (-36%)

## File Naming Convention

```
energy_{model}_{config}.json    # Energy benchmark results
ppl_{model}_{config}.json       # Perplexity benchmark results
a800_summary.csv                # Summary of all results
```

Model name abbreviations:
- `mistral_7b` = Mistral-7B-v0.1
- `yi_1_5_9b` = Yi-1.5-9B
- `qwen25_14b` = Qwen2.5-14B

Config abbreviations:
- `fp16` = FP16 baseline
- `int8_default` = INT8 Default (threshold=6.0)
- `int8_pure` = INT8 Pure (threshold=0.0)
- `nf4` = NF4 quantization
- `nf4_dq` = NF4 with double quantization

## Benchmark Environment

- **GPU**: NVIDIA A800-SXM4-80GB
- **CUDA**: 12.1
- **PyTorch**: 2.1.0
- **Transformers**: 4.36.0
- **bitsandbytes**: 0.41.3
- **Batch size**: 1
- **Precision**: Mixed precision (FP16 compute)
- **Power monitoring**: NVML at 10 Hz sampling rate

## Reproducibility

All benchmark scripts are available in the `/scripts` directory. See main README for setup instructions.

## Citation

If you use this data, please cite:

```
@misc{zhang2026a800llmenergy,
  author = {Zhang, Hongping},
  title = {A800 Large Language Model Energy Benchmark},
  year = {2026},
  url = {https://github.com/hongping-zh/ecocompute-ai}
}
```
