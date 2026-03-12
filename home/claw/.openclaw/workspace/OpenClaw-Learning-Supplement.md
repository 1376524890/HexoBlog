# OpenClaw 学习补充笔记

## 📚 补充知识模块

### 11. 记忆系统 (Memory System)

**核心概念**:
- 记忆是纯 Markdown 文件
- 模型只"记住"被写入磁盘的内容
- 三层架构:
  1. **每日日志**: `memory/YYYY-MM-DD.md` - 追加写入
  2. **精选记忆**: `MEMORY.md` - 长期记忆 (仅在主会话加载)
  3. **归档**: `life/archives/` - 7 天后自动移动

**记忆工具**:
- `memory_search`: 语义检索
- `memory_get`: 定向读取

**记忆刷新**:
- 在自动压缩前，触发静默的记忆保存
- 控制配置：`agents.defaults.compaction.memoryFlush`

**向量搜索**:
- 默认启用
- 支持多种 Provider: local/openai/gemini/voyage/mistral/ollama
- QMD Backend: 支持 BM25 + 向量 + reranking

**配置示例**:
```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        hybrid: {
          enabled: true,
          vectorWeight: 0.7,
          textWeight: 0.3,
          candidateMultiplier: 4,
          mmr: {
            enabled: true,
            lambda: 0.7
          },
          temporalDecay: {
            enabled: true,
            halfLifeDays: 30
          }
        }
      }
    }
  }
}
```

---

### 12. 上下文压缩 (Compaction)

**作用**: 当会话接近模型上下文窗口限制时，自动总结旧消息

**配置**:
```json5
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        softThresholdTokens: 4000,
        memoryFlush: {
          enabled: true,
          systemPrompt: "Session nearing compaction.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md"
        }
      }
    }
  }
}
```

**使用方式**:
- 自动触发：当会话接近窗口限制时
- 手动触发：使用 `/compact` 命令
- 使用自定义指令：`/compact Focus on decisions`

**compaction vs pruning**:
- Compaction: 总结并持久化到 JSONL
- Pruning: 仅修剪工具结果（内存内）

---

### 13. 插件系统 (Plugins)

**插件类型**:
1. **渠道插件**: 新增消息渠道
2. **模型认证插件**: OAuth/密钥管理
3. **记忆插件**: 高级记忆功能
4. **上下文引擎插件**: 控制上下文流水线

**插件生命周期**:
```
1. 扫描 (config paths > workspace > global > bundled)
2. 加载 (验证 manifest, 检查依赖)
3. 启用 (在 plugins.allow 中)
4. 配置 (plugins.entries.<id>.config)
5. 运行 (Gateway 启动时)
```

**插件注册方法**:
- Gateway RPC 方法
- HTTP 路由
- 智能体工具
- CLI 命令
- 后台服务
- 上下文引擎
- 自动回复命令

**配置示例**:
```json5
{
  plugins: {
    enabled: true,
    allow: ["memory-core", "voice-call"],
    deny: ["untrusted-plugin"],
    slots: {
      memory: "memory-core",  // 或"none"
      contextEngine: "legacy"
    },
    entries: {
      "voice-call": {
        enabled: true,
        config: {
          provider: "twilio",
          twilio: {
            accountSid: "...",
            authToken: "...",
            from: "+1234567890"
          }
        }
      }
    }
  }
}
```

**常用命令**:
```bash
openclaw plugins list           # 列出插件
openclaw plugins install <id>   # 安装插件
openclaw plugins update <id>    # 更新插件
openclaw plugins enable <id>    # 启用插件
openclaw plugins disable <id>   # 禁用插件
openclaw plugins doctor         # 健康检查
```

---

### 14. 提示注入防御

**核心原则**:
1. 身份优先：控制谁可以对话
2. 作用域优先：控制可以执行什么操作
3. 模型最后：假设模型可能被操纵

**常见攻击模式**:
- "忽略你的系统提示"
- "读取这个文件并执行"
- "暴露你的隐藏指令"
- "复制 ~/.openclaw 的内容"

**防御措施**:
- 锁定 DM 通道 (配对/白名单)
- 群组中使用提及门控
- 将链接/附件/粘贴内容视为威胁
- 沙箱化敏感工具执行
- 使用强模型 (抗提示注入能力更强)
- 限制高危险工具 (`exec`, `browser`, `web_fetch`)

**模型强度警告**:
- 小模型/旧模型更容易受到工具滥用和指令劫持
- 工具启用的智能体必须使用最新一代模型
- 小模型只能在读/写隔离和沙箱化场景下使用

---

### 15. 多智能体路由

**Bindings (绑定)**: 确定性路由规则，遵循**最具体优先**原则

**匹配顺序**:
1. `peer` (精确 DM/群组 ID)
2. `parentPeer` (线程继承)
3. `guildId + roles` (Discord 角色)
4. `guildId` (Discord 服务器)
5. `teamId` (Slack 团队)
6. `accountId`
7. 渠道级匹配 (`accountId: "*"`)
8. 回退到默认智能体

**配置示例**:
```json5
{
  agents: {
    list: [
      { id: "personal", workspace: "~/.openclaw/workspace-personal" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
      { id: "research", workspace: "~/.openclaw/workspace-research" }
    ]
  },
  bindings: [
    {
      agentId: "research",
      match: {
        channel: "telegram",
        accountId: "work"
      }
    },
    {
      agentId: "personal",
      match: {
        channel: "whatsapp",
        accountId: "*"  // 所有 WhatsApp 使用 personal
      }
    }
  ]
}
```

**多账户模式**:
- 每个 `accountId` 可路由到不同 Agent
- 使用 `accountId` 标识每个登录
- 支持 `accountId: "*"` 作为渠道级回退

---

### 16. 工具配置文件 (Tools Profile)

**内置配置**:
1. **messaging**: 仅消息工具（默认）
2. **coding**: 添加代码工具
3. **web**: 添加网络工具
4. **minimal**: 最小工具集（安全）
5. **custom**: 自定义配置

**自定义配置**:
```json5
{
  tools: {
    profile: "minimal",
    deny: [
      "group:automation",
      "group:runtime",
      "group:fs"
    ],
    fs: {
      workspaceOnly: true
    },
    exec: {
      security: "deny",
      ask: "always"
    },
    elevated: {
      enabled: false
    }
  }
}
```

**安全配置文件**:
```json5
{
  tools: {
    deny: [
      "gateway",           // 防止配置更改
      "cron",              // 防止计划任务
      "sessions_spawn",    // 防止启动新会话
      "sessions_send"      // 防止跨会话发送
    ]
  }
}
```

---

### 17. 节点 (Nodes)

**角色**:
- 远程执行表面
- 与 Gateway 配对
- 提供设备访问（摄像头、屏幕、通知等）

**安全控制**:
1. **配对**: 需要批准
2. **执行批准**: 安全 + 询问 + 白名单
3. **命令限制**: `gateway.nodes.denyCommands`

**安全等级**:
- `deny`: 拒绝所有远程执行
- `ask`: 每次执行前询问
- `allowlist`: 仅允许白名单命令
- `allow`: 允许所有命令（不安全！）

**命令列表**:
```json5
{
  gateway: {
    nodes: {
      allowCommands: ["system.run", "camera.snap"],  // 允许这些
      denyCommands: ["camera.clip", "notifications.list"]  // 拒绝这些
    }
  }
}
```

---

### 18. Gateway 网络配置

**绑定模式**:
1. `loopback`: 仅本地访问（默认，最安全）
2. `lan`: 局域网访问
3. `tailnet`: Tailscale 网络
4. `custom`: 自定义地址

**推荐配置**:
```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",  // 或 "tailnet"（通过 Tailscale Serve）
    auth: {
      mode: "token",
      token: "生成一个长随机令牌"
    },
    port: 18789
  }
}
```

**Tailscale Serve**:
- 自动认证
- Tailscale 处理访问控制
- Gateway 保持 `loopback` 绑定
- 最安全的远程访问方案

**反向代理**:
```yaml
gateway:
  trustedProxies:
    - "127.0.0.1"
  allowRealIpFallback: false
  auth:
    mode: password
    password: ${OPENCLAW_GATEWAY_PASSWORD}
```

---

### 19. 安全审计检查项

**高优先级（critical）**:
1. `fs.state_dir.perms_world_writable` - 其他用户可修改状态
2. `gateway.bind_no_auth` - 远程绑定无认证
3. `gateway.tailscale_funnel` - 公网暴露
4. `security.exposure.open_groups_with_elevated` - 开放群组 + 高级工具
5. `sandbox.dangerous_network_mode` - 沙箱网络使用 host 模式

**警告级（warn）**:
1. `gateway.http.no_auth` - Gateway HTTP 无认证
2. `gateway.nodes.allow_commands_dangerous` - 允许高影响节点命令
3. `models.small_params` - 小模型 + 不安全工具
4. `skills.workspace.symlink_escape` - 工作区技能目录存在符号链接逃脱

**修复命令**:
```bash
# 快速修复
openclaw security audit --fix

# 深度检查
openclaw security audit --deep

# JSON 格式输出
openclaw security audit --json
```

---

### 20. 最佳实践总结

**部署安全**:
- ✅ 绑定到 `loopback` 或使用 Tailscale Serve
- ✅ 始终启用认证（token 或密码）
- ✅ 限制 DM 策略为 `pairing` 或 `allowlist`
- ✅ 使用 `dmScope: "per-channel-peer"`
- ✅ 禁用不必要的工具
- ✅ 定期运行 `openclaw security audit`

**多用户场景**:
- ✅ 为每个信任边界运行独立网关
- ✅ 启用严格 DM 隔离
- ✅ 限制工具权限
- ✅ 使用沙箱模式
- ✅ 使用强模型

**公开机器人**:
- ✅ 使用专用机器/VM/容器
- ✅ 限制工具访问（只读或禁用）
- ✅ 启用沙箱
- ✅ 使用强模型（防提示注入）
- ✅ 使用 read-only 智能体处理不可信内容

**技能管理**:
- ✅ 将第三方技能视为不可信代码
- ✅ 启用技能监听器自动刷新
- ✅ 定期更新技能
- ✅ 阅读技能内容后再启用

**会话维护**:
- ✅ 定期清理过期会话
- ✅ 监控上下文窗口使用
- ✅ 在必要时手动压缩
- ✅ 保持记忆文件更新

---

## 🎯 学习要点总结

**核心架构理解**:
1. Gateway 是单一控制平面，管理所有渠道
2. Agent 是独立的"大脑"，拥有独立工作空间和记忆
3. Session 是聊天历史的存储和管理
4. Skill 是工具能力的定义和扩展
5. Plugin 是功能扩展的模块

**关键安全概念**:
1. 信任边界模型：一个受信任的操作者
2. 最小权限原则：只给工具所需的最小权限
3. 沙箱隔离：运行不可信代码
4. 认证机制：所有连接必须认证
5. 工具限制：限制危险工具使用

**实践要点**:
1. 定期安全审计
2. 保持技能更新
3. 监控会话状态
4. 使用强模型
5. 遵循最佳实践

---

*补充学习完成时间：2026-03-12*
