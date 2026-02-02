# Experimental Data

This directory contains the benchmark results from our energy efficiency experiments.

## Files

### `rtx5090_benchmark_results.csv`
Benchmark results on NVIDIA RTX 5090 (Blackwell architecture).

**Columns:**
- `model`: Model name/path
- `config`: Quantization configuration (FP16, NF4)
- `precision`: Bit precision (16, 4)
- `throughput_mean`: Mean throughput in tokens/second
- `throughput_std`: Standard deviation of throughput
- `power_mean`: Mean power consumption in Watts
- `power_std`: Standard deviation of power
- `energy_per_1k_tokens_mean`: Mean energy per 1000 tokens in Joules
- `energy_per_1k_tokens_std`: Standard deviation of energy
- `delta_energy_pct`: Percentage change from FP16 baseline
- `n_runs`: Number of benchmark iterations

### `t4_benchmark_results.csv`
Benchmark results on NVIDIA T4 (Turing architecture).

Same column structure as RTX 5090 results.

### `telemetry_config.json`
Hardware and software configuration for reproducibility.

**Contents:**
- NVML sampling frequency and interval
- Driver and CUDA versions
- bitsandbytes and PyTorch versions
- Operating system and kernel versions
- Idle power measurements
- Ambient temperature conditions
- Benchmark parameters (warmup, iterations, tokens)

## Data Collection Methodology

1. **Thermal Stabilization**: 5-minute warmup period before measurements
2. **Idle Power Subtraction**: Baseline power subtracted to isolate inference energy
3. **Multiple Iterations**: 10 measurement runs per configuration
4. **Statistical Validation**: Paired t-tests for significance (p < 0.001)

## Usage

```python
import pandas as pd

# Load RTX 5090 results
df = pd.read_csv('rtx5090_benchmark_results.csv')

# Filter by model
qwen_data = df[df['model'].str.contains('Qwen')]

# Compare FP16 vs NF4
fp16 = df[df['config'] == 'FP16']
nf4 = df[df['config'] == 'NF4']
```

## License

This data is released under the MIT License. Please cite our paper if you use this data in your research.
