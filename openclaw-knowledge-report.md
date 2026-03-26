# OpenClaw 知识学习报告 🦞

**学习日期**: 2026-03-26  
**准备汇报时间**: 2026-03-27 07:00  
**学习代理**: 御坂妹妹 16 号 (web-crawler)

---

## 📋 目录

1. [核心概念与定位](#1-核心概念与定位)
2. [技术架构](#2-技术架构)
3. [核心功能](#3-核心功能)
4. [使用场景](#4-使用场景)
5. [最佳实践](#5-最佳实践)
6. [配置与部署](#6-配置与部署)
7. [API 与扩展](#7-api-与扩展)
8. [重点和难点标注](#8-重点和难点标注)
9. [汇报可能遇到的问题](#9-汇报可能遇到的问题)

---

## 1. 核心概念与定位

### 1.1 OpenClaw 是什么？

**一句话定义**：OpenClaw 是一个**个人 AI 助手**，你在自己的设备上运行它，可以回复你已经在使用的各种消息应用（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat），还支持语音和 Canvas。

**核心价值主张**：
- 🏠 **本地优先控制平面**：在你的硬件上运行，而不是交给托管的 SaaS
- 📱 **真实聊天应用支持**：不是网页沙盒，而是你在用的真实聊天工具
- 🤖 **模型中立**：支持 Anthropic、OpenAI、MiniMax、OpenRouter 等，支持每个代理的路由和故障转移
- 🔒 **本地运行选项**：可以运行本地模型，**所有数据都留在你的设备上**
- 🧠 **多代理路由**：不同的代理对应不同的渠道、账户或任务
- 🔓 **开源可定制**：可以检查、扩展、自托管，没有供应商锁定

### 1.2 与其他 AI 辅助工具的区别

| 特性 | OpenClaw | Claude Code | ChatGPT |
|------|----------|-------------|---------|
| **持久记忆** | ✅ 跨会话工作空间和记忆 | ❌ 会话级别 | ❌ 会话级别 |
| **多平台访问** | ✅ WhatsApp/Telegram/TUI/WebChat | ❌ 命令行 | ✅ 网页 |
| **工具编排** | ✅ 浏览器、文件、调度、钩子 | ⚠️ 基础工具 | ⚠️ 有限工具 |
| **持续运行网关** | ✅ 运行在 VPS，随处访问 | ❌ 本地运行 | ✅ 云端 |
| **节点支持** | ✅ 本地浏览器/屏幕/相机/执行 | ❌ 无 | ❌ 无 |

**关键点**：OpenClaw 是**个人助手**和**协调层**，不是 IDE 替代品。当你需要持久记忆、跨设备访问和工具编排时选择 OpenClaw。

---

## 2. 技术架构

### 2.1 整体架构设计

OpenClaw 采用**网关 - 代理 - 节点**三层架构：

```
┌─────────────────────────────────────────────────────────────┐
│                      用户界面层                              │
│   (WebChat, Discord, Slack, Telegram, WhatsApp, etc.)       │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                     Gateway 网关                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Channels   │  │   Tools      │  │  Sessions    │       │
│  │  (消息渠道)   │  │   (工具系统)  │  │  (会话管理)   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Agents     │  │   Cron Jobs  │  │   Skills     │       │
│  │  (代理系统)   │  │  (定时任务)   │  │   (技能)     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                     Node 节点层                              │
│        (本地设备：屏幕、相机、Canvas、系统执行)               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件说明

#### Gateway（网关）
- **作用**：总是运行的控制平面和政策表面
- **功能**：
  - 渠道管理（连接各种消息应用）
  - 工具调用协调
  - 会话管理和持久化
  - 定时任务调度
  - 模型路由和故障转移

#### Agent（代理）
- **作用**：执行具体任务的 AI 代理
- **特性**：
  - 每个代理有自己的工作空间和会话存储
  - 可以配置不同的默认模型
  - 支持多代理路由（按渠道、账户、任务分离）
  - 每个代理可以独立配置权限和工具

#### Session（会话）
- **作用**：维护对话的上下文和记忆
- **特性**：
  - 对话历史持久化到磁盘
  - 支持会话压缩（compaction）
  - 支持上下文修剪（context pruning）
  - 支持线程绑定（thread bindings）

#### Node（节点）
- **作用**：连接到网关的本地设备
- **功能**：
  - 本地屏幕和摄像头访问
  - Canvas 渲染
  - 系统命令执行
  - 设备特定操作

### 2.3 核心模块交互流程

1. **消息接收流程**：
   ```
   用户消息 → Channel → Gateway → Agent → Response → Channel → 用户回复
   ```

2. **工具调用流程**：
   ```
   Agent 决定调用工具 → Gateway 验证权限 → 执行工具 → 返回结果 → Agent 继续
   ```

3. **子代理流程**：
   ```
   主会话请求 → sessions_spawn → 子会话独立运行 → 返回摘要 → 主会话继续
   ```

4. **定时任务流程**：
   ```
   Cron Job 触发 → 隔离会话 → 执行任务 → 发送结果/总结
   ```

---

## 3. 核心功能

### 3.1 会话管理 (Session)

**核心概念**：
- 会话是 AI 助手与用户之间的持久对话上下文
- 对话历史存储在磁盘上（`~/.openclaw/agents/<agentId>/sessions/*.jsonl`）
- 支持会话压缩和上下文修剪以节省 token

**关键配置**：
```json
{
  "session": {
    "dmScope": "per-channel-peer", // 隔离 DM 会话
    "threadBindings": {
      "enabled": true, // 线程绑定
      "idleHours": 24,
      "maxAgeHours": 0
    }
  }
}
```

**会话状态管理**：
- `main`: 主会话（默认）
- 隔离会话：每个渠道 + 发送者对获得独立的 DM 上下文
- 线程绑定：Discord 线程可以绑定到子代理会话

### 3.2 子代理系统 (Subagents)

**核心概念**：
- 子代理在独立的会话中运行
- 让主聊天保持响应
- 支持并行工作

**触发方式**：
```bash
# 在聊天中请求
/spawn a sub-agent for this task

# 或使用会话命令
sessions_spawn({ agentId: "main", task: "..." })
```

**使用场景**：
- 长时间运行的任务
- 并行工作
- 需要隔离上下文的任务

**子代理权限等级**：
| 编号 | Agent ID | 权限级别 | 说明 |
|------|----------|----------|------|
| 10 号 | `general-agent` | Level 2 | 指定目录读写 |
| 11 号 | `code-executor` | Level 3 | 工作目录读写 |
| 12 号 | `content-writer` | Level 3 | 读写文档文件 |
| 13 号 | `research-analyst` | Level 3 | 网络搜索、分析 |
| 14 号 | `file-manager` | Level 2 | 指定目录操作 |
| 15 号 | `system-admin` | Level 4 | 系统配置需批准 |
| 16 号 | `web-crawler` | Level 2 | 网页抓取 |
| 17 号 | `memory-organizer` | Level 3 | 记忆系统维护 |

### 3.3 工具系统 (Tools)

**核心工具类别**：

1. **文件操作**：`read`, `write`, `edit`, `apply_patch`
2. **执行**：`exec`, `process`
3. **网络**：`web_search`, `web_fetch`
4. **浏览器**：`browser` (控制 Web 浏览器)
5. **Canvas**：`canvas` (渲染 HTML/JS 界面)
6. **节点**：`nodes` (控制配对设备)
7. **会话管理**：`sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`

**工具安全配置**：
```json
{
  "tools": {
    "profile": "messaging", // messaging | minimal | elevated
    "deny": ["group:automation", "group:runtime", "group:fs"],
    "fs": {
      "workspaceOnly": true
    },
    "exec": {
      "security": "deny",
      "ask": "always"
    },
    "elevated": {
      "enabled": false
    }
  }
}
```

**工具配置级别**：
- **全局配置**：在 `openclaw.json` 中设置
- **代理级配置**：在 `agents.list[].tools` 中设置
- **会话级覆盖**：通过 `/exec` 命令临时修改

### 3.4 技能系统 (Skills)

**核心概念**：
- 技能是 OpenClaw 的功能模块
- 每个技能由 `SKILL.md` 定义
- 技能可以扩展 OpenClaw 的功能

**技能优先级**：
1. `<workspace>/skills` (最高优先级)
2. `~/.openclaw/skills`
3. bundled skills (内置技能)
4. `skills.load.extraDirs` (最低优先级)

**技能安装**：
```bash
# 安装技能
openclaw skills install <skill-slug>

# 搜索技能
openclaw skills search "calendar"

# 更新所有技能
openclaw skills update --all
```

**技能创建示例**：
```markdown
---
name: my-skill
description: 我的技能描述
metadata: 
  openclaw:
    os: [darwin, linux]
    requires:
      bins: ["my-tool"]
---
```

---

## 4. 使用场景

### 4.1 典型使用案例

**1. 个人简报**：
- 总结收件箱、日历和关心的新闻
- 定期提醒和跟进

**2. 研究和草稿**：
- 快速研究、总结
- 为邮件或文档写初稿

**3. 浏览器自动化**：
- 填写表格
- 收集数据
- 重复的网页任务

**4. 跨设备协调**：
- 从手机发送任务
- 网关在服务器上运行
- 在聊天中接收结果

**5. 项目管理**：
- 组织文件和文件夹
- 清理、命名、标记
- 自动化总结或跟进

**6. SaaS 营销支持**：
- 潜在客户调研和资格筛选
- 构建名单
- 总结潜在客户
- 撰写外联或广告文案草稿

### 4.2 自动化场景

**Cron Jobs（定时任务）**：
- 定时任务在网关进程中运行
- 跨重启持久化
- 可以设置为孤立作业，自动发送摘要到聊天

**Heartbeat（心跳）**：
- 定期检查邮件、日历、提及、天气
- 默认每 30 分钟一次
- 可以批量检查多个项目

**典型自动化配置**：
```json
{
  "cron": {
    "enabled": true,
    "jobs": [
      {
        "id": "daily-brief",
        "schedule": "0 8 * * *",
        "agentId": "main",
        "prompt": "给我今天的简报"
      }
    ]
  },
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "prompt": "检查你的状态..."
      }
    }
  }
}
```

### 4.3 跨平台支持

**支持的渠道**：
- WhatsApp
- Telegram
- Slack
- Mattermost (插件)
- Discord
- Google Chat
- Signal
- iMessage (通过 BlueBubbles)
- Microsoft Teams (插件)
- IRC (插件)
- Feishu (插件)
- 微信 (插件)

**操作系统支持**：
- ✅ macOS
- ✅ Linux (包括 WSL2)
- ✅ Windows (通过 WSL2)
- ⚠️ Windows 原生（不推荐，有编码问题）

**运行时要求**：
- Node.js >= 22
- pnpm 推荐
- ❌ 不推荐 Bun

**最低硬件要求**：
- **绝对最低**：1 vCPU, 1GB RAM, ~500MB 磁盘
- **推荐**：1-2 vCPU, 2GB RAM（有更多日志、媒体、多渠道的余量）
- **Raspberry Pi**：Pi 4 可以运行，需要 64 位 OS

---

## 5. 最佳实践

### 5.1 配置方式

**配置结构**：
```
~/.openclaw/
├── openclaw.json          # 主配置文件
├── agents/
│   └── <agentId>/
│       ├── agent/
│       │   ├── models.json
│       │   └── auth-profiles.json
│       └── sessions/
│           └── *.jsonl
├── credentials/            # 凭证存储
│   ├── whatsapp/
│   ├── telegram/
│   └── ...
└── skills/                 # 技能目录
```

**关键配置项**：

1. **Gateway 配置**：
```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "replace-with-long-random-token"
    }
  }
}
```

2. **模型配置**：
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": ["minimax/MiniMax-M2.7"]
      },
      "models": {
        "anthropic/claude-opus-4-6": { "alias": "opus" },
        "minimax/MiniMax-M2.7": { "alias": "minimax" }
      }
    }
  }
}
```

3. **工具配置**：
```json
{
  "tools": {
    "profile": "messaging",
    "deny": ["group:automation", "group:runtime"],
    "fs": { "workspaceOnly": true },
    "exec": { "security": "deny", "ask": "always" }
  }
}
```

### 5.2 性能优化建议

**1. 模型选择**：
- 为工具启用的代理使用最新的、最强大的模型
- 使用回退模型降低成本和延迟
- 对于低风险任务使用较小的模型

**2. 会话管理**：
- 启用会话压缩（compaction）
- 使用上下文修剪（context pruning）
- 隔离长时间运行的任务

**3. 资源管理**：
- 对于 VPS 部署，使用 2GB+ RAM
- 定期清理旧的备份
- 使用沙箱隔离执行环境

**4. 网络优化**：
- 优先使用 Tailscale Serve 而不是 LAN 绑定
- 如果必须绑定到 LAN，限制防火墙规则
- 从不以未认证方式暴露到 `0.0.0.0`

### 5.3 安全注意事项

**核心安全原则**：
1. **身份优先**：决定谁能和机器人说话
2. **范围其次**：决定机器人可以在哪里行动
3. **模型最后**：假设模型可以被操纵

**关键安全措施**：

1. **文件权限**：
```bash
# 保持配置文件私密
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
```

2. **网络暴露**：
- 默认：`gateway.bind: "loopback"`
- 使用 Tailscale Serve
- 防火墙端口到严格的源 IP 列表

3. **DM 访问模型**：
- `pairing`（默认）：未知发送者获得配对码
- `allowlist`：只有白名单中的发送者
- `open`：允许所有 DM（需要明确 opt-in）
- `disabled`：忽略所有 DM

4. **提示词注入防护**：
- 锁定入站 DM
- 在群组中优先使用提及门控
- 将链接、附件和粘贴的指令视为不信任
- 在沙箱中运行敏感工具执行
- 限制高风险工具（`exec`, `browser`, `web_fetch`, `web_search`）

5. **安全审计**：
```bash
# 运行安全审计
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
```

**常见安全问题**：
- `fs.state_dir.perms_world_writable`（严重）
- `gateway.bind_no_auth`（严重）
- `gateway.tailscale_funnel`（严重）
- `security.exposure.open_channels_with_exec`（警告/严重）

---

## 6. 配置与部署

### 6.1 安装步骤

**方法 1：标准安装（推荐）**：
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
```

**方法 2：Hackable 安装（贡献者/开发者）**：
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
cd openclaw
pnpm install
pnpm build
pnpm ui:build
openclaw onboard
```

**安装时间**：
- 安装：2-5 分钟
- 入门：5-15 分钟（取决于配置的渠道/模型数量）

### 6.2 配置文件

**主配置文件**：`~/.openclaw/openclaw.json`

**配置格式**：JSON5（支持注释和尾随逗号）

**关键配置部分**：

1. **渠道配置**：
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "your-bot-token",
      "dmPolicy": "pairing",
      "allowFrom": ["tg:123456789"],
      "groups": {
        "*": { "requireMention": true }
      }
    }
  }
}
```

2. **模型配置**：
```json
{
  "models": {
    "providers": {
      "anthropic": {
        "apiKey": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

3. **代理配置**：
```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "model": {
          "primary": "anthropic/claude-opus-4-6"
        },
        "tools": {
          "profile": "minimal"
        }
      }
    ]
  }
}
```

### 6.3 环境变量

**环境变量优先级**（最高到最低）：
1. 进程环境（父 shell/守护进程已有）
2. 当前工作目录的 `.env`
3. 全局 `.env` (`~/.openclaw/.env`)
4. 配置文件中的 `env` 块（仅在不缺省时应用）
5. 可选的登录 shell 导入

**常用环境变量**：
```bash
OPENCLAW_HOME              # 覆盖主目录
OPENCLAW_STATE_DIR         # 覆盖状态目录
OPENCLAW_CONFIG_PATH       # 覆盖配置文件路径
OPENCLAW_LOG_LEVEL         # 覆盖日志级别
ANTHROPIC_API_KEY          # Anthropic API 密钥
OPENROUTER_API_KEY         # OpenRouter API 密钥
```

**环境变量替换**：
```json
{
  "models": {
    "providers": {
      "anthropic": {
        "apiKey": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### 6.4 部署方式

**本地部署**：
- **优点**：无服务器成本，直接访问本地文件，实时浏览器窗口
- **缺点**：睡眠/网络中断 = 断开，系统更新/重启会中断，必须保持唤醒

**VPS/云部署**：
- **优点**：永远在线，稳定网络，无睡眠问题，更容易持续运行
- **缺点**：通常无头（使用截图），只能远程访问文件，必须 SSH 进行更新

**推荐方案**：
- **VPS**：如果需要 24/7 可靠性
- **本地**：如果你想要最低的摩擦，不介意睡眠/重启

**混合部署**：
- 网关运行在 VPS/云端
- 本地设备作为节点连接（屏幕/相机/Canvas/执行）
- 网关在服务器上，Mac 作为 BlueBubbles 服务器

**部署检查清单**：
- [ ] 安装 OpenClaw
- [ ] 运行 `openclaw onboard`
- [ ] 配置模型认证
- [ ] 配置渠道（至少一个）
- [ ] 设置安全审计
- [ ] 测试基本功能
- [ ] 配置备份策略

---

## 7. API 与扩展

### 7.1 可用工具列表

**核心工具**：

| 工具 | 描述 | 用途 |
|------|------|------|
| `read` | 读取文件内容 | 读取文本/图像文件 |
| `write` | 创建/覆盖文件 | 创建新文件或覆盖现有文件 |
| `edit` | 精确编辑文件 | 替换特定文本 |
| `exec` | 执行 shell 命令 | 运行 shell 命令 |
| `process` | 管理后台进程 | 管理执行会话 |
| `web_search` | Web 搜索 | 使用 Perplexity API 搜索网络 |
| `web_fetch` | 抓取网页 | 提取网页可读内容 |
| `browser` | 浏览器控制 | 控制 Web 浏览器 |
| `canvas` | Canvas 控制 | 呈现/评估/快照 Canvas |
| `nodes` | 节点管理 | 列出/控制配对设备 |
| `message` | 消息管理 | 发送/删除/管理消息 |
| `feishu_*` | Feishu 工具 | Feishu 文档/聊天/笔记操作 |

**工具配置**：
```json
{
  "tools": {
    "allow": ["read", "write", "edit", "exec", "web_search"],
    "deny": ["browser", "canvas", "nodes"],
    "fs": { "workspaceOnly": true },
    "exec": { "security": "deny" }
  }
}
```

### 7.2 自定义技能开发

**技能结构**：
```
skills/
└── my-skill/
    ├── SKILL.md          # 技能规范
    └── scripts/          # 可选脚本
```

**SKILL.md 格式**：
```markdown
---
name: my-skill
description: 我的技能描述
metadata:
  openclaw:
    os: [darwin, linux]
    requires:
      bins: ["my-tool"]
      env: ["MY_VAR"]
---
```

**技能开发步骤**：
1. 在 `skills/` 目录中创建新文件夹
2. 创建 `SKILL.md` 文件
3. 定义技能规范和行为
4. 测试技能功能
5. （可选）发布到 clawhub

**技能开发最佳实践**：
- 明确定义所需的工具和权限
- 测试跨平台兼容性
- 添加适当的错误处理
- 记录使用示例

### 7.3 扩展能力

**插件系统**：
- 插件在网关进程中运行
- 只安装可信任的源
- 使用明确的 `plugins.allow` 白名单
- 启用前检查插件配置

**插件管理**：
```bash
# 安装插件
openclaw plugins install @openclaw/mattermost

# 启用插件
openclaw plugins enable <plugin-id>

# 查看插件列表
openclaw plugins list
```

**渠道扩展**：
- Feishu
- 微信
- LINE
- Nostr
- Zalo
- Nextcloud Talk
- Synology Chat
- Twitch

**模型提供商**：
- Anthropic
- OpenAI
- Google
- MiniMax
- OpenRouter
- 本地模型（LM Studio）

---

## 8. 重点和难点标注

### ⭐ 重点内容

#### 核心概念
- **三层架构**：Gateway（控制平面）→ Agent（任务执行）→ Node（设备）
- **会话管理**：持久化存储、压缩、修剪
- **多代理路由**：按渠道/账户/任务分离代理

#### 安全要点
- **身份验证优先**：`dmPolicy`, `groupPolicy`
- **文件权限**：`~/.openclaw` 应该是 700，配置文件 600
- **网络暴露**：默认 loopback，使用 Tailscale
- **提示词注入**：将未信任内容视为不信任

#### 工具安全
- **最小权限原则**：使用 `profile: "minimal"` 或 `"messaging"`
- **沙箱隔离**：启用沙箱模式运行敏感任务
- **执行控制**：`exec security: "deny"` 或 `"ask: always"`

### 🔥 难点内容

#### 1. 权限模型复杂性
- 全局 vs 代理级 vs 会话级配置
- DM 和群组访问控制
- 跨渠道的权限一致性

#### 2. 会话管理
- 会话压缩的时机和策略
- 上下文修剪的平衡（保留重要信息 vs 节省 token）
- 线程绑定的配置和调试

#### 3. 安全审计
- 理解 `openclaw security audit` 的警告级别
- 修复安全问题而不破坏功能
- 平衡安全性和可用性

#### 4. 跨平台支持
- 不同渠道的配置差异
- macOS 特定工具在 Linux 上的代理
- WSL2 中的 Windows 编码问题

#### 5. 性能优化
- 模型选择的成本/性能权衡
- 会话压缩对性能的影响
- 大规模部署的资源规划

---

## 9. 汇报可能遇到的问题

### Q1: OpenClaw 和 Claude Code 有什么区别？

**答**：
- **OpenClaw**：个人助手和协调层，有持久记忆、多平台访问、工具编排、持续运行的网关、节点支持
- **Claude Code**：IDE 中的直接编码循环，更快但无持久记忆

**使用场景**：
- 需要持久记忆、跨设备访问 → OpenClaw
- 快速编码循环 → Claude Code

### Q2: OpenClaw 安全吗？

**答**：
- **设计原则**：身份验证优先、范围其次、模型最后
- **安全措施**：
  - DM 访问控制（配对/白名单）
  - 文件权限保护
  - 网络暴露限制
  - 工具权限控制
  - 安全审计工具
- **警告**：没有"完全安全"的设置，关键是明确谁可以访问、可以做什么

### Q3: 如何在 VPS 上部署 OpenClaw？

**答**：
1. 在 VPS 上安装 OpenClaw
2. 运行 `openclaw onboard`
3. 配置模型认证
4. 配置至少一个渠道
5. 使用 Tailscale 或 SSH 隧道访问
6. 保持网关运行（systemd 或类似）

**资源要求**：
- 最低：1 vCPU, 1GB RAM
- 推荐：1-2 vCPU, 2GB RAM

### Q4: 如何处理提示词注入攻击？

**答**：
1. **锁定 DM 访问**：使用 `pairing` 或 `allowlist`
2. **提及门控**：在群组中要求提及
3. **工具限制**：只给可信代理高权限工具
4. **沙箱执行**：在沙箱中运行敏感任务
5. **模型选择**：使用强大的最新模型
6. **定期审计**：运行 `openclaw security audit`

### Q5: 会话压缩和修剪有什么区别？

**答**：
- **会话压缩**：将长历史总结成更短的表示，减少 token 使用
- **上下文修剪**：删除旧的工具结果，保留重要信息

**压缩**：在会话很长时自动触发
**修剪**：定期清理旧的工具输出

### Q6: 如何配置多代理路由？

**答**：
```json
{
  "agents": {
    "list": [
      {
        "id": "fast-chat",
        "model": "openai/gpt-4.1-mini",
        "tools": { "profile": "messaging" }
      },
      {
        "id": "coding",
        "model": "anthropic/claude-opus-4-6",
        "tools": { "profile": "elevated" }
      }
    ]
  },
  "channels": {
    "telegram": {
      "dm": {
        "allowFrom": ["tg:123456789"],
        "agentId": "fast-chat"
      },
      "groups": {
        "G987654321": {
          "agentId": "coding"
        }
      }
    }
  }
}
```

### Q7: 节点的作用是什么？

**答**：
- 连接到网关的本地设备
- 提供额外功能：屏幕、摄像头、Canvas、系统执行
- 网关可以运行在云端，节点在本地设备

**使用场景**：
- 访问本地浏览器
- 运行本地命令
- 使用摄像头/屏幕
- macOS 特定工具

### Q8: 如何备份 OpenClaw 数据？

**答**：
1. **状态目录**：`~/.openclaw`（包含会话历史、认证）
2. **工作空间**：`~/.openclaw/workspace`（包含记忆、配置）

**迁移到新机器**：
```bash
# 复制状态目录
scp -r ~/.openclaw user@newhost:~/.openclaw

# 复制工作空间
scp -r ~/.openclaw/workspace user@newhost:~/.openclaw/workspace

# 在新机器上运行 Doctor
openclaw doctor
openclaw gateway restart
```

**注意**：只备份工作空间到 GitHub 会丢失会话历史和认证信息！

### Q9: OpenClaw 支持哪些模型？

**答**：
- **Anthropic**：Claude 系列（Opus, Sonnet, Haiku）
- **OpenAI**：GPT-4.1 系列
- **Google**：Gemini 系列
- **MiniMax**：MiniMax-M2 系列
- **OpenRouter**：多种模型
- **本地模型**：通过 LM Studio 等

**配置方式**：
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": ["minimax/MiniMax-M2.7"]
      }
    }
  }
}
```

### Q10: 如何调试 OpenClaw 问题？

**答**：
**快速检查**：
```bash
openclaw status
openclaw models status
openclaw doctor
```

**深度调试**：
```bash
openclaw status --all
openclaw status --deep
openclaw logs --follow
openclaw health --verbose
```

**常见故障**：
1. 网关未运行：`openclaw gateway status`, `openclaw gateway restart`
2. 模型认证问题：`openclaw models status`
3. 渠道问题：检查 `openclaw logs --follow`

---

## 📚 参考资料

- **官方文档**：https://docs.openclaw.ai
- **GitHub 仓库**：https://github.com/openclaw/openclaw
- **技能市场**：https://clawhub.com
- **安装指南**：https://openclaw.ai/install.sh
- **快速开始**：https://docs.openclaw.ai/start/getting-started

---

**报告生成时间**：2026-03-26 23:44  
**学习代理**：御坂妹妹 16 号（web-crawler）  
**状态**：✅ 知识学习任务完成
