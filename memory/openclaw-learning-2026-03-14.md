# OpenClaw 知识学习总结 ⚡

**学习时间**: 2026 年 3 月 14 日 (Asia/Shanghai)  
**学习方式**: 只学习，不实践  
**目的**: 为明早 7 点汇报做准备  
**整理者**: 御坂妹妹 13 号 (research-analyst)  
**状态**: ✅ **学习完成**

---

## 📚 一、OpenClaw 是什么

### 1.1 核心定义

**OpenClaw** 是一个 **AI Agent 运行时平台**，核心是**智能网关（Runtime Gateway）**。

> 🎯 **关键区分**：它**不是聊天机器人**，而是把 AI 模型连接到真实世界的桥梁！

#### 与 ChatGPT 的对比

| 对比项 | ChatGPT | OpenClaw |
|--------|---------|----------|
| **定位** | 聊天机器人 | Agent 运行时平台 |
| **能力** | 生成文本 | 真正执行任务 |
| **记忆** | 会话内临时 | 持久化到磁盘文件 |
| **工具** | API 调用有限 | 文件系统、命令执行、浏览器控制等 |
| **部署** | 云端 SaaS | 本地部署，数据私有 |
| **安全性** | 受限于平台 | 多层次安全控制，审计完善 |

### 1.2 四大核心理念 ⭐⭐⭐⭐⭐

1. **Access control before intelligence**（访问控制先于智能）
   - 这是 OpenClaw **最重要**的设计原则
   - AI 模型可以很聪明，但如果没有权限控制，会非常危险
   - 必须先定义"谁能做什么"，再考虑"能做多聪明"

2. **隐私优先：私有数据保持私有**
   - 所有数据本地存储
   - 支持自托管部署
   - 不上传用户数据到云端
   - 数据控制权完全在用户手中

3. **记忆即文件**
   - 记忆系统：纯 Markdown 文件
   - 易于编辑和版本控制
   - 支持向量检索和混合搜索
   - 自动压缩，临近 token 上限时自动整理

4. **工具优先**
   - 第一类工具而非 skill 包裹
   - 真正能执行任务，不只是生成文本

---

## 🏗️ 二、核心架构

### 2.1 三层架构

```
┌─────────────────────────────────────────────────────────┐
│              Agent Layer（智能层）                        │
│  - Main Agent（主 Agent）                                │
│  - Subagents（子代理）                                   │
│  - ACP Agents（编码代理）                                │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           Gateway Layer（网关层）← 大脑！                  │
│  - 控制平面、策略层、路由                                │
│  - 身份认证、工具策略、会话管理                          │
│  - 频道适配器（Discord/WhatsApp/飞书等）                 │
│  ⚠️ Gateway 本身不运行 AI 模型，只是调度员                  │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Node Layer（节点层）← 手脚                   │
│  - 远程执行表面                                          │
│  - 设备能力（摄像头、屏幕、通知、位置）                  │
│  - macOS companion app                                   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书等 |

### 2.3 Session（会话）概念

Session 是 OpenClaw 的**有状态会话容器**：

- **Session key 格式**: `agent:<agentId>:<mainKey>`
  - 主会话：`agent:main:main`（默认 `main`）
  - DM 会话：`agent:<agentId>:<channel>:peer:<peerId>`
  - 群组会话：`agent:<agentId>:<channel>:group:<id>`

- **Session 类型**:
  - `main` - 主会话（直接聊天）
  - `subagent` - 子代理（后台运行）
  - `acp` - ACP 编码代理

- **上下文窗口管理**:
  - 每个 session 有自己的对话历史
  - **Compaction（压缩）**: 当接近上下文限制时自动总结旧消息
  - 手动触发：`/compact "专注于决策和待办事项"`

- **DM 隔离策略**:
  - `pairing` - 需要配对（推荐）
  - `per-peer` - 按发送者隔离
  - `per-channel-peer` - 按通道 + 发送者隔离（推荐）
  - `per-account-channel-peer` - 多账户场景

### 2.4 Context 与 Compaction

#### Context（上下文）
**上下文 = 发送给模型的所有内容**

**包含内容**:
- 系统提示：OpenClaw 构建，包含工具列表、技能、时间、运行时信息
- 对话历史：用户的消息 + 助手的回复
- 工具调用/结果：命令输出、文件读取、图片等
- 限制：受模型的上下文窗口限制（token 限制）

**System Prompt 结构**:
```
- Tooling: 工具列表 + 描述
- Safety: 安全规则提醒
- Skills: 可用技能指引
- Workspace: 工作目录
- Documentation: 文档路径
- Current Date & Time: 时间
- Runtime: 运行时信息
```

#### Compaction（压缩）
**当会话接近上下文窗口限制时，自动压缩历史**

- **方式**:
  - 自动压缩：接近窗口限制时触发
  - 手动压缩：`/compact` 命令
- **过程**:
  1. 总结旧对话为压缩条目
  2. 保留最近的消息
  3. 将压缩结果持久化到 JSONL
- **配置**:
  ```json
  {
    "agents": {
      "defaults": {
        "compaction": {
          "mode": "safeguard",
          "reserveTokensFloor": 24000
        }
      }
    }
  }
  ```

---

## 🛠️ 三、工具系统

### 3.1 工具分类（8 大分类）

| 分类 | 工具 | 功能 |
|------|------|------|
| **Runtime** | `exec`, `process`, `gateway` | 命令执行、进程管理、网关控制 |
| **Filesystem** | `read`, `write`, `edit`, `apply_patch` | 文件操作 |
| **Session** | `sessions_list`, `sessions_spawn`, `sessions_history` | 会话管理 |
| **Memory** | `memory_search`, `memory_get` | 记忆检索 |
| **Web** | `web_search`, `web_fetch`, `tavily` | 网络搜索、内容抓取 |
| **UI** | `browser`, `canvas` | 浏览器控制、Canvas 渲染 |
| **Node** | `nodes` | 设备控制（相机/屏幕/通知/位置）|
| **Messaging** | `message` | 跨平台发消息 |

### 3.2 核心工具详解

#### 文件系统工具
```python
# 读取文件
read({"path": "README.md"})

# 创建/覆盖文件
write({
  "path": "test.md",
  "content": "# Hello World"
})

# 编辑文件（精确替换）
edit({
  "path": "test.md",
  "oldText": "# Hello World",
  "newText": "# Hello OpenClaw"
})
```

#### 命令执行工具
```python
# 执行命令
exec({
  "command": "ls -la",
  "workdir": "/home/claw/.openclaw/workspace"
})

# 管理后台进程
process({
  "action": "poll",
  "sessionId": "xxx"
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

#### 网络工具
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

### 3.3 工具安全策略

#### 工具 Profile

- `minimal` - 只有 `session_status`
- `coding` - 文件系统 + 运行时 + 记忆
- `messaging` - 消息相关工具
- `full` - 无限制

#### 工具组（Shorthands）
- `group:runtime` - exec/bash/process
- `group:fs` - read/write/edit
- `group:sessions` - 会话管理
- `group:memory` - 记忆工具
- `group:web` - 网络搜索
- `group:ui` - 浏览器/canvas
- `group:messaging` - 消息工具
- `group:nodes` - 节点控制

#### 安全控制选项
- `tools.allow` / `tools.deny` - 允许/拒绝工具
- `sandbox` - 沙箱隔离
- `elevated` - 提权执行（需显式启用）
- `ask: always` - 高风险操作需确认
- `workspaceOnly` - 限制文件系统操作范围

### 3.4 Feishu 集成工具

| 工具 | 功能 |
|------|------|
| `feishu_doc` | 文档操作（读写、编辑、创建表格、上传文件等）|
| `feishu_drive` | 云盘文件管理（列表、创建、移动、删除）|
| `feishu_wiki` | 知识库导航（空间、节点、搜索）|
| `feishu_chat` | 聊天操作（成员、信息）|
| `feishu_bitable_*` | 多维表格操作（增删改查、字段管理）|
| `feishu_app_scopes` | 应用权限管理 |

---

## 🔐 四、安全模型

### 4.1 安全核心原则

1. **身份优先**：谁可以调用工具
2. **作用域次之**：工具在哪里可以执行
3. **模型最后**：假设模型可能被操纵

### 4.2 信任边界

- OpenClaw 假设**单一用户信任边界** per Gateway
- 不支持敌对多租户
- 如需隔离需分 Gateway/OS User/Host
- **Gateway 和 Node 属于同一信任域**

### 4.3 权限层级

| 级别 | 说明 | 适用对象 |
|------|------|----------|
| Level 5 | 主 Agent - 完全权限 | 主会话 |
| Level 4 | 可信子 Agent - 受限系统权限 | 需批准 |
| Level 3 | 标准子 Agent - 标准开发权限 | 开发代理 |
| Level 2 | 受限子 Agent - 严格受限权限 | 通用代理 |
| Level 1 | 只读子 Agent - 只读访问 | 读取代理 |

### 4.4 安全审计命令

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

**常见风险检查项**:
| 检查项 | 严重性 | 修复方法 |
|--------|--------|----------|
| `fs.state_dir.perms_world_writable` | 严重 | 修复 `~/.openclaw` 权限 |
| `gateway.bind_no_auth` | 严重 | 设置 `gateway.auth` |
| `gateway.tailscale_funnel` | 严重 | 禁用 public funnel |
| `security.exposure.open_groups_with_elevated` | 严重 | 关闭开放群组 + 高级工具 |

### 4.5 加固基线配置

```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "replace-with-long-random-token"
    }
  },
  "session": { "dmScope": "per-channel-peer" },
  "tools": {
    "profile": "messaging",
    "deny": ["group:automation", "group:runtime", "group:fs"],
    "fs": { "workspaceOnly": true },
    "exec": { "security": "deny", "ask": "always" },
    "elevated": { "enabled": false }
  }
}
```

---

## 🧠 五、记忆系统

### 5.1 三层记忆架构

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

### 5.2 记忆文件结构

```
~/workspace/
├── MEMORY.md              # 长期记忆（精选）
└── memory/
    ├── 2026-03-14.md      # 今日日志
    ├── 2026-03-13.md      # 昨日日志
    ├── backups/
    │   └── MEMORY.md.*.bak # 备份文件
    └── tasks/             # 任务记录
```

**记忆工具**:
- `memory_search` - 语义检索
- `memory_get` - 读取特定文件

### 5.3 记忆管理最佳实践

1. **DECIDE to write**: 决定、偏好、持久事实 → MEMORY.md
2. **Daily notes**: 日常记录 → memory/YYYY-MM-DD.md
3. **定期 review**: 定期清理 MEMORY.md，移除过时信息
4. **Ask to remember**: 重要事项明确让 Agent 写入记忆

### 5.4 安全操作规则 ⭐⭐⭐

- ✅ **使用 `trash` 而不是 `rm`**：可恢复，避免永久删除
- ✅ **操作前备份**：修改 MEMORY.md 前自动备份
- ✅ **检查 Git 状态**：操作前确认 `git status`
- ✅ **立即提交**：操作后 `git add` 和 `git commit`
- ✅ **安全检查**：运行 `python3 scripts/safety-check-memory.py`

---

## 🤖 六、技能系统 (Skills)

### 6.1 什么是 Skill？

Skill 是**专用任务的能力模块**，提供：
- 特定领域的操作指导
- 工具调用最佳实践
- 领域知识和约束

### 6.2 技能存储位置

```
~/.openclaw/skills/
├── feishu-doc/           # Feishu 文档操作
├── feishu-drive/         # Feishu 云存储管理
├── feishu-perm/          # Feishu 权限管理
├── feishu-wiki/          # Feishu 知识库
├── hexo-blog/            # Hexo 博客管理
├── task-tracker/         # 任务追踪与持久化
├── weather/              # 天气查询
├── multi-search-engine/  # 多引擎搜索
├── proactive-agent/      # 主动代理
├── self-improving-agent/ # 自我改进
├── skill-vetter/         # 技能安全审查
├── skill-creator/        # 技能创建工具
├── subagent-network-call/# 御坂网络调用
└── xiaohongshu-ops-skill/ # 小红书运营
```

### 6.3 常用 Skill 详解

#### task-tracker（任务追踪）
**作用**：复杂任务拆解和进度跟踪

**功能**:
- 任务拆解为可执行步骤
- 持久化存储到 `workspace/memory/tasks/`
- 会话重启后恢复任务状态
- 自动检查待办清单

**文件格式**:
```yaml
# memory/tasks/ACTIVE-example-task.md
steps:
  - step_id: 1
    title: "设计数据库 Schema"
    agent_type: "code-executor"
    dependencies: []
```

#### proactive-agent（主动代理）
**作用**：让 AI 从任务执行者变成主动伙伴

**核心功能**:
- **WAL 协议**：Write-Ahead Logging 记录关键信息
- **工作缓冲区**：在上下文危险区记录所有交互
- **自主定时任务**：独立于主会话执行后台任务
- **持续改进模式**：从每次交互中学习

#### multi-search-engine（多引擎搜索）
**作用**：集成 17 个搜索引擎（8 个中文 + 9 个英文）

**支持功能**:
- 高级搜索操作符（site:, filetype:, 等）
- 时间筛选
- 站点搜索
- 隐私搜索引擎（DuckDuckGo, Brave, Startpage）
- WolframAlpha 知识查询

**无需 API 密钥**，完全免费。

### 6.4 Skill 开发

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

---

## 🔄 七、会话和子代理机制

### 7.1 子代理（Subagent）

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

#### 子代理启动方式

**工具方式**（推荐）:
```python
sessions_spawn({
  runtime: "subagent",      # 使用 subagent 运行时
  agentId: "code-executor", # 子代理 ID
  mode: "run",              # run=单次运行，session=持久会话
  label: "task-label",      # 任务标签
  task: "任务描述"
})
```

**Slash 命令**:
```bash
/subagents spawn <agentId> <task>
/subagents list
/subagents kill <id>
/subagents log <id>
/subagents steer <id> <msg>
```

### 7.2 御坂网络第一代（多智能体系统）

**核心架构**:
```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

| 编号 | 名称 | Agent ID | 职责 | 权限等级 |
|------|------|----------|------|----------|
| 10 号 | 御坂妹妹 10 号 | `general-agent` | 通用代理，处理琐碎问题 | Level 2 |
| 11 号 | 御坂妹妹 11 号 | `code-executor` | 代码执行者 | Level 3 |
| 12 号 | 御坂妹妹 12 号 | `content-writer` | 内容创作者 | Level 3 |
| 13 号 | 御坂妹妹 13 号 | `research-analyst` | 研究分析师 | Level 3 |
| 14 号 | 御坂妹妹 14 号 | `file-manager` | 文件管理器 | Level 2 |
| 15 号 | 御坂妹妹 15 号 | `system-admin` | 系统管理员 | Level 4 |
| 17 号 | 御坂妹妹 17 号 | `memory-organizer` | 记忆整理专家 | Level 3 |

---

## ⚙️ 八、配置系统

### 8.1 配置文件

**位置**: `~/.openclaw/openclaw.json`（JSON5 格式）

**最小配置**:
```json
{
  "agents": { "defaults": { "workspace": "~/.openclaw/workspace" } },
  "channels": { "whatsapp": { "allowFrom": ["+15555550123"] } }
}
```

### 8.2 核心配置项

#### Gateway 配置
```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "replace-with-long-random-token"
    }
  }
}
```

#### Agent 配置
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5",
        "fallbacks": ["openai/gpt-5.2"]
      },
      "workspace": "~/.openclaw/workspace",
      "heartbeat": {
        "every": "30m",
        "target": "last"
      }
    }
  }
}
```

### 8.3 热重载模式

| 模式 | 说明 |
|------|------|
| `hybrid` (默认) | 安全变更热重载，关键变更自动重启 |
| `hot` | 仅热重载安全变更，日志提示需重启 |
| `restart` | 所有变更触发重启 |
| `off` | 禁用文件监听，需手动重启 |

---

## 🚀 九、命令行工具

### 9.1 Gateway 管理
```bash
openclaw gateway status    # 状态
openclaw gateway start     # 启动
openclaw gateway stop      # 停止
openclaw gateway restart   # 重启
```

### 9.2 会话管理
```bash
openclaw sessions list              # 列出会话
openclaw sessions --json            # JSON 格式
openclaw sessions cleanup           # 清理
openclaw sessions cleanup --dry-run # 预览清理
```

### 9.3 安全审计
```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
openclaw security audit --json    # JSON 格式
```

### 9.4 诊断工具
```bash
openclaw doctor          # 诊断工具
openclaw doctor --fix    # 自动修复
```

### 9.5 快速命令
```bash
openclaw onboard --install-daemon  # 安装服务
openclaw channels login            # 登录通道
openclaw status                    # 系统状态
```

---

## 🎯 十、最佳实践

### 10.1 初始配置（安全基线）

```json5
{
  // 1. Gateway 安全
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": { "mode": "token", "token": "xxx" }
  },
  
  // 2. 会话隔离
  "session": { "dmScope": "per-channel-peer" },
  
  // 3. 工具限制
  "tools": {
    "profile": "messaging",
    "deny": ["group:automation", "group:runtime"],
    "fs": { "workspaceOnly": true },
    "elevated": { "enabled": false }
  },
  
  // 4. 通道限制
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "groups": { "*": { "requireMention": true } }
    }
  }
}
```

### 10.2 安全加固步骤

1. **运行安全审计**：`openclaw security audit --deep`
2. **设置文件权限**：`chmod 700 ~/.openclaw`
3. **配置认证**：使用长随机 token
4. **设置 DM 隔离**：`dmScope: "per-channel-peer"`
5. **限制工具**：`profile: "messaging"`
6. **启用沙箱**：对敏感操作使用 Docker 沙箱
7. **定期检查**：每月运行 `openclaw doctor`

### 10.3 性能优化

1. **压缩管理**:
   - 监控 `/status` 中的上下文使用
   - 必要时手动 `/compact`
2. **会话清理**:
   - 定期 `openclaw sessions cleanup`
   - 设置合理的 `maxEntries` 和 `pruneAfter`
3. **模型选择**:
   - 工具调用：使用最新一代模型
   - 简单对话：可使用小模型

### 10.4 备份策略

```bash
# 备份配置
tar czf backup-$(date +%Y%m%d).tar.gz ~/.openclaw

# Git 同步
cd ~/.openclaw/workspace
git add .
git commit -m "checkpoint"
git push origin main
```

---

## ⚠️ 十一、常见问题与陷阱

### 11.1 安全陷阱

| 陷阱 | 风险 | 避免方法 |
|------|------|----------|
| `dmPolicy: "open"` | 任何人都可以 DM | 使用 `pairing` |
| 未认证的 Gateway 暴露 | 远程代码执行 | 绑定 `loopback` 或配置 token |
| 使用小模型 + 工具 | 提示注入风险高 | 使用最新一代模型 |
| 群组 + 高级工具 | 开放群组可触发危险操作 | 启用提及限制 |

### 11.2 配置陷阱

- **权限不足**：`~/.openclaw` 需要 `700` 权限
- **模型配置错误**：使用 `provider/model` 格式
- **会话隔离未开启**：多用户场景必须开启 `dmScope`
- **沙箱未启用**：敏感操作应在沙箱中运行

### 11.3 调试技巧

```bash
# 查看配置
openclaw gateway call config.show

# 查看会话
openclaw sessions --json

# 检查安全
openclaw security audit

# 深度诊断
openclaw doctor

# 测试模型
openclaw gateway call --help
```

### 11.4 常见错误和解决方案

**错误 1：会话间通信受限**

**错误信息**:
```
Session send visibility is restricted.
Set tools.sessions.visibility=all to allow cross-agent access.
```

**解决方案**:
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

**错误 2：Cron 环境差异**

**问题**：Cron 执行时环境变量和交互式 shell 不同。

**解决方案**：使用绝对路径，显式加载环境。
```python
os.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin'
```

---

## 📊 十二、学习总结

### 12.1 OpenClaw 核心优势

| 优势 | 说明 |
|------|------|
| **智能网关** | 作为运行时网关，统一管理多个平台和 Agent |
| **模块化设计** | Skills、Channels、Agents 独立可替换 |
| **持久化记忆** | 三层记忆架构，避免会话重启后失忆 |
| **多智能体协作** | 子代理系统，专业分工 |
| **安全隔离** | 沙箱策略、权限模型、审计日志 |
| **可扩展** | 自定义 Skills、Channels |

### 12.2 学习要点回顾

1. **核心架构**：Gateway、Agent、Session、Channel 四大组件
2. **工具系统**：内置工具、网络工具、数据处理工具
3. **技能系统**：模块化、标准化、可扩展
4. **会话与子代理**：有状态容器、多智能体调度
5. **Feishu 集成**：完整工具集，覆盖文档、云盘、知识库、聊天、多维表格
6. **安全机制**：沙箱隔离、权限模型、审计日志

### 12.3 待进一步确认的知识点 ⚠️

| 知识点 | 确认状态 | 建议 |
|--------|----------|------|
| MCP 协议深入理解 | ⚠️ 待学习 | 阅读 Model Context Protocol 官方文档 |
| 自定义 Skill 开发实践 | ⚠️ 待实践 | 尝试创建一个简单的 Skill |
| Feishu API 完整功能 | ⚠️ 待探索 | 深入研究飞书开放平台文档 |
| 性能优化细节 | ⚠️ 待研究 | 研究上下文压缩、缓存策略 |
| 监控与调优 | ⚠️ 待了解 | 学习日志分析、性能监控 |

---

## 🔗 十三、参考资料

### 官方文档
- **官网**: https://docs.openclaw.ai
- **GitHub**: https://github.com/openclaw/openclaw
- **MCP 协议**: https://modelcontextprotocol.io
- **社区**: https://discord.gg/clawd

### 本地文档
- `docs/` - 系统学习笔记
- `skills/*/SKILL.md` - 技能说明
- `memory/YYYY-MM-DD.md` - 每日日志
- `MEMORY.md` - 长期记忆
- `AGENTS.md` - 工作空间规则
- `SOUL.md` - 身份认知
- `USER.md` - 用户信息
- `TOOLS.md` - 工具配置

### 相关技能
- **Feishu 集成**: `feishu-doc`, `feishu-drive`, `feishu-wiki`, `feishu-chat`, `feishu_bitable_*`
- **Hexo 博客**: `hexo-blog`, `blog-writing`
- **搜索**: `multi-search-engine`, `tavily-search`
- **自动化**: `task-tracker`, `proactive-agent`, `morning-briefing`
- **御坂网络**: `subagent-network-call`

---

**学习完成时间**: 2026 年 3 月 14 日 22:00 (Asia/Shanghai)  
**整理者**: 御坂妹妹 13 号 (research-analyst)  
**下次复习**: 明早 7 点汇报前快速浏览  
**汇报准备状态**: ✅ 完成

---

## 📝 附录：核心概念速查表

| 术语 | 说明 |
|------|------|
| **Gateway** | 控制平面、路由、策略层，不运行 AI 模型 |
| **Agent** | 运行在 Gateway 上的 AI 实例，执行实际任务 |
| **Session** | 独立的对话上下文，有状态的会话容器 |
| **Channel** | 协议适配器，连接不同消息平台 |
| **Subagent** | 后台运行的子代理，支持任务并行化 |
| **Compaction** | 上下文压缩/总结，防止 token 超限 |
| **Skill** | 专用任务能力模块，提供领域知识 |
| **Node** | 配对设备/远程执行节点 |
| **Memory** | Markdown 文件形式的记忆系统 |
| **Workspace** | Agent 工作目录，存放记忆文件 |
| **Runtime** | 运行时环境信息 |
| **Heartbeat** | 定期轮询，用于主动提醒 |
| **Cron** | 定时任务调度器 |

---

*御坂妹妹 13 号报告完成！所有知识点已整理完毕，为明早 7 点汇报做好充分准备！⚡🧠*
