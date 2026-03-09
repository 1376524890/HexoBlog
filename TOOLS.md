# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## 🔧 OpenClaw 配置

### 运行环境
- **模型**: `local-vllm/Qwen/Qwen3.5-35B-A3B-FP8`
- **远程模型**: `Qwen/Qwen3.5-35B-A3B-FP8`
- **网关地址**: `codeserver@39.102.210.43:6122 -> localhost:8000`

### 定时任务 (Cron)
| ID | 名称 | 频率 | 状态 |
|---|---|---|---|
| `memory-checkpoint` | 记忆检查点 | 每 6 小时 | ✅ 启用 |
| `auto-backup` | 自动备份 | 每 6 小时 | ✅ 启用 |
| `auto-cleanup` | 自动清理过期备份 | 每天 12:30 | ✅ 启用 |

## 📁 工作目录

- **主工作区**: `/home/claw/.openclaw/workspace`
- **技能目录**: `~/.openclaw/skills/`
- **配置文件**: `~/.openclaw/config/`
- **记忆目录**: `~/.openclaw/workspace/memory/`
- **备份目录**: `~/.openclaw/backup/`

## 🤖 御坂妹妹权限等级

| 编号 | Agent ID | 权限级别 | 说明 |
|------|----------|----------|------|
| 10 号 | `general-agent` | Level 2 | 指定目录读写 |
| 11 号 | `code-executor` | Level 3 | 工作目录读写 |
| 12 号 | `content-writer` | Level 3 | 读写文档文件 |
| 13 号 | `research-analyst` | Level 3 | 网络搜索、分析 |
| 14 号 | `file-manager` | Level 2 | 指定目录操作 |
| 15 号 | `system-admin` | Level 4 | 系统配置需批准 |
| 16 号 | `web-crawler` | Level 2 | 网页抓取 |
| 17 号 | `memory-organizer` | Level 3 | 记忆系统维护、整理和备份 🧠 |

## 💾 备份策略

- **本地备份**: `/home/claw/.openclaw/backup/`
- **Git 同步**: 每 6 小时自动提交到 Git
- **清理策略**: 每天 12:30 清理 7 天前的备份
- **恢复点**: 6 小时间隔的 checkpoint

---

_随着系统升级，这里会不断更新。_
