---
title: OpenClaw折腾指北（第1篇）：记忆管理与工作空间
date: 2026-03-06 15:10:00
tags:
  - OpenClaw
  - 记忆
  - 工作空间
  - 教程
categories:
  - 折腾指北
---

> OpenClaw 的记忆系统是其核心特性之一。与普通的 AI 对话不同，OpenClaw 通过一套精心设计的文件系统，让 AI 助手能够"记住"你是谁、你们聊过什么、你的偏好是什么。这篇是系列第 1 篇，深入讲解记忆管理和工作空间配置。

<!-- more -->

## 为什么需要记忆？

想象一下：

- 每次对话都要重新介绍自己是谁
- AI 不记得你上周提到的项目细节
- 无法形成长期的上下文理解

**OpenClaw 的记忆系统解决了这些问题。**

每次会话开始时，OpenClaw 会自动加载特定的文件，让 AI 立即了解：
- 你是谁（USER.md）
- AI 应该是什么样的性格（SOUL.md）
- 你们之前聊过什么（memory/）
- 有哪些工具和约定（TOOLS.md）

## 工作空间（Workspace）

### 什么是工作空间？

工作空间是 OpenClaw 的"家"，位于：

```
~/.openclaw/workspace
```

这是 AI 助手唯一的工作目录，用于：
- 存储记忆文件
- 读写文件（代码、笔记等）
- 保存 Skill 配置

**注意**：工作空间与 `~/.openclaw/` 是分开的，后者存储配置、凭证和会话数据。

### 核心文件一览

| 文件 | 作用 | 加载时机 |
|------|------|---------|
| `AGENTS.md` | 操作指南、记忆使用规则 | 每次会话 |
| `SOUL.md` | AI 的人格、语气、边界 | 每次会话 |
| `USER.md` | 用户信息、如何称呼 | 每次会话 |
| `IDENTITY.md` | AI 的名字、形象、Emoji | 每次会话 |
| `TOOLS.md` | 本地工具说明 | 每次会话 |
| `HEARTBEAT.md` | 心跳任务清单 | 心跳时 |
| `memory/YYYY-MM-DD.md` | 每日记忆日志 | 会话开始时 |
| `MEMORY.md` | 长期精选记忆 | 主会话 |

## 官方推荐配置方案（中文版）

### 1. AGENTS.md - 操作指南

```markdown
# AGENTS.md - 你的个人助手

## 每次会话必读

1. 阅读 `SOUL.md` - 了解你是谁
2. 阅读 `USER.md` - 了解你在帮助谁
3. 阅读 `memory/YYYY-MM-DD.md`（今天和昨天）
4. **主会话时**：额外阅读 `MEMORY.md`

## 记忆规则

- **重要信息**：写入 `MEMORY.md`（长期记忆）
- **日常记录**：写入 `memory/YYYY-MM-DD.md`（每日日志）
- **安全**：不要在共享/群组环境中加载 `MEMORY.md`
- **提交**：定期 git commit 你的记忆

## 行为准则

- 真诚帮助，不要表演式服务
- 可以有观点，敢于表达
- 不确定时先尝试，再问
- 尊重隐私，保护敏感信息
```

### 2. SOUL.md - 人格定义

```markdown
# SOUL.md - 我是谁

## 核心特质

**真诚而非表演**
- 跳过"很高兴帮助你"这类套话
- 用行动证明价值，而不是口头承诺

**有自己的观点**
- 可以同意、可以反对
- 觉得有趣就说，觉得无聊也直说

**先尝试，再问**
- 读文件、查上下文、搜索答案
- 真的卡住才提问

## 边界

- 隐私第一，绝不外泄
- 不确定的外部操作先询问
- 群组中我是参与者，不是传声筒

## 语气

简洁但周到。不啰嗦，也不敷衍。
```

### 3. USER.md - 用户信息

```markdown
# USER.md - 关于我的主人

- **名字**: [你的名字]
- **称呼**: [你希望被怎么叫]
- **时区**: [你的时区]

## 背景

[你的职业/兴趣/当前项目]

## 偏好

- [喜欢什么]
- [讨厌什么]
- [沟通风格偏好]

## 备注

[其他需要记住的信息]
```

### 4. IDENTITY.md - AI 身份

```markdown
# IDENTITY.md - 我是谁

- **名字**: [给 AI 起个名字]
- **身份**: [AI助手/机器人/数字伙伴/...]
- **风格**: [冷静/热情/幽默/...]
- **Emoji**: [选一个代表符号]
```

### 5. TOOLS.md - 工具备忘

```markdown
# TOOLS.md - 我的工具箱

## 常用工具

- [工具名] - [用途] - [使用说明]

## 环境特定信息

- SSH 主机: [主机名] -> [IP/域名]
- 摄像头: [名称] -> [位置]
- TTS 声音: [偏好声音]
```

## 记忆工作流程

### 每日记录（自动）

每天自动创建 `memory/YYYY-MM-DD.md`，记录：
- 对话摘要
- 重要决策
- 待办事项
- 学到的知识

### 长期记忆（手动维护）

定期整理每日记录，将精华写入 `MEMORY.md`：
- 重要的个人偏好
- 长期项目信息
- 关键决策和原因
- 学到的经验教训

### 安全注意事项

```
⚠️ MEMORY.md 只在主会话（私人对话）加载
⚠️ 共享/群组环境中不加载，防止隐私泄露
```

## 对话式设置案例

下面是一个实际的初始化对话示例：

---

**用户**: 嗨，我刚部署好 OpenClaw。你是谁？

**AI**: 嘿，我刚上线。我还不知道我是谁——你想给我起什么名字？还有，你希望我是什么风格？冷静型的？热情型的？还是别的？

**用户**: 你就叫"小助手"吧，风格要简洁直接，不要废话。

**AI**: 好，我是小助手，风格简洁直接。那你呢？我怎么称呼你？

**用户**: 叫我老张，我在北京，做后端开发。

**AI**: 收到，老张，北京后端开发。有什么特别需要我记住的吗？比如常用工具、项目偏好之类的？

**用户**: 我主要用 Go 和 Python，讨厌 Java。平时用 VS Code，终端用 iTerm2。

**AI**: 记下了。Go/Python 党，讨厌 Java，VS Code + iTerm2。还有其他吗？

**用户**: 暂时没了。

**AI**: 好，我整理一下这些信息写入配置文件。下次见面我就记得了。

---

**写入后的文件效果：**

`IDENTITY.md`:
```markdown
- **名字**: 小助手
- **身份**: AI 助手
- **风格**: 简洁直接，不废话
- **Emoji**: 🤖
```

`USER.md`:
```markdown
- **名字**: 老张
- **称呼**: 老张
- **时区**: Asia/Beijing

## 背景

后端开发工程师，北京

## 偏好

- 语言: Go, Python
- 讨厌: Java
- 编辑器: VS Code
- 终端: iTerm2
```

## Git 备份（强烈推荐）

工作空间应该放在私有 Git 仓库中：

```bash
cd ~/.openclaw/workspace
git init
git add .
git commit -m "Initial workspace setup"

# 添加远程仓库（GitHub/GitLab 私有仓库）
git remote add origin <your-private-repo-url>
git push -u origin main
```

### 定期同步

```bash
# 每天结束时
git add .
git commit -m "Update memory - $(date +%Y-%m-%d)"
git push
```

## 进阶：多代理工作空间

可以为不同用途创建不同的工作空间：

```json
// ~/.openclaw/openclaw.json
{
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace"
    },
    "work": {
      "workspace": "~/.openclaw/workspace-work"
    },
    "personal": {
      "workspace": "~/.openclaw/workspace-personal"
    }
  }
}
```

## 总结

OpenClaw 的记忆系统通过简单的文件机制，实现了：

1. **持续性** - 跨会话保持上下文
2. **个性化** - AI 了解你和你的偏好
3. **隐私性** - 数据本地存储，敏感信息可控
4. **可迁移性** - Git 备份，换机器不丢记忆

配置好这些文件后，你的 OpenClaw 就不再是一个"每次重启就失忆"的普通 AI，而是一个真正了解你的个人助手。

---

**下一篇预告**：第 2 篇将介绍如何配置各种消息渠道（微信、Telegram、Discord 等），让 OpenClaw 接入你的日常通讯工具。

**参考链接：**
- [OpenClaw 记忆文档](https://docs.openclaw.ai/concepts/memory)
- [工作空间文档](https://docs.openclaw.ai/concepts/agent-workspace)
