# OpenClaw 官方文档系统学习笔记 ⚡

**学习时间**: 2026 年 3 月 12 日  
**整理者**: 御坂美琴一号  
**用途**: 系统化学习记录

---

## 📚 目录

1. [OpenClaw 是什么](#1-openclaw-是什么)
2. [核心概念](#2-核心概念)
3. [架构设计](#3-架构设计)
4. [配置方式](#4-配置方式)
5. [技能系统](#5-技能系统)
6. [工具使用](#6-工具使用)
7. [最佳实践](#7-最佳实践)

---

## 1. OpenClaw 是什么

### 1.1 核心定义

**OpenClaw** 是一个 **AI Agent 运行时平台**，核心是**智能网关（Runtime Gateway）**。

> 🎯 **关键区分**：它**不是聊天机器人**，而是把 AI 模型连接到真实世界的桥梁！

### 1.2 与 ChatGPT 的对比

| 对比项 | ChatGPT | OpenClaw |
|--------|---------|----------|
| **定位** | 聊天机器人 | Agent 运行时平台 |
| **能力** | 生成文本 | 真正执行任务 |
| **记忆** | 会话内临时 | 持久化到磁盘文件 |
| **工具** | API 调用有限 | 文件系统、命令执行、浏览器控制等 |
| **部署** | 云端 SaaS | 本地部署，数据私有 |
| **安全性** | 受限于平台 | 多层次安全控制，审计完善 |

---

## 2. 核心概念

### 2.1 四大核心理念 ⭐⭐⭐⭐⭐

#### 1️⃣ **Access control before intelligence**（访问控制先于智能）

这是 OpenClaw **最重要**的设计原则！

- ✅ AI 模型可以很聪明，但如果没有权限控制，会非常危险
- ✅ 必须先定义"谁能做什么"，再考虑"能做多聪明"
- ✅ 权限控制是基础，智能是建立在安全之上的

#### 2️⃣ **隐私优先：私有数据保持私有**

- 所有数据本地存储
- 支持自托管部署
- 不上传用户数据到云端
- 数据控制权完全在用户手中

#### 3️⃣ **记忆即文件**

记忆系统架构：
```
~/workspace/
├── MEMORY.md              # 长期记忆（精选）
└── memory/
    ├── 2026-03-12.md      # 今日日志
    ├── 2026-03-11.md      # 昨日日志
    └── ...
```

**特点**：
- ✅ 纯 Markdown 文件 - 易于编辑和版本控制
- ✅ 向量检索 - 支持语义搜索
- ✅ 混合搜索 - BM25 + 向量相似度
- ✅ 自动压缩 - 临近 token 上限时自动整理
- ✅ 时间衰减 - 新内容优先，旧内容降权

#### 4️⃣ **工具优先**

工具分类：
- **本地工具**：文件系统、进程执行（`read`, `write`, `exec`, `process`）
- **网络工具**：网页操作（`web_search`, `web_fetch`, `browser`）
- **平台工具**：第三方集成（`feishu_*`, `message`）
- **系统工具**：系统管理（`nodes`, `canvas`, `session_*`）

---

## 3. 架构设计

### 3.1 三层架构

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

### 3.2 四核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书等 |

### 3.3 Agent Loop 工作流程

```
1. 接收输入 → 用户通过 Channel 发送消息
2. 构建上下文 → 组装 Session 历史、系统提示词、工具列表
3. LLM 推理 → 模型决定是"直接回复"还是"调用工具"
4. 工具执行 → 如需多步骤，通过 Gateway 调用外部工具
5. 循环或结束 → 多步推理继续，否则返回最终结果
6. 发送响应 → Gateway 通过原 Channel 发送给用户
```

---

## 4. 配置方式

### 4.1 配置文件

**位置**: `~/.openclaw/openclaw.json` (JSON5 格式)

**最小配置**:
```json
{
  "agents": { "defaults": { "workspace": "~/.openclaw/workspace" } },
  "channels": { "whatsapp": { "allowFrom": ["+15555550123"] } }
}
```

### 4.2 热重载模式

| 模式 | 说明 |
|------|------|
| `hybrid` (默认) | 安全变更热重载，关键变更自动重启 |
| `hot` | 仅热重载安全变更，日志提示需重启 |
| `restart` | 所有变更触发重启 |
| `off` | 禁用文件监听，需手动重启 |

### 4.3 模型管理

**命令**:
```bash
openclaw models list
openclaw models set <model-id>
openclaw models status
```

**配置示例**:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5",
        "fallbacks": ["openai/gpt-5.2"]
      }
    }
  }
}
```

---

## 5. 技能系统 (Skills)

### 5.1 什么是 Skill？

Skill 是**专用任务的能力模块**，提供：
- 特定领域的操作指导
- 工具调用最佳实践
- 领域知识和约束

### 5.2 技能来源

1. **Bundled Skills** - 内置技能 (npm 包)
2. **Managed Skills** - `~/.openclaw/skills/` (全局共享)
3. **Workspace Skills** - `<workspace>/skills/` (每个 agent 独立)
4. **ClawHub Skills** - [https://clawhub.com](https://clawhub.com) (在线仓库)

### 5.3 技能优先级

```
<workspace>/skills > ~/.openclaw/skills > bundled skills
```

### 5.4 已安装技能列表

| 编号 | 技能名称 | Agent ID | 功能 |
|------|----------|----------|------|
| 1 | `hexo-blog` | - | Hexo 博客管理 |
| 2 | `task-tracker` | - | 任务追踪与持久化 |
| 3 | `weather` | - | 天气查询（无需 API）|
| 4 | `multi-search-engine` | - | 17 个搜索引擎 |
| 5 | `proactive-agent` | - | 主动代理 |
| 6 | `self-improving-agent` | - | 自我改进 |
| 7 | `skill-vetter` | - | 技能安全审查 |
| 8 | `skill-creator` | - | 技能创建工具 |
| 9 | `subagent-network-call` | - | 御坂网络调用 |
| 10 | `xiaohongshu-ops-skill` | - | 小红书运营 |
| 11 | `morning-briefing` | - | 晨间简报 |
| 12 | `tavily-search` | - | Tavily 搜索 |
| 13 | `blog-writing` | - | 博客写作 |
| 14 | `email-sender` | - | 邮件发送 |
| 15 | `stock-analysis` | - | 股票分析 |
| 16 | `monitoring` | - | 系统监控 |

### 5.5 技能管理命令

```bash
clawhub sync              # 同步所有技能
clawhub fetch <name>      # 获取单个技能
clawhub publish <folder>  # 发布自定义技能
```

---

## 6. 工具使用

### 6.1 8 大工具分类

#### 1️⃣ **Runtime Tools**
- `exec` - 执行命令
- `process` - 管理进程
- `gateway` - 控制网关

#### 2️⃣ **Filesystem Tools**
- `read` - 读取文件
- `write` - 创建/覆盖文件
- `edit` - 编辑文件
- `apply_patch` - 应用补丁

#### 3️⃣ **Session Tools**
- `sessions_list` - 列出会话
- `sessions_history` - 获取历史
- `sessions_send` - 发送消息
- `sessions_spawn` - 启动子代理
- `session_status` - 会话状态

#### 4️⃣ **Memory Tools**
- `memory_search` - 语义搜索
- `memory_get` - 精准读取

#### 5️⃣ **Web Tools**
- `web_search` - 网络搜索
- `web_fetch` - 网页抓取
- `tavily` - Tavily 搜索

#### 6️⃣ **UI Tools**
- `browser` - 浏览器控制
- `canvas` - Canvas 控制

#### 7️⃣ **Node Tools**
- `nodes` - 节点控制（摄像头、屏幕录制、位置、通知）

#### 8️⃣ **Messaging Tools**
- `message` - 消息发送和通道操作

### 6.2 Feishu 集成工具

| 工具 | 功能 |
|------|------|
| `feishu_doc` | 文档操作（读写、编辑、创建表格、上传文件等）|
| `feishu_drive` | 云盘文件管理（列表、创建、移动、删除）|
| `feishu_wiki` | 知识库导航（空间、节点、搜索）|
| `feishu_chat` | 聊天操作（成员、信息）|
| `feishu_bitable_*` | 多维表格操作（增删改查、字段管理）|
| `feishu_app_scopes` | 应用权限管理 |

### 6.3 工具安全策略

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

### 6.4 CLI 工具命令

```bash
# 状态检查
openclaw status
openclaw health

# 配置管理
openclaw config get <path>
openclaw config set <path> <value>

# 会话管理
openclaw sessions list
openclaw sessions cleanup

# 通道管理
openclaw channels list
openclaw channels status

# 技能管理
openclaw skills list
openclaw skills check

# 模型管理
openclaw models list
openclaw models status

# Gateway 管理
openclaw gateway status
openclaw gateway start/stop/restart

# 日志查看
openclaw logs --follow

# 安全审计
openclaw security audit
```

---

## 7. 最佳实践

### 7.1 安全模型

#### 权限层级

| 级别 | 说明 | 适用对象 |
|------|------|----------|
| Level 5 | 主 Agent - 完全权限 | 主会话 |
| Level 4 | 可信子 Agent - 受限系统权限 | 需批准 |
| Level 3 | 标准子 Agent - 标准开发权限 | 开发代理 |
| Level 2 | 受限子 Agent - 严格受限权限 | 通用代理 |
| Level 1 | 只读子 Agent - 只读访问 | 读取代理 |

#### 安全审计命令

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

### 7.2 御坂网络第一代（多智能体系统）

#### 核心架构

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

#### 7 个子代理职责

| 编号 | 名称 | Agent ID | 职责 | 权限等级 |
|------|------|----------|------|----------|
| 10 号 | 御坂妹妹 10 号 | `general-agent` | 通用代理，处理琐碎问题 | Level 2 |
| 11 号 | 御坂妹妹 11 号 | `code-executor` | 代码执行者 | Level 3 |
| 12 号 | 御坂妹妹 12 号 | `content-writer` | 内容创作者 | Level 3 |
| 13 号 | 御坂妹妹 13 号 | `research-analyst` | 研究分析师 | Level 3 |
| 14 号 | 御坂妹妹 14 号 | `file-manager` | 文件管理器 | Level 2 |
| 15 号 | 御坂妹妹 15 号 | `system-admin` | 系统管理员 | Level 4 |
| 17 号 | 御坂妹妹 17 号 | `memory-organizer` | 记忆整理专家 | Level 3 |

#### 启动方式

**工具方式**（推荐）：
```python
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",
  mode: "run",
  label: "task-label",
  task: "任务描述"
})
```

**Slash 命令**：
```bash
/subagents spawn <agentId> <task>
/subagents list
/subagents kill <id>
/subagents log <id>
/subagents steer <id> <msg>
```

### 7.3 记忆管理最佳实践

1. ✅ **DECIDE to write**: 决定、偏好、持久事实 → MEMORY.md
2. ✅ **Daily notes**: 日常记录 → memory/YYYY-MM-DD.md
3. ✅ **定期 review**: 定期清理 MEMORY.md，移除过时信息
4. ✅ **Ask to remember**: 重要事项明确让 Agent 写入记忆

#### 安全操作规则

1. ✅ 使用 `trash` 而不是 `rm`
2. ✅ 操作前备份：修改 `MEMORY.md` 前自动备份
3. ✅ 检查 Git 状态：操作前确认 `git status`
4. ✅ 安全检查：运行 `python3 scripts/safety-check-memory.py`
5. ✅ 立即提交：操作后 `git add` 和 `git commit`

### 7.4 自动化能力

#### 定时任务 (Cron)

**命令**:
```bash
openclaw cron list
openclaw cron add --name "daily-check" --every "1d"
openclaw cron run daily-check
openclaw cron enable/disable daily-check
```

#### 心跳机制 (Heartbeat)

**配置示例**:
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "directPolicy": "allow"
      }
    }
  }
}
```

#### Webhooks

**配置示例**:
```json
{
  "hooks": {
    "enabled": true,
    "token": "shared-secret",
    "path": "/hooks",
    "mappings": [...]
  }
}
```

### 7.5 节点系统

#### 节点是什么？

节点是**配对的远程设备**，可以:
- 执行命令
- 访问摄像头
- 屏幕录制
- 展示 Canvas
- 发送通知

#### 节点命令

```bash
# 执行命令
nodes run --node <node-id> --command "ls -la"

# 拍照
nodes camera snap --node <node-id>

# 屏幕录制
nodes screen record --node <node-id>

# 展示 Canvas
nodes canvas present --node <node-id> --target "https://example.com"
```

---

## 📊 核心总结

### OpenClaw 的 6 大优势

1. ✅ **完整系统** - 开箱即用，不只是框架
2. ✅ **多通道支持** - 统一 API，多平台集成
3. ✅ **记忆持久化** - 纯 Markdown 文件，易于维护
4. ✅ **技能可插拔** - 模块化设计，易于扩展
5. ✅ **多智能体架构** - 灵活隔离，安全可控
6. ✅ **节点远程执行** - 跨设备协作能力

### 使用场景

| 场景 | 说明 |
|------|------|
| **个人助手** | 日程管理、信息查询、自动化任务 |
| **团队协作** | 多智能体分工、权限隔离 |
| **远程控制** | 跨设备命令执行、监控 |
| **系统集成** | Webhook 集成、API 调用 |
| **知识管理** | 记忆系统、笔记整理 |

---

## 📚 参考资料

- **官方文档**: https://docs.openclaw.ai
- **技能仓库**: https://clawhub.com
- **GitHub 仓库**: https://github.com/openclaw/openclaw
- **社区**: https://discord.com/invite/clawd

---

**学习完成时间**: 2026 年 3 月 12 日  
**整理者**: 御坂美琴一号 ⚡

*御坂网络第一代系统运行中*
