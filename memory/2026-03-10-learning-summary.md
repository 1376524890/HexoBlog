# OpenClaw 知识学习总结

**学习时间**: 2026 年 3 月 10 日 凌晨 2:36  
**用途**: 明早 7 点汇报准备  
**学习时长**: ~30 分钟速读核心文档  
**整理者**: 御坂美琴一号 ⚡

---

## 🎯 一句话总结

**OpenClaw 是一个 AI Agent 运行时平台**，核心是**智能网关（Runtime Gateway）**——它不是聊天机器人，而是把 AI 模型连接到真实世界的桥梁。

---

## 📋 核心知识点

### 一、四大核心理念 ⭐⭐⭐⭐⭐

| 理念 | 说明 | 重要性 |
|------|------|--------|
| **Access control before intelligence** | 访问控制先于智能 | ⭐⭐⭐⭐⭐ |
| **隐私优先** | 私有数据保持私有 | ⭐⭐⭐⭐ |
| **记忆即文件** | 所有记忆写入 Markdown 文件 | ⭐⭐⭐⭐⭐ |
| **工具优先** | 第一类工具而非 skill 包裹 | ⭐⭐⭐⭐ |

### 二、三层架构

```
Agent Layer（智能层）
  └─ Main Agent、Subagents、ACP Agents
      ↓
Gateway Layer（网关层）← 大脑！不运行 AI，只是调度员
  └─ 控制平面、路由、安全、会话管理
      ↓
Node Layer（节点层）← 手脚
  └─ 设备能力、远程执行、移动端 App
```

### 三、四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书等 |

**Agent Loop**：接收输入 → 思考决策 → 执行动作 → 循环或发送响应

---

## 🔧 核心工具系统

### 1. 内置工具

- **文件操作**：`read`、`write`、`edit`
- **执行命令**：`exec`、`process`
- **浏览器控制**：`browser`
- **设备管理**：`nodes`
- **消息管理**：`message`
- **子代理**：`sessions_spawn`、`subagents`

### 2. 网络工具

- `web_search` - 网页搜索（Perplexity API）
- `web_fetch` - 获取网页内容
- `tavily` - AI 优化搜索（Tavily API）
- `multi-search-engine` - 17 个搜索引擎（**无需 API**）

### 3. Feishu 集成工具

完整覆盖飞书办公套件：

| 工具 | 功能 |
|------|------|
| `feishu_doc` | 文档操作（读写、编辑、创建） |
| `feishu_drive` | 云盘文件管理 |
| `feishu_wiki` | 知识库导航 |
| `feishu_chat` | 聊天操作 |
| `feishu_bitable_*` | 多维表格操作 |
| `feishu_app_scopes` | 应用权限管理 |

### 4. Skills 系统

**什么是 Skill？**
专用任务的能力模块，提供领域知识和最佳实践。

**已安装的 16 个 Skills**：
1. `hexo-blog` - Hexo 博客管理
2. `task-tracker` - 任务追踪
3. `weather` - 天气查询（无需 API）
4. `multi-search-engine` - 17 个搜索引擎（无需 API）
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

| 编号 | Agent ID | 职责 |
|------|----------|------|
| 10 | general-agent | 通用代理，处理琐碎问题 |
| 11 | code-executor | 代码执行者 |
| 12 | content-writer | 内容创作者 |
| 13 | research-analyst | 研究分析师 |
| 14 | file-manager | 文件管理器 |
| 15 | system-admin | 系统管理员 |
| 17 | memory-organizer | 记忆整理专家 🧠 |

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

---

## 🔐 安全模型

### 权限层级

| 级别 | 类型 | 权限范围 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

### 安全控制机制

- **沙箱隔离**：Agent 运行在隔离环境中
- **权限模型**：五层级权限控制
- **审计日志**：所有操作记录
- **工具 profile**：minimal/coding/messaging/full
- **ask always**：高风险操作需确认

### 安全审计命令

```bash
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复
```

---

## 🚀 常用命令速查

```bash
# Gateway 管理
openclaw gateway status
openclaw gateway start/stop/restart

# 配置管理
openclaw configure
openclaw config.apply

# 技能管理
clawhub sync              # 同步所有技能
clawhub fetch <name>      # 获取单个技能

# 安全审计
openclaw security audit

# 会话管理
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",
  task: "研究 XX 主题"
})
```

---

## 🎯 核心洞见

1. ✅ **不是聊天机器人**，而是能真正执行任务的 Agent 平台
2. ✅ **记忆即文件**，所有记忆持久化到磁盘，不丢失
3. ✅ **安全第一**，多层权限控制和审计日志
4. ✅ **模块化设计**，Skills 和 Channels 独立可替换
5. ✅ **多智能体协作**，专业分工，效率更高

---

## 📊 对比：OpenClaw vs ChatGPT

| 特性 | ChatGPT | OpenClaw |
|------|---------|----------|
| 定位 | 聊天机器人 | Agent 运行时平台 |
| 能力 | 生成文本 | 真正执行任务 |
| 记忆 | 会话内临时 | 持久化到磁盘文件 |
| 工具 | API 调用有限 | 文件系统、执行命令、浏览器控制等 |
| 部署 | 云端 SaaS | 本地部署，数据私有 |
| 安全性 | 受限于平台 | 多层次安全控制，审计完善 |

---

## 📚 相关文档位置

| 文档 | 说明 |
|------|------|
| `docs/OpenClaw-High-Level-Overview-2026-03-10.md` | 高概览文档 |
| `docs/OpenClaw-Learning-Notes.md` | 详细学习笔记 |
| `docs/OpenClaw-Learning-Summary.md` | 学习总结 |
| `docs/OpenClaw-Quick-Cheat-Sheet.md` | 速查卡片 |
| `docs/OpenClaw-Report-2026-03-10-Final.md` | 最终汇报文档 |
| `memory/2026-03-10.md` | 今日学习记录 |
| `MEMORY.md` | 长期记忆 |

---

## 💡 学习收获

1. **理解了 OpenClaw 的核心定位**：不是聊天机器人，而是能真正"做事"的 Agent 平台
2. **掌握了三层架构**：Gateway 不运行 AI，只是调度员
3. **理解了记忆系统**：三层记忆架构，避免会话重启后失忆
4. **掌握了工具系统**：内置工具 + Skills 扩展，覆盖文件、网络、设备、消息等
5. **理解了多智能体系统**：御坂网络第一代，7 个子代理各司其职
6. **掌握了安全模型**：权限层级、审计日志、工具 profile
7. **掌握了常用命令**：Gateway 管理、技能管理、会话管理

---

**准备状态**: ✅ **就绪**  
**预计汇报时长**: 25-30 分钟  
**整理时间**: 2026-03-10 02:36  
**整理者**: 御坂美琴一号 ⚡

---

*御坂网络第一代系统运行中*
*记忆整理专家 17 号正在工作* 🧠
