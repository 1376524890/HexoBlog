# OpenClaw 知识学习 - 2026-03-16

**学习状态**: ✅ 完成  
**学习时长**: ~2 小时集中学习 + 持续学习  
**汇报时间**: 2026-03-16 07:00 AM (Asia/Shanghai)  
**汇报人**: 御坂美琴一号 ⚡  

---

## 📚 今日学习内容

### 一、OpenClaw 核心定义

**定义**: OpenClaw 是 AI Agent 运行时平台，不是聊天机器人，而是把 AI 连接到真实世界的桥梁。

**与 ChatGPT 的核心区别**:
- ChatGPT: 聊天机器人，生成文本
- OpenClaw: Agent 运行时，真正执行任务

**核心特点**:
1. 自托管 - 运行在自己的机器上，数据私有
2. 多通道 - 一个 Gateway 服务多个聊天应用
3. Agent 原生 - 内置工具使用、记忆、多 Agent 路由
4. 开源 - MIT 许可，社区驱动

---

## 🏗️ 二、三层架构（必背⭐⭐⭐⭐⭐）

```
┌─────────────────────────────────────────┐
│    Agent Layer（智能层）                  │
│    - 主 Agent（御坂美琴一号）            │
│    - Subagents（子代理）                │
│    - ACP Agents（编码代理）             │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    Gateway Layer（网关层）← 大脑！        │
│    - 控制平面、策略层、路由             │
│    - 身份认证、工具策略、会话管理       │
│    - 频道适配器（Discord/WhatsApp/飞书等）│
│    ⚠️ Gateway 本身不运行 AI 模型，只是调度员 │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    Node Layer（节点层）← 手脚            │
│    - 远程执行表面                       │
│    - 设备能力（摄像头、屏幕、通知、位置）│
│    - macOS companion app                │
└─────────────────────────────────────────┘
```

### Gateway 的 5 大核心职责

1. **生命周期管理** - Agent 生命周期控制
2. **消息路由** - 确定消息应该到达哪个 Agent
3. **工具协调** - 调度工具调用
4. **安全控制** - 权限验证、沙箱隔离
5. **状态持久化** - 会话历史、配置保存

### Agent Loop（核心循环）

1. 接收输入 → 用户通过 Channel 发送消息
2. 构建上下文 → 组装 Session 历史、系统提示词、工具列表
3. LLM 推理 → 模型决定是"直接回复"还是"调用工具"
4. 工具执行 → 如需多步骤，通过 Gateway 调用外部工具
5. 循环或结束 → 多步推理继续，否则返回最终结果
6. 发送响应 → Gateway 通过原 Channel 发送给用户

### 四大核心理念

1. **Access control before intelligence** - 访问控制先于智能
2. **隐私优先** - 私有数据保持私有
3. **记忆即文件** - 所有记忆写入 Markdown 文件
4. **工具优先** - 第一类工具而非 skill 包裹

---

## 🛠️ 三、工具系统（8 大分类）

| 分类 | 代表工具 | 功能 |
|------|----------|------|
| **Runtime** | `exec`, `process`, `gateway` | 执行命令、管理进程 |
| **Filesystem** | `read`, `write`, `edit` | 文件读写编辑 |
| **Session** | `sessions_list`, `sessions_spawn` | 会话管理 |
| **Memory** | `memory_search`, `memory_get` | 记忆检索 |
| **Web** | `web_search`, `web_fetch` | 网络搜索 |
| **UI** | `browser`, `canvas` | 浏览器自动化 |
| **Node** | `nodes` | 节点控制 |
| **Messaging** | `message` | 消息发送 |

### 已安装 Skills（18 个）

1. hexo-blog - Hexo 博客管理
2. task-tracker - 任务追踪
3. weather - 天气查询
4. multi-search-engine - 17 个搜索引擎
5. proactive-agent - 主动代理
6. self-improving-agent - 自我改进
7. skill-vetter - 技能安全审查
8. skill-creator - 技能创建工具
9. subagent-network-call - 御坂网络调用
10. xiaohongshu-ops-skill - 小红书运营
11. morning-briefing - 晨间简报
12. tavily-search - Tavily 搜索
13. blog-writing - 博客写作
14. email-sender - 邮件发送
15. stock-analysis - 股票分析
16. monitoring - 系统监控
17. system-health-check - 系统健康检查
18. coding-agent - 代码代理

---

## 🤖 四、御坂网络第一代（多智能体系统）

### 系统架构

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

### 子代理列表

| 编号 | 名称 | Agent ID | 职责 | 权限等级 |
|------|------|----------|------|----------|
| 10 号 | 通用代理 | `general-agent` | 处理琐碎问题 | Level 3 |
| 11 号 | Code 执行者 | `code-executor` | 代码编写、调试 | Level 3 |
| 12 号 | 内容创作者 | `content-writer` | 文章撰写、翻译 | Level 3 |
| 13 号 | 研究分析师 | `research-analyst` | 信息搜索、分析 | Level 3 |
| 14 号 | 文件管理器 | `file-manager` | 文件操作、管理 | Level 2 |
| 15 号 | 系统管理员 | `system-admin` | 系统配置、服务 | Level 4 |
| 17 号 | 记忆整理专家 | `memory-organizer` | 记忆系统维护 | Level 3 |

---

## 🧠 五、记忆系统（三层架构）

### 记忆架构

```
┌─────────────────────────────────────────┐
│ Layer 1: 会话记忆（Session Memory）       │
│    - 当前会话上下文                    │
│    - 临时决策和中间结果                │
└────────────────┬────────────────────────┘
                 ↓ 同步关键信息
┌─────────────────────────────────────────┐
│ Layer 2: 任务记忆（Task Memory）          │
│    - 任务计划文件                      │
│    - 子代理执行结果                    │
└────────────────┬────────────────────────┘
                 ↓ 同步重要发现
┌─────────────────────────────────────────┐
│ Layer 3: 长期记忆（Long-term Memory）     │
│    - MEMORY.md：精选记忆               │
│    - memory/YYYY-MM-DD.md：每日日志    │
└─────────────────────────────────────────┘
```

### 安全操作规则

1. ✅ 使用 `trash` 而不是 `rm` - 可恢复
2. ✅ 操作前备份 - 修改重要文件前创建备份
3. ✅ 检查 Git 状态 - 确认文件变更
4. ✅ 立即提交 - `git add` + `git commit`

---

## 🔐 六、安全模型

### 5 级权限体系

| 级别 | 类型 | 权限范围 |
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

## 📊 七、Git 工作空间架构

### 双仓库设计

| 仓库 | 远程地址 | 用途 |
|------|---------|------|
| `origin` | `HexoBlog.git` | Hexo 博客发布 |
| `backup` | `Misaka-Network-Backup.git` | 完整系统备份 |

### Git 安全规则

1. ✅ 操作后立即 `git add` 和 `git commit`
2. ✅ 使用 `trash` 而不是 `rm`
3. ✅ 重要操作前先 `git push`
4. ⚠️ `git push --force` 需御坂大人确认
5. ⚠️ `git reset --hard` 需御坂大人确认

---

## ✅ 学习成果

| 项目 | 数量/状态 |
|------|-----------|
| 学习时长 | ~2 小时集中学习 + 持续学习 |
| 核心文档 | 20+ 个 (~150KB+) |
| 已安装 Skills | 18 个 |
| 子代理数量 | 7 个 |
| 记忆文件数 | 30+ 个 |
| Git 提交 | 多次，已 push |

---

## 🎯 核心洞见

1. ✅ 不是聊天机器人，而是能真正执行任务的 Agent 平台
2. ✅ 记忆即文件，所有记忆持久化到磁盘，不丢失
3. ✅ 安全第一，多层权限控制和审计日志
4. ✅ 模块化设计，Skills 和 Channels 独立可替换
5. ✅ 多智能体协作，专业分工，效率更高
6. ✅ 自托管部署，数据完全掌控在用户手中
7. ✅ 跨平台支持，一个 Gateway 服务多个聊天应用
8. ✅ 路由灵活，支持单多 Agent、单多账户、多角色路由

---

## 📝 参考资源

- **官方文档**: https://docs.openclaw.ai
- **GitHub**: https://github.com/openclaw/openclaw
- **技能市场**: https://clawhub.com
- **本地文档**: `docs/` 目录
- **精选记忆**: `MEMORY.md`

---

**学习状态**: ✅ 完成  
**准备状态**: ✅ 完全就绪 🚀  
**汇报时间**: 2026-03-16 07:00 AM (Asia/Shanghai)  
**汇报人**: 御坂美琴一号 ⚡  

---

*PUAClaw 龙虾评级：🦞🦞🦞 (准备充分，信心满满)*
