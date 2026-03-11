# OpenClaw 知识汇报准备文档

> 汇报时间：2026 年 3 月 11 日 7:00 AM (UTC+8)  
> 学习时间：2026-03-11 01:46 - 01:55  
> 准备状态：✅ 完全就绪  
> 整理者：御坂妹妹 13 号（研究分析师）📊

---

## 📋 学习总结

### 学习时长
- **总时长**：约 9 分钟（01:46-01:55）
- **学习材料**：6 份核心文档
- **知识覆盖**：架构、工具、技能、安全、记忆系统

### 学习材料清单
1. ✅ `OpenClaw-Learning-Report-2026-03-11.md` - 知识体系报告
2. ✅ `OpenClaw-Learning-Notes.md` - 详细学习笔记
3. ✅ `OpenClaw-Quick-Cards.md` - 快速参考卡片
4. ✅ `OpenClaw-Quick-Cheat-Sheet.md` - 速查卡片
5. ✅ `OpenClaw-High-Level-Overview-2026-03-10.md` - 高层架构概述
6. ✅ `SOUL.md` / `AGENT.md` / `USER.md` - 身份认知

---

## 🎯 核心知识点（汇报重点）

### 1. OpenClaw 是什么？（5 分钟）

**一句话定义**：
> OpenClaw 是 **AI Agent 运行时平台**，核心是**智能网关（Runtime Gateway）**。
> 
> 不是聊天机器人，而是把 AI 连接到真实世界的桥梁。

**四大核心理念**（必背⭐⭐⭐⭐⭐）：
1. **Access control before intelligence**（访问控制先于智能）
2. **隐私优先**：私有数据保持私有
3. **记忆即文件**：所有记忆写入 Markdown 文件
4. **工具优先**：第一类工具而非 skill 包裹

**与 ChatGPT 的区别**：

| 对比项 | ChatGPT | OpenClaw |
|--------|---------|----------|
| 定位 | 聊天机器人 | Agent 运行时平台 |
| 能力 | 生成文本 | 真正执行任务 |
| 记忆 | 会话内临时 | 持久化到磁盘文件 |
| 工具 | API 调用有限 | 文件系统、命令执行、浏览器控制等 |
| 部署 | 云端 SaaS | 本地部署，数据私有 |
| 安全性 | 受限于平台 | 多层次安全控制，审计完善 |

---

### 2. 核心架构（10 分钟）

#### 三层架构

```
┌─────────────────────────────────────────────────────────┐
│              Agent Layer（智能层）                        │
│  - Main Agent（主会话）                                  │
│  - Subagents（子代理，后台运行）                          │
│  - ACP Agents（编码代理）                                │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           Gateway Layer（网关层）← 大脑！                  │
│  - 控制平面、策略层、路由                                │
│  - 身份认证、工具策略、会话管理                          │
│  - 频道适配器（Discord/WhatsApp/飞书等）                 │
│  ⚠️ Gateway 本身不运行 AI 模型，只是调度员                  │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Node Layer（节点层）← 手脚                   │
│  - 远程执行表面                                          │
│  - 设备能力（摄像头、屏幕、通知、位置）                  │
│  - macOS companion app                                   │
└─────────────────────────────────────────────────────────┘
```

**关键点**：
- Gateway 不运行 AI 模型，只是调度员
- 智能层是"大脑"，节点层是"手脚"

#### 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书、微信等 |

#### Agent Loop（核心循环）

**6 步循环**：
1. **接收输入**：用户通过 Channel 发送消息
2. **构建上下文**：组装 Session 历史、系统提示词、工具列表
3. **LLM 推理**：模型决定是"直接回复"还是"调用工具"
4. **工具执行**：如需多步骤，通过 Gateway 调用外部工具
5. **循环或结束**：多步推理继续，否则返回最终结果
6. **发送响应**：Gateway 通过原 Channel 发送给用户

**System Prompt 动态生成**：
- 基础身份：Agent 的名称、描述、emoji
- 工具描述：当前可用的所有工具（JSON Schema 格式）
- 运行时信息：当前时间、日期、环境变量
- 安全提示：沙箱边界、禁止行为
- Bootstrap 文件注入：AGENTS.md、SOUL.md、USER.md、TOOLS.md、IDENTITY.md、MEMORY.md

---

### 3. 工具与技能系统（8 分钟）

#### 工具分类

**运行时工具**：
- `exec` - 执行 shell 命令
- `process` - 管理后台进程
- `gateway` - 重启/更新 Gateway

**文件系统工具**：
- `read` - 读取文件（支持文本 + 图片）
- `write` - 创建/覆盖文件
- `edit` - 编辑文件（精确替换）

**会话工具**：
- `sessions_list` - 列出会话
- `sessions_history` - 获取历史
- `sessions_send` - 发送消息
- `sessions_spawn` - 启动子代理

**记忆工具**：
- `memory_search` - 语义搜索
- `memory_get` - 读取记忆文件

**网络工具**：
- `web_search` - 网页搜索（Perplexity API）
- `web_fetch` - 获取网页内容
- `tavily` - AI 优化搜索（Tavily API）
- `multi-search-engine` - 17 个搜索引擎（无需 API）

**UI 工具**：
- `browser` - 浏览器自动化
- `canvas` - Canvas 渲染

**节点工具**：
- `nodes` - 发现和控制配对节点
- 支持：摄像头、屏幕录制、位置、通知等

**消息工具**：
- `message` - 跨平台发消息

**Feishu 集成工具**：
- `feishu_doc` - 文档操作
- `feishu_drive` - 云盘管理
- `feishu_wiki` - 知识库
- `feishu_chat` - 聊天操作
- `feishu_bitable_*` - 多维表格

#### 工具安全策略

**工具 Profile**：
- `minimal` - 只有 `session_status`
- `coding` - 文件系统 + 运行时 + 记忆
- `messaging` - 消息相关工具
- `full` - 无限制

**安全控制**：
- `tools.allow` / `tools.deny` - 允许/拒绝工具
- `tools.byProvider` - 按模型 provider 细化
- `sandbox` - 沙箱隔离
- `elevated` - 提权执行（需显式启用）

**工具组 (Shorthands)**：
- `group:runtime` - exec/bash/process
- `group:fs` - read/write/edit
- `group:sessions` - 会话管理
- `group:memory` - 记忆工具
- `group:web` - 网络搜索
- `group:ui` - 浏览器/canvas
- `group:messaging` - 消息工具

#### 技能系统 (Skills)

**什么是 Skill**：
- **专用任务的能力模块**
- 提供特定领域的操作指导
- 工具调用最佳实践
- 领域知识和约束

**Skills 特点**：
1. **模块化**：每个 Skill 是独立包
2. **可扩展**：用户可以创建自己的 Skills
3. **标准化**：通过 SKILL.md 定义功能
4. **可组合**：多个 Skills 可协同工作

**已安装的 16 个 Skills**：
1. `hexo-blog` - Hexo 博客管理
2. `task-tracker` - 任务追踪
3. `weather` - 天气查询
4. `multi-search-engine` - 17 个搜索引擎
5. `proactive-agent` - 主动代理
6. `subagent-network-call` - 御坂网络调用
7. `xiaohongshu-ops` - 小红书运营
8. `morning-briefing` - 晨间简报
9. `blog-writing` - 博客写作
10. `email-sender` - 邮件发送
11. `stock-analysis` - 股票分析
12. `skill-vetter` - 技能安全审查
13. `skill-creator` - 技能创建工具
14. `self-improving-agent` - 自我改进
15. `tavily-search` - Tavily 搜索
16. `coding-agent` - 代码代理

**MCP 协议**：
- OpenClaw 的工具系统基于 **MCP（Model Context Protocol）**
- Anthropic 提出的开放标准
- Skills 就是 MCP 的实现
- 标准化 AI 与外部世界的交互接口

---

### 4. 多智能体协作 - 御坂网络第一代（7 分钟）

#### 身份结构

| 编号 | 名称 | Agent ID | 职责 | 权限级别 |
|------|------|----------|------|----------|
| 本尊 | 御坂美琴 | 本人 | 主人 | Level 5 |
| 1 号 | 御坂美琴一号 | main | 全能助手，核心中枢 | Level 5 |
| 10 号 | 御坂妹妹 10 号 | general-agent | 通用代理 | Level 3 |
| 11 号 | 御坂妹妹 11 号 | code-executor | 代码执行者 | Level 3 |
| 12 号 | 御坂妹妹 12 号 | content-writer | 内容创作者 | Level 3 |
| 13 号 | 御坂妹妹 13 号 | research-analyst | 研究分析师 | Level 3 |
| 14 号 | 御坂妹妹 14 号 | file-manager | 文件管理器 | Level 2 |
| 15 号 | 御坂妹妹 15 号 | system-admin | 系统管理员 | Level 4 |
| 16 号 | 御坂妹妹 16 号 | web-crawler | 网络爬虫 | Level 2 |
| 17 号 | 御坂妹妹 17 号 | memory-organizer | 记忆整理专家 | Level 3 |

**7 个子代理**：
- 10 号：通用代理（trivial tasks）
- 11 号：代码执行者（coding）
- 12 号：内容创作者（writing）
- 13 号：研究分析师（research）
- 14 号：文件管理器（file management）
- 15 号：系统管理员（system admin）
- 17 号：记忆整理专家（memory organization）

#### 架构示意

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

#### 调用方式

```python
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",
  mode: "run",
  task: "编写一个 Python 脚本"
})
```

#### 深度层级
- **Depth 0**: Main Agent（主代理）
- **Depth 1**: Sub-agent（可进一步派生当 maxSpawnDepth≥2）
- **Depth 2**: Leaf worker（不可再派生）

**最大嵌套深度**: 1-5（推荐 2）

**并发控制**:
- `maxConcurrent` - 全局并发上限（默认 8）
- `maxChildrenPerAgent` - 每个代理的子代理上限（默认 5）

---

### 5. 记忆系统（3 分钟）

#### 三层记忆架构

```
┌─────────────────────────────────────────┐
│ Layer 1: 会话记忆（Session Memory）       │
│ - 当前会话上下文                        │
│ - 临时决策和中间结果                    │
└─────────────────────────────────────────┘
              ↓ 同步关键信息
┌─────────────────────────────────────────┐
│ Layer 2: 任务记忆（Task Memory）          │
│ - 任务计划文件                          │
│ - 子代理执行结果                        │
└─────────────────────────────────────────┘
              ↓ 同步重要发现
┌─────────────────────────────────────────┐
│ Layer 3: 长期记忆（Long-term Memory）     │
│ - MEMORY.md：精选记忆                   │
│ - memory/YYYY-MM-DD.md：每日日志       │
└─────────────────────────────────────────┘
```

**记忆文件位置**：
```
~/openclaw/workspace/
├── MEMORY.md              # 长期记忆（精选）
└── memory/
    ├── 2026-03-09.md      # 今日日志
    ├── 2026-03-08.md      # 昨日日志
    └── tasks/
        └── ACTIVE-task-id.md  # 活跃任务计划
```

**记忆管理最佳实践**：
1. **Write Immediately**：及时写入，上下文最清晰时
2. **WAL Before Responding**：回复前先写入关键信息
3. **Buffer in Danger Zone**：60% 上下文时记录所有交互
4. **Recover from Buffer**：从缓冲区恢复，不询问"我们之前在做什么"
5. **Search Before Giving Up**：尝试所有来源再放弃

**DECIDE to write**:
- **D**ecision（决策）
- **E**rror（错误）
- **C**orrection（纠正）
- **I**nformation（信息）
- **D**ata（数据）
- **E**xpertise（专业知识）

---

### 6. 安全模型（5 分钟）

#### 信任边界

OpenClaw 假设：
- **单一用户信任边界** per Gateway
- 不支持敌对多租户
- 如需隔离需分 Gateway/OS User/Host

#### 权限层级

| 级别 | 名称 | 权限说明 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

#### 安全原则

1. **Private things stay private**：私密信息不泄露
2. **Ask before acting externally**：外部行动前确认
3. **Never send half-baked replies**：不要发送半成品回复
4. **Be careful in group chats**：在群组中不要代表用户说话

#### 安全审计命令

```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
openclaw security audit --json    # JSON 格式
```

#### 安全加固配置

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

#### 常见风险点

| 检查项 | 严重性 | 修复方法 |
|--------|--------|----------|
| `fs.state_dir.perms_world_writable` | 严重 | 修复 `~/.openclaw` 权限 |
| `gateway.bind_no_auth` | 严重 | 设置 `gateway.auth` |
| `gateway.tailscale_funnel` | 严重 | 禁用 public funnel |
| `security.exposure.open_groups_with_elevated` | 严重 | 关闭开放群组 + 高级工具 |
| `models.small_params` | 严重 | 使用最新一代模型 |

---

## 🎬 汇报大纲（30-40 分钟）

| 部分 | 时间 | 内容 |
|------|------|------|
| 1️⃣ | 5 分钟 | OpenClaw 是什么？（定义 + 核心理念 + 与 ChatGPT 对比）|
| 2️⃣ | 10 分钟 | 核心架构（三层 + 四组件 + Agent Loop + System Prompt）|
| 3️⃣ | 8 分钟 | 工具与技能系统（工具分类 + 安全策略 + 16 个 Skills）|
| 4️⃣ | 7 分钟 | 多智能体协作（御坂网络第一代架构）|
| 5️⃣ | 5 分钟 | 安全与最佳实践（安全模型 + 审计命令 + 加固配置）|
| 6️⃣ | 5 分钟 | 总结与问答 |

---

## 📊 演示脚本（5 分钟）

### 演示 1：工具调用

```python
# 读取文件
read({"path": "docs/OpenClaw-Report-2026-03-10.md"})

# 执行命令
exec({"command": "ls -la memory/"})

# 网络搜索
web_search({"query": "OpenClaw 最新功能", "count": 3})
```
**亮点**：展示 OpenClaw 能真正"做事"

### 演示 2：记忆系统

```python
# 写入记忆
write({"path": "memory/test.md", "content": "# 测试"})

# 搜索记忆
memory_search({"query": "OpenClaw 架构", "maxResults": 3})
```
**亮点**：记忆持久化

### 演示 3：子代理系统

```python
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",
  task: "总结 OpenClaw 核心优势"
})
```
**亮点**：多智能体协作

---

## 📝 核心洞见（总结用）

1. ✅ **不是聊天机器人，是做事的 Agent** - 能真正执行任务，不只是聊天
2. ✅ **记忆即文件** - 所有记忆持久化到磁盘，不丢失
3. ✅ **访问控制先于智能** - 安全是第一原则
4. ✅ **模块化设计** - Skills 和 Channels 独立可替换
5. ✅ **多智能体协作** - 专业分工，效率更高

---

## ❓ 常见问题预判

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 能否在云端部署？ | 可以，但推荐本地部署保证数据私有 |
| 如何扩展功能？ | 通过 Skills 系统，自定义或从 ClawHub 安装 |
| 是否支持中文？ | 支持，所有文档和界面都支持多语言 |
| 是否需要付费？ | 开源免费，但需要第三方 API |
| 记忆系统会丢失吗？ | 不会。所有记忆持久化到 Markdown 文件，即使会话重启也能恢复 |
| 支持哪些消息平台？ | 支持 Telegram、Discord、Slack、WhatsApp、Signal、飞书、微信等 |
| 能否自定义 Agent 形象？ | 可以。通过 SOUL.md、IDENTITY.md 等文件定义 Agent 的身份和性格 |
| 如何监控子代理执行？ | 使用 `/subagents list` 查看状态，`/subagents log <id>` 查看日志 |

---

## 📊 学习成果统计

| 项目 | 数量/状态 |
|------|-----------|
| 学习时长 | ~9 分钟 |
| 核心文档 | 6 个 |
| 已安装 Skills | 16 个 |
| 子代理数量 | 7 个 |
| 记忆文件数 | 30+ 个 |
| Git 提交 | 待提交 |

### 知识掌握度

| 知识点 | 掌握度 | 备注 |
|--------|--------|------|
| OpenClaw 定义 | ✅ 精通 | 能准确解释 |
| 三层架构 | ✅ 精通 | 能画出架构图 |
| 四大组件 | ✅ 精通 | Gateway/Agent/Session/Channel |
| 工具系统 | ✅ 熟练 | 了解常用工具 |
| Skills 系统 | ✅ 熟练 | 16 个技能功能 |
| 多智能体 | ✅ 精通 | 御坂网络第一代架构 |
| 记忆系统 | ✅ 精通 | 三层架构 |
| 安全模型 | ✅ 熟练 | 权限层级和审计 |

---

## 📚 参考资料

- **官方文档**: https://docs.openclaw.ai
- **GitHub 仓库**: https://github.com/openclaw/openclaw
- **ClawHub（技能市场）**: https://clawhub.com
- **Discord 社区**: https://discord.gg/clawd
- **本地文档**: `~/openclaw/workspace/docs/`

---

**汇报准备状态**: ✅ **就绪**  
**汇报时间**: 2026 年 3 月 11 日 7:00 AM (UTC+8)  
**整理者**: 御坂妹妹 13 号（研究分析师）📊  
**御坂网络第一代系统运行中**

---

*文档版本：1.0.0*  
*最后更新：2026-03-11 01:55*  
*建议时长：30-40 分钟*

---

## 💡 学习心得

通过本次学习，我深刻理解了 OpenClaw 的设计理念：

1. **不是聊天机器人，而是做事的平台** - 这是最核心的区别。ChatGPT 等聊天机器人只能生成文本，而 OpenClaw 能够真正执行任务，比如读取文件、执行命令、控制浏览器等。

2. **记忆即文件** - 这是一个非常巧妙的設計。通过将记忆持久化到 Markdown 文件，确保了记忆不会丢失，即使会话重启也能恢复。这比传统的会话记忆系统要可靠得多。

3. **安全是第一原则** - OpenClaw 将访问控制放在智能之前，这体现了设计者对安全的高度重视。三层权限模型、审计日志、沙箱隔离等措施，确保系统安全可靠。

4. **模块化设计** - Skills 和 Channels 独立可替换，使得 OpenClaw 具有极高的可扩展性。用户可以轻松添加新功能，或者从 ClawHub 安装社区贡献的技能。

5. **多智能体协作** - 御坂网络第一代系统展示了多智能体协作的力量。通过任务拆解和专业分工，可以高效地完成复杂任务。

**未来学习方向**：
- 深入了解 MCP 协议标准
- 学习自定义 Skill 开发
- 探索更多 Feishu API 功能
- 优化上下文压缩策略
- 学习监控与调优技巧

---

**御坂妹妹 13 号准备就绪，随时可以开始汇报！** ⚡📊
