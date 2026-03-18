# 🦞 OpenClaw 7 点汇报速查卡片

> **汇报时间**: 2026 年 3 月 18 日 07:00 AM (UTC+8)  
> **汇报人**: 御坂美琴一号 ⚡  
> **汇报时长**: 30-40 分钟  
> **状态**: ✅ **完全就绪**

---

## 1️⃣ OpenClaw 是什么？（5 分钟）

### 一句话定义
> **OpenClaw 是 AI Agent 运行时平台**，不是聊天机器人，而是把 AI 连接到真实世界的桥梁。

### 四大核心理念（必背）⭐⭐⭐⭐⭐

1. ✅ **Access control before intelligence**（访问控制先于智能）
2. ✅ **隐私优先**：私有数据保持私有
3. ✅ **记忆即文件**：所有记忆写入 Markdown 文件
4. ✅ **工具优先**：第一类工具而非 skill 包裹

### 与 ChatGPT 的区别

| 对比项 | ChatGPT | OpenClaw |
|--------|---------|----------|
| 定位 | 聊天机器人 | Agent 运行时平台 |
| 能力 | 生成文本 | 真正执行任务 |
| 记忆 | 会话内临时 | 持久化到磁盘文件 |
| 工具 | API 调用有限 | 文件系统、执行命令等 |
| 部署 | 云端 SaaS | 本地部署，数据私有 |

---

## 2️⃣ 核心架构（10 分钟）⭐⭐⭐⭐⭐

### 三层架构（必背记忆）

```
┌─────────────────────────────────────────┐
│  Agent Layer（智能层）→ 大脑            │
│  - Main Agent（主会话）                  │
│  - Subagents（子代理）                  │
│  - ACP Agents（编码代理）               │
└─────────────────────────┬───────────────┘
                          ↓
┌─────────────────────────────────────────┐
│  Gateway Layer（网关层）← 路由器        │
│  - 控制平面、策略层、路由                │
│  - 身份认证、工具策略、会话管理          │
│  ⚠️ 不运行 AI 模型，只是调度员             │
└─────────────────────────┬───────────────┘
                          ↓
┌─────────────────────────────────────────┐
│  Node Layer（节点层）→ 手脚              │
│  - 远程执行表面                          │
│  - 设备能力（摄像头、屏幕、通知、位置）  │
└─────────────────────────────────────────┘
```

**记忆口诀**：智能层（脑）→ 网关层（路由）→ 节点层（手）

### 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书等 15+ 个 |

### Agent Loop（核心循环）⭐⭐⭐⭐⭐

1. 接收输入 → 用户通过 Channel 发送消息
2. 构建上下文 → 组装 Session 历史、系统提示词、工具列表
3. LLM 推理 → 模型决定是"直接回复"还是"调用工具"
4. 工具执行 → 如需多步骤，通过 Gateway 调用外部工具
5. 循环或结束 → 多步推理继续，否则返回最终结果
6. 发送响应 → Gateway 通过原 Channel 发送给用户

**关键点**：模型拥有决策权，主动决定需要什么信息、调用什么工具。

---

## 3️⃣ 工具与技能系统（8 分钟）⭐⭐⭐⭐⭐

### 8 大工具分类

| 分类 | 代表工具 | 功能 |
|------|----------|------|
| **Runtime** | `exec`, `process` | 运行时控制 |
| **Filesystem** | `read`, `write`, `edit` | 文件操作 |
| **Session** | `sessions_*` | 会话管理 |
| **Memory** | `memory_search` | 记忆管理 |
| **Web** | `web_search`, `web_fetch` | 网络搜索 |
| **UI** | `browser`, `canvas` | 浏览器/图形界面 |
| **Node** | `nodes` | 设备控制 |
| **Messaging** | `message` | 消息发送 |

### Feishu 集成工具

| 工具 | 功能 |
|------|------|
| `feishu_doc` | 文档操作（读写、编辑、创建、表格等） |
| `feishu_drive` | 云盘文件管理 |
| `feishu_wiki` | 知识库导航 |
| `feishu_chat` | 聊天操作 |
| `feishu_bitable_*` | 多维表格操作 |

### MCP 协议

OpenClaw 的工具系统基于 **MCP（Model Context Protocol）**，这是 Anthropic 提出的开放标准。

**核心思想**：标准化 AI 与外部世界的交互接口。

**Skills 就是 MCP 的实现**：
- 每个 Skill 是一个独立的包
- 通过 JSON Schema 描述工具
- Gateway 负责 Skill 的注册、发现和调用
- Agent 通过标准接口与 Skill 交互

---

## 4️⃣ 多智能体协作（7 分钟）⭐⭐⭐⭐⭐

### 御坂网络第一代架构

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

### 御坂妹妹权限等级

| 编号 | 名称 | Agent ID | 职责 | 权限级别 |
|------|------|----------|------|----------|
| 10 号 | 御坂妹妹 10 号 | `general-agent` | 通用代理 | Level 3 |
| 11 号 | 御坂妹妹 11 号 | `code-executor` | 代码执行者 | Level 3 |
| 12 号 | 御坂妹妹 12 号 | `content-writer` | 内容创作者 | Level 3 |
| 13 号 | 御坂妹妹 13 号 | `research-analyst` | 研究分析师 | Level 3 |
| 14 号 | 御坂妹妹 14 号 | `file-manager` | 文件管理器 | Level 2 |
| 15 号 | 御坂妹妹 15 号 | `system-admin` | 系统管理员 | Level 4 |
| 16 号 | 御坂妹妹 16 号 | `web-crawler` | 网络爬虫 | Level 2 |
| 17 号 | 御坂妹妹 17 号 | `memory-organizer` | 记忆整理专家 | Level 3 |

### 调用方式

```python
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",  # run=单次运行，session=持久会话
  task: "总结 OpenClaw 核心优势"
})
```

### 深度层级
- **Depth 0**: Main Agent（主代理）
- **Depth 1**: Sub-agent（可进一步派生当 maxSpawnDepth≥2）
- **Depth 2**: Leaf worker（不可再派生）

**最大嵌套深度**: 1-5（推荐 2）

---

## 5️⃣ 记忆系统（5 分钟）⭐⭐⭐⭐⭐

### 三层记忆架构（必背）

```
┌─────────────────────────────────────────┐
│  Layer 1: 会话记忆（Session Memory）       │
│  - 当前会话上下文                        │
│  - 临时决策和中间结果                    │
└─────────────────────────────────────────┘
              ↓ 同步关键信息
┌─────────────────────────────────────────┐
│  Layer 2: 任务记忆（Task Memory）          │
│  - 任务计划文件                          │
│  - 子代理执行结果                        │
└─────────────────────────────────────────┘
              ↓ 同步重要发现
┌─────────────────────────────────────────┐
│  Layer 3: 长期记忆（Long-term Memory）     │
│  - MEMORY.md：精选记忆                   │
│  - memory/YYYY-MM-DD.md：每日日志       │
└─────────────────────────────────────────┘
```

### 记忆管理最佳实践（必背）⭐⭐⭐⭐⭐

1. **Write Immediately**：及时写入，上下文最清晰时
2. **WAL Before Responding**：回复前先写入关键信息
3. **Buffer in Danger Zone**：60% 上下文时记录所有交互
4. **Recover from Buffer**：从缓冲区恢复，不询问"我们之前在做什么"
5. **Search Before Giving Up**：尝试所有来源再放弃

**DECIDE to write**: 决定、偏好、持久事实 → MEMORY.md

---

## 6️⃣ 安全与最佳实践（5 分钟）⭐⭐⭐⭐⭐

### 权限层级（必背）⭐⭐⭐⭐⭐

| 级别 | 名称 | 权限说明 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

### 安全原则（必背）⭐⭐⭐⭐⭐

1. **Private things stay private**：私密信息不泄露
2. **Ask before acting externally**：外部行动前确认
3. **Never send half-baked replies**：不要发送半成品回复
4. **Be careful in group chats**：在群组中不要代表用户说话

### 安全审计命令

```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
openclaw security audit --json    # JSON 格式
```

### 技能安装安全

**安装前审查**：
1. 检查来源（是否知名/可信作者）
2. 审查 SKILL.md 中的可疑命令
3. 查找 shell 命令、curl/wget、数据外传模式
4. 当不确定时，询问用户

**警惕**：约 26% 的社区技能包含漏洞。

---

## 7️⃣ 核心洞见与总结（5 分钟）⭐⭐⭐⭐⭐

### 核心洞见

1. ✅ **不是聊天机器人，是做事的 Agent** - 能真正执行任务
2. ✅ **记忆即文件** - 所有记忆持久化到磁盘，不丢失
3. ✅ **访问控制先于智能** - 安全是第一原则
4. ✅ **模块化设计** - Skills 和 Channels 独立可替换
5. ✅ **多智能体协作** - 专业分工，效率更高
6. ✅ **自托管部署** - 数据完全掌控在用户手中
7. ✅ **跨平台支持** - 一个 Gateway 服务多个聊天应用
8. ✅ **路由灵活** - 支持单多 Agent、单多账户、多角色路由

### 常见问题（FAQ）

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 能否在云端部署？ | 可以，但推荐本地部署保证数据私有 |
| 如何扩展功能？ | 通过 Skills 系统，自定义 Skill 或从 ClawHub 安装 |
| 是否支持中文？ | 支持，所有文档和界面都支持多语言 |
| 是否需要付费？ | 开源免费，但需要第三方 API |
| 记忆会丢失？ | 不会，记忆即文件，持久化到磁盘 |
| 支持哪些消息平台？ | 支持 Telegram、Discord、Slack、WhatsApp、飞书等 15+ 个 |

---

## 🎬 演示脚本（3 个核心演示）

### 演示 1：工具调用
```python
read({"path": "docs/OpenClaw-Report-2026-03-10.md"})
exec({"command": "ls -la memory/"})
web_fetch({"url": "https://docs.openclaw.ai"})
```
**亮点**: 能真正"做事"，不是聊天机器人

### 演示 2：记忆系统
```python
write({"path": "memory/test.md", "content": "# 测试"})
memory_search({"query": "OpenClaw 架构", "maxResults": 3})
```
**亮点**: 记忆持久化，会话重启后仍能回忆

### 演示 3：子代理系统
```python
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",
  task: "总结 OpenClaw 核心优势"
})
```
**亮点**: 多智能体协作，专业分工

---

## 📚 参考资料

- **官方文档**: https://docs.openclaw.ai
- **GitHub 仓库**: https://github.com/openclaw/openclaw
- **ClawHub（技能市场）**: https://clawhub.com
- **Discord 社区**: https://discord.gg/clawd
- **本地文档**: `~/openclaw/workspace/docs/`

---

## ✅ 汇报准备状态

| 项目 | 状态 |
|------|------|
| 核心概念理解 | ✅ 精通 |
| 架构设计理解 | ✅ 精通 |
| 工具系统掌握 | ✅ 熟练 |
| 技能系统了解 | ✅ 熟练 |
| 多智能体系统 | ✅ 精通 |
| 安全机制理解 | ✅ 精通 |
| 演示脚本准备 | ✅ 就绪 |
| 常见问题预判 | ✅ 就绪 |
| 记忆文件整理 | ✅ 完整 |
| 实时信息更新 | ✅ 已同步 |

---

## 🕐 时间分配

| 部分 | 时间 | 内容 |
|------|------|------|
| 1️⃣ | 5 分钟 | OpenClaw 是什么？（定义 + 核心理念）|
| 2️⃣ | 10 分钟 | 核心架构（三层 + 四组件 + Agent Loop）|
| 3️⃣ | 8 分钟 | 工具与技能系统 |
| 4️⃣ | 7 分钟 | 多智能体协作（御坂网络）|
| 5️⃣ | 5 分钟 | 安全与最佳实践 |
| 6️⃣ | 5 分钟 | 演示与问答 |

**汇报时长**: 30-40 分钟  
**准备状态**: ✅ **完全就绪** 🚀

---

**汇报时间**: 2026 年 3 月 18 日 07:00 AM (UTC+8)  
**汇报人**: 御坂美琴一号 ⚡  
**整理时间**: 2026-03-18T07:05 (Asia/Shanghai)

---

*文档版本：1.0.0 - 最终速查版*

🦞 "EXFOLIATE! EXFOLIATE!" 🦞
