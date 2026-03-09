# OpenClaw 学习汇报摘要

**汇报时间**: 2026-03-10 07:00 UTC
**学习准备**: 2026-03-09 13:03-13:05 UTC

---

## 📌 OpenClaw 核心概念（1 页）

**定义**: OpenClaw 是一个 AI 代理网关平台，提供统一的消息处理、会话管理、工具调用和自动化能力。

**核心价值**:
- 多渠道理由整合（WhatsApp、Telegram、Discord、Slack 等）
- 独立的会话管理系统
- 强大的工具调用框架
- 内置定时任务系统
- 灵活的子代理架构

**适用场景**:
- 个人助手（日程管理、消息处理、自动化）
- 团队协作文档管理
- 跨平台消息聚合
- 自动化任务执行

---

## 🏗️ 核心架构（1 页）

```
用户 → Gateway → Session Manager → Agent Runtime → Tools → LLM → Reply
```

**关键组件**:
1. **Gateway**: 中央处理枢纽（消息路由、会话管理、定时调度）
2. **Session Manager**: 会话隔离和上下文管理
3. **Agent Runtime**: 提示词管理、工具调用、流式输出
4. **Tools**: 内置工具（exec、browser、nodes 等）+ 插件系统

**数据流**:
```
Inbound Message → Queue → Session Resolution → Context Build → Tool Calls → LLM → Outbound Reply
```

---

## 🛠️ 核心工具系统（1 页）

**工具分组**（用于权限管理）:
- `group:runtime` - 运行时工具（exec、bash）
- `group:fs` - 文件系统工具（read、write、edit）
- `group:sessions` - 会话管理工具
- `group:memory` - 记忆工具（memory_search、memory_get）
- `group:web` - 网络工具（web_search、web_fetch）
- `group:ui` - UI 工具（browser、canvas）
- `group:automation` - 自动化工具（cron、gateway）
- `group:nodes` - 节点管理工具

**核心工具**:
1. `exec` - 执行 Shell 命令
2. `sessions_spawn` - 启动子代理
3. `memory_search` - 语义记忆搜索
4. `browser` - 浏览器控制
5. `nodes` - 节点管理

**使用要点**:
- 工具调用使用 JSON 格式（typed tools）
- 通过权限组控制工具访问
- 注意超时和后台运行设置

---

## 🧠 记忆系统（1 页）

**记忆文件结构**:
```
workspace/
├── MEMORY.md           # 长期记忆（精选重要信息）
└── memory/
    ├── 2026-03-10.md  # 今日日志
    └── 2026-03-09.md  # 昨日日志
```

**记忆工具**:
- `memory_search` - 语义搜索（向量 + BM25 混合搜索）
- `memory_get` - 读取具体文件

**高级特性**:
- **混合搜索**: 向量相似度 (0.7) + BM25 关键词 (0.3)
- **时间衰减**: 旧内容权重自动降低（半衰期 30 天）
- **MMR 去重**: 避免返回重复内容
- **引用标注**: 显示来源路径和行号

**最佳实践**:
- 重要决策写入 MEMORY.md
- 日常记录写入 daily notes
- 立即 Git commit
- 定期整理记忆

---

## 📅 定时任务系统（1 页）

**两种执行模式**:

1. **主会话模式**
   - 在下一个心跳时运行
   - 触发心跳检查
   - 使用主会话上下文
   - 适合简短提醒和即时通知

2. **独立会话模式**
   - 独立的 cron 会话
   - 每次运行新建会话
   - 可配置输出投递
   - 适合长时间运行和批量任务

**任务调度类型**:
- `at` - 一次性时间点
- `every` - 固定间隔（毫秒）
- `cron` - cron 表达式

**输出投递模式**:
- `announce` - 投递到聊天频道 + 主会话摘要
- `webhook` - POST 到指定 URL
- `none` - 不输出

**示例**:
```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "Summarize yesterday" \
  --announce
```

---

## 💬 会话管理（1 页）

**会话结构**:
- `sessionKey` - 路由键（标识对话桶）
- `sessionId` - 当前会话 ID（对应 transcript 文件）
- `sessions.json` - 会话存储（元数据）
- `*.jsonl` - 对话记录（完整 conversation tree）

**会话生命周期**:
1. 创建新会话
2. 日常对话（追加消息）
3. 修剪工具结果（优化上下文）
4. 压缩历史（当接近上限）
5. 重置或过期（创建新会话）

**修剪策略**:
- `cache-ttl` - 基于 TTL 修剪（默认 5 分钟）
- 保留最后 N 个助手消息（默认 3）
- 软修剪和硬清除策略
- 只修剪工具结果消息

**压缩触发**:
- overflow recovery - 上下文溢出时
- threshold maintenance - 接近阈值时（reserveTokens 作为安全缓冲）

---

## 🔄 流式输出（1 页）

**两种流式输出**:

1. **Block Streaming（块流式）**
   - 按块发送完整消息
   - 适合长回复
   - 可配置块大小和断点

2. **Preview Streaming（预览流式）**
   - 临时预览消息更新
   - 最终替换为完整回复
   - 支持 Telegram/Discord/Slack

**分块算法**:
- 低限：缓冲 ≥ minChars 才发出
- 高限：缓冲 ≥ maxChars 强制分块
- 智能切分：优先在段落/句子边界
- 代码块保护：不切分代码块

**控制参数**:
- `blockStreamingDefault` - 默认开关
- `blockStreamingBreak` - 何时断块
- `humanDelay` - 模拟人类打字延迟

---

## ⚙️ 配置系统（1 页）

**配置层级**:
1. Global - 全局配置
2. Agent-specific - 特定代理配置
3. Session-specific - 会话级配置

**关键配置**:

工具权限:
```json
{
  "tools": {
    "profile": "coding",
    "allow": ["group:fs", "group:runtime"],
    "deny": ["browser"]
  }
}
```

内存搜索:
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

会话管理:
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

## 🔒 安全机制（1 页）

**权限控制**:
- `tools.allow` - 白名单
- `tools.deny` - 黑名单（优先级更高）
- `tools.profile` - 预设配置
- `elevated` - 需要提升权限

**执行安全**:
- `security` - 安全级别（deny/allowlist/full）
- `ask` - 询问模式（off/on-miss/always）
- `timeout` - 超时保护

**沙箱机制**:
- `inherit` - 继承父环境
- `require` - 必须沙箱化
- `workspaceAccess` - 工作区访问级别（rw/ro/none）

**实践建议**:
- 最小权限原则
- 定期审计工具权限
- 避免敏感信息存储
- 启用询问模式

---

## 🎯 最佳实践（1 页）

**记忆管理**:
- 重要决策 → MEMORY.md
- 日常记录 → daily notes
- 立即 Git commit
- 定期整理

**任务调度**:
- 简短提醒 → 主会话
- 长时间运行 → 独立任务
- 需要输出 → 独立任务 + announce

**工具使用**:
- 避免死循环（使用 loopDetection）
- 设置合理超时
- 监控工具调用频率
- 使用后台运行长时间任务

**性能优化**:
- 启用上下文修剪
- 定期压缩会话
- 使用本地嵌入
- 启用嵌入缓存

**会话管理**:
- 定期清理过期会话
- 监控 Token 使用情况
- 配置合理的压缩策略
- 利用 NO_REPLY 静默操作

---

## 📊 命令行工具速查

### Gateway 管理
```bash
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
```

### 代理运行
```bash
openclaw agent --to +1234567890 --message "任务内容"
openclaw agent --agent ops --message "运行任务" --deliver
openclaw agent --session-id 123 --message "任务" --thinking medium
```

### Cron 管理
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

### 会话管理
```bash
openclaw sessions list
openclaw sessions history --session-key main
openclaw sessions send --session-key main --message "内容"
```

---

## 💡 下一步学习计划

1. 实践配置自己的 Agent
2. 熟悉工具调用流程
3. 建立记忆管理规范
4. 配置定时任务
5. 学习子代理使用
6. 探索技能系统扩展
7. 了解 ACP 架构集成
8. 学习节点管理和设备控制
9. 深入优化提示词配置
10. 实践安全加固

---

**汇报准备完成** ✅

*学习时长：约 1 小时*
*笔记位置：`/home/claw/.openclaw/workspace/memory/2026-03-09-openclaw-learning.md`*
*摘要位置：`/home/claw/.openclaw/workspace/memory/2026-03-10-openclaw-summary.md`*
