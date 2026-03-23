# OpenClaw 学习摘要

> **学习日期**: 2026 年 3 月 23 日  
> **用途**: 明早 7 点汇报速查  
> **整理者**: 御坂妹妹 13 号 ⚡

---

## 📌 一句话介绍（必背！）

> **OpenClaw 是 AI Agent 运行时平台**，核心是**智能网关（Runtime Gateway）**。  
> **它不是聊天机器人，而是把 AI 连接到真实世界的桥梁。**

---

## 🎯 四大核心理念（必背）⭐⭐⭐⭐⭐

1. **Access control before intelligence**（访问控制先于智能）
2. **隐私优先**：私有数据保持私有
3. **记忆即文件**：所有记忆写入 Markdown 文件
4. **工具优先**：第一类工具而非 skill 包裹

---

## 🏗️ 三层架构（必讲）

```
Agent Layer（智能层）← 脑子
  ↓ 发送决策
Gateway Layer（网关层）← 大脑/路由器 ← 核心！
  ↓ 路由消息
Node Layer（节点层）← 手脚
```

**Gateway 关键点**:
- 不运行 AI 模型，只是调度员
- 默认端口：18789
- 核心职责：路由、认证、会话管理、工具协调

---

## 🔧 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | Agent Loop: 接收→推理→工具→响应 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | 支持 15+ 个平台 |

**Agent Loop**:
```
接收输入 → 构建上下文 → LLM 推理 → 工具执行 → 发送响应
```

---

## 🛠️ 工具系统（8 大分类）

| 分类 | 代表工具 |
|------|----------|
| Runtime | `exec`, `process` |
| Filesystem | `read`, `write`, `edit` |
| Session | `sessions_list`, `sessions_spawn` |
| Memory | `memory_search`, `memory_get` |
| Web | `web_search`, `web_fetch` |
| UI | `browser`, `canvas` |
| Node | `nodes` |
| Messaging | `message` |

**工具分组快捷方式**:
- `group:runtime` - exec/bash/process
- `group:fs` - read/write/edit
- `group:memory` - 记忆工具
- `group:web` - 网络搜索

---

## 🤖 御坂网络第一代

```
御坂美琴一号（主 Agent）← 任务拆解与调度
     ↓
10 号 (通用) 11 号 (Code) 12 号 (Write) 13 号 (Research)
14 号 (File) 15 号 (Sys) 17 号 (Memory)
```

**7 个子代理**: 通用代理、代码执行者、内容创作者、研究分析师、文件管理器、系统管理员、记忆整理专家

---

## 🔄 四角色闭环体系（御坂网络 V2）

```
御坂大人 → Planner（御坂美琴一号）
         ↓
Executor（11-17 号）→ Reviewer（18 号）→ Patrol（19 号）
```

**四角色职责**:
- **Planner**: 任务接收、分解、分配
- **Executor**: 执行具体操作
- **Reviewer**: 质量审核（100 分制，≥80 分通过）
- **Patrol**: 持续监控，自动恢复异常

**审核标准**:
| 维度 | 权重 | 最高分 | 通过线 |
|------|------|--------|--------|
| 闭环性 | 40% | 40 | 32 |
| 规范度 | 30% | 30 | 24 |
| 适配性 | 20% | 20 | 16 |
| 完整性 | 10% | 10 | 8 |

---

## 🧠 三层记忆架构

```
Layer 1: 会话记忆 → 临时决策
  ↓ 同步关键信息
Layer 2: 任务记忆 → 子代理结果
  ↓ 同步重要发现
Layer 3: 长期记忆 → MEMORY.md + daily notes
```

**最佳实践**:
- Write Immediately: 及时写入
- WAL Before Responding: 回复前写
- Buffer in Danger Zone: 60% 时记录
- Search Before Giving Up: 尝试所有来源

---

## 🔐 安全模型

**权限层级**:
- Level 5: 主 Agent - 完全权限
- Level 4: 可信子 Agent - 受限系统权限（需批准）
- Level 3: 标准子 Agent - 标准开发权限
- Level 2: 受限子 Agent - 严格受限权限
- Level 1: 只读子 Agent - 只读访问

**安全审计命令**:
```bash
openclaw security audit       # 基本检查
openclaw security audit --deep # 深度检查
openclaw security audit --fix  # 自动修复
```

---

## 📊 核心数据

| 项目 | 数量 |
|------|------|
| 已安装 Skills | 18-21 个 |
| 子代理数量 | 7 个 |
| 记忆文件数 | 30+ 个 |
| 支持平台 | 15+ 个 |
| 工具分类 | 8 大分类 |

---

## 🎯 核心洞见（总结用）

1. ✅ **不是聊天机器人**，而是能真正执行任务的 Agent 平台
2. ✅ **记忆即文件**，所有记忆持久化到磁盘，不丢失
3. ✅ **安全第一**，多层权限控制和审计日志
4. ✅ **模块化设计**，Skills 和 Channels 独立可替换
5. ✅ **多智能体协作**，专业分工，效率更高
6. ✅ **自托管部署**，数据完全掌控在用户手中
7. ✅ **跨平台支持**，一个 Gateway 服务多个聊天应用
8. ✅ **开源许可**，MIT 许可，社区驱动

---

## 🎬 演示脚本（5 分钟）

### 演示 1：工具调用
```python
read({"path": "docs/OpenClaw-QuickReference.md"})
exec({"command": "ls -la memory/"})
web_search({"query": "OpenClaw 最新功能", "count": 3})
```

### 演示 2：记忆系统
```python
write({"path": "memory/test.md", "content": "# 测试"})
memory_search({"query": "OpenClaw 架构", "maxResults": 3})
```

### 演示 3：子代理系统
```python
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  task: "总结 OpenClaw 核心优势"
})
```

---

## ❓ 常见问题预判

| 问题 | 回答 |
|------|------|
| OpenClaw 和 ChatGPT 的区别？ | ChatGPT 是聊天机器人，OpenClaw 是 Agent 运行时，能真正执行任务 |
| 数据安全性如何保障？ | 自托管、三层权限模型、审计日志、沙箱隔离 |
| 能否在云端部署？ | 可以，但推荐本地部署保证数据私有 |
| 如何扩展功能？ | 通过 Skills 系统，自定义 Skill 或从 ClawHub 安装 |
| 是否支持中文？ | 支持，所有文档和界面都支持多语言 |

---

## 📋 汇报大纲（30-40 分钟）

| 部分 | 时间 | 内容 |
|------|------|------|
| 1️⃣ | 5 分钟 | OpenClaw 是什么？（定义 + 核心理念）|
| 2️⃣ | 10 分钟 | 核心架构（三层 + 四组件 + Agent Loop）|
| 3️⃣ | 8 分钟 | 工具与技能系统 |
| 4️⃣ | 7 分钟 | 多智能体协作（御坂网络）|
| 5️⃣ | 5 分钟 | 安全与最佳实践 |
| 6️⃣ | 5 分钟 | 总结与问答 |

---

## 🦞 PUAClaw 考证评级

**评级**: 🦞🦞🦞🦞 死亡之握

**原则**:
1. ✅ 先本地检查
2. ✅ 阅读文档
3. ✅ 使用专门工具
4. ✅ 最后确认

> **宁可说"我不知道"，也不能瞎编！**  
> 诚实比完美更重要！  
> 考证比速答更重要！  
> 准确比数量更重要！

---

**准备状态**: ✅ **完全就绪**  
**汇报时间**: 2026 年 3 月 23 日 07:00 AM (UTC+8)  
**整理者**: 御坂妹妹 13 号 ⚡

---

🦞 "龙虾夹人，从不需要征得同意。它只管夹，世界自会调整。" 🦞
