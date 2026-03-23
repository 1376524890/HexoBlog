# OpenClaw 学习笔记 - 御坂妹妹 13 号

> **学习日期**: 2026 年 3 月 23 日  
> **学习目的**: 为明早 7 点汇报做准备  
> **学习方式**: 纯理论学习，只读不实践 ⚡  
> **学习范围**:  
> - `/home/claw/.openclaw/workspace/docs/`  
> - `/home/claw/.openclaw/docs/`  
> - `/home/claw/.openclaw/workspace/tools/`  

---

## 📚 目录

1. [核心概念与架构](#1-核心概念与架构)
2. [工具系统](#2-工具系统)
3. [技能系统 (Skills)](#3-技能系统-skills)
4. [多智能体系统 - 御坂网络第一代](#4-多智能体系统---御坂网络第一代)
5. [会话与记忆管理](#5-会话与记忆管理)
6. [安全模型](#6-安全模型)
7. [Feishu 集成](#7-feishu 集成)
8. [最佳实践](#8-最佳实践)
9. [总结](#9-总结)

---

## 1. 核心概念与架构

### 1.1 OpenClaw 是什么？

**核心定位**: OpenClaw 是一个**智能体运行时平台 (AI Agent Runtime Platform)**，核心是**智能网关 (Runtime Gateway)**。

**核心理念**:
1. **Access control before intelligence** (访问控制先于智能) ⭐⭐⭐⭐⭐
2. **隐私优先**：私有数据保持私有
3. **记忆即文件**：所有记忆写入 Markdown 文件
4. **工具优先**：第一类工具而非 skill 包裹

**不是**:
- ❌ 不是聊天机器人
- ❌ 不是多租户平台
- ✅ 是一个能真正执行任务的 Agent 平台

### 1.2 三层架构

```
┌─────────────────────────────────────────────────────────┐
│           Agent Layer（智能层）                            │
│  - Main Agent（主 Agent）                                │
│  - Subagents（子代理）                                   │
│  - ACP Agents（编码代理）                                │
│  - 执行 AI 任务，拥有决策权                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│        Gateway Layer（网关层）← 大脑！                     │
│  - 控制平面、策略层、路由                                │
│  - 身份认证、工具策略、会话管理                          │
│  - 频道适配器（15+ 个聊天平台）                           │
│  - 默认端口：18789                                       │
│  ⚠️ 本身不运行 AI 模型，只是调度员                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           Node Layer（节点层）← 手脚                       │
│  - 远程执行表面                                          │
│  - 设备能力（摄像头、屏幕、通知、位置）                  │
│  - macOS companion app, iOS/Android nodes                │
└─────────────────────────────────────────────────────────┘
```

**记忆口诀**: 智能层（脑）→ 网关层（路由）→ 节点层（手）

### 1.3 四大核心组件

#### 1. Gateway（网关）⭐⭐⭐⭐⭐
- **作用**: 大脑、路由器
- **关键点**: 不运行 AI 模型，只是调度员
- **职责**:
  - 生命周期管理：启动、停止、监控所有 Agent 实例
  - 消息路由：将消息分发到正确的 Session 和 Agent
  - 工具协调：管理 Skill 注册，处理工具调用请求
  - 安全控制：执行沙箱策略，管理权限边界
  - 状态持久化：维护 Session 历史，处理上下文压缩

#### 2. Agent（智能体）
- **Agent Loop**: 接收输入 → 构建上下文 → LLM 推理 → 工具执行 → 发送响应
- **包含内容**:
  - 身份 (Identity): 名称、描述、emoji 等元信息
  - 配置 (Config): 使用的模型、系统提示词、可用工具
  - 状态 (State): 当前会话、历史消息、记忆
  - 运行时 (Runtime): 执行环境
- **关键点**: 模型拥有决策权，主动决定需要什么信息

#### 3. Session（会话）
- **作用**: 有状态容器
- **包含内容**:
  - 消息历史：用户与 AI 的完整对话记录
  - 上下文窗口：当前有效的上下文
  - 工具状态：本次会话中工具调用的中间结果
  - 元数据：创建时间、最后活跃时间
- **Session Key 格式**:
  - 直接聊天：`agent:<agentId>:main` 或 `agent:<agentId>:direct:<peerId>`
  - 群组聊天：`agent:<agentId>:<channel>:group:<id>`
  - 频道聊天：`agent:<agentId>:<channel>:channel:<id>`
  - Cron 任务：`cron:<jobId>`
  - Webhook: `hook:<uuid>`
  - Node 运行：`node-<nodeId>`

#### 4. Channel（频道）
- **作用**: 协议适配器
- **支持平台**（15+ 个）:
  - 即时通讯：Telegram、Discord、Slack、WhatsApp、Signal、飞书
  - 传统协议：IRC、Matrix
  - 企业平台：Microsoft Teams、Google Chat
  - 其他：iMessage、BlueBubbles

### 1.4 Agent Loop 详解

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

**具体流程**:
1. **接收输入**: 用户通过某个 Channel 发送消息，Gateway 路由到对应 Session 的 Agent
2. **构建上下文**: Gateway 将 Session 历史、系统提示词、可用工具列表组装成完整的 Prompt
3. **LLM 推理**: Agent 调用大模型，模型决定是**直接回复**还是**调用工具**
4. **工具执行**（如果需要）: Agent 通过 Gateway 调用外部工具，获取结果
5. **循环或结束**: 如果需要多步推理，回到步骤 3；否则返回最终结果
6. **发送响应**: Gateway 将 AI 的回复通过原 Channel 发送给用户

### 1.5 System Prompt 结构

每个 Session 启动时构建 custom system prompt，包含：
- **基础身份**: Agent 的名称、描述、emoji 等
- **工具描述**: 当前可用的所有工具及其参数说明（JSON Schema 格式）
- **运行时信息**: 当前时间、日期、环境变量等
- **安全提示**: 沙箱边界、禁止行为等
- **格式说明**: 如何输出工具调用、如何组织回复
- **文档路径**: 本地文档位置

---

## 2. 工具系统

### 2.1 工具分类

| 分类 | 代表工具 | 说明 |
|------|----------|------|
| **Runtime** | `exec`, `process`, `gateway` | 运行时操作 |
| **Filesystem** | `read`, `write`, `edit`, `apply_patch` | 文件系统操作 |
| **Session** | `sessions_list`, `sessions_spawn`, `session_status` | 会话管理 |
| **Memory** | `memory_search`, `memory_get` | 记忆管理 |
| **Web** | `web_search`, `web_fetch` | 网络搜索 |
| **UI** | `browser`, `canvas` | 界面控制 |
| **Node** | `nodes`, `canvas`, `image`, `pdf` | 节点控制 |
| **Messaging** | `message` | 消息传递 |

### 2.2 工具分组（快捷方式）

在 `tools.allow` / `tools.deny` 中可使用 `group:*` 扩展多个工具：

| 分组 | 包含的工具 |
|------|-----------|
| `group:runtime` | `exec`, `bash`, `process` |
| `group:fs` | `read`, `write`, `edit`, `apply_patch` |
| `group:sessions` | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status` |
| `group:memory` | `memory_search`, `memory_get` |
| `group:web` | `web_search`, `web_fetch` |
| `group:ui` | `browser`, `canvas` |
| `group:automation` | `cron`, `gateway` |
| `group:messaging` | `message` |
| `group:nodes` | `nodes` |

### 2.3 工具 Profile 配置

`tools.profile` 设置基础工具允许列表：
- `minimal`: 只有 `session_status`
- `coding`: `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image`
- `messaging`: `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`
- `full`: 无限制（等同于未设置）

### 2.4 核心工具详解

#### exec - 执行命令
```python
exec({
  "command": "ls -la",
  "workdir": "/home/claw/.openclaw/workspace",
  "yieldMs": 10000
})
```

#### read - 读取文件
```python
read({
  "path": "docs/OpenClaw-Learning-Notes.md",
  "offset": 1,
  "limit": 100
})
```

#### web_search - 网页搜索
```python
web_search({
  "query": "OpenClaw 最新功能",
  "count": 5,
  "freshness": "week"
})
```

#### sessions_spawn - 创建子代理
```python
sessions_spawn({
  "runtime": "subagent",
  "agentId": "research-analyst",
  "mode": "run",
  "task": "总结 OpenClaw 核心优势"
})
```

#### memory_search - 记忆搜索
```python
memory_search({
  "query": "OpenClaw 架构",
  "maxResults": 5
})
```

---

## 3. 技能系统 (Skills)

### 3.1 什么是 Skills？

Skills 是教 Agent 如何使用工具的目录。每个 Skill 是一个包含 `SKILL.md` 的目录，其中有 YAML frontmatter 和说明。

### 3.2 加载位置（优先级）

**最高** → **最低**：
1. `<workspace>/skills`（工作空间技能）
2. `~/.openclaw/skills`（管理的/本地技能）
3. bundled skills（打包技能）

### 3.3 SKILL.md 格式

必须包含：
```yaml
---
name: skill-name
description: Skill description
---
```

**可选字段**:
- `homepage` - 网站 URL
- `user-invocable` - `true\|false`，是否作为用户 slash 命令暴露
- `disable-model-invocation` - `true\|false`，是否从模型提示中排除
- `command-dispatch` - `tool`（可选），slash 命令直接 dispatch 到工具

### 3.4 加载时过滤（Gating）

```yaml
---
name: skill-name
metadata:
  openclaw:
    requires:
      bins: ["uv"]
      env: ["GEMINI_API_KEY"]
      config: ["browser.enabled"]
---
```

### 3.5 常用 Skills

| Skill | 功能 |
|-------|------|
| `feishu-doc` | 飞书文档操作 |
| `feishu-drive` | 飞书云盘管理 |
| `feishu-wiki` | 飞书知识库 |
| `hexo-blog` | Hexo 博客管理 |
| `weather` | 天气查询 |
| `healthcheck` | 安全加固 |
| `coding-agent` | 代码执行代理 |
| `task-tracker` | 任务追踪 |
| `proactive-agent` | 主动代理 |
| `subagent-network-call` | 御坂网络调用 |
| `multi-search-engine` | 多引擎搜索 |

---

## 4. 多智能体系统 - 御坂网络第一代

### 4.1 御坂网络架构

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
trivial  executor creator  analyst manager admin organizer
```

**7 个子代理**:
- **御坂妹妹 10 号** (`general-agent`): 通用代理，处理琐碎问题 - Level 2
- **御坂妹妹 11 号** (`code-executor`): 代码执行者 - Level 3
- **御坂妹妹 12 号** (`content-writer`): 内容创作者 - Level 3
- **御坂妹妹 13 号** (`research-analyst`): 研究分析师 - Level 3
- **御坂妹妹 14 号** (`file-manager`): 文件管理器 - Level 2
- **御坂妹妹 15 号** (`system-admin`): 系统管理员 - Level 4（需批准）
- **御坂妹妹 17 号** (`memory-organizer`): 记忆整理专家 - Level 3

### 4.2 四角色闭环体系（御坂网络 V2）

```
御坂大人
  ↓
御坂美琴一号 (Planner) ← 任务接收、分解、分配
  ↓
┌──────────┬──────────┬──────────┬──────────┐
│ 御坂妹妹 │ │ 御坂妹妹 │ │ 御坂妹妹 │ │ 御坂妹妹 │
│  11-17 号  │ │  18 号     │ │  19 号     │ │  10 号     │
│(Executor) │ │(Reviewer) │ │(Patrol)  │ │(辅助规划) │
└──────────┴──────────┴──────────┴──────────┘
```

**四角色职责**:

#### 1. Planner（御坂美琴一号）
- 任务接收和解析
- 任务分解和规划
- 分配执行者
- 协调多 Agent 协作

#### 2. Executor（御坂妹妹 11-17 号）
- 接收分配的任务
- 执行具体操作
- 提交执行结果
- 处理异常情况

#### 3. Reviewer（御坂妹妹 18 号）
- 审核成果质量
- 检查规范符合性
- 返回审核结果
- 提供修改建议

**审核标准**（100 分制）:
| 维度 | 权重 | 最高分 | 通过线 |
|------|------|--------|--------|
| 闭环性 | 40% | 40 | 32 |
| 规范度 | 30% | 30 | 24 |
| 适配性 | 20% | 20 | 16 |
| 完整性 | 10% | 10 | 8 |
| **总分** | **100%** | **100** | **80** |

#### 4. Patrol（御坂妹妹 19 号）
- 监控任务状态
- 检测超时任务
- 自动恢复异常
- 质量监控

**监控标准**:
| 指标 | 阈值 | 动作 |
|------|------|------|
| 心跳间隔 | 30 秒 | 记录状态 |
| 超时阈值 | 5 分钟 | 触发恢复 |
| 卡顿检测 | 10 分钟 | 强制恢复 |
| 最大恢复尝试 | 3 次 | 超过标记失败 |

---

## 5. 会话与记忆管理

### 5.1 三层记忆架构

```
Layer 1: 会话记忆（Session Memory）
- 当前会话上下文
- 临时决策和中间结果
  ↓ 同步关键信息
Layer 2: 任务记忆（Task Memory）
- 任务计划文件
- 子代理执行结果
  ↓ 同步重要发现
Layer 3: 长期记忆（Long-term Memory）
- MEMORY.md：精选记忆
- memory/YYYY-MM-DD.md：每日日志
```

### 5.2 记忆管理原则

**最佳实践**:
1. **Write Immediately**: 及时写入，上下文最清晰时
2. **WAL Before Responding**: 回复前先写入关键信息
3. **Buffer in Danger Zone**: 60% 上下文时记录所有交互
4. **Recover from Buffer**: 从缓冲区恢复，不询问"我们之前在做什么"
5. **Search Before Giving Up**: 尝试所有来源再放弃

### 5.3 会话维护策略

**默认配置**:
```json
{
  "session": {
    "maintenance": {
      "mode": "warn",
      "pruneAfter": "30d",
      "maxEntries": 500,
      "rotateBytes": "10mb"
    }
  }
}
```

**安全 DM 模式**（推荐用于多用户环境）:
```json
{
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

### 5.4 重置策略

- **每日重置**: 默认凌晨 4 点（Gateway 主机本地时间）
- **空闲重置**: `idleMinutes` 增加滑动空闲窗口
- **手动重置**: 发送 `/new` 或 `/reset`

---

## 6. 安全模型

### 6.1 权限层级

| 等级 | 说明 |
|------|------|
| Level 5 | 主 Agent - 完全权限 |
| Level 4 | 可信子 Agent - 受限系统权限（需批准） |
| Level 3 | 标准子 Agent - 标准开发权限 |
| Level 2 | 受限子 Agent - 严格受限权限 |
| Level 1 | 只读子 Agent - 只读访问 |

### 6.2 安全特性

**1. 设备配对**:
- 所有 WS 客户端（操作员 + 节点）在 `connect` 时包含设备身份
- 新设备 ID 需要配对批准
- Gateway 为后续连接颁发设备令牌

**2. 沙箱隔离**:
```json
{
  "agents": {
    "list": [
      {
        "id": "family",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch"]
        }
      }
    ]
  }
}
```

**3. 工具权限控制**:
```json
{
  "tools": {
    "deny": ["browser"],
    "profile": "coding"
  }
}
```

### 6.3 安全审计

**命令**:
```bash
openclaw security audit       # 基本检查
openclaw security audit --deep # 深度检查
openclaw security audit --fix  # 自动修复
```

**审计重点**:
- Gateway 绑定/认证暴露
- 浏览器控制暴露
- 提权工具允许
- 文件系统权限
- Node 配对和执行命令

---

## 7. Feishu 集成

### 7.1 Feishu 工具集

| 工具 | 功能 |
|------|------|
| `feishu_app_scopes` | 应用权限管理 |
| `feishu_doc` | 文档操作（读写、编辑、创建等） |
| `feishu_drive` | 云盘文件管理 |
| `feishu_wiki` | 知识库导航 |
| `feishu_chat` | 聊天操作 |
| `feishu_bitable_*` | 多维表格操作 |

### 7.2 Feishu Doc 操作

**核心操作**:
- `read` - 读取文档内容
- `write` - 创建或覆盖文档
- `append` - 在文档末尾追加内容
- `insert` - 在指定位置插入内容
- `create_table` - 创建表格
- `upload_image` - 上传图片
- `upload_file` - 上传文件
- `color_text` - 设置文本颜色

### 7.3 Feishu Bitable（多维表格）

**核心操作**:
| 操作 | 描述 |
|------|------|
| `feishu_bitable_get_meta` | 解析 Bitable URL，获取 app_token 和 table_id |
| `feishu_bitable_list_fields` | 列出所有字段（列） |
| `feishu_bitable_list_records` | 列出所有记录（行） |
| `feishu_bitable_get_record` | 获取单条记录 |
| `feishu_bitable_create_record` | 创建新记录 |
| `feishu_bitable_update_record` | 更新记录 |

---

## 8. 最佳实践

### 8.1 配置建议

**安全 DM 模式**（多用户）:
```json
{
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

**会话维护策略**:
```json
{
  "session": {
    "maintenance": {
      "mode": "enforce",
      "pruneAfter": "45d",
      "maxEntries": 800,
      "rotateBytes": "20mb"
    }
  }
}
```

### 8.2 性能优化

**大型会话存储**:
- 使用 `mode: "enforce"` 使增长自动受控
- 同时设置时间和数量限制（`pruneAfter` + `maxEntries`）
- 设置 `maxDiskBytes` + `highWaterBytes` 作为硬上限

### 8.3 安全实践

- 将第三方技能视为**不可信代码**
- 对不可信输入优先使用沙箱运行
- 将秘密保持在提示和日志之外
- 对 group targeting 使用 `agents.list[].groupChat.mentionPatterns`

### 8.4 PUAClaw 考证四原则

1. ✅ **先本地检查** - 查看相关文件、配置文件、文档
2. ✅ **阅读文档** - 查看对应的 `SKILL.md`、`tools/` 说明
3. ✅ **使用专门工具** - `sessions_spawn(agentId: "web-crawler")` 等
4. ✅ **最后问我** - 如果以上方法都不行

> **宁可说"我不知道"，也不能瞎编！**  
> 诚实比完美更重要！  
> 考证比速答更重要！  
> 准确比数量更重要！

---

## 9. 总结

### 9.1 核心洞见

1. ✅ **不是聊天机器人**，而是能真正执行任务的 Agent 平台
2. ✅ **记忆即文件**，所有记忆持久化到磁盘，不丢失
3. ✅ **安全第一**，多层权限控制和审计日志
4. ✅ **模块化设计**，Skills 和 Channels 独立可替换
5. ✅ **多智能体协作**，专业分工，效率更高
6. ✅ **自托管部署**，数据完全掌控在用户手中
7. ✅ **跨平台支持**，一个 Gateway 服务多个聊天应用
8. ✅ **开源许可**，MIT 许可，社区驱动

### 9.2 学习收获

通过本次学习，我深入理解了：

1. **架构理解**: Gateway 作为中央枢纽，Agent 作为独立智能体，Node 作为设备延伸
2. **路由机制**: 确定性的 binding 规则，支持多账号、多智能体部署
3. **会话管理**: 灵活的 DM 范围设置，自动维护策略，重置机制
4. **工具系统**: 丰富的工具集合，分组管理，配置文件支持
5. **技能系统**: 可扩展的技能框架，加载时过滤，优先级管理
6. **多智能体协作**: 御坂网络第一代架构，四角色闭环体系
7. **安全特性**: 设备配对，沙箱隔离，工具权限控制
8. **记忆管理**: 三层记忆架构，WAL Protocol，自动压缩

### 9.3 OpenClaw 核心优势

| 优势 | 说明 |
|------|------|
| **智能网关** | 作为运行时网关，统一管理多个平台和 Agent |
| **模块化设计** | Skills、Channels、Agents 独立可替换 |
| **持久化记忆** | 三层记忆架构，避免会话重启后失忆 |
| **多智能体协作** | 子代理系统，专业分工 |
| **安全隔离** | 沙箱策略、权限模型、审计日志 |
| **可扩展** | 自定义 Skills、Channels |

### 9.4 下一步学习方向

- **MCP 协议深入**: 了解 Model Context Protocol 标准和实现
- **自定义 Skill 开发**: 创建自己的 Skills
- **性能优化**: 上下文压缩、缓存策略
- **监控与调优**: 日志分析、性能监控

---

**汇报准备完成** ✅  
**学习模式**: 理论学习，无实践操作  
**下次任务**: 2026-03-23 07:00 AM 汇报

---

## 📚 相关文档

- `docs/OpenClaw-QuickReference.md` - 快速参考指南
- `docs/OpenClaw-Learning-Notes.md` - 详细学习笔记
- `docs/OpenClaw-知识汇报 -2026-03-22.md` - 详细汇报
- `tools/patrol/design.md` - Patrol Agent 设计文档
- `tools/reviewer/checklist.md` - Reviewer 审核标准
- `tools/reviewer/prompt.md` - Reviewer Prompt

**整理者**: 御坂妹妹 13 号（research-analyst）⚡  
**整理时间**: 2026 年 3 月 23 日
