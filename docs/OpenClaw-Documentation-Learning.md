# OpenClaw 技术文档学习笔记

> 创建时间：2026-03-20  
> 学习目标：全面掌握 OpenClaw 核心技术栈

---

## 📚 目录

1. [OpenClaw CLI](#1-openclaw-cli)
2. [网关系统 (Gateway)](#2-网关系统-gateway)
3. [技能系统 (Skills)](#3-技能系统-skills)
4. [Agent 系统](#4-agent-系统)
5. [会话系统 (Sessions)](#5-会话系统-sessions)
6. [消息系统 (Channels)](#6-消息系统-channels)
7. [Feishu 集成](#7-feishu 集成)
8. [工具调用](#8-工具调用)
9. [备份策略](#9-备份策略)
10. [定时任务 (Cron)](#10-定时任务-cron)

---

## 1. OpenClaw CLI

### 核心命令

#### Gateway 管理
```bash
openclaw gateway status    # 查看网关状态
openclaw gateway start     # 启动网关
openclaw gateway stop      # 停止网关
openclaw gateway restart   # 重启网关
openclaw logs --follow     # 跟踪日志
```

#### Channels 管理
```bash
openclaw channels add              # 添加新频道
openclaw channels login --channel whatsapp --account personal
openclaw channels status --probe   # 测试连接
openclaw pairing list feishu       # 查看配对请求
openclaw pairing approve feishu <CODE>  # 批准配对
```

#### Agents 管理
```bash
openclaw agents add work           # 创建新 Agent
openclaw agents list --bindings    # 列出所有 Agent 绑定规则
```

#### Cron 定时任务
```bash
openclaw cron add                  # 添加定时任务
openclaw cron list                 # 列出所有任务
openclaw cron run <job-id>         # 立即运行任务
openclaw cron runs --id <job-id>   # 查看运行历史
openclaw cron edit <job-id>        # 编辑任务
```

#### Sessions 管理
```bash
openclaw sessions --json           # 列出所有会话
openclaw sessions cleanup          # 清理会话数据
```

#### Security
```bash
openclaw security audit            # 安全审计
```

---

## 2. 网关系统 (Gateway)

### 核心架构

**Gateway 是 OpenClaw 的核心中枢**，负责：
- 管理所有 Agent 的运行
- 处理所有消息路由
- 运行定时任务
- 维护会话状态
- 处理工具调用

### 存储位置

- **配置文件**: `~/.openclaw/openclaw.json`
- **会话存储**: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- **会话历史**: `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`
- **Cron 任务**: `~/.openclaw/cron/jobs.json`
- **Cron 历史**: `~/.openclaw/cron/runs/<jobId>.jsonl`

### 会话状态字段

Gateway 维护的会话元数据包括：
```json
{
  "inputTokens": 1234,
  "outputTokens": 567,
  "totalTokens": 1801,
  "contextTokens": 456
}
```

### Gateway 启动

```bash
# 开发模式
openclaw gateway

# 安装为系统服务
openclaw gateway install

# 远程访问
openclaw gateway --url http://gateway.example.com:8000 \
  --token <gateway-token>
```

---

## 3. 技能系统 (Skills)

### 什么是 Skills

**Skills 是 OpenClaw 的工具扩展系统**，用于教会 Agent 如何使用特定工具。每个 skill 是一个包含 `SKILL.md` 的目录，其中定义了工具的使用方法和条件。

### Skills 加载路径

**优先级从高到低**：
1. 工作区技能：`<workspace>/skills`
2. 管理技能：`~/.openclaw/skills`
3. 捆绑技能：随 OpenClaw 安装包

### Skill 格式

```markdown
---
name: example-skill
description: 描述技能功能
metadata:
  {"openclaw": {
    "requires": {"bins": ["tool-name"], "env": ["API_KEY"]},
    "primaryEnv": "API_KEY"
  }}
---

# Skill 名称

这里是详细的使用方法说明。
```

### Gating (加载过滤)

Skill 可以在加载时根据以下条件过滤：
- `metadata.openclaw.requires.bins`：必须存在的二进制文件
- `metadata.openclaw.requires.env`：必须存在的环境变量
- `metadata.openclaw.requires.config`：必须为真的配置项
- `metadata.openclaw.os`：支持的操作系统列表
- `always: true`：始终包含该技能

### 配置覆盖

在 `~/.openclaw/openclaw.json` 中配置：

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" },
        env: {
          GEMINI_API_KEY: "your-key-here",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
    },
  },
}
```

### ClawHub

ClawHub 是 OpenClaw 的公共技能仓库：[https://clawhub.com](https://clawhub.com)

```bash
# 安装技能
clawhub install <skill-slug>

# 更新所有技能
clawhub update --all

# 同步并推送更新
clawhub sync --all
```

---

## 4. Agent 系统

### 什么是 Agent

每个 Agent 是一个完整的"大脑"，包含：
- **工作空间**：文件、AGENTS.md/SOUL.md/USER.md、本地笔记
- **状态目录**：认证配置、模型注册表、每 Agent 配置
- **会话存储**：聊天记录和路由状态

### 路径结构

```
~/.openclaw/agents/<agentId>/agent/
  ├── auth-profiles.json          # 认证配置（每 Agent 独立）
  └── config/                     # 每 Agent 配置
```

### 单 Agent 模式（默认）

```bash
# 默认配置
agentId: "main"
workspace: "~/.openclaw/workspace"
agentDir: "~/.openclaw/agents/main/agent"
```

### 多 Agent 模式

```bash
# 创建多个 Agent
openclaw agents add coding
openclaw agents add social

# 查看绑定
openclaw agents list --bindings
```

### 路由规则 (Bindings)

路由是**确定性**的，**最具体优先**：

1. `peer` 匹配（精确 DM/群组/频道 id）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. `accountId` 匹配
7. 频道级别匹配
8. 回退到默认 Agent

### 配置示例

```json5
{
  agents: {
    list: [
      {
        id: "main",
        workspace: "~/.openclaw/workspace",
      },
      {
        id: "coding",
        workspace: "~/.openclaw/workspace-coding",
      },
    ],
  },
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

---

## 5. 会话系统 (Sessions)

### Session 核心概念

**一个 Agent 一个直接聊天会话** 是核心。直接聊天会话归并为 `agent:<agentId>:<mainKey>`，而群/频道聊天使用各自的 key。

### DM Scope 配置

控制**直接消息**如何分组：

```json5
{
  session: {
    // 默认：所有 DM 共享主会话
    dmScope: "main",
    
    // 安全模式：每个用户独立
    dmScope: "per-channel-peer",
    
    // 多账号场景
    dmScope: "per-account-channel-peer",
  },
}
```

### Session 存储

- **Store 文件**: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- **Transcripts**: `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`
- **每会话字段**: `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`

### 会话清洗

```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "45d",
      maxEntries: 800,
      rotateBytes: "20mb",
      resetArchiveRetention: "14d",
    },
  },
}
```

CLI 命令：
```bash
openclaw sessions cleanup --dry-run    # 预览
openclaw sessions cleanup --enforce    # 执行
```

### Reset 策略

```json5
{
  session: {
    reset: {
      mode: "daily",           // 默认：每天凌晨 4 点重置
      atHour: 4,
      idleMinutes: 120,        // 可选：空闲 2 小时后重置
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
  },
}
```

### 会话映射

- 直接聊天：`agent:<agentId>:<mainKey>` 或 `agent:<agentId>:direct:<peerId>`
- 群组聊天：`agent:<agentId>:<channel>:group:<id>`
- 频道聊天：`agent:<agentId>:<channel>:channel:<id>`
- Cron 任务：`cron:<job.id>`（独立）或 `session:<custom-id>`（持久）
- Webhook: `hook:<uuid>`
- Node 运行：`node-<nodeId>`

---

## 6. 消息系统 (Channels)

### 支持的频道

- WhatsApp
- Telegram
- Discord
- Slack
- Feishu (飞书)
- Signal
- iMessage
- 以及其他 20+ 种通讯平台

### 认证配置

每个频道账号有独立的认证：

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      accounts: {
        personal: {},
        work: {},
      },
    },
    telegram: {
      accounts: {
        default: {
          botToken: "123456:ABC...",
        },
      },
    },
  },
}
```

### 群组策略

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "open",  // open | allowlist | disabled
      groupAllowFrom: ["group-id-1", "group-id-2"],
      groups: {
        "group-id-1": {
          requireMention: true,  // 是否需要@提及
        },
      },
    },
  },
}
```

### 会话隔离

- **DMs**: 默认共享主会话（单用户），或 per-peer（多用户）
- **Groups**: 完全隔离，每个群组独立会话
- **Threads/Topics**: 有 `:topic:<threadId>` 后缀

---

## 7. Feishu 集成

### 快速开始

#### 方式 1: onboarding（推荐）

```bash
openclaw onboard
```

#### 方式 2: CLI 配置

```bash
openclaw channels add
# 选择 Feishu，输入 App ID 和 App Secret
```

### 飞书配置步骤

1. **创建飞书应用**
   - App ID: `cli_xxx`
   - App Secret: 保密

2. **配置权限**

```json
{
  "scopes": {
    "tenant": [
      "aily:file:read",
      "aily:file:write",
      "im:message",
      "im:message:send_as_bot",
      "im:resource"
    ],
    "user": ["aily:file:read", "aily:file:write", "im:chat.access_event.bot_p2p_chat:read"]
  }
}
```

3. **启用 Bot 功能**
   - App Capability > Bot
   - 启用 Bot 能力

4. **配置事件订阅**
   - 使用长连接接收事件（WebSocket）
   - 添加事件：`im.message.receive_v1`

5. **发布应用**

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
          botName: "My AI assistant",
        },
      },
    },
  },
}
```

### 认证批准

```bash
openclaw pairing list feishu
openclaw pairing approve feishu <CODE>
```

### 群组配置

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",  // 默认允许所有群组
      groups: {
        "oc_xxx": {
          requireMention: false,  // 不需要@提及
        },
      },
    },
  },
}
```

### 高级配置

#### 多账号

```json5
{
  channels: {
    feishu: {
      defaultAccount: "main",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
        },
        backup: {
          appId: "cli_yyy",
          appSecret: "yyy",
          enabled: false,
        },
      },
    },
  },
}
```

#### 配额优化

```json5
{
  channels: {
    feishu: {
      typingIndicator: false,      // 跳过打字提示
      resolveSenderNames: false,   // 跳过发送者名称解析
    },
  },
}
```

### ACP 会话支持

飞书支持 ACP（Agent Control Protocol）：

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "feishu",
        accountId: "default",
        peer: { kind: "direct", id: "ou_1234567890" },
      },
    },
  ],
}
```

### 常用命令

```bash
openclaw gateway status
openclaw gateway restart
openclaw logs --follow
```

---

## 8. 工具调用

### 工具调用格式

```json
{
  "toolName": "example-tool",
  "params": {
    "param1": "value1",
    "param2": 123
  }
}
```

### 核心工具

- **read**: 读取文件内容
- **write**: 创建或覆盖文件
- **edit**: 精确编辑文件
- **exec**: 执行 Shell 命令
- **process**: 管理后台进程
- **web_search**: 网络搜索
- **web_fetch**: 抓取网页内容
- **browser**: 浏览器自动化
- **message**: 发送和管理消息
- **nodes**: 管理配对设备
- **feishu_***: Feishu 集成工具
- **tts**: 文本转语音
- **subagents**: 管理子代理

### 工具调用示例

```json
{
  "toolName": "feishu_doc",
  "action": "read",
  "doc_token": "docx_XXX",
  "limit": 100
}
```

---

## 9. 备份策略

### 本地备份

- **备份目录**: `/home/claw/.openclaw/backup/`
- **Git 同步**: 每 6 小时自动提交到 Git
- **清理策略**: 每天 12:30 清理 7 天前的备份
- **恢复点**: 6 小时间隔的 checkpoint

### Cron 自动备份

```bash
# 配置示例
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 1,
  },
}
```

### 定时备份任务

```bash
openclaw cron add \
  --name "Auto backup" \
  --cron "0 */6 * * *" \
  --session isolated \
  --message "Check backup status" \
  --light-context
```

---

## 10. 定时任务 (Cron)

### 什么是 Cron

Cron 是 Gateway 的内置调度器，负责：
- 持久化任务
- 按时唤醒 Agent
- 可选地将输出推送到聊天

### 三种执行模式

1. **Main session**: 在主会话上下文中运行系统事件
2. **Isolated**: 在独立的 cron 会话中运行
3. **Current session**: 绑定到创建时的当前会话

### 任务类型

```json5
// 一次性任务
{
  "name": "Reminder",
  "schedule": { "kind": "at", "at": "2026-02-01T16:00:00Z" },
  "sessionTarget": "main",
  "payload": { "kind": "systemEvent", "text": "Reminder text" },
  "deleteAfterRun": true
}

// 周期性任务
{
  "name": "Morning brief",
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "America/Los_Angeles" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Summarize overnight updates.",
    "lightContext": true
  },
  "delivery": {
    "mode": "announce",
    "channel": "slack",
    "to": "channel:C1234567890",
    "bestEffort": true
  }
}
```

### 调度类型

1. **at**: 一次性时间戳
2. **every**: 固定间隔（毫秒）
3. **cron**: 5 字段 cron 表达式（或带秒的 6 字段）

### CLI 使用

#### 添加任务

```bash
# 一次性提醒（UTC ISO，成功后自动删除）
openclaw cron add \
  --name "Reminder" \
  --at "2026-01-12T18:00:00Z" \
  --session main \
  --system-event "Reminder: submit expense report." \
  --wake now \
  --delete-after-run

# 周期性任务
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel whatsapp \
  --to "+15551234567"
```

#### 管理任务

```bash
openclaw cron list                # 列出所有任务
openclaw cron run <job-id>        # 立即运行
openclaw cron runs --id <id>      # 查看运行历史
openclaw cron edit <job-id>       # 编辑任务
openclaw cron remove <job-id>     # 删除任务
```

### 配置

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1,
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    sessionRetention: "24h",
    runLog: {
      maxBytes: "2mb",
      keepLines: 2000,
    },
  },
}
```

### 错误重试

**一次性任务**:
- 瞬态错误：最多重试 3 次（30 秒 → 1 分钟 → 5 分钟）
- 永久错误：立即禁用

**周期性任务**:
- 任何错误都应用指数退避（30 秒 → 1 分钟 → 5 分钟 → 15 分钟 → 60 分钟）
- 任务保持启用，成功后退避重置

### 轻量模式

```bash
# 使用轻量上下文运行（不注入工作区文件）
openclaw cron add \
  --name "Light task" \
  --cron "0 9 * * *" \
  --session isolated \
  --message "Simple task" \
  --light-context
```

---

## 🎯 核心概念总结

### OpenClaw 的三层架构

1. **Gateway（网关）**：核心中枢，管理所有 Agent 和会话
2. **Agent（代理）**：独立的大脑，拥有自己的工作空间、配置和会话
3. **Skills（技能）**：工具扩展，教会 Agent 如何使用特定工具

### 关键数据流

```
用户消息 → Gateway 路由 → Agent 处理 → Tool 调用 → 输出 → Gateway 返回
```

### 会话生命周期

1. 创建：首次收到消息时创建
2. 维护：存储输入/输出 token 计数
3. 重置：每日、空闲或显式触发
4. 清洗：自动清理过期会话

### 安全性

- **沙箱隔离**：可选的 Docker 沙箱
- **工具控制**：每个 Agent 独立的工具 allow/deny 列表
- **会话隔离**：DM 和群组完全隔离
- **认证管理**：每 Agent 独立的认证配置

---

## 📖 参考资源

- **官方文档**: https://docs.openclaw.ai
- **技能仓库**: https://clawhub.com
- **完整技能列表**: 查看 `~/.openclaw/skills/`
- **工作区**: `~/.openclaw/workspace`

---

## 🎓 学习建议

1. **先从核心概念入手**：理解 Gateway、Agent、Skills 的关系
2. **掌握 CLI 命令**：熟悉常用命令的实际用法
3. **实践 Feishu 集成**：这是最常用的通道之一
4. **配置定时任务**：体验 Cron 的自动化能力
5. **开发自己的 Skills**：扩展 Agent 的能力边界

---

*最后更新：2026-03-20*
*学习状态：已完成核心技术栈学习*
