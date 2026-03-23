# 📊 股票分析系统完整清单（2026-03-23 更新）

**更新时间**: 2026-03-23 10:59 AM (UTC+8)  
**维护者**: 御坂美琴一号  
**状态**: ✅ 系统汇总完成

---

## 🎯 系统总览

系统共包含 **7 个核心组件**，涵盖从数据获取、分析、回测到执行的全流程：

```
┌─────────────────────────────────────────────────────────────────┐
│                     股票分析系统全家桶                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  系统 1: Stock Analysis (技能)                                    │
│  - 功能：实时查询、历史数据、大盘指数                           │
│  - 数据源：Tushare + Akshare                                    │
│  - 位置：~/.openclaw/skills/stock-analysis/                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  系统 2: TradingAgents (多智能体分析)                            │
│  - 功能：10 个智能体协作深度分析                                │
│  - 特点：多空辩论、BM25 记忆、多种 LLM 支持                       │
│  - 位置：projects/technical/TradingAgents                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  系统 3: Investment Manager (投资管理)                           │
│  - 功能：回测分析、持仓管理、每日报告                           │
│  - 特点：自动化运行、止损止盈规则                               │
│  - 位置：backtrader/investment_manager.py                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  系统 4: Market Analyzer (市场分析)                              │
│  - 功能：板块轮动、情绪分析、风险评估                           │
│  - 特点：多维度市场综合评估                                     │
│  - 位置：backtrader/scripts/market_analyzer.py                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  系统 5: Backtrader 模拟交易系统                                  │
│  - Vue 3 前端 (localhost:3000)                                    │
│  - FastAPI 后端 (localhost:8080)                                  │
│  - 功能：持仓管理、K 线图、投资分析                               │
│  - 位置：stock-frontend/ + backtrader/scripts/                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  系统 6: Stock CLI (命令行工具)                                  │
│  - 功能：快速股票查询                                           │
│  - 支持：8 只常用股票                                             │
│  - 位置：backup-content/scripts/stock_cli.py                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  系统 7: Feishu 报告推送                                         │
│  - 功能：每 3 小时自动发送股市报告                               │
│  - 位置：scripts/stock_report_to_feishu.py                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 系统 1: Stock Analysis Skill (已存在)

**位置**: `~/.openclaw/skills/stock-analysis/`  
**状态**: ✅ 已安装  
**文档**: `SKILL.md` (3,815 bytes)

### 功能
- 实时股票查询
- 历史数据获取
- 大盘指数查询
- 涨幅榜和行业板块
- 本地缓存机制

### 数据源
- **主数据源**: Tushare (Token 已配置)
- **备用数据源**: Akshare (免费)

### 使用方法
```bash
# 通过技能调用
技能：stock-analysis
参数：查询股票代码
```

### 相关文件
- `SKILL.md` - 使用文档
- `report_generator.py` - 报告生成器
- `stock_tool.py` - 股票工具
- `venv/` - Python 虚拟环境

---

## 📦 系统 2: TradingAgents (已同步)

**位置**: `projects/technical/TradingAgents/`  
**状态**: ✅ 已更新至 v2.0 (589b351)  
**技能**: `trading-agent`

### 功能
- 10 个智能体协作分析
- 多空辩论机制
- BM25 记忆系统
- 多种 LLM 支持

### 智能体角色
1. Market Analyst - 技术分析
2. Social Media Analyst - 情绪分析
3. News Analyst - 新闻分析
4. Fundamentals Analyst - 基本面分析
5. Bull Researcher - 多头辩论
6. Bear Researcher - 空头辩论
7. Research Manager - 辩论总结
8. Trader - 交易决策
9. Risk Management - 风险评估
10. Portfolio Manager - 组合管理

### 相关文件
- `SKILL.md` - 技能文档
- `README.md` - 项目文档
- `trading-graph.py` - 主图架构
- `default_config.py` - 默认配置

---

## 📦 系统 3: Investment Manager (新增) ⭐⭐⭐⭐⭐

**位置**: `backtrader/investment_manager.py`  
**状态**: ✅ 核心系统  
**技能**: 待创建

### 功能
1. **回测分析** - 多策略回测支持
2. **持仓管理** - 自动化持仓记录
3. **每日报告** - 日报自动生成
4. **数据更新** - 自动更新股票数据
5. **工作流** - 完整自动化流程

### 核心配置
- **止损**: -5% (自动执行，不补仓)
- **止盈**: +15% (达到即卖出)
- **仓位**: 30-50% (¥3,000-¥5,000)
- **标的**: 600519 贵州茅台 (首选)

### 自动任务
- 每 30 分钟：检查持仓盈亏
- 每 2 小时：分析市场趋势
- 每天 12:30：生成日报
- 每天 20:00：晚间分析

### 使用方法
```bash
# 运行完整工作流
python investment_manager.py

# 检查进程状态
python investment_manager.py check

# 更新数据
python investment_manager.py update [symbol]

# 运行回测
python investment_manager.py backtest [symbol]

# 运行完整工作流
python investment_manager.py workflow [symbol]
```

### 相关文件
- `investment_manager.py` - 主程序
- `investment-memory.md` - 记忆文件
- `scripts/` - 各种脚本
- `backtests/` - 回测脚本
- `data/` - 数据目录
- `reports/` - 报告目录
- `logs/` - 日志目录

---

## 📦 系统 4: Market Analyzer (新增) ⭐⭐⭐⭐

**位置**: `backtrader/scripts/market_analyzer.py`  
**状态**: ✅ 独立脚本  
**技能**: 待创建

### 功能
1. **多股票技术分析** - 多只股票同时分析
2. **板块轮动检测** - 金融、消费、科技、地产
3. **市场情绪分析** - 新闻情绪评分
4. **资金流向追踪** - 板块资金分布
5. **风险评估预警** - 市场风险评估

### 主要板块
```python
MARKET_LEADERS = {
    '金融': ['601398.SS', '600036.SS', '601318.SS'],  # 银行、保险
    '消费': ['600519.SS', '000858.SZ', '000333.SZ'],  # 白酒、家电
    '科技': ['300750.SZ', '002594.SZ', '600276.SS'],  # 电池、医药
    '地产': ['000002.SZ', '600048.SH'],  # 万科、保利
}
```

### 使用方法
```bash
python market_analyzer.py
```

### 输出示例
```
【市场分析摘要】
  时间：2026-03-23 10:59:00
  风险等级：medium
  建议仓位：50-60%，均衡配置
  市场情绪：bullish (65 分)
```

### 相关文件
- `market_analyzer.py` - 主程序
- `reports/market_analysis.json` - 分析结果
- `scripts/data_fetcher_enhanced.py` - 数据获取
- `scripts/technical_analysis.py` - 技术分析

---

## 📦 系统 5: Backtrader 模拟交易系统 (已存在)

**前端**: `stock-frontend/` (localhost:3000)  
**后端**: `backtrader/scripts/api_server.py` (localhost:8080)  
**状态**: ✅ 运行中

### 功能
- 持仓管理
- K 线图表
- 投资分析
- 新闻摘要
- 交易记录

### 相关文件
- `scripts/simulated_trading.py` - 模拟交易主程序
- `scripts/api_server.py` - 后端 API
- `stock-frontend/` - Vue 3 前端
- `scripts/stock-frontend.sh` - 前端脚本
- `scripts/stock-api.sh` - 后端脚本

---

## 📦 系统 6: Stock CLI (已存在)

**位置**: `backup-content/scripts/stock_cli.py`  
**状态**: ✅ 已封装技能  
**技能**: `stock-query`

### 功能
- 实时行情查询
- 支持 8 只常用股票
- 命令行快速查询

### 使用方法
```bash
python3 ~/.openclaw/scripts/stock-query.sh query 中国石化
```

---

## 📦 系统 7: Feishu 报告推送 (新增) ⭐⭐⭐

**位置**: `scripts/stock_report_to_feishu.py`  
**状态**: ✅ 定时任务  
**频率**: 每 3 小时

### 功能
- 自动获取 A 股市场数据
- 生成股市报告
- 发送到飞书当前会话

### 相关文件
- `stock_report_to_feishu.py` - 推送脚本
- `skills/stock-analysis/report_generator.py` - 报告生成器

---

## 🔄 系统整合建议

### 短期整合 (本周内)

1. **创建 Investment Manager 技能**
   - 封装投资管理系统
   - 添加常用命令
   - 创建使用文档

2. **创建 Market Analyzer 技能**
   - 封装市场分析器
   - 添加板块分析功能
   - 创建使用文档

3. **优化 Feishu 推送**
   - 检查定时任务配置
   - 优化报告格式
   - 添加更多数据源

### 中期整合 (本月内)

1. **统一数据源**
   - 优先使用 Tushare (准确稳定)
   - Akshare 作为备用
   - 实现数据缓存

2. **技能标准化**
   - 所有系统创建统一技能
   - 标准化输出格式
   - 统一错误处理

3. **报告系统整合**
   - 整合各系统报告
   - 统一报告格式
   - 定时自动发送

### 长期整合 (下季度)

1. **数据统一存储**
   - 集中管理所有股票数据
   - 建立数据索引
   - 实现数据共享

2. **决策系统集成**
   - 整合 TradingAgents 分析
   - 结合 Investment Manager 规则
   - 实现自动化交易

3. **监控告警系统**
   - 统一监控各系统状态
   - 异常情况自动告警
   - 系统自愈机制

---

## 📊 系统状态总览

| 系统 | 功能 | 状态 | 技能 | 文档 | 备注 |
|------|------|------|------|------|------|
| Stock Analysis | 实时查询 | ✅ 已安装 | ✅ | ✅ | 双数据源 |
| TradingAgents | 多智能体分析 | ✅ 已更新 | ✅ | ✅ | v2.0 |
| Investment Manager | 投资管理 | ✅ 已存在 | ⏳ | ⏳ | 核心系统 |
| Market Analyzer | 市场分析 | ✅ 已存在 | ⏳ | ⏳ | 独立脚本 |
| Backtrader 模拟交易 | 模拟交易 | ✅ 运行中 | ⏳ | ✅ | Vue3+FastAPI |
| Stock CLI | 命令行查询 | ✅ 已封装 | ✅ | ✅ | 8 只股票 |
| Feishu 推送 | 报告推送 | ✅ 定时任务 | ⏳ | ⏳ | 每 3 小时 |

**图例**:
- ✅ 已完成
- ⏳ 待完善

---

## 💡 快速使用指南

### 实时股票查询
```bash
# 方法 1: Stock Analysis 技能
技能：stock-analysis
参数：查询股票代码

# 方法 2: Stock CLI 技能
python3 ~/.openclaw/scripts/stock-query.sh query 中国石化
```

### 深度股票分析
```bash
# TradingAgents 技能
python3 ~/.openclaw/scripts/trading-agent-skill.py NVDA
```

### 投资分析
```bash
# 投资管理系统
python backtrader/investment_manager.py workflow 600519

# 市场分析器
python backtrader/scripts/market_analyzer.py
```

### 模拟交易
```bash
# 启动前端
~/.openclaw/scripts/stock-frontend.sh start

# 启动后端
~/.openclaw/scripts/stock-api.sh start

# 访问 http://localhost:3000
```

---

## 📚 记忆文件汇总

| 文件 | 内容 | 位置 |
|------|------|------|
| 2026-03-23-stock-system-update.md | TradingAgents 更新记录 | memory/ |
| 2026-03-17-stock-system.md | Backtrader 系统架构 | memory/ |
| 2026-03-17-stock-frontend.md | 前端配置 | memory/ |
| 2026-03-16-investment.md | 投资系统记忆 | memory/ |
| investment-memory.md | 投资管理记忆 | backtrader/ |
| trading-agents-analysis.md | TradingAgents 技术分析 | root/ |

---

## ⚠️ 注意事项

1. **API 密钥配置**: 确保 Tushare Token 和 LLM API 已配置
2. **数据源稳定性**: Akshare 可能偶尔不稳定，有 Tushare 备用
3. **模拟交易**: 所有交易均为模拟，不连接实盘
4. **风险提示**: TradingAgents 仅用于研究，不构成投资建议
5. **定期备份**: 重要数据定期备份到 Git

---

**Created by 御坂美琴一号** ⚡  
**Last Updated**: 2026-03-23 10:59 AM (UTC+8)  
**Status**: ✅ 完整清单已生成

---

## 🎯 下一步行动

1. ⏳ 创建 Investment Manager 技能
2. ⏳ 创建 Market Analyzer 技能
3. ⏳ 优化 Feishu 推送报告
4. ⏳ 统一数据源配置
5. ⏳ 整合报告系统

_系统完整度：70% - 3 个核心系统待创建技能文档_
