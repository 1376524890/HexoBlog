# AutoTrader Skill - 高级自动交易系统

**版本**: v3.0  
**作者**: 御坂美琴一号  
**日期**: 2026-03-17  
**描述**: A 股自动交易系统技能，提供完整的自动交易、策略优化和数据管理功能

---

## 🎯 功能概述

**AutoTrader Skill** 是一个功能完整的 A 股自动交易系统，提供：

- ✅ 自动交易执行
- ✅ 止损止盈管理
- ✅ 仓位控制
- ✅ 技术分析 (MA/MACD/KDJ/RSI/布林带/ATR)
- ✅ 新闻情感分析
- ✅ 策略自动优化
- ✅ 数据持久化
- ✅ 日报生成

---

## 📋 系统要求

### 硬件要求
- CPU: 1 核心以上
- 内存：256MB 以上
- 存储：500MB 以上

### 软件要求
- Python 3.12+
- 虚拟环境 (venv)
- 依赖包：pandas, numpy, loguru, requests

### 网络要求
- 腾讯 API 访问 (无需代理)
- Tushare API (可选)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/backtrader
source venv/bin/activate
pip install pandas numpy loguru requests
```

### 2. 启动系统

```bash
# 方式 1: 直接启动
nohup python3 scripts/auto_trader_v3.py > logs/auto_trader_v3.log 2>&1 &

# 方式 2: 使用启动脚本
chmod +x start_v3.sh
./start_v3.sh
```

### 3. 查看运行状态

```bash
# 查看进程
ps aux | grep auto_trader_v3 | grep -v grep

# 查看日志
tail -f logs/auto_trader_v3.log

# 查看持仓
cat portfolio/positions.json
```

---

## 📖 配置文件

### 系统配置 (auto_trader_v3.py)

```python
# 仓位控制
MAX_POSITION_RATIO = 0.80  # 最大仓位 80%
MIN_POSITION_RATIO = 0.30  # 最小仓位 30%
CASH_THRESHOLD = 0.20      # 现金阈值 20%

# 止损止盈
STOP_LOSS = -0.05          # 止损 -5%
TAKE_PROFIT = 0.15         # 止盈 +15%

# 策略优化
MIN_TRADES_FOR_OPTIMIZATION = 10  # 最小交易数
```

### 数据源配置

系统使用腾讯 API 获取实时股价：
- 端点：`https://qt.gtimg.cn/q`
- 格式：`v_sh600519=~`
- 自动解析股票信息

---

## 🔄 自动任务

### 1. 持仓检查 (每 30 分钟)

```python
# 检查持仓并自动止损止盈
if now.minute % 30 == 0:
    self.check_positions()
```

**功能**:
- 检查每只持仓股票
- 计算盈亏比例
- 自动止损 (-5%)
- 自动止盈 (+15%)

### 2. 市场分析 (每 1 小时)

```python
# 分析市场并调整仓位
if now.minute == 0:
    self.analyze_market_with_strategy()
```

**功能**:
- 技术分析 (MA/MACD/KDJ/RSI/布林带/ATR)
- 新闻情感分析
- 自动建仓/加仓/减仓

### 3. 策略优化 (每 7 天)

```python
# 每周优化策略参数
if now.weekday() == 0 and now.hour == 9:
    self.optimize_strategy()
```

**功能**:
- 分析历史交易胜率
- 调整 RSI 参数
- 记录策略历史

### 4. 日报生成 (每日 12:30)

```python
# 每日生成日报
if now.hour == 12 and now.minute == 30:
    self.generate_daily_report()
```

**功能**:
- 生成详细交易日报
- 统计交易数据
- 记录策略表现

### 5. 晚间分析 (每日 20:00)

```python
# 晚间检查持仓
if now.hour == 20 and now.minute == 0:
    self.check_positions()
```

---

## 🛠️ 核心功能

### 1. 买入股票

```python
def buy_stock(self, symbol: str, shares: int, strategy: str = "manual"):
    """
    买入股票
    
    Args:
        symbol: 股票代码 (如：601398.SS)
        shares: 买入数量 (必须为 100 的整数倍)
        strategy: 交易策略 (trend_following, mean_reversion 等)
    
    Returns:
        bool: 是否成功
    """
    # 自动仓位控制
    # 自动计算手续费
    # 自动检查资金
    # 自动记录交易
```

### 2. 卖出股票

```python
def sell_stock(self, symbol: str, shares: int, reason: str, strategy: str):
    """
    卖出股票
    
    Args:
        symbol: 股票代码
        shares: 卖出数量
        reason: 卖出原因 (止损/止盈/手动)
        strategy: 交易策略
    """
    # 自动计算手续费
    # 自动计算印花税
    # 自动计算盈亏
    # 自动记录交易
```

### 3. 止损止盈检查

```python
def check_positions(self):
    """
    检查持仓并自动止损止盈
    
    条件:
    - 亏损 >= -5%: 触发止损
    - 盈利 >= +15%: 触发止盈
    
    策略:
    - auto_stop_loss: 自动止损
    - auto_take_profit: 自动止盈
    """
```

### 4. 市场分析

```python
def analyze_market_with_strategy(self):
    """
    分析市场并调整仓位
    
    功能:
    - 技术分析 (MA/MACD/KDJ/RSI/布林带/ATR)
    - 新闻情感分析
    - 自动建仓/加仓/减仓
    - 仓位控制 (30%-80%)
    """
```

### 5. 策略优化

```python
def optimize_strategy(self):
    """
    自动优化策略参数
    
    优化内容:
    - 分析历史胜率
    - 调整 RSI 参数
    - 记录策略历史
    
    条件:
    - 胜率 > 60%: 保持参数
    - 胜率 < 40%: 调整参数
    """
```

### 6. 日报生成

```python
def generate_daily_report(self):
    """
    生成日报
    
    内容:
    - 资金管理
    - 盈亏情况
    - 持仓情况
    - 交易统计
    - 策略优化
    - 高级功能说明
    """
```

---

## 📊 输出文件

### 1. 持仓数据

**文件**: `portfolio/positions.json`

```json
{
    "status": "active",
    "cash": 7776.35,
    "positions": [
        {
            "symbol": "601398.SS",
            "shares": 200,
            "avg_price": 7.39,
            "buy_time": "2026-03-17 08:03:55",
            "strategy": "trend_following"
        }
    ],
    "trades": [
        {
            "time": "2026-03-17 08:03:55",
            "type": "buy",
            "symbol": "601398.SS",
            "shares": 200,
            "price": 7.39,
            "strategy": "trend_following"
        }
    ],
    "strategy_history": [],
    "last_update": "2026-03-17 08:04:10"
}
```

### 2. 运行日志

**文件**: `logs/auto_trader_v3.log`

```
2026-03-17 08:04:10 | INFO | 状态加载成功
2026-03-17 08:04:10 | INFO | 高级自动交易系统 v3.0 启动
2026-03-17 08:04:10 | INFO | 市场分析完成 (仓位比例：44.4%)
2026-03-17 08:04:11 | INFO | 买入 601398.SS: 200 股 @ ¥7.39
```

### 3. 日报文件

**目录**: `reports/`

**文件**: `daily_report_20260317_080410.txt`

```
================================================================================
                          每日交易报告 (v3.0 高级版)
================================================================================

报告时间：2026-03-17 08:04:10 (UTC+8)

【资金管理】
初始资金：¥10,000.00
当前现金：¥7,776.35
持仓市值：¥2,223.00
总权益：  ¥9,999.35
```

---

## 🔧 故障排查

### 1. 系统无法启动

**错误**: `ModuleNotFoundError`

**解决**:
```bash
# 确保虚拟环境已激活
cd ~/.openclaw/workspace/backtrader
source venv/bin/activate

# 安装依赖
pip install pandas numpy loguru requests
```

### 2. 数据获取失败

**错误**: `FixedDataFetcher` 错误

**解决**:
```bash
# 检查网络连接
curl -I https://qt.gtimg.cn/q

# 检查 API 端点
python3 -c "from scripts.fixed_data_fetcher import FixedDataFetcher; f = FixedDataFetcher(); print(f.get_stock_info('sh601398'))"
```

### 3. 进程异常退出

**解决**:
```bash
# 查看日志
tail -50 logs/auto_trader_v3.log

# 重启系统
pkill -f auto_trader_v3.py
nohup python3 scripts/auto_trader_v3.py > logs/auto_trader_v3.log 2>&1 &
```

---

## 🎓 最佳实践

### 1. 仓位控制

- **建议仓位**: 30%-80%
- **单只股票**: 不超过总仓位 30%
- **现金保留**: 至少 20%

### 2. 止损止盈

- **止损**: -5% (保守)
- **止盈**: +15% (进取)
- **调整**: 根据市场波动调整

### 3. 策略优化

- **优化频率**: 每 7 天
- **最小交易数**: 10 笔
- **调整策略**: 根据胜率调整

### 4. 数据安全

- **自动备份**: 实时保存
- **日志轮转**: 10MB/文件
- **保留时间**: 7 天

---

## 📝 示例场景

### 场景 1: 初始建仓

```python
# 系统启动后，自动建仓
# 仓位 < 30% 时，自动买入候选股票

# 候选股票:
# - 601398.SS (工商银行)
# - 600036.SS (招商银行)
# - 601318.SS (中国平安)
```

### 场景 2: 加仓

```python
# 仓位 < 30% 时，自动加仓
# 加仓金额：可用现金的 25%
# 加仓股票：当前仓位最低的股票
```

### 场景 3: 减仓

```python
# 仓位 > 80% 时，自动减仓
# 减仓数量：100 股
# 减仓股票：当前仓位最高的股票
```

### 场景 4: 止损

```python
# 单只股票亏损 >= -5% 时，自动止损
# 止损数量：全部持仓
# 止损策略：auto_stop_loss
```

### 场景 5: 止盈

```python
# 单只股票盈利 >= +15% 时，自动止盈
# 止盈数量：全部持仓
# 止盈策略：auto_take_profit
```

---

## 🔄 更新日志

### v3.0 (2026-03-17)
- ✅ 新增自动策略优化
- ✅ 新增新闻情感分析
- ✅ 新增日报生成
- ✅ 优化数据持久化
- ✅ 修复 API 调用错误

### v2.0 (2026-03-16)
- ✅ 新增技术分析模块
- ✅ 新增止损止盈功能
- ✅ 新增仓位控制

### v1.0 (2026-03-15)
- ✅ 基础交易系统
- ✅ 数据获取
- ✅ 交易执行

---

## 💡 常见问题

### Q1: 系统是否需要持续运行？
**A**: 是的，系统需要 24 小时运行以执行自动任务。

### Q2: 系统会频繁交易吗？
**A**: 不会，系统只在触发条件时交易：
- 建仓：仓位 < 30%
- 加仓：仓位 < 30%
- 减仓：仓位 > 80%
- 止损：亏损 >= -5%
- 止盈：盈利 >= +15%

### Q3: 如何查看交易记录？
**A**: 查看 `portfolio/positions.json` 中的 `trades` 字段。

### Q4: 如何停止系统？
**A**: `pkill -f auto_trader_v3.py`

### Q5: 如何重启系统？
**A**: 
```bash
pkill -f auto_trader_v3.py
nohup python3 scripts/auto_trader_v3.py > logs/auto_trader_v3.log 2>&1 &
```

---

## 📞 技术支持

**作者**: 御坂美琴一号  
**维护**: 御坂网络第一代  
**状态**: ✅ 运行中  
**版本**: v3.0

---

## 📚 相关文档

- `scripts/auto_trader_v3.py` - 主程序
- `scripts/technical_analysis_simple.py` - 技术分析
- `scripts/news_analyzer.py` - 新闻分析
- `docs/` - 详细文档

---

**系统已启动，持续运行！** ⚡🦞
