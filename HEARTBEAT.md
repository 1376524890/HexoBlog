# HEARTBEAT.md - 心跳检测任务清单

**上次检查**: 2026-03-12 04:42 UTC  
**检查频率**: 每 6 小时

---

## 🔄 定时任务

### 系统健康检查 (新增)
- ✅ 系统健康检查 - 每 6 小时 - `system-health-check`
  - 检查网关状态
  - 检查 Agent 状态
  - 检查会话状态
  - 检查通道状态
  - 检查定时任务
  - 检查安全配置

### 原有任务
- ✅ 记忆检查点 - 每 6 小时 - `memory-checkpoint`
- ✅ 自动备份 - 每 6 小时 - `auto-backup`
- ✅ 自动清理过期备份 - 每天 12:30 - `auto-cleanup`
- ✅ 记忆整理任务 - 每 6 小时 - `memory-整理`
- ✅ 心跳检测 - 每 30 分钟 - `heartbeat`

---

## 📋 检查清单

### 系统级 (每 6 小时)
- [x] OpenClaw 网关运行状态
- [x] 服务启用状态
- [x] 端口监听状态
- [x] WebSocket 连接状态
- [x] RPC 探针状态

### Agent 级 (每 30 分钟)
- [x] main (御坂美琴一号)
- [x] general-agent (御坂妹妹 10 号)
- [x] code-executor (御坂妹妹 11 号)
- [x] content-writer (御坂妹妹 12 号)
- [x] research-analyst (御坂妹妹 13 号)
- [x] file-manager (御坂妹妹 14 号)
- [x] system-admin (御坂妹妹 15 号)
- [x] web-crawler (御坂妹妹 16 号)
- [x] memory-organizer (御坂妹妹 17 号)
- [x] reviewer (御坂妹妹 18 号)
- [x] patrol (御坂妹妹 19 号)

### 通道级 (每 30 分钟)
- [x] 飞书通道连接状态
- [x] 心跳检测会话
- [x] 会话路由状态

### 任务级 (每 15 分钟)
- [x] 定时任务触发状态
- [x] 会话保持状态
- [x] 通知发送状态

### 安全级 (每 6 小时)
- [x] 安全配置检查
- [x] 权限配置检查
- [x] 限流配置检查
- [x] 沙箱配置检查

---

## 🚨 异常处理

如果检测到异常，请：

1. **紧急异常** (网关未运行):
   ```bash
   openclaw gateway restart
   openclaw gateway status
   ```

2. **Agent 未活跃**:
   ```bash
   openclaw agents list
   openclaw logs --follow
   ```

3. **通道未连接**:
   ```bash
   openclaw channels status
   openclaw pairing list
   ```

4. **定时任务失败**:
   ```bash
   openclaw cron list
   openclaw logs --follow
   ```

5. **安全配置警告**:
   ```bash
   openclaw status
   ```

---

## 📊 健康状态

**当前状态**: ✅ 所有检查通过

**总检测率**: 100%

---

_此文件由 system-health-check skill 自动管理_
