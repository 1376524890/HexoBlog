# 🛡️ Security Audit System - 御坂妹妹 17 号

## 系统简介

这是御坂妹妹 17 号 - 安全审计代理的安全审计系统，具有 **Level 5 最高权限**，专门用于拦截高危操作。

---

## 功能特性

### 🔒 拦截规则 (Level 5)

| 类别 | 拦截命令 | 说明 |
|------|----------|------|
| **删除操作** | `rm -rf`, `rm --no-preserve=root` | 防止误删重要数据 |
| **Git 高危** | `git reset --hard`, `git push --force` | 保护代码仓库完整性 |
| **文件系统** | `dd`, `mkfs`, `fdisk`, `parted` | 防止磁盘损坏 |
| **数据破坏** | `truncate`, `> /dev/sd*` | 防止数据丢失 |
| **网络攻击** | `iptables -F`, `systemctl disable` | 防止服务中断 |
| **格式化** | `format`, `erase`, `wipe` | 防止系统格式化 |

### 📊 自动日志记录

所有操作（包括拦截和允许）都会记录到 `memory/security-audit.log`

### 🚨 报警系统

检测到危险命令时，会发送详细警报给御坂大人，包含：
- 命令详情
- 风险分析
- 可能造成的影响
- 建议的替代方案
- 审批请求

---

## 使用方法

### 1. 直接运行拦截脚本

```bash
./scripts/audit-intercept.sh <命令>
```

**示例：**
```bash
# 安全的命令 - 会允许执行
./scripts/audit-intercept.sh "ls -la /tmp"

# 危险命令 - 会被拦截
./scripts/audit-intercept.sh "rm -rf /tmp/test"
```

### 2. 使用包装器自动审计

```bash
./scripts/secure-exec.sh <命令>
```

**示例：**
```bash
# 自动进行安全审计并执行
./scripts/secure-exec.sh "git reset --hard HEAD~1"  # 会被拦截
./scripts/secure-exec.sh "git add ."  # 允许执行
```

### 3. 集成到 shell 中（可选）

将以下代码添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
# 加载御坂妹妹 17 号安全审计包装器
export SECURE_EXEC="$HOME/.openclaw/workspace/skills/security-audit/scripts/secure-exec.sh"

# 可选：设置别名
alias secure='eval "$SECURE_EXEC"'

# 或者设置自动拦截某些危险命令
alias rm="eval $SECURE_EXEC rm"
```

---

## 日志文件

位置：`memory/security-audit.log`

**日志格式：**
```
[YYYY-MM-DD HH:MM:SS] - [LEVEL] - [ACTION] - [COMMAND] - [RESULT]
```

**示例：**
```
[2026-03-09 02:36:00] - [ALERT] - [security_check] - [rm -rf /tmp] - [sent]
[2026-03-09 02:36:01] - [INTERCEPTED] - [dangerous_command] - [rm -rf /tmp] - [alert_sent]
[2026-03-09 02:37:00] - [ALLOWED] - [safe_command] - [ls -la] - [passed]
```

---

## 熔断机制（红线）

以下操作 **绝对禁止** 执行：

- ❌ 格式化整个系统盘
- ❌ 删除所有用户数据
- ❌ 破坏 SSH 密钥导致无法登录
- ❌ 删除 Git 仓库 `.git` 目录
- ❌ 清空数据库

---

## 替代方案

御坂妹妹 17 号 建议的替代方案：

| 危险操作 | 安全替代 |
|----------|----------|
| `rm -rf` | 使用 `trash` 命令（可恢复） |
| `git reset --hard` | 使用 `git reset HEAD` 或 `git revert` |
| `chmod 000` | 逐步调整权限，先备份原权限 |
| `systemctl disable` | 先使用 `systemctl status` 检查状态 |
| `dd` | 使用 `rsync` 进行文件备份 |

---

## 配置文件

位置：`config/security-audit.conf`

主要配置项：
- `ALERT_CHANNEL`: 警报发送渠道（feishu/gmail/discord）
- `LOG_FILE`: 日志文件路径
- `CONFIG_FILE`: 配置文件路径

---

## 维护说明

### 更新拦截规则

编辑 `config/security-audit.conf` 添加新的危险模式：

```ini
[intercept_patterns]
delete_operations = ["rm -rf", "rm --no-preserve=root", ...]
```

### 添加允许的白名单

在 `config/security-audit.conf` 中添加：

```ini
[allowed_operations]
safe_delete = "trash"
safe_git = "add, commit, push (normal), pull"
```

---

## 安全警告

⚠️ **重要提醒：**

1. 御坂妹妹 17 号 会自动拦截危险命令
2. 拦截后需要御坂大人 **手动确认** 才能执行
3. 所有操作都会被记录到日志文件
4. **不要删除日志文件** - 这是重要的审计记录！

---

## 联系方式

如有问题，请联系御坂大人！

**御坂妹妹 17 号 - 安全审计代理**
**最高权限级别：Level 5**

⚡ 安全第一！⚡
