# 📊 股票交易系统配置（2026-03-17）

**创建时间**: 2026 年 3 月 17 日 16:10 UTC  
**创建者**: 御坂美琴一号  
**前端框架**: Vue 3 + TypeScript + Vite + Tailwind CSS

---

## ✅ 服务状态

**前端服务**: ✅ 已启动运行  
**访问地址**: http://localhost:3000  
**PID**: 1166681  
**状态**: 运行中  

---

## 📁 项目位置

**路径**: `~/.openclaw/workspace/stock-frontend`  
**主文件**: `package.json`, `vite.config.ts`, `tailwind.config.js`  
**服务脚本**: `~/.openclaw/scripts/stock-frontend.sh`  
**配置文档**: `stock-frontend/SERVICE-SETUP.md`

---

## 🚀 快速命令

```bash
# 查看服务状态
~/.openclaw/scripts/stock-frontend.sh status

# 查看日志
~/.openclaw/scripts/stock-frontend.sh logs

# 重启服务
~/.openclaw/scripts/stock-frontend.sh restart

# 停止服务
~/.openclaw/scripts/stock-frontend.sh stop
```

---

## 📦 功能模块

1. **概览页** - 总览、持仓、分析、交易、新闻
2. **持仓管理** - 持仓列表、排序、饼图
3. **K 线图表** - 价格走势、成交量、技术指标
4. **投资分析** - 夏普比率、最大回撤、AI 建议
5. **新闻摘要** - 实时新闻、情绪分类
6. **交易记录** - 交易流水、费用汇总

---

## 🛠️ 技术栈

- Vue 3 (Composition API)
- TypeScript
- Vite 6.0
- Tailwind CSS 3.4
- Pinia 状态管理
- Vue Router 4
- Chart.js + Vue-Chart.js
- Axios

---

## ⚙️ Systemd 配置（待配置）

**服务文件**: `/etc/systemd/system/stock-frontend.service`  
**配置步骤**:
1. `sudo nano /etc/systemd/system/stock-frontend.service`
2. 粘贴服务配置（见 SERVICE-SETUP.md）
3. `sudo systemctl daemon-reload`
4. `sudo systemctl enable stock-frontend.service`
5. `sudo systemctl start stock-frontend.service`

---

## 📝 维护说明

- **日志目录**: `~/.openclaw/logs/stock-frontend.log`
- **PID 文件**: `~/.openclaw/run/stock-frontend.pid`
- **端口**: 3000（主服务）、3001（热更新）
- **自动重启**: 服务脚本支持自动重启

---

**下次检查**: 建议每天检查服务状态  
**下次备份**: 下次重大更新前备份
