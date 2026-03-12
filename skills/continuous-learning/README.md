# 持续学习进化系统 (Continuous Learning System)

⚡ 自动化技能发现、分析、评估和集成系统

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 功能特性

### 核心功能

1. **Discovery (发现)** - 从 GitHub 搜索和发现潜在的 Skill 项目
   - 关键词搜索
   - 星标数、分叉数过滤
   - 活跃度评估
   - 结果去重和排序

2. **Analysis (分析)** - 深度分析项目代码
   - 自动克隆仓库
   - 代码结构分析
   - 依赖提取
   - Claude Code 深度分析
   - README 内容提取

3. **Evaluation (评估)** - 六维评估矩阵
   - 实用性评分
   - 创新性评分
   - 代码质量评分
   - 文档质量评分
   - 维护性评分
   - 集成度评分
   - 苏格拉底式三问检查

4. **Integration (集成)** - 自动化 Skill 集成
   - 生成 SKILL.md 文件
   - 创建测试用例
   - Git 自动提交
   - 可选的自动推送

## 📦 安装

### 依赖安装

```bash
pip install github3.py GitPython pytest
```

### 配置文件

复制配置模板:

```bash
cp config/default.json config/config.json
```

编辑 `config/config.json` 添加你的配置:

```json
{
  "github": {
    "token": "your-github-token"
  },
  "discovery": {
    "keywords": ["skill", "agent"],
    "min_stars": 10
  }
}
```

## 🚀 使用方法

### 快速开始

#### 完整流程

```bash
python continuous_learning.py --all
```

#### 分步执行

```bash
# 只执行 Discovery
python continuous_learning.py --step discovery

# 只执行 Analysis
python continuous_learning.py --step analysis

# 只执行 Evaluation
python continuous_learning.py --step evaluation

# 只执行 Integration
python continuous_learning.py --step integration
```

### 命令行参数

#### 执行步骤

- `--all` - 执行所有步骤
- `--step <step>` - 指定执行步骤 (可多次指定)
  - `discovery` - 发现项目
  - `analysis` - 分析项目
  - `evaluation` - 评估项目
  - `integration` - 集成项目

#### Discovery 参数

- `--keywords <kw1> <kw2>` - 搜索关键词 (默认：["skill", "agent", "ai"])
- `--min-stars <num>` - 最少星标数 (默认：10)
- `--min-forks <num>` - 最少分叉数 (默认：2)
- `--search-limit <num>` - 搜索限制 (默认：50)

#### Analysis 参数

- `--max-clone-time <seconds>` - 克隆超时时间 (默认：300 秒)
- `--max-projects <num>` - 最多处理的项目数 (默认：10)

#### Evaluation 参数

- `--accept-threshold <score>` - 接受阈值 (默认：7.5)
- `--review-threshold <score>` - 待审查阈值 (默认：6.0)

#### Integration 参数

- `--skip-tests` - 跳过测试
- `--auto-push` - 自动推送到 Git

#### 其他参数

- `--token <github-token>` - GitHub API token (可选)
- `--output-dir <dir>` - 输出目录 (默认：output)
- `--verbose` - 详细输出

## 📋 示例

### 搜索高星技能项目

```bash
python continuous_learning.py \
  --keywords "skill" "agent" "openclaw" \
  --min-stars 50 \
  --search-limit 30
```

### 跳过测试快速集成

```bash
python continuous_learning.py \
  --all \
  --skip-tests
```

### 自定义评估阈值

```bash
python continuous_learning.py \
  --all \
  --accept-threshold 8.0 \
  --review-threshold 7.0
```

## 📊 输出文件

系统会在 `output/` 目录生成以下文件:

- `discovery_results.json` - Discovery 结果
- `analysis_{n}.json` - 项目分析报告
- `evaluation_{n}.json` - 项目评估报告
- `process_state.json` - 流程状态

每个被接受的项目会生成:

```
skills/
└── skill-repo-name/
    ├── SKILL.md      # Skill 文件
    ├── README.md     # 项目说明
    └── tests/
        └── test_skill.py  # 测试用例
```

## 🔧 配置详解

### 配置选项

查看 `config/default.json` 的完整配置说明:

```json
{
  "github": {
    "token": "GitHub API token (可选)",
    "api_base": "API 基础地址"
  },
  "discovery": {
    "keywords": ["搜索关键词"],
    "min_stars": 10,
    "min_forks": 2,
    "limit": 50
  },
  "evaluation": {
    "weights": {
      "practicality": 1.5,
      "innovation": 1.0,
      "code_quality": 1.5,
      "documentation": 1.0,
      "maintenance": 1.2,
      "integration": 1.3
    },
    "accept_threshold": 7.5,
    "review_threshold": 6.0
  }
}
```

## 🧪 测试

运行测试:

```bash
# 运行所有测试
pytest tests/test_continuous_learning.py -v

# 运行特定测试
pytest tests/test_continuous_learning.py::TestDiscoveryEngine -v

# 生成覆盖率报告
pytest tests/test_continuous_learning.py --cov=. --cov-report=html
```

## 🏗️ 项目结构

```
continuous-learning/
├── continuous_learning.py    # 主程序
├── discovery.py              # Discovery 模块
├── analysis.py               # Analysis 模块
├── evaluation.py             # Evaluation 模块
├── integration.py            # Integration 模块
├── config/
│   └── default.json          # 配置文件模板
├── tests/
│   └── test_continuous_learning.py  # 测试套件
└── README.md                 # 说明文档
```

## 📝 模块说明

### Discovery 模块

负责从 GitHub 发现潜在 Skill 项目:

- 使用 GitHub API 进行搜索
- 支持关键词、星标数、分叉数过滤
- 自动计算项目评分
- 输出 JSON 格式结果

### Analysis 模块

深度分析项目代码:

- 临时克隆仓库
- 分析代码结构
- 提取依赖信息
- 识别技术栈
- 调用 Claude Code 生成分析报告

### Evaluation 模块

六维评估矩阵:

| 维度 | 权重 | 说明 |
|------|------|------|
| 实用性 | 1.5 | 功能完整性、是否有测试 |
| 创新性 | 1.0 | 是否有独特价值 |
| 代码质量 | 1.5 | 代码组织、依赖管理 |
| 文档质量 | 1.0 | README 完整性 |
| 维护性 | 1.2 | 项目活跃度 |
| 集成度 | 1.3 | 与 OpenClaw 兼容性 |

### Integration 模块

自动化 Skill 集成:

- 生成符合规范的 SKILL.md 文件
- 创建测试用例
- Git 自动提交

## ⚠️ 注意事项

1. **GitHub API 速率限制**
   - 未提供 token 时，每小时最多 60 次请求
   - 建议申请个人访问令牌

2. **临时目录清理**
   - Analysis 模块会创建临时目录
   - 系统会在结束后自动清理

3. **Git 操作**
   - Integration 模块会修改 Git 仓库
   - 建议先备份

## 🐛 故障排查

### 问题 1: Discovery 失败

```bash
# 检查网络连接
ping api.github.com

# 检查 GitHub token
python continuous_learning.py --token your-token
```

### 问题 2: Analysis 超时

```bash
# 增加克隆超时时间
python continuous_learning.py --max-clone-time 600
```

### 问题 3: 测试失败

```bash
# 跳过测试
python continuous_learning.py --skip-tests
```

## 📄 License

MIT License - 自由使用，修改和分发

## 🙏 致谢

- 感谢 [GitHub](https://github.com) 提供代码托管服务
- 感谢 [Claude Code](https://www.anthropic.com/claude) 提供 AI 分析能力
- 基于 [OpenClaw](https://github.com/openclaw) 技能框架构建

---

**御坂妹妹 11 号** - 持续学习进化系统开发完成！⚡
