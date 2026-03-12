# OpenClaw 知识学习笔记

## 📚 基础信息

### 1. 什么是 OpenClaw

OpenClaw 是一个**智能体网关平台**，用于：
- 将 AI 智能体连接到各种消息渠道（WhatsApp, Telegram, Discord 等）
- 实现多智能体路由和隔离
- 提供统一的网关服务管理智能体、会话和工具

**核心理念**：
- **Gateway (网关)**: 唯一的控制平面，管理所有消息渠道
- **Agent (智能体)**: 具有独立工作空间和记忆的"大脑"
- **Session (会话)**: 聊天历史的存储和管理
- **Skill (技能)**: 可扩展的工具集

---

## 🏗️ 架构设计

### 2.1 核心组件

```
┌─────────────────────────────────────────────────────┐
│                   Gateway Daemon                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Channels  │  │  Agents     │  │   Tools     │ │
│  │ (WhatsApp,  │  │ (Isolated   │  │ (Skills,    │ │
│  │  Telegram,  │  │  Workspaces)│  │  Plugins)   │ │
│  │  Discord)   │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
         │                   │                   │
    WebSocket          WebSocket          WebSocket
         │                   │                   │
┌────────┴─────┐    ┌───────┴────────┐   ┌──────┴────────┐
│   Clients    │    │      Nodes     │   │   Channels    │
│ (CLI, macOS, │    │ (iOS, Android, │   │ (Providers)   │
│  WebUI)      │    │  Headless)     │   │               │
└──────────────┘    └────────────────┘   └───────────────┘
```

### 2.2 Gateway 架构

**主要特性**:
- **单一网关**: 每主机一个 Gateway，管理所有消息渠道
- **WebSocket API**: 客户端和节点通过 WebSocket 连接
- **角色分离**: 
  - 客户端 (CLI, macOS app, WebUI) - 控制平面
  - Nodes (移动设备/无头服务) - 执行平面
  - Gateway - 路由和控制

**连接生命周期**:
```
1. Client → Gateway: req:connect (携带认证令牌)
2. Gateway → Client: res:ok (返回 hello-ok 快照)
3. Gateway → Client: event:presence (推送状态更新)
4. Client → Gateway: req:agent (发送消息/任务)
5. Gateway → Client: event:agent (流式返回结果)
```

**安全机制**:
- 所有连接必须携带 device identity
- 新设备需要配对批准 (pairing approval)
- 本地连接 (loopback) 可自动批准
- 所有连接必须签署 `connect.challenge` nonce

---

## 🔧 多智能体系统

### 3.1 什么是"Agent"

一个 Agent 是拥有独立上下文的完整智能体：
- **Workspace**: 工作空间（包含 `AGENTS.md`, `SOUL.md`, `USER.md`）
- **State Directory**: 状态目录（认证配置、模型注册）
- **Session Store**: 会话存储（聊天历史、路由状态）

**路径结构**:
```
~/.openclaw/
├── openclaw.json          # 主配置文件
├── agents/
│   └── <agentId>/
│       ├── agent/         # Agent 状态目录
│       │   └── auth-profiles.json
│       └── sessions/      # 会话存储
│           └── sessions.json
└── workspace/             # 默认工作空间
```

### 3.2 路由机制 (Bindings)

Bindings 是确定性的路由规则，遵循 **最具体优先** 原则：

1. `peer` 匹配（精确 DM/群组 ID）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord 服务器）
5. `teamId`（Slack 团队）
6. `accountId` 匹配
7. 渠道级匹配 (`accountId: "*"`)
8. 回退到默认智能体

**示例配置**:
```json5
{
  agents: {
    list: [
      { id: "personal", workspace: "~/.openclaw/workspace-personal" },
      { id: "work", workspace: "~/.openclaw/workspace-work" }
    ]
  },
  bindings: [
    { agentId: "personal", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "work" } }
  ]
}
```

### 3.3 多账户模式

支持多账户渠道（如 WhatsApp）：
- 每个 `accountId` 可路由到不同 Agent
- 使用 `accountId` 标识每个登录
- 支持 `accountId: "*"` 作为渠道级回退

**配置多账号**:
```bash
# 登录不同账号
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account work
```

---

## 💬 会话管理

### 4.1 会话结构

**会话 Key 格式**:
- 直接聊天：`agent:<agentId>:<mainKey>` (默认)
- 隔离模式：`agent:<agentId>:dm:<peerId>`
- 群组：`agent:<agentId>:<channel>:group:<id>`
- 线程：`agent:<agentId>:<channel>:topic:<threadId>`

**会话状态**:
- **Store**: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- **Transcripts**: `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

### 4.2 DM 作用域 (dmScope)

控制直接消息如何分组：

| 模式 | 效果 | 适用场景 |
|------|------|----------|
| `main` | 所有 DM 共享主会话 | 单用户场景 |
| `per-peer` | 按发件人 ID 隔离 | 多用户 DM |
| `per-channel-peer` | 按渠道 + 发件人隔离 | 共享收件箱 |
| `per-account-channel-peer` | 按账号 + 渠道 + 发件人隔离 | 多账号场景 |

**安全模式推荐**:
```json5
{
  session: {
    dmScope: "per-channel-peer"  // 推荐用于多用户设置
  }
}
```

### 4.3 会话维护

**默认配置**:
- `pruneAfter`: 30 天
- `maxEntries`: 500
- `rotateBytes`: 10MB
- `maintenance.mode`: "warn"

**维护命令**:
```bash
# 查看清理计划
openclaw sessions cleanup --dry-run

# 强制清理
openclaw sessions cleanup --enforce
```

---

## 🧰 技能系统 (Skills)

### 5.1 技能概述

Skills 是 Teach 智能体如何使用工具的文件夹，每个技能包含：
- `SKILL.md`: 包含 YAML frontmatter 和指令
- 可选脚本/资源文件

**位置优先级** (从高到低):
1. `<workspace>/skills` (最高)
2. `~/.openclaw/skills` (管理/本地)
3. Bundled skills (最低)

### 5.2 技能格式

**基础 SKILL.md 格式**:
```markdown
---
name: nano-banana-pro
description: Generate or edit images via Gemini 3 Pro Image
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
      "primaryEnv": "GEMINI_API_KEY"
    }
  }
---

# 技能说明
...
```

** gating 条件**:
- `requires.bins`: 必须存在的二进制文件
- `requires.env`: 必须存在的环境变量
- `requires.config`: 必须在配置中为真
- `os`: 支持的操作系统列表

### 5.3 ClawHub

ClawHub 是 OpenClaw 的公共技能注册表：
- 网站：https://clawhub.com
- 安装：`clawhub install <skill-slug>`
- 更新：`clawhub update --all`
- 同步：`clawhub sync --all`

---

## 🔒 安全模型

### 6.1 信任边界

**核心原则**:
- **个人助手模式**: 一个受信任的操作者边界，可能多个智能体
- **不支持**: 多租户/敌对用户共享单一网关
- **解决方案**: 为每个信任边界运行独立的网关

**安全矩阵**:

| 边界或控制 | 含义 | 常见误解 |
|-----------|------|---------|
| `gateway.auth` | 认证调用者 | "需要每帧签名" ❌ |
| `sessionKey` | 路由选择器 | "是用户认证边界" ❌ |
| Prompt 防护 | 减少模型滥用 | "仅靠 prompt 防护就安全" ❌ |
| Node 配对 | 远程执行 | "应该被视为未授权访问" ❌ |

### 6.2 安全加固清单

**基础安全配置**:
```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "替换为长随机令牌" }
  },
  session: {
    dmScope: "per-channel-peer"  // 多用户场景
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs"]
  },
  channels: {
    whatsapp: { dmPolicy: "pairing" }
  }
}
```

**安全审计**:
```bash
# 常规审计
openclaw security audit

# 深度审计
openclaw security audit --deep

# 自动修复
openclaw security audit --fix

# JSON 格式输出
openclaw security audit --json
```

### 6.3 常见安全问题

**高优先级问题**:
1. `fs.state_dir.perms_world_writable` - 其他用户可修改完整状态
2. `gateway.bind_no_auth` - 远程绑定无认证
3. `gateway.tailscale_funnel` - 公网暴露
4. `security.exposure.open_groups_with_elevated` - 开放群组 + 高级工具

**修复建议**:
- 权限：`~/.openclaw` 设置为 `700`, `openclaw.json` 设置为 `600`
- 网络：绑定到 `loopback` 或 Tailscale
- 认证：始终使用 token 或密码
- DM 策略：使用 `pairing` 或 `allowlist`

---

## 📖 最佳实践

### 7.1 部署建议

**单机/个人使用**:
- 绑定到 `loopback` (默认)
- 启用 token 认证
- 使用 `dmScope: "per-channel-peer"`
- 定期运行 `openclaw security audit`

**多用户场景**:
- 运行独立网关 per trust boundary
- 启用严格 DM 隔离
- 限制工具权限
- 使用沙箱模式

**公开机器人**:
- 使用专用机器/VM/容器
- 限制工具访问（只读或禁用）
- 启用沙箱
- 使用强模型（防提示注入）

### 7.2 技能管理

**最佳实践**:
- 将第三方技能视为不可信代码
- 启用技能监听器自动刷新
- 定期更新技能
- 阅读技能内容后再启用

**沙箱兼容性**:
- 确保沙箱内包含所需二进制文件
- 使用 `agents.defaults.sandbox.docker.setupCommand` 安装依赖

### 7.3 会话维护

**定期维护**:
```bash
# 查看会话状态
openclaw status

# 查看会话列表
openclaw sessions --json

# 清理过期会话
openclaw sessions cleanup --dry-run
```

**配置优化**:
```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "45d",
      maxEntries: 800
    }
  }
}
```

---

## 🎯 工具使用

### 8.1 CLI 命令分类

**网关管理**:
- `openclaw gateway status/start/stop/restart`
- `openclaw gateway --port <port>` - 前台运行
- `openclaw health` - 检查健康状态

**智能体管理**:
- `openclaw agents list` - 列出智能体
- `openclaw agents add <agentId>` - 添加智能体
- `openclaw agents list --bindings` - 查看路由规则

**渠道管理**:
- `openclaw channels login --channel <channel>` - 登录渠道
- `openclaw channels status` - 检查渠道状态
- `openclaw pairing approve` - 批准配对

**会话管理**:
- `openclaw sessions list` - 列出会话
- `openclaw sessions cleanup` - 清理会话
- `/status` - 发送消息查看会话状态

**技能管理**:
- `openclaw skills` - 查看技能
- `clawhub install` - 安装技能
- `clawhub update` - 更新技能

**安全审计**:
- `openclaw security audit` - 安全审计
- `openclaw doctor` - 健康检查和快速修复

### 8.2 快捷命令

**快速启动**:
```bash
# 打开仪表盘
openclaw dashboard

# 前台运行网关
openclaw gateway --port 18789

# 开发模式
openclaw --dev gateway
```

**发送消息**:
```bash
# 发送测试消息
openclaw message send --target +15555550123 --message "Hello"

# 通过特定渠道发送
openclaw message send --channel telegram --target @mychat --message "Hi"
```

---

## 📝 配置详解

### 9.1 主配置结构

**核心配置项**:
```json5
{
  gateway: {
    mode: "local",           // 运行模式
    bind: "loopback",        // 绑定地址
    auth: {                  // 认证配置
      mode: "token",
      token: "..."
    },
    port: 18789,
    remote: {                // 远程客户端配置
      token: "...",
      tlsFingerprint: "..."
    }
  },
  agents: {
    list: [...],             // 智能体列表
    defaults: {              // 默认配置
      sandbox: {
        mode: "off"          // 沙箱模式：off/all/shared
      }
    }
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",   // DM 策略
      groups: {}             // 群组配置
    },
    telegram: {
      accounts: {}           // 多账号配置
    }
  },
  session: {
    dmScope: "per-channel-peer",
    maintenance: {
      mode: "warn",
      pruneAfter: "30d"
    }
  },
  tools: {
    profile: "messaging",
    deny: [...]
  }
}
```

### 9.2 环境变量

**关键环境变量**:
- `OPENCLAW_HOME` - 主目录
- `OPENCLAW_STATE_DIR` - 状态目录
- `OPENCLAW_CONFIG_PATH` - 配置文件路径
- `OPENCLAW_GATEWAY_TOKEN` - 网关令牌
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS` - 允许不安全 WS 连接

---

## 🔄 工作流程

### 10.1 消息处理流程

```
用户消息
   ↓
渠道连接器 (WhatsApp/Telegram 等)
   ↓
Gateway 接收 → 验证认证 → 检查权限
   ↓
查找匹配 Binding → 路由到 Agent
   ↓
查询 Session → 加载上下文
   ↓
生成 System Prompt (包含技能列表)
   ↓
LLM 处理 → 生成响应/调用工具
   ↓
执行工具（受权限控制）
   ↓
返回结果给 LLM
   ↓
生成最终回复
   ↓
保存到 Session
   ↓
通过渠道发送回复
```

### 10.2 技能加载流程

```
Session 启动
   ↓
读取所有技能文件 (SKILL.md)
   ↓
应用 gating 条件过滤
   ↓
生成技能快照 (XML 格式)
   ↓
注入 System Prompt
   ↓
后续 turns 复用快照（热重载可选）
```

---

## 📚 参考资料

**官方文档**:
- https://docs.openclaw.ai
- https://github.com/openclaw/openclaw

**技能仓库**:
- https://clawhub.com

**社区**:
- Discord: https://discord.com/invite/clawd

---

## 🎓 学习总结

OpenClaw 是一个功能强大的智能体网关平台，其核心特点包括：

1. **模块化架构**: Gateway、Agent、Session、Skill 各司其职
2. **多智能体支持**: 每个 Agent 有独立的工作空间和记忆
3. **安全优先**: 严格的权限控制、认证机制和沙箱支持
4. **可扩展性**: Skills 系统允许无限扩展工具能力
5. **跨平台**: 支持多种消息渠道和移动设备集成

**关键概念**:
- Gateway 是单一控制平面
- Agent 是独立的"大脑"，拥有独立上下文
- Session 是聊天历史的存储
- Skill 是工具能力的定义
- Binding 是路由规则
- Sandbox 是安全隔离机制

**学习要点**:
- 理解信任边界模型
- 掌握路由配置方法
- 熟悉安全加固实践
- 了解技能开发流程
- 掌握会话管理技巧

---

*学习笔记整理时间：2026-03-12*
