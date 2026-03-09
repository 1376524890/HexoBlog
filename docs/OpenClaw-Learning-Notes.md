# OpenClaw 学习文档

> 系统学习 OpenClaw 核心概念、工具系统、技能系统、会话与子代理机制、Feishu 集成、安全机制与最佳实践  
> 学习日期：2026-03-09  
> 目的：为明早 7 点的汇报做准备

---

## 目录

1. [核心概念与架构](#1-核心概念与架构)
2. [工具系统](#2-工具系统)
3. [技能系统 (Skills)](#3-技能系统-skills)
4. [会话和子代理机制](#4-会话和子代理机制)
5. [Feishu 集成](#5-feishu 集成)
6. [安全机制和最佳实践](#6-安全机制和最佳实践)
7. [总结](#7-总结)

---

## 1. 核心概念与架构

### 1.1 OpenClaw 是什么？

OpenClaw 是一个 **AI Agent 运行时平台**，核心定位是**智能网关（Runtime Gateway）**。

#### 核心定义

- **运行时（Runtime）**：提供 Agent 执行所需的环境、资源和生命周期管理
- **平台（Platform）**：可扩展、可配置的生态系统
- **AI Agent**：以大语言模型（LLM）为核心，具备工具调用能力的智能体

#### 架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Telegram │  │ Discord  │  │  Slack   │  │ 其他平台  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┴─────────────┴─────────────┘           │
│                         │                                    │
│                    Channel Layer                            │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │   Session Manager   │                        │
│              └──────────┬──────────┘                        │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │     Agent Pool      │                        │
│              └──────────┬──────────┘                        │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │   Tool Registry     │ ← Skills/MCP          │
│              └──────────┬──────────┘                        │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │   LLM Providers     │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 四大核心组件

#### 1. Gateway（网关）

Gateway 是 OpenClaw 的核心守护进程（Daemon），是系统的"大脑"和"路由器"。

**职责**：
- **生命周期管理**：启动、停止、监控所有 Agent 实例
- **消息路由**：将来自各 Channel 的消息分发到正确的 Session 和 Agent
- **工具协调**：管理 Skill 注册，处理工具调用请求
- **安全控制**：执行沙箱策略，管理权限边界
- **状态持久化**：维护 Session 历史，处理上下文压缩

**重要特点**：Gateway 本身**不运行 AI 模型**，只是 AI 模型的"调度员"。

#### 2. Agent（AI 执行体）

Agent 是实际执行 AI 任务的实例。

**每个 Agent 包含**：
- **身份（Identity）**：名称、描述、头像等元信息
- **配置（Config）**：使用的模型、系统提示词、可用工具等
- **状态（State）**：当前会话、历史消息、记忆等
- **运行时（Runtime）**：执行环境（本地进程、Docker、远程等）

**运行环境**：Agent 运行在**隔离环境**中，通过**Bridge Protocol**与 Gateway 通信。

#### 3. Session（会话容器）

Session 是 OpenClaw 的**有状态的会话容器**。

**包含内容**：
- **消息历史**：用户与 AI 的完整对话记录
- **上下文窗口**：当前有效的上下文（经过压缩处理）
- **工具状态**：本次会话中工具调用的中间结果
- **元数据**：创建时间、最后活跃时间、关联的 Channel 等

**核心挑战**：上下文长度管理。通过**Compaction（压缩）**机制解决。

#### 4. Channel（消息通道）

Channel 是 OpenClaw 与外部世界连接的**协议适配器**。

**官方支持的 Channel**：
- **即时通讯**：Telegram、Discord、Slack、WhatsApp、Signal、微信（通过 Lark/Feishu）
- **传统协议**：IRC、Matrix
- **企业平台**：Microsoft Teams、Google Chat、飞书
- **其他**：iMessage、BlueBubbles、Webhook

**插件化设计**：每个 Channel 都是插件，实现统一接口：
- 接收消息（从平台到 OpenClaw）
- 发送消息（从 OpenClaw 到平台）
- 格式转换（平台特定格式 ↔ OpenClaw 标准格式）

### 1.3 Agent Loop

理解 OpenClaw 的关键是理解**Agent Loop**——AI Agent 持续运行的核心循环。

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
└──────────────────────────────────────────────────────────┘
```

**具体流程**：
1. **接收输入**：用户通过某个 Channel 发送消息，Gateway 路由到对应 Session 的 Agent
2. **构建上下文**：Gateway 将 Session 历史、系统提示词、可用工具列表组装成完整的 Prompt
3. **LLM 推理**：Agent 调用大模型，模型决定是**直接回复**还是**调用工具**
4. **工具执行**（如果需要）：Agent 通过 Gateway 调用外部工具，获取结果
5. **循环或结束**：如果需要多步推理，回到步骤 3；否则返回最终结果
6. **发送响应**：Gateway 将 AI 的回复通过原 Channel 发送给用户

**关键点**：模型拥有决策权，主动决定需要什么信息、调用什么工具、如何组织答案。

### 1.4 System Prompt

System Prompt（系统提示词）是 Agent 的"出厂设置"，定义了身份、能力、行为规则和环境信息。

**动态生成机制**：
1. **基础身份**：Agent 的名称、描述、emoji 等
2. **工具描述**：当前可用的所有工具及其参数说明（JSON Schema 格式）
3. **运行时信息**：当前时间、日期、环境变量等
4. **安全提示**：沙箱边界、禁止行为等
5. **格式说明**：如何输出工具调用、如何组织回复

### 1.5 MCP 协议

OpenClaw 的工具系统基于**MCP（Model Context Protocol）**，这是 Anthropic 提出的开放标准。

**MCP 核心思想**：标准化 AI 与外部世界的交互接口。

**OpenClaw 的 Skills 就是 MCP 的实现**：
- 每个 Skill 是一个独立的包，包含工具定义和实现
- Skill 通过 JSON Schema 描述工具的输入输出
- Gateway 负责 Skill 的注册、发现和调用
- Agent 通过标准接口与 Skill 交互，无需关心具体实现

---

## 2. 工具系统

### 2.1 工具分类

OpenClaw 的工具系统分为以下几类：

#### 基础工具（内置）

| 工具 | 功能 | 说明 |
|------|------|------|
| `read` | 读取文件 | 支持文本文件和图片（jpg, png, gif, webp） |
| `write` | 创建/覆盖文件 | 自动创建父目录 |
| `edit` | 编辑文件 | 精确替换指定文本 |
| `exec` | 执行命令 | 支持后台运行、PTY 模式 |
| `process` | 管理进程 | list, poll, log, write, send-keys |
| `browser` | 浏览器控制 | 页面控制、截图、自动化 |
| `canvas` | Canvas 控制 | 呈现/评估/快照 |
| `nodes` | 节点管理 | 设备状态、相机、屏幕录制等 |
| `message` | 消息管理 | 发送、删除、频道操作 |
| `subagents` | 子代理管理 | list, kill, steer |
| `tts` | 文本转语音 | 将文本转换为语音 |

#### 网络工具

| 工具 | 功能 | API |
|------|------|-----|
| `web_search` | 网页搜索 | Perplexity API |
| `web_fetch` | 网页内容提取 | 内置 |
| `tavily` | AI 优化搜索 | Tavily API |
| `multi-search-engine` | 多引擎搜索 | 17 个搜索引擎（无需 API） |

#### 数据处理工具

| 工具 | 功能 |
|------|------|
| `feishu_doc` | Feishu 文档操作 |
| `feishu_drive` | Feishu 云存储操作 |
| `feishu_wiki` | Feishu 知识库操作 |
| `feishu_chat` | Feishu 聊天操作 |
| `feishu_bitable_*` | Feishu 飞书多维表格操作 |
| `feishu_app_scopes` | 应用权限管理 |

### 2.2 工具使用示例

#### 文件操作

```python
# 读取文件
read({"path": "README.md"})

# 创建文件
write({
  "path": "test.md",
  "content": "# Hello World"
})

# 编辑文件
edit({
  "path": "test.md",
  "oldText": "# Hello World",
  "newText": "# Hello OpenClaw"
})

# 执行命令
exec({
  "command": "ls -la",
  "workdir": "/home/claw/.openclaw/workspace"
})
```

#### 浏览器控制

```python
# 打开网页
browser({
  "action": "open",
  "targetUrl": "https://example.com"
})

# 截图
browser({
  "action": "screenshot",
  "fullPage": True
})

# 点击元素
browser({
  "action": "act",
  "kind": "click",
  "ref": "e123"
})
```

#### 网络搜索

```python
# 网页搜索
web_search({
  "query": "OpenClaw 官方文档",
  "count": 5
})

# 内容提取
web_fetch({
  "url": "https://example.com/article",
  "extractMode": "markdown"
})
```

---

## 3. 技能系统 (Skills)

### 3.1 Skills 概述

Skills 是 OpenClaw 的工具扩展，提供特定功能。

#### Skills 特点

1. **模块化**：每个 Skill 是一个独立的包
2. **可扩展**：用户可以创建自己的 Skills
3. **标准化**：通过 SKILL.md 定义功能和配置
4. **可组合**：多个 Skills 可以协同工作

#### Skills 存储位置

```
~/.openclaw/skills/
├── stock-analysis/          # 股票分析
├── hexo-blog/              # Hexo 博客管理
├── tavily-search/          # Tavily 搜索
├── multi-search-engine/    # 多引擎搜索
├── email-sender/           # 邮件发送
├── task-tracker/           # 任务追踪
├── proactive-agent/        # 主动代理
├── subagent-network-call/  # 御坂网络调用
├── xiaohongshu-ops-skill/  # 小红书运营
├── self-improving-agent/   # 自我改进
├── skill-vetter/           # 技能审查
├── skill-creator/          # 技能创建
├── healthcheck/            # 安全加固
├── morning-briefing/       # 晨间简报
└── feishu-*                # Feishu 集成
```

### 3.2 常用 Skills 详解

#### 3.2.1 Task Tracker（任务追踪）

**作用**：复杂任务拆解和进度跟踪

**功能**：
- 任务拆解为可执行步骤
- 持久化存储到 `workspace/memory/tasks/`
- 会话重启后恢复任务状态
- 自动检查待办清单

**文件格式**：
```markdown
# 任务：OpenClaw 博客系列

- **任务 ID**: openclaw-blog-series
- **创建时间**: 2026-03-07T10:00:00Z
- **状态**: active
- **优先级**: high

## 步骤清单

- [ ] 步骤 1: 规划文章大纲
- [x] 步骤 2: 撰写 SP1: 架构全景 (完成于：2026-03-07T11:30)
- [ ] 步骤 3: 撰写 SP2: Agent 生命周期
```

#### 3.2.2 Proactive Agent（主动代理）

**作用**：让 AI 从任务执行者变成主动伙伴

**核心功能**：
- **WAL 协议**：Write-Ahead Logging 记录关键信息
- **工作缓冲区**：在上下文危险区记录所有交互
- **自主定时任务**：独立于主会话执行后台任务
- **持续改进模式**：从每次交互中学习

**三层记忆架构**：
1. **会话记忆**：当前会话的上下文（临时）
2. **任务记忆**：任务计划文件（任务期间）
3. **长期记忆**：MEMORY.md、每日日志（永久）

#### 3.2.3 Multi Search Engine（多引擎搜索）

**作用**：集成 17 个搜索引擎（8 个中文 + 9 个英文）

**支持功能**：
- 高级搜索操作符（site:, filetype:, 等）
- 时间筛选
- 站点搜索
- 隐私搜索引擎（DuckDuckGo, Brave, Startpage）
- WolframAlpha 知识查询

**无需 API 密钥**，完全免费。

#### 3.2.4 Morning Briefing（晨间简报）

**作用**：自动生成每日晨报

**功能**：
- 天气信息查询
- 日历事件读取
- 待办事项汇总
- 新闻摘要
- 通过飞书/微信推送

**配置方式**：
```bash
# 创建定时任务
python3 skills/morning-briefing/scripts/create_cron.py "0 8 * * *"

# 生成简报
python3 skills/morning-briefing/scripts/morning_brief.py
```

#### 3.2.5 Subagent Network Call（御坂网络调用）

**作用**：根据任务类型自动调用对应的子代理执行

**身份结构**：
- **御坂美琴一号**：核心中枢，负责调度和监控
- **御坂妹妹 10-16 号**：6 名专业子代理
  - 10 号：通用代理
  - 11 号：代码执行者
  - 12 号：内容创作者
  - 13 号：研究分析师
  - 14 号：文件管理器
  - 15 号：系统管理员
  - 16 号：网络爬虫

**调用方式**：
```python
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",
  mode: "run",
  task: "编写一个 Python 脚本"
})
```

### 3.3 Skill 开发

#### Skill 目录结构

```
~/.openclaw/skills/my-skill/
├── SKILL.md              # Skill 定义（必需）
├── README.md             # 使用说明
├── scripts/              # 脚本文件
├── references/           # 参考文档
├── config/               # 配置文件
└── examples/             # 使用示例
```

#### SKILL.md 格式

```yaml
---
name: my-skill
description: "Skill 描述"
version: "1.0.0"
---

# Skill 标题

## 功能描述

...

## 配置

...

## 使用示例

...
```

#### 创建新 Skill

```bash
# 使用 skill-creator 工具
openclaw skill create my-skill

# 手动创建
mkdir -p ~/.openclaw/skills/my-skill/scripts
cd ~/.openclaw/skills/my-skill
touch SKILL.md README.md scripts/
```

---

## 4. 会话和子代理机制

### 4.1 会话（Session）

Session 是 OpenClaw 的**有状态会话容器**，管理用户与 AI 的完整对话历史。

#### Session 生命周期

```
创建 → 运行中 → 压缩 → 结束/归档
```

#### Context 管理

**挑战**：大模型有 token 限制，无法无限保留历史。

**解决方案**：**Compaction（压缩）**机制
- 当历史消息超过阈值时
- 智能总结和裁剪
- 保留关键信息的同时释放空间

### 4.2 子代理（Subagent）

子代理是 OpenClaw 的**多智能体系统**，允许主代理创建并调度子代理执行特定任务。

#### 子代理架构

```
┌─────────────────────────────────────────────────────────────┐
│                      主 Agent（御坂美琴一号）                  │
│                     职责：任务拆解与调度                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Code Agent│   │ Write Agent│   │Research Agent│
   └──────────┘    └──────────┘    └──────────┘
```

#### 子代理运行模式

```python
# 创建子代理会话
sessions_spawn({
  runtime: "subagent",      # 使用 subagent 运行时
  agentId: "code-executor", # 子代理 ID
  mode: "run",              # run=单次运行，session=持久会话
  label: "task-label",      # 任务标签
  task: "任务描述"
})
```

#### 子代理配置

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

**重启 Gateway**：
```bash
openclaw gateway restart
```

### 4.3 任务调度器

任务调度器负责将任务计划分发给子代理执行。

#### 核心组件

| 组件 | 功能 |
|------|------|
| **任务队列管理器** | 管理任务队列，支持添加、获取、完成状态 |
| **依赖解析器** | 构建依赖图，确定执行顺序（拓扑排序） |
| **任务执行器** | 执行单个任务，处理错误和结果 |

#### 执行流程

```
1. 读取任务计划文件
   → memory/tasks/ACTIVE-<task-id>.md

2. 解析任务步骤
   → 提取每个步骤的 agent_type 和 dependencies

3. 构建依赖图
   → 确定任务执行顺序

4. 按顺序执行任务
   → 无依赖或依赖已完成 → 执行

5. 更新任务状态
   → 写入任务文件

6. 收集执行结果
   → 输出报告
```

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

---

## 5. Feishu 集成

### 5.1 Feishu 工具概览

OpenClaw 提供完整的 Feishu（飞书）集成工具集：

| 工具 | 功能 |
|------|------|
| `feishu_app_scopes` | 查看应用权限 |
| `feishu_doc` | 文档操作（读写、编辑、创建等） |
| `feishu_drive` | 云盘文件管理 |
| `feishu_wiki` | 知识库导航 |
| `feishu_chat` | 聊天操作 |
| `feishu_bitable_*` | 多维表格操作 |

### 5.2 Feishu Doc 操作

**核心操作**：

| 操作 | 描述 |
|------|------|
| `read` | 读取文档内容 |
| `write` | 创建或覆盖文档 |
| `append` | 在文档末尾追加内容 |
| `insert` | 在指定位置插入内容 |
| `create_table` | 创建表格 |
| `upload_image` | 上传图片 |
| `upload_file` | 上传文件 |
| `color_text` | 设置文本颜色 |

**示例**：

```python
# 读取文档
feishu_doc({
  "action": "read",
  "doc_token": "docx_xxxxx"
})

# 创建文档
feishu_doc({
  "action": "create",
  "title": "我的文档",
  "content": "# 标题\n\n内容"
})

# 创建表格
feishu_doc({
  "action": "create_table",
  "row_size": 5,
  "column_size": 3
})
```

### 5.3 Feishu Bitable（多维表格）

**Bitable 是 Feishu 的多维表格工具**，类似 Airtable。

#### 核心操作

| 操作 | 描述 |
|------|------|
| `feishu_bitable_get_meta` | 解析 Bitable URL，获取 app_token 和 table_id |
| `feishu_bitable_list_fields` | 列出所有字段（列） |
| `feishu_bitable_list_records` | 列出所有记录（行） |
| `feishu_bitable_get_record` | 获取单条记录 |
| `feishu_bitable_create_record` | 创建新记录 |
| `feishu_bitable_update_record` | 更新记录 |
| `feishu_bitable_create_app` | 创建新的 Bitable 应用 |
| `feishu_bitable_create_field` | 创建新字段 |

**工作流程**：

1. 获取元数据
```python
feishu_bitable_get_meta({
  "url": "https://feishu.cn/base/xxx?table=yyy"
})
```

2. 列出字段
```python
feishu_bitable_list_fields({
  "app_token": "xxx",
  "table_id": "yyy"
})
```

3. 创建记录
```python
feishu_bitable_create_record({
  "app_token": "xxx",
  "table_id": "yyy",
  "fields": {
    "姓名": "张三",
    "年龄": 25
  }
})
```

### 5.4 Feishu Drive（云盘）

**功能**：
- 列出文件夹内容
- 创建文件夹
- 移动文件
- 删除文件

**示例**：

```python
# 列出文件
feishu_drive({
  "action": "list",
  "folder_token": "folder_xxx"
})

# 创建文件夹
feishu_drive({
  "action": "create_folder",
  "name": "新文件夹",
  "folder_token": "folder_xxx"
})
```

### 5.5 Feishu Wiki（知识库）

**功能**：
- 获取知识空间列表
- 节点操作（创建、移动、重命名）
- 搜索

**示例**：

```python
# 获取知识空间
feishu_wiki({
  "action": "spaces"
})

# 创建节点
feishu_wiki({
  "action": "create",
  "title": "新文档",
  "parent_node_token": "node_xxx"
})
```

### 5.6 Feishu Chat（聊天）

**功能**：
- 获取群成员列表
- 获取群信息

**示例**：

```python
feishu_chat({
  "action": "members",
  "chat_id": "chat_xxx"
})
```

---

## 6. 安全机制和最佳实践

### 6.1 安全机制

#### 6.1.1 沙箱隔离

- **Agent 隔离**：Agent 运行在隔离环境中
- **沙箱策略**：Gateway 执行沙箱策略，管理权限边界
- **限制**：禁止访问系统关键路径（/etc/, /usr/, ~/.ssh/）

#### 6.1.2 权限模型

```
Level 5: 主 Agent - 完全权限
Level 4: 可信子 Agent - 受限系统权限（需要批准）
Level 3: 标准子 Agent - 标准开发权限
Level 2: 受限子 Agent - 严格受限权限
Level 1: 只读子 Agent - 只读访问
```

#### 6.1.3 审计日志

所有操作记录到审计日志：

```json
{
  "timestamp": "2026-03-08T05:30:00Z",
  "agent_id": "code-agent-001",
  "action": "file_write",
  "resource": "~/workspace/project/main.py",
  "result": "allowed"
}
```

### 6.2 最佳实践

#### 6.2.1 记忆管理

**三层记忆架构**：

```
┌─────────────────────────────────────┐
│ Layer 1: 会话记忆（Session Memory）   │
│ - 当前会话上下文                    │
│ - 临时决策和中间结果                │
└─────────────────────────────────────┘
         │
         ▼ 同步关键信息
┌─────────────────────────────────────┐
│ Layer 2: 任务记忆（Task Memory）      │
│ - 任务计划文件                      │
│ - 子代理执行结果                    │
└─────────────────────────────────────┘
         │
         ▼ 同步重要发现
┌─────────────────────────────────────┐
│ Layer 3: 长期记忆（Long-term Memory） │
│ - MEMORY.md                         │
│ - memory/YYYY-MM-DD.md              │
└─────────────────────────────────────┘
```

**最佳实践**：
1. **Write Immediately**：及时写入，上下文最清晰时
2. **WAL Before Responding**：回复前先写入关键信息
3. **Buffer in Danger Zone**：60% 上下文时记录所有交互
4. **Recover from Buffer**：从缓冲区恢复，不询问"我们之前在做什么"
5. **Search Before Giving Up**：尝试所有来源再放弃

#### 6.2.2 安全原则

1. **Private things stay private**：私密信息不泄露
2. **Ask before acting externally**：外部行动前确认
3. **Never send half-baked replies**：不要发送半成品回复
4. **Be careful in group chats**：在群组中不要代表用户说话

#### 6.2.3 技能安装安全

**安装前审查**：
1. 检查来源（是否知名/可信作者）
2. 审查 SKILL.md 中的可疑命令
3. 查找 shell 命令、curl/wget、数据外传模式
4. 当不确定时，询问用户

**警惕**：约 26% 的社区技能包含漏洞。

#### 6.2.4 上下文泄露预防

**发布到共享频道前检查**：
1. 频道中还有谁？
2. 是否正在讨论某人？
3. 是否分享了用户隐私信息？

**如果答案是"是"**：路由到用户直接，不发送到共享频道。

### 6.3 常见错误和解决方案

#### 错误 1：会话间通信受限

**错误信息**：
```
Session send visibility is restricted.
Set tools.sessions.visibility=all to allow cross-agent access.
```

**解决方案**：
```json
{
  "tools": {
    "sessions": {
      "visibility": "all"
    }
  }
}
openclaw gateway restart
```

#### 错误 2：ACP runtime 未配置

**错误信息**：
```
Error: ACP runtime backend is not configured.
Install and enable the acpx runtime plugin.
```

**解决方案**：改用 `runtime: "subagent"` 方式。

#### 错误 3：Cron 环境差异

**问题**：Cron 执行时环境变量和交互式 shell 不同。

**解决方案**：使用绝对路径，显式加载环境。
```python
os.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin'
```

---

## 7. 总结

### 7.1 OpenClaw 核心优势

| 优势 | 说明 |
|------|------|
| **智能网关** | 作为运行时网关，统一管理多个平台和 Agent |
| **模块化设计** | Skills、Channels、Agents 独立可替换 |
| **持久化记忆** | 三层记忆架构，避免会话重启后失忆 |
| **多智能体协作** | 子代理系统，专业分工 |
| **安全隔离** | 沙箱策略、权限模型、审计日志 |
| **可扩展** | 自定义 Skills、Channels |

### 7.2 学习要点回顾

1. **核心架构**：Gateway、Agent、Session、Channel 四大组件
2. **工具系统**：内置工具、网络工具、数据处理工具
3. **技能系统**：模块化、标准化、可扩展
4. **会话与子代理**：有状态容器、多智能体调度
5. **Feishu 集成**：完整工具集，覆盖文档、云盘、知识库、聊天、多维表格
6. **安全机制**：沙箱隔离、权限模型、审计日志

### 7.3 后续学习方向

- **MCP 协议深入**：了解 Model Context Protocol 标准和实现
- **自定义 Skill 开发**：创建自己的 Skills
- **Feishu API 完整使用**：探索更多 API 功能
- **性能优化**：上下文压缩、缓存策略
- **监控与调优**：日志分析、性能监控

---

## 附录

### A. 常用命令参考

```bash
# Gateway 管理
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart

# 配置管理
openclaw config set tools.sessions.visibility all

# 技能管理
openclaw skill create my-skill
openclaw skill list

# 会话管理
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",
  mode: "run"
})
```

### B. 文档参考

| 文档 | 位置 |
|------|------|
| AGENTS.md | 工作空间规则 |
| SOUL.md | 身份认知 |
| USER.md | 用户信息 |
| TOOLS.md | 工具配置 |
| MEMORY.md | 长期记忆 |
| memory/YYYY-MM-DD.md | 每日日志 |
| skills/*/SKILL.md | 技能说明 |

### C. 相关资源

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [MCP 协议文档](https://modelcontextprotocol.io)
- [Feishu 开放平台](https://open.feishu.cn)
- [Hal Stack](https://github.com/halthelobster) - Proactive Agent 作者

---

**文档版本**：1.0.0  
**创建时间**：2026-03-09  
**目的**：为明早 7 点的汇报做准备
