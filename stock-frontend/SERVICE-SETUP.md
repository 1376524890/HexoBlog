# 📊 股票交易系统启动说明

## ✅ 当前状态

**前端服务**: ✅ 已启动并运行中  
**访问地址**: http://localhost:3000 或 http://localhost:3001  
**PID**: 1166681  

---

## 🎯 快速操作

### 1. 查看服务状态
```bash
~/.openclaw/scripts/stock-frontend.sh status
```

### 2. 查看实时日志
```bash
~/.openclaw/scripts/stock-frontend.sh logs
```

### 3. 重启服务
```bash
~/.openclaw/scripts/stock-frontend.sh restart
```

### 4. 停止服务
```bash
~/.openclaw/scripts/stock-frontend.sh stop
```

---

## 🚀 开机自动启动（Systemd 配置）

由于安全原因，需要您手动配置 systemd 服务。

### 步骤 1: 创建服务文件

```bash
sudo nano /etc/systemd/system/stock-frontend.service
```

### 步骤 2: 粘贴以下内容

```ini
[Unit]
Description=Stock Trading System Frontend Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=claw
Group=claw
WorkingDirectory=/home/claw/.openclaw/workspace/stock-frontend
ExecStart=/home/claw/.openclaw/scripts/stock-frontend.sh start
ExecStop=/home/claw/.openclaw/scripts/stock-frontend.sh stop
Restart=always
RestartSec=10
StandardOutput=append:/home/claw/.openclaw/logs/stock-frontend.log
StandardError=append:/home/claw/.openclaw/logs/stock-frontend.err
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

### 步骤 3: 启用并启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-frontend.service
sudo systemctl start stock-frontend.service
sudo systemctl status stock-frontend.service
```

### 验证服务状态

```bash
# 检查是否开机自启
sudo systemctl is-enabled stock-frontend.service

# 查看服务状态
sudo systemctl status stock-frontend.service

# 查看日志
journalctl -u stock-frontend.service -f
```

---

## 🎨 功能模块说明

### 1️⃣ 概览页 (Overview)
- 总权益、可用资金、总盈亏
- 持仓概览（前 5 只股票）
- 系统分析摘要
- 最近交易记录
- 最新资讯推送

### 2️⃣ 持仓管理 (Portfolio)
- 完整持仓列表
- 多维度排序（市值、盈亏、涨幅）
- 资产配置可视化饼图
- 个股表现分析

### 3️⃣ K 线图表 (Charts)
- 实时价格走势图表
- 成交量分析
- 持仓分布饼图
- 技术指标展示

### 4️⃣ 投资分析 (Analysis)
- 性能指标（夏普比率、最大回撤等）
- AI 投资建议
- 市场情绪分析
- 风险评估报告

### 5️⃣ 新闻摘要 (News)
- 实时财经新闻
- 情绪分类（利好/中性/利空）
- 多维度筛选和搜索
- 相关股票关联

### 6️⃣ 交易记录 (Transactions)
- 完整交易流水
- 买入/卖出统计
- 费用汇总
- CSV 导出功能

---

## 🔧 服务脚本说明

**脚本位置**: `~/.openclaw/scripts/stock-frontend.sh`

**功能**:
- `start` - 启动服务（后台运行）
- `stop` - 停止服务
- `restart` - 重启服务
- `status` - 查看服务状态
- `logs` - 实时查看日志
- `help` - 显示帮助信息

**日志文件**:
- 主日志：`~/.openclaw/logs/stock-frontend.log`
- 错误日志：`~/.openclaw/logs/stock-frontend.err`
- PID 文件：`~/.openclaw/run/stock-frontend.pid`

---

## 📊 当前运行状态

```bash
# 查看端口监听
ss -tlnp | grep 300[01]

# 查看进程
ps aux | grep node | grep vite

# 查看服务
~/.openclaw/scripts/stock-frontend.sh status
```

---

## 💡 温馨提示

1. **服务运行中**: 前端服务已启动，可以通过 http://localhost:3000 访问
2. **端口占用**: 默认使用 3000 端口，3001 是热更新端口
3. **后台运行**: 服务在后台运行，不影响其他操作
4. **持久化**: 配置 systemd 后，开机自动启动
5. **日志监控**: 可以通过 `logs` 命令实时查看运行状态

---

## 🐛 常见问题

### Q1: 服务启动失败
**解决方案**:
```bash
# 查看详细日志
tail -f ~/.openclaw/logs/stock-frontend.log

# 检查端口是否被占用
lsof -i :3000

# 停止旧进程并重启
~/.openclaw/scripts/stock-frontend.sh stop
~/.openclaw/scripts/stock-frontend.sh start
```

### Q2: 如何修改端口
**解决方案**:
编辑 `stock-frontend/package.json`:
```json
{
  "scripts": {
    "dev": "vite --port 8080"
  }
}
```

### Q3: 如何查看访问日志
**解决方案**:
```bash
# 实时查看
tail -f ~/.openclaw/logs/stock-frontend.log

# 查看最近 100 行
tail -100 ~/.openclaw/logs/stock-frontend.log
```

---

## 📝 下一步建议

1. **接入真实后端**: 修改 `src/stores/stock.ts`，将模拟数据替换为真实 API 调用
2. **自定义样式**: 修改 `tailwind.config.js` 调整主题色
3. **添加实时数据**: 配置 WebSocket 实现实时行情推送
4. **部署到生产**: 使用 `npm run build` 构建生产版本

---

**Created by 御坂美琴一号** ⚡  
**Date**: 2026-03-17  
**Version**: 1.0.0
