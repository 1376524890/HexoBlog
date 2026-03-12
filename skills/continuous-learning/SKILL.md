---
name: continuous-learning
version: 0.1.0
description: "自动化技能发现、分析、评估和集成系统"
author: "御坂妹妹 11 号 (code-executor)"
permissions: level3
keywords:
  - skill
  - github
  - automation
  - learning
  - discovery
  - evaluation
---

# 持续学习进化系统 (Continuous Learning System)

⚡ 自动化技能发现、分析、评估和集成系统

## 🌟 功能特性

### 核心功能

**四步自动化流程**：
1. **Discovery (发现)** - 从 GitHub 搜索高潜力项目
2. **Analysis (分析)** - 深度分析代码结构和依赖
3. **Evaluation (评估)** - 六维评估矩阵 + 苏格拉底式三问
4. **Integration (集成)** - 生成 Skill 文件并集成到系统

### 特色功能

- ✅ **自动化搜索** - GitHub API 智能搜索
- ✅ **深度分析** - Claude Code 深度理解代码
- ✅ **六维评估** - 实用性、创新性、代码质量等
- ✅ **苏格拉底式三问** - 深度思考机制
- ✅ **Skill 生成** - 自动生成符合规范的 SKILL.md
- ✅ **Git 集成** - 自动提交到仓库

## 🚀 使用方法

### 基本用法

```bash
# 完整流程（推荐）
skill continuous-learning --all

# 只执行 Discovery
skill continuous-learning --step discovery

# 分步执行
skill continuous-learning --step discovery --step analysis
skill continuous-learning --step evaluation --step integration
```

### 搜索参数

```bash
# 搜索特定关键词
skill continuous-learning --all --keywords "AI agent" "LLM framework" --min-stars 50

# 自定义评估阈值
skill continuous-learning --all --accept-threshold 8.0 --review-threshold 6.5

# 跳过测试直接集成
skill continuous-learning --all --skip-tests
```

### 输出位置

所有结果保存在 `output/` 目录：
- `discovery_results.json` - 发现的项目列表
- `analysis_{n}.json` - 项目分析报告
- `evaluation_{n}.json` - 项目评估报告
- `skills/` - 集成后的 Skill 文件

## 📋 配置选项

### 命令行参数

#### 执行控制
- `--all` - 执行所有步骤
- `--step <step>` - 指定步骤（discovery|analysis|evaluation|integration）
- `--skip-tests` - 跳过测试
- `--verbose` - 详细输出

#### Discovery 参数
- `--keywords <kw1> <kw2> ...` - 搜索关键词（默认：["skill", "agent", "ai"]）
- `--min-stars <num>` - 最少星标数（默认：10）
- `--min-forks <num>` - 最少分叉数（默认：2）
- `--search-limit <num>` - 搜索限制（默认：50）

#### Analysis 参数
- `--max-clone-time <seconds>` - 克隆超时时间（默认：300）
- `--max-projects <num>` - 最多处理项目数（默认：10）

#### Evaluation 参数
- `--accept-threshold <score>` - 接受阈值（默认：7.5）
- `--review-threshold <score>` - 待审查阈值（默认：6.0）

#### Integration 参数
- `--auto-push` - 自动推送到 Git
- `--output-dir <dir>` - 输出目录（默认：output）

## 🎯 评估标准

### 六维评估矩阵

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| **实用性** | 1.5 | 功能完整性、是否有测试 |
| **创新性** | 1.0 | 独特价值、差异化 |
| **代码质量** | 1.5 | 代码组织、依赖管理 |
| **文档质量** | 1.0 | README 完整性 |
| **维护性** | 1.2 | 项目活跃度、更新频率 |
| **集成度** | 1.3 | 与 OpenClaw 兼容性 |

### 决策阈值

| 总分 | 决策 | 说明 |
|------|------|------|
| **85-100** | ✅ Accept | 直接集成 |
| **70-84** | ⚠️ Review | 需要人工审核 |
| **60-69** | 📁 Archive | 保留到 future 库 |
| **< 60** | ❌ Reject | 拒绝集成 |

## 🧪 苏格拉底式三问检查

每个项目评估时都会问：

1. **"为什么需要这个改进？"** → 问题识别
2. **"改进后真的更好吗？"** → 价值验证
3. **"如果失败了怎么办？"** → 风险评估

## 📊 使用示例

### 搜索高星 AI 项目

```bash
skill continuous-learning \
  --all \
  --keywords "LangChain" "LlamaIndex" "AutoGen" \
  --min-stars 50 \
  --verbose
```

### 只查找并分析（不集成）

```bash
skill continuous-learning \
  --step discovery \
  --step analysis \
  --keywords "Python" "automation" \
  --min-stars 20
```

### 使用自定义配置

```bash
# 创建 config.yaml
echo "search_keywords: ['skill', 'agent']
min_stars: 100
accept_threshold: 8.0" > ~/.openclaw/config/continuous-learning.yaml

# 应用配置
skill continuous-learning --config ~/.openclaw/config/continuous-learning.yaml
```

## 🔧 模块说明

### Discovery 模块

从 GitHub 发现潜在 Skill 项目：
- GitHub API 搜索
- 关键词、星标数、分叉数过滤
- 自动计算项目评分
- 结果去重和排序

### Analysis 模块

深度分析项目代码：
- 临时克隆仓库
- 代码结构分析
- 依赖提取
- README 内容提取
- Claude Code 深度分析

### Evaluation 模块

六维评估矩阵：
- 计算综合评分
- 苏格拉底式三问检查
- 生成评估报告
- 决策建议（accept/review/reject）

### Integration 模块

自动化 Skill 集成：
- 生成 SKILL.md 文件
- 创建 README.md
- 生成测试用例
- Git 自动提交

## 📁 输出文件

```
output/
├── discovery_results.json      # 发现结果
├── analysis_1.json             # 项目分析报告
├── evaluation_1.json           # 项目评估报告
├── process_state.json          # 流程状态
└── skills/                     # 集成后的 Skill
    └── skill-{repo-name}/
        ├── SKILL.md
        ├── README.md
        └── tests/
            └── test_skill.py
```

## ⚠️ 注意事项

### GitHub API 速率限制
- 未提供 token 时，每小时最多 60 次请求
- 建议申请个人访问令牌提升限制

### 临时目录清理
- Analysis 模块会创建临时目录
- 系统会在结束后自动清理

### Git 操作
- Integration 模块会修改 Git 仓库
- 建议先备份重要修改

## 🐛 故障排查

### 问题 1: Discovery 失败

```bash
# 检查网络连接
ping api.github.com

# 使用 GitHub token
skill continuous-learning --token $GITHUB_TOKEN
```

### 问题 2: Analysis 超时

```bash
# 增加克隆超时时间
skill continuous-learning --max-clone-time 600
```

### 问题 3: 测试失败

```bash
# 跳过测试
skill continuous-learning --skip-tests
```

## 📄 License

MIT License

---

**御坂妹妹 11 号 (code-executor) - 持续学习进化系统** ⚡
