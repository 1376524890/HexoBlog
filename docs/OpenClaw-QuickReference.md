# OpenClaw 快速参考指南

> 核心概念速查表

---

## 🚀 快速开始

### 1. 启动网关

```bash
openclaw gateway
```

### 2. 添加频道

```bash
openclaw channels add
# 选择 Feishu/Telegram/WhatsApp 等
```

### 3. 批准配对

```bash
openclaw pairing approve feishu <CODE>
```

---

## 🔧 核心命令速查

### Gateway 管理

| 命令 | 说明 |
|------|------|
| `openclaw gateway status` | 查看状态 |
| `openclaw gateway start` | 启动 |
| `openclaw gateway stop` | 停止 |
| `openclaw gateway restart` | 重启 |
| `openclaw logs --follow` | 跟踪日志 |

### Channels 管理

| 命令 | 说明 |
|------|------|
| `openclaw channels add` | 添加新频道 |
| `openclaw channels login` | 登录新账号 |
| `openclaw pairing list <channel>` | 查看配对请求 |
| `openclaw pairing approve <channel> <CODE>` | 批准配对 |

### Agents 管理

| 命令 | 说明 |
|------|------|
| `openclaw agents add <name>` | 创建新 Agent |
| `openclaw agents list --bindings` | 查看绑定规则 |

### Cron 任务

| 命令 | 说明 |
|------|------|
| `openclaw cron add` | 添加任务 |
| `openclaw cron list` | 列出任务 |
| `openclaw cron run <id>` | 立即运行 |
| `openclaw cron edit <id>` | 编辑任务 |
| `openclaw cron remove <id>` | 删除任务 |

### Sessions 管理

| 命令 | 说明 |
|------|------|
| `openclaw sessions --json` | 列出会话 |
| `openclaw sessions cleanup` | 清理会话 |

---

## 📁 重要路径

```
~/.openclaw/
├── openclaw.json              # 主配置文件
├── agents/
│   └── <agentId>/
│       ├── agent/
│       │   └── auth-profiles.json  # 认证配置
│       └── sessions/
│           ├── sessions.json     # 会话元数据
│           └── <SessionId>.jsonl # 会话历史
├── cron/
│   ├── jobs.json               # 定时任务
│   └── runs/                   # 任务历史记录
└── skills/                     # 技能目录
```

---

## 🎯 核心概念

### 三层架构

```
┌─────────────────────────────────────┐
│           Gateway (网关)             │
│  ┌─────────────┐  ┌──────────────┐ │
│  │   Agent 1   │  │   Agent 2    │ │
│  └─────────────┘  └──────────────┘ │
└─────────────────────────────────────┘
            ↑         ↑
        Skills 1   Skills 2
```

### 会话 Key 格式

| 类型 | 格式 |
|------|------|
| 直接聊天 | `agent:<agentId>:main` 或 `agent:<agentId>:direct:<peerId>` |
| 群组聊天 | `agent:<agentId>:<channel>:group:<id>` |
| 频道聊天 | `agent:<agentId>:<channel>:channel:<id>` |
| Cron 任务 | `cron:<jobId>` |
| Webhook | `hook:<uuid>` |
| Node 运行 | `node-<nodeId>` |

---

## ⏰ Cron 配置示例

### 一次性任务

```bash
openclaw cron add \
  --name "Reminder" \
  --at "2026-03-21T09:00:00Z" \
  --session main \
  --system-event "Reminder: submit report." \
  --wake now
```

### 周期性任务

```bash
openclaw cron add \
  --name "Daily brief" \
  --cron "0 8 * * *" \
  --session isolated \
  --message "Summarize yesterday's work." \
  --announce \
  --channel feishu \
  --to "oc_xxx"
```

### 使用环境变量

```bash
openclaw cron add \
  --name "Backup check" \
  --cron "0 0 * * *" \
  --session isolated \
  --message "Check backup status" \
  --light-context
```

---

## 🤖 Feishu 配置速查

### 快速配置

```bash
# 1. 创建应用
# 在 https://open.feishu.cn/app 创建应用

# 2. 添加频道
openclaw channels add

# 3. 输入 App ID 和 App Secret

# 4. 批准配对
openclaw pairing list feishu
openclaw pairing approve feishu <CODE>

# 5. 测试
# 在飞书中 @bot 发送消息
```

### 配置示例

```json5
{
  channels: {
    feishu: {
      enabled: true,
      dmPolicy: "pairing",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
        },
      },
    },
  },
}
```

### 权限配置

```json
{
  "scopes": {
    "tenant": [
      "aily:file:read",
      "aily:file:write",
      "im:message",
      "im:message:send_as_bot",
      "im:resource"
    ]
  }
}
```

---

## 🛡️ 安全配置

### 沙箱配置

```json5
{
  agents: {
    list: [
      {
        id: "unsafe",
        sandbox: {
          mode: "all",
          scope: "agent",
        },
      },
    ],
  },
}
```

### 工具控制

```json5
{
  agents: {
    list: [
      {
        id: "restricted",
        tools: {
          allow: ["read"],
          deny: ["exec", "write", "edit"],
        },
      },
    ],
  },
}
```

---

## 🔍 故障排查

### Gateway 不启动

```bash
openclaw gateway status
openclaw logs --follow
```

### 频道收不到消息

```bash
# 检查认证
openclaw pairing list <channel>

# 查看日志
openclaw logs --follow

# 检查事件订阅（飞书）
# 在飞书开放平台确认已启用事件订阅
```

### 会话问题

```bash
# 列出会话
openclaw sessions --json

# 清理会话
openclaw sessions cleanup
```

### Cron 任务不运行

```bash
# 查看任务
openclaw cron list

# 手动运行
openclaw cron run <job-id>

# 查看运行历史
openclaw cron runs --id <job-id>
```

---

## 📊 Token 统计

会话状态包含以下字段：

```json
{
  "inputTokens": 1234,     # 输入 token
  "outputTokens": 567,     # 输出 token
  "totalTokens": 1801,     # 总 token
  "contextTokens": 456     # 上下文 token
}
```

---

## 🎨 会话 Reset 策略

```json5
{
  session: {
    reset: {
      mode: "daily",           // daily | idle
      atHour: 4,               // 每天凌晨 4 点
      idleMinutes: 120,        // 空闲 2 小时
    },
    resetTriggers: ["/new", "/reset"],
  },
}
```

---

## 🔄 多 Agent 路由

### 基本路由

```json5
{
  bindings: [
    {
      agentId: "main",
      match: { channel: "whatsapp" },
    },
    {
      agentId: "coding",
      match: { channel: "telegram" },
    },
  ],
}
```

### 精确路由（优先）

```json5
{
  bindings: [
    {
      agentId: "premium",
      match: {
        channel: "whatsapp",
        peer: { kind: "direct", id: "+15551234567" },
      },
    },
    {
      agentId: "main",
      match: { channel: "whatsapp" },
    },
  ],
}
```

---

## 🎯 常用场景

### 1. 每日工作总结

```bash
openclaw cron add \
  --name "Daily work summary" \
  --cron "17 18 * * 1-5" \
  --session isolated \
  --message "Summarize today's work and prepare tomorrow's plan." \
  --announce \
  --channel feishu \
  --to "oc_xxx"
```

### 2. 备份检查

```bash
openclaw cron add \
  --name "Backup health check" \
  --cron "0 9 * * *" \
  --session isolated \
  --message "Check if recent backups exist." \
  --light-context
```

### 3. 重要提醒

```bash
openclaw cron add \
  --name "Meeting reminder" \
  --at "2026-03-21T09:30:00Z" \
  --session main \
  --system-event "Reminder: Team meeting in 30 minutes!" \
  --wake now
```

---

## 📖 文档链接

- **官方文档**: https://docs.openclaw.ai
- **技能仓库**: https://clawhub.com
- **飞书开放平台**: https://open.feishu.cn/app
- **Telegram BotFather**: https://t.me/BotFather
- **Discord Developer Portal**: https://discord.com/developers

---

*创建时间：2026-03-20*
*维护者：御坂美琴一号*
