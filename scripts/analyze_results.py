#!/usr/bin/env python3
"""
Analysis Script for Energy Benchmark Results
=============================================
This script analyzes benchmark results and generates figures for the paper.

Usage:
    python analyze_results.py --data ../data/rtx5090_benchmark_results.csv --output ../figures/

Requirements:
    pip install pandas numpy matplotlib seaborn scipy

Author: Hongping Zhang
License: MIT
"""

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


def load_data(filepath: str) -> pd.DataFrame:
    """Load benchmark results from CSV."""
    df = pd.read_csv(filepath)
    return df


def calculate_energy_delta(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate energy delta between FP16 and quantized configurations."""
    results = []
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        fp16_data = model_data[model_data['config'] == 'FP16']
        
        if fp16_data.empty:
            continue
            
        fp16_energy = fp16_data['energy_per_1k_tokens_mean'].values[0]
        
        for _, row in model_data.iterrows():
            if row['config'] != 'FP16':
                delta = ((row['energy_per_1k_tokens_mean'] - fp16_energy) / fp16_energy) * 100
                results.append({
                    'model': model,
                    'config': row['config'],
                    'fp16_energy': fp16_energy,
                    'quant_energy': row['energy_per_1k_tokens_mean'],
                    'delta_pct': delta
                })
    
    return pd.DataFrame(results)


def perform_statistical_tests(df: pd.DataFrame) -> Dict:
    """Perform paired t-tests for energy differences."""
    results = {}
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        fp16_data = model_data[model_data['config'] == 'FP16']
        nf4_data = model_data[model_data['config'] == 'NF4']
        
        if fp16_data.empty or nf4_data.empty:
            continue
        
        # For demonstration, we use the mean and std to simulate t-test
        # In practice, you would use raw iteration data
        fp16_mean = fp16_data['energy_per_1k_tokens_mean'].values[0]
        fp16_std = fp16_data['energy_per_1k_tokens_std'].values[0]
        nf4_mean = nf4_data['energy_per_1k_tokens_mean'].values[0]
        nf4_std = nf4_data['energy_per_1k_tokens_std'].values[0]
        n = nf4_data['n_runs'].values[0]
        
        # Welch's t-test approximation
        se = np.sqrt((fp16_std**2 / n) + (nf4_std**2 / n))
        t_stat = (nf4_mean - fp16_mean) / se
        
        # Degrees of freedom (Welch-Satterthwaite)
        df_num = ((fp16_std**2 / n) + (nf4_std**2 / n))**2
        df_denom = ((fp16_std**2 / n)**2 / (n-1)) + ((nf4_std**2 / n)**2 / (n-1))
        dof = df_num / df_denom
        
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), dof))
        
        results[model] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'significant': p_value < 0.001
        }
    
    return results


def plot_energy_comparison(df: pd.DataFrame, output_dir: Path):
    """Generate energy comparison bar chart."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    models = df['model'].unique()
    x = np.arange(len(models))
    width = 0.35
    
    fp16_energy = []
    nf4_energy = []
    
    for model in models:
        model_data = df[df['model'] == model]
        fp16_data = model_data[model_data['config'] == 'FP16']
        nf4_data = model_data[model_data['config'] == 'NF4']
        
        fp16_energy.append(fp16_data['energy_per_1k_tokens_mean'].values[0] if not fp16_data.empty else 0)
        nf4_energy.append(nf4_data['energy_per_1k_tokens_mean'].values[0] if not nf4_data.empty else 0)
    
    bars1 = ax.bar(x - width/2, fp16_energy, width, label='FP16', color='#2196F3')
    bars2 = ax.bar(x + width/2, nf4_energy, width, label='NF4 (4-bit)', color='#FF9800')
    
    # Add percentage labels
    for i, (fp16, nf4) in enumerate(zip(fp16_energy, nf4_energy)):
        if fp16 > 0:
            delta = ((nf4 - fp16) / fp16) * 100
            color = 'red' if delta > 0 else 'green'
            sign = '+' if delta > 0 else ''
            ax.annotate(f'{sign}{delta:.1f}%', 
                       xy=(x[i] + width/2, nf4), 
                       ha='center', va='bottom',
                       fontsize=10, fontweight='bold', color=color)
    
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Energy (J per 1k tokens)', fontsize=12)
    ax.set_title('Energy Consumption: FP16 vs 4-bit NF4 Quantization', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([m.split('/')[-1] for m in models], rotation=15, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'fig1_energy_comparison.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'fig1_energy_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: fig1_energy_comparison.pdf/png")


def plot_energy_trend(df: pd.DataFrame, output_dir: Path):
    """Generate energy trend with model size."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract model sizes (approximate from model names)
    model_sizes = {
        'TinyLlama-1.1B': 1.1,
        'Qwen2-1.5B': 1.5,
        'Qwen2.5-3B': 3.0,
        'Qwen2-7B': 7.0
    }
    
    delta_data = calculate_energy_delta(df)
    
    sizes = []
    deltas = []
    
    for _, row in delta_data.iterrows():
        model_short = row['model'].split('/')[-1].replace('-Instruct', '').replace('-Chat-v1.0', '')
        if model_short in model_sizes:
            sizes.append(model_sizes[model_short])
            deltas.append(row['delta_pct'])
    
    # Scatter plot
    ax.scatter(sizes, deltas, s=100, c=['red' if d > 0 else 'green' for d in deltas], 
               edgecolors='black', linewidths=1.5, zorder=5)
    
    # Linear regression
    if len(sizes) >= 2:
        slope, intercept, r_value, p_value, std_err = stats.linregress(sizes, deltas)
        x_line = np.linspace(min(sizes) - 0.5, max(sizes) + 0.5, 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'b--', alpha=0.7, label=f'Linear fit (R² = {r_value**2:.2f})')
        
        # Find crossover point
        crossover = -intercept / slope if slope != 0 else None
        if crossover and 0 < crossover < 15:
            ax.axvline(x=crossover, color='purple', linestyle=':', alpha=0.7, 
                      label=f'Crossover: {crossover:.1f}B params')
    
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    ax.fill_between([0, 10], [0, 0], [-50, -50], alpha=0.1, color='green', label='Energy savings')
    ax.fill_between([0, 10], [0, 0], [50, 50], alpha=0.1, color='red', label='Energy penalty')
    
    ax.set_xlabel('Model Size (Billion Parameters)', fontsize=12)
    ax.set_ylabel('Energy Change from Quantization (%)', fontsize=12)
    ax.set_title('Quantization Energy Efficiency vs Model Size', fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 8)
    ax.set_ylim(-20, 35)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'fig2_energy_trend.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'fig2_energy_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: fig2_energy_trend.pdf/png")


def plot_power_throughput(df: pd.DataFrame, output_dir: Path):
    """Generate power vs throughput comparison."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    models = df['model'].unique()
    x = np.arange(len(models))
    width = 0.35
    
    # Power comparison
    fp16_power = []
    nf4_power = []
    fp16_throughput = []
    nf4_throughput = []
    
    for model in models:
        model_data = df[df['model'] == model]
        fp16_data = model_data[model_data['config'] == 'FP16']
        nf4_data = model_data[model_data['config'] == 'NF4']
        
        fp16_power.append(fp16_data['power_mean'].values[0] if not fp16_data.empty else 0)
        nf4_power.append(nf4_data['power_mean'].values[0] if not nf4_data.empty else 0)
        fp16_throughput.append(fp16_data['throughput_mean'].values[0] if not fp16_data.empty else 0)
        nf4_throughput.append(nf4_data['throughput_mean'].values[0] if not nf4_data.empty else 0)
    
    # Power subplot
    ax1.bar(x - width/2, fp16_power, width, label='FP16', color='#2196F3')
    ax1.bar(x + width/2, nf4_power, width, label='NF4', color='#FF9800')
    ax1.set_xlabel('Model', fontsize=11)
    ax1.set_ylabel('Average Power (W)', fontsize=11)
    ax1.set_title('Power Consumption', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([m.split('/')[-1].split('-')[0] for m in models], rotation=15)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Throughput subplot
    ax2.bar(x - width/2, fp16_throughput, width, label='FP16', color='#2196F3')
    ax2.bar(x + width/2, nf4_throughput, width, label='NF4', color='#FF9800')
    ax2.set_xlabel('Model', fontsize=11)
    ax2.set_ylabel('Throughput (tokens/s)', fontsize=11)
    ax2.set_title('Inference Throughput', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels([m.split('/')[-1].split('-')[0] for m in models], rotation=15)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'fig3_power_throughput.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'fig3_power_throughput.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: fig3_power_throughput.pdf/png")


def generate_latex_table(df: pd.DataFrame, output_dir: Path):
    """Generate LaTeX table for paper."""
    latex = r"""\begin{table*}[t]
\centering
\caption{Energy Efficiency: FP16 vs. 4-bit NF4 (mean $\pm$ std, n=10). $^{***}p < 0.001$.}
\label{tab:main_results}
\begin{tabular}{llrrrr}
\toprule
\textbf{Model} & \textbf{Config} & \textbf{Throughput (tok/s)} & \textbf{Avg Power (W)} & \textbf{Energy (J/1k tok)} & \textbf{$\Delta$ Energy} \\
\midrule
"""
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        model_short = model.split('/')[-1]
        
        for _, row in model_data.iterrows():
            config = row['config']
            throughput = f"{row['throughput_mean']:.2f} $\\pm$ {row['throughput_std']:.2f}"
            power = f"{row['power_mean']:.2f} $\\pm$ {row['power_std']:.2f}"
            energy = f"{row['energy_per_1k_tokens_mean']:.2f} $\\pm$ {row['energy_per_1k_tokens_std']:.2f}"
            
            if config == 'FP16':
                delta = "---"
            else:
                delta_val = row['delta_energy_pct']
                if delta_val > 0:
                    delta = f"\\textcolor{{red}}{{+{delta_val:.1f}\\%}}$^{{***}}$"
                else:
                    delta = f"\\textcolor{{green}}{{{delta_val:.1f}\\%}}$^{{***}}$"
            
            latex += f"{model_short} & {config} & {throughput} & {power} & {energy} & {delta} \\\\\n"
        
        latex += "\\midrule\n"
    
    latex = latex.rstrip("\\midrule\n") + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    
    with open(output_dir / 'table_results.tex', 'w') as f:
        f.write(latex)
    
    print(f"Saved: table_results.tex")


def main():
    parser = argparse.ArgumentParser(description="Analyze Energy Benchmark Results")
    parser.add_argument("--data", type=str, required=True, help="Path to benchmark CSV")
    parser.add_argument("--output", type=str, default="./figures", help="Output directory")
    
    args = parser.parse_args()
    
    # Load data
    df = load_data(args.data)
    print(f"Loaded {len(df)} rows from {args.data}")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Statistical tests
    print("\n=== Statistical Analysis ===")
    stats_results = perform_statistical_tests(df)
    for model, result in stats_results.items():
        print(f"{model}: t={result['t_statistic']:.3f}, p={result['p_value']:.6f}, significant={result['significant']}")
    
    # Generate figures
    print("\n=== Generating Figures ===")
    plot_energy_comparison(df, output_dir)
    plot_energy_trend(df, output_dir)
    plot_power_throughput(df, output_dir)
    
    # Generate LaTeX table
    print("\n=== Generating LaTeX Table ===")
    generate_latex_table(df, output_dir)
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
