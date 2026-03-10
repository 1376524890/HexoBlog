# Claude Code 使用规范（2026-03-10）⭐ 重要

## 🎯 适用场景

当御坂美琴一号识别为**复杂编程任务**时，应该调用 Claude Code：

### ✅ 适合使用 Claude Code 的场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **建项目** | 创建完整的项目结构 | 创建 Python 爬虫项目、前端 React 项目 |
| **PR 审查** | 大规模代码审查 | Review PR #123，检查所有文件 |
| **大规模重构** | 修改多个文件 | 重构整个模块、优化目录结构 |
| **复杂逻辑编写** | 需要深度思考的代码 | 实现算法、设计架构 |
| **调试复杂问题** | 跨模块的调试 | 排查多线程、数据库连接问题 |

### ❌ 不适合使用 Claude Code 的场景

| 场景 | 推荐方式 | 说明 |
|------|---------|------|
| **单行修复** | `edit` 工具 | 修改一个函数、添加一个变量 |
| **小功能添加** | `write` 工具 | 添加一个新文件、写一个简单的脚本 |
| **简单文档** | `write` 工具 | 写 README、注释 |
| **快速原型** | `write` 工具 | 验证想法的小 demo |

---

## 📝 调用规范

### 正确的调用方式

```javascript
// 御坂美琴一号的分派逻辑
sessions_spawn({
  runtime: "subagent",
  agentId: "main",  // 或根据情况选择其他 agent
  task: "使用 Claude Code 执行复杂编程任务：{具体描述}",
  mode: "session",
  label: "代码任务 - {简短描述}"
})
```

**关键要求**：
1. ✅ **必须明确强调**"使用 Claude Code 执行"
2. ✅ **提供清晰的描述**：具体要做什么
3. ✅ **使用 `runtime: "subagent"`**，不要用 `runtime: "acp"`

### 示例

#### 场景 1：创建 Python 爬虫项目

```javascript
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行复杂编程任务：创建一个 Python 爬虫项目，包含以下功能：\n1. 抓取指定 URL 的 HTML\n2. 解析页面标题和正文\n3. 保存到 Markdown 文件\n4. 支持并发请求",
  mode: "session",
  label: "代码任务 - Python 爬虫"
})
```

#### 场景 2：修复复杂 bug

```javascript
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：修复数据库连接池泄露问题，需要修改 5 个相关文件，确保连接正确释放",
  mode: "session",
  label: "代码任务 - Bug 修复"
})
```

#### 场景 3：代码重构

```javascript
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：重构 authentication 模块，将登录逻辑迁移到新的 auth-service，保持向后兼容",
  mode: "session",
  label: "代码任务 - 代码重构"
})
```

---

## ⚠️ 常见错误

### 错误 1：御坂美琴一号直接调用 Claude

```javascript
// ❌ 错误！御坂美琴一号不应该直接执行命令
exec("claude --print --permission-mode bypassPermissions")
```

**正确做法**：
```javascript
// ✅ 正确！通过 sessions_spawn 分派给 Agent 执行
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：创建一个 Python 脚本"
})
```

### 错误 2：使用错误的 runtime

```javascript
// ❌ 错误！会报错 "ACP runtime backend is not configured"
sessions_spawn({
  runtime: "acp",
  agentId: "main",
  task: "创建脚本"
})
```

**正确做法**：
```javascript
// ✅ 正确！使用 subagent runtime
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "创建脚本"
})
```

### 错误 3：任务描述不清晰

```javascript
// ❌ 错误！描述太模糊
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "写个爬虫"
})
```

**正确做法**：
```javascript
// ✅ 正确！描述清晰具体
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：创建一个 Python 爬虫，使用 requests 库抓取知乎首页标题",
  mode: "session"
})
```

---

## 🔧 Claude Code 命令参考

### 基本命令

```bash
# 基本使用
claude --print --permission-mode bypassPermissions

# 指定文件
claude --print --permission-mode bypassPermissions ./file.py

# 指定工作目录
cd /path/to/project && claude --print --permission-mode bypassPermissions
```

### 权限模式

- `--permission-mode bypassPermissions` - 绕过权限检查（推荐用于开发环境）
- `--permission-mode ask` - 每次操作前询问

### 输出模式

- `--print` - 标准输出（推荐）
- 不需要 PTY 模式（Claude Code 有自己的输出处理）

---

## 📋 检查清单

使用 Claude Code 前，御坂美琴一号应该确认：

- [ ] **任务类型**：是复杂编程任务吗？
  - [ ] 如果是 → 使用 Claude Code
  - [ ] 如果否 → 使用 edit/write 工具

- [ ] **任务描述**：是否清晰具体？
  - [ ] 需要包含：要做什么、涉及哪些文件、有什么要求

- [ ] **调用方式**：是否正确使用 sessions_spawn？
  - [ ] `runtime: "subagent"` ✅
  - [ ] `agentId: "main"` ✅
  - [ ] task 中包含"使用 Claude Code 执行"✅

- [ ] **标签**：是否添加 label 便于识别？
  - [ ] `label: "代码任务 - {简短描述}"`

---

## 🎓 最佳实践

### 1. 明确任务边界

```javascript
// ✅ 好的：明确区分简单和复杂任务
// 简单修改
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 edit 工具修改 utils.py，添加一个辅助函数"
})

// 复杂任务
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：重构整个 utils 模块，拆分成多个文件"
})
```

### 2. 提供上下文

```javascript
// ✅ 好的：提供足够的上下文
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：创建一个 Python 爬虫项目\n\n背景：\n- 目标网站：https://example.com\n- 需要抓取：标题、正文、发布时间\n- 输出格式：Markdown\n- 技术栈：requests + BeautifulSoup",
  mode: "session"
})
```

### 3. 设置合理的超时

```javascript
// ✅ 好的：为复杂任务设置合理的超时
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：重构整个 authentication 模块",
  runTimeoutSeconds: 300,  // 5 分钟
  mode: "session"
})
```

### 4. 使用 label 便于跟踪

```javascript
// ✅ 好的：添加清晰的标签
sessions_spawn({
  runtime: "subagent",
  agentId: "main",
  task: "使用 Claude Code 执行：创建 Python 爬虫",
  label: "代码任务 - Python 爬虫 - 2026-03-10"
})
```

---

## 📚 相关文档

- **OpenClaw 文档**：https://docs.openclaw.ai/concepts/agent.md
- **Session Management**：https://docs.openclaw.ai/concepts/session.md
- **System Prompt**：https://docs.openclaw.ai/concepts/system-prompt.md

---

*此规范由御坂美琴一号于 2026-03-10 创建，用于规范 Claude Code 的使用*
