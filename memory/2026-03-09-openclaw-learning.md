# OpenClaw 知识学习笔记

**学习时间**: 2026-03-09 13:03 UTC
**目标**: 为明早 7 点汇报做准备

---

## 📚 一、OpenClaw 核心概念

### 1.1 什么是 OpenClaw？

OpenClaw 是一个**AI 代理网关平台**，它提供了：

- **统一的消息处理** - 支持 WhatsApp、Telegram、Discord、Slack、Signal、iMessage 等多个渠道
- **会话管理** - 为每个对话维护独立的状态和上下文
- **工具系统** - 为 AI 代理提供丰富的工具调用能力
- **定时任务** - 内置 cron 系统，支持周期性任务执行
- **节点管理** - 可以控制配对设备（相机、屏幕、位置等）
- **子代理系统** - 支持主代理调度子代理进行复杂任务

**关键特点**：
- 网关架构 - 所有消息处理和 AI 运行都通过 Gateway 进行
- 会话隔离 - 每个会话有独立的上下文
- 工具调用 - 使用 typed tools 而不是 shell 命令
- 持久化 - 会话、记忆、配置都持久化存储

---

### 1.2 核心架构

```
用户消息 → Gateway → Session Manager → Agent Runtime → Tools → LLM → Reply
```

**主要组件**：

1. **Gateway** - 中央处理枢纽
   - 消息路由
   - 会话管理
   - 定时调度
   - 工具分发

2. **Session Manager** - 会话管理
   - 会话隔离
   - 上下文管理
   - 会话修剪
   - 会话压缩

3. **Agent Runtime** - 代理运行时
   - 提示词管理
   - 工具调用
   - 流式输出
   - 记忆访问

4. **Tools** - 工具系统
   - 内置工具 (exec, browser, nodes 等)
   - 插件工具
   - 权限控制

---

## 🔧 二、核心工具详解

### 2.1 工具分组

OpenClaw 工具通过分组系统进行权限管理：

```json
{
  "group:runtime": ["exec", "bash", "process"],
  "group:fs": ["read", "write", "edit", "apply_patch"],
  "group:sessions": ["sessions_list", "sessions_history", "sessions_send", "sessions_spawn", "session_status"],
  "group:memory": ["memory_search", "memory_get"],
  "group:web": ["web_search", "web_fetch"],
  "group:ui": ["browser", "canvas"],
  "group:automation": ["cron", "gateway"],
  "group:messaging": ["message"],
  "group:nodes": ["nodes"],
  "group:openclaw": "所有内置工具（不包括插件）"
}
```

### 2.2 核心工具功能

#### `exec` - 执行 Shell 命令
```json
{
  "action": "exec",
  "command": "ls -la",
  "yieldMs": 10000,
  "background": false,
  "timeout": 1800,
  "pty": false
}
```

**关键参数**：
- `yieldMs` - 自动后台运行的延迟
- `background` - 立即后台运行
- `timeout` - 超时时间（默认 1800 秒）
- `elevated` - 需要提升权限
- `pty` - 伪终端（用于需要 TTY 的命令）

#### `sessions_spawn` - 启动子代理
```json
{
  "task": "执行某个任务",
  "label": "任务描述",
  "runtime": "subagent",
  "agentId": "agent-id",
  "mode": "session",
  "thread": true,
  "streamTo": "parent"
}
```

**运行时模式**：
- `subagent` - 子代理模式（默认）
- `acp` - ACP 模式（用于 Codex/Claude Code）

**模式选择**：
- `run` - 一次性任务
- `session` - 持久化会话（需要 `thread: true`）

#### `memory_search` - 语义记忆搜索
```json
{
  "action": "memory_search",
  "query": "搜索关键词",
  "maxResults": 5,
  "minScore": 0.7
}
```

**搜索特性**：
- 混合搜索（向量 + BM25）
- 时间衰减
- MMR 重排序（去重）
- 引用来源标注

#### `browser` - 浏览器控制
```json
{
  "action": "snapshot",
  "refs": "aria",
  "targetId": "浏览器标签 ID"
}
```

**核心动作**：
- `status` - 检查状态
- `snapshot` - 获取页面快照
- `act` - UI 操作（点击、输入等）
- `screenshot` - 截图
- `navigate` - 导航

#### `nodes` - 节点管理
```json
{
  "action": "status",
  "node": "节点 ID"
}
```

**功能**：
- 设备状态检查
- 相机截图/录像
- 屏幕录制
- 位置获取
- 设备通知

---

## 🧠 三、记忆系统

### 3.1 记忆文件结构

```
workspace/
├── MEMORY.md           # 长期记忆（精选）
└── memory/
    ├── 2026-03-09.md  # 每日日志
    └── 2026-03-08.md  # 昨日日志
```

**读取规则**：
- 主会话：启动时读取 TODAY.md + YESTERDAY.md + MEMORY.md
- 子会话：只读取 TODAY.md + YESTERDAY.md

### 3.2 记忆工具

#### `memory_search` - 语义搜索
- 基于向量相似度
- 返回片段 + 行号范围
- 支持混合搜索

#### `memory_get` - 读取具体文件
- 读取具体 Markdown 文件
- 支持行范围读取
- 路径校验（只能访问 memory/目录）

### 3.3 记忆特性

**Hybrid Search（混合搜索）**：
- 向量相似度 + BM25 关键词
- 权重可配置（默认 0.7:0.3）

**Temporal Decay（时间衰减）**：
- 旧内容权重自动降低
- 半衰期可配置（默认 30 天）
- MEMORY.md 不受衰减

**MMR Re-ranking**：
- 去重功能
- 平衡相关性和多样性
- lambda=0.7 默认

---

## 📅 四、定时任务（Cron）

### 4.1 两种执行模式

#### Main Session（主会话）
```json
{
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "提醒内容"
  },
  "wakeMode": "now"
}
```

**特点**：
- 在下一个心跳时运行
- 触发心跳检查
- 使用主会话上下文

#### Isolated Session（独立会话）
```json
{
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "任务内容"
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram"
  }
}
```

**特点**：
- 独立的 cron 会话
- 每次运行新建会话
- 可配置输出投递

### 4.2 任务调度

**调度类型**：
- `at` - 一次性时间点
- `every` - 固定间隔（毫秒）
- `cron` - cron 表达式

**示例**：
```bash
# 每天早上 7 点运行
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "Summarize yesterday" \
  --announce
```

### 4.3 输出投递模式

1. **announce** - 投递到聊天频道 + 主会话摘要
2. **webhook** - POST 到指定 URL
3. **none** - 不输出

---

## 💬 五、会话管理

### 5.1 会话修剪（Session Pruning）

**目的**：减少上下文大小，降低缓存成本

**修剪模式**：
- `off` - 不修剪
- `cache-ttl` - 基于 TTL 修剪

**修剪策略**：
- `ttl` - TTL 时长（默认 5 分钟）
- `keepLastAssistants` - 保留最后 N 个助手消息（默认 3）
- `softTrimRatio` - 软修剪比例（默认 0.3）
- `hardClearRatio` - 硬清除比例（默认 0.5）

**修剪内容**：
- 只修剪 `toolResult` 消息
- 保留用户 + 助手消息
- 图片块不会被修剪

### 5.2 会话压缩（Session Compaction）

**触发条件**：上下文接近上限

**压缩步骤**：
1. 记忆刷新提醒
2. 压缩历史对话
3. 保存压缩结果

**压缩策略**：
- `short` - 5 分钟保留
- `long` - 1 小时保留
- `unlimited` - 不限制

---

## 🔄 六、流式输出

### 6.1 流式输出模式

#### Block Streaming（块流式）
- 按块发送完整消息
- 适合长回复
- 可配置块大小

**控制参数**：
- `blockStreamingDefault` - 默认开关
- `blockStreamingBreak` - 何时断块（`text_end` / `message_end`）
- `blockStreamingChunk` - 块大小限制
- `humanDelay` - 模拟人类打字延迟

#### Preview Streaming（预览流式）
- 临时预览消息更新
- 最终替换为完整回复

**通道支持**：
- Telegram ✅
- Discord ✅
- Slack ✅

### 6.2 分块算法

```
缓冲 ≥ minChars → 等待更多
缓冲 ≥ maxChars → 强制分块
```

**智能切分**：
- 优先在段落/句子边界切分
- 代码块不切分
- 保持 Markdown 格式完整

---

## ⚙️ 七、配置系统

### 7.1 配置层级

1. **Global** - 全局配置
2. **Agent-specific** - 特定代理配置
3. **Session-specific** - 会话级配置

### 7.2 关键配置

#### 工具权限
```json
{
  "tools": {
    "profile": "coding",
    "allow": ["group:fs", "group:runtime"],
    "deny": ["browser"]
  }
}
```

#### 内存搜索
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "local",
        "fallback": "none"
      }
    }
  }
}
```

#### 会话管理
```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "5m"
      },
      "maxConcurrent": 4
    }
  }
}
```

---

## 🔒 八、安全机制

### 8.1 权限控制

**工具权限**：
- `tools.allow` - 白名单
- `tools.deny` - 黑名单（优先级更高）
- `tools.profile` - 预设配置

**执行权限**：
- `elevated` - 需要提升权限
- `security` - 安全级别（`deny`/`allowlist`/`full`）
- `ask` - 询问模式（`off`/`on-miss`/`always`）

### 8.2 沙箱机制

**沙箱级别**：
- `inherit` - 继承父环境
- `require` - 必须沙箱化

**访问控制**：
- `workspaceAccess` - 工作区访问级别（`rw`/`ro`/`none`）
- `sessionToolsVisibility` - 工具可见性范围

---

## 📊 九、性能优化

### 9.1 缓存策略

**Prompt Caching**（Anthropic）：
- 缓存 TTL 5 分钟
- 修剪过期内容
- 降低缓存写入成本

**Embedding Cache**：
- SQLite 存储嵌入向量
- 增量更新
- 减少重新索引

### 9.2 队列管理

**队列模式**：
- `collect` - 收集消息批量处理（默认）
- `steer` - 立即插队处理
- `followup` - 等待当前任务完成
- `steer-backlog` - 插队 + 保留后续

**队列参数**：
- `debounceMs` - 防抖延迟（默认 1000ms）
- `cap` - 队列上限（默认 20）
- `drop` - 溢出策略（`old`/`new`/`summarize`）

---

## 🎯 十、最佳实践

### 10.1 记忆管理

**原则**：
- 重要决策 → 写入 MEMORY.md
- 日常记录 → 写入 daily notes
- 不要依赖 RAM（会话重启会丢失）

**实践**：
```bash
# 定期整理记忆
# 1. 阅读 recent daily notes
# 2. 提取重要信息到 MEMORY.md
# 3. 清理过期内容
```

### 10.2 任务调度

**主会话任务**：
- 简短提醒
- 心跳检查
- 即时通知

**独立任务**：
- 长时间运行
- 批量处理
- 定时任务

### 10.3 工具使用

**避免循环**：
- 使用 `loopDetection` 防止死循环
- 设置合理的超时时间
- 监控工具调用频率

**资源管理**：
- 合理使用浏览器工具
- 控制节点操作范围
- 避免重复 API 调用

---

## 📝 十一、命令行工具速查

### 11.1 Gateway 管理
```bash
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
```

### 11.2 代理运行
```bash
openclaw agent --to +1234567890 --message "任务内容"
openclaw agent --agent ops --message "运行任务" --deliver
openclaw agent --session-id 123 --message "任务" --thinking medium
```

### 11.3 Cron 管理
```bash
# 添加任务
openclaw cron add --name "任务名" --cron "0 7 * * *" --session isolated --message "内容"

# 查看任务
openclaw cron list
openclaw cron runs --id <job-id>

# 运行任务
openclaw cron run <job-id>
openclaw cron run <job-id> --due
```

### 11.4 会话管理
```bash
# 查看会话
openclaw sessions list
openclaw sessions history --session-key main

# 发送消息
openclaw sessions send --session-key main --message "内容"
```

---

## 🎓 十二、学习收获

### 核心要点回顾

1. **网关架构** - 所有操作通过 Gateway 统一管理
2. **会话隔离** - 每个会话独立，互不干扰
3. **记忆持久化** - 所有记忆通过 Markdown 文件存储
4. **工具安全** - 通过权限系统控制工具使用
5. **定时任务** - Cron 系统支持两种执行模式
6. **流式输出** - 块流式 + 预览流式两种方式
7. **性能优化** - 缓存 + 队列 + 修剪策略

### 会话管理深入理解

**会话结构**：
- `sessionKey` - 路由键，标识对话桶
- `sessionId` - 当前会话 ID，对应 transcript 文件
- `sessions.json` - 会话存储，记录元数据
- `*.jsonl` - 对话记录，完整的 conversation tree

**会话生命周期**：
1. 创建新会话（首次消息）
2. 日常对话（追加消息）
3. 修剪工具结果（优化上下文）
4. 压缩历史（当接近上限）
5. 重置或过期（创建新会话）

**自动压缩触发**：
- overflow recovery - 上下文溢出时
- threshold maintenance - 接近阈值时
- 保留 `reserveTokens` 作为安全缓冲

### 关键特性

**NO_REPLY 静默操作**：
- 助手回复以 "NO_REPLY" 开头
- 用户不会看到中间输出
- 用于后台任务（记忆写入、定时检查等）

**Memory Flush**：
- 压缩前的自动记忆刷新
- 防止重要信息被压缩丢失
- 在 softThresholdTokens 触发

**会话修剪 vs 压缩**：
- 修剪：只修剪工具结果，临时操作
- 压缩：总结历史，持久化操作

---

## 💡 十三、实用技巧

### 13.1 高效工具使用

**exec 工具**：
```json
// 后台运行长时间任务
{
  "action": "exec",
  "command": "npm run build",
  "background": true,
  "yieldMs": 30000
}

// 需要 TTY 的命令（如 vim）
{
  "action": "exec",
  "command": "vim config.json",
  "pty": true
}

// 带超时保护
{
  "action": "exec",
  "command": "python script.py",
  "timeout": 600
}
```

**sessions_spawn 技巧**：
```json
// 线程绑定会话（Discord 群聊）
{
  "runtime": "subagent",
  "mode": "session",
  "thread": true
}

// 一次性任务
{
  "runtime": "subagent",
  "mode": "run",
  "cleanup": "delete"
}

// 使用 ACP 模式（Codex/Claude Code）
{
  "runtime": "acp",
  "agentId": "code-executor"
}
```

### 13.2 记忆管理最佳实践

**日常记录**：
- ✅ 立即 commit 到 Git
- ✅ 记录重要决策
- ✅ 记录遇到的问题和解决方案
- ❌ 不要记录敏感信息

**定期整理**：
- 每周整理 MEMORY.md
- 删除过期信息
- 归档重要内容到 archives/

**记忆搜索优化**：
- 使用清晰的关键词
- 混合搜索适合自然语言查询
- 向量搜索适合语义匹配

### 13.3 Cron 任务优化

**主会话 vs 独立任务**：
- 简短提醒 → 主会话
- 长时间运行 → 独立任务
- 需要输出到频道 → 独立任务 + announce

**任务去重**：
- 使用 stagger 减少同时执行
- 配置合理的重试策略
- 使用 lightContext 减少启动开销

### 13.4 性能优化

**降低 Token 消耗**：
- 启用上下文修剪
- 定期压缩会话
- 限制工具结果大小

**优化记忆搜索**：
- 使用本地嵌入（避免 API 调用）
- 启用嵌入缓存
- 合理配置半衰期

---

## 🔮 十四、进阶主题（待学习）

1. **技能系统** - 自定义工具扩展
2. **ACP 架构** - Codex/Claude Code 集成
3. **节点管理** - 设备控制和自动化
4. **Feishu 集成** - 飞书文档和笔记管理
5. **自定义提示词** - 优化系统提示
6. **权限配置** - 细粒度工具访问控制
7. **监控和日志** - 性能和错误追踪
8. **高级 cron** - 复杂调度场景
9. **流式输出优化** - 改进用户体验
10. **安全加固** - 增强权限控制

---

## 📚 十五、参考资料

### 官方文档
- 核心概念：https://docs.openclaw.ai/concepts/
- 网关管理：https://docs.openclaw.ai/gateway/
- 工具系统：https://docs.openclaw.ai/tools/
- 命令行参考：https://docs.openclaw.ai/cli/
- 自动化：https://docs.openclaw.ai/automation/

### 本地文档
- `/home/claw/.openclaw/workspace/docs/` - 本地文档
- `TOOLS.md` - 本地工具笔记
- `AGENTs.md` - 代理配置指南

### 社区资源
- GitHub: https://github.com/openclaw/openclaw
- Discord: https://discord.com/invite/clawd
- ClawHub: https://clawhub.com

---

**学习结束** 🎉

*学习时长：约 1 小时*
*笔记创建时间：2026-03-09 13:05 UTC*
*为明早 7 点汇报准备*

---

## 📋 汇报大纲（明早）

### 1. OpenClaw 是什么（5 分钟）
- 核心概念
- 主要功能
- 适用场景

### 2. 核心架构（10 分钟）
- 网关架构
- 会话管理
- 工具系统
- 记忆机制

### 3. 工具使用（15 分钟）
- 工具分组和权限
- 核心工具详解
- 最佳实践

### 4. 定时任务（10 分钟）
- Cron 系统
- 两种执行模式
- 输出投递

### 5. 会话管理（10 分钟）
- 会话结构
- 修剪和压缩
- 性能优化

### 6. 实操演示（10 分钟）
- 创建子代理
- 配置定时任务
- 管理会话

### 7. Q&A（5 分钟）

**总计：65 分钟**

*备注：准备一些实际案例和截图*
