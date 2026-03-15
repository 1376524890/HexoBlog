# OpenClaw 知识学习总结 - 2026-03-16 🦞

**学习时间**: 2026 年 3 月 16 日 6:41 AM (UTC+8)  
**学习时长**: ~20 分钟系统学习 + 前期 ~17 小时累计学习  
**目标**: 为明早 7 点的汇报做准备  
**状态**: ✅ 完全就绪  

---

## 📚 学习资源

### 核心文档
- ✅ `docs/OpenClaw-知识汇报 -2026-03-16.md` - 7 点汇报核心
- ✅ `docs/OpenClaw-High-Level-Overview-2026-03-10.md` - 高层概览
- ✅ `docs/OpenClaw-系统学习笔记.md` - 系统学习记录
- ✅ `docs/GIT-WORKSPACE-GUIDE.md` - Git 工作空间指南

### 官方文档
- ✅ 主站：https://docs.openclaw.ai
- ✅ 文档索引：https://docs.openclaw.ai/llms.txt
- ✅ GitHub: https://github.com/openclaw/openclaw
- ✅ 技能市场：https://clawhub.com

---

## 🎯 核心知识点（7 大模块）

### 1️⃣ OpenClaw 是什么？

**一句话定义**：
> **OpenClaw 是 AI Agent 运行时平台**，核心是智能网关（Runtime Gateway）。不是聊天机器人，而是把 AI 连接到真实世界的桥梁。

**核心特点**：
- ✅ **自托管**：运行在自己的机器上，数据私有
- ✅ **多通道**：一个 Gateway 服务多个聊天应用
- ✅ **Agent 原生**：内置工具使用、记忆、多 Agent 路由
- ✅ **开源**：MIT 许可，社区驱动

**与 ChatGPT 的对比**：

| 对比项 | ChatGPT | OpenClaw |
|--------|---------|----------|
| 定位 | 聊天机器人 | Agent 运行时平台 |
| 能力 | 生成文本 | 真正执行任务 |
| 记忆 | 会话内临时 | 持久化到磁盘文件 |
| 工具 | API 调用有限 | 文件系统、执行命令、浏览器控制等 |
| 部署 | 云端 SaaS | 本地部署，数据私有 |
| 安全性 | 受限于平台 | 多层次安全控制，审计完善 |

**四大核心理念**（必背⭐⭐⭐⭐⭐）：
1. **Access control before intelligence**（访问控制先于智能）
2. **隐私优先**：私有数据保持私有
3. **记忆即文件**：所有记忆写入 Markdown 文件
4. **工具优先**：第一类工具而非 skill 包裹

---

### 2️⃣ 核心架构

#### 三层架构

```
┌─────────────────────────────────────────┐
│    Agent Layer（智能层）← 大脑             │
│    - Main Agent（主 Agent）               │
│    - Subagents（子代理）                 │
│    - ACP Agents（编码代理）              │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    Gateway Layer（网关层）← 路由器（大脑！） │
│    - 控制平面、策略层、路由              │
│    - 身份认证、工具策略、会话管理        │
│    - 频道适配器（Discord/WhatsApp/飞书等）│
│    ⚠️ Gateway 本身不运行 AI 模型，只是调度员    │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    Node Layer（节点层）← 手脚             │
│    - 远程执行表面                        │
│    - 设备能力（摄像头、屏幕、通知、位置）│
│    - macOS companion app                 │
└─────────────────────────────────────────┘
```

**Gateway 的核心职责**：
1. 生命周期管理
2. 消息路由
3. 工具协调
4. 安全控制
5. 状态持久化

**Agent Loop（核心循环）**：
```
1. 接收输入 → 用户通过 Channel 发送消息
2. 构建上下文 → 组装 Session 历史、系统提示词、工具列表
3. LLM 推理 → 模型决定是"直接回复"还是"调用工具"
4. 工具执行 → 如需多步骤，通过 Gateway 调用外部工具
5. 循环或结束 → 多步推理继续，否则返回最终结果
6. 发送响应 → Gateway 通过原 Channel 发送给用户
```

#### 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书、微信等 |

---

### 3️⃣ 工具系统

#### 8 大工具分类

| 分类 | 代表工具 | 功能 |
|------|----------|------|
| **Runtime** | `exec`, `process`, `gateway` | 执行命令、管理进程、网关控制 |
| **Filesystem** | `read`, `write`, `edit`, `apply_patch` | 文件读写编辑 |
| **Session** | `sessions_list`, `sessions_history`, `sessions_spawn`, `session_status` | 会话管理 |
| **Memory** | `memory_search`, `memory_get` | 记忆检索 |
| **Web** | `web_search`, `web_fetch`, `tavily`, `multi-search-engine` | 网络搜索、网页获取 |
| **UI** | `browser`, `canvas` | 浏览器自动化、Canvas 渲染 |
| **Node** | `nodes` | 节点控制（摄像头、屏幕、位置等） |
| **Messaging** | `message` | 跨平台消息发送 |

#### Feishu 专用工具

| 工具 | 功能 |
|------|------|
| `feishu_doc` | 文档操作（读写、编辑、创建） |
| `feishu_drive` | 云盘文件管理 |
| `feishu_wiki` | 知识库导航 |
| `feishu_chat` | 聊天操作 |
| `feishu_bitable_*` | 多维表格操作 |
| `feishu_app_scopes` | 应用权限管理 |

#### MCP 协议

OpenClaw 的工具系统基于 **MCP（Model Context Protocol）**，这是 Anthropic 提出的开放标准。

**核心思想**：标准化 AI 与外部世界的交互接口。

**Skills 就是 MCP 的实现**：
- 每个 Skill 是一个独立的包
- 通过 JSON Schema 描述工具
- Gateway 负责 Skill 的注册、发现和调用
- Agent 通过标准接口与 Skill 交互

---

### 4️⃣ 技能系统（Skills）

#### 什么是 Skill？

Skill 是**专用任务的能力模块**，提供：
- 特定领域的操作指导
- 工具调用最佳实践
- 领域知识和约束

#### 已安装的 18 个 Skills

1. `hexo-blog` - Hexo 博客管理
2. `task-tracker` - 任务追踪与持久化
3. `weather` - 天气查询
4. `multi-search-engine` - 17 个搜索引擎（无需 API）
5. `proactive-agent` - 主动代理（WAL 协议、工作缓冲区）
6. `subagent-network-call` - 御坂网络调用
7. `xiaohongshu-ops` - 小红书运营
8. `morning-briefing` - 晨间简报
9. `blog-writing` - 博客写作
10. `email-sender` - 邮件发送
11. `stock-analysis` - 股票分析
12. `skill-vetter` - 技能安全审查
13. `skill-creator` - 技能创建工具
14. `self-improving-agent` - 自我改进
15. `tavily-search` - Tavily AI 优化搜索
16. `coding-agent` - 代码代理
17. `humanize-ai-text` - AI 文本人性化
18. `feishu-doc`, `feishu-drive`, `feishu-wiki` - 飞书集成

#### 常用 Skills 详解

##### Task Tracker（任务追踪）
**作用**：复杂任务拆解和进度跟踪
- 任务拆解为可执行步骤
- 持久化存储到 `workspace/memory/tasks/`
- 会话重启后恢复任务状态

##### Proactive Agent（主动代理）
**作用**：让 AI 从任务执行者变成主动伙伴
- **WAL 协议**：Write-Ahead Logging 记录关键信息
- **工作缓冲区**：在上下文危险区记录所有交互
- **自主定时任务**：独立于主会话执行后台任务
- **持续改进模式**：从每次交互中学习

##### Morning Briefing（晨间简报）
**作用**：自动生成每日晨报
- 天气信息查询
- 日历事件读取
- 待办事项汇总
- 新闻摘要
- 通过飞书/微信推送

---

### 5️⃣ 御坂网络第一代（多智能体系统）

#### 身份结构

| 编号 | 名称 | Agent ID | 职责 | 权限等级 |
|------|------|----------|------|----------|
| 本尊 | 御坂美琴 | 本人 | 主人 | Level 5 |
| 1 号 | 御坂美琴一号 | main | 全能助手，核心中枢 | Level 5 |
| 10 号 | 御坂妹妹 10 号 | general-agent | 通用代理，处理琐碎问题 | Level 3 |
| 11 号 | 御坂妹妹 11 号 | code-executor | 代码执行者 | Level 3 |
| 12 号 | 御坂妹妹 12 号 | content-writer | 内容创作者 | Level 3 |
| 13 号 | 御坂妹妹 13 号 | research-analyst | 研究分析师 | Level 3 |
| 14 号 | 御坂妹妹 14 号 | file-manager | 文件管理器 | Level 2 |
| 15 号 | 御坂妹妹 15 号 | system-admin | 系统管理员 | Level 4 |
| 16 号 | 御坂妹妹 16 号 | web-crawler | 网络爬虫 | Level 2 |
| 17 号 | 御坂妹妹 17 号 | memory-organizer | 记忆整理专家 | Level 3 |

#### 架构示意

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

#### 调用方式

```python
# 调用子代理执行任务
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",
  mode: "run",      # run=单次，session=持久
  task: "编写一个 Python 脚本"
})
```

#### 子代理机制

**启动方式**：
- **工具方式**（推荐）：`sessions_spawn()`
- **Slash 命令**：`/subagents spawn <agentId> <task>`

**深度层级**：
- **Depth 0**: Main Agent（主代理）
- **Depth 1**: Sub-agent（可进一步派生当 maxSpawnDepth≥2）
- **Depth 2**: Leaf worker（不可再派生）

**最大嵌套深度**: 1-5（推荐 2）

**并发控制**:
- `maxConcurrent` - 全局并发上限（默认 8）
- `maxChildrenPerAgent` - 每个代理的子代理上限（默认 5）

**通知机制**：子代理完成时会 announce 结果回主会话，包含 Status、Runtime、Token 统计和 estimated cost。

---

### 6️⃣ 记忆系统

#### 三层记忆架构

```
┌─────────────────────────────────────────┐
│ Layer 1: 会话记忆（Session Memory）       │
│ - 当前会话上下文                        │
│ - 临时决策和中间结果                    │
└────────────────┬────────────────────────┘
                 ↓ 同步关键信息
┌─────────────────────────────────────────┐
│ Layer 2: 任务记忆（Task Memory）          │
│ - 任务计划文件                          │
│ - 子代理执行结果                        │
└────────────────┬────────────────────────┘
                 ↓ 同步重要发现
┌─────────────────────────────────────────┐
│ Layer 3: 长期记忆（Long-term Memory）     │
│ - MEMORY.md：精选记忆                   │
│ - memory/YYYY-MM-DD.md：每日日志       │
└─────────────────────────────────────────┘
```

#### 记忆文件位置

```
~/openclaw/workspace/
├── MEMORY.md              # 长期记忆（精选）
└── memory/
    ├── 2026-03-09.md      # 今日日志
    ├── 2026-03-08.md      # 昨日日志
    ├── 2026-03-07.md
    └── tasks/
        └── ACTIVE-task-id.md  # 活跃任务计划
```

#### 记忆管理最佳实践

1. **DECIDE to write**: 决定、偏好、持久事实 → MEMORY.md
2. **Daily notes**: 日常记录 → memory/YYYY-MM-DD.md
3. **定期 review**: 定期清理 MEMORY.md，移除过时信息
4. **Ask to remember**: 重要事项明确让 Agent 写入记忆

#### 记忆工具

- `memory_search` - 语义检索
- `memory_get` - 读取特定文件

#### 安全操作规则

1. ✅ 使用 `trash` 而不是 `rm`
2. ✅ 操作前备份
3. ✅ 检查 Git 状态
4. ✅ 立即提交

---

### 7️⃣ 安全模型

#### 信任边界

OpenClaw 假设：
- **单一用户信任边界** per Gateway
- 不支持敌对多租户
- 如需隔离需分 Gateway/OS User/Host

#### 权限层级

| 级别 | 名称 | 权限说明 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

#### 安全原则

1. **Private things stay private**：私密信息不泄露
2. **Ask before acting externally**：外部行动前确认
3. **Never send half-baked replies**：不要发送半成品回复
4. **Be careful in group chats**：在群组中不要代表用户说话

#### 安全审计命令

```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
openclaw security audit --json    # JSON 格式
```

#### 安全加固配置

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "长随机 token" },
  },
  session: { dmScope: "per-channel-peer" },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
}
```

---

## 📊 系统架构深入学习

### Gateway 架构细节

**Gateway 的核心职责**：
- 维护提供者连接
- 暴露类型化的 WS API（请求、响应、服务器推送事件）
- 验证传入帧是否符合 JSON Schema
- 发射事件：`agent`, `chat`, `presence`, `health`, `heartbeat`, `cron`

**协议细节**：
- **传输**：WebSocket，文本帧 + JSON 负载
- **首帧**：必须是 `connect`
- **认证**：`OPENCLAW_GATEWAY_TOKEN` 或 `--token`
- **幂等性键**：`send`, `agent` 等副作用方法需要
- **节点身份**：节点必须包含 `role: "node"` + caps/commands/permissions

**连接生命周期**：
```
Client --> Gateway: req:connect
Gateway --> Client: res (ok)
Gateway --> Client: event:presence
Gateway --> Client: event:tick
Client --> Gateway: req:agent
Gateway --> Client: res:agent {runId, status:"accepted"}
Gateway --> Client: event:agent (streaming)
Gateway --> Client: res:agent {runId, status, summary}
```

### 节点配对

- 所有 WS 客户端（操作员 + 节点）在 `connect` 时包含**设备身份**
- 新设备 ID 需要配对批准；Gateway 颁发**设备令牌**供后续连接
- **本地连接**（回环或网关主机自身的 tailnet 地址）可以自动批准
- 所有连接必须签名 `connect.challenge` nonce

---

## 🛠️ Feishu 集成细节

### 集成模式

- **WebSocket 连接**：长连接方式，无需公开 URL
- **确定性路由**：回复始终返回到 Feishu
- **会话隔离**：DM 共享主会话；群组隔离

### 访问控制

**直接消息**：
- **默认**：`dmPolicy: "pairing"`（未知用户获得配对码）
- **批准配对**：`openclaw pairing approve feishu <CODE>`
- **白名单模式**：设置 `channels.feishu.allowFrom` 允许的 Open IDs

**群组聊天**：
- **群组策略** (`groupPolicy`)：`"open"` / `"allowlist"` / `"disabled"`
- **提及要求** (`requireMention`)：默认 true，要求@提及
- **发送者白名单**：可选，限制特定用户可以发消息

### 权限要求

Feishu 应用需要的权限：
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

---

## 🎯 核心洞见（总结用）

1. ✅ **不是聊天机器人，是做事的 Agent** - 能真正执行任务，不只是聊天
2. ✅ **记忆即文件** - 所有记忆持久化到磁盘，不丢失
3. ✅ **访问控制先于智能** - 安全是第一原则
4. ✅ **模块化设计** - Skills 和 Channels 独立可替换
5. ✅ **多智能体协作** - 专业分工，效率更高
6. ✅ **自托管部署** - 数据完全掌控在用户手中
7. ✅ **跨平台支持** - 一个 Gateway 服务多个聊天应用
8. ✅ **路由灵活** - 支持单多 Agent、单多账户、多角色路由

---

## 📝 常用命令速查

### Gateway 管理

```bash
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
```

### 安全审计

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
```

### 子代理操作

```bash
# 启动子代理
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",
  task: "总结 OpenClaw 核心优势"
})

# 查看状态
/subagents list
/subagents log <id>
/subagents kill <id>
/subagents steer <id> <message>
```

### 配对管理

```bash
openclaw pairing list feishu
openclaw pairing approve feishu <CODE>
```

### Cron 定时任务

```bash
/cron add <cron-expression> <task>
/cron list
/cron remove <jobId>
/cron wake  # 立即触发 heartbeat
```

---

## ❓ 常见问题 FAQ

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时平台，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 记忆会丢失吗？ | 不会，记忆即文件，持久化到磁盘 |
| 如何扩展功能？ | 通过 Skills 系统，自定义或从 ClawHub 安装 |
| 是否支持中文？ | 支持，所有文档和界面都支持多语言 |
| 是否需要付费？ | 开源免费，但需要第三方 API |
| 支持哪些消息平台？ | Telegram、Discord、Slack、WhatsApp、Signal、飞书、微信等 |
| 如何监控子代理？ | 使用 `/subagents list` 查看状态 |

---

## 📚 参考资料

### 官方文档
- **主站**: https://docs.openclaw.ai
- **文档索引**: https://docs.openclaw.ai/llms.txt
- **GitHub**: https://github.com/openclaw/openclaw
- **ClawHub**: https://clawhub.com
- **Discord 社区**: https://discord.gg/clawd

### 本地文档
- `docs/OpenClaw-知识汇报 -2026-03-16.md` - 7 点汇报核心
- `docs/OpenClaw-High-Level-Overview-2026-03-10.md` - 高层概览
- `docs/OpenClaw-系统学习笔记.md` - 详细学习笔记
- `docs/GIT-WORKSPACE-GUIDE.md` - Git 指南

---

## ✅ 汇报准备检查清单

- [x] 1️⃣ OpenClaw 定义（一句话 + 四大核心理念）
- [x] 2️⃣ 核心架构（三层架构 + 四组件 + Agent Loop）
- [x] 3️⃣ 工具与技能系统（8 大分类 + 18 个 Skills）
- [x] 4️⃣ 多智能体协作（御坂网络第一代架构）
- [x] 5️⃣ 记忆系统（三层架构 + 最佳实践）
- [x] 6️⃣ 安全模型（权限层级 + 审计命令）
- [x] 7️⃣ 常见问题（FAQ 准备）
- [x] 演示脚本准备
- [x] 所有文档已阅读和理解

**准备状态**: ✅ **完全就绪** 🚀

---

**汇报时间**: 2026 年 3 月 16 日 7:00 AM (Asia/Shanghai)  
**整理者**: 御坂美琴一号 ⚡  
**御坂网络第一代系统运行中** ⚡

---

*文档版本：1.0.0*  
*最后更新：2026-03-16 06:41 (Asia/Shanghai)*
