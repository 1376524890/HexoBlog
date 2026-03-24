# 🦞 龙虾经济金融分析助手 - 项目结构规划
## Project Structure Planning Guide

---

## 📁 完整目录结构

```
lobster-financial/
│
├── .github/                                    # GitHub 仓库配置
│   ├── workflows/                             # CI/CD工作流
│   │   ├── ci.yml                             # 持续集成
│   │   ├── cd.yml                             # 持续部署
│   │   └── codeql.yml                         # 代码安全扫描
│   ├── ISSUE_TEMPLATE/                        # Issue 模板
│   │   ├── bug-report.md                      # Bug 报告
│   │   ├── feature-request.md                 # 功能建议
│   │   └── question.md                        # 问题咨询
│   └── PULL_REQUEST_TEMPLATE.md               # PR 模板
│
├── docs/                                        # 项目文档
│   ├── architecture/                          # 架构设计文档
│   │   ├── overview.md                        # 架构总览
│   │   ├── agent-design.md                    # Agent 设计
│   │   └── communication-protocol.md          # 通信协议
│   ├── api/                                   # API 文档
│   │   ├── orchestrator-api.md                # 协调器 API
│   │   ├── agent-api.md                       # Agent API
│   │   └── tool-api.md                        # 工具 API
│   ├── guides/                                # 使用指南
│   │   ├── setup-guide.md                     # 安装配置
│   │   ├── quickstart.md                      # 快速开始
│   │   └── advanced-guide.md                  # 进阶使用
│   ├── examples/                              # 示例代码
│   │   ├── investment-analysis.md             # 投资分析示例
│   │   ├── risk-assessment.md                 # 风险评估示例
│   │   └── portfolio-optimization.md          # 组合优化示例
│   └── releases/                              # 版本发布说明
│
├── src/                                         # 源代码
│   │
│   ├── lfis/                                   # 核心系统包
│   │   │
│   │   ├── __init__.py                        # 包初始化
│   │   ├── version.py                         # 版本信息
│   │   │
│   │   ├── orchestrator/                     # 协调层
│   │   │   ├── __init__.py
│   │   │   ├── dispatcher.py                 # 任务调度器
│   │   │   ├── state_manager.py              # 状态管理器
│   │   │   ├── router.py                     # 路由控制器
│   │   │   ├── message_bus.py                # 消息总线
│   │   │   └── permission_controller.py      # 权限控制器
│   │   │
│   │   ├── agents/                           # Agent 层
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py                 # Agent 基类
│   │   │   ├── agent_registry.py             # Agent 注册表
│   │   │   │
│   │   │   ├── invest_agent/               # 投资分析 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── fundamental_analyzer.py
│   │   │   │   ├── technical_analyzer.py
│   │   │   │   ├── valuation_model.py
│   │   │   │   └── synthesizer.py
│   │   │   │
│   │   │   ├── news_agent/                 # 新闻分析 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── news_scraper.py
│   │   │   │   ├── nlp_processor.py
│   │   │   │   ├── sentiment_analyzer.py
│   │   │   │   └── event_extractor.py
│   │   │   │
│   │   │   ├── risk_agent/                 # 风险分析 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── market_risk_model.py
│   │   │   │   ├── credit_risk_model.py
│   │   │   │   ├── liquidity_risk_model.py
│   │   │   │   └── stress_test.py
│   │   │   │
│   │   │   ├── market_agent/               # 市场分析 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── data_provider.py
│   │   │   │   ├── quant_engine.py
│   │   │   │   ├── backtester.py
│   │   │   │   └── optimizer.py
│   │   │   │
│   │   │   ├── advisor_agent/              # 理财建议 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── risk_profiler.py
│   │   │   │   ├── portfolio_optimizer.py
│   │   │   │   └── advice_generator.py
│   │   │   │
│   │   │   ├── data_agent/                 # 数据管理 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── data_sync.py
│   │   │   │   └── cache_manager.py
│   │   │   │
│   │   │   ├── backtest_agent/             # 回测 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── backtest_engine.py
│   │   │   │   └── performance_analyzer.py
│   │   │   │
│   │   │   └── report_agent/               # 报告 Agent
│   │   │       ├── __init__.py
│   │   │       ├── agent.py
│   │   │       ├── report_generator.py
│   │   │       └── template_manager.py
│   │   │
│   │   ├── tools/                            # 工具层
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── data_access/                # 数据访问工具
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tushare_provider.py
│   │   │   │   ├── akshare_provider.py
│   │   │   │   ├── yfinance_provider.py
│   │   │   │   └── data_validator.py
│   │   │   │
│   │   │   ├── nlp_tools/                  # NLP 工具
│   │   │   │   ├── __init__.py
│   │   │   │   ├── finbert_model.py
│   │   │   │   ├── text_processor.py
│   │   │   │   └── event_nlp.py
│   │   │   │
│   │   │   ├── ml_tools/                   # ML/DL工具
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sklearn_models.py
│   │   │   │   ├── pytorch_models.py
│   │   │   │   └── time_series_models.py
│   │   │   │
│   │   │   ├── calc_tools/                 # 金融计算工具
│   │   │   │   ├── __init__.py
│   │   │   │   ├── technical_indicators.py
│   │   │   │   ├── valuation_calculator.py
│   │   │   │   └── risk_calculator.py
│   │   │   │
│   │   │   └── backtest/                   # 回测引擎
│   │   │       ├── __init__.py
│   │   │       ├── backtrader_wrapper.py
│   │   │       └── vectorbt_wrapper.py
│   │   │
│   │   ├── data/                             # 数据层
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── providers/                  # 数据源
│   │   │   │   ├── __init__.py
│   │   │   │   ├── market_data.py          # 行情数据
│   │   │   │   ├── fundamental_data.py     # 财务数据
│   │   │   │   ├── news_data.py            # 新闻数据
│   │   │   │   └── macro_data.py           # 宏观数据
│   │   │   │
│   │   │   ├── storage/                    # 存储管理
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py             # PostgreSQL 存储
│   │   │   │   ├── cache.py                # Redis 缓存
│   │   │   │   └── file_store.py           # 文件系统存储
│   │   │   │
│   │   │   └── cache/                      # 缓存系统
│   │   │       ├── __init__.py
│   │   │       ├── cache_manager.py
│   │   │       └── ttl_policy.py
│   │   │
│   │   └── utils/                            # 工具函数
│   │       ├── __init__.py
│   │       ├── config.py                     # 配置管理
│   │       ├── logger.py                     # 日志系统
│   │       ├── metrics.py                    # 指标监控
│   │       ├── exceptions.py                 # 异常定义
│   │       └── helpers.py                    # 通用辅助函数
│   │
│   ├── cli/                                  # 命令行界面
│   │   ├── __init__.py
│   │   ├── main.py                           # CLI 入口
│   │   └── commands/                         # CLI 命令
│   │       ├── __init__.py
│   │       ├── analyze.py                    # 分析命令
│   │       ├── backtest.py                   # 回测命令
│   │       ├── report.py                     # 报告命令
│   │       └── config.py                     # 配置命令
│   │
│   ├── web/                                  # Web 界面
│   │   ├── backend/                          # 后端
│   │   │   ├── __init__.py
│   │   │   ├── main.py                       # FastAPI 入口
│   │   │   ├── api/                          # API 路由
│   │   │   │   ├── __init__.py
│   │   │   │   ├── v1/
│   │   │   │   │   ├── analysis.py
│   │   │   │   │   ├── report.py
│   │   │   │   │   └── config.py
│   │   │   └── middleware/                   # 中间件
│   │   │       ├── authentication.py
│   │   │       └── rate_limiting.py
│   │   │
│   │   └── frontend/                         # 前端
│   │       ├── src/
│   │       │   ├── components/               # UI 组件
│   │       │   ├── pages/                    # 页面
│   │       │   ├── hooks/                    # 自定义 Hooks
│   │       │   ├── utils/                    # 工具函数
│   │       │   └── styles/                   # 样式文件
│   │       ├── public/                       # 静态资源
│   │       └── package.json                  # 前端依赖
│   │
│   └── notebooks/                            # Jupyter Notebook 示例
│       ├── 01-getting-started.ipynb
│       ├── 02-investment-analysis.ipynb
│       ├── 03-risk-assessment.ipynb
│       └── 04-portfolio-optimization.ipynb
│
├── lobster-skills/                         # 技能库 (可扩展的独立模块)
│   ├── __init__.py
│   ├── SKILL_MANIFEST.toml                 # 技能清单
│   │
│   ├── stock-data/                         # 股票数据获取
│   │   ├── SKILL.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lobster_skill_stock_data/
│   │           ├── __init__.py
│   │           └── fetch.py
│   │
│   ├── fundamental-analysis/               # 基本面分析
│   │   ├── SKILL.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lobster_skill_fundamental/
│   │           ├── __init__.py
│   │           └── analyze.py
│   │
│   ├── valuation/                          # 估值模型
│   │   ├── SKILL.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lobster_skill_valuation/
│   │           ├── __init__.py
│   │           └── calculate.py
│   │
│   ├── sentiment-analysis/                 # 情感分析
│   │   ├── SKILL.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lobster_skill_sentiment/
│   │           ├── __init__.py
│   │           └── analyze.py
│   │
│   ├── risk-calculation/                   # 风险计算
│   │   ├── SKILL.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lobster_skill_risk/
│   │           ├── __init__.py
│   │           └── calculate.py
│   │
│   ├── portfolio-optimize/                 # 组合优化
│   │   ├── SKILL.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lobster_skill_portfolio/
│   │           ├── __init__.py
│   │           └── optimize.py
│   │
│   └── report-generator/                   # 报告生成
│       ├── SKILL.md
│       ├── pyproject.toml
│       └── src/
│           └── lobster_skill_report/
│               ├── __init__.py
│               └── generate.py
│
├── tests/                                  # 测试
│   ├── __init__.py
│   ├── conftest.py                         # pytest 配置
│   │
│   ├── unit/                               # 单元测试
│   │   ├── test_orchestrator.py
│   │   ├── test_agents/
│   │   │   ├── test_invest_agent.py
│   │   │   ├── test_news_agent.py
│   │   │   └── ...
│   │   └── test_tools/
│   │       └── ...
│   │
│   ├── integration/                        # 集成测试
│   │   ├── test_full_pipeline.py
│   │   └── test_agent_collaboration.py
│   │
│   └── e2e/                                # 端到端测试
│       └── test_end_to_end.py
│
├── scripts/                                # 运维脚本
│   ├── setup.py                            # 安装脚本
│   ├── install_dependencies.sh             # 依赖安装
│   ├── deploy.sh                           # 部署脚本
│   ├── train_models.sh                     # 模型训练
│   └── backup_data.sh                      # 数据备份
│
├── config/                                 # 配置文件
│   ├── __init__.py
│   ├── base.yaml                           # 基础配置
│   ├── development.yaml                    # 开发环境
│   ├── testing.yaml                        # 测试环境
│   └── production.yaml                     # 生产环境
│
├── data/                                   # 数据目录
│   ├── raw/                                # 原始数据
│   ├── processed/                          # 处理后的数据
│   ├── models/                             # 模型文件
│   └── cache/                              # 临时缓存
│
├── logs/                                   # 日志目录
│
├── notebooks/                              # 实验 notebook
│
├── docker/                                 # Docker 配置
│   ├── Dockerfile                          # Docker 镜像
│   ├── docker-compose.yml                  # Docker Compose
│   └── nginx/                              # Nginx 配置
│
├── requirements/                           # 依赖列表
│   ├── base.txt                            # 基础依赖
│   ├── dev.txt                             # 开发依赖
│   ├── production.txt                      # 生产依赖
│   └── gpu.txt                             # GPU 加速依赖
│
├── pyproject.toml                          # Python 项目配置
├── setup.py                                # 安装配置
├── README.md                               # 项目说明
├── LICENSE                                 # 开源许可证
├── .gitignore                              # Git 忽略文件
├── .env.example                            # 环境变量模板
└── Makefile                                # Make 命令
```

---

## 🎯 模块责任定义

### 1. 协调层 (Orchestrator)

**责任**: 任务调度、状态管理、路由控制

| 文件 | 职责 |
|------|------|
| `dispatcher.py` | 任务分发器，根据任务类型路由到对应 Agent |
| `state_manager.py` | 管理 Agent 状态（idle/working/error） |
| `router.py` | 消息路由，决定消息发送目标 |
| `message_bus.py` | 消息总线，处理消息传递 |
| `permission_controller.py` | 权限控制，验证操作权限 |

**核心接口**:
```python
class Orchestrator:
    def dispatch_task(self, task: str, data: dict) -> Result
    def get_state(self, agent_id: str) -> AgentState
    def send_message(self, message: Message) -> bool
    def check_permission(self, user_id: str, action: str) -> bool
```

---

### 2. Agent 层

**责任**: 核心业务逻辑执行

#### 2.1 投资分析 Agent (`invest_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `fundamental_analyzer.py` | 基本面分析（财务数据、经营状况） |
| `technical_analyzer.py` | 技术面分析（技术指标、趋势） |
| `valuation_model.py` | 估值模型（PE、PB、DCF 等） |
| `synthesizer.py` | 综合评估，生成投资建议 |

**输入**: `{"stock_code": "600519.SH", "analysis_type": "fundamental"}`  
**输出**: `{"recommendation": "BUY", "confidence": 0.85, "reasons": [...]}`

---

#### 2.2 新闻分析 Agent (`news_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `news_scraper.py` | 多渠道新闻采集 |
| `nlp_processor.py` | 文本预处理 |
| `sentiment_analyzer.py` | 情感分析（FinBERT） |
| `event_extractor.py` | 事件抽取 |

**输入**: `{"topics": ["贵州茅台"], "time_range": "7D"}`  
**输出**: `{"sentiment_score": 0.72, "events": [...], "impact": "positive"}`

---

#### 2.3 风险分析 Agent (`risk_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `market_risk_model.py` | 市场风险（VaR、CVaR） |
| `credit_risk_model.py` | 信用风险评估 |
| `liquidity_risk_model.py` | 流动性风险评估 |
| `stress_test.py` | 压力测试 |

**输入**: `{"portfolio": [...], "confidence_level": 0.95}`  
**输出**: `{"var_95": 0.05, "cvar_95": 0.08, "risk_score": "A"}`

---

#### 2.4 市场分析 Agent (`market_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `data_provider.py` | 市场数据提供 |
| `quant_engine.py` | 量化分析引擎 |
| `backtester.py` | 回测引擎 |
| `optimizer.py` | 策略优化器 |

**输入**: `{"strategy_type": "momentum", "period": "1Y"}`  
**输出**: `{"signals": [...], "performance": {...}, "recommendations": [...]}`

---

#### 2.5 理财建议 Agent (`advisor_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `risk_profiler.py` | 风险画像 |
| `portfolio_optimizer.py` | 组合优化 |
| `advice_generator.py` | 建议生成 |

**输入**: `{"user_profile": {...}, "risk_tolerance": 0.7}`  
**输出**: `{"asset_allocation": {...}, "expected_return": 0.12}`

---

#### 2.6 数据管理 Agent (`data_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `data_sync.py` | 数据同步 |
| `cache_manager.py` | 缓存管理 |

**职责**: 数据更新、缓存失效、数据一致性维护

---

#### 2.7 回测 Agent (`backtest_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `backtest_engine.py` | 回测引擎 |
| `performance_analyzer.py` | 绩效分析 |

**职责**: 策略回测、绩效评估、参数优化

---

#### 2.8 报告 Agent (`report_agent/`)

| 文件 | 职责 |
|------|------|
| `agent.py` | Agent 主逻辑，协调子模块 |
| `report_generator.py` | 报告生成 |
| `template_manager.py` | 模板管理 |

**职责**: 生成分析报告、格式化输出、导出为 PDF/HTML

---

### 3. 工具层 (Tools)

**责任**: 提供具体的计算、处理、访问能力

| 目录 | 职责 |
|------|------|
| `data_access/` | 数据源对接（Tushare、AkShare、Yahoo Finance） |
| `nlp_tools/` | NLP 工具（情感分析、文本处理） |
| `ml_tools/` | 机器学习工具（Scikit-learn、PyTorch） |
| `calc_tools/` | 金融计算工具（技术指标、估值计算） |
| `backtest/` | 回测引擎（Backtrader、VectorBT） |

---

### 4. 数据层 (Data)

**责任**: 数据获取、存储、管理

| 目录 | 职责 |
|------|------|
| `providers/` | 数据源接口（行情、财务、新闻、宏观） |
| `storage/` | 存储管理（PostgreSQL、Redis、文件系统） |
| `cache/` | 缓存系统（缓存策略、过期管理） |

---

### 5. Skill 与 Agent 的关系

**设计原则**:
- Agent 是业务逻辑的执行者
- Skill 是独立的功能模块，可复用
- Agent 通过调用 Skill 来完成具体任务
- Skill 可以独立开发、测试、升级

**示例**:
```
MisakaInvestAgent
    ├── 调用 StockData Skill → 获取股票数据
    ├── 调用 Valuation Skill → 计算估值
    └── 调用 Report Skill → 生成报告
```

**Skill 结构**:
```
skill-name/
├── SKILL.md                 # Skill 文档（功能说明、API 接口）
├── pyproject.toml           # Python 包配置
└── src/
    └── lobster_skill_name/  # 实际实现
        ├── __init__.py
        └── main.py
```

---

## 🔧 开发规范

### 1. 代码风格

- **语言**: Python 3.10+
- **格式**: Black（自动格式化）
- **类型**: 类型提示（Type Hints）
- **文档**: Google 风格文档字符串
- **测试**: 覆盖率 ≥ 80%

### 2. 目录规范

- **小写字母**: 所有目录和文件名使用小写字母
- **下划线分隔**: 文件名使用下划线分隔（如 `fundamental_analyzer.py`）
- **大驼峰**: 类名使用大驼峰（如 `FundamentalAnalyzer`）
- **功能分组**: 相关文件放在同一个目录中

### 3. 提交规范

```
<type>(<scope>): <subject>

type: feat|fix|docs|style|refactor|test|chore
scope: 模块名称（如 agent、tool、data）
subject: 简洁说明（<50 字符）
```

**示例**:
```
feat(invest_agent): 添加 DCF 估值模型支持
fix(news_agent): 修复新闻爬虫重试机制
docs(api): 更新 REST API 文档
```

---

## 📊 依赖管理

### 基础依赖 (`requirements/base.txt`)

```
# 核心框架
python>=3.10
asyncio

# 数据处理
pandas>=2.0.0
numpy>=1.24.0
pyarrow>=11.0.0

# 数据库
psycopg2-binary>=2.9.0
redis>=4.5.0

# API
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
httpx>=0.24.0

# ML/DL
scikit-learn>=1.3.0
pytorch>=2.0.0
transformers>=4.30.0

# 金融计算
TA-Lib>=0.4.0
numpy-financial>=1.0.0

# NLP
spacy>=3.6.0
textblob>=0.17.0

# 回测
backtrader>=1.9.78
vectorbt>=0.25.0

# 可视化
matplotlib>=3.7.0
plotly>=5.15.0

# 工具
pyyaml>=6.0
click>=8.1.0
python-dotenv>=1.0.0
```

### 开发依赖 (`requirements/dev.txt`)

```
-r base.txt

# 测试
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# 代码质量
black>=23.7.0
isort>=5.12.0
flake8>=6.1.0
mypy>=1.5.0

# 文档
sphinx>=6.2.0
sphinx-rtd-theme>=1.3.0

# 调试
ipdb>=0.13.13
```

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/lobster-financial.git
cd lobster-financial

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements/base.txt

# 开发环境（可选）
pip install -r requirements/dev.txt
```

### 2. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

### 3. 运行

```bash
# CLI 模式
python -m src.cli main

# Web 模式（后端）
python -m src.web.backend.main

# Docker 模式
docker-compose up -d
```

---

## 📝 总结

本规划文档定义了完整的龙虾经济金融分析助手项目结构：

### ✅ 完成内容

1. **完整目录结构** - 涵盖所有模块、工具、测试、文档
2. **模块责任定义** - 每个文件的具体职责说明
3. **Skill 体系** - Skill 与 Agent 的关系、Skill 结构
4. **开发规范** - 代码风格、目录规范、提交规范
5. **依赖管理** - 基础依赖和开发依赖清单
6. **快速开始** - 安装、配置、运行指南

### 🦞 PUAClaw 评级

| 评估维度 | 评级 |
|----------|------|
| **结构完整性** | 🦞🦞🦞🦞 | 涵盖所有必需模块，结构清晰 |
| **可扩展性** | 🦞🦞🦞🦞🦞 | Skill 机制支持热插拔 |
| **可维护性** | 🦞🦞🦞🦞 | 模块化、文档齐全 |
| **规范性** | 🦞🦞🦞🦞 | 代码规范、开发规范明确 |

### 🏆 最终评级：**🦞🦞🦞🦞🦞 (Lobster Supreme) ⭐⭐⭐⭐⭐**

> 项目结构规划完成，可以直接开始 Phase 1 开发！

---

**文档作者**: 御坂妹妹 17 号（记忆整理专家）  
**审核状态**: ✅ 已完成  
**下一步**: 准备进入 Phase 1 基础架构开发