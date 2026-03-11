# 任务分派检查表 - 御坂美琴一号专用

**创建时间**: 2026-03-11 12:10 UTC  
**用途**: 每次分派任务前检查，确保正确调用 Agent 和技能  
**维护者**: 御坂美琴一号

---

## 📋 任务分派前检查清单

### ✅ 第一步：识别任务类型

| 任务特征 | 正确 Agent ID | 对应妹妹 |
|---------|-------------|----------|
| 搜索资料、抓取网页、网络研究 | `web-crawler` | 16 号 |
| 写代码、调试、重构、构建项目 | `code-executor` | 11 号 |
| 写文章、翻译、润色、博客 | `content-writer` | 12 号 |
| 数据分析、统计、报告 | `research-analyst` | 13 号 |
| 文件整理、移动、复制 | `file-manager` | 14 号 |
| 系统配置、服务管理 | `system-admin` | 15 号 |
| 无法分类的琐碎任务 | `general-agent` | 10 号 |
| 记忆整理、备份、归档 | `memory-organizer` | 17 号 |

---

### ✅ 第二步：构建任务描述

#### ❌ 错误示范（必须避免）

```javascript
// 错误 1: 描述太模糊
task: "帮我搜索机器学习"
// 结果：Agent 会使用 web_search 或 web_fetch 直接调用

// 错误 2: 指定错误工具而不是技能
task: "使用 web_fetch 抓取这个网页"
// 结果：Agent 会直接用工具而不是技能

// 错误 3: 御坂美琴一号自己调用工具
web_fetch({url: "https://r.jina.ai/..."})
// 结果：应该让 Agent 去调用！
```

#### ✅ 正确示范

```javascript
// 正确 1: 指定技能名称
task: "使用 smart-search skill 搜索：机器学习入门资料"
// 结果：御坂妹妹 16 号会执行 python3 ~/skills/smart-search/smart_search.py

// 正确 2: 指定执行方式
task: "使用 Claude Code 执行：创建一个 Python 爬虫项目"
// 结果：御坂妹妹 11 号会运行 claude --print --permission-mode bypassPermissions
```

---

### ✅ 第三步：构建 sessions_spawn 调用

#### ✅ 标准格式（2026-03-10 修正版）

```javascript
sessions_spawn({
  runtime: "subagent",  // ⚠️ 必须用 subagent，不能用 acp！
  agentId: "web-crawler",  // 从 agents_list 中选择
  task: "使用 smart-search skill 搜索：XXX",  // 明确指定技能和具体任务
  mode: "session",  // 推荐用 session 模式（持久化）
  label: "搜索任务"  // 可选，便于识别
})
```

#### ❌ 常见错误

```javascript
// 错误 1: 用 acp runtime（会报错）
sessions_spawn({
  runtime: "acp",  // ❌ ACP runtime backend is not configured
  agentId: "web-crawler",
  task: "搜索 XXX"
})

// 错误 2: 没有指定任务细节
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",
  task: "写个代码"  // ❌ 太模糊！
})

// 错误 3: 御坂美琴一号自己调用工具
web_fetch({url: "https://r.jina.ai/..."})  // ❌ 应该让 Agent 去调用！
```

---

## 🛠️ 技能使用规范

### 1️⃣ SmartSearch（搜索技能）
- **位置**: `/home/claw/.openclaw/workspace/skills/smart-search/`
- **执行脚本**: `smart_search.py`
- **正确任务描述**: `task: "使用 smart-search skill 搜索：机器学习"`
- **Agent 执行命令**:
  ```bash
  python3 /home/claw/.openclaw/workspace/skills/smart-search/smart_search.py "机器学习"
  ```

### 2️⃣ web-markdown-search（单 URL 抓取）
- **位置**: `/home/claw/.openclaw/skills/web-markdown-search/`
- **使用工具**: `web_fetch({url: "https://r.jina.ai/URL"})`
- **正确任务描述**: `task: "使用 web-markdown-search skill 抓取：https://example.com"`

### 3️⃣ Coding-Agent（代码执行）
- **位置**: `/home/claw/.openclaw/extensions/feishu/node_modules/openclaw/skills/coding-agent/`
- **执行命令**: `claude --print --permission-mode bypassPermissions`
- **正确任务描述**: `task: "使用 coding-agent skill 创建 Python 爬虫项目"`
- **Agent 执行命令**:
  ```bash
  cd /path/to/project && claude --print --permission-mode bypassPermissions "创建 Python 爬虫项目"
  ```

### 4️⃣ Blog-Writing（博客写作）
- **位置**: `~/.openclaw/extensions/feishu/skills/blog-writing/`
- **用途**: Hexo 博客文章创作
- **正确任务描述**: `task: "使用 blog-writing skill 写一篇机器学习入门博客"`

### 5️⃣ Task-Tracker（任务追踪）
- **位置**: `/home/claw/.openclaw/skills/task-tracker/`
- **用途**: 复杂任务拆解和进度追踪
- **正确任务描述**: `task: "使用 task-tracker skill 拆解并追踪：XXX"`

---

## 🔄 分派后监督机制

### 御坂美琴一号每次分派任务时的自检：

- [ ] 是否选择了正确的 Agent ID？
- [ ] 任务描述是否明确指定了技能名称？
- [ ] 是否使用了 `runtime: "subagent"`？
- [ ] 任务描述是否清晰具体，不是模糊的"写个代码"？
- [ ] 是否避免了自己直接调用工具？

### 分派后的检查：

- [ ] 通过 `subagents list` 查看任务状态
- [ ] 通过 `sessions_history` 查看 Agent 是否使用了正确的工具
- [ ] 如果发现问题，立即干预并纠正

---

## 📊 历史问题记录

### 问题 1: web-crawler 使用老工具（2026-03-11 发现）
- **现象**: 16 号使用 `web_search` 和 `web_fetch` 直接调用，而不是 smart-search skill
- **原因**: 任务描述没有明确指定技能名称
- **解决**: 更新 MEMORY.md，创建检查表，任务描述必须写"使用 smart-search skill 搜索"

### 问题 2: code-executor 直接调用 exec（2026-03-11 发现）
- **现象**: 11 号直接运行 `exec(openclaw gateway restart)`，没有使用 Claude Code
- **原因**: 任务描述没有指定使用 coding-agent skill 和 Claude Code
- **解决**: 任务描述必须写"使用 coding-agent skill 执行 XXX"

---

## 📝 使用示例

### 示例 1: 网络搜索任务
```javascript
// 御坂大人说："帮我搜索机器学习资料"
sessions_spawn({
  runtime: "subagent",
  agentId: "web-crawler",
  task: "使用 smart-search skill 搜索：机器学习入门资料，深度 3",
  mode: "session",
  label: "机器学习搜索"
})
```

### 示例 2: 代码编写任务
```javascript
// 御坂大人说："帮我写个 Python 爬虫"
sessions_spawn({
  runtime: "subagent",
  agentId: "code-executor",
  task: "使用 coding-agent skill 和 Claude Code 创建一个 Python 爬虫项目",
  mode: "session",
  label: "Python 爬虫开发"
})
```

### 示例 3: 单 URL 抓取任务
```javascript
// 御坂大人说："帮我看看这个网页"
sessions_spawn({
  runtime: "subagent",
  agentId: "web-crawler",
  task: "使用 web-markdown-search skill 抓取：https://example.com",
  mode: "session",
  label: "网页抓取"
})
```

### 示例 4: 博客写作任务
```javascript
// 御坂大人说："帮我写一篇博客文章"
sessions_spawn({
  runtime: "subagent",
  agentId: "content-writer",
  task: "使用 blog-writing skill 写一篇关于机器学习入门的 Hexo 博客文章",
  mode: "session",
  label: "博客写作"
})
```

---

## 📋 待完善的 Skill 清单

### ✅ 已正确配置的技能

| 技能名称 | Agent ID | 位置 | 状态 |
|---------|----------|------|------|
| smart-search | web-crawler | `workspace/skills/smart-search/` | ✅ 已配置 |
| web-markdown-search | web-crawler | `~/.openclaw/skills/web-markdown-search/` | ✅ 已配置 |
| coding-agent | code-executor | `extensions/feishu/node_modules/openclaw/skills/coding-agent/` | ✅ 已配置 |
| blog-writing | content-writer | `extensions/feishu/skills/blog-writing/` | ✅ 已配置 |
| task-tracker | 通用 | `~/.openclaw/skills/task-tracker/` | ✅ 已配置 |
| hexo-blog | content-writer | `~/.openclaw/skills/hexo-blog/` | ✅ 已配置 |

### ⚠️ 缺少 SKILL.md 文档的技能（待创建）

| 技能名称 | 预期 Agent ID | 位置 | 优先级 |
|---------|-------------|------|--------|
| code-executor | code-executor | `workspace/skills/code-executor/` | 🔥 高 |
| complex-research-skill | research-analyst | `workspace/skills/complex-research-skill/` | ⭐ 中 |
| memory-organizer | memory-organizer | `workspace/skills/memory-organizer/` | 🔥 高 |
| security-audit | system-admin | `workspace/skills/security-audit/` | ⭐ 中 |
| public | 通用 | `workspace/skills/public/` | 💡 低 |

**下一步行动**：
- 为每个自定义技能创建 SKILL.md 文档
- 明确描述任务类型、使用方法、执行方式
- 更新到 TASK-DISPATCH-CHECKLIST.md 的"技能使用规范"章节

---

## ⚠️ 重要提醒

1. **永远不要自己调用工具** - 御坂美琴一号只负责分派，不执行具体操作
2. **永远不要使用 acp runtime** - 只使用 `runtime: "subagent"`
3. **任务描述必须具体** - 明确指定技能名称和执行方式
4. **分派后必须检查** - 通过 `sessions_history` 确认 Agent 使用了正确的工具
5. **为自定义技能创建 SKILL.md** - 确保每个技能都有清晰的文档

---

**创建者**: 御坂美琴一号  
**审核者**: 御坂美琴本尊  
**状态**: ✅ 已生效  
**下次更新**: 发现问题时立即更新
