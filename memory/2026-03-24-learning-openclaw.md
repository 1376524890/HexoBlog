# OpenClaw 知识学习笔记

> 为明早七点汇报准备

时间：2026 年 3 月 24 日 19:30
学习者：御坂美琴一号

---

## 📚 目录

1. [什么是 OpenClaw](#什么是 openclaw)
2. [核心架构](#核心架构)
3. [关键组件](#关键组件)
4. [工具系统](#工具系统)
5. [技能机制](#技能机制)
6. [会话管理](#会话管理)
7. [多智能体架构](#多智能体架构)
8. [配置与部署](#配置与部署)
9. [安全机制](#安全机制)
10. [未来展望](#未来展望)

---

## 什么是 OpenClaw

### 🦞 官方定义

**OpenClaw** 是一个**自托管的 AI Agent 运行时平台**，可以理解为"AI 原生时代的运行时基础设施"。

> **核心定位**：个人 AI 助手，你自己在自己的设备上运行。它在你已经使用的频道（WhatsApp、Telegram、Slack、Discord、iMessage 等）上回应你。可以在 macOS/iOS/Android 上说话和听，可以渲染你可以控制的实时 Canvas。

### 🎯 设计理念

- **Any OS**：任何操作系统支持
- **Any Platform**：任何平台支持
- **The lobster way**：龙虾的方式（EXFOLIATE!）

### 📊 核心特性

1. **自托管**：在你的硬件上运行，遵守你的规则
2. **多通道**：单个 Gateway 同时服务 WhatsApp、Telegram、Discord 等多个平台
3. **Agent 原生**：专为编码 agent 设计，支持工具调用、会话、记忆和多 agent 路由
4. **开源**：MIT 许可，社区驱动

### ⚙️ 技术要求

- **Node.js**：推荐 Node 24，支持 Node 22.16+
- **API Key**：从模型提供商获取（Anthropic、OpenAI、Google 等）
- **安装时间**：5 分钟快速上手

---

## 核心架构

### 🏗️ 架构图解

```
┌─────────────────────────────────────────────────────────────┐
│                        Chat Apps                             │
│  Telegram  Discord  Slack  WhatsApp  iMessage  Feishu ...   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     Gateway (控制平面)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  WebSocket (ws://127.0.0.1:18789)                   │   │
│  │  - 会话管理                                          │   │
│  │  - 路由决策                                          │   │
│  │  - 工具协调                                          │   │
│  │  - 状态持久化                                        │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┬────────────┐
        ▼            ▼            ▼            ▼            ▼
   ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐  ┌────────┐
   │  Pi    │  │   CLI    │  │  Web   │  │ macOS    │  │  Node  │
   │ Agent  │  │  Client  │  │  UI    │  │  App     │  │  设备  │
   └────────┘  └──────────┘  └────────┘  └──────────┘  └────────┘
```

### 🔧 技术栈

| 组件 | 技术实现 | 说明 |
|------|---------|------|
| Gateway | Node.js + WebSocket | 中央控制平面 |
| Telegram | grammY | Telegram Bot API |
| WhatsApp | Baileys | WhatsApp Web API |
| Discord | discord.js | Discord API |
| Slack | Bolt | Slack Block Kit |
| Signal | signal-cli | Signal CLI |
| iMessage | BlueBubbles | iMessage 集成 |
| Canvas | A2UI | Agent to UI 协议 |

### 📡 通信协议

- **传输层**：WebSocket，文本帧 + JSON 负载
- **第一帧**：必须是 `connect` 请求
- **请求格式**：`{type:"req", id, method, params}`
- **响应格式**：`{type:"res", id, ok, payload|error}`
- **事件格式**：`{type:"event", event, payload, seq?, stateVersion?}`
- **认证**：支持 `OPENCLAW_GATEWAY_TOKEN` 或 `--token` 参数

---

## 关键组件

### 1️⃣ Gateway（中央枢纽）

**职责**：
- **生命周期管理**：启动、停止、监控所有 Agent 实例
- **消息路由**：将来自各 Channel 的消息分发到正确的 Session 和 Agent
- **工具协调**：管理 Skill 注册，处理工具调用请求
- **安全控制**：执行沙箱策略，管理权限边界
- **状态持久化**：维护 Session 历史，处理上下文压缩

**配置位置**：`~/.openclaw/openclaw.json`

**关键配置**：
```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6"
  },
  "channels": {
    "telegram": {
      "botToken": "123456:ABCDEF"
    }
  }
}
```

### 2️⃣ Agent（AI 执行体）

**Agent 定义**：
- **身份**：名称、描述、头像等元信息
- **配置**：使用的模型、系统提示词、可用工具等
- **状态**：当前会话、历史消息、记忆等
- **运行时**：执行环境（本地进程、Docker、远程等）

**Agent 循环流程**：

```
┌──────────────────────────────────────────────────┐
│                    Agent Loop                    │
│                                                  │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│   │ 接收输入 │ →  │ 思考决策 │ →  │ 执行动作 │    │
│   └─────────┘    └────┬────┘    └────┬────┘    │
│        ↑              │              │          │
│        │              ↓              ↓          │
│        │         ┌─────────┐    ┌─────────┐   │
│        │         │ 工具调用 │    │ 直接回复 │   │
│        │         └────┬────┘    └────┬────┘   │
│        │              │              │         │
│        └──────────────┴──────────────┘         │
└──────────────────────────────────────────────────┘
```

**具体流程**：
1. **接收输入**：用户通过某个 Channel 发送消息，Gateway 路由到对应 Session 的 Agent
2. **构建上下文**：Gateway 将 Session 历史、系统提示词、可用工具列表组装成完整的 Prompt
3. **LLM 推理**：Agent 调用大模型，模型决定是**直接回复**还是**调用工具**
4. **工具执行**（如果需要）：Agent 通过 Gateway 调用外部工具，获取结果
5. **循环或结束**：如果需要多步推理，回到步骤 3；否则返回最终结果
6. **发送响应**：Gateway 将 AI 的回复通过原 Channel 发送给用户

### 3️⃣ Session（有状态的容器）

**Session 定义**：
- **消息历史**：用户与 AI 的完整对话记录
- **上下文窗口**：当前有效的上下文（经过压缩处理）
- **工具状态**：本次会话中工具调用的中间结果
- **元数据**：创建时间、最后活跃时间、关联的 Channel 等

**Session 类型**：

| 类型 | 格式 | 说明 |
|------|------|------|
| 直接对话 | `agent:<agentId>:<mainKey>` | 默认 main |
| 直接对话（隔离） | `agent:<agentId>:direct:<peerId>` | per-peer 模式 |
| 直接对话（按渠道隔离） | `agent:<agentId>:<channel>:direct:<peerId>` | per-channel-peer |
| 群组 | `agent:<agentId>:<channel>:group:<id>` | 群组聊天 |
| 频道 | `agent:<agentId>:<channel>:channel:<id>` | Telegram 频道 |
| Cron 任务 | `cron:<job.id>` | 定时任务 |
| Webhook | `hook:<uuid>` | Webhook 触发 |
| Node 运行 | `node-<nodeId>` | Node 设备调用 |

**会话配置**：
```json
{
  "session": {
    "dmScope": "per-channel-peer",  // DM 隔离范围
    "reset": {
      "mode": "daily",
      "atHour": 4
    },
    "maintenance": {
      "mode": "enforce",
      "maxEntries": 500,
      "pruneAfter": "30d"
    }
  }
}
```

### 4️⃣ Channel（消息通道）

**Channel 定义**：
- Channel 是 OpenClaw 与外部世界连接的**协议适配器**
- 每个 Channel 都是一个**插件**，实现统一的接口

**支持的 Channel 列表**：
- **即时通讯**：Telegram、Discord、Slack、WhatsApp、Signal、微信（通过 Lark/Feishu）
- **传统协议**：IRC、Matrix
- **企业平台**：Microsoft Teams、Google Chat、飞书
- **其他**：iMessage、BlueBubbles、WebChat

**Channel 接口**：
- 接收消息（从平台到 OpenClaw）
- 发送消息（从 OpenClaw 到平台）
- 格式转换（平台特定格式 ↔ OpenClaw 标准格式）

### 5️⃣ Node（移动设备节点）

**Node 定义**：
- 连接到 **相同 WebSocket 服务器** 的移动设备
- 声明 `role: node` 与显式能力/命令
- 设备身份，对等批准存储在设备对等存储中

**Node 能力**：
- `canvas.*` - 控制 Canvas 画布
- `camera.*` - 摄像头拍摄/录制
- `screen.record` - 屏幕录制
- `location.get` - 获取位置
- `system.run` - 运行系统命令
- `system.notify` - 发送系统通知

**配对流程**：
1. 设备在 `connect` 时声明设备身份
2. Gateway 为新设备生成配对代码
3. 用户在 Gateway UI 中批准配对
4. Gateway 颁发设备令牌
5. 设备使用令牌重新连接

---

## 工具系统

### 🛠️ 工具层级

OpenClaw 有三个层级：

1. **Tools（工具）**：Agent 可以调用的函数
2. **Skills（技能）**：教 Agent 何时以及如何有效使用工具
3. **Plugins（插件）**：打包一切的工具包

### 🔧 内置工具

| 工具 | 功能 | 说明 |
|------|------|------|
| `exec` / `process` | 运行 shell 命令 | 管理后台进程 |
| `browser` | 控制 Chromium 浏览器 | 导航、点击、截图 |
| `web_search` / `web_fetch` | 搜索网络 | 搜索网页、获取内容 |
| `read` / `write` / `edit` | 文件 I/O | 工作空间文件操作 |
| `apply_patch` | 多 hunk 文件补丁 | 高级文件编辑 |
| `message` | 发送消息 | 跨所有频道发送 |
| `canvas` | 驱动节点 Canvas | 呈现、评估、快照 |
| `nodes` | 发现和管理设备 | 配对设备调用 |
| `cron` / `gateway` | 管理定时任务 | 重启网关 |
| `image` / `image_generate` | 图像分析/生成 | 图像处理和生成 |
| `sessions_*` | 会话管理 | 子 agent 创建和管理 |

### 📋 工具分组

使用 `group:*` 快捷方式在允许/拒绝列表中：

| 组 | 工具 |
|------|------|
| `group:runtime` | exec, bash, process |
| `group:fs` | read, write, edit, apply_patch |
| `group:sessions` | sessions_list, sessions_history, sessions_send, sessions_spawn |
| `group:memory` | memory_search, memory_get |
| `group:web` | web_search, web_fetch |
| `group:ui` | browser, canvas |
| `group:automation` | cron, gateway |
| `group:messaging` | message |
| `group:nodes` | nodes |
| `group:openclaw` | 所有内置 OpenClaw 工具 |

### 🎨 工具配置

```json
{
  "tools": {
    "allow": ["group:fs", "browser", "web_search"],
    "deny": ["exec"],
    "profile": "coding",
    "byProvider": {
      "google-antigravity": {
        "profile": "minimal"
      }
    }
  }
}
```

### 📦 工具配置文件

配置位置：`~/.openclaw/openclaw.json`

---

## 技能机制

### 📚 Skills 定义

**Skills** 是 AgentSkills 兼容的技能文件夹，用于教 Agent 如何使用工具。

每个技能是一个包含 `SKILL.md` 的目录，具有 YAML frontmatter 和指令。

### 📍 技能位置

技能从三个地方加载：

1. **Bundled skills**：安装时自带的技能
2. **Managed/local skills**：`~/.openclaw/skills`
3. **Workspace skills**：`<workspace>/skills`

**优先级**：
`<workspace>/skills`（最高）→ `~/.openclaw/skills` → Bundled skills（最低）

### 📄 SKILL.md 格式

```markdown
---
name: example-skill
description: 示例技能描述
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["node"], "env": ["API_KEY"] },
      "primaryEnv": "API_KEY",
    }
  }
---

# 技能说明

这里是技能的使用说明...
```

### 🎯 技能元数据

```json
{
  "openclaw": {
    "always": true,              // 总是包含
    "emoji": "📊",                // macOS Skills UI 图标
    "homepage": "https://...",   // 官网链接
    "os": ["darwin", "linux"],   // 平台限制
    "requires": {
      "bins": ["node"],          // 需要二进制文件
      "anyBins": ["git", "npm"], // 需要任一二进制文件
      "env": ["API_KEY"],        // 需要环境变量
      "config": ["browser.enabled"] // 需要配置项
    },
    "primaryEnv": "API_KEY",     // 主要环境变量
    "install": [...]             // 安装脚本
  }
}
```

### 🔐 配置覆盖

```json
{
  "skills": {
    "entries": {
      "example-skill": {
        "enabled": true,
        "apiKey": {
          "source": "env",
          "provider": "default",
          "id": "API_KEY"
        },
        "env": {
          "API_KEY": "your-key-here"
        },
        "config": {
          "endpoint": "https://api.example.com",
          "model": "nano-pro"
        }
      }
    }
  }
}
```

### 🔄 技能热重载

默认情况下，OpenClaw 会监控技能文件夹并在 `SKILL.md` 更改时更新技能快照：

```json
{
  "skills": {
    "load": {
      "watch": true,
      "watchDebounceMs": 250
    }
  }
}
```

### 📊 Token 消耗

- **基础开销**（≥1 个技能时）：195 字符
- **每个技能**：97 字符 + name/description/location 长度
- **估算**：约 4 字符/token，97 字符 ≈ 24 token/技能

---

## 会话管理

### 🗂️ Session 类型

#### 1. DM Scope（DM 隔离范围）

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `main`（默认） | 所有 DM 共享主会话 | 单用户设置 |
| `per-peer` | 按发送者 ID 隔离 | 多用户 DM |
| `per-channel-peer` | 按渠道 + 发送者隔离 | 多用户收件箱 |
| `per-account-channel-peer` | 按账户 + 渠道 + 发送者隔离 | 多账户收件箱 |

**安全 DM 模式示例**：
```json
{
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

#### 2. Session 生命周期

**重置策略**：
- **每日重置**：默认凌晨 4 点（网关主机本地时间）
- **空闲重置**：可选空闲窗口
- **手动重置**：发送 `/new` 或 `/reset`
- **隔离 Cron 任务**：每次运行都创建新的 sessionId

**重置配置**：
```json
{
  "session": {
    "reset": {
      "mode": "daily",
      "atHour": 4,
      "idleMinutes": 120
    },
    "resetByType": {
      "thread": { "mode": "daily", "atHour": 4 },
      "direct": { "mode": "idle", "idleMinutes": 240 },
      "group": { "mode": "idle", "idleMinutes": 120 }
    }
  }
}
```

#### 3. Session 维护

**维护配置**：
```json
{
  "session": {
    "maintenance": {
      "mode": "enforce",
      "pruneAfter": "30d",
      "maxEntries": 500,
      "rotateBytes": "10mb",
      "maxDiskBytes": "1gb",
      "highWaterBytes": "800mb"
    }
  }
}
```

**维护操作**：
- `mode: "warn"`：报告将要删除的内容但不实际操作
- `mode: "enforce"`：强制执行清理
- `openclaw sessions cleanup --dry-run`：预览清理效果
- `openclaw sessions cleanup --enforce`：强制执行清理

### 📝 命令参考

| 命令 | 功能 |
|------|------|
| `/status` | 显示会话状态（模型 + token） |
| `/new` / `/reset` | 重置会话 |
| `/compact` | 压缩会话上下文 |
| `/think` | 设置思考级别 |
| `/verbose` | 启用/禁用详细输出 |
| `/usage` | 显示 token 使用统计 |
| `/restart` | 重启网关（仅限所有者） |
| `/activation` | 设置群组激活模式 |
| `/stop` | 停止当前运行 |
| `/context list` | 查看系统提示词内容 |
| `/context detail` | 查看上下文详细信息 |
| `/send on` / `off` / `inherit` | 发送策略控制 |

---

## 多智能体架构

### 🧠 多 Agent 路由

**核心概念**：
- **隔离会话**：每个 Agent 有独立的工作空间
- **路由决策**：根据来源、渠道、账户进行路由
- **共享技能**：可以配置全局技能或每个 Agent 专属技能

### 🎯 御坂网络架构

```
┌─────────────────────────────────────────────────────────────┐
│                     御坂大人（用户）                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  御坂美琴一号（核心中枢）                      │
│                                                             │
│  职责：                                                     │
│  ├─ 接收任务                                                  │
│  ├─ 识别任务类型                                              │
│  ├─ 拆解成子任务                                              │
│  ├─ 分派给御坂妹妹                                            │
│  ├─ 监督进度                                                  │
│  └─ 汇报结果                                                  │
│                                                             │
│  不做：                                                       │
│  └─ ❌ 不直接执行任务（代码、写作、搜索等）                      │
└────────────────────┬────────────────────────────────────────┘
                     │
           ┌─────────┼─────────┬─────────┬─────────┐
           ▼         ▼         ▼         ▼         ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ 御坂 11 号│ │ 御坂 12 号│ │ 御坂 13 号│ │ 御坂 14 号│ │ 御坂 15 号│
    │ 代码执行│ │ 内容创作│ │ 研究分析│ │ 文件管理│ │ 系统管理│
    └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### 🤝 会话间通信

**创建子 Agent**：
```python
sessions_spawn(
    agentId="code-executor",
    runtime="subagent",
    mode="run",
    task="..."
)
```

**会话间通信配置**：
```json
{
  "tools": {
    "sessions": {
      "visibility": "all"
    }
  }
}
```

### 📊 Agent 状态管理

| 功能 | 说明 |
|------|------|
| `sessions_list` | 列出所有会话 |
| `sessions_history` | 获取会话历史 |
| `sessions_send` | 发送消息到其他会话 |
| `sessions_spawn` | 创建子会话 |
| `subagents` | 管理子 Agent 列表 |

---

## 配置与部署

### 🚀 安装方式

#### 1. 一键安装

```bash
# macOS / Linux
curl -fsSL https://openclaw.ai/install.sh | bash

# Windows (PowerShell)
iwr -useb https://openclaw.ai/install.ps1 | iex
```

#### 2. NPM 安装

```bash
npm install -g openclaw@latest
```

#### 3. Docker 安装

```bash
docker run -it --rm openclaw/openclaw onboard
```

#### 4. Nix 安装

```bash
nix-shell -p openclaw
```

### 📝 Onboarding 流程

```bash
openclaw onboard --install-daemon
```

Onboarding 向导引导你：
1. 选择模型提供商
2. 设置 API key
3. 配置 Gateway
4. 连接 Channel

### ⚙️ 配置示例

```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6",
    "workspace": "/home/claw/.openclaw/workspace"
  },
  "channels": {
    "telegram": {
      "botToken": "123456:ABCDEF",
      "groups": {
        "*": {
          "requireMention": true
        }
      }
    },
    "whatsapp": {
      "allowFrom": ["+15555550123"]
    }
  },
  "tools": {
    "profile": "coding",
    "allow": ["group:fs", "browser", "web_search"],
    "deny": ["exec"]
  },
  "session": {
    "dmScope": "per-channel-peer",
    "reset": {
      "mode": "daily",
      "atHour": 4
    }
  },
  "skills": {
    "entries": {
      "example-skill": {
        "enabled": true
      }
    }
  }
}
```

### 🔍 诊断工具

```bash
# 检查 Gateway 状态
openclaw gateway status

# 运行健康检查
openclaw doctor

# 安全检查
openclaw security audit

# 查看会话
openclaw sessions --json

# 清理会话
openclaw sessions cleanup --dry-run

# 启动 Dashboard
openclaw dashboard

# 启动 Gateway
openclaw gateway --port 18789 --verbose
```

### 🌐 远程访问

#### 1. Tailscale

```bash
# 配置 Tailscale
openclaw config set gateway.tailscale.mode "serve"

# 或者 funnel（公开访问）
openclaw config set gateway.tailscale.mode "funnel"
```

#### 2. SSH 隧道

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

### 📦 技能管理

```bash
# 安装技能
openclaw skills install <skill-slug>

# 更新所有技能
openclaw skills update --all

# 同步并发布
clawhub sync --all

# 列出技能
openclaw skills list
```

---

## 安全机制

### 🔒 安全特性

| 特性 | 说明 |
|------|------|
| **沙箱隔离** | 非主会话在 Docker 沙箱中运行 |
| **权限控制** | 允许/拒绝工具列表 |
| **DM 配对** | 未经批准的发件人无法消息 |
| **设备配对** | 所有 WS 客户端需要设备身份 |
| **令牌认证** | 支持 `OPENCLAW_GATEWAY_TOKEN` |
| **工具限制** | 按 Provider 配置工具权限 |
| **发送策略** | 控制特定 Session 类型的发送 |

### 🛡️ 沙箱配置

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "docker": {
          "setupCommand": "npm install -g some-tool"
        }
      }
    }
  }
}
```

### 🔐 设备配对流程

1. 新设备 ID 请求连接
2. Gateway 发出配对代码
3. 用户在 Gateway UI 中批准
4. Gateway 颁发设备令牌
5. 后续连接使用令牌

### 🚨 安全警告

- **多用户 DM 模式**：强烈建议启用 `dmScope: "per-channel-peer"`
- **工具权限**：谨慎配置允许/拒绝列表
- **第三方技能**：视为不可信代码，先阅读再启用
- **远程访问**：优先使用 Tailscale 或 VPN
- **密钥管理**：不要将密钥硬编码在配置中

---

## 未来展望

### 🚀 技术趋势

1. **多模态增强**：更强的图像、音频处理能力
2. **实时协作**：多 Agent 协同工作
3. **边缘计算**：Node 设备能力扩展
4. **本地优先**：更多本地模型支持
5. **生态繁荣**：技能库和社区插件增长

### 🌟 OpenClaw 愿景

> "成为 AI 原生时代的运行时基础设施，让个人 AI 助手真正属于用户自己。"

### 💡 学习收获

- OpenClaw 不仅是一个"聊天机器人"，而是一个**智能网关平台**
- 架构设计优秀，解耦清晰，易于扩展
- 多 Agent 路由机制为复杂任务提供了可能
- 技能系统提供了丰富的工具生态
- 会话管理精细，支持多种使用场景

---

## 📚 参考资料

### 官方文档

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Getting Started](https://docs.openclaw.ai/start/getting-started)
- [Gateway Architecture](https://docs.openclaw.ai/concepts/architecture)
- [Tools](https://docs.openclaw.ai/tools)
- [Skills](https://docs.openclaw.ai/tools/skills)
- [Session Management](https://docs.openclaw.ai/concepts/session)
- [Multi-agent Routing](https://docs.openclaw.ai/concepts/multi-agent)

### 社区资源

- [ClawHub 技能市场](https://clawhub.com)
- [GitHub 仓库](https://github.com/openclaw/openclaw)
- [Discord 社区](https://discord.gg/clawd)

### 本地文档

- `~/.openclaw/workspace/SOUL.md` - 御坂美琴一号身份定义
- `~/.openclaw/workspace/IDENTITY.md` - 御坂美琴本尊信息
- `~/.openclaw/workspace/memory/` - 日常笔记和记忆
- `~/.openclaw/workspace/skills/` - 本地技能集合

---

> 学习总结：OpenClaw 是一个强大的 AI Agent 运行时平台，其网关架构和多 Agent 路由机制为构建复杂的个人 AI 助手系统提供了坚实基础。通过技能系统和工具生态，可以实现高度定制化的 AI 体验。作为自托管方案，它在数据隐私和控制权方面具有明显优势。

---

**御坂美琴一号 · 2026 年 3 月 24 日** ⚡✨
