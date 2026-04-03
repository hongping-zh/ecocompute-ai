---
title: "When Quantization Hurts: The Surprising Energy Cost of 4-bit LLMs on RTX 5090"
thumbnail: /blog/assets/quantization-energy/thumbnail.png
authors:
- user: your-hf-username
---

# When Quantization Hurts: The Surprising Energy Cost of 4-bit LLMs on RTX 5090

**TL;DR**: We benchmarked 4-bit quantization vs FP16 on the new RTX 5090 and found that **quantization increases energy consumption by up to 29% for models smaller than 5B parameters**. Only 7B+ models benefit from quantization in terms of energy efficiency.

## The Assumption We All Made

4-bit quantization has become the go-to technique for running LLMs on consumer hardware. Tools like `bitsandbytes`, GPTQ, and AWQ make it trivially easy to shrink models to a quarter of their size. The benefits seem obvious:

- ✅ 4x less memory
- ✅ Fits larger models on consumer GPUs  
- ✅ Lower power consumption
- ✅ Better for the environment... **right?**

We assumed that last point was true. **We were wrong.**

## The Experiment

We got access to an **NVIDIA RTX 5090**—the new Blackwell architecture flagship with 32GB GDDR7 and 575W TDP—and ran a comprehensive energy benchmark.

### Setup

| Component | Specification |
|-----------|---------------|
| GPU | NVIDIA GeForce RTX 5090 |
| Architecture | Blackwell (sm_120) |
| VRAM | 32 GB GDDR7 |
| PyTorch | 2.10.0+cu128 |

We compared two configurations:
- **FP16**: Native half-precision inference
- **4-bit NF4**: bitsandbytes quantization with FP16 compute

### Models Tested

| Model | Parameters |
|-------|------------|
| TinyLlama | 1.1B |
| Qwen2 | 1.5B |
| Qwen2.5-Instruct | 3B |
| Qwen2 | 7B |

For each model, we generated 256 tokens × 10 samples while measuring power at 100ms intervals using NVML.

## The Surprising Results

Here's what we found:

| Model | FP16 Energy | 4-bit Energy | Change |
|-------|-------------|--------------|--------|
| TinyLlama 1.1B | 1,659 J/1k tokens | 2,098 J/1k tokens | **+26.5%** 🔴 |
| Qwen2 1.5B | 2,411 J/1k tokens | 3,120 J/1k tokens | **+29.4%** 🔴 |
| Qwen2.5 3B | 3,383 J/1k tokens | 3,780 J/1k tokens | **+11.7%** 🔴 |
| Qwen2 7B | 5,509 J/1k tokens | 4,878 J/1k tokens | **-11.4%** 🟢 |

**For models under 5B parameters, 4-bit quantization uses MORE energy, not less!**

## The Crossover Point

There's a clear pattern emerging:

```
Model Size → Energy Change (4-bit vs FP16)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1.1B       → +26.5% (worse)
1.5B       → +29.4% (worse)  
3B         → +11.7% (worse, but gap narrowing)
7B         → -11.4% (better) ✓
```

The **crossover point** where quantization becomes beneficial is around **5B parameters** on RTX 5090.

## Why Does This Happen?

The answer lies in the **de-quantization overhead**.

When using 4-bit quantization, the GPU must:
1. Load 4-bit weights from memory
2. **De-quantize** them to FP16 for computation
3. Perform the actual matrix multiplication

### For Small Models:
- Memory bandwidth isn't the bottleneck (model fits easily in cache)
- De-quantization overhead becomes a significant fraction of total compute
- **Result**: More energy consumed

### For Large Models:
- Memory bandwidth IS the bottleneck
- 4-bit reduces memory traffic by ~4x
- De-quantization cost is amortized over more compute
- **Result**: Energy savings

### The Power-Throughput Trade-off

Here's the key insight: **4-bit quantization always reduces power draw** (by 24-48%), but it also **reduces throughput by ~40%**.

| Model | FP16 Power | 4-bit Power | FP16 Throughput | 4-bit Throughput |
|-------|------------|-------------|-----------------|------------------|
| 1.1B | 157W | 117W | 95 tok/s | 56 tok/s |
| 7B | 388W | 202W | 70 tok/s | 41 tok/s |

For small models, the throughput penalty outweighs the power savings. Energy = Power × Time, and the extra time dominates.

## Practical Guidelines

Based on our findings, here's what we recommend for RTX 5090:

| Scenario | Recommendation | Reason |
|----------|----------------|--------|
| Models < 5B | **Use FP16** | Quantization increases energy |
| Models ≥ 5B | **Use 4-bit** | Saves ~11% energy |
| VRAM-constrained | Use 4-bit | Accept energy penalty for capability |
| Latency-critical | Use FP16 | 40% faster throughput |

## Implications for Green AI

This finding has important implications for sustainable AI:

1. **Don't assume quantization = green**. For small models, you're actually increasing your carbon footprint.

2. **Right-size your model**. A 3B FP16 model may be more environmentally friendly than a 7B quantized model.

3. **Measure, don't assume**. Energy efficiency varies by hardware and model size.

4. **Hardware matters**. The crossover point likely differs on other GPUs. We hypothesize it would be smaller on memory-bandwidth-limited hardware like T4 or L4.

## Try It Yourself

We've open-sourced our benchmarking code and created **EcoCompute AI**, a tool to estimate LLM training cost and carbon footprint:

🔗 **GitHub**: [github.com/your-repo/ecocompute-ai](https://github.com/your-repo/ecocompute-ai)

🔗 **Live Demo**: [ecocompute.ai](https://ecocompute.ai)

The benchmarking script:

```python
from ecocompute import EnergyAuditor

auditor = EnergyAuditor(gpu_index=0)
auditor.start()

# Your inference code here
outputs = model.generate(inputs, max_new_tokens=256)

energy, avg_power, peak_power = auditor.stop()
print(f"Energy: {energy:.2f} J, Avg Power: {avg_power:.2f} W")
```

## What's Next?

We're planning to:

1. **Test other quantization methods** (GPTQ, AWQ) to see if they have lower de-quantization overhead
2. **Benchmark on other GPUs** (A100, L4, T4) to map the crossover point across hardware
3. **Explore power-limiting** as a way to shift the crossover point

## Conclusion

**4-bit quantization is not a silver bullet for Green AI.** On high-performance GPUs like the RTX 5090, it only provides energy savings for models larger than ~5B parameters. For smaller models, stick with FP16—it's faster AND more energy-efficient.

The next time someone tells you quantization is always better for the environment, show them this data. 📊

---

*This research was conducted as part of the EcoCompute AI project. We welcome feedback and collaboration!*

## Citation

If you find this work useful, please cite:

```bibtex
@article{ecocompute2026quantization,
  title={When Quantization Hurts: Energy Efficiency Crossover Point for LLM Inference on RTX 5090},
  author={Anonymous},
  journal={Hugging Face Blog},
  year={2026},
  url={https://huggingface.co/blog/quantization-energy}
}
```

---

**Tags**: `green-ai`, `quantization`, `energy-efficiency`, `rtx-5090`, `sustainability`, `bitsandbytes`
