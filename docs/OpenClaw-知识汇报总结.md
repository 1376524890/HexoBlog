# OpenClaw 知识汇报总结

**汇报时间**: 2026 年 3 月 12 日 7:00 AM (UTC+8)  
**准备状态**: ✅ 完成  
**整理者**: 御坂美琴一号

---

## 一、OpenClaw 是什么？

**一句话**: OpenClaw 是 **AI Agent 运行时平台**，不是聊天机器人，而是把 AI 连接到真实世界的桥梁。

**四大核心理念**（必背）：
1. Access control before intelligence（访问控制先于智能）⭐⭐⭐⭐⭐
2. 隐私优先：私有数据保持私有
3. 记忆即文件：所有记忆写入 Markdown 文件
4. 工具优先：第一类工具而非 skill 包裹

**与 ChatGPT 的区别**：

| 对比项 | ChatGPT | OpenClaw |
|--------|---------|----------|
| 定位 | 聊天机器人 | Agent 运行时平台 |
| 能力 | 生成文本 | 真正执行任务 |
| 记忆 | 会话内临时 | 持久化到磁盘文件 |
| 部署 | 云端 SaaS | 本地部署，数据私有 |

---

## 二、核心架构

### 三层架构

```
Agent Layer（智能层）
  - Main Agent、Subagents、ACP Agents
    ↓
Gateway Layer（网关层）← 大脑！不运行 AI，只是调度员
  - 控制平面、路由、安全、会话管理
    ↓
Node Layer（节点层）← 手脚
  - 设备能力、远程执行、移动端 App
```

### 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书等 |

### Agent Loop（6 步工作流程）

1. 接收输入 → 用户通过 Channel 发送消息
2. 构建上下文 → 组装 Session 历史、系统提示词、工具列表
3. LLM 推理 → 模型决定是"直接回复"还是"调用工具"
4. 工具执行 → 如需多步骤，通过 Gateway 调用外部工具
5. 循环或结束 → 多步推理继续，否则返回最终结果
6. 发送响应 → Gateway 通过原 Channel 发送给用户

---

## 三、工具系统

### 8 大工具分类

1. **Runtime Tools**: exec, process, gateway
2. **Filesystem Tools**: read, write, edit
3. **Session Tools**: sessions_spawn, sessions_list
4. **Memory Tools**: memory_search, memory_get
5. **Web Tools**: web_search, web_fetch
6. **UI Tools**: browser, canvas
7. **Node Tools**: nodes
8. **Messaging Tools**: message

### Feishu 集成

| 工具 | 功能 |
|------|------|
| feishu_doc | 文档操作（读写、编辑、创建表格） |
| feishu_drive | 云盘文件管理 |
| feishu_wiki | 知识库导航 |
| feishu_bitable_* | 多维表格操作 |

### 安全策略

- **工具 Profile**: minimal/coding/messaging/full
- **安全控制**: tools.allow/deny, sandbox, elevated
- **工具组 Shorthands**: group:runtime, group:fs, group:sessions 等

---

## 四、技能系统 (Skills)

### 什么是 Skill？

Skill 是**专用任务的能力模块**，提供特定领域的操作指导和最佳实践。

### 已安装的 16 个 Skills

1. hexo-blog - Hexo 博客管理
2. task-tracker - 任务追踪
3. weather - 天气查询
4. multi-search-engine - 17 个搜索引擎
5. proactive-agent - 主动代理
6. subagent-network-call - 御坂网络调用
7. xiaohongshu-ops - 小红书运营
8. morning-briefing - 晨间简报
9. blog-writing - 博客写作
10. email-sender - 邮件发送
11. stock-analysis - 股票分析
12. skill-vetter - 技能安全审查
13. skill-creator - 技能创建工具
14. self-improving-agent - 自我改进
15. tavily-search - Tavily 搜索
16. monitoring - 系统监控

### 常用 Skills 详解

#### Task Tracker（任务追踪）
- 复杂任务拆解为可执行步骤
- 持久化存储到 workspace/memory/tasks/
- 会话重启后恢复任务状态

#### Proactive Agent（主动代理）
- WAL 协议：Write-Ahead Logging 记录关键信息
- 工作缓冲区：在上下文危险区记录所有交互
- 自主定时任务：独立于主会话执行后台任务

---

## 五、会话和子代理机制

### Session（会话）

Session 是 OpenClaw 的**有状态会话容器**。

#### Context 管理 - Compaction（压缩）机制

- 当历史消息超过阈值时智能总结和裁剪
- 保留关键信息的同时释放空间

**手动触发**: `/compact "专注于决策和待办事项"`

### 子代理 (Subagent)

子代理是从主会话启动的**后台代理运行**。

#### 启动方式

```python
sessions_spawn({
  task: "研究 XX 主题",
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",      # run=单次，session=持久
  label: "任务标签"
})
```

**Slash 命令**:
- `/subagents list` - 列出所有子代理
- `/subagents kill <id>` - 杀死子代理
- `/subagents log <id>` - 查看日志
- `/subagents steer <id> <msg>` - 向子代理发送消息

---

## 六、记忆系统

### 三层记忆架构

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

### 记忆文件位置

```
~/openclaw/workspace/
├── MEMORY.md              # 长期记忆（精选）
└── memory/
    ├── 2026-03-12.md      # 今日日志
    └── tasks/
        └── ACTIVE-task-id.md  # 活跃任务计划
```

### 安全操作规则

1. ✅ 使用 `trash` 而不是 `rm`
2. ✅ 操作前备份
3. ✅ 检查 Git 状态
4. ✅ 立即提交

---

## 七、御坂网络第一代（多智能体系统）

### 7 个子代理

| 编号 | 名称 | Agent ID | 职责 |
|------|------|----------|------|
| 10 号 | 通用代理 | general-agent | 处理琐碎问题 |
| 11 号 | 代码执行者 | code-executor | 代码编写、调试 |
| 12 号 | 内容创作者 | content-writer | 文章撰写、翻译 |
| 13 号 | 研究分析师 | research-analyst | 信息搜索、分析 |
| 14 号 | 文件管理器 | file-manager | 文件操作、管理 |
| 15 号 | 系统管理员 | system-admin | 系统配置、服务 |
| 17 号 | 记忆整理专家 | memory-organizer | 记忆系统维护 🧠 |

### 架构示意

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

---

## 八、安全模型

### 权限层级

| 级别 | 名称 | 权限说明 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

### 安全审计命令

```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
```

---

## 九、汇报大纲（30-40 分钟）

| 部分 | 时间 | 内容 |
|------|------|------|
| 1️⃣ | 5 分钟 | OpenClaw 是什么？（定义 + 核心理念）|
| 2️⃣ | 10 分钟 | 核心架构（三层 + 四组件 + Agent Loop）|
| 3️⃣ | 8 分钟 | 工具与技能系统 |
| 4️⃣ | 7 分钟 | 多智能体协作（御坂网络）|
| 5️⃣ | 5 分钟 | 安全与最佳实践 |
| 6️⃣ | 5 分钟 | 总结与问答 |

---

## 十、核心洞见（总结用）

1. ✅ **不是聊天机器人，是做事的 Agent** - 能真正执行任务，不只是聊天
2. ✅ **记忆即文件** - 所有记忆持久化到磁盘，不丢失
3. ✅ **访问控制先于智能** - 安全是第一原则
4. ✅ **模块化设计** - Skills 和 Channels 独立可替换
5. ✅ **多智能体协作** - 专业分工，效率更高

---

## 十一、常见问题 (FAQ)

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 能否在云端部署？ | 可以，但推荐本地部署保证数据私有 |
| 如何扩展功能？ | 通过 Skills 系统，自定义或从 ClawHub 安装 |
| 是否支持中文？ | 支持，所有文档和界面都支持多语言 |
| 是否需要付费？ | 开源免费，但需要第三方 API |

---

**准备状态**: ✅ **完全就绪**  
**汇报时间**: 2026 年 3 月 12 日 7:00 AM (UTC+8)  
**整理者**: 御坂美琴一号 ⚡  
**御坂网络第一代系统运行中**
