# OpenClaw 快速参考卡

**创建时间**: 2026-03-09 13:05 UTC  
**用途**: 明早 7 点汇报的快速参考

---

## 🎯 一句话定义
OpenClaw 是一个 AI 代理网关平台，通过统一的消息处理和会话管理，将多个聊天渠道整合为一个智能助手系统。

---

## 🔑 五大核心功能

| 功能 | 说明 | 核心价值 |
|------|------|----------|
| **多渠道消息** | WhatsApp/Telegram/Discord/Slack | 统一入口，集中管理 |
| **会话隔离** | 每个对话独立上下文 | 互不干扰，状态清晰 |
| **工具系统** | exec/browser/nodes/sessions 等 | 强大的外部能力 |
| **记忆系统** | Markdown 文件持久化 | 持久记忆，语义搜索 |
| **定时任务** | Cron 调度系统 | 自动化执行 |

---

## 🏗️ 架构概览

```
用户 → Gateway → Session → Agent → Tools → LLM → Reply
          ↓         ↓         ↓
      定时任务  记忆系统  工具调用
```

---

## 🛠️ 核心工具（常用）

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `exec` | Shell 命令 | yieldMs, background, timeout |
| `sessions_spawn` | 启动子代理 | runtime, mode, thread |
| `memory_search` | 语义搜索 | query, maxResults, minScore |
| `browser` | 浏览器控制 | action, refs, targetId |
| `nodes` | 节点管理 | action, node, deviceId |

---

## 📅 Cron 命令速查

```bash
# 添加定时任务
openclaw cron add --name "任务名" --cron "0 7 * * *" --session isolated --message "内容" --announce

# 查看任务
openclaw cron list
openclaw cron runs --id <job-id>

# 运行任务
openclaw cron run <job-id>
```

---

## 🧠 记忆系统

**文件结构**:
```
MEMORY.md           # 长期记忆
memory/2026-03-10.md  # 今日日志
memory/2026-03-09.md  # 昨日日志
```

**工具**:
- `memory_search` - 语义搜索（向量 + BM25）
- `memory_get` - 读取文件

**特性**:
- 混合搜索（向量 0.7 + 关键词 0.3）
- 时间衰减（半衰期 30 天）
- MMR 去重（避免重复）

---

## 💬 会话管理

**两个关键 ID**:
- `sessionKey` - 路由键（标识对话桶）
- `sessionId` - 当前会话 ID（对应 transcript 文件）

**生命周期**:
1. 创建 → 2. 对话 → 3. 修剪 → 4. 压缩 → 5. 重置/过期

**修剪策略**:
- `cache-ttl` - 基于 TTL 修剪（默认 5 分钟）
- 保留最后 3 个助手消息
- 只修剪工具结果

---

## ⚙️ 配置关键

**工具权限**:
```json
{
  "tools": {
    "allow": ["group:fs", "group:runtime"],
    "deny": ["browser"]
  }
}
```

**记忆搜索**:
```json
{
  "memorySearch": {
    "provider": "local",
    "fallback": "none"
  }
}
```

**会话修剪**:
```json
{
  "contextPruning": {
    "mode": "cache-ttl",
    "ttl": "5m"
  }
}
```

---

## 🎯 最佳实践

**✅ 要做**:
- 立即 Git commit 记忆文件
- 重要决策写 MEMORY.md
- 定期压缩会话
- 设置合理超时
- 使用后台运行长时间任务

**❌ 避免**:
- 依赖 RAM（会话重启会丢失）
- 不设置超时
- 循环调用工具
- 不配置权限
- 忽略 Git

---

## 💡 实用技巧

**后台运行**:
```json
{
  "action": "exec",
  "command": "npm run build",
  "background": true,
  "yieldMs": 30000
}
```

**子代理线程绑定**:
```json
{
  "runtime": "subagent",
  "mode": "session",
  "thread": true
}
```

**静默操作**:
- 回复以 "NO_REPLY" 开头
- 用户不会看到中间输出
- 用于后台任务

---

## 📞 联系方式

**官方文档**: https://docs.openclaw.ai  
**GitHub**: https://github.com/openclaw/openclaw  
**Discord**: https://discord.com/invite/clawd  
**本地文档**: /home/claw/.openclaw/workspace/docs/

---

**快速链接**:
- 详细学习笔记：memory/2026-03-09-openclaw-learning.md
- 汇报摘要：memory/2026-03-10-openclaw-summary.md

---

*Keep learning, keep building! 🚀*
