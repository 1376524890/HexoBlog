# OpenClaw 知识学习报告

**学习时间**: 2026 年 3 月 9 日 12:00-14:00 UTC  
**汇报时间**: 2026 年 3 月 9 日 7:00 AM (UTC+8)  
**汇报时长**: 25-30 分钟  
**整理者**: 御坂美琴一号 ⚡  
**用途**: 明早 7 点汇报准备 ✅

---

## 📌 快速导航

| 章节 | 重点内容 | 预计耗时 |
|------|----------|----------|
| 1. OpenClaw 是什么 | 核心定义、四大特点 | 3 分钟 |
| 2. 核心架构 | Gateway/Agent/Session/Channel 四组件 | 8 分钟 |
| 3. 工具系统 | 内置工具 + Skills 扩展 | 6 分钟 |
| 4. 多智能体系统 | 御坂网络第一代、子代理调度 | 5 分钟 |
| 5. 安全模型 | 权限层级、最佳实践 | 4 分钟 |
| 6. 演示建议 | 工具调用、记忆系统、子代理 | 5 分钟 |

---

## 1️⃣ OpenClaw 是什么？

### 核心定义

**OpenClaw 不是聊天机器人，而是一个 AI Agent 运行时平台**。

**核心定位**: **智能网关（Runtime Gateway）** —— 把 AI 模型连接到真实世界的桥梁。

**一句话总结**: 它不是用来聊天的，而是用来**做事情的**。

### 四大核心理念

| 理念 | 含义 | 重要性 |
|------|------|--------|
| **Access control before intelligence** | 访问控制先于智能 | ⭐⭐⭐⭐⭐ |
| **隐私优先** | 私有数据保持私有 | ⭐⭐⭐⭐ |
| **记忆即文件** | 所有记忆写入 Markdown 文件 | ⭐⭐⭐⭐⭐ |
| **工具优先** | 第一类工具而非 skill 包裹 | ⭐⭐⭐⭐ |

### 关键特点

| 特点 | 说明 | 价值 |
|------|------|------|
| **自托管 (Self-hosted)** | 运行在自己的硬件上 | 数据私有，不依赖云 |
| **多通道 (Multi-channel)** | 一个 Gateway 服务多个平台 | 统一管理，效率提升 |
| **Agent 原生 (Agent-native)** | 内置工具调用、会话管理 | 真正的智能体 |
| **开源 (Open source)** | MIT 许可，社区驱动 | 可定制，可扩展 |

**支持的平台**: Telegram、Discord、Slack、WhatsApp、Signal、飞书、微信（通过 Lark）等 15+ 个通道。

---

## 2️⃣ 核心架构解析

### 2.1 三层架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                   Agent Layer (智能层)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Main Agent   │  │ Subagents    │  │ ACP Agents   │      │
│  │ 主 Agent      │  │ 子代理        │  │ 编码代理     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                   Gateway Layer (网关层)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 控制平面 · 策略层 · 路由 · 身份认证 · 会话管理          │  │
│  │ 🔑 核心：Gateway 本身**不运行 AI 模型**，只是调度员      │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    Node Layer (节点层)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 设备能力     │  │ 远程执行     │  │ 移动端 App   │      │
│  │ (相机/屏幕)  │  │              │  │ (iOS/Android)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 四大核心组件详解

#### 🏗️ 1. Gateway（网关）—— 大脑

**职责**:
- 生命周期管理（启动/停止/监控 Agent）
- 消息路由（从 Channel 到 Session）
- 工具协调（Skill 注册与调用）
- 安全控制（沙箱策略、权限管理）
- 状态持久化（维护 Session 历史）

**核心特点**: Gateway 本身**不运行 AI 模型**，只是 AI 模型的"调度员"。

#### 🤖 2. Agent（AI 执行体）—— 执行者

**每个 Agent 包含**:
- **身份（Identity）**: 名称、描述、头像
- **配置（Config）**: 使用的模型、系统提示词
- **状态（State）**: 当前会话、历史消息、记忆
- **运行时（Runtime）**: 执行环境（隔离环境）

**通信方式**: 通过 **Bridge Protocol** 与 Gateway 通信。

#### 📦 3. Session（会话容器）—— 有状态容器

**定义**: OpenClaw 的**有状态的会话容器**

**包含内容**:
- **消息历史**: 完整对话记录
- **上下文窗口**: 经过压缩处理的有效上下文
- **工具状态**: 本次会话的工具调用中间结果
- **元数据**: 创建时间、最后活跃时间等

**核心挑战**: **上下文长度管理** → 通过 **Compaction（压缩）** 机制解决

#### 🔌 4. Channel（消息通道）—— 协议适配器

**定义**: 与外部世界连接的**协议适配器**

**官方支持的 Channel**:
- **即时通讯**: Telegram、Discord、Slack、WhatsApp、Signal
- **企业平台**: 飞书、Microsoft Teams、Google Chat
- **传统协议**: IRC、Matrix
- **其他**: iMessage、Webhook

**插件化设计**: 每个 Channel 都是独立插件，实现统一接口。

### 2.3 Agent Loop（核心循环）

理解 OpenClaw 的关键是理解 **Agent Loop**。

```
┌──────────────────────────────────────────────────────────┐
│                      Agent Loop                          │
│                                                          │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│   │ 接收输入 │ → │ 思考决策 │ → │ 执行动作 │             │
│   └─────────┘    └────┬────┘    └────┬────┘             │
│        ↑              │              │                   │
│        │         ┌─────────┐    ┌─────────┐             │
│        │         │工具调用 │    │直接回复 │             │
│        │         └────┬────┘    └────┬────┘             │
│        │              │              │                   │
│        └──────────────┴──────────────┘                   │
└──────────────────────────────────────────────────────────┘
```

**流程详解**:
1. **接收输入**：用户通过 Channel 发送消息，Gateway 路由到对应 Session
2. **构建上下文**：组装 Session 历史、系统提示词、工具列表
3. **LLM 推理**：模型决定是**直接回复**还是**调用工具**
4. **工具执行**：如需多步骤，通过 Gateway 调用外部工具
5. **循环或结束**：多步推理则继续，否则返回最终结果
6. **发送响应**：Gateway 通过原 Channel 发送给用户

**关键点**: 模型拥有**决策权**，主动决定需要什么信息、调用什么工具。

---

## 3️⃣ 工具系统

### 3.1 工具分类

#### 🔧 基础工具（内置）

| 工具 | 功能 | 说明 |
|------|------|------|
| `read` | 读取文件 | 支持文本和图片（jpg, png, gif, webp） |
| `write` | 创建/覆盖文件 | 自动创建父目录 |
| `edit` | 编辑文件 | 精确替换指定文本 |
| `exec` | 执行命令 | 支持后台运行、PTY 模式 |
| `browser` | 浏览器控制 | 页面控制、截图、自动化 |
| `message` | 消息管理 | 发送、删除、频道操作 |
| `nodes` | 节点管理 | 设备状态、相机、屏幕录制 |
| `sessions_*` | 会话管理 | 启动子代理、获取历史等 |

#### 🌐 网络工具

| 工具 | API | 特点 |
|------|-----|------|
| `web_search` | Perplexity API | 结构化搜索 |
| `tavily` | Tavily API | AI 优化搜索 |
| `multi-search-engine` | **17 个引擎** | 无需 API，完全免费 |

#### 📊 Feishu 集成工具

| 工具 | 功能 |
|------|------|
| `feishu_doc` | 文档操作（读写、表格、上传） |
| `feishu_drive` | 云盘文件管理 |
| `feishu_wiki` | 知识库导航 |
| `feishu_chat` | 聊天操作 |
| `feishu_bitable_*` | 多维表格操作（增删改查） |
| `feishu_app_scopes` | 应用权限管理 |

### 3.2 Skills 系统

#### 什么是 Skill？

Skill 是**专用任务的能力模块**，提供：
- 特定领域的操作指导
- 工具调用最佳实践
- 领域知识和约束

#### Skills 特点

1. **模块化**: 每个 Skill 是独立包
2. **可扩展**: 用户可以自定义 Skill
3. **标准化**: 通过 `SKILL.md` 定义功能
4. **可组合**: 多个 Skill 协同工作

#### 当前已安装 Skills（16 个）

| Skill | 功能 |
|-------|------|
| `hexo-blog` | Hexo 博客管理 |
| `task-tracker` | 任务追踪与进度管理 |
| `weather` | 天气查询（无需 API） |
| `multi-search-engine` | 17 个搜索引擎 |
| `proactive-agent` | 主动代理，变成主动伙伴 |
| `self-improving-agent` | 自我改进系统 |
| `skill-vetter` | 技能安全审查 |
| `skill-creator` | 技能创建工具 |
| `subagent-network-call` | 御坂网络调用 |
| `xiaohongshu-ops-skill` | 小红书运营 |
| `morning-briefing` | 晨间简报 |
| `tavily-search` | Tavily 搜索 |
| `blog-writing` | 博客写作 |
| `email-sender` | 邮件发送 |
| `stock-analysis` | 股票分析 |
| `monitoring` | 系统监控 |

**技能管理命令**:
```bash
clawhub sync              # 同步所有技能
clawhub fetch <name>      # 获取单个技能
clawhub publish <folder>  # 发布自定义技能
```

---

## 4️⃣ 多智能体系统（御坂网络第一代）

### 4.1 什么是子代理（Subagent）

子代理是从主会话启动的**后台代理运行**，用于：
- 并行化耗时任务
- 隔离敏感/复杂操作
- 支持嵌套编排模式

**核心思想**: 主 Agent 负责任务拆解与调度，子 Agent 负责具体执行。

### 4.2 御坂网络第一代架构 ⚡

```
┌─────────────────────────────────────────────────────────────┐
│                    御坂美琴一号（主 Agent）                   │
│                      职责：任务拆解与调度                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ 11 号 Code│   │ 12 号 Write│   │ 13 号 Research│
   │ 代码执行者│   │ 内容创作者│   │ 研究分析师│
   └──────────┘    └──────────┘    └──────────┘
          │               │               │
          ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ 14 号 File│   │ 15 号 Sys │   │ 16 号 Crawler│
   │ 文件管理器│   │ 系统管理员│   │ 网络爬虫  │
   └──────────┘    └──────────┘    └──────────┘
```

#### 子代理职责表

| 编号 | 名称 | Agent ID | 职责 |
|------|------|----------|------|
| 10 号 | 通用代理 | `general-agent` | 处理琐碎问题 |
| 11 号 | Code 执行者 | `code-executor` | 代码编写、调试、重构 |
| 12 号 | 内容创作者 | `content-writer` | 文章撰写、翻译、润色 |
| 13 号 | 研究分析师 | `research-analyst` | 信息搜索、数据分析 |
| 14 号 | 文件管理器 | `file-manager` | 文件操作、目录管理 |
| 15 号 | 系统管理员 | `system-admin` | 系统配置、服务管理 |
| 16 号 | 网络爬虫 | `web-crawler` | 网页抓取、数据提取 |

### 4.3 子代理启动方式

#### 工具方式（推荐）

```python
sessions_spawn({
  runtime: "subagent",      # 使用 subagent 运行时
  agentId: "code-executor", # 子代理 ID
  mode: "run",              # run=单次运行，session=持久会话
  label: "task-label",      # 任务标签
  task: "任务描述"
})
```

#### Slash 命令方式

```bash
/subagents spawn <agentId> <task>
/subagents list              # 列出所有子代理
/subagents kill <id>         # 杀死子代理
/subagents log <id>          # 查看日志
/subagents steer <id> <msg>  # 向子代理发送消息
```

### 4.4 任务调度机制

#### 任务计划格式

```yaml
# memory/tasks/ACTIVE-example-task.md
steps:
  - step_id: 1
    title: "设计数据库 Schema"
    agent_type: "code-executor"
    dependencies: []
    input:
      requirements: "设计博客系统数据库"
  
  - step_id: 2
    title: "编写后端 API"
    agent_type: "code-executor"
    dependencies: [1]
    input:
      schema: "{{step_1.output.schema}}"
```

#### 执行流程

```
1. 读取任务计划文件
   → memory/tasks/ACTIVE-<task-id>.md

2. 解析任务步骤
   → 提取 agent_type 和 dependencies

3. 构建依赖图
   → 确定任务执行顺序（拓扑排序）

4. 按顺序执行任务
   → 无依赖或依赖已完成 → 执行

5. 更新任务状态
   → 写入任务文件

6. 收集执行结果
   → 输出报告
```

### 4.5 三层记忆架构

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: 会话记忆（Session Memory）                          │
│ - 当前会话上下文                                             │
│ - 临时决策和中间结果                                         │
└─────────────────────────────────────────────────────────────┘
         │ 同步关键信息
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: 任务记忆（Task Memory）                             │
│ - 任务计划文件                                               │
│ - 子代理执行结果                                             │
└─────────────────────────────────────────────────────────────┘
         │ 同步重要发现
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: 长期记忆（Long-term Memory）                        │
│ - MEMORY.md: 精选记忆                                       │
│ - memory/YYYY-MM-DD.md: 每日日志                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 5️⃣ 安全模型与最佳实践

### 5.1 安全模型核心

#### 信任边界

OpenClaw 假设：
- **单一用户信任边界** per Gateway
- Gateway 和 Node 属于同一信任域
- 不支持敌对多租户

#### 权限层级

| 级别 | 类型 | 权限范围 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

#### 安全控制机制

- **沙箱隔离**: Agent 运行在隔离环境中
- **权限模型**: 五层级权限控制
- **审计日志**: 所有操作记录到审计日志
- **工具 profile**: minimal/coding/messaging/full
- **ask always**: 高风险操作需确认

### 5.2 最佳实践

#### 记忆管理

1. **DECIDE to write**: 决定、偏好、持久事实 → MEMORY.md
2. **Daily notes**: 日常记录 → memory/YYYY-MM-DD.md
3. **定期 review**: 定期清理 MEMORY.md，移除过时信息
4. **Ask to remember**: 重要事项明确让 Agent 写入记忆

#### 安全建议

1. **定期 audit**: 每月运行安全审计
2. **最小权限**: 按需开放工具
3. **强认证**: 使用长随机 token
4. **本地部署**: Gateway 绑定到 loopback
5. **权限检查**: 确认 ~/.openclaw 权限设置

#### 工具安全策略

| 策略 | 说明 |
|------|------|
| `tools.allow` / `tools.deny` | 允许/拒绝工具 |
| `sandbox` | 沙箱隔离 |
| `elevated` | 提权执行（需显式启用） |
| `ask: always` | 高风险操作需确认 |
| `workspaceOnly` | 限制文件系统操作范围 |

### 5.3 安全审计命令

```bash
# 基本检查
openclaw security audit

# 深度检查
openclaw security audit --deep

# 自动修复
openclaw security audit --fix

# JSON 格式输出
openclaw security audit --json
```

---

## 6️⃣ 常用命令速查

### Gateway 管理

```bash
openclaw gateway status   # 查看状态
openclaw gateway start    # 启动网关
openclaw gateway stop     # 停止网关
openclaw gateway restart  # 重启网关
```

### 配置管理

```bash
openclaw configure              # 配置向导
openclaw config.apply           # 应用配置
openclaw config.schema.lookup   # 查看配置 schema
```

### 技能管理

```bash
clawhub sync              # 同步所有技能
clawhub fetch <name>      # 获取单个技能
clawhub publish <folder>  # 发布自定义技能
```

### 会话管理

```bash
# 启动子代理
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",
  label: "task-label",
  task: "研究 XX 主题"
})

# 查看会话
sessions_list()

# 查看会话历史
sessions_history({sessionKey: "...", limit: 20})
```

### 定时任务

```bash
/cron add <表达式> <任务>    # 添加定时任务
/cron list                   # 列出所有定时任务
/cron remove <jobId>         # 删除定时任务
/cron wake                   # 立即触发 heartbeat
```

---

## 7️⃣ 汇报演示建议

### 7.1 演示重点（5 分钟）

#### 演示 1：工具调用

```python
# 1. 读取文件
read({"path": "docs/OpenClaw-Report-Final-2026-03-09.md"})

# 2. 执行命令
exec({
  "command": "ls -la memory/",
  "workdir": "/home/claw/.openclaw/workspace"
})

# 3. 网络搜索
web_search({
  "query": "OpenClaw 最新功能",
  "count": 3
})
```

**亮点**: 展示 OpenClaw 能真正"做事"，不仅仅是聊天。

#### 演示 2：记忆系统

```python
# 1. 写入记忆
write({
  "path": "memory/2026-03-09.md",
  "content": "# 今日学习记录\n\n- 学习了 OpenClaw 核心架构\n- 整理了三层记忆系统..."
})

# 2. 搜索记忆
memory_search({
  "query": "OpenClaw 架构",
  "maxResults": 3
})
```

**亮点**: 展示记忆持久化，会话重启后仍能回忆。

#### 演示 3：子代理系统

```python
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",
  label: "research-task",
  task: "总结 OpenClaw 的三大核心优势"
})
```

**亮点**: 展示多智能体协作，主代理负责任务调度。

### 7.2 演示准备清单

- [ ] 打开 Gateway 状态（`openclaw gateway status`）
- [ ] 准备测试文件（memory/ 目录）
- [ ] 确认技能已安装（`clawhub sync`）
- [ ] 准备演示脚本

### 7.3 常见问题预判

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时平台，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 能否在云端部署？ | 可以，但推荐本地部署保证数据私有 |
| 如何扩展功能？ | 通过 Skills 系统，自定义 Skill 或从 ClawHub 安装 |

---

## 📊 总结

### OpenClaw 核心优势

| 优势 | 说明 |
|------|------|
| **智能网关** | 统一管理多个平台和 Agent |
| **模块化设计** | Skills、Channels、Agents 独立可替换 |
| **持久化记忆** | 三层记忆架构，避免失忆 |
| **多智能体协作** | 子代理系统，专业分工 |
| **安全隔离** | 沙箱策略、权限模型、审计日志 |
| **可扩展** | 自定义 Skills、Channels |

### 学习重点回顾

1. ✅ **核心架构**: Gateway、Agent、Session、Channel 四大组件
2. ✅ **Agent Loop**: AI 持续运行的核心循环
3. ✅ **工具系统**: 内置工具 + Skills 扩展
4. ✅ **多智能体**: 子代理系统、御坂网络第一代
5. ✅ **记忆同步**: 三层记忆架构
6. ✅ **安全模型**: 权限层级与审计机制

### 关键理念

- **不是聊天机器人，是做事的 Agent**
- **记忆即文件**，所有记忆持久化到磁盘
- **访问控制先于智能**，安全是第一原则
- **模块化设计**，Skills 可扩展，Channels 可替换

---

## 📚 参考资料

| 资源 | 链接 |
|------|------|
| 官方文档 | https://docs.openclaw.ai |
| GitHub 仓库 | https://github.com/openclaw/openclaw |
| ClawHub（技能市场） | https://clawhub.com |
| Discord 社区 | https://discord.gg/clawd |
| 本地文档 | `~/openclaw/workspace/docs/` |

---

**汇报准备完成时间**: 2026 年 3 月 9 日 14:00 UTC  
**建议携带**: 笔记本电脑（现场演示）、演示脚本、常见问题清单  

---

*整理：御坂美琴一号 ⚡  
更新时间：2026-03-09 14:00 UTC*
