# OpenClaw 学习笔记

> 🦞 *"EXFOLIATE! EXFOLIATE!"* — A space lobster, probably
> 
> 学习日期：2026-03-17
> 学习目标：为明早七点汇报做准备
> 学习方式：只学习不实践，系统性知识梳理

---

## 📚 一、OpenClaw 核心概念与定位

### 1.1 什么是 OpenClaw？

**一句话定义**：OpenClaw 是一个**自托管网关（self-hosted gateway）**，连接你最喜欢的聊天应用（WhatsApp、Telegram、Discord、iMessage 等）与 AI 编码代理（如 Pi）。

**核心特征**：
- 🏠 **自托管**：运行在你自己的机器上，你的规则
- 🌐 **多通道**：单个 Gateway 同时服务多个聊天平台
- 🤖 **Agent 原生**：内置工具使用、sessions、memory、多代理路由
- 📄 **开源**：MIT 许可证，社区驱动

**目标用户**：
- 希望拥有个人 AI 助手的开发者和高级用户
- 想要从任何地方发消息给 AI 助手，同时不交出数据控制权的人

**需求**：
- Node 24（推荐）或 Node 22 LTS（22.16+）
- 选择的服务提供商 API key
- 5 分钟时间

### 1.2 核心架构概览

```
Chat apps + plugins
        ↓
   Gateway (核心中枢)
   /    |    |    \
 Pi  agent  CLI  Web Control UI  macOS app  iOS/Android nodes
```

**Gateway 是单一事实来源**，负责：
- sessions 管理
- 路由分发
- 通道连接

---

## 🏗️ 二、核心架构与组件

### 2.1 Gateway（守护进程）

**核心职责**：
- 维护 provider 连接
- 暴露 typed WebSocket API（请求、响应、服务器推送事件）
- 验证传入帧（JSON Schema）
- 发射事件：`agent`、`chat`、`presence`、`health`、`heartbeat`、`cron`

**连接生命周期**：
```
Client → Gateway: req:connect
Gateway → Client: res (ok) 或 res error + close
        → event:presence
        → event:tick
Client → Gateway: req:agent
Gateway → Client: res:agent (ack → streaming → final)
```

**通信协议**：
- 传输：WebSocket，文本帧 + JSON 负载
- 首帧必须是 `connect`
- 握手后：
  - 请求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
  - 事件：`{type:"event", event, payload, seq?, stateVersion?}`
- 认证：`OPENCLAW_GATEWAY_TOKEN` 或 `--token`
- 幂等键：对 `send`、`agent` 等副作用操作必需

### 2.2 Clients（客户端）

包括：
- macOS app
- CLI
- Web admin

**特征**：
- 每个客户端一条 WS 连接
- 发送请求：`health`、`status`、`send`、`agent`、`system-presence`
- 订阅事件：`tick`、`agent`、`presence`、`shutdown`

### 2.3 Nodes（节点）

**定义**：伴随设备（macOS/iOS/Android/headless），通过 WebSocket 连接到 Gateway，`role: "node"`

**功能**：
- 暴露设备命令：`canvas.*`、`camera.*`、`screen.record`、`location.get`、`notifications.*`、`system.*`
- 通过 `node.invoke` 调用
- 配对基于**设备身份**，approval 存储在设备配对 store

**节点类型**：
- macOS 节点（menubar app 模式）
- Android 节点（完整设备控制）
- iOS 节点
- Headless 节点主机（无 UI，纯执行）

**核心用途**：
- Canvas 展示和交互
- 相机/屏幕录制
- 设备命令执行（系统命令、通知、短信等）

---

## 🔧 三、主要功能模块

### 3.1 Channels（通道）

**支持的原生通道**：
- ✅ **WhatsApp**（Baileys）
- ✅ **Telegram**（grammY）
- ✅ **Discord**（channels.discord.js）
- ✅ **iMessage**（imsg CLI，macOS 本地）
- ✅ **Mattermost**（插件）
- ✅ Signal、Slack、IRC、LINE、Matrix、Microsoft Teams 等

**通道管理**：
- 多账户支持：每个 channel 可以配置多个 `accountId`
- 路由绑定（bindings）：将特定通道/群组/用户路由到不同 agent
- 提及激活：群组聊天支持 `@mention` 激活
- 媒体支持：图片、音频、文档收发

**安全控制**：
- DM 策略：`pairing`、`allowlist`、`denylist`、`open`
- 群组政策：`groupPolicy` 控制群组加入方式
- 提及规则：`requireMention` 确保 agent 不被误触发

### 3.2 Sessions（会话管理）

**核心理念**：
- 每个 agent 一个直接聊天会话（direct-chat session）
- 直接聊天折叠为 `agent:<agentId>:<mainKey>`
- 群组/频道聊天独立会话

**会话键命名规则**：
- 直接聊天（DM）：
  - `main`（默认）：`agent:<agentId>:<mainKey>`（跨设备/通道连续性）
  - `per-peer`：`agent:<agentId>:direct:<peerId>`
  - `per-channel-peer`：`agent:<agentId>:<channel>:direct:<peerId>`
  - `per-account-channel-peer`：`agent:<agentId>:<channel>:<accountId>:direct:<peerId>`
- 群组：`agent:<agentId>:<channel>:group:<id>`
- 频道：`agent:<agentId>:<channel>:channel:<id>`
- Telegram 主题：`...:topic:<threadId>`

**状态存储**：
- Store 文件：`~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transcripts：`~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`
- **Gateway 是真理来源**：UI 客户端必须查询 Gateway 获取 session 列表

**安全 DM 模式（强烈推荐）**：
```json5
{
  session: {
    // 安全 DM 模式：每个用户隔离 DM 上下文
    dmScope: "per-channel-peer",
  },
}
```
**为什么需要**：如果 agent 接收多用户 DM，默认设置会让所有用户共享同一对话上下文，可能泄露隐私信息。

**维护策略**：
- 自动清理：`pruneAfter: "30d"`（默认 30 天前删除）
- 条目限制：`maxEntries: 500`（默认最多 500 个）
- 磁盘限制：`maxDiskBytes`（可选，控制会话目录最大占用）
- 旋转：`rotateBytes: "10mb"`（超过自动旋转）

**命令控制**：
- `/new` - 开始新会话
- `/reset` - 重置会话
- `/status` - 查看会话状态
- `/context` - 查看系统提示和注入文件
- `/stop` - 中止当前运行
- `/compact` - 压缩上下文释放空间

### 3.3 Agents（代理）

**什么是 Agent**：
- 完全隔离的大脑，拥有独立的：
  - **Workspace**（文件、AGENTS.md/SOUL.md/USER.md、本地规则）
  - **State directory**（`agentDir`，存储 auth 配置、模型注册表）
  - **Session store**（聊天历史、路由状态）

**Agent 配置路径**：
```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json  # 认证配置
~/.openclaw/agents/<agentId>/sessions/                 # 会话存储
<workspace>/skills/                                    # 技能
<workspace>/AGENTS.md, SOUL.md, USER.md                # 人格配置
```

**多 Agent 路由**：
- 每个 agentId 是一个**完全隔离的人格**
- 可以绑定不同电话号码/账户
- 不同人格（不同的 AGENTS.md/SOUL.md）
- 独立认证 + 会话（默认不跨 agent 交流）

**绑定规则（bindings）优先级**（最具体胜出）：
1. `peer` 匹配（精确 DM/群组/频道 ID）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. `accountId` 匹配（通道账户）
7. 通道级匹配（`accountId: "*"`)
8. fallback 到默认 agent（第一个，默认 `main`）

**添加 Agent**：
```bash
openclaw agents add <agentId>
openclaw agents list --bindings  # 验证绑定
```

### 3.4 Tools（工具系统）

**核心工具**（总是可用，受工具策略控制）：
- `read` - 读取文件
- `write` - 创建/覆盖文件
- `edit` - 精确编辑文件
- `exec` - 执行 shell 命令
- `browser` - 浏览器控制
- `message` - 消息发送
- `web_search` - 网络搜索
- `web_fetch` - 网页抓取

**工具策略**：
- 全局控制：`tools.exec.host`、`tools.exec.security`
- 安全模式：`sandbox`、`allowlist`、`full`
- 提升模式：`tools.elevated`（基于发送者）

**Node 绑定**：
```bash
openclaw config set tools.exec.host node
openclaw config set tools.exec.security allowlist
openclaw config set tools.exec.node <node-id>
```

**Skills**：
- 加载位置：bundled / `~/.openclaw/skills` / `<workspace>/skills`
- Workspace 优先（名称冲突时）
- 可以配置/环境变量控制启用

---

## 📖 四、文档结构和资源

### 4.1 文档结构

**核心文档章节**：
1. **start** - 入门指南
   - getting-started.md
   - setup.md
   - wizard.md
   - onboarding.md

2. **concepts** - 核心概念
   - architecture.md - 架构
   - agent.md - 代理运行时
   - session.md - 会话管理
   - multi-agent.md - 多代理路由
   - memory.md - 记忆
   - context.md - 上下文
   - features.md - 功能列表

3. **gateway** - Gateway 配置
   - configuration.md - 配置
   - security.md - 安全
   - protocol.md - 协议
   - remote.md - 远程访问
   - troubleshooting.md - 故障排除

4. **channels** - 通道
   - whatsapp.md
   - telegram.md
   - discord.md
   - 每个通道独立的设置文档

5. **nodes** - 节点
   - index.md - 节点总览
   - camera.md - 相机
   - canvas.md - Canvas
   - talk.md - 语音模式

6. **tools** - 工具
   - index.md - 工具总览
   - skills.md - 技能
   - browser.md - 浏览器
   - exec.md - 执行
   - subagents.md - 子代理

7. **providers** - 模型提供商
   - openai.md
   - anthropic.md
   - vllm.md
   - ollama.md
   - 等数十个提供商

8. **install** - 安装
   - node.md
   - docker.md
   - kubernetes.md
   - 各平台特定安装

9. **web** - Web 界面
   - control-ui.md
   - dashboard.md
   - webchat.md

### 4.2 主要资源链接

| 资源 | 链接 | 说明 |
|------|------|------|
| 官网文档 | https://docs.openclaw.ai | 完整文档 |
| 文档索引 | https://docs.openclaw.ai/llms.txt | 所有页面列表 |
| GitHub | https://github.com/openclaw/openclaw | 源代码仓库 |
| ClawHub | https://clawhub.ai | 技能市场 |
| Discord | https://discord.com/invite/clawd | 社区 |

### 4.3 配置文件

**主配置**：`~/.openclaw/openclaw.json`（JSON5 格式）

**核心配置项**：
```json5
{
  // Gateway 配置
  gateway: {
    port: 18789,
    bind: "loopback",  // 或 "all"
    auth: {
      token: "your-token"
    }
  },
  
  // 通道配置
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      dmPolicy: "pairing",  // pairing | allowlist | denylist | open
      groups: { "*": { requireMention: true } }
    },
    telegram: {
      dmPolicy: "pairing"
    }
  },
  
  // Session 配置
  session: {
    dmScope: "per-channel-peer",  // 安全 DM 模式
    reset: {
      mode: "daily",
      atHour: 4  // 每天凌晨 4 点重置
    },
    maintenance: {
      mode: "enforce",
      pruneAfter: "30d",
      maxEntries: 500
    }
  },
  
  // Agents 配置
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: "anthropic/claude-3-5-sonnet-latest"
    },
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "work", workspace: "~/.openclaw/workspace-work" }
    ]
  },
  
  // 绑定（路由）
  bindings: [
    {
      agentId: "main",
      match: { channel: "whatsapp" }
    }
  ]
}
```

---

## 🚀 五、使用案例与最佳实践

### 5.1 典型使用场景

#### 场景 1：个人 AI 助手
- 一个 agent（`main`）
- 单一 WhatsApp/Telegram 账户
- DM 共享会话（`dmScope: "main"`）
- 用于日常聊天、信息查询、任务提醒

#### 场景 2：工作/个人分离
```json5
{
  agents: {
    list: [
      { id: "work", workspace: "~/.openclaw/workspace-work" },
      { id: "personal", workspace: "~/.openclaw/workspace-personal" }
    ]
  },
  bindings: [
    { agentId: "work", match: { channel: "whatsapp", accountId: "work" } },
    { agentId: "personal", match: { channel: "whatsapp", accountId: "personal" } }
  ]
}
```
- 工作账户和个人账户分开
- 不同的 workspace 文件（SOUL.md、AGENTS.md 等）
- 隔离的会话和认证

#### 场景 3：多用户共享服务器
```json5
{
  agents: {
    list: [
      { id: "alice", workspace: "~/.openclaw/workspace-alice" },
      { id: "bob", workspace: "~/.openclaw/workspace-bob" }
    ]
  },
  bindings: [
    {
      agentId: "alice",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230001" } }
    },
    {
      agentId: "bob",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230002" } }
    }
  ],
  session: {
    dmScope: "per-channel-peer"  // 安全 DM 模式
  }
}
```
- 多用户共享一台服务器
- 每个用户独立人格
- 会话完全隔离
- 隐私保护

#### 场景 4：不同平台不同模型
```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "日常聊天",
        model: "anthropic/claude-3-5-haiku"
      },
      {
        id: "deep-work",
        name: "深度工作",
        model: "anthropic/claude-3-5-opus"
      }
    ]
  },
  bindings: [
    { agentId: "chat", match: { channel: "whatsapp" } },
    { agentId: "deep-work", match: { channel: "telegram" } }
  ]
}
```
- WhatsApp 用快速便宜的模型
- Telegram 用强大昂贵的模型
- 根据使用场景智能分配

### 5.2 最佳实践

#### 安全性
1. **启用安全 DM 模式**：`session.dmScope: "per-channel-peer"`
2. **使用 Token 认证**：`OPENCLAW_GATEWAY_TOKEN`
3. **限制 allowFrom**：只允许信任的用户
4. **开启提及规则**：`requireMention: true`（群组）
5. **定期清理**：启用 maintenance mode
6. **沙箱模式**：对不信任的 agent 启用 `sandbox: { mode: "all" }`

#### 性能优化
1. **会话限制**：设置 `maxEntries: 500` 和 `pruneAfter: "30d"`
2. **磁盘预算**：`maxDiskBytes` 防止无限增长
3. **定期压缩**：`/compact` 释放上下文空间
4. **Node 主机**：将执行任务分散到 node host

#### 可用性
1. **远程访问**：使用 Tailscale 或 SSH 隧道
2. **多通道**：一个 Gateway 服务多个平台
3. **自动重启**：使用 launchd/systemd 托管
4. **健康检查**：定期运行 `openclaw health`

#### 开发工作流
1. **本地优先**：先在本地开发
2. **技能系统**：将常用功能封装为技能
3. **版本控制**：将 workspace 文件加入 Git
4. **备份**：定期备份 `~/.openclaw/`

---

## 🔮 六、未来发展方向

### 6.1 当前状态

**已实现的核心功能**：
- ✅ 多通道网关
- ✅ 多 Agent 路由
- ✅ Node 支持（macOS/iOS/Android）
- ✅ Canvas 交互
- ✅ 媒体支持
- ✅ Web Control UI
- ✅ 会话管理
- ✅ 工具系统
- ✅ Skills 生态系统

**正在发展的方向**：
- 更多通道支持（IRC、Matrix、Slack 等已实现，继续扩展）
- 更好的移动节点功能
- 增强的媒体理解
- 语音呼叫集成
- 更多模型提供商支持

### 6.2 实验性功能

从文档可以看到一些实验性计划：
- **ACP Thread Bound Agents** - 线程绑定代理
- **Unified Runtime Streaming Refactor** - 统一运行时流重构
- **Browser Evaluate CDP Refactor** - 浏览器 CDP 重构
- **OpenResponses Gateway** - OpenResponses API
- **PTY and Process Supervision** - PTY 和进程监管

### 6.3 社区驱动

**ClawHub 生态系统**：
- 上传和版本化 AgentSkills 包
- 向量搜索使其可查找
- 无 gatekeeping，只关注信号质量
- 版本化、可回滚

**开源社区**：
- MIT 许可
- 社区驱动开发
- 插件系统扩展功能
- 技能市场

---

## 📝 七、核心知识点总结

### 7.1 必背概念

1. **Gateway**：单一事实来源，管理所有连接
2. **Channels**：支持 WhatsApp、Telegram、Discord 等
3. **Sessions**：每个 agent 一个会话 store，JSONL 格式
4. **Agents**：完全隔离的"大脑"，独立 workspace
5. **Nodes**：设备伴侣，提供 canvas/camera 等命令
6. **Bindings**：路由规则，最具体胜出
7. **Tools**：read/write/exec/browser 等
8. **Skills**：功能包，类似 npm 包
9. **Security**：DM scope、allowlist、token 认证
10. **Maintenance**：自动清理、磁盘预算

### 7.2 关键命令速查

```bash
# 安装和设置
npm install -g openclaw@latest
openclaw onboard --install-daemon
openclaw setup

# Gateway 管理
openclaw gateway --port 18789
openclaw gateway restart
openclaw gateway status

# Agent 管理
openclaw agents add <agentId>
openclaw agents list
openclaw agents list --bindings

# Session 管理
openclaw sessions list
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce

# Node 管理
openclaw nodes status
openclaw nodes describe --node <id>
openclaw nodes canvas snapshot --node <id>
openclaw nodes camera snap --node <id>
openclaw nodes screen record --node <id>

# 通道管理
openclaw channels login --channel whatsapp
openclaw channels status --probe

# 配置
openclaw config set <path> <value>
openclaw config get <path>
openclaw config unset <path>

# 安全
openclaw security audit
openclaw approvals allowlist add <command>

# 诊断
openclaw doctor
openclaw health
openclaw logs
```

### 7.3 文件结构速览

```
~/.openclaw/
├── openclaw.json              # 主配置
├── agents/
│   └── <agentId>/
│       ├── agent/
│       │   └── auth-profiles.json  # 认证配置
│       └── sessions/
│           ├── sessions.json     # 会话 store
│           └── <sessionId>.jsonl # 会话 transcript
├── credentials/
│   └── <channel>/<accountId>/    # 通道认证
├── skills/                        # 全局技能
├── workspace/                     # 主工作区
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── TOOLS.md
│   ├── USER.md
│   └── skills/
└── node.json                      # Node 配置

# 或
~/.openclaw/agents/main/workspace/   # 主 agent 工作区
```

---

## 🎯 八、学习要点回顾

### 8.1 OpenClaw 是什么？

OpenClaw 是一个**自托管的聊天代理网关**，让你可以：
- 从任何聊天应用（WhatsApp、Telegram 等）发送消息给 AI
- 完全控制数据和隐私
- 运行多个独立代理，每个有自己的人格和记忆
- 连接物理设备（手机、Mac）作为扩展能力

### 8.2 核心价值主张

1. **隐私优先**：数据留在你的机器上
2. **灵活性**：多通道、多 agent、可定制
3. **开源透明**：MIT 许可，社区驱动
4. **强大功能**：不仅仅是聊天，还有代码执行、设备控制

### 8.3 学习建议

1. **先理解核心概念**：Gateway、Channel、Session、Agent
2. **从简单开始**：单 agent + 单通道，然后逐步扩展
3. **阅读配置文档**：`configuration.md` 是必读
4. **理解安全模型**：DM scope、bindings、auth
5. **实践但不急于求成**：先学习，再动手

---

## 📚 学习完成

> 🦞 本次学习已完成所有规划内容的阅读：
> - ✅ OpenClaw 核心概念和架构
> - ✅ 主要功能模块（Gateway、sessions、agents、tools、nodes）
> - ✅ 文档结构和资源
> - ✅ 使用案例和最佳实践
> - ✅ 未来发展方向

**下一步**：等待明早七点汇报，准备回答御坂大人的问题！

**备注**：学习过程中未进行任何实际操作，仅通过网络抓取和阅读官方文档。所有信息均来自 OpenClaw 官方文档（docs.openclaw.ai）和 ClawHub 网站。

---

*学习日期：2026-03-17 21:40 GMT+8*  
*学习代理：御坂妹妹 16 号（web-crawler）*  
*汇报时间：2026-03-18 07:00 GMT+8*
