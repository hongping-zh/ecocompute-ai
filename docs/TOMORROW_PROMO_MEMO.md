# EcoCompute AI 宣传备忘录

**日期**：2026年1月30日（明天执行）

**目标**：利用 RTX 5090 实验数据宣传 EcoCompute AI 项目

---

## 🎯 核心卖点

### 1. 独家数据：RTX 5090 能效悖论

> **"4-bit 量化在小模型上反而更耗能 26-29%"**

这是全网首个在 RTX 5090 (Blackwell) 上的量化能效实测数据，具有极高的新闻价值。

### 2. 智能计算器

**链接**：https://hongping-zh.github.io/ecocompute-ai/calculator/

- 实时估算 LLM 训练/推理的碳足迹
- **新功能**：量化选择器 + 智能警告（< 3B 模型不建议 4-bit）

---

## 📣 宣传渠道 & 内容

### 1. Twitter/X 推文

```
🔬 We ran the FIRST energy efficiency benchmark on RTX 5090 (Blackwell)

Surprising finding: 4-bit quantization uses 26% MORE energy on small models!

📊 TinyLlama-1.1B:
- FP16: 1659 J/1k tokens
- 4-bit: 2098 J/1k tokens (+26.5%)

Try our free calculator: https://hongping-zh.github.io/ecocompute-ai/calculator/

#GreenAI #LLM #RTX5090
```

### 2. Reddit 帖子

**Subreddits**: r/MachineLearning, r/LocalLLaMA, r/nvidia

**标题**: `[R] First RTX 5090 Energy Benchmark: 4-bit Quantization Paradox for Small Models`

**内容要点**:
- 实验环境：RTX 5090, PyTorch 2.10, CUDA 12.8
- 关键发现：< 3B 模型量化反而更耗能
- 功耗限制实验证明是 kernel 瓶颈
- 链接到计算器和 GitHub

### 3. Hacker News

**标题**: `Show HN: EcoCompute AI – LLM Carbon Footprint Calculator with RTX 5090 Benchmark Data`

### 4. LinkedIn 帖子

面向企业用户，强调：
- Green AI 合规性
- 成本优化（能耗 = 电费）
- 可量化的碳足迹报告

### 5. 微信公众号/知乎

中文版宣传，标题建议：
- 《RTX 5090 首测：4-bit 量化的能耗陷阱》
- 《小模型量化反而更费电？我们用 5090 做了实验》

---

## 📊 数据亮点（用于宣传）

### 能效对比表

| 模型 | FP16 能耗 | 4-bit 能耗 | 变化 |
|------|-----------|------------|------|
| TinyLlama-1.1B | 1659 J/1k | 2098 J/1k | **+26.5%** ⚠️ |
| Qwen2-1.5B | 2411 J/1k | 3120 J/1k | **+29.4%** ⚠️ |
| Qwen2-7B | 5509 J/1k | 4878 J/1k | **-11.4%** ✅ |

### 功耗限制实验（独家）

| 功耗限制 | TinyLlama 4-bit 惩罚 |
|----------|---------------------|
| 575W | -24.3% |
| 300W | -13.6% |
| 150W | -11.3% |

**结论**：即使模拟低功耗环境，小模型量化仍然更耗能

---

## 🔗 关键链接

| 资源 | 链接 |
|------|------|
| **GitHub 仓库** | https://github.com/hongping-zh/ecocompute-ai/ |
| **在线计算器** | https://hongping-zh.github.io/ecocompute-ai/calculator/ |
| **英文报告** | RTX5090_Energy_Benchmark_Report_EN.md |
| **bitsandbytes Issue** | 待提交 |

---

## ✅ 明天执行清单

1. [ ] **提交 bitsandbytes Issue**（使用 `bitsandbytes_issue_template.md`）
2. [ ] **发布 Twitter 推文**
3. [ ] **发布 Reddit 帖子**（r/MachineLearning, r/LocalLLaMA）
4. [ ] **提交 Hacker News**
5. [ ] **更新 GitHub README**（添加 RTX 5090 实验数据摘要）
6. [ ] **准备中文宣传内容**（知乎/公众号）

---

## 💡 宣传话术建议

### 英文版

> "We discovered that 4-bit quantization on small models (<3B) actually INCREASES energy consumption by 26-29% on RTX 5090. This challenges the common assumption that quantization always saves energy. Try our free calculator to estimate your LLM's carbon footprint!"

### 中文版

> "我们在 RTX 5090 上发现：小模型（<3B）使用 4-bit 量化反而增加 26-29% 能耗！这颠覆了'量化一定省电'的常识。欢迎使用我们的免费计算器估算你的 LLM 碳足迹！"

---

## 🎨 可视化素材（建议制作）

1. **能效对比柱状图**：FP16 vs 4-bit 各模型能耗
2. **拐点曲线图**：模型规模 vs 量化收益
3. **功耗限制实验折线图**：功耗限制 vs 能耗惩罚

---

*备忘录创建于 2026年1月29日晚*
*明天首要任务执行*
