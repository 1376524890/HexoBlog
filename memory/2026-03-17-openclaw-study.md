# OpenClaw 知识学习总结
> 为 2026-03-17 07:00 汇报做准备
> 学习完成时间：2026-03-17 09:24 (Asia/Shanghai)

---

## 📌 什么是 OpenClaw？

**核心定义**：OpenClaw 是一个**个人 AI 助手运行时平台**（Personal AI Assistant Runtime Platform）。

**通俗理解**：它不是简单的"聊天机器人"，而是一个**智能网关**（AI Runtime Gateway）——站在用户、AI 模型、工具生态和各类消息平台之间，扮演智能路由中枢的角色。

**一句话**：OpenClaw 让你在任何聊天平台上拥有一个能**做事**的 AI 助手。

---

## 🏗️ 核心架构

### 1. Gateway（网关）—— 中央枢纽

Gateway 是 OpenClaw 的核心守护进程（Daemon），职责包括：

- **生命周期管理**：启动、停止、监控所有 Agent 实例
- **消息路由**：将来自各 Channel 的消息分发到正确的 Session 和 Agent
- **工具协调**：管理 Skill 注册，处理工具调用请求
- **安全控制**：执行沙箱策略，管理权限边界
- **状态持久化**：维护 Session 历史，处理上下文压缩

**关键**：Gateway 本身**不运行 AI 模型**，它只是 AI 模型的"调度员"。

### 2. Agent（智能体）—— AI 执行体

Agent 是实际执行 AI 任务的实例，每个 Agent 有自己的：

- **身份（Identity）**：名称、描述、头像等元信息
- **配置（Config）**：使用的模型、系统提示词、可用工具等
- **状态（State）**：当前会话、历史消息、记忆等
- **运行时（Runtime）**：执行环境（本地进程、Docker、远程等）

Agent 运行在**隔离环境**中，通过**Bridge Protocol**与 Gateway 通信。

### 3. Session（会话）—— 有状态的容器

Session 的核心是**有状态的会话容器**，包含：

- 消息历史
- 上下文窗口（经过压缩处理）
- 工具状态（中间结果）
- 元数据（创建时间、最后活跃时间等）

**上下文管理挑战**：大模型有 token 限制，OpenClaw 通过**Compaction（压缩）**机制解决。

### 4. Channel（通道）—— 消息适配器

Channel 是 OpenClaw 与外部世界连接的**协议适配器**，支持：

| 平台类型 | 支持的平台 |
|---------|-----------|
| 即时通讯 | Telegram、Discord、Slack、WhatsApp、Signal、Feishu（飞书） |
| 传统协议 | IRC、Matrix |
| 企业平台 | Microsoft Teams、Google Chat |
| 其他 | iMessage、BlueBubbles、LINE、Mattermost、Nextcloud Talk、Nostr、Twitch |

---

## 🔄 Agent Loop：AI 如何工作？

```
┌──────────────────────────────────────────────────────────┐
│                      Agent Loop                          │
│                                                          │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│   │ 接收输入 │ → │ 思考决策 │ → │ 执行动作 │             │
│   └─────────┘    └────┬────┘    └────┬────┘             │
│        ↑              │              │                   │
│        │              ↓              ↓                   │
│        │         ┌─────────┐    ┌─────────┐             │
│        │         │ 工具调用 │    │ 直接回复 │             │
│        │         └────┬────┘    └────┬────┘             │
│        │              │              │                   │
│        └──────────────┴──────────────┘                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**流程**：
1. **接收输入**：用户发送消息
2. **构建上下文**：组装 Session 历史、系统提示词、工具列表
3. **LLM 推理**：模型决定是直接回复还是调用工具
4. **工具执行**（需要时）：调用外部工具，获取结果
5. **循环或结束**：多步推理则返回步骤 3
6. **发送响应**：通过原 Channel 回复用户

---

## 🛠️ 核心概念

### System Prompt（系统提示词）

每个 Agent 的"出厂设置"，定义：
- **身份**：你是谁
- **能力**：你能做什么
- **行为规则**：你应该如何回应
- **环境信息**：当前时间、可用资源、安全策略等

OpenClaw 的系统提示词是**动态生成**的，根据实际需要实时调整。

### Skills（技能）

OpenClaw 的工具系统基于 **MCP（Model Context Protocol）** 标准：
- 每个 Skill 是一个独立的包，包含工具定义和实现
- Skill 通过 JSON Schema 描述工具的输入输出
- Gateway 负责 Skill 的注册、发现和调用
- 支持社区发布和共享

**本地技能示例**（已安装的）：
- `blog-writing`：博客写作
- `hexo-blog`：Hexo 博客管理
- `skill-vetter`：技能安全检查
- `task-tracker`：任务追踪
- `weather`：天气预报
- `feishu-doc`：飞书文档操作
- `proactive-agent`：主动代理
- `self-improving-agent`：自我改进代理
- `subagent-network-call`：御坂网络调用

### MCP（Model Context Protocol）

这是 Anthropic 提出的开放标准，**标准化 AI 与外部世界的交互接口**。在 MCP 之前，每个 AI 框架有自己的工具定义方式；MCP 试图统一这一切。

---

## 🤖 多智能体架构（御坂网络第一代）

御坂美琴一号作为核心中枢，调度和监控所有子 Agent（御坂妹妹）：

| 编号 | Agent ID | 职责 | 权限级别 |
|------|----------|------|----------|
| 10 号 | `general-agent` | 通用代理，处理琐碎问题 | Level 2 |
| 11 号 | `code-executor` | 代码执行者 | Level 3 |
| 12 号 | `content-writer` | 内容创作者 | Level 3 |
| 13 号 | `research-analyst` | 研究分析师 | Level 3 |
| 14 号 | `file-manager` | 文件管理器 | Level 2 |
| 15 号 | `system-admin` | 系统管理员 | Level 4 |
| 16 号 | `web-crawler` | 网络爬虫 | Level 2 |
| 17 号 | `memory-organizer` | 记忆整理专家 | Level 3 |

**核心原则**：
- 御坂美琴一号：只做指挥，不做执行
- 御坂妹妹们：只做执行，不做决策
- 分工合作，效率最高

---

## 💾 记忆系统（三层架构）

御坂大人使用的记忆系统参考了 `ClawIntelligentMemory` 项目：

### 第一层：每日日志
```
~/.openclaw/workspace/memory/
└── 2026-03-17.md  <- 今日原始记录
```
- 无限存储，原始内容
- 记录每天做了什么、学到了什么、遇到了什么挑战

### 第二层：精选记忆
```
~/.openclaw/workspace/MEMORY.md  <- 核心记忆（<2500 字符）
```
- 从每日日志提取的精华
- 包含系统配置、重要决策、近期成果
- **每次会话启动时自动加载**

### 第三层：长期归档
```
~/.openclaw/workspace/life/
├── decisions/       <- 决策记录
├── motivation/      <- 成就和连胜
└── archives/        <- 周报和归档
```
- 高价值内容，按需归档
- 决策日志、动机系统、每周总结

**自动化**：每 6 小时从当日日志中提取关键记忆，更新 `MEMORY.md`。

---

## 📦 安装和配置

### 安装（推荐方式）
```bash
npm install -g openclaw@latest
# 或：pnpm add -g openclaw@latest

openclaw onboard --install-daemon
```

### 运行 Gateway
```bash
openclaw gateway --port 18789 --verbose
```

### 基本命令
```bash
# 发送消息
openclaw message send --to +1234567890 --message "Hello"

# 运行单轮 Agent
openclaw agent --message "Ship checklist" --thinking high

# 查看状态
openclaw status

# 启动设置向导
openclaw onboard
```

### 支持的平台
- **macOS**: 有专属菜单栏应用，支持 Canvas、Voice Wake、Talk Mode
- **iOS/Android**: 有 Node 应用，支持相机、屏幕录制、位置、通知等
- **Web**: 有 WebChat 界面

---

## 🔐 安全特性

### 默认行为
- **DM 配对**（Pairing）：未知发送者需要配对码才能激活
- **沙箱隔离**：Agent 在隔离环境中运行
- **权限分级**：不同 Agent 有不同的权限级别（Level 2-4）

### 安全准则
- 任何外部操作（邮件、推文、公开帖子）都需要询问
- Git 操作前确认，使用 `trash` 而不是 `rm`
- 记忆文件修改前确保有备份
- 删除文件前确认路径和内容

---

## 📊 核心优势

### 1. 平台中立
同一个 OpenClaw 可以同时在多个平台运行：
- WhatsApp / Telegram / Slack / Discord / Feishu...
- 无需为每个平台单独部署

### 2. 工具丰富
- **Browser**：浏览器控制
- **Canvas**：可视化工作空间
- **Nodes**：设备操作（相机、屏幕录制、位置、通知）
- **Cron**：定时任务
- **Sessions**：会话管理
- **Skills**：扩展工具

### 3. 隐私优先
- 本地运行，数据不出你的设备
- 支持本地模型（vLLM 等）
- 支持多种模型提供商（OpenAI、Anthropic、本地模型等）

### 4. 高度可扩展
- Skills 系统（可发布到 ClawHub）
- 插件架构（插件作为独立包）
- MCP 支持（通过 mcporter 桥接）

---

## 🎯 应用场景

### 1. 个人助手
- 邮件管理
- 日程提醒
- 消息整理
- 任务追踪

### 2. 内容创作
- 博客写作
- 文章润色
- 翻译
- 资料整理

### 3. 项目开发
- 代码编写
- 项目调试
- 文档生成
- Git 管理

### 4. 自动化
- 定时任务
- 监控告警
- 数据同步
- 批量处理

---

## 📚 学习资源

### 官方文档
- **GitHub**: https://github.com/openclaw/openclaw
- **文档**: https://docs.openclaw.ai
- **官网**: https://openclaw.ai
- **社区**: https://discord.gg/clawd

### 本地资源
- README: `/home/claw/.openclaw/workspace/docs/README.md`
- SOUL: `/home/claw/.openclaw/workspace/SOUL.md`（身份定义）
- USER: `/home/claw/.openclaw/workspace/USER.md`（用户信息）
- TOOLS: `/home/claw/.openclaw/workspace/TOOLS.md`（本地工具说明）
- IDENTITY: `/home/claw/.openclaw/workspace/IDENTITY.md`（身份背景）

### 参考文章
- SP1: 网关视角看 OpenClaw 架构
- 御坂网络第一代：多智能体架构
- 三层记忆宫殿：记忆系统设计
- 部署指南
- 折腾指北系列

---

## 🎓 关键总结

### OpenClaw 是什么？
**个人 AI 助手运行时平台** —— 一个能让你在任何聊天平台上拥有能做事的 AI 助手的网关系统。

### 核心组件？
Gateway（网关）+ Agent（智能体）+ Session（会话）+ Channel（通道）

### 关键概念？
- **Skills**：工具扩展系统
- **MCP**：标准化工具协议
- **Agent Loop**：AI 工作流程
- **System Prompt**：动态系统提示词
- **记忆系统**：三层架构持久化

### 我的使用方式？
- 本地 vLLM 部署大模型（Qwen3.5-35B）
- 御坂网络第一代多智能体架构
- 三层记忆系统（每日日志 + 精选记忆 + 长期归档）
- Feishu 作为主通道
- 定时任务（Cron）自动检查

### 安全要点？
- 先考证，不瞎编
- 任何外部操作前询问
- Git 操作用 `trash` 代替 `rm`
- 删除前确认路径和内容
- 修改记忆文件前备份

---

## 📝 明早汇报要点

### 1. OpenClaw 的核心价值
- 跨平台 AI 助手
- 能做事，不只是聊天
- 本地运行，隐私优先

### 2. 技术架构
- Gateway + Agent + Session + Channel
- 多智能体协作（御坂网络）
- 三层记忆系统

### 3. 工具和能力
- 丰富的内置工具（Browser、Canvas、Nodes 等）
- Skills 扩展系统
- MCP 支持

### 4. 我的配置
- 本地 vLLM 模型
- Feishu 通道
- 御坂网络第一代
- Cron 定时任务

### 5. 使用体验
- 多智能体分工明确
- 记忆持久化
- 自动化工具丰富
- 安全性高

---

**汇报时间**：2026-03-17 07:00 (Asia/Shanghai)
**准备状态**：✅ 已完成
**备注**：宁可不完美，也不瞎编！所有信息均来自官方文档和本地资料。
