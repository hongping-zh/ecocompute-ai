# JOSS (Journal of Open Source Software) 投稿指南

## 什么是 JOSS？

JOSS 是一个同行评审的开源软件期刊，专门发表研究软件。它：
- **免费发表**（无 APC 费用）
- **无需背书**
- **快速审稿**（通常 4-8 周）
- **获得 DOI**，可被正式引用
- **影响因子**：约 5.0

## EcoCompute AI 是否适合 JOSS？

✅ **适合的条件**：
- 开源软件（需要 GitHub 仓库）
- 有研究价值
- 有文档和测试
- 可安装和使用

⚠️ **需要准备**：
- 完整的 GitHub 仓库
- README 文档
- 安装说明
- 使用示例
- 单元测试（推荐）

## 投稿前准备清单

### 1. GitHub 仓库要求

```
ecocompute-ai/
├── README.md              # 项目介绍、安装、使用说明
├── LICENSE                # 开源许可证（MIT、Apache 等）
├── CONTRIBUTING.md        # 贡献指南
├── CODE_OF_CONDUCT.md     # 行为准则
├── setup.py / pyproject.toml  # Python 包配置
├── requirements.txt       # 依赖
├── ecocompute/           # 源代码
│   ├── __init__.py
│   ├── calculator.py
│   └── benchmark.py
├── tests/                # 测试
│   └── test_calculator.py
├── docs/                 # 文档
│   └── index.md
└── paper/                # JOSS 论文
    ├── paper.md
    └── paper.bib
```

### 2. 论文文件

已创建：
- `paper.md` - 论文正文（Markdown 格式）
- `paper.bib` - 参考文献

### 3. 软件要求

- [ ] 有版本号（如 v1.0.0）
- [ ] 有 DOI（可通过 Zenodo 获取）
- [ ] 有安装说明
- [ ] 有使用文档
- [ ] 有测试覆盖

## 投稿步骤

### Step 1: 准备 GitHub 仓库

确保仓库包含所有必需文件，并创建一个 release。

### Step 2: 获取 Zenodo DOI

1. 登录 https://zenodo.org
2. 连接 GitHub 账号
3. 为仓库创建 release
4. Zenodo 自动生成 DOI

### Step 3: 提交预检查

访问 https://joss.theoj.org/papers/new

填写：
- 仓库 URL
- 软件版本
- 论文标题

系统会自动检查仓库是否符合要求。

### Step 4: 正式提交

通过预检查后：
1. 确认作者信息
2. 提交论文
3. 等待编辑分配审稿人

### Step 5: 审稿过程

- 审稿在 GitHub Issue 上公开进行
- 审稿人会检查软件质量和论文内容
- 根据反馈修改
- 通过后发表

## 时间线

| 阶段 | 预计时间 |
|------|----------|
| 预检查 | 1-2 天 |
| 编辑分配 | 1 周 |
| 审稿 | 2-4 周 |
| 修改 | 1-2 周 |
| 发表 | 1 周 |
| **总计** | **4-8 周** |

## 注意事项

1. **论文长度**：JOSS 论文通常 1-2 页，重点是软件功能而非研究发现
2. **代码质量**：审稿人会检查代码，确保可运行
3. **文档完整**：README 和 API 文档很重要
4. **响应及时**：审稿过程中及时回复

## 参考资源

- JOSS 官网：https://joss.theoj.org
- 投稿指南：https://joss.readthedocs.io/en/latest/submitting.html
- 论文示例：https://joss.theoj.org/papers

---

## 当前状态

| 文件 | 状态 |
|------|------|
| paper.md | ✅ 已创建 |
| paper.bib | ✅ 已创建 |
| GitHub 仓库 | ⏳ 需要整理 |
| Zenodo DOI | ⏳ 待创建 |
| 测试代码 | ⏳ 需要添加 |
