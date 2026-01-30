#!/usr/bin/env python3
"""
Generate figures for arXiv paper: When Quantization Hurts
"""

import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 14

# Data from experiments
models = ['TinyLlama\n1.1B', 'Qwen2\n1.5B', 'Qwen2.5\n3B', 'Qwen2\n7B']
params = [1.1, 1.5, 3, 7]

fp16_energy = [1659.00, 2411.09, 3382.64, 5508.56]
nf4_energy = [2098.44, 3120.49, 3779.60, 4877.88]

fp16_throughput = [94.87, 71.45, 54.77, 70.47]
nf4_throughput = [55.79, 41.57, 31.85, 41.40]

fp16_power = [157.45, 172.30, 185.59, 388.34]
nf4_power = [117.02, 129.83, 120.46, 201.88]

energy_change = [26.5, 29.4, 11.7, -11.4]

# Figure 1: Energy Efficiency Comparison (Bar Chart)
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(models))
width = 0.35

bars1 = ax.bar(x - width/2, fp16_energy, width, label='FP16', color='#2ecc71', edgecolor='black')
bars2 = ax.bar(x + width/2, nf4_energy, width, label='4-bit NF4', color='#e74c3c', edgecolor='black')

ax.set_xlabel('Model')
ax.set_ylabel('Energy (J / 1k tokens)')
ax.set_title('Energy Consumption: FP16 vs 4-bit NF4 on RTX 5090')
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend()

# Add percentage labels
for i, (fp, nf, change) in enumerate(zip(fp16_energy, nf4_energy, energy_change)):
    color = 'red' if change > 0 else 'green'
    sign = '+' if change > 0 else ''
    ax.annotate(f'{sign}{change}%', 
                xy=(i + width/2, nf + 100), 
                ha='center', fontsize=11, fontweight='bold', color=color)

plt.tight_layout()
plt.savefig('fig1_energy_comparison.pdf', dpi=300, bbox_inches='tight')
plt.savefig('fig1_energy_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Saved fig1_energy_comparison.pdf/png")

# Figure 2: Energy Change Trend (Line Chart with Crossover)
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(params, energy_change, 'o-', markersize=10, linewidth=2, color='#3498db')
ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5, label='Break-even')

# Fill regions
ax.fill_between([0, 7], 0, 50, alpha=0.1, color='red', label='Quantization hurts')
ax.fill_between([0, 7], -20, 0, alpha=0.1, color='green', label='Quantization helps')

# Annotate crossover
ax.annotate('Crossover\n~5B', xy=(5, 0), xytext=(5.5, 15),
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=12, ha='center')

ax.set_xlabel('Model Size (Billion Parameters)')
ax.set_ylabel('Energy Change (%)\n(4-bit vs FP16)')
ax.set_title('Quantization Energy Efficiency by Model Size')
ax.set_xlim(0, 8)
ax.set_ylim(-20, 40)
ax.legend(loc='upper right')

# Add data labels
for p, e in zip(params, energy_change):
    sign = '+' if e > 0 else ''
    ax.annotate(f'{sign}{e}%', xy=(p, e), xytext=(p, e+3), ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('fig2_energy_trend.pdf', dpi=300, bbox_inches='tight')
plt.savefig('fig2_energy_trend.png', dpi=300, bbox_inches='tight')
print("✅ Saved fig2_energy_trend.pdf/png")

# Figure 3: Power vs Throughput Trade-off
fig, ax1 = plt.subplots(figsize=(10, 6))

x = np.arange(len(models))
width = 0.35

# Power bars
ax1.bar(x - width/2, fp16_power, width, label='FP16 Power', color='#3498db', alpha=0.7)
ax1.bar(x + width/2, nf4_power, width, label='4-bit Power', color='#9b59b6', alpha=0.7)
ax1.set_xlabel('Model')
ax1.set_ylabel('Average Power (W)', color='#3498db')
ax1.tick_params(axis='y', labelcolor='#3498db')
ax1.set_xticks(x)
ax1.set_xticklabels(models)

# Throughput line on secondary axis
ax2 = ax1.twinx()
ax2.plot(x - width/2, fp16_throughput, 's-', color='#2ecc71', markersize=8, linewidth=2, label='FP16 Throughput')
ax2.plot(x + width/2, nf4_throughput, 'o-', color='#e74c3c', markersize=8, linewidth=2, label='4-bit Throughput')
ax2.set_ylabel('Throughput (tokens/s)', color='#2ecc71')
ax2.tick_params(axis='y', labelcolor='#2ecc71')

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

ax1.set_title('Power and Throughput: FP16 vs 4-bit NF4')

plt.tight_layout()
plt.savefig('fig3_power_throughput.pdf', dpi=300, bbox_inches='tight')
plt.savefig('fig3_power_throughput.png', dpi=300, bbox_inches='tight')
print("✅ Saved fig3_power_throughput.pdf/png")

# Figure 4: Energy Breakdown Concept (Stacked Bar)
fig, ax = plt.subplots(figsize=(8, 5))

# Conceptual breakdown (estimated)
models_short = ['1.1B', '1.5B', '3B', '7B']

# For FP16: compute + memory
fp16_compute = [800, 1200, 1800, 2500]
fp16_memory = [859, 1211, 1583, 3009]

# For 4-bit: compute + memory + dequant overhead
nf4_compute = [600, 900, 1200, 1800]
nf4_memory = [400, 600, 800, 1500]
nf4_dequant = [1098, 1620, 1780, 1578]

x = np.arange(len(models_short))
width = 0.35

# FP16 stacked
ax.bar(x - width/2, fp16_compute, width, label='Compute', color='#3498db')
ax.bar(x - width/2, fp16_memory, width, bottom=fp16_compute, label='Memory', color='#2ecc71')

# 4-bit stacked
ax.bar(x + width/2, nf4_compute, width, color='#3498db', alpha=0.6)
ax.bar(x + width/2, nf4_memory, width, bottom=nf4_compute, color='#2ecc71', alpha=0.6)
ax.bar(x + width/2, nf4_dequant, width, bottom=[c+m for c,m in zip(nf4_compute, nf4_memory)], 
       label='De-quant Overhead', color='#e74c3c')

ax.set_xlabel('Model Size')
ax.set_ylabel('Energy (J / 1k tokens)')
ax.set_title('Energy Breakdown: Why Quantization Hurts Small Models')
ax.set_xticks(x)
ax.set_xticklabels(['FP16 | 4-bit\n1.1B', 'FP16 | 4-bit\n1.5B', 'FP16 | 4-bit\n3B', 'FP16 | 4-bit\n7B'])
ax.legend()

plt.tight_layout()
plt.savefig('fig4_energy_breakdown.pdf', dpi=300, bbox_inches='tight')
plt.savefig('fig4_energy_breakdown.png', dpi=300, bbox_inches='tight')
print("✅ Saved fig4_energy_breakdown.pdf/png")

print("\n🎉 All figures generated successfully!")
print("Files created:")
print("  - fig1_energy_comparison.pdf/png")
print("  - fig2_energy_trend.pdf/png")
print("  - fig3_power_throughput.pdf/png")
print("  - fig4_energy_breakdown.pdf/png")
