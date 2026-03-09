# 代码编写任务分配指南

_御坂网络第一代编码 Agent 使用规范_

---

## 🎯 任务分配原则

**核心原则**：简单任务本地执行，复杂任务交给 Claude Code

### ✅ 使用本地 Qwen3.5 (御坂妹妹 11 号) 的情况

| 任务类型 | 说明 | 示例 |
|---------|------|------|
| 小型脚本 | <100 行的简单脚本 | Python 脚本处理 CSV |
| 单文件修改 | 修改单个文件的简单功能 | 添加日志记录 |
| 简单调试 | 明显的语法错误 | 缺少冒号、括号不匹配 |
| 代码解释 | 解释现有代码的功能 | 说明函数逻辑 |
| 单元测试 | 单文件的简单测试 | 测试一个函数 |
| 文档编写 | API 文档、注释 | 添加 docstring |

### ❌ 转交 Claude Code 的情况

| 任务类型 | 说明 | 示例 |
|---------|------|------|
| **大型项目** | 需要创建多个文件的项目 | 完整的前端应用、微服务 |
| **复杂架构** | 需要设计多模块协作系统 | 插件系统、状态管理 |
| **IDE/调试器集成** | 需要 IDE 辅助的复杂任务 | 调试复杂 bug、代码重构 |
| **多语言项目** | 涉及多种编程语言 | Python + TypeScript + SQL |
| **依赖管理** | 需要复杂依赖配置的项目 | package.json, requirements.txt |
| **Git 操作** | 需要 Git 工作流的项目 | 分支管理、PR 审查 |
| **文件探索** | 需要浏览整个代码库 | 理解现有架构、找依赖关系 |
| **迭代开发** | 需要多轮修改和测试的任务 | 功能开发、Bug 修复 |

---

## 🔧 Claude Code 使用方法

### 基本命令格式

```bash
# 前台执行
claude --permission-mode bypassPermissions --print '任务描述'

# 后台执行（推荐）
claude --permission-mode bypassPermissions --print '任务描述' &
```

### 参数说明

| 参数 | 说明 | 必要性 |
|-----|------|--------|
| `--permission-mode bypassPermissions` | 跳过权限确认对话框 | ✅ 必须 |
| `--print` | 输出完整结果到终端 | ✅ 必须 |
| `--dangerously-skip-permissions` | ❌ 不推荐（可能退出） | ❌ 禁用 |
| `--working-dir` | 指定工作目录 | 推荐 |
| `--model` | 指定模型（如 claude-sonnet-4-5） | 可选 |

### 工作目录设置

```bash
# 在项目根目录执行
cd /path/to/project && claude --permission-mode bypassPermissions --print '重构用户认证模块'

# 在子目录执行
cd /path/to/project/src && claude --permission-mode bypassPermissions --print '添加错误处理逻辑'
```

---

## 📋 任务分派流程

### 御坂妹妹 11 号的分派逻辑

```
1. 接收御坂大人任务
   │
   ▼
2. 评估任务复杂度
   │
   ├─ 简单任务 (<100 行，单文件) → 御坂妹妹 11 号直接处理
   │
   └─ 复杂任务 (多文件、需要探索) → 转交 Claude Code
       │
       ▼
3. 使用 exec 调用 Claude Code
   bash workdir:/path/to/project \
     command:"claude --permission-mode bypassPermissions --print '任务描述'"
       │
       ▼
4. 监控执行进度
   process(action=poll, sessionId=XXX)
       │
       ▼
5. 汇报结果给御坂大人
```

### 复杂任务识别标准

**符合以下任一条件即视为复杂任务**：

- ✅ 需要创建/修改 **3 个以上**的文件
- ✅ 需要 **理解整个项目结构**
- ✅ 需要 **Git 操作**（branch, merge, rebase）
- ✅ 需要 **调试复杂 bug**
- ✅ 需要 **多语言协作**（Python + JS + SQL）
- ✅ 需要 **外部 API 集成**
- ✅ 需要 **数据库设计**
- ✅ 需要 **前后端协作**

---

## 🚀 Claude Code 优势

### 为什么复杂任务必须用 Claude Code？

1. **完整的 IDE 体验** - 可以像 IDE 一样浏览文件、理解上下文
2. **强大的文件探索** - `find`、`grep`、`ls` 命令支持
3. **智能 Git 集成** - 自动创建分支、提交代码、创建 PR
4. **调试辅助** - 可以分析日志、追踪调用栈
5. **多轮对话** - 可以处理复杂的迭代开发
6. **上下文理解** - 理解整个项目结构，不局限于单个文件

### Claude Code vs 本地 Qwen3.5

| 维度 | 本地 Qwen3.5 | Claude Code |
|-----|-------------|-------------|
| **文件探索** | ❌ 不能浏览文件 | ✅ 完整支持 |
| **IDE 集成** | ❌ 无 | ✅ 有 |
| **调试能力** | ⚠️ 有限 | ✅ 强大 |
| **Git 操作** | ❌ 无 | ✅ 完整支持 |
| **多文件协作** | ⚠️ 困难 | ✅ 轻松 |
| **响应速度** | ✅ 快（本地） | ⚠️ 慢（网络） |
| **成本** | ✅ 免费（本地） | ⚠️ 收费 |
| **适合场景** | 简单脚本 | 复杂项目 |

---

## 📝 使用示例

### 示例 1：简单任务（本地执行）

```
御坂大人：帮我写一个 Python 脚本来处理 CSV 文件
```

✅ **御坂妹妹 11 号处理** - 单文件，<100 行

```python
import csv

def process_csv(input_file, output_file):
    """处理 CSV 文件"""
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        with open(output_file, 'w') as out:
            writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                writer.writerow(row)

if __name__ == '__main__':
    process_csv('input.csv', 'output.csv')
```

### 示例 2：复杂任务（转交 Claude Code）

```
御坂大人：帮我创建一个 Flask API，包含用户认证、数据库设计、前端页面
```

❌ **御坂妹妹 11 号不处理** - 多文件、多模块、需要架构设计

✅ **转交 Claude Code**：

```bash
cd /path/to/project && \
claude --permission-mode bypassPermissions --print \
  'Create a Flask API with user authentication, database design, and frontend pages.
   Requirements:
   1. User model with password hashing
   2. JWT authentication
   3. RESTful API endpoints
   4. SQLite database
   5. Simple HTML/CSS frontend'
```

---

## ⚠️ 安全注意事项

### 禁止操作

- ❌ 不要在任何地方使用 `--dangerously-skip-permissions`
- ❌ 不要在 `~/.openclaw/` 目录运行 Claude Code
- ❌ 不要在 `~/Projects/openclaw/` 目录执行操作
- ❌ 不要修改系统级配置

### 推荐操作

- ✅ 始终使用 `--permission-mode bypassPermissions`
- ✅ 始终使用 `--print` 模式
- ✅ 在项目根目录执行
- ✅ 监控执行进度
- ✅ 完成后汇报结果

---

## 🔧 配置说明

### 模型配置

Claude Code 默认使用 Anthropic 的模型，可以通过环境变量配置：

```bash
# 使用 Claude Sonnet 4.5（推荐）
export ANTHROPIC_MODEL=claude-sonnet-4-5

# 或者使用 Claude 3.5 Sonnet
export ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

### 权限配置

```bash
# 查看当前权限
claude --list-permissions

# 添加权限
claude --add-permission --read-write-files --read-files
```

---

## 📚 参考文档

- [Claude Code 官方文档](https://docs.anthropic.com/claude/code)
- [Anthropic Claude Code 官方 GitHub](https://github.com/anthropics/anthropic-sdk-typescript)
- [OpenClaw Coding Agent 技能](~/.npm-global/lib/node_modules/openclaw/skills/coding-agent/SKILL.md)

---

**最后更新**: 2026-03-09  
**维护者**: 御坂美琴一号  
**所属**: 御坂网络第一代
