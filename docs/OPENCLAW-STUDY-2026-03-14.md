# OpenClaw 知识学习总结

> 学习日期：2026-03-13  
> 用途：2026-03-14 07:00 AM 汇报准备  
> 学习方式：纯理论学习，无实践

---

## 📚 一、OpenClaw 概述

### 1.1 核心定位
OpenClaw 是一个**智能体网关系统**，将 AI 模型与各种通信渠道、设备能力连接起来。

**核心理念**：
- 单一 Gateway 控制所有消息表面（WhatsApp、Telegram、Discord、iMessage 等）
- 通过 WebSocket 与客户端和节点通信
- 支持多智能体路由，每个智能体有独立的工作空间、认证和会话

### 1.2 关键概念

#### Gateway（网关守护进程）
- 运行在宿主机上的核心服务
- 维护提供者连接（WhatsApp、Telegram 等）
- 通过 WebSocket 暴露 typed API
- 默认端口：127.0.0.1:18789
- 是唯一的 WhatsApp 会话拥有者

#### Agent（智能体）
一个 agent 是完整的"大脑"，包含：
- **Workspace**（工作空间）：文件、AGENTS.md/SOUL.md/USER.md、个性化规则
- **State directory**（状态目录）：auth profiles、模型注册表、每个 agent 的配置
- **Session store**（会话存储）：聊天历史 + 路由状态

#### Node（节点）
- 辅助设备（macOS/iOS/Android/headless）
- 以 `role: "node"` 连接到 Gateway
- 暴露命令表面（canvas、camera、screen、location 等）
- 不是网关，不运行为消息通道

---

## 🏗️ 二、架构设计

### 2.1 组件和流程

```
┌─────────────┐      WebSocket      ┌──────────────┐
│  Clients    │◄───────────────────►│   Gateway    │
│  (CLI/App)  │                     │   (Daemon)   │
└─────────────┘                     └──────┬───────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
              ┌─────▼─────┐         ┌─────▼─────┐          ┌─────▼─────┐
              │  Channels │         │  Nodes    │          │  Models   │
              │ WhatsApp  │         │ iOS/Android│         │ Claude/GPT│
              │ Telegram  │         │ macOS      │          │           │
              │ Discord   │         │ Headless   │          │           │
              └───────────┘         └────────────┘          └───────────┘
```

### 2.2 连接生命周期

1. **Connect** - 客户端发送 `req:connect`
2. **Handshake** - Gateway 返回 `res` + `event:presence` + `event:tick`
3. **Request** - 客户端发送 `req:agent`
4. **Response** - Gateway 返回 `res:agent` (含 `runId`, `status: "accepted"`)
5. **Streaming** - Gateway 推送 `event:agent` 流式响应
6. **Final** - Gateway 返回最终结果 `res:agent {runId, status, summary}`

### 2.3 协议类型

- **Transport**: WebSocket, JSON 文本帧
- **First frame**: 必须是 `connect`
- **Requests**: `{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
- **Events**: `{type:"event", event, payload, seq?, stateVersion?}`
- **Auth**: 如果设置了 `OPENCLAW_GATEWAY_TOKEN`，`connect.params.auth.token` 必须匹配

---

## 🔄 三、多智能体路由

### 3.1 什么是"一个 agent"？

每个 agent 是完全隔离的：
- 不同的电话号码/账号（每个 channel `accountId`）
- 不同的人格（每个 agent 工作空间的 SOUL.md、AGENTS.md）
- 分离的认证和会话（除非明确启用）

### 3.2 路由规则（确定性）

**优先级从高到低**：
1. `peer` 匹配（精确 DM/群组/频道 id）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. `accountId` 匹配 channel 账号
7. channel 级匹配（`accountId: "*"`）
8. 回退到默认 agent（`agents.list[].default`，否则第一条，默认：`main`）

**重要**：如果一个 binding 在同一个级别匹配多个，配置顺序中第一个 wins。

### 3.3 多账号支持

支持多账号的 channel 使用 `accountId` 识别每个登录：
- `whatsapp`, `telegram`, `discord`, `slack`, `signal`, `imessage`
- `irc`, `line`, `googlechat`, `mattermost`, `matrix`, `nextcloud-talk`
- `bluebubbles`, `zalo`, `zalouser`, `nostr`, `feishu`

---

## 🗂️ 四、会话管理

### 4.1 会话键格式

**Direct messages (DM)** 根据 `session.dmScope`：
- `main`（默认）：`agent:<agentId>:<mainKey>` - 所有 DM 共享主会话
- `per-peer`：`agent:<agentId>:direct:<peerId>`
- `per-channel-peer`：`agent:<agentId>:<channel>:direct:<peerId>`
- `per-account-channel-peer`：`agent:<agentId>:<channel>:<accountId>:direct:<peerId>`

**Group chats**（群组）：
- `agent:<agentId>:<channel>:group:<id>`
- Telegram 论坛话题追加 `:topic:<threadId>`

**其他来源**：
- Cron jobs: `cron:<job.id>`
- Webhooks: `hook:<uuid>`
- Node runs: `node-<nodeId>`

### 4.2 安全 DM 模式（推荐用于多用户环境）

**问题**：如果 agent 可以接收多人的 DM，默认设置下所有用户共享同一个会话上下文，可能导致隐私泄露。

**示例问题**：
- Alice 发送私密消息（医疗预约）
- Bob 问"我们刚才说什么来着？"
- 因为共享会话，模型可能用 Alice 的上下文回答 Bob

**解决方案**：
```json5
{
  session: {
    dmScope: "per-channel-peer",  // 安全 DM 模式：每个频道 + 发送者隔离 DM 上下文
  },
}
```

### 4.3 会话维护

**默认配置**：
- `session.maintenance.mode`: `warn`
- `session.maintenance.pruneAfter`: `30d`
- `session.maintenance.maxEntries`: `500`
- `session.maintenance.rotateBytes`: `10mb`

**维护模式**：
- `mode: "warn"` - 报告会清除什么但不修改
- `mode: "enforce"` - 应用清理：
  1. 删除超过 `pruneAfter` 的旧条目
  2. 限制条目数到 `maxEntries`（最老的先）
  3. 归档不再引用的对话文件
  4. 清理旧的归档文件
  5. 旋转 `sessions.json`
  6. 如果设置了 `maxDiskBytes`，强制磁盘预算

### 4.4 重置策略

- **每日重置**：默认凌晨 4 点（Gateway 主机本地时间）
- **空闲重置**：`idleMinutes` 增加滑动空闲窗口
- **手动重置**：发送 `/new` 或 `/reset`
- **Per-type overrides**：`resetByType` 可分别为 `direct`, `group`, `thread` 设置不同策略

---

## 🛠️ 五、工具系统

### 5.1 工具分组（快捷方式）

在 `tools.allow` / `tools.deny` 中可使用 `group:*` 扩展多个工具：

| 分组 | 包含的工具 |
|------|-----------|
| `group:runtime` | `exec`, `bash`, `process` |
| `group:fs` | `read`, `write`, `edit`, `apply_patch` |
| `group:sessions` | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status` |
| `group:memory` | `memory_search`, `memory_get` |
| `group:web` | `web_search`, `web_fetch` |
| `group:ui` | `browser`, `canvas` |
| `group:automation` | `cron`, `gateway` |
| `group:messaging` | `message` |
| `group:nodes` | `nodes` |
| `group:openclaw` | 所有内置 OpenClaw 工具 |

### 5.2 工具配置文件

`tools.profile` 设置基础工具允许列表：
- `minimal`: 只有 `session_status`
- `coding`: `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image`
- `messaging`: `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`
- `full`: 无限制（等同于未设置）

### 5.3 核心工具列表

#### 执行相关
- **`exec`** - 在工作空间中运行 shell 命令
- **`process`** - 管理后台执行会话
- **`apply_patch`** - 跨一个或多个文件应用结构化补丁

#### 网页相关
- **`web_search`** - 使用 Perplexity、Brave、Gemini、Grok 或 Kimi 搜索网页
- **`web_fetch`** - 获取并提取 URL 的可读内容（HTML → markdown/text）
- **`browser`** - 控制 OpenClaw 管理的专用浏览器

#### 会话管理
- **`sessions_list`** - 列出会话
- **`sessions_history`** - 获取会话历史
- **`sessions_send`** - 向另一个会话发送消息
- **`sessions_spawn`** - 生成隔离的 sub-agent 或 ACP 编码会话
- **`session_status`** - 显示会话状态卡

#### 节点控制
- **`nodes`** - 发现和定位配对的节点
- **`canvas`** - 驱动节点 Canvas
- **`image`** - 使用配置的图像模型分析图像
- **`pdf`** - 分析一个或多个 PDF 文档

#### 消息传递
- **`message`** - 跨 Discord/Google Chat/Slack/Telegram/WhatsApp/Signal/iMessage/MS Teams 发送消息

#### 自动化
- **`cron`** - 管理 Gateway cron jobs 和唤醒
- **`gateway`** - 重启或更新运行的 Gateway 进程

---

## 🧩 六、技能系统（Skills）

### 6.1 什么是 Skills？

Skills 是教 agent 如何使用工具的目录。每个 skill 是一个包含 `SKILL.md` 的目录，其中有 YAML frontmatter 和说明。

### 6.2 加载位置（优先级）

**最高** → **最低**：
1. `<workspace>/skills`（工作空间技能）
2. `~/.openclaw/skills`（管理的/本地技能）
3. bundled skills（打包技能）

**每 agent vs 共享**：
- **Per-agent skills**：在 `<workspace>/skills` 中，仅对该 agent 可见
- **Shared skills**：在 `~/.openclaw/skills` 中，对所有 agent 可见

### 6.3 SKILL.md 格式

必须包含：
```markdown
---
name: skill-name
description: Skill description
---
```

**可选字段**：
- `homepage` - 网站 URL
- `user-invocable` - `true\|false`（默认：`true`），是否作为用户 slash 命令暴露
- `disable-model-invocation` - `true\|false`（默认：`false`），是否从模型提示中排除
- `command-dispatch` - `tool`（可选），slash 命令直接 dispatch 到工具
- `command-tool` - 当 `command-dispatch: tool` 时使用的工具名
- `command-arg-mode` - `raw`（默认）

### 6.4 加载时过滤（Gating）

```markdown
---
name: skill-name
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

**关键字段**：
- `always: true` - 始终包含该 skill
- `os` - 平台列表（`darwin`, `linux`, `win32`）
- `requires.bins` - 必须存在于 PATH 的列表
- `requires.anyBins` - 至少一个存在于 PATH 的列表
- `requires.env` - 必须存在或提供的配置的环境变量列表
- `requires.config` - 必须为真的配置路径列表

---

## 📱 七、节点系统（Nodes）

### 7.1 节点是什么？

- **节点**是配套设备（macOS/iOS/Android/headless）
- 以 `role: "node"` 连接到 Gateway WebSocket
- 暴露命令表面（canvas、camera、screen、location 等）

### 7.2 配对流程

1. **WS nodes** 使用设备配对
2. 节点在 `connect` 时呈现设备身份
3. Gateway 为 `role: node` 创建设备配对请求
4. 通过 devices CLI 批准：`openclaw devices approve <requestId>`

### 7.3 节点命令

#### 屏幕截图（Canvas snapshots）
```bash
openclaw nodes canvas snapshot --node <idOrNameOrIp> --format png
```

#### Canvas 控制
```bash
openclaw nodes canvas present --node <id> --target https://example.com
openclaw nodes canvas hide --node <id>
openclaw nodes canvas navigate https://example.com --node <id>
openclaw nodes canvas eval --node <id> --js "document.title"
```

#### A2UI（Canvas）
```bash
openclaw nodes canvas a2ui push --node <id> --text "Hello"
openclaw nodes canvas a2ui reset --node <id>
```

#### 照片 + 视频（节点相机）
```bash
openclaw nodes camera list --node <id>
openclaw nodes camera snap --node <id> --facing front
openclaw nodes camera clip --node <id> --duration 10s
```

#### 屏幕录制
```bash
openclaw nodes screen record --node <id> --duration 10s --fps 10
```

#### 位置
```bash
openclaw nodes location get --node <id> --accuracy precise
```

#### 系统命令（Node host / Mac node）
```bash
openclaw nodes run --node <id> -- echo "Hello from mac node"
openclaw nodes notify --node <id> --title "Ping" --body "Gateway ready"
```

---

## 🔒 八、安全特性

### 8.1 认证与授权

**设备配对**：
- 所有 WS 客户端（操作员 + 节点）在 `connect` 时包含**设备身份**
- 新设备 ID 需要配对批准
- Gateway 为后续连接颁发**设备令牌**
- **本地**连接（回环或网关主机自己的 tailnet 地址）可以自动批准
- **非本地**连接仍需要明确批准

**Exec 批准**：
- `tools.elevated` 通过 `tools.elevated` 和任何 `agents.list[].tools.elevated` 覆盖限制
- **两者**必须允许
- 仅当 agent 被沙箱化时更改行为（否则无操作）

### 8.2 沙箱（Sandboxing）

**每 agent 沙箱**：
```json5
{
  agents: {
    list: [
      {
        id: "family",
        sandbox: {
          mode: "all",     // 始终沙箱化
          scope: "agent",  // 每个 agent 一个容器
        },
        tools: {
          allow: ["read"],              // 只允许 read 工具
          deny: ["exec", "write", "edit", "apply_patch"],  // 拒绝其他工具
        },
      },
    ],
  },
}
```

### 8.3 工具权限控制

**全局允许/拒绝**：
```json5
{
  tools: { deny: ["browser"] },
}
```

**按提供者限制**：
```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```

---

## 🔄 九、自动化与定时任务

### 9.1 Cron vs Heartbeat

**使用 Heartbeat 时**：
- 多个检查可以批量处理（邮箱 + 日历 + 通知一次完成）
- 需要最近消息的对话上下文
- 时间可以稍微漂移（每~30 分钟即可）
- 想通过组合周期性检查减少 API 调用

**使用 Cron 时**：
- 精确时间要求（"每周一上午 9:00 准时"）
- 任务需要与主会话历史隔离
- 想要不同的模型或思考级别
- 一次性提醒（"20 分钟后提醒我"）
- 输出应直接传递到 channel 而不涉及主会话

### 9.2 Cron 工具

核心操作：
- `status`, `list` - 查看状态和列表
- `add`, `update`, `remove`, `run`, `runs` - 管理 cron job
- `wake` - 入队系统事件 + 可选立即心跳

---

## 🌐 十、通信渠道

### 10.1 支持的渠道

| 渠道 | 说明 |
|------|------|
| WhatsApp | 通过 WhatsApp Web (Baileys) |
| Telegram | 机器人支持 (grammY) |
| Discord | 机器人支持 (channels.discord.js) |
| Mattermost | 机器人支持（插件） |
| iMessage | 通过本地 imsg CLI (macOS) |
| Signal | 原生支持 |
| Slack | 原生支持 |
| 更多 | 通过插件扩展 |

### 10.2 渠道配置示例

**WhatsApp**：
```bash
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

**Discord**：
- 为每个 agent 创建一个 bot
- 启用 Message Content Intent
- 复制每个 token

**Telegram**：
- 通过 BotFather 为每个 agent 创建一个 bot
- 复制每个 token

---

## 📦 十一、部署与安装

### 11.1 快速安装

**macOS/Linux**：
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Windows (PowerShell)**：
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

### 11.2 初始化向导

```bash
openclaw onboard --install-daemon
```

### 11.3 检查 Gateway

```bash
openclaw gateway status
```

### 11.4 打开 Control UI

```bash
openclaw dashboard
```

或直接访问：`http://127.0.0.1:18789/`

### 11.5 远程访问

**首选**：Tailscale 或 VPN

**替代**：SSH 隧道
```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

---

## 🧠 十二、内存与上下文管理

### 12.1 内存系统

**三层架构**：
1. **每日日志** (`memory/YYYY-MM-DD.md`) - 实时记录
2. **精选记忆** (`MEMORY.md`) - 定期由御坂妹妹 17 号整理
3. **长期归档** (`life/archives/`) - 7 天后自动移动

### 12.2 会话压缩（Compaction）

当会话接近自动压缩时，OpenClaw 可以运行**静默内存刷新**提醒模型将持久化笔记写入磁盘。

### 12.3 上下文修剪

默认情况下，OpenClaw 在 LLM 调用前修剪内存中的**旧工具结果**。这不重写 JSONL 历史。

---

## 🎯 十三、最佳实践

### 13.1 配置建议

**安全 DM 模式（多用户）**：
```json5
{
  session: {
    dmScope: "per-channel-peer",
  },
}
```

**会话维护策略**：
```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "45d",
      maxEntries: 800,
      rotateBytes: "20mb",
    },
  },
}
```

**工具限制（family agent）**：
```json5
{
  agents: {
    list: [
      {
        id: "family",
        sandbox: {
          mode: "all",
          scope: "agent",
        },
        tools: {
          allow: ["read"],
          deny: ["exec", "write", "edit", "apply_patch"],
        },
      },
    ],
  },
}
```

### 13.2 性能优化

**大型会话存储**：
- 使用 `mode: "enforce"` 使增长自动受控
- 同时设置时间和数量限制（`pruneAfter` + `maxEntries`）
- 设置 `maxDiskBytes` + `highWaterBytes` 作为硬上限
- 保持 `highWaterBytes` 明显低于 `maxDiskBytes`（默认 80%）

### 13.3 安全实践

- 将第三方技能视为**不可信代码**
- 对不可信输入优先使用沙箱运行
- 将秘密保持在提示和日志之外
- 对 group targeting 使用 `agents.list[].groupChat.mentionPatterns`

---

## 📚 参考资源

### 官方文档
- https://docs.openclaw.ai
- https://docs.openclaw.ai/llms.txt（完整文档索引）

### Skills 仓库
- https://clawhub.com（公开技能注册中心）

### 项目仓库
- 本地文档：`/home/claw/.openclaw/workspace/docs`
- GitHub：https://github.com/openclaw/openclaw
- Discord：https://discord.com/invite/clawd

---

## 📝 学习心得

本次学习主要围绕 OpenClaw 的核心概念展开，涵盖了：

1. **架构理解**：Gateway 作为中央枢纽，Agent 作为独立智能体，Node 作为设备延伸
2. **路由机制**：确定性的 binding 规则，支持多账号、多智能体部署
3. **会话管理**：灵活的 DM 范围设置，自动维护策略，重置机制
4. **工具系统**：丰富的工具集合，分组管理，配置文件支持
5. **技能系统**：可扩展的技能框架，加载时过滤，优先级管理
6. **节点控制**：设备配对，命令执行，媒体 capture
7. **安全特性**：设备配对，沙箱隔离，工具权限控制

OpenClaw 的设计非常注重：
- **隔离性**：每个 agent 完全独立
- **灵活性**：支持多种部署场景
- **安全性**：多层权限控制
- **可维护性**：自动会话清理，配置热重载

---

**汇报准备完成** ✅  
**学习模式**：理论学习，无实践操作  
**下次任务**：2026-03-14 07:00 AM 汇报
