# Hugging Face Blog 投稿指南

## 什么是 Hugging Face Blog？

Hugging Face Blog 是 AI/ML 社区最有影响力的技术博客之一，发布在 https://huggingface.co/blog

**优势**：
- 🌍 全球 AI 社区曝光
- 🔗 与 Hugging Face 生态集成
- 📊 高质量技术内容
- 🆓 免费发布
- ⚡ 无需同行评审

## 投稿方式

### 方式 1：社区博客（推荐）

任何 Hugging Face 用户都可以发布社区博客：

1. 登录 https://huggingface.co
2. 进入个人主页
3. 点击 "New" → "Blog Post"
4. 使用 Markdown 编辑器撰写
5. 发布

**优点**：即时发布，无需审核

### 方式 2：官方博客

官方博客需要通过 GitHub PR 提交：

1. Fork https://github.com/huggingface/blog
2. 在 `_blog-posts/` 目录创建新文件
3. 提交 PR
4. 等待 Hugging Face 团队审核

**优点**：更高曝光度，官方背书

## 投稿步骤（社区博客）

### Step 1: 注册/登录 Hugging Face

访问 https://huggingface.co/join

### Step 2: 准备内容

已创建的文件：`huggingface_blog.md`

需要修改：
- [ ] 替换 `your-hf-username` 为你的用户名
- [ ] 替换 GitHub 链接
- [ ] 上传图片到 Hugging Face

### Step 3: 上传图片

1. 在 Hugging Face 创建一个 Dataset 或 Space
2. 上传图片文件：
   - `fig1_energy_comparison.png`
   - `fig2_energy_trend.png`
   - `fig3_power_throughput.png`
3. 获取图片 URL

### Step 4: 发布博客

1. 进入个人主页
2. 点击 "New" → "Blog Post"
3. 粘贴 Markdown 内容
4. 预览并发布

## 投稿步骤（官方博客 PR）

### Step 1: Fork 仓库

```bash
git clone https://github.com/huggingface/blog.git
cd blog
```

### Step 2: 创建博客文件

```bash
# 创建新分支
git checkout -b quantization-energy-blog

# 复制博客文件
cp /path/to/huggingface_blog.md _blog-posts/quantization-energy.md
```

### Step 3: 添加图片

将图片放入 `assets/quantization-energy/` 目录：

```
assets/
└── quantization-energy/
    ├── thumbnail.png
    ├── fig1_energy_comparison.png
    ├── fig2_energy_trend.png
    └── fig3_power_throughput.png
```

### Step 4: 提交 PR

```bash
git add .
git commit -m "Add blog post: When Quantization Hurts"
git push origin quantization-energy-blog
```

然后在 GitHub 上创建 Pull Request。

## 博客格式要求

### Front Matter（头部元数据）

```yaml
---
title: "文章标题"
thumbnail: /blog/assets/xxx/thumbnail.png
authors:
- user: your-hf-username
---
```

### 内容建议

- **长度**：1500-3000 字
- **图片**：至少 2-3 张
- **代码**：包含可运行示例
- **结论**：明确的 takeaway

### 标签

使用相关标签增加曝光：
- `green-ai`
- `quantization`
- `energy-efficiency`
- `sustainability`

## 推广策略

发布后：

1. **Twitter/X**：@huggingface 可能会转发
2. **LinkedIn**：分享到 AI 相关群组
3. **Reddit**：r/MachineLearning, r/LocalLLaMA
4. **Discord**：Hugging Face Discord 服务器

## 当前状态

| 文件 | 状态 |
|------|------|
| huggingface_blog.md | ✅ 已创建 |
| 图片文件 | ✅ 已生成（本地） |
| Hugging Face 账号 | ⏳ 需要确认 |
| 图片上传 | ⏳ 待完成 |

## 下一步行动

1. 登录 Hugging Face
2. 上传图片
3. 发布博客
4. 分享到社交媒体

---

## 参考资源

- Hugging Face Blog: https://huggingface.co/blog
- Blog 仓库: https://github.com/huggingface/blog
- 写作指南: https://huggingface.co/docs/hub/community-blog
