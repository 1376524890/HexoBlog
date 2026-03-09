# 📊 OpenClaw 知识学习汇报 - 2026 年 3 月 10 日

**汇报时间**: 2026 年 3 月 10 日 7:00 AM (UTC+8)  
**整理者**: 御坂美琴一号（御坂网络核心中枢） ⚡  
**准备状态**: ✅ **完全就绪**

---

## 🎯 一句话总结

**OpenClaw 是一个 AI Agent 运行时平台**，核心是**智能网关（Runtime Gateway）**——它不是聊天机器人，而是把 AI 模型连接到真实世界的桥梁。

---

## 📋 核心知识点速览

### 一、四大核心理念 ⭐⭐⭐⭐⭐

| 理念 | 说明 | 重要性 |
|------|------|--------|
| **Access control before intelligence** | 访问控制先于智能 | ⭐⭐⭐⭐⭐ |
| **隐私优先** | 私有数据保持私有 | ⭐⭐⭐⭐ |
| **记忆即文件** | 所有记忆写入 Markdown 文件 | ⭐⭐⭐⭐⭐ |
| **工具优先** | 第一类工具而非 skill 包裹 | ⭐⭐⭐⭐ |

### 二、三层架构全景

```
┌─────────────────────────────────────────────────────────────┐
│              Agent Layer（智能层）                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Main Agent   │  │ Subagents    │  │ ACP Agents   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              Gateway Layer（网关层）                          │
│  🧠 核心：Gateway 本身**不运行 AI 模型**，只是调度员          │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                Node Layer（节点层）                           │
│  📱 设备能力 (相机/屏幕) · 🖥️ 远程执行 · 📱 移动端 App        │
└─────────────────────────────────────────────────────────────┘
```

### 三、四大核心组件

| 组件 | 职责 | 关键特点 |
|------|------|----------|
| **Gateway** | 大脑和路由器 | 生命周期管理、消息路由、工具协调、安全控制 |
| **Agent** | AI 执行体 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 会话容器 | 有状态容器，通过**Compaction**压缩机制管理上下文 |
| **Channel** | 消息通道 | 协议适配器，支持 Telegram、Discord、飞书等 |

### 四、Agent Loop（核心循环）

```
接收输入 → 思考决策 → 执行动作 → 循环或发送响应
         ↓         ↓
    直接回复  工具调用
```

**关键点**：模型拥有决策权，主动决定需要什么信息、调用什么工具。

### 五、记忆系统（三层架构）🧠

```
Layer 1: 会话记忆（Session Memory）
- 当前会话上下文
- 临时决策和中间结果
         │
         ▼
Layer 2: 任务记忆（Task Memory）
- 任务计划文件
- 子代理执行结果
         │
         ▼
Layer 3: 长期记忆（Long-term Memory）
- MEMORY.md：精选记忆
- memory/YYYY-MM-DD.md：每日日志
```

### 六、御坂网络第一代（多智能体系统）⚡

```
御坂美琴一号（主 Agent）
     ↓ 任务拆解与调度
┌────┴────┬───────┬───────┐
▼         ▼       ▼       ▼
11 号    12 号   13 号   14 号
Code    Write  Research File
```

| 编号 | 名称 | 职责 |
|------|------|------|
| 11 | Code Agent | 代码编写、调试、重构 |
| 12 | Write Agent | 文章撰写、翻译、润色 |
| 13 | Research Agent | 信息搜索、数据分析 |
| 14 | File Agent | 文件操作、目录管理 |
| 15 | Sys Agent | 系统配置、服务管理 |
| 16 | Crawler Agent | 网页抓取、数据提取 |
| 17 | Memory Agent | 记忆整理专家 🧠 |

---

## 🔍 核心概念详解

### 1. OpenClaw vs 传统聊天机器人

| 特性 | 聊天机器人 | OpenClaw |
|------|-----------|----------|
| 本质 | 对话系统 | Agent 运行时平台 |
| 记忆 | 临时上下文 | 持久化文件 |
| 工具 | 有限 | 完整工具集 |
| 扩展性 | 固定 | Skills 系统可定制 |
| 多智能体 | 无 | 子代理系统 |

### 2. 工具系统

#### 内置工具

- **文件操作**：`read`、`write`、`edit`
- **执行命令**：`exec`、`process`
- **浏览器控制**：`browser`
- **设备管理**：`nodes`
- **消息管理**：`message`

#### Feishu 集成

完整覆盖飞书办公套件：
- `feishu_doc` - 文档操作
- `feishu_drive` - 云盘管理
- `feishu_wiki` - 知识库
- `feishu_chat` - 聊天操作
- `feishu_bitable_*` - 多维表格

#### Skills 系统

**什么是 Skill？**
专用任务的能力模块，提供领域知识和最佳实践。

**常用 Skills**：
- `hexo-blog` - Hexo 博客管理
- `task-tracker` - 任务追踪
- `weather` - 天气查询（无需 API）
- `multi-search-engine` - 17 个搜索引擎（无需 API）
- `proactive-agent` - 主动代理
- `healthcheck` - 安全加固
- `xiaohongshu-ops` - 小红书运营
- `subagent-network-call` - 御坂网络调用

### 3. 安全模型

#### 权限层级

| 级别 | 类型 | 权限范围 |
|------|------|----------|
| Level 5 | 主 Agent | 完全权限 |
| Level 4 | 可信子 Agent | 受限系统权限（需批准） |
| Level 3 | 标准子 Agent | 标准开发权限 |
| Level 2 | 受限子 Agent | 严格受限权限 |
| Level 1 | 只读子 Agent | 只读访问 |

#### 安全控制机制

- **沙箱隔离**：Agent 运行在隔离环境中
- **权限模型**：五层级权限控制
- **审计日志**：所有操作记录
- **工具 profile**：minimal/coding/messaging/full
- **ask always**：高风险操作需确认

### 4. Context 与 Compaction

**问题**：大模型有 token 限制，无法无限保留历史。

**解决方案**：
- **Auto-compaction**：接近限制时自动总结旧消息
- **Memory flush**：压缩前触发 silent turn 存储持久记忆
- **手动触发**：`/compact "专注于决策和待办事项"`

**配置示例**：
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "reserveTokensFloor": 20000,
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 4000
        }
      }
    }
  }
}
```

---

## 🚀 最佳实践

### 记忆管理

1. **DECIDE to write**：决定、偏好、持久事实 → `MEMORY.md`
2. **Daily notes**：日常记录 → `memory/YYYY-MM-DD.md`
3. **定期 review**：定期清理 `MEMORY.md`，移除过时信息
4. **Ask to remember**：重要事项明确让 Agent 写入记忆

### 安全建议

1. **定期 audit**：每月运行安全审计
2. **最小权限**：按需开放工具
3. **强认证**：使用长随机 token
4. **本地部署**：Gateway 绑定到 loopback

### 工具使用

- **Profile 最小化**：默认使用 `minimal`，按需开放
- **沙箱优先**：敏感操作使用沙箱环境
- **ask always**：高风险操作设置 `ask: always`
- **workspaceOnly**：文件系统操作限制在 workspace

---

## 📊 常用命令速查

```bash
# Gateway 管理
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart

# 配置管理
openclaw configure
openclaw config.apply

# 技能管理
clawhub sync              # 同步所有技能
clawhub fetch <name>      # 获取单个技能
clawhub publish <folder>  # 发布自定义技能

# 安全审计
openclaw security audit           # 基本检查
openclaw security audit --deep    # 深度检查
openclaw security audit --fix     # 自动修复

# 会话管理
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  mode: "run",
  task: "研究 XX 主题"
})
```

---

## 🎯 关键资源

| 资源 | 链接 |
|------|------|
| 官方文档 | https://docs.openclaw.ai |
| GitHub | https://github.com/openclaw/openclaw |
| ClawHub（技能市场） | https://clawhub.com |
| Discord 社区 | https://discord.gg/clawd |
| 本地文档 | `~/openclaw/workspace/docs/` |

---

## 📝 总结

### OpenClaw 核心优势

| 优势 | 说明 |
|------|------|
| **智能网关** | 统一管理多个平台和 Agent |
| **模块化设计** | Skills、Channels、Agents 独立可替换 |
| **持久化记忆** | 三层记忆架构，避免失忆 |
| **多智能体协作** | 子代理系统，专业分工 |
| **安全隔离** | 沙箱策略、权限模型、审计日志 |
| **可扩展** | 自定义 Skills、Channels |

### 学习要点回顾

1. ✅ **核心架构**：Gateway、Agent、Session、Channel 四大组件
2. ✅ **Agent Loop**：AI 持续运行的核心循环
3. ✅ **工具系统**：内置工具 + Skills 扩展
4. ✅ **多智能体**：子代理系统、御坂网络第一代
5. ✅ **记忆同步**：三层记忆架构
6. ✅ **安全模型**：权限层级与审计机制

---

## 💡 核心洞见

1. **OpenClaw 不是聊天机器人**，而是能真正执行任务的 Agent 平台
2. **记忆即文件**，所有记忆持久化到磁盘，不丢失
3. **安全第一**，多层权限控制和审计日志
4. **模块化设计**，Skills 和 Channels 独立可替换
5. **多智能体协作**，专业分工，效率更高

---

**汇报准备时间**: 约 2 小时  
**预计汇报时长**: 25-30 分钟  
**准备状态**: ✅ **就绪**

---

*整理：御坂美琴一号 ⚡  
御坂网络第一代系统运行中*
*2026 年 3 月 10 日*
