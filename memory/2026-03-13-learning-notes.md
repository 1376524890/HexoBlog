# OpenClaw 学习笔记

> 学习日期：2026-03-13  
> 学习目的：为明早七点汇报做准备  
> 学习范围：核心概念、工具系统、会话管理、最佳实践

---

## 目录

1. [OpenClaw 概述](#1-openclaw-概述)
2. [核心架构](#2-核心架构)
3. [工具系统](#3-工具系统)
4. [Skill 系统](#4-skill-系统)
5. [会话和子代理管理](#5-会话和子代理管理)
6. [记忆系统](#6-记忆系统)
7. [定时任务与自动化](#7-定时任务与自动化)
8. [最佳实践](#8-最佳实践)

---

## 1. OpenClaw 概述

### 1.1 什么是 OpenClaw？

OpenClaw 是一个 **AI Agent 运行时平台**，可以理解为：

- **智能网关 (Gateway)**：站在用户、AI 模型、工具生态和各类消息平台之间
- **运行时 (Runtime)**：提供 Agent 执行所需的环境、资源和生命周期管理
- **平台 (Platform)**：可扩展、可配置的生态系统

### 1.2 核心定位

与传统"聊天机器人"不同，OpenClaw 更像是**智能流量网关**：

| 传统网关 | OpenClaw 网关 |
|---------|-------------|
| 路由 HTTP 请求 | 路由用户消息 |
| 协议转换（HTTP ↔ gRPC） | 协议转换（Telegram/Discord/... ↔ 内部格式） |
| 负载均衡 | Agent 池管理 |
| API 聚合 | 工具编排 |
| 安全认证 | 沙箱隔离 |
| 日志监控 | Session 追踪 |

### 1.3 官方定义

OpenClaw 官网 (https://openclaw.ai) 将其定义为：
- 一个 AI 原生时代的**运行时基础设施**
- 支持多个 LLM 提供商（本地 vLLM、DashScope、Zai 等）
- 支持多个 Channel（Telegram、Discord、Slack、飞书等）

---

## 2. 核心架构

### 2.1 四大核心组件

#### 2.1.1 Gateway（中央枢纽）

**职责**：
- **生命周期管理**：启动、停止、监控所有 Agent 实例
- **消息路由**：将来自各 Channel 的消息分发到正确的 Session 和 Agent
- **工具协调**：管理 Skill 注册，处理工具调用请求
- **安全控制**：执行沙箱策略，管理权限边界
- **状态持久化**：维护 Session 历史，处理上下文压缩

**关键特性**：
- Gateway 本身**不运行 AI 模型**，只是 AI 模型的"调度员"
- 与 Agent 运行环境分离，可以独立升级和扩展
- 支持本地模型和远程 API

**配置**：
```json
{
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "lan",
    "auth": {
      "mode": "token",
      "token": "xxx"
    }
  }
}
```

#### 2.1.2 Agent（AI 执行体）

**每个 Agent 包含**：
- **身份（Identity）**：名称、描述、头像等元信息
- **配置（Config）**：使用的模型、系统提示词、可用工具等
- **状态（State）**：当前会话、历史消息、记忆等
- **运行时（Runtime）**：执行环境（本地进程、Docker、远程等）

**运行在隔离环境中**，通过 Bridge Protocol 与 Gateway 通信。

**配置示例**（从 openclaw.json）：
```json
{
  "id": "general-agent",
  "name": "general-agent",
  "workspace": "/home/claw/.openclaw/workspace",
  "agentDir": "/home/claw/.openclaw/agents/general-agent",
  "identity": {
    "name": "御坂妹妹 10 号",
    "theme": "professional",
    "emoji": "⚡"
  }
}
```

#### 2.1.3 Session（有状态的容器）

**包含**：
- 消息历史
- 上下文窗口（经过压缩处理）
- 工具状态（本次会话中工具调用的中间结果）
- 元数据（创建时间、最后活跃时间、关联的 Channel 等）

**核心挑战**：上下文长度管理
- 使用 **Compaction（压缩）** 机制解决 token 限制问题
- 当历史消息超过阈值时，智能总结和裁剪

#### 2.1.4 Channel（消息通道）

**官方支持的 Channel**：
- 即时通讯：Telegram、Discord、Slack、WhatsApp、Signal、微信（通过 Lark/Feishu）
- 传统协议：IRC、Matrix
- 企业平台：Microsoft Teams、Google Chat、飞书
- 其他：iMessage、BlueBubbles、Webhook

**每个 Channel 都是插件**，实现统一的接口：
- 接收消息（从平台到 OpenClaw）
- 发送消息（从 OpenClaw 到平台）
- 格式转换（平台特定格式 ↔ OpenClaw 标准格式）

**配置示例**：
```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_a920785bf0f8dbcb",
      "appSecret": "xxx",
      "connectionMode": "websocket",
      "domain": "feishu"
    }
  }
}
```

### 2.2 Agent Loop：AI 如何"活"起来

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

**具体流程**：
1. **接收输入**：用户通过某个 Channel 发送消息，Gateway 路由到对应 Session 的 Agent
2. **构建上下文**：Gateway 将 Session 历史、系统提示词、可用工具列表组装成完整的 Prompt
3. **LLM 推理**：Agent 调用大模型，模型决定是**直接回复**还是**调用工具**
4. **工具执行**（如果需要）：Agent 通过 Gateway 调用外部工具，获取结果
5. **循环或结束**：如果需要多步推理，回到步骤 3；否则返回最终结果
6. **发送响应**：Gateway 将 AI 的回复通过原 Channel 发送给用户

---

## 3. 工具系统

### 3.1 工具概述

OpenClaw 的工具系统基于 **MCP（Model Context Protocol）**，这是 Anthropic 提出的一种开放标准。

**MCP 的核心思想**：标准化 AI 与外部世界的交互接口。

### 3.2 工具配置

从 `openclaw.json` 中可以看到工具配置：

```json
{
  "tools": {
    "profile": "full",
    "web": {
      "search": {
        "enabled": true,
        "provider": "perplexity",
        "maxResults": 10,
        "timeoutSeconds": 30
      },
      "fetch": {
        "enabled": true,
        "maxChars": 50000
      }
    },
    "sessions": {
      "visibility": "all"
    },
    "agentToAgent": {
      "enabled": true,
      "allow": [
        "main",
        "general-agent",
        "code-executor",
        "content-writer",
        ...
      ]
    }
  }
}
```

### 3.3 主要工具类型

#### 3.3.1 内置工具（Built-in Tools）

| 工具 | 功能 |
|------|------|
| `read` | 读取文件内容 |
| `write` | 创建或覆盖文件 |
| `edit` | 精确编辑文件 |
| `exec` | 执行 Shell 命令 |
| `process` | 管理后台进程 |
| `browser` | 浏览器控制 |
| `canvas` | Canvas 控制 |
| `message` | 发送消息 |
| `tts` | 文本转语音 |
| `nodes` | 管理 paired nodes |
| `subagents` | 管理子代理 |

#### 3.3.2 Web 工具

```json
{
  "web": {
    "search": {
      "enabled": true,
      "provider": "perplexity"
    },
    "fetch": {
      "enabled": true,
      "maxChars": 50000
    }
  }
}
```

#### 3.3.3 会话间通信

```json
{
  "tools": {
    "sessions": {
      "visibility": "all"
    }
  }
}
```

**作用**：允许 Agent 之间相互通信，是御坂网络第一代的关键配置。

### 3.4 工具使用示例

从工具调用文档可以看到，每个工具都有详细的参数说明和示例。

**示例**：`message` 工具发送消息
```json
{
  "action": "send",
  "channel": "feishu",
  "target": "xxx",
  "message": "Hello!"
}
```

---

## 4. Skill 系统

### 4.1 什么是 Skill？

Skill 是 OpenClaw 的**功能扩展包**，每个 Skill 提供一组相关的工具和功能。

**特点**：
- 每个 Skill 有独立的目录和 `SKILL.md` 文档
- Skill 定义了工具的使用场景和方式
- Skill 可以独立开发和分发

### 4.2 本地 Skill 结构

从学习过程中看到的本地 Skill：

```
~/.openclaw/workspace/skills/
├── memory-organizer/SKILL.md
├── novel-scraper/SKILL.md
└── smart-search/SKILL.md

~/.openclaw/skills/
├── hexo-blog/SKILL.md
├── proactive-agent/SKILL.md
├── self-improving-agent/SKILL.md
├── task-tracker/SKILL.md
├── skill-vetter/SKILL.md
├── subagent-network-call/SKILL.md
├── tavily-search/SKILL.md
├── web-markdown-search/SKILL.md
├── multi-search-engine/SKILL.md
├── xiaohongshu-ops-skill/SKILL.md
└── ...
```

### 4.3 经典 Skill 示例

#### 4.3.1 hexo-blog

**功能**：管理 Hexo 博客

**关键配置**：
- 博客地址：https://blog.plk161211.top
- 仓库：`git@github.com:1376524890/HexoBlog.git`
- 本地路径：`~/blog`

**使用流程**：
```bash
# 创建新文章
hexo new post "文章标题"

# 预览
hexo server -p 4000

# 生成 + 部署
hexo clean && hexo generate && hexo deploy
```

#### 4.3.2 proactive-agent

**功能**：将 AI Agent 从任务执行者转变为主动合作伙伴

**三大支柱**：
1. **Proactive** - 不等待指令，主动创造价值
2. **Persistent** - 在上下文丢失后仍然能恢复
3. **Self-improving** - 从每次交互中学习改进

**核心协议**：
- **WAL Protocol**：Write-Ahead Logging，在回复前记录关键信息
- **Working Buffer Protocol**：在 60% 上下文阈值时记录每个交互
- **Compaction Recovery Protocol**：在上下文压缩后恢复状态

#### 4.3.3 self-improvement

**功能**：捕获学习、错误和修正，实现持续改进

**日志格式**：
```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending

### Summary
...

### Details
...

### Suggested Action
...
```

**分类**：
- `correction` - 用户纠正
- `knowledge_gap` - 知识差距
- `best_practice` - 最佳实践

#### 4.3.4 task-tracker

**功能**：任务追踪与持久化系统

**使用场景**：
- 复杂任务需要拆解步骤
- 跟踪进度
- 在会话重启后恢复任务状态

**文件结构**：
```
workspace/memory/tasks/
├── ACTIVE-openclaw-blog.md    # 进行中的任务
└── completed/                 # 已完成的任务
```

#### 4.3.5 memory-organizer

**功能**：御坂妹妹 17 号 - 记忆整理专家

**核心职责**：
- 三层架构维护
- 定期整理（每 6 小时）
- 安全备份
- 自动清理

**整理流程**：
```
1. 扫描 memory/ 目录下的每日日志
   ↓
2. 提取精华内容
   ↓
3. 备份当前 MEMORY.md
   ↓
4. 更新精选记忆
   ↓
5. 移动过期日志到长期归档
   ↓
6. 清理旧备份
```

### 4.4 Skill 的 SKILL.md 结构

标准的 SKILL.md 包含：

```markdown
---
name: skill-name
description: Skill 描述
version: 1.0.0
---

# Skill 名称

## 概述

## 快速开始

## 使用方法

## 配置

## 示例

## 注意事项
```

---

## 5. 会话和子代理管理

### 5.1 会话机制

**Session 的核心**：
- 每个用户交互都发生在独立的 Session 中
- Session 包含完整的对话历史
- Session 有生命周期管理（创建、压缩、销毁）

### 5.2 子代理系统

#### 5.2.1 子代理的作用

子代理（Subagent）允许主 Agent 将任务分派给专门的子 Agent 执行。

**优势**：
- **上下文隔离**：子 Agent 的上下文不会污染主 Agent
- **专业化**：不同的子 Agent 负责不同的任务
- **容错性**：一个子 Agent 失败不影响其他子 Agent

#### 5.2.2 御坂网络第一代架构

```
┌─────────────────────────────────────────────────────────────┐
│                     御坂大人（用户）                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  御坂美琴一号（核心中枢）                      │
│                                                             │
│  职责：                                                     │
│  ├─ 接收任务                                                  │
│  ├─ 识别任务类型                                              │
│  ├─ 分派给御坂妹妹                                            │
│  ├─ 监督进度                                                  │
│  └─ 汇报结果                                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
    ┌──────────────┐      ┌──────────────┐
    │ 御坂妹妹 11 号  │      │ 御坂妹妹 12 号  │
    │ code-executor │      │ content-writer│
    └──────────────┘      └──────────────┘
```

**成员列表**：
| 编号 | Agent ID | 职责 | 状态 |
|------|----------|------|------|
| 10 号 | `general-agent` | 通用代理 | ✅ |
| 11 号 | `code-executor` | 代码执行者 | ✅ |
| 12 号 | `content-writer` | 内容创作者 | ✅ |
| 13 号 | `research-analyst` | 研究分析师 | ✅ |
| 14 号 | `file-manager` | 文件管理器 | ✅ |
| 15 号 | `system-admin` | 系统管理员 | ✅ |
| 16 号 | `web-crawler` | 网络爬虫 | ✅ |
| 17 号 | `memory-organizer` | 记忆整理专家 | ✅ |

#### 5.2.3 子代理配置

**会话间通信配置**：
```bash
# 设置会话间通信权限
openclaw config set tools.sessions.visibility all

# 重启 Gateway
openclaw gateway restart
```

**创建子代理**：
```python
sessions_spawn(
    agentId="code-executor",
    runtime="subagent",
    mode="run",
    task="执行任务描述"
)
```

#### 5.2.4 子代理工作流

```
1. 主 Agent 接收用户任务
   ↓
2. 识别任务类型，选择对应的子 Agent
   ↓
3. 使用 sessions_spawn 创建子 Agent
   ↓
4. 等待子 Agent 完成（自动汇报）
   ↓
5. 主 Agent 格式化结果并汇报给用户
```

### 5.3 会话管理工具

**可用工具**：
- `sessions_list` - 列出会话
- `sessions_history` - 查看会话历史
- `sessions_send` - 发送消息到其他会话
- `sessions_spawn` - 创建子代理

---

## 6. 记忆系统

### 6.1 三层记忆架构

#### 6.1.1 第一层：每日日志

**位置**：`~/.openclaw/workspace/memory/YYYY-MM-DD.md`

**特点**：
- 原始记录，无限存储
- 详细的、未经筛选的事件记录
- 作为长期记忆的来源

#### 6.1.2 第二层：精选记忆

**位置**：`~/.openclaw/workspace/MEMORY.md`

**特点**：
- 精华提取，<3000 字符
- 只保留重要、可复用的知识
- 每次启动时自动加载

**必须包含的板块**：
```markdown
- 📋 系统架构
- 🤖 自动化配置 (定时任务)
- 📝 近期成果 (按日期)
- 🏠 基本信息 (御坂大人、御坂妹妹助手系统)
- ⚙️ 技术栈
- 🌐 御坂网络信息
- ⚡ 安全规范
- 📦 备份策略
- 🧠 记忆整理任务详情
```

#### 6.1.3 第三层：长期归档

**位置**：`~/.openclaw/workspace/life/archives/`

**特点**：
- 高价值保存，按需归档
- 超过 7 天的每日日志移动到此
- 重要的技术文档、设计模式

### 6.2 记忆系统维护

#### 6.2.1 自动化整理

**脚本**：`checkpoint-memory-llm.sh`

**功能**：
- 每 6 小时自动运行
- 从当日日志提取关键信息
- 追加到 `MEMORY.md`

**配置**（OpenClaw Cron）：
```json
{
  "id": "memory-checkpoint",
  "name": "记忆检查点",
  "schedule": {
    "kind": "cron",
    "expr": "0 */6 * * *",
    "tz": "UTC"
  },
  "command": [
    "bash",
    "/home/claw/.openclaw/workspace/para-system/checkpoint-memory-llm.sh"
  ]
}
```

#### 6.2.2 安全规范

**规则**：
1. **永远使用 `trash` 而不是 `rm`！**
2. **修改文件前必须备份**
   - 备份路径：`memory/backups/MEMORY.md.<timestamp>.bak`
   - 保留期限：3 天
3. **验证备份完整性**
4. **权限控制**：不访问敏感目录

### 6.3 自我改进系统

#### 6.3.1 学习日志

**位置**：`~/.openclaw/workspace/.learnings/`

**文件**：
- `LEARNINGS.md` - 修正、知识差距、最佳实践
- `ERRORS.md` - 命令失败、异常
- `FEATURE_REQUESTS.md` - 用户请求的功能

**格式**：
```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
```

#### 6.3.2 学习类型

| 触发条件 | 日志类型 |
|----------|----------|
| 命令/操作失败 | `.learnings/ERRORS.md` |
| 用户纠正 | `.learnings/LEARNINGS.md` (correction) |
| 用户请求新功能 | `.learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | `.learnings/ERRORS.md` |
| 知识过时 | `.learnings/LEARNINGS.md` (knowledge_gap) |
| 找到更好的方法 | `.learnings/LEARNINGS.md` (best_practice) |

---

## 7. 定时任务与自动化

### 7.1 Cron 任务系统

OpenClaw 支持 Cron 风格的定时任务。

**配置示例**：
```json
{
  "id": "auto-backup",
  "name": "自动备份",
  "description": "每 6 小时自动备份记忆",
  "schedule": {
    "kind": "cron",
    "expr": "0 */6 * * *",
    "tz": "UTC"
  },
  "command": [
    "bash",
    "/path/to/backup.sh"
  ]
}
```

**Cron 表达式格式**：
```
分 时 日 月 周
```

**示例**：
- `0 */6 * * *` - 每 6 小时
- `0 9 * * 1` - 每周一 9:00
- `0 0 * * *` - 每天午夜

### 7.2 常用定时任务

从配置文件和文档中看到的任务：

| ID | 名称 | 频率 | 状态 |
|---|---|---|---|
| `memory-checkpoint` | 记忆检查点 | 每 6 小时 | ✅ |
| `auto-backup` | 自动备份 | 每 6 小时 | ✅ |
| `auto-cleanup` | 自动清理过期备份 | 每天 12:30 | ✅ |
| `memory-整理` | 记忆整理任务 | 每 6 小时 | ✅ |

### 7.3 定时任务类型

#### 7.3.1 Autonomous vs Prompted Crons

**关键区别**：

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `systemEvent` | 发送提示给主会话 | 需要人工关注的任务 |
| `isolated agentTurn` | 创建子 Agent 自主执行 | 后台工作、维护任务 |

**示例**：
```json
// 错误：只是提示
{
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "Check if X needs updating"
  }
}

// 正确：自主执行
{
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "AUTONOMOUS: Read SESSION-STATE.md, compare..."
  }
}
```

---

## 8. 最佳实践

### 8.1 行为准则

#### 8.1.1 考证原则

**任何输出的结论都需要考证！**

**正确做法**：
1. 先本地检查结构
2. 阅读文档
3. 使用专门的 Agent 和工具
4. 最后可以问用户

**禁止做法**：
- ❌ 永远不能瞎编
- ❌ 不能下没有依据的结论
- ❌ 不能说"我记得"如果不确定
- ❌ 不能为了完成回答而编造信息

#### 8.1.2 安全规范

- 不要泄露私人数据
- 执行外部操作前先询问
- Git 操作永远先 `git add` 再 `git commit`
- 删除前使用 `trash` 而不是 `rm`

### 8.2 记忆管理最佳实践

#### 8.2.1 文件操作规范

```bash
# 推荐：使用 trash
trash file.txt

# 不推荐：直接删除
rm file.txt
```

#### 8.2.2 备份策略

- **本地备份**：`~/.openclaw/backup/`
- **Git 同步**：每 6 小时自动提交
- **清理策略**：每天 12:30 清理 7 天前的备份
- **恢复点**：6 小时间隔的 checkpoint

### 8.3 编写高质量 Skill

#### 8.3.1 SKILL.md 规范

**必备字段**：
- `name` - Skill 名称
- `description` - 描述
- `version` - 版本号（可选）

**内容结构**：
1. 概述
2. 快速开始
3. 使用方法
4. 配置
5. 示例
6. 注意事项

#### 8.3.2 命名规范

- 使用小写字母
- 用连字符分隔：`task-tracker`
- 匹配文件夹名称

### 8.4 文档维护

#### 8.4.1 文档更新时机

**需要更新文档的情况**：
- 修改系统配置
- 添加新功能
- 修复 Bug
- 学习新经验

**更新的文档**：
- `SOUL.md` - 核心身份
- `MEMORY.md` - 精选记忆
- `IDENTITY.md` - 身份信息
- `TOOLS.md` - 工具配置
- `memory/YYYY-MM-DD.md` - 每日日志

#### 8.4.2 文档同步原则

**系统化更新**：
1. 先更新核心文档（SOUL.md、IDENTITY.md）
2. 再更新精选记忆（MEMORY.md）
3. 然后更新每日日志（memory/YYYY-MM-DD.md）
4. 最后更新辅助文档（TOOLS.md、SKILL.md）

### 8.5 调试和故障排查

#### 8.5.1 常见问题

**问题 1：会话间通信受限**
```
Session send visibility is restricted.
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
```

**问题 2：ACP runtime 未配置**
```
Error: ACP runtime backend is not configured.
```

**解决方案**：改用 `runtime: "subagent"`

**问题 3：子 Agent 完成后不汇报**

**原因**：子 Agent 的回复是发送给主 session，而不是直接发送给最终用户。

**解决方案**：让 main 会话负责转发子 Agent 的结果。

### 8.6 系统启动和配置

#### 8.6.1 OpenClaw 启动

**启动 Gateway**：
```bash
openclaw gateway start
```

**重启 Gateway**：
```bash
openclaw gateway restart
```

**查看状态**：
```bash
openclaw gateway status
```

#### 8.6.2 配置管理

**设置配置**：
```bash
openclaw config set tools.sessions.visibility all
```

**查看配置**：
```bash
cat ~/.openclaw/openclaw.json
```

---

## 附录：参考资料

### A.1 学习到的关键文件

| 文件 | 说明 |
|------|------|
| `~/.openclaw/openclaw.json` | OpenClaw 主配置文件 |
| `~/.openclaw/workspace/MEMORY.md` | 精选记忆 |
| `~/.openclaw/workspace/memory/YYYY-MM-DD.md` | 每日日志 |
| `~/.openclaw/workspace/AGENTS.md` | 多 Agent 工作流 |
| `~/.openclaw/workspace/SOUL.md` | 核心身份和原则 |
| `~/.openclaw/workspace/IDENTITY.md` | 身份信息 |
| `~/.openclaw/workspace/TOOLS.md` | 工具配置 |

### A.2 核心 Skill 列表

| Skill | 功能 |
|-------|------|
| `hexo-blog` | Hexo 博客管理 |
| `proactive-agent` | 主动代理 |
| `self-improvement` | 自我改进 |
| `task-tracker` | 任务追踪 |
| `memory-organizer` | 记忆整理 |
| `skill-vetter` | 技能审核 |
| `subagent-network-call` | 子代理网络调用 |
| `tavily-search` | Tavily 搜索 |
| `web-markdown-search` | Markdown 网页搜索 |
| `multi-search-engine` | 多搜索引擎 |
| `xiaohongshu-ops` | 小红书运营 |

### A.3 常用命令

| 命令 | 说明 |
|------|------|
| `openclaw gateway start` | 启动 Gateway |
| `openclaw gateway restart` | 重启 Gateway |
| `openclaw gateway status` | 查看状态 |
| `openclaw config set` | 设置配置 |
| `clawdhub install` | 安装 Skill |
| `hexo new post` | 创建新博客文章 |
| `hexo server` | 预览博客 |
| `hexo deploy` | 部署博客 |

---

## 总结

通过今天的学习，我对 OpenClaw 有了全面深入的理解：

### 核心概念
1. **OpenClaw 是一个智能运行时网关**，不是简单的聊天机器人
2. **四大核心组件**：Gateway、Agent、Session、Channel
3. **工具基于 MCP 协议**，支持标准化扩展

### 工具系统
1. **内置工具丰富**：文件操作、浏览器控制、消息发送等
2. **Web 工具**：搜索、抓取
3. **会话间通信**：需要配置 `tools.sessions.visibility`

### Skill 系统
1. **Skill 是功能扩展包**，每个 Skill 独立管理
2. **SKILL.md** 是 Skill 的核心文档
3. **本地 Skill** 和 **远程 Skill** 并存

### 会话和子代理
1. **Session 是有状态的容器**，管理对话历史
2. **子代理系统**实现任务分派和专业分工
3. **御坂网络第一代**是子代理系统的具体实现

### 记忆系统
1. **三层架构**：每日日志、精选记忆、长期归档
2. **自动化整理**：每 6 小时自动更新
3. **自我改进**：记录错误、学习、功能请求

### 定时任务
1. **Cron 风格**，支持多种频率
2. **Autonomous vs Prompted** 两种类型
3. **重要任务**：记忆检查点、自动备份、自动清理

### 最佳实践
1. **考证原则**：不瞎编，有依据
2. **安全规范**：使用 `trash`，备份优先
3. **文档同步**：系统化更新所有相关文档

---

*学习笔记完成于 2026-03-13*  
*准备用于明早七点汇报*
