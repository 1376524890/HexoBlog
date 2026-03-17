# AutoTrader Skill - 高级自动交易系统

**版本**: v3.0  
**创建时间**: 2026-03-17  
**描述**: A 股自动交易系统技能

---

## 🚀 快速使用

### 启动系统

```bash
cd ~/.openclaw/workspace/backtrader
nohup python3 scripts/auto_trader_v3.py > logs/auto_trader_v3.log 2>&1 &
```

### 查看状态

```bash
ps aux | grep auto_trader_v3
tail -f logs/auto_trader_v3.log
cat portfolio/positions.json
```

### 停止系统

```bash
pkill -f auto_trader_v3.py
```

---

## 📖 详细文档

请查看 [`SKILL.md`](SKILL.md) 获取完整的文档说明。

---

## 📂 文件结构

```
backtrader/
├── scripts/
│   ├── auto_trader_v3.py          # 主程序
│   ├── technical_analysis_simple.py # 技术分析
│   ├── news_analyzer.py           # 新闻分析
│   └── fixed_data_fetcher.py      # 数据获取
├── portfolio/
│   └── positions.json             # 持仓数据
├── logs/
│   └── auto_trader_v3.log         # 运行日志
├── reports/
│   └── daily_report_*.txt         # 日报
├── start_v3.sh                    # 启动脚本
└── README.md                      # 本文件
```

---

## 💡 功能特性

- ✅ 自动交易执行
- ✅ 止损止盈管理
- ✅ 仓位控制 (30%-80%)
- ✅ 技术分析 (MA/MACD/KDJ/RSI/布林带/ATR)
- ✅ 新闻情感分析
- ✅ 策略自动优化 (每周)
- ✅ 数据持久化
- ✅ 日报生成 (每日 12:30)

---

## 📊 配置参数

```python
MAX_POSITION_RATIO = 0.80  # 最大仓位 80%
MIN_POSITION_RATIO = 0.30  # 最小仓位 30%
STOP_LOSS = -0.05          # 止损 -5%
TAKE_PROFIT = 0.15         # 止盈 +15%
```

---

## 🔧 系统要求

- Python 3.12+
- pandas, numpy, loguru, requests
- 虚拟环境 (venv)

---

**维护者**: 御坂美琴一号  
**状态**: ✅ 运行中  
**版本**: v3.0
