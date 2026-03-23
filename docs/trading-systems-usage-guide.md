# 📊 股票分析系统使用指南
**创建时间**: 2026-03-23 10:53 AM (UTC+8)  
**版本**: 1.0.0  
**维护者**: 御坂美琴一号

---

## 🎯 系统概览

本系统包含三个主要部分：

1. **TradingAgents** - 多智能体股票分析系统（基于 LangGraph）
2. **Backtrader** - 模拟交易系统（Vue 3 前端 + FastAPI 后端）
3. **Stock CLI** - 命令行股票查询工具

---

## 📦 系统 1: TradingAgents（多智能体分析）

### 位置
```
/home/claw/.openclaw/workspace/projects/technical/TradingAgents
```

### 功能
- 多智能体协作的股票分析系统
- 支持多空辩论机制
- 支持多种 LLM 提供商（OpenAI、Google、Anthropic、本地 Ollama 等）
- BM25 记忆系统
- 模拟真实交易公司团队协作模式

### 核心智能体
| 角色 | 职责 |
|------|------|
| Market Analyst | 技术分析（MACD、RSI、布林带等） |
| Social Media Analyst | 社交媒体情绪分析 |
| News Analyst | 新闻和宏观经济分析 |
| Fundamentals Analyst | 基本面和财务分析 |
| Bull Researcher | 多头辩论 |
| Bear Researcher | 空头辩论 |
| Research Manager | 辩论总结 |
| Trader | 交易决策 |
| Risk Management | 风险评估 |
| Portfolio Manager | 投资组合审批 |

### 使用方法

#### Python API
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 基本用法
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
final_state, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)  # 输出：BUY / HOLD / SELL

# 自定义配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-5.2"
config["quick_think_llm"] = "gpt-5-mini"
config["max_debate_rounds"] = 2

ta = TradingAgentsGraph(debug=True, config=config)
final_state, decision = ta.propagate("AAPL", "2026-02-01")
```

#### CLI 使用
```bash
cd /home/claw/.openclaw/workspace/projects/technical/TradingAgents
python -m cli.main
```

### 配置文件位置
```
/home/claw/.openclaw/workspace/projects/technical/TradingAgents/tradingagents/default_config.py
```

---

## 📦 系统 2: Backtrader 模拟交易系统

### 架构
```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 前端 (前端)                          │
│  http://localhost:3000                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI 后端 (后端)                          │
│  http://localhost:8080                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Backtrader 模拟交易                             │
└─────────────────────────────────────────────────────────────┘
```

### 服务状态
- **前端**: http://localhost:3000 ✅ 运行中
- **后端**: http://localhost:8080 ✅ 运行中

### 快速命令

#### 前端服务
```bash
# 启动
~/.openclaw/scripts/stock-frontend.sh start

# 查看状态
~/.openclaw/scripts/stock-frontend.sh status

# 重启
~/.openclaw/scripts/stock-frontend.sh restart

# 停止
~/.openclaw/scripts/stock-frontend.sh stop

# 查看日志
~/.openclaw/scripts/stock-frontend.sh logs
```

#### 后端服务
```bash
# 启动
~/.openclaw/scripts/stock-api.sh start

# 查看状态
~/.openclaw/scripts/stock-api.sh status

# 重启
~/.openclaw/scripts/stock-api.sh restart

# 停止
~/.openclaw/scripts/stock-api.sh stop

# 查看日志
~/.openclaw/scripts/stock-api.sh logs
```

### API 端点
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/portfolio/summary` | 投资组合摘要 |
| GET | `/api/portfolio/positions` | 当前持仓 |
| POST | `/api/trade/buy` | 买入股票 |
| POST | `/api/trade/sell` | 卖出股票 |
| GET | `/api/trade/history` | 交易历史 |
| GET | `/api/stock/price/{symbol}` | 股票价格 |
| GET | `/api/analysis/summary` | 投资分析摘要 |
| GET | `/api/news` | 新闻摘要 |

### 前端功能模块
1. **概览页** - 总览、持仓、分析、交易、新闻
2. **持仓管理** - 持仓列表、排序、饼图
3. **K 线图表** - 价格走势、成交量、技术指标
4. **投资分析** - 夏普比率、最大回撤、AI 建议
5. **新闻摘要** - 实时新闻、情绪分类
6. **交易记录** - 交易流水、费用汇总

### 配置文件
- **前端**: `~/.openclaw/workspace/stock-frontend/`
- **后端**: `~/.openclaw/workspace/backtrader/scripts/api_server.py`
- **模拟交易**: `~/.openclaw/workspace/backtrader/scripts/simulated_trading.py`

---

## 📦 系统 3: Stock CLI（命令行工具）

### 位置
```
/home/claw/.openclaw/workspace/backup-content/scripts/stock_cli.py
```

### 功能
- 实时股票行情查询
- 支持中文名称和股票代码
- 显示关键指标：现价、涨跌幅、成交量、市值等

### 使用方法
```bash
# 通过股票代码查询
python /home/claw/.openclaw/workspace/backup-content/scripts/stock_cli.py 600028

# 通过股票名称查询
python /home/claw/.openclaw/workspace/backup-content/scripts/stock_cli.py 中国石化
```

### 支持的股票
- 中国石化 (600028)
- 中国平安 (601318)
- 贵州茅台 (600519)
- 宁德时代 (300750)
- 比亚迪 (002594)
- 招商银行 (600036)
- 万科 A (000002)
- 平安银行 (000001)

---

## 🔄 同步更新说明

### 1. 代码更新
```bash
# TradingAgents 代码更新
cd /home/claw/.openclaw/workspace/projects/technical/TradingAgents
git pull origin main

# 查看更新内容
git log --oneline -10
```

### 2. 记忆文件更新
- **TradingAgents 分析**: `memory/trading-agents-analysis.md`
- **系统架构**: `memory/2026-03-17-stock-system.md`
- **前端配置**: `memory/2026-03-17-stock-frontend.md`
- **最近交易**: `memory/stock-report-2026-03-10.md`

### 3. Skill 创建
可以创建以下 OpenClaw Skill：

#### 3.1 trading-agents-skill
**功能**: 调用 TradingAgents 进行股票分析

**SKILL.md 内容**:
```markdown
# TradingAgents 股票分析技能

## 功能
调用 TradingAgents 多智能体系统进行股票分析

## 使用方法
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
final_state, decision = ta.propagate("NVDA", "2026-01-15")
```

## 配置
- LLM 提供商：OpenAI、Google、Anthropic、本地 Ollama
- 辩论轮次：默认 1 轮
- 最大递归：100 次
```

#### 3.2 stock-query-skill
**功能**: 命令行股票查询

**SKILL.md 内容**:
```markdown
# 股票查询技能

## 功能
通过命令行工具查询实时股票行情

## 使用方法
```bash
python /home/claw/.openclaw/workspace/backup-content/scripts/stock_cli.py <股票代码或名称>
```

## 示例
- `python stock_cli.py 600028`
- `python stock_cli.py 中国石化`
```

---

## 📊 使用流程

### 场景 1: 单只股票深度分析
1. **使用 TradingAgents**:
   ```python
   ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
   final_state, decision = ta.propagate("NVDA", "2026-03-23")
   ```
2. **查看结果**: 输出 BUY/HOLD/SELL 决策

### 场景 2: 实时行情查询
```bash
python /home/claw/.openclaw/workspace/backup-content/scripts/stock_cli.py 中国石化
```

### 场景 3: 模拟交易
1. 启动前端：`~/.openclaw/scripts/stock-frontend.sh start`
2. 启动后端：`~/.openclaw/scripts/stock-api.sh start`
3. 访问 http://localhost:3000
4. 进行模拟买卖操作

---

## 🔧 常见问题

### Q1: TradingAgents 导入失败
**解决方案**:
```bash
cd /home/claw/.openclaw/workspace/projects/technical/TradingAgents
pip install -e .
```

### Q2: 前端服务启动失败
**解决方案**:
```bash
# 检查端口占用
lsof -i :3000

# 停止旧进程
~/.openclaw/scripts/stock-frontend.sh stop

# 重新启动
~/.openclaw/scripts/stock-frontend.sh start
```

### Q3: 后端 API 无法连接
**解决方案**:
```bash
# 查看日志
~/.openclaw/scripts/stock-api.sh logs

# 检查服务状态
~/.openclaw/scripts/stock-api.sh status
```

---

## 📚 相关文档

- **TradingAgents README**: `projects/technical/TradingAgents/README.md`
- **技术分析报告**: `trading-agents-analysis.md`
- **系统架构图**: `memory/2026-03-17-stock-system.md`
- **前端文档**: `memory/2026-03-17-stock-frontend.md`

---

## 💡 最佳实践

1. **定期更新代码**: 使用 `git pull` 保持代码最新
2. **检查服务状态**: 使用 `status` 命令检查服务运行情况
3. **查看日志**: 遇到问题时优先查看日志文件
4. **备份配置**: 定期备份配置文件和交易数据
5. **记录决策**: 将重要的分析结果记录到记忆文件中

---

**Created by 御坂美琴一号** ⚡  
**Last Updated**: 2026-03-23 10:53 AM (UTC+8)
