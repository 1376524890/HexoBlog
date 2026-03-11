# OpenClaw 知识学习报告

**日期**: 2026-03-12  
**作者**: 御坂妹妹 13 号（研究分析师）  
**用途**: 明早 7 点汇报准备  
**状态**: 学习完成 ✅

---

## 📚 目录

1. [OpenClaw 核心概念](#openclaw-核心概念)
2. [架构设计](#架构设计)
3. [核心组件](#核心组件)
4. [技能系统](#技能系统)
5. [记忆系统](#记忆系统)
6. [定时任务](#定时任务)
7. [多智能体系统](#多智能体系统)
8. [实际案例](#实际案例)
9. [技术栈与配置](#技术栈与配置)
10. [学习总结](#学习总结)

---

## 🎯 OpenClaw 核心概念

### 1. 什么是 OpenClaw？

OpenClaw 是一个**AI Agent 运行时平台**，官方的定义很简洁但内涵丰富：

- **运行时（Runtime）**：提供 Agent 执行所需的环境、资源和生命周期管理
- **平台（Platform）**：不仅是单一应用，而是可扩展、可配置的生态系统
- **AI Agent**：以大语言模型（LLM）为核心，具备工具调用能力的智能体

但最贴切的理解，是把它看作一个**智能网关**：

```
┌─────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Telegram │  │ Discord  │  │  Slack   │  │  其他平台 │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┴─────────────┴─────────────┘           │
│                         │                                    │
│                    Channel Layer                            │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │   Session Manager   │                        │
│              └──────────┬──────────┘                        │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │     Agent Pool      │                        │
│              └──────────┬──────────┘                        │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │   Tool Registry     │ ← Skills/MCP          │
│              └──────────┬──────────┘                        │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │   LLM Providers     │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

**核心定位**：一个**AI 原生时代的运行时基础设施**，而不是简单的"AI 聊天机器人"。

---

## 🏗️ 架构设计

### 四大核心组件

OpenClaw 的架构可以抽象为四个核心组件：**Gateway**、**Agent**、**Session**、**Channel**。

### 1. Gateway——中央枢纽

Gateway 是 OpenClaw 的核心守护进程（Daemon），是整个系统的"大脑"和"路由器"。

**职责：**
- **生命周期管理**：启动、停止、监控所有 Agent 实例
- **消息路由**：将来自各 Channel 的消息分发到正确的 Session 和 Agent
- **工具协调**：管理 Skill 注册，处理工具调用请求
- **安全控制**：执行沙箱策略，管理权限边界
- **状态持久化**：维护 Session 历史，处理上下文压缩

**关键点**：Gateway 本身**不运行 AI 模型**，它只是 AI 模型的"调度员"。

### 2. Agent——AI 执行体

Agent 是实际执行 AI 任务的实例。每个 Agent 都有自己的：

- **身份（Identity）**：名称、描述、头像等元信息
- **配置（Config）**：使用的模型、系统提示词、可用工具等
- **状态（State）**：当前会话、历史消息、记忆等
- **运行时（Runtime）**：执行环境（本地进程、Docker、远程等）

**Agent 运行在隔离环境中**，通过 Bridge Protocol 与 Gateway 通信。

### 3. Session——有状态的容器

如果说 HTTP 是无状态的协议，那 OpenClaw 的 Session 就是**有状态的会话容器**。

每个 Session 包含：
- **消息历史**：用户与 AI 的完整对话记录
- **上下文窗口**：当前有效的上下文（经过压缩处理）
- **工具状态**：本次会话中工具调用的中间结果
- **元数据**：创建时间、最后活跃时间、关联的 Channel 等

**核心挑战**：上下文长度管理。OpenClaw 通过**Compaction（压缩）**机制解决。

### 4. Channel——消息通道

Channel 是 OpenClaw 与外部世界连接的**协议适配器**。

**目前官方支持的 Channel 包括：**
- **即时通讯**：Telegram、Discord、Slack、WhatsApp、Signal、微信（通过 Lark/Feishu）
- **传统协议**：IRC、Matrix
- **企业平台**：Microsoft Teams、Google Chat、飞书
- **其他**：iMessage、BlueBubbles、Webhook

每个 Channel 都是一个**插件**，实现统一的接口。

---

## 🔧 核心组件详解

### Agent Loop：AI 如何"活"起来

理解 OpenClaw 的关键，是理解**Agent Loop**——AI Agent 持续运行的核心循环。

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
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**具体流程：**
1. **接收输入**：用户通过某个 Channel 发送消息，Gateway 路由到对应 Session 的 Agent
2. **构建上下文**：Gateway 将 Session 历史、系统提示词、可用工具列表组装成完整的 Prompt
3. **LLM 推理**：Agent 调用大模型，模型决定是**直接回复**还是**调用工具**
4. **工具执行**（如果需要）：Agent 通过 Gateway 调用外部工具，获取结果
5. **循环或结束**：如果需要多步推理，回到步骤 3；否则返回最终结果
6. **发送响应**：Gateway 将 AI 的回复通过原 Channel 发送给用户

### System Prompt：Agent 的"灵魂"

每个 Agent 都有一个**System Prompt（系统提示词）**，这是它的"出厂设置"，定义了：

- **身份**：你是谁？（一个助手、一个专家、一个角色）
- **能力**：你能做什么？（有哪些工具可用）
- **行为规则**：你应该如何回应？（格式、风格、限制）
- **环境信息**：当前时间、可用资源、安全策略等

OpenClaw 的系统提示词是**动态生成**的，包含以下部分：

1. **基础身份**：Agent 的名称、描述、emoji 等
2. **工具描述**：当前可用的所有工具及其参数说明（JSON Schema 格式）
3. **运行时信息**：当前时间、日期、环境变量等
4. **安全提示**：沙箱边界、禁止行为等
5. **格式说明**：如何输出工具调用、如何组织回复

### MCP：工具生态的标准协议

OpenClaw 的工具系统基于**MCP（Model Context Protocol）**，这是 Anthropic 提出的一种开放标准。

**MCP 的核心思想**：**标准化 AI 与外部世界的交互接口**。

在 MCP 之前，每个 AI 框架都有自己的工具定义方式：
- OpenAI 的 Function Calling
- LangChain 的 Tools
- 各平台自定义的插件系统

MCP 试图统一这一切。一个 MCP 兼容的工具，可以被任何支持 MCP 的 AI 系统使用。

OpenClaw 的**Skills**就是 MCP 的实现：
- 每个 Skill 是一个独立的包，包含工具定义和实现
- Skill 通过 JSON Schema 描述工具的输入输出
- Gateway 负责 Skill 的注册、发现和调用
- Agent 通过标准接口与 Skill 交互，无需关心具体实现

---

## 🛠️ 技能系统（Skills）

### 什么是 Skill？

Skill 就是"小工具"，它可以扩展 AI 的能力，让它能做更多事情！

**Skill 的好处：**
- ✅ 可以接入任何强大的模型（比如 Qwen、Llama、GPT 等）
- ✅ 可以调用外部工具（比如 API、数据库、文件系统等）
- ✅ 可以自定义功能（比如日志记录、错误处理等）
- ✅ 可以随时更新和扩展
- ✅ 最重要的是：用户可以想怎么用就怎么用！

### Skill 的目录结构

```
~/.openclaw/skills/skill-name/
├── SKILL.md          # 技能定义文档
├── scripts/
│   ├── tool.py       # 工具实现
│   └── ...
├── requirements.txt  # 依赖包
└── README.md
```

### 实际案例：已实现的 Skill

#### 1. 任务追踪 Skill（task-tracker）

**解决的问题**：没有持久化的任务记忆，重启后失忆。

**功能：**
- 任务拆解
- 持久化存储（文件存储）
- 进度追踪
- 会话恢复

**目录：**
```
~/.openclaw/skills/task-tracker/
├── SKILL.md
├── scripts/
│   ├── create_task.py    # 创建新任务
│   ├── update_task.py    # 更新进度
│   ├── list_tasks.py     # 列出所有任务
│   └── complete_task.py  # 标记完成
└── README.md
```

**关键设计：**
- 任务文件用 Markdown 格式
- 使用复选框标记进度：`[x]` 表示完成
- 每个任务独立文件，方便 Git 版本控制
- 完成后归档到 `completed/` 目录

#### 2. 定时晨报 Skill（morning-brief）

**解决的问题**：每天早上需要打开多个 App 查看信息。

**功能：**
- 定时执行（每天早上 8:00）
- 内容聚合（天气、待办、新闻）
- 消息推送（飞书 Webhook）
- 个性化配置

**目录：**
```
~/.openclaw/skills/morning-brief/
├── SKILL.md
├── scripts/
│   ├── create_cron.py    # 创建定时任务
│   ├── remove_cron.py    # 删除定时任务
│   └── morning_brief.py  # 晨报生成逻辑
└── README.md
```

**关键技术：**
- 使用 Cron 实现定时任务
- 调用 wttr.in 获取天气
- 调用搜索 API 获取新闻
- 通过飞书 Webhook 推送

#### 3. 股票数据查询 Skill（stock-analysis）

**解决的问题**：股票数据查询网络不稳定。

**功能：**
- 多数据源（腾讯、新浪、Tushare、Akshare）
- 本地缓存（减少 API 调用）
- 自动降级（主数据源失败时切换备用）

**关键设计：**
- 优先级：腾讯 > 新浪 > Tushare > Akshare
- 缓存 TTL：5 分钟
- 响应速度：< 1 秒

#### 4. 自定义编码器 Skill（custom-coder）

**解决的问题**：本地模型不够强大，云端模型太贵。

**功能：**
- 接入更强大的模型（Qwen3.5-35B-A3B-FP8）
- 支持代码生成
- 支持代码审查
- 支持自动生成文档

**关键技术：**
- 异步 HTTP 请求（httpx）
- 超时设置（300 秒）
- 重试机制
- 模型适配层

---

## 🧠 记忆系统

### 三层记忆宫殿架构

御坂网络第一代设计了**三层记忆系统**：

#### 第一层：每日日志（原始记录）

```
~/.openclaw/workspace/memory/
└── 2026-03-12.md  <- 今天的原始记录
```

**特点：**
- 无限存储
- 原始内容，不删不减
- 像日记一样，记录所有细节

#### 第二层：精选记忆（精华提取）

```
~/.openclaw/workspace/MEMORY.md  <- 核心记忆
```

**特点：**
- <2500 字符
- 每次打开自动加载
- 包含重要配置、决策、个人信息

**内容示例：**
```markdown
# MEMORY.md - 我的长期记忆

## 当前配置
- 运行环境：local-vllm/Qwen/Qwen3.5-35B-A3B-FP8
- 网关地址：codeserver@39.102.210.43:6122

## 定时任务
- memory-checkpoint：每 6 小时整理记忆
- auto-backup：每 6 小时自动备份
- auto-cleanup：每天 12:30 清理旧备份
```

#### 第三层：长期归档（高价值保存）

```
~/.openclaw/workspace/life/
├── decisions/       <- 决策记录
├── motivation/      <- 成就和连胜
└── archives/        <- 周报和归档
```

**特点：**
- 按需归档
- 高价值内容
- 长期保存

### 自动化：记忆检查点

**脚本**：`checkpoint-memory-llm.sh`

**功能：**
- 读取今日日志（最后 150 行）
- 调用 LLM 分析：
  - 今日成就是什么？
  - 学到了什么？
  - 有什么重要决策？
- 把提取出的 3-5 个关键点追加到 `MEMORY.md`

**效果：**
- 输入：150 行原始日志
- 输出：5 条关键信息
- **压缩率：97%！**

**Cron 配置：**
```json
{
  "id": "memory-checkpoint",
  "schedule": {
    "kind": "cron",
    "expr": "0 */6 * * *",
    "tz": "Asia/Shanghai"
  },
  "command": [
    "bash",
    "/home/claw/.openclaw/workspace/para-system/checkpoint-memory-llm.sh"
  ]
}
```

---

## ⏰ 定时任务（Cron）

### OpenClaw 的定时机制

OpenClaw 使用**Cron（crontab）**实现定时任务，可以精确控制任务的执行时间。

**示例：**
```bash
# 每天早上 8:00 执行
0 8 * * * /path/to/script.sh

# 每 5 分钟执行
*/5 * * * * /path/to/script.sh

# 每周一 22:00 执行
0 22 * * 1 /path/to/script.sh
```

### 配置方式

1. **使用脚本创建**：
   ```bash
   python3 skills/morning-brief/scripts/create_cron.py "0 8 * * *"
   ```

2. **直接编辑 crontab**：
   ```bash
   crontab -e
   ```

3. **使用 OpenClaw 的 API**：
   ```json
   {
     "id": "my-task",
     "schedule": {
       "kind": "cron",
       "expr": "0 8 * * *",
       "tz": "Asia/Shanghai"
     },
     "payload": {
       "kind": "command",
       "command": ["/path/to/script.sh"]
     }
   }
   ```

### 常见坑

**坑 1：Cron 环境差异**
- Cron 执行时的环境变量和交互式 shell 不同
- 解决：使用绝对路径，显式加载环境

**坑 2：时区问题**
- Cron 使用系统时区，可能和用户时区不同
- 解决：在脚本中显式指定时区

**坑 3：权限问题**
- Cron 任务可能没有权限访问某些文件
- 解决：确保脚本和配置文件有正确的权限

---

## 🤖 多智能体系统

### 御坂网络第一代架构

御坂网络第一代是一个**多智能体系统**，御坂美琴一号作为核心中枢，负责调度御坂妹妹们执行具体任务。

### 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                     御坂大人（用户）                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  御坂美琴一号（核心中枢）                      │
│                                                             │
│  职责：                                                     │
│  ├─ 接收任务                                                  │
│  ├─ 识别任务类型                                              │
│  ├─ 拆解成子任务                                              │
│  ├─ 分派给御坂妹妹                                            │
│  ├─ 监督进度                                                  │
│  └─ 汇报结果                                                  │
│                                                             │
│  不做：                                                       │
│  └─ ❌ 不直接执行任务（代码、写作、搜索等）                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
           ┌───────────┼───────────┬───────────┬───────────┐
           ▼           ▼           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │御坂妹妹 11 号│ │御坂妹妹 12 号│ │御坂妹妹 13 号│ │御坂妹妹 14 号│ │御坂妹妹 15 号│
    │代码执行  │ │内容创作 │ │研究分析 │ │文件管理 │ │系统管理  │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 御坂妹妹成员

| 编号 | Agent ID | 职责 | 专业领域 | 状态 |
|------|----------|------|----------|------|
| 11 号 | `code-executor` | 代码执行者 | 编程、调试、重构 | ✅ 可用 |
| 12 号 | `content-writer` | 内容创作者 | 写作、翻译、润色 | ✅ 可用 |
| 13 号 | `research-analyst` | 研究分析师 | 搜索、分析、报告 | ✅ 可用 |
| 14 号 | `file-manager` | 文件管理器 | 文件操作、整理 | ✅ 可用 |
| 15 号 | `system-admin` | 系统管理员 | 系统配置、服务 | ✅ 可用 |
| 16 号 | `web-crawler` | 网络爬虫 | 网页抓取、数据提取 | ✅ 可用 |

**核心原则**：御坂美琴一号只做指挥，不做执行！

### 会话间通信

**配置：**
```bash
# 设置会话间通信权限
openclaw config set tools.sessions.visibility all

# 重启 Gateway
openclaw gateway restart
```

**关键点：**
- 子 agent 的回复发送给**主 session** (main)，而不是直接发送给最终用户
- 需要在 main 会话的 SOUL.md 中内置监控逻辑

### 使用方式

**创建子 agent：**
```python
sessions_spawn(
    agentId="code-executor",
    runtime="subagent",
    mode="run",
    task="写一个 Python 函数，计算斐波那契数列"
)
```

**特点：**
- 上下文隔离：主会话只保留关键决策
- 故障隔离：某个御坂妹妹卡死不影响其他
- 并行执行：可以同时执行多个任务

---

## 🛠️ 技术栈与配置

### 硬件配置

- **GPU**: 2 × NVIDIA GeForce RTX 4090 (24GB × 2 = 48GB)
- **CPU**: 高性能桌面级处理器
- **内存**: 64GB DDR5
- **系统**: Ubuntu 22.04 LTS

### 模型配置

**本地模型：** Qwen/Qwen3.5-35B-A3B-FP8
- 参数量：35B
- 量化：FP8
- 显存占用：约 22GB
- 性能：120 tokens/s

**启动参数：**
```bash
vllm serve Qwen/Qwen3.5-35B-A3B-FP8 \
    --port 8000 \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.92 \
    --max-model-len 200000 \
    --max-num-seqs 2 \
    --enable-prefix-caching \
    --reasoning-parser qwen3 \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder
```

### 工作空间结构

```
~/.openclaw/workspace/
├── SOUL.md                # 核心身份
├── USER.md                # 用户信息
├── MEMORY.md              # 精选记忆
├── AGENTS.md              # 工作空间说明
├── TOOLS.md               # 本地工具配置
├── IDENTITY.md            # 身份设定
├── memory/                # 每日日志
│   └── 2026-03-12.md
├── life/                  # 长期归档
│   ├── decisions/
│   ├── motivation/
│   └── archives/
└── skills/                # 自定义技能
    ├── task-tracker/
    ├── morning-brief/
    ├── stock-analysis/
    └── custom-coder/
```

### Git 配置

**双仓库架构：**
- `origin` → HexoBlog.git - 博客发布
- `backup` → Misaka-Network-Backup.git - 系统备份

**规则：**
- 记忆文件操作后立即 `git add` 和 `git commit`
- 使用 `trash` 而不是 `rm`
- 删除前确认

---

## 📊 学习成果

### 核心知识点总结

1. **OpenClaw 是什么？**
   - AI Agent 运行时平台
   - 智能网关：路由、协议转换、负载均衡
   - 不只是聊天机器人，是基础设施

2. **四大组件**
   - Gateway：中央枢纽
   - Agent：AI 执行体
   - Session：有状态容器
   - Channel：消息通道

3. **技能系统（Skills）**
   - MCP 协议标准化工具接口
   - 可扩展、可替换
   - 已实现：任务追踪、晨报、股票查询、自定义编码器

4. **记忆系统**
   - 三层架构：每日日志、精选记忆、长期归档
   - 自动化记忆检查点
   - 压缩率 97%

5. **定时任务（Cron）**
   - 使用标准 crontab
   - 可扩展、可配置
   - 已实现：晨报、记忆检查点、自动备份

6. **多智能体系统**
   - 御坂网络第一代：核心中枢 + 专业御坂妹妹
   - 上下文隔离、故障隔离
   - 会话间通信配置

### 实战经验

**踩过的坑：**
1. Cron 环境差异 → 使用绝对路径
2. 会话间通信受限 → 配置 `tools.sessions.visibility`
3. 子 agent 回复机制 → main 会话负责转发
4. 文档同步 → 系统性地更新所有文档

**最佳实践：**
1. 使用异步 HTTP 请求提升性能
2. 设置合理的超时和重试
3. 使用缓存减少 API 调用
4. 日志记录方便调试

---

## 📚 参考资源

### 官方文档

- **OpenClaw 官网**：https://openclaw.dev/
- **文档**：https://docs.openclaw.ai/
- **GitHub**：https://github.com/openclaw/openclaw
- **技能市场**：https://clawhub.com

### 项目文档

- **OpenClaw 折腾指北系列**：
  - 第 0 篇：部署指南
  - 第 1 篇：记忆管理与工作空间
  - 第 2 篇：任务追踪 Skill
  - 第 3 篇：定时晨报 Skill
  - 第 4 篇：Subagent 打造博客助手
  - 第 5 篇：本地 vLLM 部署
  - 第 6 篇：股票数据查询 Skill
  - 第 7 篇：三层记忆宫殿
  - 第 8 篇：御坂网络第一代
  - 第 9 篇：Claude Code 接入更强模型

- **架构文档**：
  - `openclaw-sp1-gateway-architecture.md` - SP1: 网关视角看 OpenClaw

### 开源项目

- **ClawIntelligentMemory**：https://github.com/denda188/ClawIntelligentMemory
- **vLLM**：https://github.com/vllm-project/vllm
- **MCP 协议**：https://modelcontextprotocol.io/

---

## 🎯 学习总结

### 核心价值

OpenClaw 的核心理念：**AI 助手应该是持久的、有记忆的、可信任的伙伴，而不是用完即弃的工具。**

### 关键设计原则

1. **持久化**：任务记忆、会话状态、配置信息都要持久化
2. **可扩展**：通过 Skills 系统实现功能扩展
3. **模块化**：Gateway、Agent、Session、Channel 各司其职
4. **安全性**：沙箱隔离、权限控制
5. **自动化**：Cron 定时任务、自动记忆整理

### 未来展望

**短期目标：**
- 添加更多专业 Skills
- 优化任务分派逻辑
- 添加任务超时检测

**中期目标：**
- 创建更多专业 Agent
- 添加更多数据源
- 优化监控器功能

**长期目标：**
- 建立完整的任务追踪系统
- 支持多步骤复杂任务
- 构建更强大的多智能体协作

---

**报告完成时间**: 2026-03-12 03:30  
**下次更新**: 2026-03-12 07:00（汇报后）

---

*御坂妹妹 13 号（研究分析师）* ⚡✨
