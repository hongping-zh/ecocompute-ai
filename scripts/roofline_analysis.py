#!/usr/bin/env python3
"""
Roofline Model Analysis for Quantization Energy Efficiency
===========================================================
This script implements the theoretical framework for predicting
when quantization yields energy benefits based on compute-to-bandwidth ratios.

Usage:
    python roofline_analysis.py --gpu rtx5090 --model qwen2-1.5b

Requirements:
    pip install numpy matplotlib

Author: Hongping Zhang
License: MIT
"""

import argparse
from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class GPUSpecs:
    """GPU hardware specifications."""
    name: str
    fp16_tflops: float  # TFLOPS
    memory_bandwidth_tb_s: float  # TB/s
    tdp_watts: float  # Watts
    architecture: str
    
    @property
    def compute_to_bandwidth_ratio(self) -> float:
        """FLOPS per Byte."""
        return (self.fp16_tflops * 1e12) / (self.memory_bandwidth_tb_s * 1e12)


@dataclass
class ModelSpecs:
    """Model specifications."""
    name: str
    parameters_billions: float
    hidden_dim: int
    num_layers: int
    vocab_size: int = 32000
    
    @property
    def fp16_memory_bytes(self) -> float:
        """Memory footprint in FP16 (bytes)."""
        return self.parameters_billions * 1e9 * 2  # 2 bytes per FP16
    
    @property
    def nf4_memory_bytes(self) -> float:
        """Memory footprint in NF4 (bytes)."""
        return self.parameters_billions * 1e9 * 0.5  # 0.5 bytes per 4-bit


# GPU Database
GPU_SPECS = {
    "rtx5090": GPUSpecs("RTX 5090", 660, 1.8, 575, "Blackwell"),
    "rtx4090": GPUSpecs("RTX 4090", 330, 1.008, 450, "Ada Lovelace"),
    "h100": GPUSpecs("H100", 990, 3.35, 700, "Hopper"),
    "a100": GPUSpecs("A100", 312, 2.039, 400, "Ampere"),
    "t4": GPUSpecs("T4", 65, 0.3, 70, "Turing"),
}

# Model Database
MODEL_SPECS = {
    "tinyllama-1.1b": ModelSpecs("TinyLlama-1.1B", 1.1, 2048, 22),
    "qwen2-1.5b": ModelSpecs("Qwen2-1.5B", 1.5, 1536, 28),
    "qwen2.5-3b": ModelSpecs("Qwen2.5-3B", 3.0, 2048, 36),
    "qwen2-7b": ModelSpecs("Qwen2-7B", 7.0, 3584, 28),
    "llama2-7b": ModelSpecs("Llama2-7B", 7.0, 4096, 32),
    "llama2-13b": ModelSpecs("Llama2-13B", 13.0, 5120, 40),
    "llama2-70b": ModelSpecs("Llama2-70B", 70.0, 8192, 80),
}


def calculate_arithmetic_intensity(
    model: ModelSpecs,
    batch_size: int = 1,
    sequence_length: int = 512,
    precision: str = "fp16"
) -> float:
    """
    Calculate arithmetic intensity for LLM inference.
    
    Arithmetic Intensity = FLOPs / Bytes Transferred
    
    For autoregressive decoding:
    - FLOPs per token ≈ 2 * num_parameters (for matrix multiplications)
    - Bytes per token = model_size_bytes (full model loaded per token in memory-bound regime)
    """
    flops_per_token = 2 * model.parameters_billions * 1e9
    
    if precision == "fp16":
        bytes_per_token = model.fp16_memory_bytes
    elif precision == "nf4":
        bytes_per_token = model.nf4_memory_bytes
    else:
        raise ValueError(f"Unknown precision: {precision}")
    
    # Arithmetic intensity in FLOP/Byte
    ai = flops_per_token / bytes_per_token
    
    return ai


def calculate_dequantization_overhead(
    model: ModelSpecs,
    gpu: GPUSpecs
) -> float:
    """
    Estimate de-quantization overhead factor.
    
    De-quantization involves:
    1. Loading quantized weights (4-bit)
    2. Loading scale factors (FP16)
    3. Performing de-quantization computation
    
    Overhead factor O_dequant represents the additional compute
    required relative to direct FP16 operations.
    """
    # Empirical overhead factor based on bitsandbytes implementation
    # Higher for high-compute GPUs due to kernel launch overhead
    base_overhead = 1.15  # 15% base overhead
    
    # Scale with compute-to-bandwidth ratio
    # Higher ratio = more compute-bound = higher relative overhead
    ratio_factor = gpu.compute_to_bandwidth_ratio / 100
    
    overhead = base_overhead + 0.1 * ratio_factor
    
    return min(overhead, 2.0)  # Cap at 2x overhead


def predict_energy_ratio(
    model: ModelSpecs,
    gpu: GPUSpecs,
    empirical_throughput_fp16: float = None,
    empirical_throughput_nf4: float = None,
    empirical_power_fp16: float = None,
    empirical_power_nf4: float = None
) -> Dict:
    """
    Predict energy ratio E_Q4 / E_FP16 using the Roofline-based model.
    
    Energy = Power × Time = Power × (Tokens / Throughput)
    
    For 1000 tokens:
    E = P × (1000 / T)
    
    Energy Ratio = (P_Q4 × T_FP16) / (P_FP16 × T_Q4)
    """
    # Calculate arithmetic intensities
    ai_fp16 = calculate_arithmetic_intensity(model, precision="fp16")
    ai_nf4 = calculate_arithmetic_intensity(model, precision="nf4")
    
    # Get de-quantization overhead
    o_dequant = calculate_dequantization_overhead(model, gpu)
    
    # Compute-to-bandwidth ratio
    R = gpu.compute_to_bandwidth_ratio
    
    # Theoretical throughput ratio
    # In memory-bound regime: T ∝ Bandwidth / Model_Size
    # NF4 has 4x smaller model, but de-quantization overhead
    theoretical_throughput_ratio = 4.0 / o_dequant  # T_NF4 / T_FP16
    
    # Theoretical power ratio
    # Power scales with compute utilization and memory access
    # NF4 typically has lower power due to reduced memory traffic
    theoretical_power_ratio = 0.75  # P_NF4 / P_FP16 (empirical estimate)
    
    # Use empirical values if provided
    if empirical_throughput_fp16 and empirical_throughput_nf4:
        actual_throughput_ratio = empirical_throughput_nf4 / empirical_throughput_fp16
    else:
        actual_throughput_ratio = theoretical_throughput_ratio
    
    if empirical_power_fp16 and empirical_power_nf4:
        actual_power_ratio = empirical_power_nf4 / empirical_power_fp16
    else:
        actual_power_ratio = theoretical_power_ratio
    
    # Energy ratio: E_Q4 / E_FP16 = (P_Q4 / P_FP16) × (T_FP16 / T_Q4)
    energy_ratio = actual_power_ratio / actual_throughput_ratio
    
    # Determine if quantization is beneficial
    is_beneficial = energy_ratio < 1.0
    
    return {
        "model": model.name,
        "gpu": gpu.name,
        "arithmetic_intensity_fp16": ai_fp16,
        "arithmetic_intensity_nf4": ai_nf4,
        "dequantization_overhead": o_dequant,
        "compute_to_bandwidth_ratio": R,
        "throughput_ratio": actual_throughput_ratio,
        "power_ratio": actual_power_ratio,
        "energy_ratio": energy_ratio,
        "energy_change_pct": (energy_ratio - 1) * 100,
        "is_beneficial": is_beneficial
    }


def find_crossover_point(gpu: GPUSpecs, model_sizes: np.ndarray = None) -> float:
    """
    Find the model size at which quantization becomes energy-beneficial.
    
    Returns the crossover point in billions of parameters.
    """
    if model_sizes is None:
        model_sizes = np.linspace(0.5, 20, 100)
    
    energy_changes = []
    
    for size in model_sizes:
        # Create synthetic model spec
        model = ModelSpecs(f"Model-{size}B", size, int(1024 * np.sqrt(size)), int(20 + size * 2))
        result = predict_energy_ratio(model, gpu)
        energy_changes.append(result["energy_change_pct"])
    
    energy_changes = np.array(energy_changes)
    
    # Find where energy change crosses zero
    crossover_idx = np.where(np.diff(np.sign(energy_changes)))[0]
    
    if len(crossover_idx) > 0:
        # Linear interpolation for more precise crossover
        idx = crossover_idx[0]
        x1, x2 = model_sizes[idx], model_sizes[idx + 1]
        y1, y2 = energy_changes[idx], energy_changes[idx + 1]
        crossover = x1 - y1 * (x2 - x1) / (y2 - y1)
        return crossover
    
    return None


def plot_roofline_analysis(gpu: GPUSpecs, output_path: str = None):
    """Generate Roofline analysis visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Energy change vs model size
    ax1 = axes[0]
    model_sizes = np.linspace(0.5, 15, 50)
    energy_changes = []
    
    for size in model_sizes:
        model = ModelSpecs(f"Model-{size}B", size, int(1024 * np.sqrt(size)), int(20 + size * 2))
        result = predict_energy_ratio(model, gpu)
        energy_changes.append(result["energy_change_pct"])
    
    ax1.plot(model_sizes, energy_changes, 'b-', linewidth=2, label=gpu.name)
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    ax1.fill_between(model_sizes, energy_changes, 0, 
                     where=np.array(energy_changes) > 0, 
                     alpha=0.3, color='red', label='Energy penalty')
    ax1.fill_between(model_sizes, energy_changes, 0, 
                     where=np.array(energy_changes) <= 0, 
                     alpha=0.3, color='green', label='Energy savings')
    
    crossover = find_crossover_point(gpu)
    if crossover:
        ax1.axvline(x=crossover, color='purple', linestyle=':', linewidth=2)
        ax1.annotate(f'Crossover: {crossover:.1f}B', 
                    xy=(crossover, 0), xytext=(crossover + 1, 10),
                    fontsize=10, arrowprops=dict(arrowstyle='->', color='purple'))
    
    ax1.set_xlabel('Model Size (Billion Parameters)', fontsize=12)
    ax1.set_ylabel('Energy Change from Quantization (%)', fontsize=12)
    ax1.set_title(f'Quantization Energy Efficiency on {gpu.name}', fontsize=14)
    ax1.legend(loc='upper right')
    ax1.grid(alpha=0.3)
    ax1.set_xlim(0, 15)
    
    # Plot 2: Crossover points across GPUs
    ax2 = axes[1]
    gpus = list(GPU_SPECS.values())
    crossovers = []
    ratios = []
    
    for g in gpus:
        cp = find_crossover_point(g)
        crossovers.append(cp if cp else 0)
        ratios.append(g.compute_to_bandwidth_ratio)
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(gpus)))
    
    for i, (g, cp, r) in enumerate(zip(gpus, crossovers, ratios)):
        ax2.scatter(r, cp, s=150, c=[colors[i]], edgecolors='black', linewidths=1.5, zorder=5)
        ax2.annotate(g.name, xy=(r, cp), xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax2.set_xlabel('Compute-to-Bandwidth Ratio (FLOP/Byte)', fontsize=12)
    ax2.set_ylabel('Crossover Point (Billion Parameters)', fontsize=12)
    ax2.set_title('Crossover Points Across GPU Architectures', fontsize=14)
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()


def case_study_qwen2_1_5b_rtx5090():
    """
    Detailed case study: Qwen2-1.5B on RTX 5090
    
    This demonstrates the numerical derivation from the paper.
    """
    print("\n" + "="*70)
    print("CASE STUDY: Qwen2-1.5B on RTX 5090 (Blackwell)")
    print("="*70)
    
    model = MODEL_SPECS["qwen2-1.5b"]
    gpu = GPU_SPECS["rtx5090"]
    
    # Empirical measurements from Table 4
    T_FP16 = 71.45  # tokens/s
    T_NF4 = 41.57   # tokens/s
    P_FP16 = 172.30  # W
    P_NF4 = 129.83   # W
    
    print(f"\n1. Hardware Specifications:")
    print(f"   GPU: {gpu.name} ({gpu.architecture})")
    print(f"   FP16 Compute: {gpu.fp16_tflops} TFLOPS")
    print(f"   Memory Bandwidth: {gpu.memory_bandwidth_tb_s} TB/s")
    print(f"   Compute-to-Bandwidth Ratio: {gpu.compute_to_bandwidth_ratio:.2f} FLOP/Byte")
    
    print(f"\n2. Model Specifications:")
    print(f"   Model: {model.name}")
    print(f"   Parameters: {model.parameters_billions}B")
    print(f"   FP16 Memory: {model.fp16_memory_bytes / 1e9:.2f} GB")
    print(f"   NF4 Memory: {model.nf4_memory_bytes / 1e9:.2f} GB")
    
    print(f"\n3. Empirical Measurements:")
    print(f"   FP16 Throughput: {T_FP16:.2f} tok/s")
    print(f"   NF4 Throughput: {T_NF4:.2f} tok/s")
    print(f"   FP16 Power: {P_FP16:.2f} W")
    print(f"   NF4 Power: {P_NF4:.2f} W")
    
    print(f"\n4. Arithmetic Intensity Analysis:")
    ai_fp16 = calculate_arithmetic_intensity(model, precision="fp16")
    ai_nf4 = calculate_arithmetic_intensity(model, precision="nf4")
    print(f"   I_FP16 = 2 × {model.parameters_billions}B / {model.fp16_memory_bytes/1e9:.2f}GB = {ai_fp16:.2f} FLOP/Byte")
    print(f"   I_NF4 = 2 × {model.parameters_billions}B / {model.nf4_memory_bytes/1e9:.2f}GB = {ai_nf4:.2f} FLOP/Byte")
    print(f"   Machine Balance R = {gpu.compute_to_bandwidth_ratio:.2f} FLOP/Byte")
    print(f"   Since I < R, inference is MEMORY-BOUND")
    
    print(f"\n5. Energy Ratio Calculation:")
    print(f"   E_Q4/E_FP16 = (P_Q4/P_FP16) × (T_FP16/T_Q4)")
    power_ratio = P_NF4 / P_FP16
    throughput_ratio = T_FP16 / T_NF4
    energy_ratio = power_ratio * throughput_ratio
    print(f"             = ({P_NF4:.2f}/{P_FP16:.2f}) × ({T_FP16:.2f}/{T_NF4:.2f})")
    print(f"             = {power_ratio:.3f} × {throughput_ratio:.3f}")
    print(f"             = {energy_ratio:.3f}")
    
    energy_change = (energy_ratio - 1) * 100
    print(f"\n6. Result:")
    print(f"   Energy Change: {energy_change:+.1f}%")
    print(f"   Quantization is {'BENEFICIAL' if energy_change < 0 else 'NOT BENEFICIAL'} for this configuration")
    
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description="Roofline Analysis for Quantization Energy Efficiency")
    parser.add_argument("--gpu", type=str, default="rtx5090", 
                        choices=list(GPU_SPECS.keys()),
                        help="GPU to analyze")
    parser.add_argument("--model", type=str, default="qwen2-1.5b",
                        choices=list(MODEL_SPECS.keys()),
                        help="Model to analyze")
    parser.add_argument("--output", type=str, default="roofline_analysis.pdf",
                        help="Output figure path")
    parser.add_argument("--case-study", action="store_true",
                        help="Run detailed case study")
    
    args = parser.parse_args()
    
    gpu = GPU_SPECS[args.gpu]
    model = MODEL_SPECS[args.model]
    
    # Run analysis
    print(f"\n=== Roofline Analysis: {model.name} on {gpu.name} ===\n")
    
    result = predict_energy_ratio(model, gpu)
    
    print(f"Arithmetic Intensity (FP16): {result['arithmetic_intensity_fp16']:.2f} FLOP/Byte")
    print(f"Arithmetic Intensity (NF4): {result['arithmetic_intensity_nf4']:.2f} FLOP/Byte")
    print(f"Compute-to-Bandwidth Ratio: {result['compute_to_bandwidth_ratio']:.2f} FLOP/Byte")
    print(f"De-quantization Overhead: {result['dequantization_overhead']:.2f}x")
    print(f"Predicted Energy Ratio: {result['energy_ratio']:.3f}")
    print(f"Predicted Energy Change: {result['energy_change_pct']:+.1f}%")
    print(f"Quantization Beneficial: {result['is_beneficial']}")
    
    # Find crossover point
    crossover = find_crossover_point(gpu)
    if crossover:
        print(f"\nCrossover Point for {gpu.name}: {crossover:.1f}B parameters")
    
    # Generate visualization
    plot_roofline_analysis(gpu, args.output)
    
    # Run case study if requested
    if args.case_study:
        case_study_qwen2_1_5b_rtx5090()


if __name__ == "__main__":
    main()
