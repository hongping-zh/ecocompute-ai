# [Performance/Energy] 4-bit NF4 shows significant energy efficiency penalty on Blackwell (RTX 5090) for small models

## Describe the Observation

Hi bitsandbytes team,

I'm working on an open-source Green AI framework called **EcoCompute AI**, focused on auditing the energy-economic impact of LLMs.

During our benchmarking on the new **NVIDIA RTX 5090 (Blackwell, sm_120)**, we observed a significant **"Energy Efficiency Paradox"** when using 4-bit NF4 quantization on models under 3B parameters.

## Environment

- **GPU**: NVIDIA GeForce RTX 5090 (32GB GDDR7, Blackwell sm_120)
- **PyTorch**: 2.10.0+cu128
- **CUDA**: 12.8
- **bitsandbytes**: 0.49.1
- **transformers**: 5.0.0
- **OS**: Ubuntu 22.04 (AutoDL Cloud)

## The Data (RTX 5090)

| Model | Config | Throughput (tok/s) | Avg Power (W) | Energy (J/1k Tokens) | Change |
| :--- | :--- | ---: | ---: | ---: | :--- |
| TinyLlama-1.1B | FP16 | 94.87 | 157.45 | 1659.00 | baseline |
| TinyLlama-1.1B | 4-bit NF4 | 55.79 | 117.02 | 2098.44 | **+26.5%** ⚠️ |
| Qwen2-1.5B | FP16 | 71.45 | 172.30 | 2411.09 | baseline |
| Qwen2-1.5B | 4-bit NF4 | 41.57 | 129.83 | 3120.49 | **+29.4%** ⚠️ |
| Qwen2-7B | FP16 | 70.47 | 388.34 | 5508.56 | baseline |
| Qwen2-7B | 4-bit NF4 | 41.40 | 201.88 | 4877.88 | **-11.4%** ✅ |

## Key Findings

### 1. The Energy Trap
For models ≤1.5B parameters, although 4-bit reduced average power by ~25%, the **~41% drop in throughput** (due to de-quantization overhead) resulted in **26-29% MORE energy consumed per token** compared to FP16.

### 2. The Crossover Point
The energy benefit only becomes positive when the model scales to ~7B parameters, where memory bandwidth savings outweigh the de-quantization penalty.

### 3. Throughput Consistency
Across all model sizes, 4-bit NF4 throughput is consistently **~58-59% of FP16** throughput. This ratio appears to be an inherent characteristic of the current implementation.

## 🔬 Power-Limit Experiment: De-quantization Kernel Bottleneck Evidence

To isolate whether the issue is GPU power-related or kernel-related, we ran experiments with software power limits:

| Power Limit | Model | FP16 Energy | 4-bit Energy | 4-bit Penalty |
|-------------|-------|-------------|--------------|---------------|
| 575W (native) | TinyLlama-1.1B | 1496 J/1k | 1860 J/1k | **-24.3%** |
| 300W (A100-level) | TinyLlama-1.1B | 1614 J/1k | 1833 J/1k | **-13.6%** |
| 150W (L4-level) | TinyLlama-1.1B | 1612 J/1k | 1795 J/1k | **-11.3%** |

### Critical Insight

**Even when we simulate low-power environments (150W), the de-quantization kernel remains the primary bottleneck for small models on Blackwell.** 

The energy penalty improved from -24% to -11%, but **never crossed the break-even point**. This strongly suggests:

1. The bottleneck is **kernel-level**, not power-level
2. The de-quantization overhead is **compute-bound**, not memory-bound for small models
3. There may be **optimization opportunities** in the sm_120 de-quantization kernels

## Potential Impact

On ultra-fast hardware like the RTX 5090, **blind quantization of small models might inadvertently increase the carbon footprint** of AI deployments. This is counterintuitive for users who assume quantization always saves energy.

## Questions for the Team

1. Is this throughput penalty a known bottleneck for the **Blackwell architecture's de-quantization kernels**?
2. Are there plans to optimize bitsandbytes for **sm_120** to bridge this throughput gap?
3. Would it be possible to add a **warning or recommendation** in the documentation about the energy trade-off for small models on high-performance GPUs?

## Reproduction Code

```python
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

def benchmark(model_id, use_4bit=False):
    kwargs = {"torch_dtype": torch.float16}
    if use_4bit:
        kwargs = {"quantization_config": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4"
        )}
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", **kwargs)
    
    inputs = tokenizer("Hello", return_tensors="pt").to("cuda")
    
    # Warmup
    model.generate(**inputs, max_new_tokens=20)
    torch.cuda.synchronize()
    
    # Benchmark
    start = time.time()
    for _ in range(10):
        model.generate(**inputs, max_new_tokens=128, do_sample=True)
    torch.cuda.synchronize()
    
    print(f"{'4-bit' if use_4bit else 'FP16'}: {time.time() - start:.2f}s")

# Run on TinyLlama-1.1B
benchmark("TinyLlama/TinyLlama-1.1B-Chat-v1.0", use_4bit=False)
benchmark("TinyLlama/TinyLlama-1.1B-Chat-v1.0", use_4bit=True)
```

## Additional Context

- Full technical report available at: [TechRxiv Link - to be added]
- EcoCompute AI repository: [GitHub Link - to be added]
- Happy to provide more telemetry data (power traces, memory profiles) if needed.

Thank you for your amazing work on bitsandbytes! 🙏
