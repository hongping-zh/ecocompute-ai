# PR: Add RTX 5090 and H100 to mlco2/impact

## Target Repository
https://github.com/mlco2/impact (Your fork: https://github.com/hongping-zh/impact)

## PR Title
`Add NVIDIA RTX 5090 (Blackwell) and H100 GPU data`

---

## 修改文件

### `data/gpus.csv`

在文件末尾添加以下行：

```csv
RTX 5090,gpu,575,209.2,209.2,363.8,363.8,32,https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
H100 PCIe,gpu,350,51,1979,145.7,5654.3,80,https://www.nvidia.com/en-us/data-center/h100/
H100 SXM5,gpu,700,67,1979,95.7,2827.1,80,https://www.nvidia.com/en-us/data-center/h100/
```

### 数据说明

| GPU | TDP (W) | TFLOPS32 | TFLOPS16 | Memory (GB) | Source |
|-----|---------|----------|----------|-------------|--------|
| **RTX 5090** | 575 | 209.2 | 209.2 | 32 | NVIDIA Official |
| **H100 PCIe** | 350 | 51 | 1979 | 80 | NVIDIA Official |
| **H100 SXM5** | 700 | 67 | 1979 | 80 | NVIDIA Official |

---

## PR Description

### Summary

This PR adds the latest NVIDIA GPUs to the calculator:

1. **RTX 5090 (Blackwell)** - Consumer flagship, 575W TDP
2. **H100 PCIe** - Data center GPU, 350W TDP  
3. **H100 SXM5** - High-performance variant, 700W TDP

### Why This Matters

The RTX 5090 is the first consumer Blackwell GPU, and we have conducted **real-world energy benchmarks** on it:

| Model | Config | Energy (J/1k Tokens) |
|-------|--------|---------------------|
| TinyLlama-1.1B | FP16 | 1659 |
| TinyLlama-1.1B | 4-bit | 2098 (+26.5%) |
| Qwen2-7B | FP16 | 5509 |
| Qwen2-7B | 4-bit | 4878 (-11.4%) |

**Key Finding**: 4-bit quantization increases energy consumption for small models (<3B) on high-performance GPUs.

### Data Sources

- RTX 5090: https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
- H100: https://www.nvidia.com/en-us/data-center/h100/

### Related Work

Full benchmark report available at: https://github.com/hongping-zh/ecocompute-ai

---

## 执行步骤

1. **Clone 你的 Fork**
   ```bash
   git clone https://github.com/hongping-zh/impact.git
   cd impact
   ```

2. **编辑 `data/gpus.csv`**
   在文件末尾添加：
   ```csv
   RTX 5090,gpu,575,209.2,209.2,363.8,363.8,32,https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
   H100 PCIe,gpu,350,51,1979,145.7,5654.3,80,https://www.nvidia.com/en-us/data-center/h100/
   H100 SXM5,gpu,700,67,1979,95.7,2827.1,80,https://www.nvidia.com/en-us/data-center/h100/
   ```

3. **Commit & Push**
   ```bash
   git add data/gpus.csv
   git commit -m "Add NVIDIA RTX 5090 (Blackwell) and H100 GPU data"
   git push origin master
   ```

4. **创建 PR**
   - 访问 https://github.com/hongping-zh/impact
   - 点击 "Contribute" → "Open pull request"
   - 使用上面的 PR Description

---

## 注意事项

- RTX 5090 的 GFLOPS/W 计算：209.2 / 575 ≈ 363.8
- H100 的 FP16 性能是 Tensor Core 性能 (1979 TFLOPS)
- 确保 CSV 格式正确（逗号分隔，无多余空格）

---

*准备于 2026年1月30日*
