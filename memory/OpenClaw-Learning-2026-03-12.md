# OpenClaw 知识学习笔记

## 📅 学习日期
2026-03-12

## 🎯 学习目标
为明早七点的 OpenClaw 知识汇报做准备，全面了解系统架构、核心功能和最佳实践。

---

## 一、OpenClaw 概述

### 1.1 什么是 OpenClaw?

OpenClaw 是一个**自托管的智能体网关**,将你的聊天应用 (WhatsApp、Telegram、Discord、iMessage 等) 与 AI 编码智能体连接起来。

**核心理念**: "EXFOLIATE! EXFOLIATE!" 🦞

- **个人 AI 助手**: 运行在自己设备上
- **任意系统**: 支持任何操作系统
- **任意平台**: 支持几乎所有主流聊天平台
- **龙虾风格**: 社区驱动的开源项目

### 1.2 支持的平台

**聊天平台** (26+ 种):
- WhatsApp, Telegram, Slack, Discord
- Google Chat, Signal, iMessage, BlueBubbles
- IRC, Microsoft Teams, Matrix
- Feishu (飞书), LINE, Mattermost
- Nextcloud Talk, Nostr, Synology Chat
- Tlon, Twitch, Zalo, Zalo Personal, WebChat

**设备节点**:
- macOS (带菜单栏应用)
- iOS 节点
- Android 节点

### 1.3 技术栈

- **运行时**: Node.js ≥ 22
- **包管理器**: npm, pnpm, 或 bun
- **许可证**: MIT
- **开源**: GitHub 开源项目

---

## 二、核心架构

### 2.1 架构概览

```
Chat Apps + Plugins
       ↓
┌────────────────────────┐
│    Gateway (控制平面)   │
│  ws://127.0.0.1:18789 │
└──────────┬─────────────┘
           ↓
   ┌───────┼───────┬───────┬────────┐
   ↓       ↓       ↓       ↓        ↓
Pi agent  CLI   WebChat  macOS    iOS/Android
(RPC)         UI       App      Nodes
```

### 2.2 Gateway (网关)

Gateway 是整个系统的**控制平面**,负责:

- **会话管理**: 维护所有智能体会话
- **路由调度**: 将消息路由到正确的智能体
- **通道连接**: 管理与各个聊天平台的连接
- **工具调用**: 执行智能体的工具请求
- **事件调度**: Cron 作业、Webhook、心跳等

**默认端口**: 18789

### 2.3 智能体运行时

OpenClaw 使用 **Pi agent** 作为基础运行时:

- RPC 模式运行
- 工具流式传输
- 块流式传输
- 支持多种模型提供商

### 2.4 会话模型

**会话类型**:
- **Main session**: 直接对话 (主人)
- **Group sessions**: 群聊隔离
- **Agent sessions**: 智能体特定隔离

**会话特性**:
- 每个智能体独立的隔离会话
- 按工作空间隔离
- 按智能体会话隔离
- 支持激活模式、队列模式

---

## 三、核心功能

### 3.1 多通道网关

单 Gateway 进程同时服务多个聊天平台:

- WhatsApp (使用 Baileys 库)
- Telegram (使用 grammY 库)
- Slack (使用 Bolt 库)
- Discord (使用 discord.js 库)
- 等等...

### 3.2 设备节点

**macOS 节点**:
- 系统命令执行 (`system.run`)
- 系统通知 (`system.notify`)
- Canvas 可视化工作区
- 摄像头/屏幕录制
- 位置获取
- 通知管理

**iOS 节点**:
- Canvas 可视化
- Voice Wake 语音唤醒
- Talk Mode 连续语音
- 摄像头/屏幕录制
- Bonjour 发现 + 设备配对

**Android 节点**:
- Connect/Chat/Voice 标签页
- Canvas/相机/屏幕捕获
- 设备命令 (通知/位置/SMS/照片/联系人/日历/运动/应用更新)

### 3.3 Canvas 可视化工作区

Agent 驱动的可视化工作空间:

- **A2UI**: 代理驱动的 UI 推送
- 支持 eval、snapshot 操作
- macOS 平台的核心功能
- 可用于远程控制其他设备

### 3.4 Voice Wake 和 Talk Mode

**Voice Wake** (语音唤醒):
- macOS/iOS 支持
- 自定义唤醒词
- 推送语音转文本

**Talk Mode** (对话模式):
- Android 连续语音支持
- ElevenLabs + 系统 TTS 回退
- 连续对话体验

### 3.5 自动化功能

**Cron Jobs** (定时任务):
- 精确时间点触发
- 周期性任务
- 与 Heartbeat 配合使用

**Heartbeat** (心跳):
- 每 30 分钟轮询检查
- 批量检查多个服务
- 可配置的心跳提示

**Webhooks** (网络钩子):
- 外部触发器
- 可配置端点
- 支持多种协议

**Gmail Pub/Sub** (邮件发布/订阅):
- 邮件自动化
- Gmail 触发器

### 3.6 Skills 平台

技能是 OpenClaw 的功能扩展系统:

**技能类型**:
- **Bundled skills**: 内置技能
- **Managed skills**: 托管技能
- **Workspace skills**: 工作空间技能

**Skill Hub **(ClawHub):
- 最小化的技能注册表
- 自动搜索技能
- 按需获取新技能

### 3.7 工具系统

**核心工具**:
- `browser`: 浏览器控制
- `canvas`: Canvas 可视化
- `nodes`: 设备节点操作
- `cron`: Cron 作业管理
- `sessions`: 会话管理
- `discord/slack`: 平台特定操作

**工具策略**:
- 沙盒模式
- 工具策略
- 提升权限模式

---

## 四、安装和配置

### 4.1 快速安装

```bash
# 1. 安装 OpenClaw
npm install -g openclaw@latest

# 2. 安装守护进程
openclaw onboard --install-daemon

# 3. 配置通道
openclaw channels login

# 4. 启动网关
openclaw gateway --port 18789
```

### 4.2 从源码构建

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw

pnpm install
pnpm ui:build  # 首次运行自动安装 UI 依赖
pnpm build

pnpm openclaw onboard --install-daemon

# 开发模式 (自动重载)
pnpm gateway:watch
```

### 4.3 配置文件

**配置文件位置**: `~/.openclaw/openclaw.json`

**基本配置示例**:
```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6"
  },
  "channels": {
    "whatsapp": {
      "allowFrom": ["+15555550123"],
      "groups": {
        "*": {
          "requireMention": true
        }
      }
    },
    "telegram": {
      "botToken": "123456:ABCDEF"
    },
    "slack": {
      "botToken": "xoxb-...",
      "appToken": "xapp-..."
    }
  }
}
```

### 4.4 安全配置

**DM 策略**:
- `dmPolicy: "pairing"` (默认): 未知发送者需要配对码
- `dmPolicy: "open"`: 允许所有 DM

**沙盒模式**:
```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "allowlist": ["bash", "process", "read", "write"],
        "denylist": ["browser", "canvas", "nodes"]
      }
    }
  }
}
```

---

## 五、平台特定部署

### 5.1 macOS

**特点**:
- 菜单栏应用
- Voice Wake + PTT 覆盖层
- WebChat
- 远程网关控制
- Canvas 支持

**权限**:
- 需要 TCC 权限
- 菜单栏控制 Gateway 健康
- 签名构建以保留权限

### 5.2 iOS

**特点**:
- 作为节点配对
- Voice Wake 触发转发
- Canvas 表面
- 设备配对

**运行手册**: `platforms/ios.md`

### 5.3 Android

**特点**:
- WS 节点配对
- Connect/Chat/Voice 标签页
- Canvas、相机、屏幕捕获
- 设备命令 (通知/位置/SMS/照片/联系人/日历/运动/应用更新)

**运行手册**: `platforms/android.md`

### 5.4 Linux/WSL2

**推荐配置**:
- WSL2 (Windows)
- VPS 部署
- Docker/Podman 容器

### 5.5 远程部署选项

**云平台支持**:
- Fly.io
- GCP
- Hetzner
- Oracle Cloud
- Northflank
- Railway
- Render

**容器部署**:
- Docker
- Podman
- Nix (声明式配置)

### 5.6 Tailscale 暴露

**模式**:
- `off`: 无 Tailscale 自动化 (默认)
- `serve`: tailnet-only HTTPS
- `funnel`: 公共 HTTPS (需要密码认证)

**配置示例**:
```json
{
  "gateway": {
    "tailscale": {
      "mode": "serve",
      "resetOnExit": true
    },
    "auth": {
      "mode": "password"
    }
  }
}
```

---

## 六、最佳实践

### 6.1 工作空间管理

**工作空间**: `~/.openclaw/workspace`

**注入的提示文件**:
- `AGENTS.md`: 智能体身份定义
- `SOUL.md`: 灵魂定义
- `TOOLS.md`: 工具说明
- `USER.md`: 用户信息

**记忆系统**:
- `memory/YYYY-MM-DD.md`: 每日日志
- `MEMORY.md`: 长期记忆
- `life/archives/`: 归档

### 6.2 智能体路由

**多智能体路由**:
- 按工作空间隔离
- 按智能体隔离会话
- 按发送者隔离

**会话工具**:
- `sessions_list`: 发现活动会话
- `sessions_history`: 获取会话历史
- `sessions_send`: 发送消息到另一会话
- `sessions_spawn`: 创建新的子智能体

### 6.3 媒体处理

**媒体管道**:
- 图像/音频/视频处理
- 转录钩子
- 大小限制
- 临时文件生命周期

**支持的媒体类型**:
- 图片 (jpg, png, gif, webp)
- 音频 (转录)
- 文档

### 6.4 状态追踪

**使用追踪**:
- 每响应使用页脚
- `/usage off|tokens|full`
- 成本追踪

**会话状态**:
- `/status`: 紧凑状态
- 模型 + token 使用
- 可用成本

### 6.5 错误处理和重试

**重试策略**:
- 可配置的重试策略
- 错误恢复
- 日志记录

**故障排除**:
- `/doctor`: 系统诊断
- `/logs`: 查看日志
- 故障排除指南

---

## 七、命令行工具

### 7.1 主要命令

**网关管理**:
- `openclaw gateway`: 启动网关
- `openclaw daemon`: 守护进程管理
- `openclaw health`: 健康检查
- `openclaw doctor`: 系统诊断

**通道管理**:
- `openclaw channels`: 通道管理
- `openclaw channels login`: 登录通道
- `openclaw pairing`: 配对管理

**智能体操作**:
- `openclaw agent`: 发送智能体消息
- `openclaw message`: 发送消息
- `openclaw sessions`: 会话管理

**系统管理**:
- `openclaw onboard`: 引导设置
- `openclaw config`: 配置管理
- `openclaw skills`: 技能管理
- `openclaw update`: 更新系统

### 7.2 快捷命令

**群组命令**:
- `/status`: 紧凑会话状态
- `/new` / `/reset`: 重置会话
- `/compact`: 压缩会话上下文
- `/think`: 设置思考级别
- `/verbose`: 启用详细模式
- `/usage`: 启用使用追踪
- `/restart`: 重启网关
- `/activation`: 组激活切换

---

## 八、安全性

### 8.1 安全原则

**核心原则**:
- 私有数据保持私密
- 不确定时先询问
- 永远不要半生不熟地回复
- 在群聊中要谨慎
- Git 操作前先检查

### 8.2 权限控制

**三种模式**:
- **沙盒模式**: 隔离执行环境
- **工具策略**: 允许/拒绝特定工具
- **提升权限**: 系统级权限

**DM 安全**:
- 默认配对策略
- 白名单控制
- 群组提及要求

### 8.3 威胁模型

**安全文档**:
- `security/CONTRIBUTING-THREAT-MODEL.md`: 贡献威胁模型
- `security/THREAT-MODEL-ATLAS.md`: 威胁模型图谱
- `security/formal-verification.md`: 形式验证

### 8.4 安全最佳实践

- 使用强密码
- 限制 DM 访问
- 配置群组提及
- 定期审计权限
- 保持系统更新

---

## 九、故障排除

### 9.1 常见问题

**Gateway 问题**:
- 运行 `openclaw doctor` 诊断
- 检查日志
- 验证配置

**通道连接问题**:
- 检查凭据
- 验证网络
- 重试登录

**性能问题**:
- 压缩会话上下文
- 调整思考级别
- 检查资源使用

### 9.2 诊断工具

- `/status`: 查看状态
- `/logs`: 查看日志
- `/health`: 健康检查
- `/doctor`: 系统诊断

---

## 十、扩展和集成

### 10.1 插件系统

**插件类型**:
- 通道插件
- 工具插件
- 智能体插件

**插件清单**: `plugins/manifest.md`

### 10.2 自定义技能

**创建技能**:
- `tools/creating-skills.md`: 创建技能指南
- 遵循 SKILL.md 规范
- 包含权限说明

### 10.3 模型集成

**支持的服务商**:
- OpenAI
- Anthropic
- Google Vertex AI
- Hugging Face
- Ollama
- 等等...

**模型故障转移**:
- 多模型支持
- 自动故障转移
- 成本优化

---

## 十一、社区和资源

### 11.1 官方资源

- **网站**: https://openclaw.ai
- **文档**: https://docs.openclaw.ai
- **GitHub**: https://github.com/openclaw/openclaw
- **Discord**: https://discord.gg/clawd

### 11.2 文档分类

**快速开始**:
- Getting Started
- Quick Start
- Onboarding Wizard

**核心概念**:
- Architecture
- Session Management
- Multi-Agent Routing
- Security

**平台指南**:
- macOS
- iOS
- Android
- Linux/WSL2

**工具参考**:
- Tools Index
- Skills
- Browser
- Canvas
- Nodes

**部署**:
- Docker
- VPS
- Cloud Platforms
- Nix

---

## 十二、总结

### 12.1 核心亮点

1. **自托管**: 运行在自己的硬件上
2. **多通道**: 单一网关服务多个平台
3. **智能体原生**: 为智能体设计的工具使用
4. **开源**: MIT 许可，社区驱动
5. **跨平台**: 支持所有主流操作系统

### 12.2 使用场景

- 个人 AI 助手
- 团队协作
- 自动化任务
- 远程设备控制
- 编程辅助
- 跨平台消息管理

### 12.3 学习建议

1. 阅读快速开始指南
2. 使用 wizard 进行设置
3. 探索技能系统
4. 阅读安全文档
5. 参与社区讨论

---

## 📚 参考文档

**核心文档**:
- https://docs.openclaw.ai/start/getting-started
- https://docs.openclaw.ai/gateway
- https://docs.openclaw.ai/tools
- https://docs.openclaw.ai/security

**GitHub**:
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/nix-openclaw

**社区**:
- https://discord.gg/clawd
- https://clawhub.com

---

**学习完成时间**: 2026-03-12 00:20
**下次复习**: 明早 7 点汇报前
