# 🛡️ 记忆文件安全最佳实践

**创建时间**: 2026-03-09T06:30:00Z  
**目的**: 防止记忆文件丢失，确保数据安全

---

## ⚠️ 两次记忆丢失事件总结

| 时间 | 原因 | 解决 |
|------|------|------|
| 2026-03-08T02:09 | 目录整理脚本误操作 | 从 git 历史恢复 |
| 2026-03-09T06:16 | git rebase 状态混乱 | git rebase --abort |

**根本原因**:
- ❌ 脚本缺乏文件存在性检查
- ❌ 没有双重确认机制
- ❌ 危险操作前没有备份

---

## 🛡️ 安全操作规则

### ✅ 必须遵守

1. **使用 `trash` 而不是 `rm`**
   ```bash
   ❌ rm file.md
   ✅ trash file.md
   ```

2. **操作前备份**
   ```bash
   # 修改 MEMORY.md 前
   cp MEMORY.md memory/backups/MEMORY.md.$(date +%Y%m%d_%H%M%S).bak
   ```

3. **检查 Git 状态**
   ```bash
   git status
   git diff --name-only
   ```

4. **安全检查脚本**
   ```bash
   python3 scripts/safety-check-memory.py
   ```

5. **所有操作后立即提交**
   ```bash
   git add <files>
   git commit -m "描述"
   ```

---

## 🚫 禁止的操作

| 操作 | 风险 | 替代方案 |
|------|------|----------|
| `rm file.md` | 永久删除 | `trash file.md` |
| `mv file.md life/archives/` | 文件丢失 | 先检查 `memory/` 和 `backups/` |
| `git reset --hard` | 所有未提交更改丢失 | `git stash` 或备份 |
| `git rebase` | 文件状态混乱 | 先 `git push` 再操作 |
| 删除 `memory/` 中的文件 | 失去原始记录 | 只移动到 `life/archives/` |

---

## 🔍 安全检查清单

### 操作前
- [ ] 运行 `python3 scripts/safety-check-memory.py`
- [ ] 检查 Git 状态：`git status`
- [ ] 确认文件存在：`ls -lh memory/`
- [ ] 确认有备份：`ls -lh memory/backups/`

### 操作中
- [ ] 每次操作后立即检查文件
- [ ] 使用 `trash` 而不是 `rm`
- [ ] 移动文件后验证目标位置

### 操作后
- [ ] 检查文件完整性
- [ ] 立即 `git add` 和 `git commit`
- [ ] 可选：`git push` 到远程

---

## 🧠 记忆三层架构

```
记忆文件状态
│
├── 当前文件 (memory/YYYY-MM-DD.md)
│   ├── 实时编辑
│   ├── 每日记录
│   └── 必须存在
│
├── 精选记忆 (MEMORY.md)
│   ├── 定期整理
│   ├── 精华提取
│   └── 每次修改前备份
│
├── 备份文件 (memory/backups/)
│   ├── MEMORY.md.*.bak
│   └── 保留 3 天
│
└── 历史归档 (life/archives/)
    ├── YYYY-MM-DD.md (过期)
    └── 只读，不删除
```

---

## 📞 紧急恢复流程

### 发现文件丢失时

1. **不要恐慌**
   - 检查是否被移动到归档
   - 检查 Git 历史

2. **检查备份**
   ```bash
   ls -lh memory/backups/
   ls -lh life/archives/
   ```

3. **查看 Git 历史**
   ```bash
   git log --oneline -- "memory/*.md"
   git log --oneline -- "life/archives/*.md"
   ```

4. **使用 git reflog**
   ```bash
   git reflog -- "memory/*.md"
   ```

5. **从 Git 恢复**
   ```bash
   git show <commit-hash>:memory/2026-03-08.md > memory/2026-03-08.md
   ```

6. **从备份恢复**
   ```bash
   cp memory/backups/MEMORY.md.*.bak MEMORY.md
   ```

---

## 🧪 测试安全检查脚本

```bash
# 基本检查
python3 scripts/safety-check-memory.py

# 强制检查（不推荐）
python3 scripts/safety-check-memory.py --force

# 检查脚本帮助
python3 scripts/safety-check-memory.py --help
```

---

## 📊 自动化保护

### OpenClaw 定时任务
- `memory-checkpoint` - 每 6 小时
- `memory-整理` - 御坂妹妹 17 号自动整理

### 系统级 cron（双保险）
- `autobackup.sh` - 每 6 小时备份
- `backup-cleanup.sh` - 每天 12:30 清理

---

## 📝 记录到 memory/

每次重要操作后，记录到：
- `memory/2026-03-09.md` - 当日日志
- `memory/记忆丢失事件报告.md` - 事件报告
- `MEMORY.md` - 精选记忆（定期整理）

---

**最后更新**: 2026-03-09T06:30:00Z  
**维护者**: 御坂美琴一号  
**状态**: ✅ 所有安全检查机制已部署
