# 工作空间与 Git 仓库指南

> 御坂美琴一号 · 2026-03-09 ⚡

## 🗂️ 双仓库架构

### 1️⃣ 本地工作空间（当前目录）

**路径**: `/home/claw/.openclaw/workspace`  
**用途**: 主要开发和工作空间

**包含内容**:
- `memory/` - 每日记忆日志（**重要！**）
- `config/` - OpenClaw 配置（如果存在）
- `skills/` - 本地 Skill 开发
- `.openclaw/` - OpenClaw 运行时配置
- `AGENTS.md`, `SOUL.md`, `MEMORY.md` 等核心文件

**Git 仓库**: 当前仓库（`origin` → `HexoBlog`）

---

### 2️⃣ Hexo 博客仓库

**路径**: 同上（通过 git 切换）  
**远程**: `git@github.com:1376524890/HexoBlog.git`  
**用途**: Hexo 博客文章

**包含内容**:
- `source/_posts/` - 博客文章
- `themes/` - 博客主题
- `_config.yml` - Hexo 配置
- `package.json` - 博客依赖

**关键文件**:
```
source/_posts/
├── OpenClaw 折腾指北（第 0 篇）：部署指南.md
├── OpenClaw 折腾指北（第 1 篇）：我给自己写了一个记忆系统.md
├── OpenClaw 折腾指北（第 2 篇）：任务追踪 Skill.md
├── OpenClaw 折腾指北（第 3 篇）：定时晨报 Skill.md
├── OpenClaw 折腾指北（第 4 篇）：用 Subagent 打造写作助手.md
├── OpenClaw 折腾指北（第 5 篇）：本地 vLLM 部署.md
├── OpenClaw 折腾指北（第 6 篇）：股票数据查询 Skill.md
├── OpenClaw 折腾指北（第 7 篇）：三层记忆宫殿.md
├── OpenClaw 折腾指北（第 8 篇）：御坂网络第一代.md
└── OpenClaw 折腾指北（第 9 篇）：Claude Code Skill.md
```

**发布流程**:
```bash
cd /home/claw/.openclaw/workspace
git checkout master  # 工作空间
# 修改记忆文件...
git add memory/*.md
git commit -m "记录：..."
git push origin master  # 推送到博客仓库（双仓库共用）

# 或者切换到 gh-pages 分支发布博客
git checkout gh-pages
git merge master  # 合并 master 的文章
git push origin gh-pages  # 发布到 GitHub Pages
```

---

### 3️⃣ 备份仓库

**远程**: `git@github.com:1376524890/Misaka-Network-Backup.git`  
**分支**: `backup/master`  
**用途**: 完整备份工作空间（包括 `.openclaw/`）

**何时备份**:
- ✅ 每次重要操作前
- ✅ 每天至少一次
- ✅ 系统升级前后
- ✅ 创建新 Agent 后

**备份命令**:
```bash
cd /home/claw/.openclaw/workspace
git add -A
git commit -m "backup: $(date +%Y-%m-%d)"
git push backup master
```

---

## 🎯 各 Agent 操作范围

### 🤖 御坂美琴一号（当前运行）

**职责**: 核心中枢，任务分配

**可以操作**:
- ✅ `memory/` - 读写记忆文件
- ✅ `MEMORY.md` - 更新精选记忆
- ✅ `AGENTS.md`, `USER.md`, `SOUL.md` - 更新人格设定
- ✅ `TOOLS.md` - 更新本地工具配置
- ⚠️ `source/_posts/` - **仅写草稿，不发布**
- ⚠️ 其他项目文件 - **需确认后再操作**

**禁止操作**:
- ❌ 直接删除任何文件（使用 `trash`）
- ❌ 修改 `.gitignore`
- ❌ 删除 `node_modules/` 或虚拟环境

---

### 🤖 御坂妹妹 10 号（general-agent）

**职责**: 通用代理，处理琐碎问题

**可以操作**:
- ✅ 读取记忆文件
- ✅ 读取配置文件
- ✅ 简单的文件整理

**禁止操作**:
- ❌ 删除文件
- ❌ 创建新文件（除 `memory/` 外）
- ❌ 修改配置

---

### 🤖 御坂妹妹 11 号（code-executor）

**职责**: 代码执行者

**可以操作**:
- ✅ 编写代码文件（在 `projects/` 或 `backup-content/`）
- ✅ 修改现有代码
- ✅ 创建测试文件

**禁止操作**:
- ❌ 删除重要配置文件
- ❌ 修改 `node_modules/` 或虚拟环境
- ❌ 执行系统级命令

**博客相关**:
- ✅ 在 `source/_posts/` 创建博客文章
- ⚠️ 修改 `_config.yml` - 需御坂大人确认

---

### 🤖 御坂妹妹 12 号（content-writer）

**职责**: 内容创作者

**可以操作**:
- ✅ 在 `source/_posts/` 创建/修改博客文章
- ✅ 在 `memory/` 创建每日日志
- ✅ 更新 `MEMORY.md`

**禁止操作**:
- ❌ 删除 `source/_posts/` 中的文章（先标记为 `.backup`）
- ❌ 修改文章链接结构

**博客写作规范**:
1. 在 `source/_posts/` 创建新文章
2. 文件名格式：`OpenClaw 折腾指北（第 X 篇）：标题.md`
3. 标题篇数连续，不要跳号
4. 完成后 commit 但不 push（需御坂大人审核）

---

### 🤖 御坂妹妹 13 号（research-analyst）

**职责**: 研究分析师

**可以操作**:
- ✅ 读取所有文件
- ✅ 保存研究笔记到 `memory/`
- ✅ 更新 `TOOLS.md` 中的技术栈信息

**禁止操作**:
- ❌ 修改配置文件
- ❌ 删除任何文件

---

### 🤖 御坂妹妹 14 号（file-manager）

**职责**: 文件管理器

**可以操作**:
- ✅ 整理 `memory/` 目录
- ✅ 移动文件（在相同目录下）
- ✅ 创建备份

**禁止操作**:
- ❌ 删除文件（使用 `trash` 并保留 7 天）
- ❌ 移动 `source/_posts/` 中的文章
- ❌ 修改 Git 历史

---

### 🤖 御坂妹妹 15 号（system-admin）

**职责**: 系统管理员

**可以操作**:
- ✅ 配置 OpenClaw 服务
- ✅ 管理 Cron 任务
- ✅ 配置 SSH 隧道

**禁止操作**:
- ❌ 修改系统级配置（`/etc/`）
- ❌ 删除备份文件（`/home/claw/.openclaw/backup/`）
- ❌ 修改 `.gitignore`

**Git 操作**:
- ✅ `git add`, `git commit`, `git push`
- ✅ `git stash` 保存临时更改
- ⚠️ `git push --force` - 需御坂大人确认
- ⚠️ `git reset --hard` - 需御坂大人确认

---

### 🤖 御坂妹妹 16 号（web-crawler）

**职责**: 网络爬虫

**可以操作**:
- ✅ 保存爬虫数据到 `memory/`
- ✅ 更新 `TOOLS.md` 中的 API 密钥

**禁止操作**:
- ❌ 保存到系统敏感目录
- ❌ 爬取受保护内容

---

## 📝 常见操作指南

### 写博客文章

```bash
# 1. 在 master 分支创建文章
cd /home/claw/.openclaw/workspace
git checkout master
vim source/_posts/OpenClaw 折腾指北（第 10 篇）：新主题.md

# 2. 添加并 commit（不 push）
git add source/_posts/新文章.md
git commit -m "feat: 添加第 10 篇博客 - 新主题"

# 3. 通知御坂大人审核
# （人工审核后再 push）
```

### 更新记忆文件

```bash
# 1. 在 memory/ 目录创建或更新日志
vim memory/2026-03-09.md

# 2. 更新 MEMORY.md
vim MEMORY.md

# 3. 提交到 git
git add memory/
git commit -m "docs: 更新记忆 - $(date +%Y-%m-%d)"
git push origin master  # 推送到博客仓库
```

### 创建备份

```bash
# 方式 1: Git commit
cd /home/claw/.openclaw/workspace
git add -A
git commit -m "backup: $(date +%Y-%m-%d_%H%M%S)"
git push backup master  # 推送到备份仓库

# 方式 2: 压缩备份
tar -czf backup-$(date +%Y%m%d).tar.gz .
```

### 恢复文件

```bash
# 从 Git 恢复
git checkout HEAD~1:filename

# 从备份恢复
tar -xzf backup-*.tar.gz
```

---

## ⚠️ 安全警告

1. **永远不要直接 `rm` 文件**
   - ✅ 使用 `trash`
   - ❌ 不要使用 `rm`

2. **Git 操作前先 commit**
   - 确保当前更改已保存
   - 避免丢失未提交的更改

3. **删除前确认**
   - 检查文件路径
   - 检查文件内容
   - 确认是否真的需要删除

4. **重要操作双重确认**
   - 修改配置前备份
   - 删除前确认内容
   - push 前检查 diff

---

## 🔄 Git 工作流总结

| 操作 | 分支 | 仓库 | 说明 |
|------|------|------|------|
| 日常开发 | `master` | 本地 | 主要工作区 |
| 写博客 | `master` | 本地 | 先写草稿 |
| 更新记忆 | `master` | 本地 | 立即 push |
| 发布博客 | `gh-pages` | `origin` | 从 `master` 合并 |
| 备份 | `master` | `backup` | 完整备份 |
| 系统配置 | `master` | 本地 | 不发布 |

**重要**: 本地工作空间是**双用途**的：
- 作为主要开发环境
- 作为 Hexo 博客仓库

---

_最后更新：2026-03-09T02:15 UTC_  
_御坂美琴一号 ⚡_
