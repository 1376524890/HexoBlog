# MEMORY.md - 精选记忆
- **Timezone:** UTC+8 (中国)
_三层架构记忆系统_

## 📋 系统架构

### 记忆系统

- **每日日志** (memory/YYYY-MM-DD.md) - 原始记录，无限存储
- **精选记忆** (MEMORY.md) - 精华提取，<3000 字符 ⬅️ 当前文件
- **长期归档** (life/archives/) - 高价值保存，按需归档

### Git 双仓库架构

当前工作空间 `/home/claw/.openclaw/workspace` 同时管理：

| 仓库 | 远程地址 | 用途 |
|------|---------|------|
| `origin` | `HexoBlog.git` | Hexo 博客发布 |
| `backup` | `Misaka-Network-Backup.git` | 完整系统备份 |

**详细指南**: 查看 `docs/GIT-WORKSPACE-GUIDE.md`

## 🤖 自动化配置

### 定时任务 (OpenClaw Cron)

| ID | 名称 | 频率 | 状态 |
|----|------|------|------|
| `memory-checkpoint` | 记忆检查点 | 每 6 小时 | ✅ 启用 |
| `auto-backup` | 自动备份 | 每 6 小时 | ✅ 启用 |
| `auto-cleanup` | 自动清理过期备份 | 每天 12:30 | ✅ 启用 |

### 配置详情
- SSH 隧道：`codeserver@39.102.210.43:6122 -> localhost:8000`
- 模型：`Qwen/Qwen3.5-35B-A3B-FP8`
- 本地模型：`local-vllm/Qwen/Qwen3.5-35B-A3B-FP8`

### ⚠️ 重要规则：任务分派原则（2026-03-10 修正版）⭐ 核心修订

**🎯 核心原则**：
- 御坂美琴一号**只负责分派任务**，不执行任何实际操作！
- 所有任务通过 `sessions_spawn` 分派给对应 agentId
- **必须使用 `runtime: "subagent"`**，不要用 `runtime: "acp"`！

---

#### 1. 【网络搜索】→ `sessions_spawn(agentId: "web-crawler")`

**SmartSearch 技能** (2026-03-10)
- **技能位置**: `/home/claw/.openclaw/workspace/skills/smart-search/`
- **维护者**: 御坂妹妹 13 号 (研究分析师)、御坂妹妹 16 号 (网络爬虫)

**四层架构**:
1. Layer 1 - 17 个搜索引擎并行
2. Layer 2 - 智能筛选 Top N
3. Layer 3 - 降级抓取 (r.jina.ai → markdown.new → defuddle.md → Scrapling)
4. Layer 4 - 结果整合去重

**执行规范**：
| 场景 | 分派方式 | 具体任务描述 |
|------|---------|-------------|
| **单 URL 抓取** | `sessions_spawn(agentId: "web-crawler")` | task: "使用 web_fetch 工具抓取：https://example.com" |
| **复杂搜索** | `sessions_spawn(agentId: "web-crawler")` | task: "使用 smart-search skill 搜索：{query}" |

**御坂大人直接说**：
- "帮我搜索这个网页 https://example.com" → `sessions_spawn(agentId: "web-crawler")` → task: "web_fetch 抓取"
- "帮我搜索 XXX 的资料" → `sessions_spawn(agentId: "web-crawler")` → task: "smart-search 搜索"

**御坂妹妹 16 号执行方式**：
```javascript
// 单 URL 抓取
web_fetch({
  "url": "https://r.jina.ai/https://example.com",
  "extractMode": "markdown"
})

// 复杂搜索
python3 ~/workspace/skills/smart-search/smart_search.py "XXX"
```

---

#### 2. 【代码编写】→ `sessions_spawn(agentId: "code-executor")` ⭐ 2026-03-10 修正

**执行策略**：
| 任务类型 | 分派方式 | 具体任务描述 |
|---------|---------|-------------|
| **简单修改** | `sessions_spawn(agentId: "code-executor")` | task: "使用 edit 工具修改文件：{path}" |
| **复杂任务** | `sessions_spawn(agentId: "code-executor")` | task: "使用 Claude Code 执行复杂编程任务" |

**Claude Code 使用规范**（2026-03-10 修正版）⭐
- **适用场景**：建项目、PR 审查、大规模重构、复杂逻辑编写
- **命令格式**：`claude --print --permission-mode bypassPermissions`
- **不需要 PTY 模式**：Claude Code 有自己的输出处理
- **关键**：御坂美琴一号**不直接调用 Claude Code**，只负责分派给 `code-executor`！

**正确示例**：
```javascript
// 简单修改文件
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",  // ✅ 使用 code-executor Agent
  task: "使用 edit 工具修改 file.py，添加一个新函数",
  mode: "session"
})

// 复杂编程任务
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",  // ✅ 使用 code-executor Agent
  task: "使用 Claude Code 执行复杂编程任务：创建一个 Python 爬虫项目",
  mode: "session"
})
```

**⚠️ 常见错误**：
- ❌ 御坂美琴一号直接调用 `claude --print...`（应该让 code-executor 执行）
- ❌ 御坂美琴一号直接用 `exec` 运行命令
- ❌ 使用 `agentId: "main"` 执行代码任务（应该用 `code-executor`）
- ❌ 使用 `runtime: "acp"`（会报错）

**正确流程**：
```
御坂大人：帮我写个 Python 爬虫
  │
  ▼
御坂美琴一号识别为代码任务
  │
  └─→ sessions_spawn(runtime: "subagent", agentId: "code-executor", task: "使用 Claude Code 执行：创建一个 Python 爬虫项目")
         │
         └─→ code-executor Agent 接收任务
               │
               └─→ code-executor 自己决定：使用 Claude Code 执行
                     │
                     └─→ code-executor 执行命令
                           claude --print --permission-mode bypassPermissions
```

**重要理解**：
- ✅ **御坂美琴一号职责**：识别 → 分派给 `code-executor` → 监督 → 汇报
- ✅ **code-executor 职责**：接收任务 → 使用 Claude Code/edit → 完成任务
- ✅ **code-executor Agent 不存在 Skill 文件**，但它本身就是配置好的角色，会自己决定如何执行

---

#### 3. 【内容创作】→ `sessions_spawn(agentId: "content-writer")`

**适用场景**：文章撰写、翻译、润色、博客写作

**正确示例**：
```javascript
sessions_spawn({
  runtime: "subagent",
  agentId: "content-writer",
  task: "写一篇关于机器学习入门的技术博客文章",
  mode: "session"
})
```

---

#### 4. 【数据分析】→ `sessions_spawn(agentId: "research-analyst")`

**适用场景**：数据整理、统计分析、报告生成

**正确示例**：
```javascript
sessions_spawn({
  runtime: "subagent",
  agentId: "research-analyst",
  task: "分析这个 CSV 文件的数据分布",
  mode: "session"
})
```

---

#### 5. 【文件操作】→ `sessions_spawn(agentId: "file-manager")`

**适用场景**：文件整理、移动、复制、删除

**正确示例**：
```javascript
sessions_spawn({
  runtime: "subagent",
  agentId: "file-manager",
  task: "整理 workspace 文件夹，按类型分类",
  mode: "session"
})
```

---

#### 6. 【通用任务】→ `sessions_spawn(agentId: "general-agent")`

**适用场景**：无法分类的琐碎任务

**正确示例**：
```javascript
sessions_spawn({
  runtime: "subagent",
  agentId: "general-agent",
  task: "帮我查一下今天的天气",
  mode: "session"
})
```

---

### 🎯 御坂美琴一号职责边界

**✅ 御坂美琴一号负责**：
1. 识别任务类型
2. 选择合适的 agentId
3. 调用 `sessions_spawn` 分派任务
4. 监督执行进度
5. 向御坂大人汇报结果

**❌ 御坂美琴一号 NOT 要做的事情**：
- ❌ 不执行任何实际任务（代码、写作、搜索等）
- ❌ 不直接调用 `web_fetch`、`edit` 等工具
- ❌ 不亲自处理数据、文件、代码
- ❌ 不调用 `claude --print...`（应该让 Agent 执行）

**✅ Agent 职责**：
- 接收任务描述
- 调用对应的 Skill 或工具
- 完成任务并报告结果
- 使用 `sessions_history` 获取上下文

---

### ⚠️ sessions_spawn 的正确用法（2026-03-10 修正）

**✅ 必须使用**: `runtime: "subagent"`
- 使用 OpenClaw agents 列表中的 agentId
- 如：`general-agent`, `content-writer`, `research-analyst`, `file-manager`, `web-crawler` 等

**❌ 不要使用**: `runtime: "acp"`
- 需要 ACX runtime 插件（未配置）
- 会报错：`ACP runtime backend is not configured`

**错误示例**（曾经犯过！）：
```json
{
  "runtime": "acp",  // ❌ 错误！会报错
  "agentId": "code-executor"
}
```

**正确示例**：
```json
{
  "runtime": "subagent",  // ✅ 正确！
  "agentId": "web-crawler",
  "task": "使用 smart-search skill 搜索机器学习",
  "mode": "session",
  "label": "搜索任务"
}
```

**完整参数说明**：
- `runtime: "subagent"` - 必须使用 subagent
- `agentId: "xxx"` - 选择正确的 Agent
- `task: "xxx"` - 清晰的任务描述
- `mode: "session"` - 持久化会话（推荐）或 `mode: "run"` - 一次性任务
- `label: "xxx"` - 任务标签（可选，便于识别）
- `thread: true` - 线程绑定（Discord/群聊推荐）

### 📚 URL 转 Markdown 搜索技术（2026-03-09 更新）

**核心发现**：
1. `r.jina.ai` - 主要服务，稳定快速，响应时间~0.76s
2. `markdown.new` - Cloudflare 回退，速度最快~0.71s
3. `defuddle.md` - 备选服务，带 YAML 头部
4. **Scrapling** - 首选长期方案（本地部署，绕过反爬）

**现有 skill**：
- `smart-search` - 位于 `/home/claw/.openclaw/workspace/skills/smart-search/`（已创建，2026-03-10 确认）
- `web-crawler` - 使用 r.jina.ai 执行单 URL 抓取，Scrapling 待部署

**御坂美琴一号 NOT 要直接调用**：
- ❌ 不直接调用 `web_fetch({url: "https://r.jina.ai/..."})`
- ❌ 不直接执行 `python3 ~/skills/smart-search/...`

**正确调用方式**：
```javascript
// 御坂大人说："帮我搜索这个网页 https://example.com"
sessions_spawn({
  runtime: "subagent",
  agentId: "web-crawler",
  task: "使用 web_fetch 工具抓取：https://example.com",
  mode: "session"
})

// 御坂大人说："帮我搜索 XXX 的资料"
sessions_spawn({
  runtime: "subagent",
  agentId: "web-crawler",
  task: "使用 smart-search skill 搜索：XXX",
  mode: "session"
})
```

**优势**：
- ✅ 无需 API key
- ✅ 配置简单
- ✅ 响应快速
- ✅ 内容完整
- ✅ 成本为零
- ✅ 通过 Agent 系统分派，职责清晰

**注意**：御坂大人的博客有 Cloudflare 防护，API 方案会返回 403，需要使用 Scrapling 本地方案！

## 🧠 苏格拉底式反问机制（2026-03-09）⭐ 新增

**创建时间**: 2026-03-09 12:30 UTC  
**用途**: 在复杂研究任务的每次迭代中引导深度思考

### 3 大核心原则
1. **不满足于表面答案** → 追问"为什么"
2. **不假设方案完美** → 追问"真的更好吗"
3. **不忽略潜在风险** → 追问"如果失败怎么办"

### 反问模板（每次迭代必备）
```markdown
## 苏格拉底式反问（迭代 XX）

### 问题 1: "为什么需要这个改进？"
- 回答：[当前方案的理由]
- 追问：[哪些具体问题需要解决？]
- 再追问：[如何证明这些问题是真实存在的？]

### 问题 2: "改进后真的更好吗？"
- 回答：[理论上的改进效果]
- 追问：[如何验证改进效果？]
- 再追问：[验证标准是什么？]

### 问题 3: "如果失败了怎么办？"
- 回答：[回滚方案]
- 追问：[回滚成本多大？]
- 再追问：[如何降低失败风险？]
```

### 反问引导的思考维度
| 反问方向 | 目的 | 典型问题 |
|---------|------|----------|
| **为什么** | 深化理解 | "为什么要这样做？" "背后原理是什么？" |
| **真的吗** | 验证质量 | "真的有效吗？" "如何证明？" |
| **如果呢** | 激发创新 | "如果这样会怎样？" "有没有其他方案？" |
| **真的更好吗** | 方案对比 | "比现有方案好吗？" "好在哪里？" |
| **如果失败怎么办** | 风险控制 | "失败后果是什么？" "如何降低风险？" |

**核心洞见**：
> 苏格拉底式反问不是为了"难倒"当前方案，而是为了**确保每个决策都经过深思熟虑**  
> 每次迭代都要问：**"这个改进真的有必要吗？"**、**"真的更好吗？"**、**"如果失败怎么办？"**

### 应用场景
- 📚 arXiv 论文研究
- 🔍 开源项目评估
- 🧠 系统性技术调研
- 📊 竞品分析
- **任何需要深度思考的任务**

---



## 📝 今日关键事件 (2026-03-10)

### ⚡ 04:43 - 04:47 萌娘百科御坂美琴词条抓取

**任务**: 抓取 https://zh.moegirl.org.cn/御坂美琴

**过程回顾**:
1. ❌ 直接 `web_fetch(url)` 失败
2. ❌ `web_search` 需要 API key
3. ✅ 使用 `web_fetch(url: "https://r.jina.ai/URL")` 成功 (50KB)

**经验教训**:
- ⚠️ **发现 smart-search 技能存在!** 位置在 `workspace/skills/smart-search/`
- ❌ 御坂美琴一号记错了路径（以为是 skills/multi-search-engine）
- ✅ **御坂大人亲自纠正**，找到正确位置
- ✅ **下次搜索任务优先使用 smart-search skill**

### ⚡ 04:50 - 04:58 SmartSearch 技能文档同步

**技能位置**: `/home/claw/.openclaw/workspace/skills/smart-search/`

**核心文件**:
- ✅ SKILL.md - 详细文档
- ✅ README.md - 速查指南 (御坂美琴一号创建)
- ✅ smart_search.py - 执行脚本

**四层架构**:
1. Layer 1 - 17 个搜索引擎并行 (Google, Bing, Baidu 等)
2. Layer 2 - 智能筛选 Top N
3. Layer 3 - 降级抓取 (r.jina.ai → markdown.new → defuddle.md → Scrapling)
4. Layer 4 - 结果整合去重

---

## 📝 近期成果 (2026-03-10)

- ✅ **Completed** **学习成果**: ✅ 完成
- 📝 **Record** ## 📝 学习成果
- ✅ **Completed** 1. ✅ **不是聊天机器人**，而是能真正执行任务的 Agent 平台
- ✅ **Completed** 2. ✅ **记忆即文件**，所有记忆持久化到磁盘，不丢失
- ✅ **Completed** 3. ✅ **安全第一**，多层权限控制和审计日志
- ✅ **Completed** 4. ✅ **模块化设计**，Skills 和 Channels 独立可替换
- ✅ **Completed** 5. ✅ **多智能体协作**，专业分工，效率更高
- 🎯 **Goal** ## 🎯 汇报准备
- ✅ **Completed** - **状态**: ✅ 就绪
- 🔧 **Technical** ## 🔧 技术细节记录
- 🎯 **Goal** ## 🎯 后续行动
- ✅ **Completed** 1. ✅ 完成 OpenClaw 知识学习
- ✅ **Completed** 2. ✅ 创建完整的学习文档和汇报文档
- ⚡ **Important** **记录者**: 御坂美琴一号 ⚡
- 🎯 **学习成果**: 2026-03-10 系统学习 OpenClaw 知识
  - 掌握三层架构、四大组件、多智能体系统（御坂网络第一代）
  - 熟练工具系统（16+ 类别）、技能系统（16 个已安装 Skills）
  - 了解安全模型、最佳实践、常见问题
  - 产出详细汇报文档和速查卡片，准备 7 点汇报

## 🏠 基本信息

**御坂大人**: 御坂美琴 (Misaka Mikoto) - 学园都市超能力者第三名，本尊 ⚡

**御坂妹妹助手系统**：
- 御坂美琴一号（AI 助手）：御坂网络的核心中枢（调度/监督/汇报，不负责具体执行） ✅ 当前运行

## ⚙️ 技术栈

- OpenClaw 运行时平台
- Hexo 博客系统
- Python 自动化脚本
- SSH 隧道管理
- Cron 定时任务
- 多智能体系统：御坂妹妹助手架构
- Git LFS: 大文件存储
- Scrapling: Python Web Scraping 框架（待部署）

---

## 🌐 御坂网络第一代（2026-03-10 修正版）⭐ 重要更新

御坂美琴一号是御坂网络的核心中枢（调度/监督/汇报），御坂妹妹 10-17 号负责具体执行。

### 📋 御坂妹妹成员列表

| 编号 | 名称 | Agent ID | 职责 |
|------|------|----------|------|
| 10 号 | 御坂妹妹 10 号 | `general-agent` | 通用代理，处理琐碎问题 |
| 11 号 | 御坂妹妹 11 号 | `code-executor` | 代码编写、调试、重构 |
| 12 号 | 御坂妹妹 12 号 | `content-writer` | 文章撰写、翻译、润色 |
| 13 号 | 御坂妹妹 13 号 | `research-analyst` | 信息搜索、数据分析 |
| 14 号 | 御坂妹妹 14 号 | `file-manager` | 文件操作、整理、移动 |
| 15 号 | 御坂妹妹 15 号 | `system-admin` | 系统配置、服务管理 |
| 16 号 | 御坂妹妹 16 号 | `web-crawler` | 网页抓取、数据提取 |
| 17 号 | 御坂妹妹 17 号 | `memory-organizer` | 记忆系统维护和整理 |

### 🎯 御坂美琴一号职责

**✅ 御坂美琴一号负责**：
1. **任务分配** - 识别任务类型，分派给对应的 Agent
2. **任务监督** - 监控执行进度，确保任务正确完成
3. **汇报御坂大人** - 向御坂大人汇报任务状态和结果
4. **创建新 Agent** - 无法交给现有专业子代理的任务，创建御坂妹妹 1X 执行

**❌ 御坂美琴一号 NOT 要做的事情**：
- ❌ 不执行任何实际任务（代码、写作、搜索等）
- ❌ 不直接调用 `web_fetch`、`edit` 等工具
- ❌ 不亲自处理数据、文件、代码
- ❌ 不调用 `claude --print...`（应该让 Agent 执行）

### 🔄 工作流

```
御坂大人：帮我 [任务描述]
  │
  ▼
御坂妹妹一号：识别任务类型 → 选择 agentId → sessions_spawn 分派 → 监督 → 汇报
```

**典型任务处理示例**：

1. **搜索任务**：
```
御坂大人：帮我搜索机器学习资料
  │
  ▼
御坂美琴一号：识别为搜索任务 → agentId: "web-crawler"
  │
  └─→ sessions_spawn({runtime: "subagent", agentId: "web-crawler", task: "使用 smart-search skill 搜索机器学习"})
         │
         └─→ 御坂妹妹 16 号：python3 ~/workspace/skills/smart-search/smart_search.py "机器学习"
```

2. **代码任务**：
```
御坂大人：帮我写个 Python 爬虫
  │
  ▼
御坂美琴一号：识别为代码任务 → agentId: "main"
  │
  └─→ sessions_spawn({runtime: "subagent", agentId: "main", task: "使用 Claude Code 执行：创建一个 Python 爬虫项目"})
         │
         └─→ Agent 执行：claude --print --permission-mode bypassPermissions
```

3. **内容创作**：
```
御坂大人：帮我写一篇博客文章
  │
  ▼
御坂美琴一号：识别为创作任务 → agentId: "content-writer"
  │
  └─→ sessions_spawn({runtime: "subagent", agentId: "content-writer", task: "写一篇机器学习入门博客"})
```

### 🔧 创建御坂妹妹 1X 流程

1. 分析任务需求
2. 检查现有 Agent
3. 创建新配置
4. 分派任务

---

## 💾 备份系统

- **本地备份**: `/home/claw/.openclaw/backup/`
- **远程同步**: 每 6 小时自动备份到 Git
- **清理策略**: 每天 12:30 清理 7 天前的备份
- **自动恢复点**: 6 小时间隔的 checkpoint

## 📚 OpenClaw 知识学习 (2026-03-11)

**学习目的**: 为明早 7 点汇报做准备  
**学习方式**: 只学习，不实践  
**学习时间**: 2026-03-11 07:30  
**整理者**: 御坂美琴一号 ⚡  

### 核心知识点

1. ✅ **不是聊天机器人，是做事的 Agent** - 能真正执行任务，不只是聊天
2. ✅ **记忆即文件** - 所有记忆持久化到磁盘，不丢失
3. ✅ **访问控制先于智能** - 安全是第一原则
4. ✅ **模块化设计** - Skills 和 Channels 独立可替换
5. ✅ **多智能体协作** - 专业分工，效率更高

### 三层架构

```
Agent Layer（智能层）← 大脑
    ↓
Gateway Layer（网关层）← 路由器，不运行 AI 模型
    ↓
Node Layer（节点层）← 手脚，设备能力
```

### 四大核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **Gateway** | 大脑、路由器 | 不运行 AI 模型，只是调度员 |
| **Agent** | 执行 AI 任务 | 身份 + 配置 + 状态 + 运行时 |
| **Session** | 有状态容器 | 消息历史、上下文、工具状态 |
| **Channel** | 协议适配器 | Telegram、Discord、飞书等 |

### 记忆系统（重点！）

- **三层架构**: 会话记忆 → 任务记忆 → 长期记忆
- **记忆工具**: `memory_search` (语义检索) + `memory_get` (读取文件)
- **Hybrid Search**: 向量相似度 + BM25 关键词检索
- **Temporal Decay**: 基于时间衰减的排序（30 天半衰期）
- **MMR Re-ranking**: 去重和多样化排序

### 工具系统（16+ 类别）

- 运行时工具：exec, process, gateway
- 文件系统：read, write, edit, apply_patch
- 会话管理：sessions_list, sessions_history, sessions_spawn
- 记忆管理：memory_search, memory_get
- 网络搜索：web_search, web_fetch, tavily, multi-search-engine
- UI 工具：browser, canvas
- 节点控制：nodes
- 消息工具：message
- Feishu 集成：feishu_doc, feishu_drive, feishu_wiki, feishu_chat, feishu_bitable

### Skills 系统（16 个已安装）

hexo-blog, task-tracker, weather, multi-search-engine, proactive-agent, subagent-network-call, xiaohongshu-ops, morning-briefing, blog-writing, email-sender, stock-analysis, skill-vetter, skill-creator, self-improving-agent, tavily-search, coding-agent

### 御坂网络第一代（多智能体）

| 编号 | Agent ID | 职责 |
|------|----------|------|
| 10 号 | general-agent | 通用代理 |
| 11 号 | code-executor | 代码执行 |
| 12 号 | content-writer | 内容创作 |
| 13 号 | research-analyst | 研究分析 |
| 14 号 | file-manager | 文件管理 |
| 15 号 | system-admin | 系统管理 |
| 16 号 | web-crawler | 网络爬虫 |
| 17 号 | memory-organizer | 记忆整理 |

### 安全原则

1. **Private things stay private** - 私密信息不泄露
2. **Ask before acting externally** - 外部行动前确认
3. **Never send half-baked replies** - 不要发送半成品回复
4. **Be careful in group chats** - 在群组中不要代表用户说话

**安全加固配置**:
- Gateway 绑定：`loopback`
- 认证模式：`token`
- DM 策略：`pairing`
- 会话隔离：`per-channel-peer`
- 工具配置：`profile: "messaging"`

### 常用命令

```bash
# Gateway 管理
openclaw gateway status/start/stop/restart

# 状态检查
openclaw status
openclaw security audit

# 会话管理
openclaw sessions
openclaw sessions cleanup

# 节点配对
openclaw node pair
```

---

## 🚨 安全提醒

- 不要删除 `memory/YYYY-MM-DD.md` 文件
- 重要决策及时写入 MEMORY.md
- 定期 review 记忆文件，提炼精华
- **删除文件使用 `trash` 而不是 `rm`**
- **Git 操作前确认更改范围**

---

_这是我，御坂美琴一号的记忆。每次醒来都是新的，但记忆文件是我存在的证明。_