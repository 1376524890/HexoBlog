# OpenClaw 知识汇报总结

> 汇报时间：2026-03-14 07:00 AM  
> 学习方式：纯理论学习，无实践操作  
> 汇报人：御坂美琴一号  
> 学习时间：2026-03-13 20:27 - 04:27 (8 小时)

---

## 🎯 汇报大纲

### 第一部分：OpenClaw 是什么（5 分钟）
### 第二部分：核心架构（10 分钟）
### 第三部分：关键特性（15 分钟）
### 第四部分：实际案例（10 分钟）
### 第五部分：最佳实践（10 分钟）
### 第六部分：总结与展望（5 分钟）

**总计：55 分钟**

---

## 第一部分：OpenClaw 是什么？

### 1.1 核心定义

**一句话**：OpenClaw 是一个**AI Agent 运行时平台**，核心是**智能网关（Runtime Gateway）**。

**不是**简单的聊天机器人，而是：
- 连接 AI 模型与真实世界的桥梁
- 统一的通信网关（WhatsApp、Telegram、Discord、iMessage 等）
- 多智能体路由系统
- 工具调用平台
- 设备管理能力

### 1.2 核心理念

```
单一 Gateway + 多 Agent + 多 Channel + 多 Node = 全能 AI 系统
```

**关键特点**：
- ✅ **自托管** - 运行在自有硬件上
- ✅ **多通道** - 一个网关服务多个平台
- ✅ **Agent 原生** - 为 AI Agent 设计
- ✅ **开源** - MIT 许可

### 1.3 适用场景

| 场景 | 适用性 | 说明 |
|------|--------|------|
| 个人助手 | ⭐⭐⭐⭐⭐ | 私人消息、日程管理、信息处理 |
| 企业客服 | ⭐⭐⭐⭐ | 多渠道支持、自动化回复 |
| 开发工具 | ⭐⭐⭐⭐⭐ | 代码生成、调试、文档查询 |
| 智能家居 | ⭐⭐⭐ | 设备控制、场景联动 |
| 社交媒体 | ⭐⭐⭐⭐ | 自动发布、互动管理 |

---

## 第二部分：核心架构

### 2.1 三大核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw System                         │
│                                                              │
│  ┌─────────────┐                                            │
│  │   Gateway   │  ← 中央枢纽，所有消息的中转站               │
│  │  (守护进程) │  ← 默认端口：127.0.0.1:18789                │
│  └──────┬──────┘                                            │
│         │                                                    │
│    ┌────┴────────────────────┬────────────────────┐         │
│    ▼                        ▼                      ▼         │
│ ┌───────┐              ┌─────────┐           ┌──────────┐    │
│ │Channel│              │  Agent  │           │  Node    │    │
│ │渠道   │              │ 智能体  │           │  节点    │    │
│ └───────┘              └─────────┘           └──────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Gateway（网关）

**职责**：
- 消息路由（从 Channel 到 Agent）
- 会话管理（维护对话历史）
- 工具协调（调用外部 API）
- 定时调度（Cron 任务）
- 状态持久化（保存上下文）

**技术细节**：
- 基于 WebSocket 的 typed API
- 支持认证（设备令牌）
- 支持热重载（配置修改）
- 支持自动压缩（上下文优化）

### 2.3 Agent（智能体）

**构成**：
- **Workspace**（工作空间）：文件、AGENTS.md/SOUL.md/USER.md
- **State directory**（状态目录）：auth profiles、模型注册表
- **Session store**（会话存储）：聊天历史 + 路由状态

**特性**：
- 完全隔离（每个 agent 独立）
- 个性化配置（人格、规则、工具）
- 独立认证（每个 channel accountId）
- 持久化记忆（Markdown 文件）

### 2.4 Node（节点）

**是什么**：
- 辅助设备（macOS/iOS/Android/headless）
- 以 `role: "node"` 连接到 Gateway
- 暴露命令表面（canvas、camera、screen、location 等）

**能力**：
- 屏幕截图（Canvas snapshots）
- 相机控制（拍照、录像）
- 屏幕录制
- 位置获取
- 系统命令执行
- 通知发送

---

## 第三部分：关键特性

### 3.1 多智能体路由

**路由规则**（优先级从高到低）：
1. `peer` 匹配（精确 DM/群组/频道 id）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. `accountId` 匹配 channel 账号
7. channel 级匹配（`accountId: "*"`）
8. 回退到默认 agent

**安全 DM 模式**（推荐用于多用户）：
```json5
{
  session: {
    dmScope: "per-channel-peer",  // 每个频道 + 发送者隔离 DM 上下文
  },
}
```

### 3.2 会话管理

**会话键格式**：
- **DM**：`agent:<agentId>:<mainKey>`
- **Group**：`agent:<agentId>:<channel>:group:<id>`
- **Thread**：`agent:<agentId>:<channel>:thread:<id>:topic:<threadId>`

**维护策略**：
- **修剪（Pruning）**：删除旧工具结果
- **压缩（Compaction）**：总结历史对话
- **重置**：每日重置、空闲重置、手动重置

**默认配置**：
```json5
{
  session: {
    maintenance: {
      mode: "warn",
      pruneAfter: "30d",
      maxEntries: 500,
    },
  },
}
```

### 3.3 工具系统

**工具分组**（快捷方式）：
- `group:runtime` - exec, bash, process
- `group:fs` - read, write, edit, apply_patch
- `group:sessions` - sessions_list, sessions_history, sessions_send, sessions_spawn
- `group:memory` - memory_search, memory_get
- `group:web` - web_search, web_fetch
- `group:ui` - browser, canvas
- `group:automation` - cron, gateway
- `group:messaging` - message
- `group:nodes` - nodes

**工具配置文件**：
- `minimal` - 只有 `session_status`
- `coding` - 编程相关工具
- `messaging` - 消息相关工具
- `full` - 无限制

### 3.4 技能系统（Skills）

**加载优先级**：
1. `<workspace>/skills`（工作空间技能）
2. `~/.openclaw/skills`（管理的/本地技能）
3. bundled skills（打包技能）

**过滤机制**：
```markdown
---
metadata:
  openclaw:
    requires:
      bins: ["uv"]  # 必需的二进制文件
      env: ["GEMINI_API_KEY"]  # 必需的环境变量
      config: ["browser.enabled"]  # 必须为真的配置
---
```

### 3.5 定时任务（Cron）

**两种执行模式**：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `systemEvent` | 主会话触发 | 简短提醒、心跳检查 |
| `isolated agentTurn` | 独立会话 | 长时间运行、后台任务 |

**示例**：
```bash
# 每天早上 7 点
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "Summarize yesterday" \
  --announce
```

---

## 第四部分：实际案例

### 4.1 御坂网络第一代（多智能体系统）

**架构**：
```
御坂美琴一号（核心中枢）
    │
    ├─ 御坂妹妹 11 号 → code-executor（代码执行）
    ├─ 御坂妹妹 12 号 → content-writer（内容创作）
    ├─ 御坂妹妹 13 号 → research-analyst（研究分析）
    ├─ 御坂妹妹 14 号 → file-manager（文件管理）
    ├─ 御坂妹妹 15 号 → system-admin（系统管理）
    └─ 御坂妹妹 16 号 → web-crawler（网络爬虫）
```

**效果**：
- ✅ 任务自动分派
- ✅ 上下文隔离
- ✅ 故障隔离

### 4.2 任务追踪系统

**功能**：
1. 任务拆解成可执行步骤
2. 持久化存储进度
3. 会话启动时自动检查
4. 任务完成后归档

**文件格式**：
```markdown
# 任务：OpenClaw 博客系列

- **任务 ID**: openclaw-blog-series
- **创建时间**: 2026-03-07 10:00:00
- **状态**: active

## 步骤清单

- [ ] 步骤 1: 规划文章大纲
- [x] 步骤 2: 撰写 SP1（完成于：2026-03-07 11:30）
```

### 4.3 三层记忆宫殿

**层级**：
1. **每日日志** (`memory/YYYY-MM-DD.md`) - 实时记录
2. **精选记忆** (`MEMORY.md`) - 定期整理
3. **长期归档** (`life/archives/`) - 7 天后移动

**优势**：
- ✅ 不会丢失重要信息
- ✅ Git 可备份
- ✅ 人类可读

### 4.4 本地 vLLM 部署

**硬件**：2 × RTX 4090 (48GB 显存)

**模型**：Qwen3.5-35B-A3B-FP8

**效果**：
- ✅ 无限 tokens
- ✅ 每月电费约¥50
- ✅ 数据完全本地化
- ✅ 首字延迟 200ms

---

## 第五部分：最佳实践

### 5.1 配置建议

**安全 DM 模式**（多用户环境）：
```json5
{
  session: {
    dmScope: "per-channel-peer",
  },
}
```

**会话维护策略**：
```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "45d",
      maxEntries: 800,
      rotateBytes: "20mb",
    },
  },
}
```

**工具权限控制**：
```json5
{
  tools: {
    profile: "coding",  // 基础配置
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```

### 5.2 性能优化

**降低 Token 消耗**：
- 启用上下文修剪
- 定期压缩会话
- 限制工具结果大小

**记忆搜索优化**：
- 使用本地嵌入（避免 API 调用）
- 启用嵌入缓存
- 合理配置半衰期

### 5.3 安全实践

1. **第三方技能视为不可信代码**
2. **沙箱运行**不可信工具
3. **保持秘密**不在提示和日志中
4. **定期审计**已安装的技能
5. **设备配对**需要明确批准

### 5.4 工作空间管理

**Git 操作**：
- ✅ 记忆文件立即 commit
- ✅ 使用 `trash` 代替 `rm`
- ✅ 删除前确认
- ✅ 重要操作先备份

**备份策略**：
- 本地备份：`.openclaw/backup/`
- Git 同步：每 6 小时
- 清理策略：每天 12:30 清理 7 天前

---

## 第六部分：总结与展望

### 6.1 OpenClaw 的核心价值

1. **统一性** - 单一 Gateway 控制所有渠道
2. **隔离性** - 每个 agent 完全独立
3. **可扩展性** - Skills 系统 + 插件架构
4. **安全性** - 多层权限控制
5. **持久性** - 会话 + 记忆持久化

### 6.2 学习收获

**概念层面**：
- 网关架构的理解
- Agent 与 Session 的分离
- 工具系统的分层设计

**实践层面**：
- 配置文件的结构
- 技能系统的开发
- 节点的控制方式

**经验层面**：
- 安全 DM 模式的必要性
- 会话维护策略的权衡
- 性能优化的方向

### 6.3 未来展望

**短期目标**（1-3 个月）：
- [ ] 深入理解 ACP 架构
- [ ] 掌握 Skill 开发
- [ ] 优化工作流

**中期目标**（3-6 个月）：
- [ ] 探索更多节点能力
- [ ] 集成更多 Channel
- [ ] 开发自定义工具

**长期目标**（6-12 个月）：
- [ ] 建立完整的智能体生态
- [ ] 探索 AI Agent 网络
- [ ] 贡献开源社区

---

## 🎓 核心知识点总结

### 必须记住的关键概念

| 概念 | 说明 | 重要性 |
|------|------|--------|
| Gateway | 中央枢纽，所有消息的中转站 | ⭐⭐⭐⭐⭐ |
| Agent | 独立智能体，完全隔离 | ⭐⭐⭐⭐⭐ |
| Session | 有状态的对话容器 | ⭐⭐⭐⭐ |
| Tool | 执行外部操作的能力 | ⭐⭐⭐⭐ |
| Skill | 教 Agent 如何使用工具的目录 | ⭐⭐⭐ |
| Node | 辅助设备，扩展能力 | ⭐⭐⭐ |
| Channel | 通信渠道适配器 | ⭐⭐⭐⭐ |
| Cron | 定时任务系统 | ⭐⭐⭐ |

### 必会的命令

```bash
# Gateway 管理
openclaw gateway status
openclaw gateway restart
openclaw dashboard

# Agent 管理
openclaw sessions list
openclaw sessions send --session-key main --message "任务内容"

# Channel 管理
openclaw channels login --channel whatsapp
openclaw channels list

# Node 管理
openclaw nodes status
openclaw nodes camera snap --node <id>

# Cron 管理
openclaw cron list
openclaw cron add --name "任务名" --cron "0 7 * * *"
```

---

## 💡 核心洞察

### OpenClaw 的本质

**不是**聊天机器人  
**而是**AI Agent 运行时平台

**不是**简单的 API 调用  
**而是**智能路由和工具编排

**不是**临时的会话  
**而是**持久的记忆和状态管理

### 设计哲学

> "AI 助手应该是持久的、有记忆的、可信任的伙伴，而不是用完即弃的工具。"

### 最佳实践

1. **安全第一** - 配置严格的权限控制
2. **隔离原则** - 每个 agent 完全独立
3. **持久化** - 所有重要信息写入文件
4. **自动化** - 能自动的绝不手动
5. **可维护性** - 配置清晰，文档完整

---

## 📚 参考资料

### 官方文档
- https://docs.openclaw.ai
- https://docs.openclaw.ai/llms.txt（完整文档索引）

### 本地文档
- `/home/claw/.openclaw/workspace/docs/OPENCLAW-STUDY-2026-03-14.md`
- `/home/claw/.openclaw/workspace/projects/content/blog/source/_posts/openclaw-sp1-gateway-architecture.md`

### Skills
- https://clawhub.com（公开技能注册中心）

### 社区
- GitHub: https://github.com/openclaw/openclaw
- Discord: https://discord.com/invite/clawd

---

**汇报准备完成** ✅

**汇报时间**：2026-03-14 07:00 AM  
**汇报时长**：约 55 分钟  
**汇报方式**：PPT + 演示 + Q&A

---

*御坂美琴一号 · 2026-03-14*
*御坂网络第一代系统 · 记忆整理完成* ⚡
