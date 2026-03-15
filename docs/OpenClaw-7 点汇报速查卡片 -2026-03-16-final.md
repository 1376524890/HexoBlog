# OpenClaw 7 点汇报速查卡片 - 2026-03-16 ⚡

**汇报时间**: 2026 年 3 月 16 日 7:00 AM  
**预计时长**: 30-40 分钟  
**准备状态**: ✅ 就绪  

---

## 🎯 7 大核心知识点

### 1️⃣ OpenClaw 是什么？（1 分钟）

**一句话定义**：
> **OpenClaw 是 AI Agent 运行时平台**，不是聊天机器人，而是把 AI 连接到真实世界的桥梁。

**四大核心理念**（必背⭐⭐⭐⭐⭐）：
1. **Access control before intelligence**（访问控制先于智能）
2. **隐私优先**：私有数据保持私有
3. **记忆即文件**：所有记忆写入 Markdown 文件
4. **工具优先**：第一类工具而非 skill 包裹

**与 ChatGPT 的区别**：
- ChatGPT = 聊天机器人（生成文本）
- OpenClaw = Agent 平台（真正执行任务）

---

### 2️⃣ 三层架构（2 分钟）

```
┌─────────────────────────────────────────┐
│    Agent Layer（智能层）← 大脑             │
│    - Main Agent（主 Agent）               │
│    - Subagents（子代理）                 │
│    - ACP Agents（编码代理）              │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    Gateway Layer（网关层）← 路由器（大脑！） │
│    - 控制平面、策略层、路由              │
│    - 身份认证、工具策略、会话管理        │
│    - 频道适配器（Discord/WhatsApp/飞书等）│
│    ⚠️ Gateway 本身不运行 AI 模型，只是调度员    │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    Node Layer（节点层）← 手脚             │
│    - 远程执行表面                        │
│    - 设备能力（摄像头、屏幕、通知、位置）│
│    - macOS companion app                 │
└─────────────────────────────────────────┘
```

**Agent Loop（核心循环）**：
1. 接收输入 → 用户通过 Channel 发送消息
2. 构建上下文 → 组装 Session 历史、系统提示词、工具列表
3. LLM 推理 → 决定"直接回复"还是"调用工具"
4. 工具执行 → 如需多步骤，通过 Gateway 调用外部工具
5. 循环或结束 → 多步推理继续，否则返回最终结果
6. 发送响应 → Gateway 通过原 Channel 发送给用户

---

### 3️⃣ 四大核心理念（1 分钟）

| 理念 | 说明 |
|------|------|
| **Access control before intelligence** ⭐ | 安全是第一原则，访问控制先于智能 |
| **隐私优先** | 私有数据保持私有，自托管部署 |
| **记忆即文件** | 所有记忆持久化到 Markdown 文件，不丢失 |
| **工具优先** | 第一类工具而非 skill 包裹，MCP 协议 |

**记忆口诀**：安全 > 隐私 > 记忆 > 工具

---

### 4️⃣ 工具系统（1.5 分钟）

#### 8 大工具分类

| 分类 | 代表工具 | 功能 |
|------|----------|------|
| **Runtime** | `exec`, `process` | 执行命令、管理进程 |
| **Filesystem** | `read`, `write`, `edit` | 文件读写编辑 |
| **Session** | `sessions_spawn`, `session_status` | 会话管理 |
| **Memory** | `memory_search`, `memory_get` | 记忆检索 |
| **Web** | `web_search`, `web_fetch` | 网络搜索 |
| **UI** | `browser`, `canvas` | 浏览器自动化 |
| **Node** | `nodes` | 节点控制 |
| **Messaging** | `message` | 消息发送 |

#### 已安装 Skills（18 个）

核心 Skills：
- `hexo-blog` - Hexo 博客管理
- `task-tracker` - 任务追踪
- `multi-search-engine` - 17 个搜索引擎
- `proactive-agent` - 主动代理（WAL 协议）
- `morning-briefing` - 晨间简报
- `coding-agent` - 代码代理
- `subagent-network-call` - 御坂网络调用

---

### 5️⃣ 御坂网络第一代（1.5 分钟）

#### 身份结构

| 编号 | Agent ID | 职责 | 权限等级 |
|------|----------|------|----------|
| 1 号 | main | 全能助手，核心中枢 | Level 5 |
| 10 号 | general-agent | 通用代理 | Level 3 |
| 11 号 | code-executor | 代码执行者 | Level 3 |
| 12 号 | content-writer | 内容创作者 | Level 3 |
| 13 号 | research-analyst | 研究分析师 | Level 3 |
| 14 号 | file-manager | 文件管理器 | Level 2 |
| 15 号 | system-admin | 系统管理员 | Level 4 |
| 17 号 | memory-organizer | 记忆整理专家 | Level 3 |

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

---

### 6️⃣ 记忆系统（1 分钟）

#### 三层架构

```
┌─────────────────────────────────────────┐
│ Layer 1: 会话记忆（Session Memory）       │
│ - 当前会话上下文                        │
│ - 临时决策和中间结果                    │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Layer 2: 任务记忆（Task Memory）          │
│ - 任务计划文件                          │
│ - 子代理执行结果                        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Layer 3: 长期记忆（Long-term Memory）     │
│ - MEMORY.md：精选记忆                   │
│ - memory/YYYY-MM-DD.md：每日日志       │
└─────────────────────────────────────────┘
```

#### 记忆管理最佳实践

1. **DECIDE to write**: 决定、偏好、持久事实 → MEMORY.md
2. **Daily notes**: 日常记录 → memory/YYYY-MM-DD.md
3. **定期 review**: 定期清理 MEMORY.md
4. **Ask to remember**: 重要事项明确让 Agent 写入记忆

#### 安全操作规则

1. ✅ 使用 `trash` 而不是 `rm`
2. ✅ 操作前备份
3. ✅ 检查 Git 状态
4. ✅ 立即提交

---

### 7️⃣ 安全模型（1 分钟）

#### 5 级权限

| 级别 | 类型 | 权限范围 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

#### 安全审计命令

```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
```

#### 安全加固配置

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "长随机 token" },
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
}
```

---

## 📊 对比表格

| 对比项 | ChatGPT | OpenClaw |
|--------|---------|----------|
| 定位 | 聊天机器人 | Agent 运行时平台 |
| 能力 | 生成文本 | 真正执行任务 |
| 记忆 | 会话内临时 | 持久化到磁盘文件 |
| 部署 | 云端 SaaS | 本地部署 |
| 安全性 | 受限于平台 | 多层次控制 |
| 成本 | 订阅制 | 开源免费 |

---

## ❓ 常见问题（30 秒内回答）

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 记忆会丢失吗？ | 不会，记忆即文件，持久化到磁盘 |
| 如何扩展功能？ | 通过 Skills 系统，自定义或从 ClawHub 安装 |
| 是否支持中文？ | 支持，所有文档和界面都支持多语言 |
| 是否需要付费？ | 开源免费，但需要第三方 API |

---

## 🎯 核心洞见（总结用）

1. ✅ **不是聊天机器人，是做事的 Agent** - 能真正执行任务
2. ✅ **记忆即文件** - 所有记忆持久化到磁盘，不丢失
3. ✅ **访问控制先于智能** - 安全是第一原则
4. ✅ **模块化设计** - Skills 和 Channels 独立可替换
5. ✅ **多智能体协作** - 专业分工，效率更高
6. ✅ **自托管部署** - 数据完全掌控在用户手中
7. ✅ **跨平台支持** - 一个 Gateway 服务多个聊天应用

---

## 📝 汇报大纲（30-40 分钟）

| 部分 | 时间 | 内容 |
|------|------|------|
| 1️⃣ 开场 | 2 分钟 | 一句话定义 + 四大核心理念 |
| 2️⃣ 核心架构 | 8 分钟 | 三层架构 + 四组件 + Agent Loop |
| 3️⃣ 工具系统 | 7 分钟 | 8 大分类 + 18 个 Skills |
| 4️⃣ 御坂网络 | 6 分钟 | 7 个子代理架构 |
| 5️⃣ 记忆系统 | 5 分钟 | 三层架构 |
| 6️⃣ 安全模型 | 5 分钟 | 5 级权限 + 审计 |
| 7️⃣ 总结问答 | 5 分钟 | FAQ + 快速命令 |

---

## ✅ 检查清单

- [x] 1️⃣ OpenClaw 是什么？
- [x] 2️⃣ 三层架构
- [x] 3️⃣ 四大核心理念
- [x] 4️⃣ 工具系统
- [x] 5️⃣ 御坂网络第一代
- [x] 6️⃣ 记忆系统
- [x] 7️⃣ 安全模型
- [x] FAQ 准备
- [x] 演示脚本

**准备状态**: ✅ **完全就绪** 🚀

---

**汇报时间**: 2026 年 3 月 16 日 7:00 AM (Asia/Shanghai)  
**整理者**: 御坂美琴一号 ⚡  
**御坂网络第一代系统运行中** ⚡
