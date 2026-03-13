# HEARTBEAT.md - 心跳检测任务清单

**上次检查**: 2026-03-13 16:18 UTC  
**检查频率**: 每 30 分钟

---

## 🔄 定时任务

### 系统健康检查 (新增)
- ✅ 系统健康检查 - 每 30 分钟 - `system-health-check`
  - 检查网关状态
  - 检查 Agent 状态
  - 检查会话状态
  - 检查通道状态
  - 检查定时任务
  - 检查安全配置

### 原有任务
- ✅ 记忆检查点 - 每 30 分钟 - `memory-checkpoint`
- ✅ 自动备份 - 每 30 分钟 - `auto-backup`
- ✅ 自动清理过期备份 - 每天 12:30 - `auto-cleanup`
- ✅ 记忆整理任务 - 每 30 分钟 - `memory-整理`
- ✅ 心跳检测 - 每 30 分钟 - `heartbeat`

---

## 📋 检查清单 (2026-03-13 16:18 UTC)

### 系统级 (每 30 分钟)
- [x] OpenClaw 网关运行状态 ✅ 运行中
- [x] 服务启用状态 ✅ enabled
- [x] 端口监听状态 ✅ 正常
- [x] WebSocket 连接状态 ✅ ok
- [x] RPC 探针状态 ✅ ok

### Agent 级 (每 30 分钟)
- [x] main (御坂美琴一号) ✅ 已配置
- [x] general-agent (御坂妹妹 10 号) ✅ 已配置
- [x] code-executor (御坂妹妹 11 号) ✅ 已配置
- [x] content-writer (御坂妹妹 12 号) ✅ 已配置
- [x] research-analyst (御坂妹妹 13 号) ✅ 已配置
- [x] file-manager (御坂妹妹 14 号) ✅ 已配置
- [x] system-admin (御坂妹妹 15 号) ✅ 已配置
- [x] web-crawler (御坂妹妹 16 号) ✅ 已配置
- [x] memory-organizer (御坂妹妹 17 号) ✅ 已配置
- [x] reviewer (御坂妹妹 18 号) ✅ 已配置
- [x] patrol (御坂妹妹 19 号) ✅ 已配置

### 通道级 (每 30 分钟)
- [x] 飞书通道连接状态 ✅ 已连接
- [x] 心跳检测会话 ✅ 活跃
- [x] 会话路由状态 ✅ 正常

### 任务级 (每 15 分钟)
- [x] 定时任务触发状态 ⚠️ 部分任务失败
- [x] 会话保持状态 ✅ 正常
- [x] 通知发送状态 ✅ 正常

### 安全级 (每 30 分钟)
- [x] 安全配置检查 ✅ 正常
- [x] 权限配置检查 ✅ 正常
- [x] 限流配置检查 ✅ 正常
- [x] 沙箱配置检查 ✅ 正常

---

## ⚠️ 检测到的问题

### 定时任务失败 (需要关注)

以下定时任务状态为 **error**：

1. **OpenClaw 知识学习** (315d1bd9-6294-4de7-8f82-58264afa9b85)
   - 调度：cron 0,30 * * * *
   - 状态：error
   
2. **llm-tunnel-auto-start**
   - 调度：cron 0 * * * *
   - 状态：error
   
3. **llm-health-check**
   - 调度：cron */1 * * * *
   - 状态：error
   
4. **llm-heartbeat-status**
   - 调度：cron */10 * * * *
   - 状态：error
   
5. **记忆检查点** (memory-checkpoint)
   - 调度：cron 0 */6 * * *
   - 状态：error
   
6. **自动备份** (4a130e98-720b-4337-a761-52a7a79a8919)
   - 调度：cron 0 */6 * * *
   - 状态：error
   
7. **记忆整理任务** (memory-整理)
   - 调度：cron 0 */6 * * *
   - 状态：error
   
8. **morning-briefing**
   - 调度：cron 30 7 * * *
   - 状态：error
   
9. **自动清理过期备份** (eee8f17a-00df-4f15-805a-eae16eea6c1e)
   - 调度：cron 30 12 * * *
   - 状态：error

### 配置警告

- ⚠️ Feishu 插件重复 id 检测
  - 位置：`~/.openclaw/extensions/feishu/index.ts`
  - 建议：检查配置是否重复

- ⚠️ Gateway 服务嵌入 Token
  - 建议：运行 `openclaw gateway install --force` 移除嵌入的 Token

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

**当前状态**: ⚠️ 部分定时任务失败，但核心系统正常运行

**总检测率**: 100% (核心组件正常，但定时任务有 9 个失败)

**建议操作**:
1. 检查定时任务日志，排查失败原因
2. 修复 Feishu 插件重复配置问题
3. 重新安装 Gateway 服务移除嵌入 Token

---

_此文件由 system-health-check skill 自动管理_

### 飞书通知任务 (新增)
- ✅ 心跳结果通知 - 每 30 分钟 - `heartbeat_to_feishu`
  - 自动将检测结果发送到飞书当前会话
  - 脚本位置：`scripts/heartbeat_to_feishu.py`
  - 通知格式：Markdown 格式，包含所有检查结果
