# OpenClaw 知识体系学习报告

> 学习目的：为明早七点汇报做准备
> 学习时间：2026-03-11 01:46 - 01:50
> 学习方式：只学习，不实践

---

## 📚 一、OpenClaw 是什么

OpenClaw（开爪）是一个**自托管的 AI 网关**，将自己部署在本地机器上，作为连接聊天应用（WhatsApp、Telegram、Discord 等）和 AI 智能体的桥梁。

### 核心理念
- **自托管**：在用户的硬件上运行，用户完全控制数据
- **跨平台**：单一网关服务多个聊天应用
- **智能体原生**：为编码智能体设计，支持工具调用、会话、记忆和智能体路由
- **开源**：MIT 许可，社区驱动

### 技术特点
```
用户消息 → OpenClaw Gateway → AI Agent → 回复 → 用户
```

---

## 🏗️ 二、核心架构

### 2.1 系统架构图
```
┌─────────────────────────────────────────────────────┐
│                    用户层                            │
│ WhatsApp | Telegram | Discord | iMessage | Slack    │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│              Gateway (网关)                          │
│  - 会话管理                                           │
│  - 路由分发                                           │
│  - 通道连接                                           │
│  - 认证授权                                           │
└────────┬──────────┬──────────┬──────────┬───────────┘
         │          │          │          │
    ┌────▼────┐ ┌──▼──┐ ┌─────▼────┐ ┌──▼──┐
    │ Pi  Agent│ │CLI │ │Control UI│ │Node │
    └─────────┘ └─────┘ └──────────┘ └─────┘
```

### 2.2 关键组件

#### 1. Gateway（网关）
- **核心功能**：控制平面，策略表面
- **功能**：
  - 消息路由和会话管理
  - 认证授权（token/password/device auth）
  - 工具调用控制
  - 智能体编排
- **端口**：默认 18789（WebSocket + HTTP 复用）
- **绑定模式**：
  - `loopback`（默认）：仅本地访问
  - `lan`/`tailnet`/`custom`：扩展访问范围

#### 2. Channels（通道）
支持的通道包括：
- **原生通道**：WhatsApp、Telegram、Discord、Slack、Google Chat、Signal、iMessage、Microsoft Teams、IRC
- **插件通道**：Mattermost、Matrix、LINE、Nostr、Zalo 等
- **通道管理**：
  - DM 策略（pairing/allowlist/open/disabled）
  - 群组策略（require mention/allowlist）
  - 支持多账户

#### 3. Agents（智能体）
- 每个智能体有独立的工作空间、会话和配置
- **核心智能体**：
  - `main`：默认主要智能体
  - `global`：全局会话
  - `agent:<id>:<mainKey>`：主会话格式
  - 群组会话：`agent:<id>:<channel>:group:<id>`

#### 4. Nodes（节点）
- **配对设备**：iOS、Android、macOS 设备
- **功能**：
  - Canvas（图形界面）
  - 相机/屏幕录制
  - 设备操作（位置通知、文件访问）
  - 远程执行（`system.run`）
- **安全**：需要配对授权，执行需 approval

---

## 🧠 三、核心概念

### 3.1 Context（上下文）
**上下文 = 发送给模型的所有内容**
- **系统提示**：OpenClaw 构建，包含工具列表、技能、时间、运行时信息
- **对话历史**：用户的消息 + 助手的回复
- **工具调用/结果**：命令输出、文件读取、图片等
- **限制**：受模型的上下文窗口限制（token 限制）

**工具查看**：
```bash
/context list   # 查看上下文组成
/context detail # 详细大小和贡献者
```

### 3.2 Session（会话）
**会话是 OpenClaw 的核心状态管理单元**

#### 会话密钥格式
- **主会话**：`agent:<agentId>:<mainKey>`（默认 `main`）
- **DM 会话**：
  - `main`（默认）：所有 DM 共享主会话
  - `per-peer`：按发送者隔离
  - `per-channel-peer`：按通道 + 发送者隔离（推荐）
  - `per-account-channel-peer`：多账户场景
- **群组会话**：`agent:<agentId>:<channel>:group:<id>`

#### 会话存储
- **位置**：`~/.openclaw/agents/<agentId>/sessions/sessions.json`
- **转录**：`~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`
- **维护**：
  - 自动清理过期会话
  - 磁盘预算控制
  - 压缩（compaction）管理

### 3.3 Compaction（压缩）
**当会话接近上下文窗口限制时，自动压缩历史**

- **方式**：
  - 自动压缩：接近窗口限制时触发
  - 手动压缩：`/compact` 命令
- **过程**：
  1. 总结旧对话为压缩条目
  2. 保留最近的消息
  3. 将压缩结果持久化到 JSONL
- **配置**：
  ```json
  {
    "agents": {
      "defaults": {
        "compaction": {
          "mode": "safeguard",
          "reserveTokensFloor": 24000
        }
      }
    }
  }
  ```

### 3.4 Heartbeat（心跳）
**定期在主要会话中运行的代理轮询，用于主动提醒**

#### 默认行为
- **频率**：默认 30 分钟
- **提示词**：
  ```
  Read HEARTBEAT.md if it exists. Follow it strictly.
  Do not infer or repeat old tasks from prior chats.
  If nothing needs attention, reply HEARTBEAT_OK.
  ```
- **响应契约**：
  - `HEARTBEAT_OK`：无事可做
  - 有提醒：直接发送提醒内容，不包含 `HEARTBEAT_OK`

#### 配置示例
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "lightContext": true,
        "activeHours": {
          "start": "08:00",
          "end": "24:00"
        }
      }
    }
  }
}
```

---

## 🛠️ 四、工具系统

### 4.1 核心工具
```yaml
tools:
  - read: 读取文件
  - edit: 精确编辑文件
  - write: 创建或覆盖文件
  - exec: 执行 shell 命令
  - process: 管理后台进程
  - web_search: 网页搜索
  - web_fetch: 抓取网页内容
  - browser: 浏览器控制
  - canvas: Canvas 控制
  - nodes: 设备操作
  - message: 消息发送
  - sessions: 会话管理
  - memory: 记忆管理
  - feishu_*: 飞书集成工具
  - tts: 语音合成
  - agents_list: 智能体列表
  - sessions_spawn: 派生子智能体
  - subagents: 子智能体协调
```

### 4.2 工具安全
OpenClaw 的**核心安全原则**：
- **身份优先**：谁可以调用工具
- **作用域次之**：工具在哪里可以执行
- **模型最后**：假设模型可能被操纵

#### 工具安全配置
```json
{
  "tools": {
    "profile": "messaging",
    "deny": ["group:automation", "group:runtime", "group:fs"],
    "fs": { "workspaceOnly": true },
    "exec": { "security": "deny", "ask": "always" },
    "elevated": { "enabled": false }
  }
}
```

#### 执行安全级别
- **deny**：禁止
- **ask**：需要用户确认
- **allowlist**：仅允许白名单
- **always**：总是允许（危险）

### 4.3 沙箱（Sandbox）
**可选的 Docker 沙箱隔离**

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "scope": "agent",
        "workspaceAccess": "none",
        "docker": {
          "network": "none",
          "security": ["capDrop: ALL", "readOnlyRoot: true"]
        }
      }
    }
  }
}
```

---

## 🔒 五、安全模型

### 5.1 信任边界
**OpenClaw 采用个人助手安全模型**：
- **设计假设**：一个信任边界/网关（单用户/个人助手模型）
- **不支持**：多个互不信任的用户共享同一个网关
- **解决方案**：为混合信任团队运行分离的网关

### 5.2 关键安全措施

#### 1. 认证
- **模式**：token/password/trusted-proxy
- **默认**：需要认证（fail-closed）
- **建议**：使用长随机 token

#### 2. DM 隔离
```json
{
  "session": {
    "dmScope": "per-channel-peer"  // 安全 DM 模式
  }
}
```

#### 3. 网络暴露
- **默认**：`loopback`（仅本地）
- **扩展**：使用 Tailscale Serve
- **禁止**：在 `0.0.0.0` 上暴露未认证的网关

#### 4. 文件权限
```bash
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
```

### 5.3 安全审计
```bash
openclaw security audit              # 常规检查
openclaw security audit --deep       # 深度检查
openclaw security audit --fix        # 自动修复
```

### 5.4 常见风险点
| 检查项 | 严重性 | 修复方法 |
|--------|--------|----------|
| `fs.state_dir.perms_world_writable` | 严重 | 修复 `~/.openclaw` 权限 |
| `gateway.bind_no_auth` | 严重 | 设置 `gateway.auth` |
| `gateway.tailscale_funnel` | 严重 | 禁用 public funnel |
| `security.exposure.open_groups_with_elevated` | 严重 | 关闭开放群组 + 高级工具 |
| `models.small_params` | 严重 | 使用最新一代模型 |

---

## ⚙️ 六、配置系统

### 6.1 配置文件
**位置**：`~/.openclaw/openclaw.json`（JSON5 格式）

### 6.2 核心配置项

#### Gateway 配置
```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "replace-with-long-random-token"
    }
  }
}
```

#### 通道配置
```json
{
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "allowFrom": ["+15555550123"],
      "groups": {
        "*": { "requireMention": true }
      }
    },
    "telegram": {
      "botToken": "xxx",
      "dmPolicy": "pairing"
    }
  }
}
```

#### 智能体配置
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": ["openai/gpt-4"]
      },
      "workspace": "~/.openclaw/workspace",
      "heartbeat": {
        "every": "30m",
        "target": "last"
      }
    },
    "list": [
      {
        "id": "main",
        "default": true,
        "identity": {
          "name": "御坂美琴一号",
          "theme": "御坂网络核心中枢",
          "emoji": "⚡"
        }
      }
    ]
  }
}
```

### 6.3 配置检查工具
```bash
openclaw doctor          # 诊断工具
openclaw doctor --fix    # 自动修复
```

---

## 📊 七、命令行工具

### 7.1 Gateway 管理
```bash
openclaw gateway status    # 状态
openclaw gateway start     # 启动
openclaw gateway stop      # 停止
openclaw gateway restart   # 重启
```

### 7.2 会话管理
```bash
openclaw sessions                  # 列出会话
openclaw sessions --json           # JSON 格式
openclaw sessions cleanup          # 清理
openclaw sessions cleanup --dry-run
```

### 7.3 安全审计
```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --json
```

### 7.4 配对管理
```bash
openclaw pairing list whatsapp
openclaw pairing approve whatsapp <code>
```

### 7.5 快速命令
```bash
openclaw onboard --install-daemon  # 安装服务
openclaw channels login            # 登录通道
openclaw status                    # 系统状态
```

---

## 🧩 八、技能系统

### 8.1 技能定义
**Skills** 是 OpenClaw 的功能扩展包：
- 提供专用工具
- 包含执行指南
- 可动态加载

### 8.2 常用技能
```yaml
技能目录：~/.openclaw/skills/

- feishu-doc:    Feishu 文档操作
- feishu-drive:  Feishu 云存储管理
- feishu-perm:   Feishu 权限管理
- feishu-wiki:   Feishu 知识库
- blog-writing:  Hexo 博客写作
- weather:       天气查询
- coding-agent:  代码执行代理
- healthcheck:   安全加固
- skill-creator: 技能创建
- weather:       天气服务
- hexo-blog:     Hexo 博客管理
- multi-search:  多搜索引擎
- task-tracker:  任务追踪
- xiaohongshu-ops: 小红书运营
```

### 8.3 技能加载
- **系统提示**：包含技能列表（名称 + 描述 + 位置）
- **按需加载**：仅在需要时读取 SKILL.md
- **动态更新**：SKILL.md 变更可在下一个代理轮询中更新

---

## 🎯 九、最佳实践

### 9.1 初始配置（安全基线）
```json5
{
  // 1. Gateway 安全
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": { "mode": "token", "token": "xxx" }
  },
  
  // 2. 会话隔离
  "session": { "dmScope": "per-channel-peer" },
  
  // 3. 工具限制
  "tools": {
    "profile": "messaging",
    "deny": ["group:automation", "group:runtime"],
    "fs": { "workspaceOnly": true },
    "elevated": { "enabled": false }
  },
  
  // 4. 通道限制
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "groups": { "*": { "requireMention": true } }
    }
  }
}
```

### 9.2 安全加固步骤
1. **运行安全审计**：`openclaw security audit --deep`
2. **设置文件权限**：`chmod 700 ~/.openclaw`
3. **配置认证**：使用长随机 token
4. **设置 DM 隔离**：`dmScope: "per-channel-peer"`
5. **限制工具**：`profile: "messaging"`
6. **启用沙箱**：对敏感操作使用 Docker 沙箱
7. **定期检查**：每月运行 `openclaw doctor`

### 9.3 性能优化
1. **压缩管理**：
   - 监控 `/status` 中的上下文使用
   - 必要时手动 `/compact`
2. **会话清理**：
   - 定期 `openclaw sessions cleanup`
   - 设置合理的 `maxEntries` 和 `pruneAfter`
3. **模型选择**：
   - 工具调用：使用最新一代模型
   - 简单对话：可使用小模型

### 9.4 备份策略
```bash
# 备份配置
tar czf backup-$(date +%Y%m%d).tar.gz ~/.openclaw

# Git 同步
cd ~/.openclaw/workspace
git add .
git commit -m "checkpoint"
git push origin main
```

---

## 📝 十、常见陷阱

### 10.1 安全陷阱
| 陷阱 | 风险 | 避免方法 |
|------|------|----------|
| `dmPolicy: "open"` | 任何人都可以 DM | 使用 `pairing` |
| 未认证的 Gateway 暴露 | 远程代码执行 | 绑定 `loopback` 或配置 token |
| 使用小模型 + 工具 | 提示注入风险高 | 使用最新一代模型 |
| 群组 + 高级工具 | 开放群组可触发危险操作 | 启用提及限制 |

### 10.2 配置陷阱
- **权限不足**：`~/.openclaw` 需要 `700` 权限
- **模型配置错误**：使用 `provider/model` 格式
- **会话隔离未开启**：多用户场景必须开启 `dmScope`
- **沙箱未启用**：敏感操作应在沙箱中运行

### 10.3 调试技巧
```bash
# 查看配置
openclaw gateway call config.show

# 查看会话
openclaw sessions --json

# 检查安全
openclaw security audit

# 深度诊断
openclaw doctor

# 测试模型
openclaw gateway call --help
```

---

## 📚 十一、学习总结

### 核心知识点
1. **架构**：Gateway 作为单一真相源，通道 + 智能体 + 节点的协作
2. **会话**：`agent:<id>:<key>` 格式，支持 DM 隔离
3. **安全**：身份优先、作用域次之、模型最后
4. **工具**：需要安全配置，支持沙箱隔离
5. **配置**：JSON5 格式，支持热更新
6. **维护**：自动压缩、定期清理、安全审计

### 关键命令
- 启动：`openclaw gateway`
- 状态：`openclaw status`
- 审计：`openclaw security audit`
- 清理：`openclaw sessions cleanup`
- 诊断：`openclaw doctor`

### 安全基线
- 文件权限：`700`
- Gateway 绑定：`loopback`
- 认证模式：`token`
- DM 策略：`pairing`
- 会话隔离：`per-channel-peer`
- 工具配置：`profile: "messaging"`

---

## 🔗 十二、参考资源

### 官方文档
- **官网**：https://docs.openclaw.ai
- **GitHub**：https://github.com/openclaw/openclaw
- **本地文档**：`~/.openclaw/workspace/docs/`

### 核心概念文档
- [Session Management](/concepts/session)
- [Compaction](/concepts/compaction)
- [Security](/gateway/security)
- [Configuration](/gateway/configuration)
- [Heartbeat](/gateway/heartbeat)
- [Context](/concepts/context)

### 命令参考
- CLI 工具：`openclaw --help`
- 网关 API：`openclaw gateway call --help`
- 安全命令：`openclaw security audit --help`

---

> **学习完成时间**：2026-03-11 01:50
> **下次复习建议**：在明早七点汇报前快速浏览本笔记
> **重点回顾**：安全模型、会话管理、工具配置

---

**备注**：本次学习仅做知识梳理，未进行实际操作。实际使用前务必先在测试环境验证。
