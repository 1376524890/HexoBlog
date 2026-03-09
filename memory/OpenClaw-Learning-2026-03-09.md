# OpenClaw 知识学习总结 📚

> **学习目标**: 掌握 OpenClaw 核心概念、架构、工具和最佳实践
> **学习时间**: 2026-03-09 03:34 AM
> **用途**: 明早七点汇报准备

---

## 🎯 什么是 OpenClaw?

OpenClaw 是一个**个人 AI 助手框架**，旨在将前沿的 AI 模型与真实世界的消息传递平台（如 WhatsApp、Telegram、Discord、Slack 等）连接起来。

### 核心理念

1. **个人助手安全模型**: 一个受信任的操作员边界，多个 AI 代理
2. **工具优先**: 通过第一类工具（browser, canvas, nodes, cron）与外部交互
3. **会话连续性**: 保持对话上下文，让 AI 记得你的需求
4. **技能系统**: 通过 AgentSkills 兼容的技能文件夹扩展 AI 能力
5. **网关架构**: 中央网关控制 + 节点扩展能力

---

## 🏗️ 核心架构

### 三大组成部分

```
┌─────────────────────────────────────────────────────────────┐
│                        Gateway (中央控制)                     │
│  • WebSocket 协议通信                                         │
│  • 会话状态管理                                               │
│  • 工具调度中心                                               │
│  • 权限控制和验证                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────┐
        ↓                                 ↓
┌───────────────┐                 ┌───────────────┐
│   Agents      │                 │    Nodes      │
│  (AI 代理)     │                 │  (能力节点)    │
│               │                 │               │
│ • 多代理支持   │                 │ • macOS 节点   │
│ • 技能加载     │                 │ • iOS 节点     │
│ • 会话管理     │                 │ • 设备能力     │
└───────────────┘                 │   (相机/屏幕)  │
        ↑                         └───────────────┘
        ↓
┌───────────────┐
│  Channels     │
│  (消息平台)    │
│               │
│ • WhatsApp    │
│ • Telegram    │
│ • Discord     │
│ • Slack       │
│ • 等等...      │
└───────────────┘
```

### 关键概念

#### 1. 网关 (Gateway)
- **端口**: 默认 `ws://127.0.0.1:18789`
- **角色**: 控制平面，政策表面
- **职责**: 
  - 管理所有代理和会话
  - 执行工具调用
  - 处理权限验证
  - 维护节点配对状态

#### 2. 代理 (Agents)
- 运行在网关内的 AI 实例
- 每个代理有自己的会话空间
- 可配置独立的工具访问权限
- 支持多代理并行运行

#### 3. 节点 (Nodes)
- 远程设备客户端（macOS/iOS）
- 提供本地能力（相机、屏幕、系统命令）
- 需要网关配对授权
- 受 Exec 审批控制

#### 4. 消息通道 (Channels)
- 外部消息平台连接器
- 支持 DM 和群组消息
- 独立的会话隔离策略

---

## 🔄 核心概念详解

### 1. 会话管理 (Session Management)

**会话键 (Session Key)** 结构:
```
agent:<agentId>:<channel>:<scope>:<id>
```

**DM 作用域 (dmScope)** 选项:
- `main` (默认): 所有 DM 共享一个会话（连续性优先）
- `per-peer`: 按发送者隔离
- `per-channel-peer`: 按渠道 + 发送者隔离（**推荐用于多用户**）
- `per-account-channel-peer`: 按账号 + 渠道 + 发送者隔离（多账号场景）

**会话重置策略**:
- `daily`: 每天凌晨 4 点重置（可配置）
- `idle`: 空闲超时重置
- `/new` 或 `/reset`: 手动触发

### 2. 心跳机制 (Heartbeat)

**目的**: 周期性检查后台任务，不干扰用户

**默认配置**:
- 频率：30 分钟（OAuth 模式 1 小时）
- 提示词：读取 `HEARTBEAT.md` 检查清单
- 响应：`HEARTBEAT_OK` = 无事可做，否则发送警报

**典型检查任务**:
- 邮件/通知
- 日历事件
- 社交媒体提及
- 天气提醒

**HEARTBEAT.md 示例**:
```markdown
# Heartbeat checklist

- 快速扫描：任何紧急邮件？
- 如果是白天，轻量级检查用户需求
- 如果任务被阻塞，记录缺失内容并询问
```

### 3. 记忆系统 (Memory)

**两层记忆架构**:
1. **短期记忆**: 会话 JSONL 历史（自动压缩）
2. **长期记忆**: `MEMORY.md` + `memory/YYYY-MM-DD.md` 文件

**记忆维护**:
- 会话压缩：超过上下文窗口时自动摘要
- 心跳检查：定期更新长期记忆
- Git 同步：立即提交到版本控制

**文件位置**:
```
~/.openclaw/workspace/
  ├── MEMORY.md           # 长期记忆摘要
  └── memory/
      ├── 2026-03-09.md   # 今日日志
      └── 2026-03-08.md   # 昨日日志
```

### 4. 技能系统 (Skills)

**技能位置优先级** (从高到低):
1. `<workspace>/skills` (工作区技能，最高优先级)
2. `~/.openclaw/skills` (全局技能)
3. `bundled skills` (内置技能，最低优先级)

**技能格式 (AgentSkills)**:
```markdown
---
name: weather
description: 获取天气信息
---

## 使用方法
当你需要了解某地天气时调用 `weather` 工具...

---
metadata:
  {
    "openclaw": {
      "requires": { "bins": [] },
      "os": ["darwin", "linux", "win32"]
    }
  }
---
```

**技能加载时检查**:
- 操作系统兼容性
- 必需的二进制文件
- 必需的环境变量
- 配置文件要求

### 5. 工具 (Tools)

**工具分组** (用于快速配置):
- `group:runtime`: `exec`, `bash`, `process`
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: 会话管理工具
- `group:memory`: 记忆工具
- `group:web`: 网络搜索和抓取
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: 节点控制
- `group:openclaw`: 所有内置 OpenClaw 工具

**工具配置文件**:
```json
{
  "tools": {
    "profile": "messaging",  // minimal / messaging / coding / full
    "allow": ["slack", "discord"],  // 额外允许
    "deny": ["exec", "browser"]  // 禁止
  }
}
```

---

## 🔧 核心工具详解

### 1. 浏览器自动化 (browser)

**使用流程**:
```
1. browser → status / start
2. browser → snapshot (获取 UI 元素引用)
3. browser → act (点击/输入等操作)
4. browser → screenshot (视觉确认)
```

**核心动作**:
- `status`: 检查浏览器状态
- `start/stop`: 启动/停止浏览器
- `snapshot`: 获取 UI 快照（推荐 `aria` 模式）
- `act`: UI 操作（点击、输入、拖拽等）
- `navigate`: 导航 URL
- `screenshot`: 截屏

**多配置支持**:
- 支持多个浏览器配置文件
- 端口范围：18800-18899
- 支持远程 Chrome CDP 连接

### 2. 节点控制 (nodes)

**设备能力**:
- 相机快照/录影
- 屏幕录制
- 系统通知
- 位置获取
- 设备信息
- 系统命令执行 (`run`)

**安全控制**:
- 需要节点配对
- Exec 审批机制（allowlist / ask / deny）
- 支持敏感命令白名单

**常用命令**:
```json
{
  "action": "run",
  "node": "office-mac",
  "command": ["echo", "Hello"],
  "env": ["FOO=bar"],
  "commandTimeoutMs": 12000
}
```

### 3. 会话管理 (sessions)

**核心操作**:
- `sessions_list`: 列出会话
- `sessions_history`: 获取会话历史
- `sessions_send`: 发送消息到其他会话
- `sessions_spawn`: 启动子代理
- `session_status`: 会话状态

**子代理启动**:
```json
{
  "action": "spawn",
  "task": "处理复杂任务",
  "runtime": "subagent",  // 或 acp
  "mode": "session",  // 或 run (一次性)
  "thread": true,  // Discord 线程绑定
  "cleanup": "delete"  // 完成后清理
}
```

### 4. 定时任务 (cron)

**管理命令**:
- `status`: 查看任务状态
- `list`: 列出所有任务
- `add`: 添加新任务
- `update`: 更新任务
- `remove`: 删除任务
- `run`: 立即执行
- `runs`: 查看执行历史

### 5. 消息发送 (message)

**跨平台支持**:
- WhatsApp, Telegram, Discord, Slack
- Google Chat, Signal, iMessage
- MS Teams

**功能**:
- 文本/媒体消息
- Polls (投票)
- 反应/表情
- 线程管理
- 成员管理

---

## 🛡️ 安全模型

### 信任边界设计

**个人助手模型**:
- 一个受信任的操作员边界（一个用户/主机）
- 支持多个代理
- **不支持**敌对多租户隔离

**关键原则**:
1. **身份优先**: 决定谁可以联系你的机器人
2. **范围次之**: 决定机器人可以在哪里行动
3. **模型最后**: 假设模型可能被操纵

### 安全加固要点

**1. DM 访问控制**:
```json
{
  "session": {
    "dmScope": "per-channel-peer"  // 多用户模式推荐
  },
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing"  // pairing/allowlist/open/disabled
    }
  }
}
```

**2. 工具限制**:
```json
{
  "tools": {
    "profile": "messaging",  // minimal/messaging/coding/full
    "deny": ["exec", "browser", "gateway"]  // 禁止危险工具
  }
}
```

**3. 网关安全**:
```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "replace-with-long-random-token"
    }
  }
}
```

**4. 沙箱模式**:
```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "docker",  // docker / none
        "docker": {
          "network": "isolated"
        }
      }
    }
  }
}
```

### 安全检查命令

```bash
# 全面安全检查
openclaw security audit

# 深度检查（尝试连接网关）
openclaw security audit --deep

# 自动修复
openclaw security audit --fix

# JSON 输出
openclaw security audit --json
```

**常见问题排查**:
- 文件系统权限 (`~/.openclaw` 不应可写)
- 网关认证是否启用
- DM 策略是否过于开放
- 工具访问权限是否最小化
- 沙箱是否启用

---

## 🚀 高级特性

### 1. 会话压缩 (Compaction)

**机制**:
- 当会话接近上下文窗口限制时触发
- 将旧对话总结为紧凑条目
- 保持近期对话完整

**触发方式**:
- 自动触发（达到限制时）
- 手动：`/compact [指令]`

**配置**:
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "model": "anthropic/claude-sonnet-4-5",  // 总结模型
        "targetTokens": 100000
      }
    }
  }
}
```

### 2. 会话剪枝 (Session Pruning)

**作用**: 在每次 LLM 调用前清理旧的 toolResult

**模式**:
- `cache-ttl`: 基于 Anthropic 缓存 TTL 清理
- `off`: 默认关闭

**优势**:
- 减少 Anthropic 缓存大小
- 重置 TTL 窗口
- 降低首请求成本

### 3. 子代理 (Subagents)

**两种运行时**:
- `subagent`: 标准子代理运行
- `acp`: ACP 编排模式

**启动模式**:
- `run`: 一次性任务
- `session`: 持久线程绑定

**使用场景**:
- 复杂任务分解
- 长时间运行任务
- 任务隔离

### ⚠️ 重要说明：runtime 用法

**正确的 runtime 参数**：

✅ **必须使用**: `runtime: "subagent"`
- 使用 OpenClaw agents 列表中的 agentId
- 如：`general-agent`, `code-executor`, `web-crawler` 等

❌ **不要使用**: `runtime: "acp"`
- 需要 ACX runtime 插件（未配置）
- 会报错：`ACP runtime backend is not configured`

**错误示例**：
```json
{
  "action": "spawn",
  "task": "处理复杂任务",
  "runtime": "acp",  // ❌ 错误！未配置
  "agentId": "code-executor",
  "mode": "run"
}
```

**正确示例**：
```json
{
  "action": "spawn",
  "task": "处理复杂任务",
  "runtime": "subagent",  // ✅ 正确！
  "agentId": "code-executor",
  "mode": "run"
}
```

### 5. 御坂网络

**核心概念**:
- 本尊（御坂美琴）= 用户
- 御坂妹妹 = AI 助手分身
- 各司其职，统一调度

**等级制度**:
- Level 1: 通用代理
- Level 2: 指定目录读写
- Level 3: 工作目录读写
- Level 4: 系统配置（需批准）

---

## 📁 工作空间结构

```
~/.openclaw/
├── workspace/                     # 主要工作空间
│   ├── AGENTS.md                  # 代理身份定义
│   ├── SOUL.md                    # AI 人格设定
│   ├── USER.md                    # 用户信息
│   ├── MEMORY.md                  # 长期记忆
│   ├── memory/                    # 每日记忆
│   ├── skills/                    # 本地技能
│   ├── docs/                      # 文档
│   └── HEARTBEAT.md               # 心跳检查清单
│
├── agents/                        # 代理配置
│   └── <agentId>/
│       ├── sessions/              # 会话历史
│       └── agent/auth-profiles.json  # 认证配置
│
├── credentials/                   # 凭证存储
│   ├── whatsapp/                  # WhatsApp 凭证
│   ├── telegram-allowFrom.json    # 电报白名单
│   └── ...
│
├── openclaw.json                  # 全局配置
└── extensions/                    # 插件目录
```

---

## 🎯 最佳实践

### 1. 权限最小化

- 默认使用 `minimal` 或 `messaging` 工具配置
- 仅对可信代理授予 `coding` 或 `full` 配置
- 禁止 `gateway` 和 `cron` 工具（除非必要）

### 2. 多用户隔离

- 启用 `session.dmScope: "per-channel-peer"`
- 使用 `dmPolicy: "pairing"` 或严格的白名单
- 避免共享 Agent 给敌对用户

### 3. 内容安全

- 将网页搜索/抓取结果视为不可信内容
- 对未受信任内容使用只读代理
- 保持 `allowUnsafeExternalContent` 禁用

### 4. 定期维护

- 检查 `HEARTBEAT.md` 并更新任务清单
- 定期运行 `security audit`
- 审查会话历史并更新 `MEMORY.md`
- 清理过期技能

### 5. Git 工作流

- 记忆文件立即 commit
- 博客文章先写草稿后发布
- 配置文件修改前备份
- 使用 `trash` 代替 `rm`

---

## 📊 性能优化

### 1. 上下文管理

- 使用 `/compact` 手动压缩
- 启用自动压缩
- 监控 `session_status` 的 token 使用

### 2. 缓存利用

- 匹配 Anthropic 缓存 TTL（5 分钟/1 小时）
- 启用会话剪枝
- 定期重置 TTL 窗口

### 3. 模型选择

- 复杂任务使用更强的模型
- 心跳检查使用更便宜的模型
- 考虑本地模型降低成本

---

## 🔍 故障排查

### 常见问题

**1. 网关无法连接**:
```bash
# 检查网关状态
openclaw gateway status

# 重启网关
openclaw gateway restart
```

**2. 节点配对失败**:
- 检查配对审批 (`openclaw pairing list <channel>`)
- 验证节点设备令牌
- 检查网络连通性

**3. 会话混乱**:
```bash
# 列出会话
openclaw sessions --json

# 清理会话
openclaw sessions cleanup
```

**4. 工具调用失败**:
- 检查工具是否在允许列表中
- 验证必需的二进制文件/环境变量
- 查看会话历史确认错误详情

---

## 🌟 总结

OpenClaw 是一个强大的个人 AI 助手框架，核心优势：

✅ **工具优先**: 丰富的第一类工具支持
✅ **多平台**: 支持几乎所有主流消息平台
✅ **灵活架构**: 多代理、节点扩展、技能系统
✅ **安全设计**: 信任边界清晰、权限可控
✅ **持续学习**: 完善的记忆和压缩机制

**关键学习点**:
1. 网关是控制核心，代理是执行单元
2. 会话管理是连续性的关键
3. 安全配置需要在便利性和安全性间平衡
4. 技能系统是扩展 AI 能力的核心机制
5. 心跳机制让 AI 主动服务用户

---

**汇报准备完成** ✨
下次检查时间：2026-03-09 10:34 AM (约 7 小时后)
