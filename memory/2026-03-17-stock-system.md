# 📊 股票交易系统完整架构（2026-03-17）

**创建时间**: 2026 年 3 月 17 日 16:10 UTC  
**创建者**: 御坂美琴一号  
**架构**: 前后端分离 + 模拟交易系统

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 前端 (前端)                          │
│  http://localhost:3000 / 3001                               │
│  - 概览页、持仓管理、K 线图表、投资分析、新闻、交易记录        │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI 后端 (后端)                          │
│  http://localhost:8080                                      │
│  - 持仓管理 API                                              │
│  - 交易执行 API                                              │
│  - 股票数据 API                                              │
│  - 分析 API                                                  │
│  - 新闻 API                                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ 内部调用
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              模拟交易系统 (Backtrader)                        │
│  - PortfolioManager (持仓管理)                               │
│  - PerformanceTracker (绩效追踪)                             │
│  - DataFetcher (数据获取)                                    │
│  - SimulatedTradingSystem (主系统)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ 服务状态

| 服务 | 状态 | 端口 | PID |
|------|------|------|-----|
| **Vue 前端** | ✅ 运行中 | 3000/3001 | 1166681 |
| **FastAPI 后端** | ✅ 运行中 | 8080 | 1167728 |

---

## 📁 项目位置

| 组件 | 路径 |
|------|------|
| **Vue 前端** | `~/.openclaw/workspace/stock-frontend` |
| **FastAPI 后端** | `~/.openclaw/workspace/backtrader/scripts/api_server.py` |
| **模拟交易** | `~/.openclaw/workspace/backtrader/scripts/simulated_trading.py` |
| **后端脚本** | `~/.openclaw/scripts/stock-api.sh` |
| **前端脚本** | `~/.openclaw/scripts/stock-frontend.sh` |

---

## 🚀 快速命令

### 前端服务
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

### 后端服务
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

---

## 📊 API 端点

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/portfolio/summary` | 投资组合摘要 |
| GET | `/api/portfolio/positions` | 当前持仓 |
| POST | `/api/trade/buy` | 买入股票 |
| POST | `/api/trade/sell` | 卖出股票 |
| GET | `/api/trade/history` | 交易历史 |
| GET | `/api/stock/price/{symbol}` | 股票价格 |
| GET | `/api/stock/history` | 股票历史数据 |
| GET | `/api/analysis/summary` | 投资分析摘要 |
| GET | `/api/analysis/risk` | 风险分析 |
| GET | `/api/reports/daily` | 每日报告 |
| GET | `/api/news` | 新闻摘要 |
| POST | `/api/strategy/run` | 运行策略 |
| GET | `/health` | 健康检查 |

---

## 🎨 前端功能

### 1. 概览页 (Overview)
- 总权益、可用资金、总盈亏
- 持仓概览（前 5 只股票）
- 系统分析摘要
- 最近交易记录
- 最新资讯推送

### 2. 持仓管理 (Portfolio)
- 完整持仓列表
- 多维度排序（市值、盈亏、涨幅）
- 资产配置可视化饼图
- 个股表现分析

### 3. K 线图表 (Charts)
- 实时价格走势图表
- 成交量分析
- 持仓分布饼图
- 技术指标展示

### 4. 投资分析 (Analysis)
- 性能指标（夏普比率、最大回撤等）
- AI 投资建议
- 市场情绪分析
- 风险评估报告

### 5. 新闻摘要 (News)
- 实时财经新闻
- 情绪分类（利好/中性/利空）
- 多维度筛选和搜索
- 相关股票关联

### 6. 交易记录 (Transactions)
- 完整交易流水
- 买入/卖出统计
- 费用汇总
- CSV 导出功能

---

## 🛠️ 技术栈

### 前端
- **Vue 3** - Composition API
- **TypeScript** - 类型安全
- **Vite 6.0** - 构建工具
- **Tailwind CSS 3.4** - 样式框架
- **Pinia** - 状态管理
- **Vue Router 4** - 路由
- **Chart.js** + **Vue-Chart.js** - 图表
- **Axios** - HTTP 客户端

### 后端
- **FastAPI 0.135** - Web 框架
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器
- **Loguru** - 日志记录
- **Python 3.12** - 语言

### 交易系统
- **Backtrader** - 回测框架
- **Akshare** - 股票数据
- **Pandas** - 数据处理
- **NumPy** - 数值计算

---

## 🔧 系统配置

### 虚拟环境
**位置**: `~/.openclaw/workspace/backtrader/venv`

**已安装包**:
- fastapi
- uvicorn
- loguru
- akshare
- backtrader
- baostock
- ccxt
- pandas
- numpy

### 日志文件
| 文件 | 路径 |
|------|------|
| **前端日志** | `~/.openclaw/logs/stock-frontend.log` |
| **后端日志** | `~/.openclaw/logs/stock-api.log` |
| **后端错误** | `~/.openclaw/logs/stock-api.err` |
| **交易日志** | `~/.openclaw/workspace/backtrader/logs/simulated_trading.log` |

### PID 文件
| 服务 | PID 文件 |
|------|---------|
| **前端** | `~/.openclaw/run/stock-frontend.pid` |
| **后端** | `~/.openclaw/run/stock-api.pid` |

---

## 📈 当前状态

**初始资金**: ¥10,000.00  
**当前现金**: ¥5,552.70  
**持仓数量**: 0 只  
**总权益**: ¥0.00  
**总盈亏**: ¥0.00 (0.00%)  
**交易次数**: 5 次

**交易历史**:
- 2026-03-17 07:00:10 - 买入 601398.SS 100 股 @ ¥7.39
- 2026-03-17 07:00:11 - 买入 601398.SS 100 股 @ ¥7.39
- 2026-03-17 07:05:32 - 买入 601398.SS 100 股 @ ¥7.39
- 2026-03-17 08:00:33 - 买入 601398.SS 100 股 @ ¥7.39
- 2026-03-17 08:03:56 - 买入 601398.SS 200 股 @ ¥7.39 (trend_following)

---

## 🎯 开机自启配置

### Systemd 服务配置（手动配置）

**服务文件**: `/etc/systemd/system/stock-api.service`
**前端服务文件**: `/etc/systemd/system/stock-frontend.service`

**配置步骤**:
1. 复制服务文件：
```bash
sudo cp /home/claw/.openclaw/scripts/stock-api.service /etc/systemd/system/
sudo cp /home/claw/.openclaw/scripts/stock-frontend.service /etc/systemd/system/
```

2. 启用并启动：
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-api.service
sudo systemctl start stock-api.service
sudo systemctl enable stock-frontend.service
sudo systemctl start stock-frontend.service
```

3. 验证：
```bash
sudo systemctl status stock-api.service
sudo systemctl status stock-frontend.service
```

---

## 🐛 常见问题

### Q1: 服务启动失败
**解决方案**:
```bash
# 查看详细日志
tail -f ~/.openclaw/logs/stock-api.log

# 检查端口占用
lsof -i :8080

# 停止旧进程并重启
~/.openclaw/scripts/stock-api.sh stop
~/.openclaw/scripts/stock-api.sh start
```

### Q2: Python 模块缺失
**解决方案**:
```bash
cd ~/.openclaw/workspace/backtrader
./venv/bin/pip install fastapi uvicorn loguru
```

### Q3: 端口被占用
**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8080

# 终止进程
kill -9 <PID>

# 或者使用防火墙规则
```

---

## 📝 维护说明

- **每日**: 检查服务状态、查看日志
- **每周**: 备份交易数据、更新依赖
- **每月**: 清理日志文件、性能优化

**下次维护**: 2026-03-24

---

**Created by 御坂美琴一号** ⚡  
**Version**: 1.0.0  
**Date**: 2026-03-17
