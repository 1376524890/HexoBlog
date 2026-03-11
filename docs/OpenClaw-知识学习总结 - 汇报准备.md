# OpenClaw 知识学习总结
**学习日期**: 2026-03-11  
**学习目的**: 为明早七点汇报做准备  
**学习方式**: 只学习，不实践

---

## 🎯 一、OpenClaw 是什么

### 1.1 核心定位
OpenClaw 是一个**智能体网关系统**，类似于"个人版 Autogen"，但它:
- ✅ 不是纯框架，是**完整的系统**
- ✅ 不是纯聊天机器人，是**可配置的 AI 助手**
- ✅ 不是纯自动化工具，是**多智能体协作平台**

### 1.2 一句话概括
> **OpenClaw = 智能体网关 + 多通道支持 + 技能系统 + 记忆系统 + 自动化能力**

---

## 🏗️ 二、核心架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   用户交互层                         │
│  WhatsApp / Telegram / Discord / Slack / ...       │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              OpenClaw Gateway (WS 服务)              │
│  - 会话管理 (Session)                                │
│  - 路由转发 (Routing)                                │
│  - 工具调度 (Tools)                                  │
│  - 技能调用 (Skills)                                 │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                   Agent 层                           │
│  - 工作空间 (Workspace)                              │
│  - 记忆系统 (Memory)                                 │
│  - 模型配置 (Models)                                 │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  工具层                              │
│  - 本地工具 (File, Exec, System)                     │
│  - 网络工具 (Web Search, Browser)                    │
│  - 平台工具 (Feishu, Bitable, Drive)                 │
│  - 节点工具 (Nodes, Camera, Screen)                  │
└─────────────────────────────────────────────────────┘
```

### 2.2 关键组件

| 组件 | 职责 | 位置 |
|------|------|------|
| **Gateway** | WebSocket 网关，会话路由，工具调度 | 主进程 |
| **Agent** | 独立智能体实例，有独立工作空间 | 工作区 |
| **Skills** | 工具使用指南，能力封装 | `skills/` |
| **Memory** | 持久化记忆，上下文管理 | `memory/` |
| **Nodes** | 远程节点设备，执行环境 | 配对设备 |

---

## 🔧 三、核心概念

### 3.1 会话管理 (Session)

**什么是会话？**  
会话是**一次对话的上下文状态**，包含历史消息、系统提示、工具调用等。

**会话类型**:
- **DM 会话**: 一对一聊天
- **Group 会话**: 群组聊天
- **Thread 会话**: 线程/主题聊天

**会话隔离策略** (`session.dmScope`):
```json
{
  "session": {
    "dmScope": "per-channel-peer"  // 每个渠道 + 每个用户独立会话
  }
}
```

**会话生命周期**:
1. **创建**: 首次消息到达时
2. **维护**: 持续记录消息历史
3. **重置**: 可手动 (`/reset`) 或自动 (每日 4 点，闲置超时)
4. **清理**: 自动归档旧会话

**关键命令**:
```bash
openclaw sessions list          # 列出会话
openclaw sessions cleanup       # 清理会话
```

### 3.2 记忆系统 (Memory)

**双重记忆架构**:

| 类型 | 文件 | 用途 |
|------|------|------|
| **短期记忆** | `memory/YYYY-MM-DD.md` | 每日日志，实时更新 |
| **长期记忆** | `MEMORY.md` | 精选知识，长期保存 |

**记忆工具**:
- `memory_search`: 语义搜索，基于向量检索
- `memory_get`: 精准读取文件内容

**记忆特性**:
- ✅ **纯 Markdown 文件** - 易于编辑和版本控制
- ✅ **向量检索** - 支持语义搜索
- ✅ **混合搜索** - BM25 + 向量相似度
- ✅ **自动压缩** - 临近 token 上限时自动整理记忆
- ✅ **时间衰减** - 新内容优先，旧内容降权

**配置示例**:
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",  // 使用 OpenAI 嵌入
        "hybrid": {
          "enabled": true,
          "vectorWeight": 0.7,
          "textWeight": 0.3,
          "mmr": {
            "enabled": true,
            "lambda": 0.7
          },
          "temporalDecay": {
            "enabled": true,
            "halfLifeDays": 30
          }
        }
      }
    }
  }
}
```

### 3.3 技能系统 (Skills)

**技能是什么？**  
技能是**AgentSkills 兼容的目录**，包含 `SKILL.md` 和工具使用说明，教 AI 如何使用工具。

**技能来源**:
1. **Bundled Skills** - 内置技能（npm 包）
2. **Managed Skills** - `~/.openclaw/skills/` (全局共享)
3. **Workspace Skills** - `<workspace>/skills/` (每个 agent 独立)
4. **ClawHub Skills** - [https://clawhub.com](https://clawhub.com) (在线仓库)

**技能优先级** (从高到低):
```
<workspace>/skills > ~/.openclaw/skills > bundled skills
```

**技能结构**:
```
skill-name/
├── SKILL.md          # 技能说明 (必须)
├── README.md         # 详细说明 (可选)
├── tools/            # 工具文件 (可选)
├── assets/           # 资源文件 (可选)
└── scripts/          # 脚本文件 (可选)
```

**SKILL.md 格式**:
```markdown
---
name: my-skill
description: 这个技能的描述
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["uv"] },
      "emoji": "✨"
    }
  }
---

# 技能说明

这里是详细的使用说明...
```

**使用 ClawHub 管理技能**:
```bash
# 安装技能
clawhub install <skill-slug>

# 更新所有技能
clawhub update --all

# 同步技能 (扫描 + 发布)
clawhub sync --all
```

### 3.4 多智能体架构 (Multi-Agent)

**为什么要多智能体？**  
隔离不同的工作流、权限、配置，提高安全性和专注度。

**配置示例**:
```json
{
  "agents": {
    "list": [
      {
        "id": "home",
        "default": true,
        "workspace": "~/.openclaw/workspace-home"
      },
      {
        "id": "work",
        "workspace": "~/.openclaw/workspace-work"
      }
    ]
  },
  "bindings": [
    {
      "agentId": "home",
      "match": { "channel": "whatsapp", "accountId": "personal" }
    },
    {
      "agentId": "work",
      "match": { "channel": "whatsapp", "accountId": "biz" }
    }
  ]
}
```

### 3.5 工具系统 (Tools)

**工具分类**:

| 类别 | 说明 | 示例 |
|------|------|------|
| **本地工具** | 文件系统、进程执行 | `read`, `write`, `exec`, `process` |
| **网络工具** | 网页操作 | `web_search`, `web_fetch`, `browser` |
| **平台工具** | 第三方集成 | `feishu_*`, `message` |
| **系统工具** | 系统管理 | `nodes`, `canvas`, `session_*` |

**工具安全**:
- 使用 **沙箱** 隔离敏感操作
- 工具调用需要**明确授权**
- 敏感工具可配置**白名单**

---

## ⚙️ 四、配置管理

### 4.1 配置文件

**配置文件位置**: `~/.openclaw/openclaw.json` (JSON5 格式)

**最小配置**:
```json
{
  "agents": { "defaults": { "workspace": "~/.openclaw/workspace" } },
  "channels": { "whatsapp": { "allowFrom": ["+15555550123"] } }
}
```

### 4.2 通道管理

**支持的通道**:
- WhatsApp
- Telegram
- Discord
- Slack
- Signal
- iMessage
- Google Chat
- MS Teams
- Mattermost

**通道权限控制** (`dmPolicy`):
| 值 | 说明 |
|----|------|
| `pairing` | 配对模式 - 陌生人需一次性配对码 |
| `allowlist` | 白名单模式 - 仅允许列表内用户 |
| `open` | 开放模式 - 允许所有 DM |
| `disabled` | 禁用 - 不处理 DM |

### 4.3 模型管理

**模型配置**:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5",
        "fallbacks": ["openai/gpt-5.2"]
      },
      "models": {
        "anthropic/claude-sonnet-4-5": { "alias": "Sonnet" },
        "openai/gpt-5.2": { "alias": "GPT" }
      }
    }
  }
}
```

**模型命令**:
```bash
# 列出模型
openclaw models list

# 设置主模型
openclaw models set anthropic/claude-sonnet-4-5

# 查看模型状态
openclaw models status
```

### 4.4 配置热重载

**重载模式** (`gateway.reload.mode`):

| 模式 | 说明 |
|------|------|
| `hybrid` (默认) | 安全变更热重载，关键变更自动重启 |
| `hot` | 仅热重载安全变更，日志提示需重启 |
| `restart` | 所有变更触发重启 |
| `off` | 禁用文件监听，需手动重启 |

**需要重启的配置**:
- Gateway 服务器配置 (端口、绑定、认证)
- 基础设施配置 (Tailscale、TLS、插件)

---

## 🤖 五、节点系统 (Nodes)

### 5.1 节点是什么？

节点是**配对的远程设备**,可以:
- 执行命令
- 访问摄像头
- 屏幕录制
- 展示 Canvas
- 发送通知

### 5.2 节点工具

```bash
# 列出节点
nodes status

# 执行命令
nodes run --node <node-id> --command "ls -la"

# 拍照
nodes camera snap --node <node-id>

# 屏幕录制
nodes screen record --node <node-id>

# 展示 Canvas
nodes canvas present --node <node-id> --target "https://example.com"
```

### 5.3 节点安全

**安全级别**:
1. **Level 1**: 基础执行 (只读)
2. **Level 2**: 指定目录读写
3. **Level 3**: 工作目录读写
4. **Level 4**: 系统配置 (需批准)

---

## 🛠️ 六、CLI 工具

### 6.1 常用命令

```bash
# 状态检查
openclaw status
openclaw health

# 配置管理
openclaw config get <path>
openclaw config set <path> <value>
openclaw config unset <path>

# 会话管理
openclaw sessions list
openclaw sessions cleanup

# 通道管理
openclaw channels list
openclaw channels status
openclaw channels add

# 技能管理
openclaw skills list
openclaw skills check

# 模型管理
openclaw models list
openclaw models status

# Gateway 管理
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart

# 日志查看
openclaw logs --follow

# 安全审计
openclaw security audit
openclaw security audit --fix
```

### 6.2 聊天命令 (Slash Commands)

在聊天中直接输入 `/...`:

| 命令 | 说明 |
|------|------|
| `/status` | 查看会话状态 |
| `/config` | 修改配置 |
| `/debug` | 运行时调试 |
| `/new [model]` | 重置会话 |
| `/reset` | 重置会话 |
| `/stop` | 停止当前运行 |
| `/compact` | 压缩上下文 |

---

## 🔐 七、安全机制

### 7.1 认证与授权

**认证方式**:
- Token 认证
- 密码认证
- OAuth 认证

**权限模型**:
- **通道级**: 控制谁能发送消息
- **会话级**: 隔离不同会话
- **工具级**: 限制可调用工具
- **节点级**: 控制节点访问权限

### 7.2 沙箱隔离

**沙箱模式** (`agents.defaults.sandbox.mode`):

| 模式 | 说明 |
|------|------|
| `off` | 禁用沙箱 |
| `non-main` | 非主会话使用沙箱 |
| `all` | 所有会话使用沙箱 |

**配置示例**:
```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "scope": "agent"  // session | agent | shared
      }
    }
  }
}
```

### 7.3 安全最佳实践

1. ✅ **启用 DM 隔离** - 多用户场景必须启用 `dmScope: "per-channel-peer"`
2. ✅ **定期审计** - 使用 `openclaw security audit`
3. ✅ **限制通道** - 仅允许可信通道
4. ✅ **使用沙箱** - 敏感操作必须沙箱隔离
5. ✅ **最小权限** - 工具只开启必要的

---

## 🚀 八、自动化能力

### 8.1 定时任务 (Cron)

**Cron 功能**:
- 支持 `every`, `at`, `cron` 三种调度方式
- 支持系统事件、消息推送
- 可运行独立会话

**配置示例**:
```json
{
  "cron": {
    "enabled": true,
    "maxConcurrentRuns": 2,
    "sessionRetention": "24h"
  }
}
```

**Cron 命令**:
```bash
# 列出任务
openclaw cron list

# 添加任务
openclaw cron add --name "daily-check" --every "1d" --system-event "check"

# 运行任务
openclaw cron run daily-check

# 启用/禁用
openclaw cron enable daily-check
openclaw cron disable daily-check
```

### 8.2 心跳机制 (Heartbeat)

**心跳作用**:
- 定期检查邮箱、日历、天气
- 主动推送重要信息
- 减少被动等待

**配置示例**:
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",  # 最后对话通道
        "directPolicy": "allow"
      }
    }
  }
}
```

### 8.3 Webhooks

**Webhook 用途**:
- 接收外部 HTTP 请求
- 集成第三方服务
- 触发自动化任务

**配置示例**:
```json
{
  "hooks": {
    "enabled": true,
    "token": "shared-secret",
    "path": "/hooks",
    "mappings": [
      {
        "match": { "path": "gmail" },
        "action": "agent",
        "agentId": "main",
        "deliver": true
      }
    ]
  }
}
```

---

## 📊 九、监控与诊断

### 9.1 状态检查

```bash
# 整体状态
openclaw status --deep

# Gateway 健康
openclaw health --json

# 日志追踪
openclaw logs --follow --limit 200
```

### 9.2 诊断工具

```bash
# 诊断工具
openclaw doctor

# 修复建议
openclaw doctor --fix

# 深层诊断
openclaw doctor --deep
```

---

## 🎓 十、学习要点总结

### 10.1 核心优势

1. **完整系统** - 不只是框架，开箱即用
2. **多通道支持** - 统一 API，多平台集成
3. **记忆持久化** - 纯 Markdown，易于维护
4. **技能可插拔** - 模块化设计，易于扩展
5. **多智能体架构** - 灵活隔离，安全可控
6. **节点远程执行** - 跨设备协作

### 10.2 使用场景

| 场景 | 说明 |
|------|------|
| **个人助手** | 日程管理、信息查询、自动化任务 |
| **团队协作** | 多智能体分工、权限隔离 |
| **远程控制** | 跨设备命令执行、监控 |
| **系统集成** | Webhook 集成、API 调用 |
| **知识管理** | 记忆系统、笔记整理 |

### 10.3 进阶技巧

1. **记忆整理**: 定期从 `memory/YYYY-MM-DD.md` 提炼到 `MEMORY.md`
2. **技能定制**: 编写自己的技能，扩展工具能力
3. **自动化编排**: 结合 Cron 和 Webhook 构建复杂工作流
4. **多智能体**: 按场景划分多个 Agent，提高专注度
5. **节点网络**: 建立节点网络，实现跨设备协作

---

## 📚 十一、参考资料

### 官方文档

- [主文档](https://docs.openclaw.ai)
- [LLM 索引](https://docs.openclaw.ai/llms.txt)
- [配置示例](https://docs.openclaw.ai/gateway/configuration-examples)
- [配置参考](https://docs.openclaw.ai/gateway/configuration-reference)

### 工具与资源

- [ClawHub 技能仓库](https://clawhub.com)
- [AgentSkills 规范](https://agentskills.io)
- [GitHub 仓库](https://github.com/openclaw/openclaw)

### 社区

- [Discord](https://discord.com/invite/clawd)

---

## 💡 十二、明日汇报要点

### 12.1 开场 (1 分钟)

1. OpenClaw 定位：智能体网关系统
2. 核心价值：完整系统、多通道、可扩展
3. 一句话总结："个人版 Autogen"

### 12.2 核心架构 (3 分钟)

1. 四层架构：用户层 → Gateway → Agent → 工具层
2. 关键组件职责
3. 数据流向

### 12.3 核心特性 (4 分钟)

1. **会话管理** - 隔离策略、生命周期
2. **记忆系统** - 双重架构、向量检索
3. **技能系统** - 模块化、ClawHub
4. **节点系统** - 远程执行、跨设备

### 12.4 使用演示 (2 分钟)

1. CLI 常用命令
2. 配置示例
3. 聊天命令

### 12.5 总结与展望 (1 分钟)

1. 核心优势回顾
2. 使用场景
3. 未来方向

**总时长**: 约 10 分钟

---

*文档整理完成时间：2026-03-11 20:05*  
*下次更新：汇报后根据反馈补充*
