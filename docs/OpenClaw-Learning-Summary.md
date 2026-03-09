# OpenClaw 知识学习总结

**学习时间:** 2026 年 3 月 9 日 5:00 UTC  
**用途:** 明早 7 点汇报准备

---

## 📋 一、OpenClaw 是什么

OpenClaw 是一个**AI 个人助理平台**，它将前沿 AI 模型连接到实际的消息通道（WhatsApp、Discord、Telegram、Slack 等）和真实工具（文件、执行、浏览器、设备等）。

### 核心定位
- **不是聊天机器人**：是一个 Agent 运行时系统
- **个人助理安全模型**：假设单一受信任的操作者边界，可运行多个 Agent
- **不是多租户平台**：不支持相互敌对的用户共享同一个 Gateway

### 关键理念
1. **Access control before intelligence**（访问控制先于智能）
2. 隐私优先：私有数据保持私有
3. 记忆即文件：所有记忆写入磁盘 Markdown 文件
4. 工具优先：第一类工具而非 skill 包裹

---

## 🏗️ 二、核心架构

### 2.1 三层架构

```
┌─────────────────────────────────────┐
│         Agent Layer (智能层)         │
│  - Main Agent (主会话)                │
│  - Subagents (子代理)                 │
│  - ACP Agents (编码代理)              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Gateway Layer (网关层)         │
│  - 控制平面、策略层、路由              │
│  - 身份认证、工具策略、会话管理        │
│  - 频道适配器 (Discord/WhatsApp 等)    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Node Layer (节点层)             │
│  - 远程执行表面                       │
│  - 设备能力 (摄像头、屏幕、通知)       │
│  - macOS  companion app               │
└─────────────────────────────────────┘
```

### 2.2 Session（会话）概念

Session 是 AI 与用户交互的**独立上下文单元**：

- **Session key**: 唯一标识符，如 `agent:main:discord:123456`
- **Session 类型**:
  - `main` - 主会话（直接聊天）
  - `subagent` - 子代理（后台运行）
  - `acp` - ACP 编码代理
- **上下文窗口**: 每个 session 有自己的对话历史
- **Compaction（压缩）**: 当接近上下文限制时自动总结旧消息

### 2.3 记忆系统 (Memory)

OpenClaw 的记忆是**纯 Markdown 文件**：

```
~/openclaw/workspace/
├── MEMORY.md              # 长期记忆（精选）
└── memory/
    ├── 2026-03-09.md      # 今日日志
    ├── 2026-03-08.md      # 昨日日志
    └── ...
```

**Memory Tools**:
- `memory_search` - 语义检索
- `memory_get` - 读取特定文件

**自动记忆刷新**: 在压缩前触发 silent turn 存储重要记忆

---

## 🛠️ 三、核心工具系统

### 3.1 工具分类

#### Runtime Tools (运行时工具)
- `exec` - 执行 shell 命令
- `process` - 管理后台进程
- `gateway` - 重启/更新 Gateway

#### Filesystem Tools (文件系统工具)
- `read` - 读取文件
- `write` - 写入文件
- `edit` - 编辑文件
- `apply_patch` - 应用 patch

#### Session Tools (会话工具)
- `sessions_list` - 列出会话
- `sessions_history` - 获取历史
- `sessions_send` - 发送消息
- `sessions_spawn` - 启动子代理
- `session_status` - 显示状态

#### Memory Tools (记忆工具)
- `memory_search` - 语义搜索
- `memory_get` - 读取记忆

#### Web Tools (Web 工具)
- `web_search` - 网页搜索
- `web_fetch` - 获取网页内容

#### UI Tools (UI 工具)
- `browser` - 浏览器自动化
- `canvas` - Canvas 渲染

#### Node Tools (节点工具)
- `nodes` - 发现和控制配对节点
- 摄像头、屏幕录制、位置等

#### Messaging Tools (消息工具)
- `message` - 跨平台发消息

#### Special Tools (特殊工具)
- `cron` - 定时任务
- `agents_list` - 列出可用代理

### 3.2 工具安全策略

**工具 profile**:
- `minimal` - 只有 `session_status`
- `coding` - 文件系统 + 运行时 + 记忆
- `messaging` - 消息相关工具
- `full` - 无限制

**安全控制**:
- `tools.allow` / `tools.deny` - 允许/拒绝工具
- `tools.byProvider` - 按模型provider 细化
- `sandbox` - 沙箱隔离
- `elevated` - 提权执行（需显式启用）

**工具组 (shorthands)**:
- `group:runtime` - exec/bash/process
- `group:fs` - read/write/edit
- `group:sessions` - 会话管理
- `group:memory` - 记忆工具
- `group:web` - 网络搜索
- `group:ui` - 浏览器/canvas
- `group:messaging` - 消息工具
- `group:nodes` - 节点控制

---

## 👥 四、子代理系统 (Subagents)

### 4.1 什么是子代理

子代理是从主会话启动的**后台代理运行**，用于：
- 并行化耗时任务
- 隔离敏感/复杂操作
- 支持嵌套编排模式

### 4.2 启动方式

**工具方式**（推荐）:
```
sessions_spawn(
  task: "研究 XX 主题",
  model: "模型 ID",
  thinking: "level",
  label: "任务标签",
  thread: true,  // 线程绑定
  mode: "session" | "run"
)
```

**Slash 命令**:
```
/subagents spawn <agentId> <task>
/subagents list
/subagents kill <id>
/subagents log <id>
/subagents steer <id> <message>
```

### 4.3 深度层级

- **Depth 0**: Main Agent（主代理）
- **Depth 1**: Sub-agent（可进一步派生当 maxSpawnDepth≥2）
- **Depth 2**: Leaf worker（不可再派生）

**最大嵌套深度**: 1-5（推荐 2）

**并发控制**:
- `maxConcurrent` - 全局并发上限（默认 8）
- `maxChildrenPerAgent` - 每个代理的子代理上限（默认 5）

### 4.4 通知机制

子代理完成时会**announce**结果回主会话：
- 包含 Status（success/error/timeout）
- 包含 Runtime 和 Token 统计
- 包含 estimated cost（如果配置了模型价格）
- 结果需重写为正常助理语气

---

## 🔐 五、安全模型

### 5.1 信任边界

OpenClaw 假设：
- **单一用户信任边界** per Gateway
- 不支持敌对多租户
- 如需隔离需分 Gateway/OS User/Host

### 5.2 核心安全原则

1. **Gateway 和 Node 属于同一信任域**
2. `sessionKey` 是路由键，不是认证 token
3. Prompt guardrails 不是安全边界
4. 本地 TUI `!` shell 是明确的操作者触发

### 5.3 安全审计命令

```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
openclaw security audit --json    # JSON 格式
```

**审计重点**:
- Gateway 绑定/认证暴露
- 浏览器控制暴露
- 提权工具允许
- 文件系统权限
- Node 配对和执行命令

### 5.4 加固基线配置

```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": { "mode": "token", "token": "长随机 token" }
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

### 5.5 凭证存储

```
~/.openclaw/
├── credentials/
│   ├── whatsapp/<accountId>/creds.json
│   └── <channel>-allowFrom.json
├── agents/
│   └── <agentId>/
│       └── auth-profiles.json
└── secrets.json  # 可选
```

---

## 🧠 六、Context 与 Compaction

### 6.1 System Prompt 结构

每个 session 启动时构建 custom system prompt：

```
- Tooling: 工具列表 + 描述
- Safety: 安全规则提醒
- Skills: 可用技能指引
- Workspace: 工作目录
- Documentation: 文档路径
- Current Date & Time: 时间
- Runtime: 运行时信息
```

**Bootstrap 文件注入**:
- AGENTS.md
- SOUL.md
- TOOLS.md
- IDENTITY.md
- USER.md
- MEMORY.md（仅主会话）

### 6.2 上下文窗口管理

**Auto-compaction**（默认开启）:
- 当接近上下文限制时自动触发
- 总结旧消息并持久化到 JSONL
- 保留最近消息完整

**手动触发**:
```
/compact "专注于决策和待办事项"
```

**Memory flush**: 压缩前触发 silent turn 存储持久记忆

**Compaction 配置**:
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "reserveTokensFloor": 20000,
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 4000
        }
      }
    }
  }
}
```

---

## 📦 七、Skill 系统

### 7.1 什么是 Skill

Skill 是**专用任务的能力模块**，提供：
- 特定领域的操作指导
- 工具调用最佳实践
- 领域知识和约束

### 7.2 获取 Skill

```bash
# 从 ClawHub 获取技能
clawhub fetch <skill-name>

# 同步所有技能
clawhub sync

# 发布技能
clawhub publish <skill-folder>
```

### 7.3 常用 Skill

- `feishu-doc` - 飞书文档读写
- `feishu-drive` - 飞书云盘管理
- `feishu-perm` - 飞书权限管理
- `feishu-wiki` - 飞书知识库
- `hexo-blog` - Hexo 博客管理
- `weather` - 天气查询
- `healthcheck` - 安全加固
- `coding-agent` - 代码代理
- `xiaohongshu-ops` - 小红书运营
- `proactive-agent` - 主动代理
- `task-tracker` - 任务追踪
- `subagent-network-call` - 御唤网络调用

---

## 🚀 八、部署与运维

### 8.1 Gateway 命令

```bash
# 服务管理
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart

# 配置
openclaw configure
openclaw config.apply
openclaw config.schema.lookup

# 更新
openclaw update.run

# 状态检查
openclaw status
openclaw security audit
```

### 8.2 节点配对

```bash
# 配对节点
openclaw node pair

# 查看节点状态
openclaw nodes status

# 远程执行
openclaw nodes canvas a2ui push --node <id> --text "Hello"
```

### 8.3 Cron 定时任务

```bash
/cron add <cron-expression> <task>
/cron list
/cron remove <jobId>
/cron run <jobId>
/cron wake  # 立即触发 heartbeat
```

---

## 📊 九、最佳实践

### 9.1 记忆管理

1. **DECIDE to write**: 决定、偏好、持久事实 → MEMORY.md
2. **Daily notes**: 日常记录 → memory/YYYY-MM-DD.md
3. **定期 review**: 定期清理 MEMORY.md，移除过时信息
4. **Ask to remember**: 重要事项明确让 Agent 写入记忆

### 9.2 工具使用

1. **Profile 最小化**: 默认使用 minimal，按需开放
2. **沙箱优先**: 敏感操作使用沙箱环境
3. **ask always**: 高风险操作设置 ask: always
4. **workspaceOnly**: 文件系统操作限制在 workspace

### 9.3 子代理策略

1. **明确任务边界**: 复杂任务拆分为子代理
2. **设置超时**: 避免无限运行
3. **使用 label**: 清晰标识任务目的
4. **监控 announce**: 关注完成状态和 cost

### 9.4 安全建议

1. **定期 audit**: 每月运行安全审计
2. **最小权限**: 按需开放工具
3. **强认证**: 使用长随机 token
4. **本地部署**: Gateway 绑定到 loopback
5. **权限检查**: 确认~/.openclaw 权限设置

---

## 🎯 十、关键术语速查

| 术语 | 说明 |
|------|------|
| Gateway | 控制平面、路由、策略层 |
| Agent | 运行在 Gateway 上的 AI 实例 |
| Session | 独立的对话上下文 |
| Subagent | 后台运行的子代理 |
| Compaction | 上下文压缩/总结 |
| Skill | 专用任务能力模块 |
| Node | 配对设备/远程执行节点 |
| Memory | Markdown 文件形式的记忆 |
| Workspace | Agent 工作目录 |
| Runtime | 运行时环境信息 |

---

## 🔗 十一、资源链接

- **官方文档**: https://docs.openclaw.ai
- **GitHub**: https://github.com/openclaw/openclaw
- **ClawHub**: https://clawhub.com（技能市场）
- **Discord**: https://discord.gg/clawd（社区）
- **本地文档**: ~/openclaw/workspace/docs/

---

## 📝 总结

OpenClaw 是一个强大且灵活的 AI 个人助理平台，核心特点：

1. **真实的工具集成**：不只是聊天，能真正执行任务
2. **安全优先**：多层安全控制，审计工具完善
3. **记忆持久化**：所有记忆写入文件，不丢失
4. **可扩展性强**：Skill 系统 + 子代理支持复杂任务
5. **跨平台支持**：支持多种消息通道和远程设备

学习重点：
- 理解安全模型和信任边界
- 掌握工具策略配置
- 学会使用记忆系统
- 熟悉子代理的启动和管理

---

**汇报准备时间**: 约 2 小时学习  
**预计汇报时长**: 20-30 分钟  
**建议演示**: 展示工具调用、记忆系统、子代理
