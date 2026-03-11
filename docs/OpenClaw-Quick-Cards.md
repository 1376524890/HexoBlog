# OpenClaw 快速参考卡片

> 明早七点汇报用 - 核心要点速查

---

## 🎯 OpenClaw 是什么？

**一句话**：自托管的 AI 网关，连接聊天应用（WhatsApp/Telegram/Discord 等）和 AI 智能体

**核心特点**：
- ✅ 自托管（数据在自己手中）
- ✅ 多通道（一个网关服务所有聊天应用）
- ✅ 智能体原生（为编码智能体设计）
- ✅ 开源（MIT 许可）

---

## 🏗️ 核心架构

```
用户消息 → Gateway → AI Agent → 回复 → 用户
          ↓
     会话管理 + 路由分发 + 认证授权
```

**四大组件**：
1. **Gateway**：控制平面，消息路由
2. **Channels**：通道层（WhatsApp/Telegram/Discord 等）
3. **Agents**：智能体（工作空间、会话、配置）
4. **Nodes**：配对设备（iOS/Android/macOS）

---

## 🧠 关键概念

### 上下文（Context）
- 发送给模型的所有内容
- 受模型上下文窗口限制
- 使用 `/context list` 查看

### 会话（Session）
- 核心状态管理单元
- 格式：`agent:<agentId>:<key>`
- DM 隔离：`dmScope: "per-channel-peer"`（推荐）

### 压缩（Compaction）
- 自动总结旧对话
- 释放上下文空间
- 使用 `/compact` 手动触发

### 心跳（Heartbeat）
- 定期主动提醒（默认 30 分钟）
- 无事时回复 `HEARTBEAT_OK`
- 有提醒时直接发送

---

## 🛠️ 核心工具

**基础工具**：
- `read`/`edit`/`write`：文件操作
- `exec`：执行命令
- `web_search`/`web_fetch`：网络搜索
- `browser`/`canvas`：浏览器/图形界面
- `nodes`：设备操作
- `sessions_*`：会话管理

**安全配置**：
```json
{
  "tools": {
    "profile": "messaging",
    "elevated": { "enabled": false }
  }
}
```

---

## 🔒 安全基线

**60 秒加固**：
```bash
# 1. 文件权限
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json

# 2. 安全审计
openclaw security audit --deep
openclaw security audit --fix
```

**配置要点**：
- Gateway 绑定：`loopback`（仅本地）
- 认证模式：`token`（长随机值）
- DM 策略：`pairing`
- 会话隔离：`per-channel-peer`
- 工具限制：`profile: "messaging"`

**安全原则**：
1. **身份优先**：谁可以调用
2. **作用域次之**：在哪里执行
3. **模型最后**：假设模型可被操纵

---

## ⚙️ 常用命令

| 命令 | 说明 |
|------|------|
| `openclaw gateway status` | Gateway 状态 |
| `openclaw gateway start` | 启动 Gateway |
| `openclaw status` | 系统状态 |
| `openclaw sessions` | 会话列表 |
| `openclaw security audit` | 安全审计 |
| `openclaw doctor` | 诊断工具 |
| `/compact` | 手动压缩上下文 |
| `/context list` | 查看上下文 |

---

## 📊 配置结构

```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": { "mode": "token", "token": "xxx" }
  },
  "session": { "dmScope": "per-channel-peer" },
  "tools": { "profile": "messaging" },
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "groups": { "*": { "requireMention": true } }
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-6",
      "workspace": "~/.openclaw/workspace"
    }
  }
}
```

---

## 🎯 明早七点汇报要点

### 1. OpenClaw 的核心价值
- 自托管 AI 助手，数据在自己手中
- 一个网关服务所有聊天应用
- 为开发者设计的智能体平台

### 2. 架构亮点
- Gateway 作为单一真相源
- 会话隔离设计（DM/群组分离）
- 支持 Docker 沙箱
- 多智能体路由

### 3. 安全特性
- 严格的认证授权
- 工具执行控制
- 会话隔离
- 安全审计工具

### 4. 实际应用场景
- 个人 AI 助手（WhatsApp/Telegram）
- 团队协作工具（Slack/Discord）
- 编码智能体（支持代码执行）
- 自动化任务（cron + 心跳）

### 5. 学习收获
- 架构设计：Gateway 作为中心枢纽
- 会话管理：隔离 + 压缩机制
- 安全模型：身份优先原则
- 工具系统：安全配置 + 沙箱

---

**文档来源**：OpenClaw 官方文档 + 本地学习总结  
**学习时间**：2026-03-11 01:46-01:50  
**状态**：理论学习完成，准备汇报 ✅
