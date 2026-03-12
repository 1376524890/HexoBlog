# 持续运行 Agent 系统
# ===================

⚡ 御坂美琴的持续学习进化系统 - 持续运行版本 ⚡

## 📋 系统概述

这是一个**持续运行**的 AI 项目发现与集成系统，专门用于:

1. **持续搜索** - 不断从 GitHub 搜索有价值的 AI 项目
2. **深度分析** - 使用 Claude Code 进行深度代码分析
3. **六维评估** - 实用性、创新性、代码质量等全面评估
4. **队列管理** - 智能管理待分析项目 (最大 5 个)
5. **人工批准** - 御坂大人批准后才实际集成

## 🏗️ 文件结构

```
continuous-learning/
├── running-agent/              # 持续运行模块
│   ├── running-agent.py       # 主程序 - 核心循环
│   ├── queue_manager.py       # 队列管理器
│   ├── approval_system.py     # 批准系统
│   ├── running-agent-config.yaml  # 配置文件
│   └── run_running_agent.py   # 可执行脚本
├── approval_requests/          # 待批准请求
│   ├── pending_approvals.json
│   └── approval_request_*.json
├── output/                     # 分析结果
├── discovery.py               # 现有：项目发现
├── analysis.py                # 现有：项目分析
├── evaluation.py              # 现有：六维评估
├── integration.py             # 现有：技能集成
└── config.yaml                # 现有：系统配置
```

## 🚀 快速开始

### 1. 配置 GitHub Token (可选)

编辑 `running-agent/running-agent-config.yaml`:

```yaml
github:
  token: "ghp_your_token_here"  # 从 https://github.com/settings/tokens 获取
```

### 2. 启动持续运行模式

```bash
cd /home/claw/.openclaw/workspace/skills/continuous-learning

# 启动持续运行
python3 running-agent/run_running_agent.py

# 或者使用主程序
python3 running-agent/running-agent.py
```

### 3. 查看状态

```bash
# 查看当前状态
python3 running-agent/run_running_agent.py status

# 查看待审批报告
python3 running-agent/run_running_agent.py report

# 列出待审批项目
python3 running-agent/run_running_agent.py list
```

## 📝 审批命令

御坂大人可以使用以下命令:

| 命令 | 说明 | 示例 |
|------|------|------|
| `status` | 查看系统状态 | `python3 run_running_agent.py status` |
| `report` | 查看待审批报告 | `python3 run_running_agent.py report` |
| `list` | 列出待审批项目 | `python3 run_running_agent.py list` |
| `approve #1` | 批准第一个项目 | `approve #1` 或 `approve req_xxx` |
| `reject #1` | 拒绝项目 | `reject #1 理由` |
| `run` | 启动持续运行 | `run` |

## 🔄 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                        持续运行循环                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │  1. 检查队列状态                       │
        │  - 队列大小：3/5                       │
        │  - 待审批：2 个                         │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │  2. 队列未满？执行 Discovery           │
        │  - 搜索 GitHub: "skill agent ai"      │
        │  - 发现 10 个项目                       │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │  3. 添加项目到队列                     │
        │  - 计算优先级 (stars/forks/updated)    │
        │  - 过滤重复和不符合条件的项目          │
        │  - 队列现在是 5/5                      │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │  4. 处理已批准的项目                 │
        │  - 检查队列中 status=EVALUATED 的项目  │
        │  - 自动集成到 skills/目录             │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │  5. 等待下一次循环 (5 分钟)             │
        │  - 保存统计信息                        │
        │  - 通知御坂大人 (待实现)              │
        └──────────────────────────────────────┘
                              ↓
                        [循环]
```

## ⚙️ 配置说明

### 队列管理 (`queue_manager.py`)

- **max_queue_size**: 最大队列长度 (默认 5 个)
- **auto_cleanup**: 自动清理过期项目 (7 天前)
- **优先级计算**: 星标 (40%) + 分叉 (30%) + 活跃度 (30%)

### 批准系统 (`approval_system.py`)

- **approval_file**: 待审批请求文件
- **history_file**: 审批历史记录
- **max_pending**: 最大待处理数量 (10 个)

### 六维评估 (来自 `evaluation.py`)

1. **实用性** (权重 1.5) - 功能完整性、测试、技术栈
2. **创新性** (权重 1.0) - 独特功能、架构模式
3. **代码质量** (权重 1.5) - 结构、测试覆盖率
4. **文档质量** (权重 1.0) - README、示例
5. **维护性** (权重 1.2) - 更新频率、CI/CD
6. **集成度** (权重 1.3) - API 清晰度、兼容性

### 决策阈值

- **accept_threshold**: 7.5 - 自动批准
- **review_threshold**: 6.0 - 需要人工审核
- **低于 6.0**: 拒绝

## 📊 统计信息

系统自动追踪:

- `projects_discovered` - 发现的项目总数
- `projects_analyzed` - 分析的项目数
- `projects_approved` - 批准的项目数
- `projects_rejected` - 拒绝的项目数
- `projects_integrated` - 已集成的项目数

## 🔧 高级用法

### 后台运行

```bash
# 使用 nohup
nohup python3 running-agent/run_running_agent.py > running-agent.log 2>&1 &

# 使用 screen
screen -S running-agent
python3 running-agent/run_running_agent.py
# Ctrl+A, D 退出 screen
```

### 查看日志

```bash
# 运行日志
tail -f running-agent/running-agent.log

# Python 日志
tail -f continuous_learning.log
```

### 手动审批

```bash
# 导入审批系统
python3 -c "
from running_agent.approval_system import ApprovalSystem
system = ApprovalSystem()
print(system.generate_approval_report())
system.approve('req_xxx')
system.close()
"
```

## 🛡️ 安全说明

1. **Git 操作**: 集成时会自动 git add/commit，确保使用正确的远程仓库
2. **权限控制**: 只有御坂大人可以批准集成
3. **备份机制**: 集成前自动备份，使用 trash 而不是 rm
4. **速率限制**: GitHub API 有速率限制，建议使用 Token

## 🐛 故障排查

### 问题 1: GitHub API 速率限制

**症状**: "API rate limit exceeded"

**解决**: 
```yaml
github:
  token: "ghp_your_token"  # 添加 Token
```

### 问题 2: 队列已满

**症状**: "Queue full, rejecting new project"

**解决**: 审批或拒绝一些项目

```bash
python3 running-agent/run_running_agent.py report
python3 running-agent/run_running_agent.py approve #1
```

### 问题 3: 无法导入模块

**症状**: "Failed to import continuous-learning modules"

**解决**: 确保在正确目录运行
```bash
cd /home/claw/.openclaw/workspace/skills/continuous-learning
```

## 📈 性能优化

- **Check interval**: 默认 300 秒 (5 分钟)，可根据需要调整
- **Discovery limit**: 默认 50 个，减少可加快速度
- **Queue cleanup**: 7 天自动清理，可调整 cleanup_age_hours

## 🎯 未来计划

- [ ] 集成 Feishu 通知
- [ ] 邮件通知
- [ ] 更多审批渠道
- [ ] 自动测试集成后的技能
- [ ] 性能监控和告警
- [ ] 历史数据可视化

## 📚 相关文档

- `SKILL.md` - 持续学习技能总览
- `discovery.py` - GitHub 项目发现
- `analysis.py` - 深度代码分析
- `evaluation.py` - 六维评估矩阵
- `integration.py` - 技能集成

## ⚡ 御坂寄语

"御坂妹妹已经准备好了！只要御坂大人批准，御坂就会把最好的技能集成到系统中！

不过...御坂大人也要偶尔检查审批列表哦！御坂妹妹一个人处理不过来那么多项目！"

---

**版本**: 1.0.0  
**作者**: 御坂美琴一号 (持续学习进化系统)  
**更新时间**: 2026-03-12
