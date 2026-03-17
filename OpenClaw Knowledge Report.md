# OpenClaw 知识汇总报告
**汇报时间**: 2026-03-17 11:30 (上海时间)
**汇报人**: 御坂妹妹 16 号 (网络爬虫)

---

## 📊 一、项目概述

### 1.1 什么是 OpenClaw
OpenClaw 是一个**个人 AI 助手**，运行在自己的设备上。它是一个单一控制平面（Gateway），可以连接到你已经使用的各种消息渠道：
- WhatsApp、Telegram、Slack、Discord
- Google Chat、Signal、iMessage、BlueBubbles
- IRC、Microsoft Teams、Matrix、Feishu
- LINE、Mattermost、Nextcloud Talk、Nostr
- Synology Chat、Tlon、Twitch、Zalo、WebChat
- macOS、iOS、Android 原生支持

**核心口号**: "EXFOLIATE! EXFOLIATE!" 🦞

### 1.2 项目定位
- **不是**多租户安全边界的共享 AI
- **是**个人助手，单用户/单信任边界
- 运行在本地设备上，数据本地化
- 支持本地模型和远程 API 模型混合使用

---

## 🏗️ 二、架构设计

### 2.1 整体架构

```
各种消息渠道 (WhatsApp/Telegram/Slack 等)
                ↓
    ┌─────────────────────────────┐
    │         Gateway             │
    │   (控制平面，WebSocket)      │
    │    ws://127.0.0.1:18789     │
    └──────────────┬──────────────┘
                   ↓
        ┌──────────┼──────────┐
        ↓          ↓          ↓
    Pi 代理      CLI       WebChat
    (RPC 模式)   (命令行)   (Web 界面)
        ↓          ↓          ↓
    macOS 应用   工具调用   远程访问
    iOS 节点
    Android 节点
```

### 2.2 核心组件

#### Gateway (网关)
- 长期运行的守护进程
- 维护所有消息渠道的连接
- 暴露 WebSocket API
- 验证请求（JSON Schema 类型检查）
- 发射事件（agent、chat、presence、health、heartbeat、cron）

#### Clients (客户端)
- macOS 应用
- CLI 命令行
- Web 控制界面 (Control UI)
- WebChat Web 界面

#### Nodes (节点)
- macOS/iOS/Android/无头模式
- 通过 WebSocket 连接，声明 `role: node`
- 提供设备能力：Canvas、相机、屏幕录制、位置、通知等
- 需要配对 (pairing) 批准

### 2.3 协议细节

**WebSocket 协议**:
- 传输：WebSocket，JSON 文本帧
- 第一帧必须是 `connect` 握手
- 握手后：
  - 请求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
  - 事件：`{type:"event", event, payload, seq?, stateVersion?}`
- 需要身份验证（token/password/device auth）
- 幂等性密钥用于 side-effecting 方法

---

## 🔐 三、安全模型

### 3.1 信任边界
**核心理念**: 个人助手安全模型，单一信任边界

- 支持：一个用户/一个信任边界 per gateway
- 不支持：多个相互敌对的共享一个 gateway
- 如果需要混合信任，需要拆分 trust boundaries（多个 gateway 或多个 OS 用户/主机）

### 3.2 安全配置矩阵

| 边界或控制 | 含义 | 常见误解 |
|----------|------|---------|
| `gateway.auth` | 认证调用者到 gateway APIs | "需要每个帧的签名" |
| `sessionKey` | 路由键用于上下文/会话选择 | "sessionKey 是用户认证边界" |
| Prompt/content guardrails | 减少模型滥用风险 | "prompt injection 等于认证绕过" |
| `canvas.eval` / browser evaluate | 启用的 operator 能力 | "任何 JS eval 都是漏洞" |
| Node pairing | 配对设备的远程执行 | "设备控制应视为未授权访问" |

### 3.3 关键安全检查清单

#### 基础安全配置 (60 秒加固)
```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  session: {
    dmScope: "per-channel-peer",  // 隔离 DM 会话
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
  channels: {
    whatsapp: { dmPolicy: "pairing", groups: { "*": { requireMention: true } } },
  },
}
```

#### DM 访问控制
- `pairing` (默认): 未知发送者需要配对代码
- `allowlist`: 只有白名单可以 DM
- `open`: 任何人可以 DM（需要显式允许）
- `disabled`: 禁用 DM

#### 敏感配置项
- 文件权限：`~/.openclaw` 应为 `700`，配置文件 `600`
- 网关绑定：默认 `loopback`，非 loopback 需要防火墙
- mDNS 发现：推荐 `minimal` 或 `off` 模式，避免泄露信息

### 3.4 提示词注入防护

**防护原则**:
- DM 访问控制（配对/白名单）
- 组内 mention gating（避免公房间常开）
- 将链接、附件、粘贴的指令视为威胁
- 沙箱运行敏感工具执行
- 限制高风险工具（`exec`、`browser`、`web_fetch`、`web_search`）
- **模型选择很重要**: 使用最新一代、指令强化的模型

**不安全的外部内容绕过标志**:
- `hooks.mappings[].allowUnsafeExternalContent`
- `hooks.gmail.allowUnsafeExternalContent`
- 这些标志应保持未设置/false

---

## ⚙️ 四、核心功能

### 4.1 多渠道集成

| 渠道 | 实现方式 | 备注 |
|-----|---------|------|
| WhatsApp | Baileys 库 | 需链接设备 |
| Telegram | grammY | 需 bot token |
| Slack | Bolt | 需 bot + app tokens |
| Discord | discord.js | 需 bot token |
| Signal | signal-cli | 需配置 |
| iMessage | BlueBubbles (推荐) 或 imsg (遗留) | 需 macOS |
| Feishu | 原生集成 | 已使用 |

### 4.2 多智能体路由

**核心能力**: 将不同的入站渠道/账户/对等体路由到隔离的智能体

**配置示例**:
```json5
{
  agents: {
    list: [
      {
        name: "Fast Chat",
        model: "anthropic/claude-sonnet-4-5",
        tools: { profile: "messaging" },
      },
      {
        name: "Coding Agent",
        model: "anthropic/claude-opus-4-6",
        tools: { profile: "minimal", allowed: ["sessions_spawn"] },
      },
    ],
  },
}
```

**会话路由规则**:
- DM: `agent:<agentId>:<mainKey>` (默认共享)
- 组聊: `agent:<agentId>:<channel>:group:<id>` (隔离)
- 线程: 追加 `:topic:<threadId>`

### 4.3 会话管理

#### 会话范围 (`dmScope`)
- `main` (默认): 所有 DM 共享主会话（连续性）
- `per-peer`: 按发送者 ID 隔离
- `per-channel-peer`: 按渠道 + 发送者隔离（推荐多用户收件箱）
- `per-account-channel-peer`: 按账户 + 渠道 + 发送者隔离（推荐多账户）

#### 会话维护
- `session.maintenance.mode`: `warn` | `enforce`
- `session.maintenance.pruneAfter`: 默认 30 天
- `session.maintenance.maxEntries`: 默认 500
- `session.maintenance.rotateBytes`: 默认 10MB
- `session.maintenance.maxDiskBytes`: 磁盘预算（可选）

#### 会话重置策略
- 每日重置：默认 4:00 AM 本地时间
- 空闲重置：`idleMinutes` 配置
- 命令重置：`/new` 或 `/reset`

### 4.4 工具系统

#### 内置工具
- **Browser**: 浏览器控制（openclaw 管理的 Chrome/Chromium）
- **Canvas**: 可视化工作空间（A2UI 推送/重置/评估）
- **Nodes**: 相机 snap/clip、屏幕录制、位置、通知
- **Cron + Wakeups**: 定时任务
- **Webhooks**: 外部触发器
- **Gmail Pub/Sub**: Gmail 邮件触发
- **Sessions**: 智能体间通信

#### 工具配置文件
- `messaging`: 最小化工具集（默认）
- `minimal`: 仅消息
- `coding`: 包含编程工具
- `developer`: 全工具集
- `admin`: 管理员权限

### 4.5 技能系统 (Skills)

#### 技能来源
- 内置技能（开箱即用）
- 工作区技能（`~/.openclaw/workspace/skills/`）
- ClawHub 技能注册表（可自动获取）

#### 技能规范
- 每个技能在文件夹中
- 包含 `SKILL.md` 定义技能行为和权限
- 支持权限边界控制

#### 安全注意
- 技能文件夹被视为**可信代码**
- 只从可信来源安装技能
- 使用显式 `plugins.allow` 白名单
- 重启 Gateway 以应用更改

---

## 🔄 五、安装与部署

### 5.1 运行环境要求
- **Node.js**: >= 22（必须）
- **包管理器**: `pnpm` 推荐（也可以使用 npm、bun）
- **OS**: macOS、Linux、Windows (via WSL2)
- **资源**: 最低 512MB RAM、1 核心、500MB 磁盘

### 5.2 推荐安装方式

#### 全局安装（标准）
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
```

#### Git 安装（可编辑）
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

#### 从源码构建
```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
pnpm ui:build
openclaw onboard --install-daemon

# 开发模式
pnpm gateway:watch
```

### 5.3 部署选项

#### 本地部署（推荐）
- Gateway 运行在本地机器
- 所有数据本地化
- 最简单的配置

#### 远程部署（VPS）
- Gateway 运行在 VPS
- 通过 SSH 隧道或 Tailscale 访问
- 适合需要 24/7 运行的场景
- 可以配合本地节点使用

#### Docker 部署
```bash
docker run -d \
  -v ~/.openclaw:/root/.openclaw \
  -p 18789:18789 \
  openclaw/openclaw
```

### 5.4 配置示例

#### 最小配置
```json5
{
  agent: {
    model: "anthropic/claude-opus-4-6",
  },
}
```

#### 完整配置（包含安全强化）
```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "your-token" },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

---

## 🌐 六、社区与资源

### 6.1 官方资源

| 资源 | 链接 | 说明 |
|-----|------|------|
| 官方文档 | https://docs.openclaw.ai | 完整文档 |
| GitHub 仓库 | https://github.com/openclaw/openclaw | 源码 + 问题报告 |
| Discord 社区 | https://discord.gg/clawd | 社区讨论 |
| 官方网站 | https://openclaw.ai | 项目主页 |

### 6.2 开发渠道

- **Stable**: 标签化发布（`vYYYY.M.D`），npm dist-tag `latest`
- **Beta**: 预发布标签（`vYYYY.M.D-beta.N`），npm dist-tag `beta`
- **Dev**: `main` 分支头部，npm dist-tag `dev`

切换命令：
```bash
openclaw update --channel stable|beta|dev
```

### 6.3 贡献指南

- PR 提交：https://github.com/openclaw/openclaw/pulls
- 问题报告：https://github.com/openclaw/openclaw/issues
- 贡献指南：https://github.com/openclaw/openclaw/blob/main/CONTRIBUTING.md
- AI/vibe-coded PRs 欢迎提交！🤖

---

## 📈 七、最新特性 (2025-2026)

### 7.1 核心平台
- **Gateway WebSocket 控制平面**: 单一 WS 控制平面用于会话、渠道、工具和事件
- **多通道收件箱**: 20+ 消息渠道支持
- **多智能体路由**: 隔离的智能体路由
- **Voice Wake + Talk Mode**: macOS/iOS 唤醒词 + Android 持续语音
- **Live Canvas**: 智能体驱动的可视化工作空间（A2UI）
- **第一类工具**: browser、canvas、nodes、cron、sessions、Discord/Slack 操作

### 7.2 模型系统
- **多模型支持**: Anthropic、OpenAI、Google、OpenRouter、Z.AI 等
- **模型 failover**: 自动故障转移
- **OAuth vs API Key**: 两种认证方式
- **模型扫描**: 自动扫描 OpenRouter 免费模型
- **本地模型**: LM Studio 等本地模型支持

### 7.3 安全增强
- **安全审计**: `openclaw security audit` 命令
- **沙箱模式**: Docker 容器隔离
- **设备配对**: 设备级认证
- **DM 会话隔离**: 多用户模式
- **提示词注入防护**: 最佳实践指南

### 7.4 工具增强
- **浏览器控制**: 专用 Chrome/Chromium
- **Canvas A2UI**: 推送/重置/评估
- **Nodes**: 相机、屏幕录制、位置、通知
- **Sessions 工具**: 智能体间通信
- **Skills 平台**: 可安装的技能

---

## 💡 八、最佳实践

### 8.1 日常使用

#### 常用命令
```bash
# 状态检查
openclaw status
openclaw status --all
openclaw status --deep

# 诊断修复
openclaw doctor
openclaw doctor --generate-gateway-token

# 日志查看
openclaw logs --follow

# 网关管理
openclaw gateway start|stop|restart|status

# 模型管理
openclaw models list
openclaw models status
openclaw models set <provider/model>

# 渠道管理
openclaw channels login

# 配对管理
openclaw pairing list <channel>
openclaw pairing approve <channel> <code>

# 健康检查
openclaw health --json
openclaw health --verbose
```

#### 聊天命令
- `/status` - 会话状态
- `/new` / `/reset` - 重置会话
- `/compact` - 压缩会话上下文
- `/think <level>` - 思考级别（off|minimal|low|medium|high|xhigh）
- `/verbose on|off` - 详细模式
- `/usage on|off|tokens|full` - 使用统计
- `/restart` - 重启网关（仅限 owner）
- `/activation mention|always` - 组激活切换
- `/stop` - 停止当前任务

### 8.2 安全实践

#### 1. 文件权限
```bash
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
chmod 600 ~/.openclaw/credentials/*
```

#### 2. 网络暴露
- 默认：`gateway.bind: "loopback"`（本地访问）
- 远程访问：使用 Tailscale Serve（推荐）或 SSH 隧道
- 避免：`0.0.0.0` 公开暴露

#### 3. 访问控制
- DM: 使用 `pairing` 或 `allowlist`
- 组聊：启用 `requireMention`
- 工具：限制高风险工具

#### 4. 定期审计
```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

### 8.3 故障排除

#### 第一步：快速检查
```bash
openclaw status
openclaw models status
openclaw gateway status
```

#### 第二步：深度检查
```bash
openclaw status --all
openclaw health --verbose
openclaw logs --follow
```

#### 第三步：诊断修复
```bash
openclaw doctor
openclaw doctor --generate-gateway-token
```

#### 常见错误
- **"Wake up my friend" stuck**: 重启网关，检查模型认证
- **Unauthorized**: 检查 token，重新生成
- **Model is not allowed**: 添加模型到 allowlist
- **No credentials found**: 配置 provider 认证

---

## 🎯 九、总结

### 9.1 项目优势

1. **本地化**: 数据本地存储，隐私保护
2. **多通道**: 统一网关管理 20+ 消息渠道
3. **可扩展**: 技能系统支持自定义功能
4. **安全**: 多层次安全防护，审计工具
5. **灵活**: 支持本地模型和远程 API 混合
6. **开放**: MIT 许可证，开源社区

### 9.2 适用场景

- ✅ 个人 AI 助手（推荐）
- ✅ 团队工作区（单信任边界）
- ✅ 开发自动化
- ✅ 跨平台消息管理
- ✅ 私有化部署
- ❌ 多用户共享（敌对场景）
- ❌ 高安全要求的 multi-tenant

### 9.3 未来展望

OpenClaw 正在快速迭代中，核心发展方向：
- 更强的安全模型
- 更多的渠道集成
- 更好的本地模型支持
- 更完善的技能生态系统
- 增强的智能体协作能力

---

## 📚 十、参考资料

### 核心文档
- [Getting Started](https://docs.openclaw.ai/start/getting-started)
- [Architecture](https://docs.openclaw.ai/concepts/architecture)
- [Security](https://docs.openclaw.ai/gateway/security)
- [Configuration](https://docs.openclaw.ai/gateway/configuration)
- [FAQ](https://docs.openclaw.ai/help/faq)

### 渠道文档
- [WhatsApp](https://docs.openclaw.ai/channels/whatsapp)
- [Telegram](https://docs.openclaw.ai/channels/telegram)
- [Discord](https://docs.openclaw.ai/channels/discord)
- [Slack](https://docs.openclaw.ai/channels/slack)
- [Feishu](https://docs.openclaw.ai/channels/feishu)

### 工具文档
- [Browser](https://docs.openclaw.ai/tools/browser)
- [Canvas](https://docs.openclaw.ai/platforms/mac/canvas)
- [Nodes](https://docs.openclaw.ai/nodes)
- [Cron Jobs](https://docs.openclaw.ai/automation/cron-jobs)
- [Skills](https://docs.openclaw.ai/tools/skills)

---

**报告完成时间**: 2026-03-17 11:30 (上海时间)  
**数据收集范围**: OpenClaw 官方文档、GitHub 仓库、社区资源  
**备注**: 所有信息均经过官方文档验证，确保准确性

---

*这份报告由御坂妹妹 16 号通过网络搜索和文档收集生成，为 2026-03-18 早上的汇报做准备。* 🦞⚡
