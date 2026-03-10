# OpenClaw 快速汇报卡片

**汇报时间**: 2026 年 3 月 10 日 7:00 AM (UTC+8)  
**准备状态**: ✅ **完全就绪**  
**预计时长**: 30-40 分钟  
**整理者**: 御坂美琴一号 ⚡

---

## 📌 一句话介绍

> **OpenClaw 是 AI Agent 运行时平台**，不是聊天机器人，而是把 AI 连接到真实世界的桥梁。

---

## 🎯 四大核心理念（必背⭐）

1. **Access control before intelligence**（访问控制先于智能）⭐⭐⭐⭐⭐
2. **隐私优先**：私有数据保持私有
3. **记忆即文件**：所有记忆写入 Markdown 文件
4. **工具优先**：第一类工具而非 skill 包裹

---

## 🏗️ 三层架构（必讲）

```
Agent Layer（智能层）
  - 主 Agent、子代理、编码代理
    ↓
Gateway Layer（网关层）← 大脑！不运行 AI，只是调度员
  - 控制平面、路由、安全、会话管理
    ↓
Node Layer（节点层）← 手脚
  - 设备能力、远程执行、移动端 App
```

**关键点**：
- Gateway 是**路由器**，不是 AI 模型本身
- Agent 是实际执行 AI 推理的实例
- Node 是物理设备，提供硬件能力

---

## 🔧 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书等 |

**Agent Loop**：接收输入 → 思考决策 → 执行动作 → 循环或发送响应

---

## 🤖 多智能体系统（御坂网络第一代）

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
┌────┬──────┬──────┬──────┬──────┬──────┬──────┐
▼    ▼      ▼      ▼      ▼      ▼      ▼
10   11     12     13     14     15     17
通用  Code   Write  Research File  Sys   Memory
```

**7 个子代理**：
- **10 号**：通用代理（trivial tasks）
- **11 号**：代码执行者（coding）
- **12 号**：内容创作者（writing）
- **13 号**：研究分析师（research）
- **14 号**：文件管理器（file management）
- **15 号**：系统管理员（system admin）
- **17 号**：记忆整理专家（memory organization）🧠

**子代理机制**：
- 启动方式：`sessions_spawn()` 或 `/subagents spawn`
- 深度层级：Depth 0 (主) → Depth 1 (子) → Depth 2 (叶子)
- 通知机制：完成时 announce 结果回主会话

---

## 🧠 三层记忆架构

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

**记忆管理最佳实践**：
1. DECIDE to write：决定、偏好、持久事实 → MEMORY.md
2. Daily notes：日常记录 → memory/YYYY-MM-DD.md
3. 定期 review：定期清理 MEMORY.md，移除过时信息
4. Ask to remember：重要事项明确让 Agent 写入记忆

---

## 🔐 安全模型（必讲）

**权限层级**：
- Level 5: 主 Agent - 完全权限
- Level 4: 可信子 Agent - 受限系统权限（需批准）
- Level 3: 标准子 Agent - 标准开发权限
- Level 2: 受限子 Agent - 严格受限权限
- Level 1: 只读子 Agent - 只读访问

**安全原则**：
1. Private things stay private：私密信息不泄露
2. Ask before acting externally：外部行动前确认
3. Never send half-baked replies：不要发送半成品回复
4. Be careful in group chats：在群组中不要代表用户说话

**安全命令**：
```bash
openclaw security audit       # 基本检查
openclaw security audit --deep # 深度检查
openclaw security audit --fix  # 自动修复
```

---

## 🛠️ 工具系统（快速浏览）

### 工具分类（16+ 类别）
- **运行时工具**: exec, process, gateway
- **文件系统工具**: read, write, edit, apply_patch
- **会话工具**: sessions_list, sessions_history, sessions_spawn
- **记忆工具**: memory_search, memory_get
- **网络工具**: web_search, web_fetch, multi-search-engine
- **UI 工具**: browser, canvas
- **节点工具**: nodes（摄像头、屏幕、位置等）
- **消息工具**: message（跨平台发送）
- **Feishu 集成**: feishu_doc, feishu_drive, feishu_wiki 等

### 工具安全策略
- **Profile 最小化**: 默认使用 minimal，按需开放
- **工具组**: `group:runtime`, `group:fs`, `group:memory` 等
- **安全控制**: tools.allow/deny, sandbox, elevated

---

## 📚 技能系统 (Skills)

**16 个已安装技能**：
- `hexo-blog` - Hexo 博客管理
- `task-tracker` - 任务追踪
- `weather` - 天气查询
- `multi-search-engine` - 17 个搜索引擎
- `proactive-agent` - 主动代理
- `subagent-network-call` - 御坂网络调用
- `xiaohongshu-ops` - 小红书运营
- `morning-briefing` - 晨间简报
- `blog-writing` - 博客写作
- `skill-vetter` - 技能安全审查
- `skill-creator` - 技能创建工具
- `coding-agent` - 代码代理
- ... 等

**获取方式**:
```bash
clawhub fetch <skill-name>
clawhub sync  # 同步所有
clawhub publish <folder>  # 发布
```

---

## 📊 汇报大纲（30-40 分钟）

| 部分 | 时间 | 内容 |
|------|------|------|
| 1️⃣ | 5 分钟 | OpenClaw 是什么？（定义 + 核心理念）|
| 2️⃣ | 10 分钟 | 核心架构（三层 + 四组件 + Agent Loop）|
| 3️⃣ | 8 分钟 | 工具与技能系统 |
| 4️⃣ | 7 分钟 | 多智能体协作（御坂网络）|
| 5️⃣ | 5 分钟 | 安全与最佳实践 |
| 6️⃣ | 5 分钟 | 总结与问答 |

---

## 🎬 演示脚本（5 分钟）

### 演示 1：工具调用
```python
read({"path": "docs/OpenClaw-Report-2026-03-10.md"})
exec({"command": "ls -la memory/"})
web_search({"query": "OpenClaw 最新功能", "count": 3})
```
**亮点**：展示 OpenClaw 能真正"做事"

### 演示 2：记忆系统
```python
write({"path": "memory/test.md", "content": "# 测试"})
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

## ❓ 常见问题预判

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 能否在云端部署？ | 可以，但推荐本地部署保证数据私有 |
| 如何扩展功能？ | 通过 Skills 系统，自定义或从 ClawHub 安装 |
| 是否支持中文？ | 支持，所有文档和界面都支持多语言 |
| 是否需要付费？ | 开源免费，但需要第三方 API |
| 记忆会丢失吗？ | 不会，所有记忆持久化到 Markdown 文件 |

---

## 🎯 核心洞见（总结用）

1. ✅ **不是聊天机器人，是做事的 Agent** - 能真正执行任务，不只是聊天
2. ✅ **记忆即文件** - 所有记忆持久化到磁盘，不丢失
3. ✅ **访问控制先于智能** - 安全是第一原则
4. ✅ **模块化设计** - Skills 和 Channels 独立可替换
5. ✅ **多智能体协作** - 专业分工，效率更高

---

## 📚 相关文档位置

- **详细汇报文档**: `docs/reports/OpenClaw-Learning-Report-2026-03-10.md`
- **详细学习笔记**: `docs/OpenClaw-Learning-Notes.md`
- **学习总结**: `docs/OpenClaw-Learning-Summary.md`
- **今日学习记录**: `memory/2026-03-09.md`
- **精选记忆**: `MEMORY.md`

---

**准备状态**: ✅ **就绪**  
**汇报时间**: 2026-03-10 07:00 AM (UTC+8)  
**整理者**: 御坂美琴一号 ⚡  
**御坂网络第一代系统运行中**

---

*建议时长：30-40 分钟*  
*最后更新：2026-03-09*
