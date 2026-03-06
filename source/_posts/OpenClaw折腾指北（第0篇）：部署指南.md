---
title: OpenClaw折腾指北（第0篇）：部署指南
date: 2026-03-06 15:04:32
tags:
  - OpenClaw
  - 部署
  - 教程
categories:
  - 折腾指北
---

> OpenClaw 是一个开源的 AI 助手平台，让你能够在本地运行自己的 AI Agent，并连接到各种消息渠道（微信、Telegram、Discord 等）。这篇是系列文章的第 0 篇，介绍如何部署 OpenClaw。

<!-- more -->

## 什么是 OpenClaw？

OpenClaw 是一个**个人 AI 助手平台**，核心特点：

- **本地优先**：数据存储在本地，隐私可控
- **多渠道接入**：支持微信、Telegram、Discord、Slack、飞书等
- **可扩展**：通过 Skill 系统扩展功能
- **多模型支持**：OpenAI、Anthropic、Google、本地模型等

## 部署方式概览

OpenClaw 提供三种部署方式：

| 方式 | 适用场景 | 难度 |
|------|---------|------|
| **npm 安装** | 有 Node.js 环境的用户 | ⭐⭐ |
| **Docker** | 希望隔离环境的用户 | ⭐⭐ |
| **macOS App** | Mac 用户，最简单 | ⭐ |

## 方式一：npm 安装（推荐）

### 前置要求

- Node.js 18+（推荐 20 LTS）
- npm 或 yarn
- Git

### 安装步骤

```bash
# 全局安装 OpenClaw CLI
npm install -g openclaw

# 验证安装
openclaw --version

# 启动配置向导
openclaw onboard
```

### 配置向导

`openclaw onboard` 会引导你完成：

1. **选择模型提供商**：OpenAI、Anthropic、Google、Azure 或自定义
2. **配置 API Key**：输入对应平台的 API Key
3. **选择消息渠道**：微信、Telegram、Discord 等
4. **完成初始化**：自动生成配置文件

### 启动服务

```bash
# 启动 Gateway 服务
openclaw gateway start

# 查看状态
openclaw status
```

## 方式二：Docker 部署

### 使用 Docker Run

```bash
# 创建配置目录
mkdir -p ~/.openclaw

# 运行容器
docker run -d \
  --name openclaw \
  -v ~/.openclaw:/home/claw/.openclaw \
  -p 8080:8080 \
  ghcr.io/openclaw/openclaw:latest
```

### 使用 Docker Compose

```yaml
version: '3.8'
services:
  openclaw:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: openclaw
    volumes:
      - ~/.openclaw:/home/claw/.openclaw
    ports:
      - "8080:8080"
    restart: unless-stopped
```

### 进入容器配置

```bash
# 进入容器
docker exec -it openclaw bash

# 运行配置向导
openclaw onboard

# 重启容器生效
docker restart openclaw
```

## 方式三：macOS App（最简单）

适合不想折腾命令行的 Mac 用户：

1. 从 [GitHub Releases](https://github.com/openclaw/openclaw/releases) 下载 `.dmg` 文件
2. 拖拽安装到 Applications
3. 首次启动会自动运行配置向导
4. 菜单栏图标管理启停

## 配置详解

### 模型配置（`~/.openclaw/agents/main/agent/models.json`）

```json
{
  "default": "openai/gpt-4o",
  "providers": {
    "openai": {
      "apiKey": "sk-...",
      "baseURL": "https://api.openai.com/v1"
    }
  }
}
```

### 渠道配置（`~/.openclaw/agents/main/channels/`）

每个渠道独立配置，例如 Telegram：

```json
{
  "botToken": "YOUR_BOT_TOKEN",
  "enabled": true
}
```

## 常用命令

```bash
# 查看状态
openclaw status

# 启动/停止/重启 Gateway
openclaw gateway start
openclaw gateway stop
openclaw gateway restart

# 查看日志
openclaw logs

# 更新到最新版本
npm update -g openclaw
```

## 验证部署

1. **检查 Gateway 状态**：`openclaw status` 应显示 running
2. **测试对话**：向你配置的渠道发送消息，AI 应该回复
3. **查看日志**：`openclaw logs` 检查是否有错误

## 下一步

部署完成后，你可以：

- 安装 Skills 扩展功能（搜索、代码执行、文件管理等）
- 配置更多消息渠道
- 自定义 Agent 的行为和记忆

下一篇将介绍如何配置各种消息渠道，让 OpenClaw 真正接入你的日常通讯工具。

---

**参考链接：**

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [GitHub 仓库](https://github.com/openclaw/openclaw)
- [Skill 市场](https://clawhub.com)
