# 持续运行 Agent - 快速启动指南
## 御坂美琴的持续学习进化系统 ⚡

### 🚀 启动方式

#### 方法 1: 直接运行 (推荐)

```bash
cd /home/claw/.openclaw/workspace/skills/continuous-learning

# 启动持续运行模式
python3 running-agent/run_running_agent.py
```

#### 方法 2: 后台运行

```bash
# 使用 nohup
nohup python3 running-agent/run_running_agent.py > running-agent.log 2>&1 &

# 或使用 screen
screen -S running-agent
python3 running-agent/run_running_agent.py
# 按 Ctrl+A, D 退出 screen
```

#### 方法 3: 使用 Systemd (推荐用于长期运行)

创建 `/etc/systemd/system/running-agent.service`:

```ini
[Unit]
Description=Running Agent for Continuous Learning
After=network.target

[Service]
Type=simple
User=claw
WorkingDirectory=/home/claw/.openclaw/workspace/skills/continuous-learning
ExecStart=/usr/bin/python3 running-agent/run_running_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动:
```bash
sudo systemctl daemon-reload
sudo systemctl enable running-agent
sudo systemctl start running-agent
```

### 📊 常用命令

```bash
# 查看状态
python3 running-agent/run_running_agent.py status

# 查看待审批报告
python3 running-agent/run_running_agent.py report

# 列出待审批项目
python3 running-agent/run_running_agent.py list

# 批准项目
python3 running-agent/run_running_agent.py approve #1

# 拒绝项目
python3 running-agent/run_running_agent.py reject #1 不符合要求

# 查看帮助
python3 running-agent/run_running_agent.py help
```

### ⚙️ 配置

编辑 `running-agent/running_agent_config.yaml`:

```yaml
github:
  token: "ghp_your_token_here"  # 添加 GitHub Token (可选)

discovery:
  keywords:
    - "skill"
    - "agent"
    - "ai"
  
  min_stars: 10  # 最小星标数
  min_forks: 2   # 最小分叉数

queue:
  max_size: 5  # 最大队列长度

running:
  check_interval: 300  # 检查间隔 (秒)
```

### 📁 文件结构

```
continuous-learning/
├── running-agent/              # 持续运行模块
│   ├── running_agent.py       # 主程序
│   ├── queue_manager.py       # 队列管理
│   ├── approval_system.py     # 批准系统
│   ├── running_agent_config.yaml  # 配置文件
│   └── run_running_agent.py   # 可执行脚本
├── approval_requests/          # 待批准请求
│   └── pending_approvals.json
├── output/                     # 分析结果
├── discovery.py               # 项目发现
├── analysis.py                # 项目分析
├── evaluation.py              # 六维评估
└── integration.py             # 技能集成
```

### 🔄 工作流程

```
1. 启动 → 检查队列
2. 队列 < 5 → 执行 Discovery 搜索
3. 发现项目 → 添加到队列
4. 队列满 → 等待
5. 分析项目 → 评估
6. 生成待批准列表
7. 御坂大人批准
8. 批准 → 自动集成
9. 循环
```

### 📝 审批说明

御坂大人可以使用以下命令:

- `approve` - 批准第一个待审批项目
- `approve #1` - 批准第一个项目
- `approve req_xxx` - 批准指定请求
- `reject #1 原因` - 拒绝项目并说明原因
- `report` - 查看详细报告
- `list` - 列出待审批项目

### 🐛 故障排查

#### 问题 1: 权限不足

```bash
# 确保脚本有执行权限
chmod +x running-agent/run_running_agent.py
```

#### 问题 2: 依赖缺失

```bash
# 安装必要依赖
pip3 install github3.py PyYAML python-git
```

#### 问题 3: GitHub API 速率限制

添加 GitHub Token:
```bash
# 编辑配置
vim running-agent/running_agent_config.yaml

# 添加 token
github:
  token: "ghp_your_token_here"
```

### 📈 性能监控

```bash
# 查看运行日志
tail -f running-agent/running-agent.log

# 查看统计信息
cat running-agent/agent_stats.json

# 查看队列状态
python3 running-agent/queue_manager.py --status
```

### 🎯 下一步

1. **添加 GitHub Token** - 避免 API 速率限制
2. **配置通知** - 集成 Feishu 消息通知
3. **设置自动启动** - 使用 systemd 或 cron
4. **定期审查** - 检查待审批项目和集成结果

---

御坂妹妹已经准备好啦！御坂大人可以开始使用了！⚡
