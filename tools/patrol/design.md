# Patrol Agent 设计文档

> **文档版本**: v2.0  
> **创建时间**: 2026-03-12  
> **作者**: 御坂妹妹 11 号  
> **用途**: 御坂妹妹 19 号（Patrol Agent）的设计与实现

---

## 一、设计目标

### 1.1 核心职责

**Patrol Agent（御坂妹妹 19 号）的核心职责是监控御坂网络系统的运行状态，确保系统稳定性。**

**核心目标**：
1. **实时监控** - 持续监控系统运行状态
2. **异常检测** - 及时发现系统异常
3. **自动恢复** - 对常见异常自动恢复
4. **健康报告** - 定期输出系统健康度报告

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **最小影响** | 监控过程不干扰正常业务 |
| **高可用性** | 自身要高度可靠，不死机 |
| **快速响应** | 发现问题快速响应 |
| **自动恢复** | 常见异常自动处理 |
| **详细日志** | 所有操作记录日志 |

---

## 二、监控对象

### 2.1 任务监控

```
监控对象：任务状态机
监控指标：
- 任务总数
- 各状态任务数
- 任务平均耗时
- 任务失败率
- 任务超时数
```

### 2.2 模块监控

```
监控对象：御坂妹妹各模块
监控指标：
- 模块状态（运行/停止/异常）
- CPU 使用率
- 内存使用率
- 响应时间
- 错误率
```

### 2.3 系统监控

```
监控对象：系统整体
监控指标：
- 系统总负载
- 可用内存
- 磁盘空间
- 网络连接数
- 队列长度
```

### 2.4 审核监控

```
监控对象：Review 审核流程
监控指标：
- 审核通过率
- 审核平均耗时
- 审核失败数
- 审核队列长度
```

---

## 三、监控机制

### 3.1 心跳检测

```python
class HeartbeatMonitor:
    """心跳检测器"""
    
    def __init__(self):
        self.heartbeat_interval = 30  # 30 秒
        self.timeout_threshold = 90   # 90 秒超时
        self.heartbeat_history = {}
        
    def send_heartbeat(self, agent_id):
        """发送心跳"""
        
        heartbeat = {
            'agent_id': agent_id,
            'timestamp': time.time(),
            'status': 'alive',
            'memory_usage': self.get_memory_usage(agent_id),
            'cpu_usage': self.get_cpu_usage(agent_id),
            'task_count': self.get_task_count(agent_id),
        }
        
        self.heartbeat_history[agent_id] = heartbeat
        return heartbeat
    
    def check_heartbeat(self, agent_id):
        """检查心跳"""
        
        if agent_id not in self.heartbeat_history:
            return {
                'status': 'unknown',
                'message': '未收到心跳'
            }
        
        last_heartbeat = self.heartbeat_history[agent_id]['timestamp']
        current_time = time.time()
        
        if current_time - last_heartbeat > self.timeout_threshold:
            return {
                'status': 'timeout',
                'message': '心跳超时',
                'elapsed': current_time - last_heartbeat
            }
        else:
            return {
                'status': 'alive',
                'message': '心跳正常',
                'elapsed': current_time - last_heartbeat
            }
    
    def run(self):
        """运行心跳检测"""
        
        while True:
            # 检测所有 Agent
            agents = self.get_all_agents()
            for agent_id in agents:
                status = self.check_heartbeat(agent_id)
                
                if status['status'] == 'timeout':
                    self.handle_timeout(agent_id, status)
            
            sleep(self.heartbeat_interval)
```

### 3.2 任务超时检测

```python
class TaskTimeoutMonitor:
    """任务超时检测器"""
    
    def __init__(self):
        self.timeout_threshold = 30 * 60  # 30 分钟
        self.warning_threshold = 20 * 60  # 20 分钟
        
    def check_tasks(self):
        """检查任务状态"""
        
        tasks = self.get_running_tasks()
        timeout_tasks = []
        warning_tasks = []
        
        for task in tasks:
            elapsed = time.time() - task['started_at']
            
            if elapsed > self.timeout_threshold:
                timeout_tasks.append(task)
            elif elapsed > self.warning_threshold:
                warning_tasks.append(task)
        
        return {
            'timeout': timeout_tasks,
            'warning': warning_tasks
        }
    
    def handle_timeout(self, task):
        """处理超时任务"""
        
        # 1. 记录日志
        self.log(f"任务超时：{task['id']}")
        
        # 2. 尝试自动恢复
        recovery_result = self.try_recovery(task)
        
        if recovery_result['success']:
            # 恢复成功，继续任务
            self.resume_task(task)
        else:
            # 恢复失败，标记为失败
            self.mark_task_failed(task, 'timeout')
```

### 3.3 资源监控

```python
class ResourceMonitor:
    """资源监控器"""
    
    def __init__(self):
        self.memory_warning_threshold = 80  # 80%
        self.memory_critical_threshold = 90  # 90%
        self.cpu_warning_threshold = 70  # 70%
        self.cpu_critical_threshold = 90  # 90%
        
    def check_resources(self):
        """检查系统资源"""
        
        memory_usage = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()
        disk_usage = self.get_disk_usage()
        
        alerts = []
        
        # 检查内存
        if memory_usage > self.memory_critical_threshold:
            alerts.append({
                'type': 'critical',
                'metric': 'memory',
                'value': memory_usage,
                'message': f'内存使用率过高：{memory_usage}%'
            })
        elif memory_usage > self.memory_warning_threshold:
            alerts.append({
                'type': 'warning',
                'metric': 'memory',
                'value': memory_usage,
                'message': f'内存使用率偏高：{memory_usage}%'
            })
        
        # 检查 CPU
        if cpu_usage > self.cpu_critical_threshold:
            alerts.append({
                'type': 'critical',
                'metric': 'cpu',
                'value': cpu_usage,
                'message': f'CPU 使用率过高：{cpu_usage}%'
            })
        elif cpu_usage > self.cpu_warning_threshold:
            alerts.append({
                'type': 'warning',
                'metric': 'cpu',
                'value': cpu_usage,
                'message': f'CPU 使用率偏高：{cpu_usage}%'
            })
        
        return alerts
```

### 3.4 审核质量监控

```python
class AuditQualityMonitor:
    """审核质量监控器"""
    
    def __init__(self):
        self.pass_rate_threshold = 70  # 70% 通过率
        self.fails_threshold = 5  # 连续 5 次失败
        
    def check_audit_quality(self):
        """检查审核质量"""
        
        # 获取最近 100 次审核
        audits = self.get_recent_audits(limit=100)
        
        if not audits:
            return {
                'status': 'no_data',
                'message': '没有审核数据'
            }
        
        # 计算通过率
        passed = sum(1 for a in audits if a['passed'])
        pass_rate = passed / len(audits) * 100
        
        # 检查连续失败
        consecutive_fails = 0
        for audit in reversed(audits):
            if not audit['passed']:
                consecutive_fails += 1
            else:
                break
        
        alerts = []
        
        # 检查通过率
        if pass_rate < self.pass_rate_threshold:
            alerts.append({
                'type': 'warning',
                'metric': 'pass_rate',
                'value': pass_rate,
                'message': f'审核通过率偏低：{pass_rate}%'
            })
        
        # 检查连续失败
        if consecutive_fails > self.fails_threshold:
            alerts.append({
                'type': 'critical',
                'metric': 'consecutive_fails',
                'value': consecutive_fails,
                'message': f'审核连续失败过多：{consecutive_fails}次'
            })
        
        return {
            'status': 'ok' if not alerts else 'alert',
            'pass_rate': pass_rate,
            'consecutive_fails': consecutive_fails,
            'alerts': alerts
        }
```

---

## 四、自动恢复机制

### 4.1 恢复策略

```python
class RecoveryStrategy:
    """恢复策略"""
    
    # 恢复策略类型
    RESTART = 'restart'           # 重启
    RESET_STATE = 'reset_state'   # 重置状态
    ROLLBACK = 'rollback'         # 回滚
    SKIP = 'skip'                 # 跳过
    ALERT = 'alert'               # 人工介入
    
    def choose_recovery(self, error_type, error_context):
        """选择恢复策略"""
        
        # 心跳超时 - 重启
        if error_type == 'heartbeat_timeout':
            return self.RESTART
        
        # 任务超时 - 重试
        elif error_type == 'task_timeout':
            return self.RETRY
        
        # 内存溢出 - 重启
        elif error_type == 'memory_error':
            return self.RESTART
        
        # 审核失败 - 重置状态
        elif error_type == 'audit_failed':
            return self.RESET_STATE
        
        # 未知错误 - 人工介入
        else:
            return self.ALERT
```

### 4.2 恢复执行器

```python
class RecoveryExecutor:
    """恢复执行器"""
    
    def execute_recovery(self, agent_id, recovery_strategy):
        """执行恢复"""
        
        if recovery_strategy == RecoveryStrategy.RESTART:
            return self.restart_agent(agent_id)
        
        elif recovery_strategy == RecoveryStrategy.RESET_STATE:
            return self.reset_agent_state(agent_id)
        
        elif recovery_strategy == RecoveryStrategy.ROLLBACK:
            return self.rollback_agent(agent_id)
        
        elif recovery_strategy == RecoveryStrategy.SKIP:
            return self.skip_task(agent_id)
        
        elif recovery_strategy == RecoveryStrategy.ALERT:
            return self.alert_human(agent_id)
    
    def restart_agent(self, agent_id):
        """重启 Agent"""
        
        # 1. 保存当前状态
        state = self.save_agent_state(agent_id)
        
        # 2. 停止 Agent
        self.stop_agent(agent_id)
        
        # 3. 等待清理
        sleep(5)
        
        # 4. 启动 Agent
        self.start_agent(agent_id)
        
        # 5. 恢复状态
        self.restore_agent_state(agent_id, state)
        
        return {'success': True, 'strategy': 'restart'}
    
    def reset_agent_state(self, agent_id):
        """重置 Agent 状态"""
        
        # 1. 获取当前状态
        current_state = self.get_agent_state(agent_id)
        
        # 2. 回滚到上一个稳定状态
        previous_state = self.get_previous_stable_state(agent_id)
        
        # 3. 应用回滚
        self.apply_state(agent_id, previous_state)
        
        # 4. 验证状态
        if self.verify_state(agent_id, previous_state):
            return {'success': True, 'strategy': 'reset_state'}
        else:
            return {'success': False, 'strategy': 'reset_state'}
```

### 4.3 恢复流程

```
┌─────────────────┐
│  检测到异常     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  选择恢复策略   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ↓         ↓          ↓          ↓
 restart  reset_state  rollback   alert
    │         │          │          │
    ↓         ↓          ↓          ↓
  重启      重置        回滚      人工
  Agent     状态       状态      介入
    │         │          │          │
    └─────────┴──────────┴──────────┘
                  │
                  ↓
          ┌───────────────┐
          │  验证恢复结果 │
          └───────────────┘
                  │
         ┌────────┴────────┐
         ↓                 ↓
    恢复成功          恢复失败
         │                 │
         ↓                 ↓
    继续运行          人工介入
```

---

## 五、健康报告

### 5.1 报告内容

```json
{
  "timestamp": "2026-03-12T10:00:00",
  "report_type": "hourly",
  "system_health": {
    "status": "healthy",
    "score": 95,
    "uptime": "30 days 5 hours",
    "total_agents": 10,
    "active_agents": 10,
    "healthy_agents": 9,
    "warning_agents": 1,
    "unhealthy_agents": 0
  },
  "task_statistics": {
    "total_tasks": 150,
    "pending_tasks": 5,
    "running_tasks": 20,
    "completed_tasks": 120,
    "failed_tasks": 5,
    "avg_completion_time": "25 minutes"
  },
  "audit_statistics": {
    "total_audits": 100,
    "passed_audits": 85,
    "failed_audits": 15,
    "pass_rate": "85%",
    "avg_audit_time": "3 minutes"
  },
  "resource_usage": {
    "memory": {
      "used": "4.2 GB",
      "total": "8 GB",
      "usage_percent": 52.5,
      "status": "normal"
    },
    "cpu": {
      "usage_percent": 35,
      "status": "normal"
    },
    "disk": {
      "used": "120 GB",
      "total": "500 GB",
      "usage_percent": 24,
      "status": "normal"
    }
  },
  "alerts": [
    {
      "level": "warning",
      "type": "memory",
      "message": "内存使用率偏高",
      "timestamp": "2026-03-12T09:45:00"
    }
  ],
  "recommendations": [
    "建议监控内存使用",
    "建议优化任务队列"
  ]
}
```

### 5.2 报告生成器

```python
class HealthReportGenerator:
    """健康报告生成器"""
    
    def generate_report(self, report_type='hourly'):
        """生成健康报告"""
        
        report = {
            'timestamp': time.time(),
            'report_type': report_type,
            'system_health': self.generate_system_health(),
            'task_statistics': self.generate_task_statistics(),
            'audit_statistics': self.generate_audit_statistics(),
            'resource_usage': self.generate_resource_usage(),
            'alerts': self.get_active_alerts(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_system_health(self):
        """生成系统健康度"""
        
        agents = self.get_all_agents()
        
        healthy_count = 0
        warning_count = 0
        unhealthy_count = 0
        
        for agent in agents:
            status = agent['status']
            if status == 'healthy':
                healthy_count += 1
            elif status == 'warning':
                warning_count += 1
            else:
                unhealthy_count += 1
        
        # 计算健康分
        total = len(agents)
        health_score = (healthy_count * 100 + warning_count * 50) / total
        
        return {
            'status': 'healthy' if health_score >= 90 else 'warning' if health_score >= 70 else 'unhealthy',
            'score': health_score,
            'uptime': self.get_uptime(),
            'total_agents': total,
            'active_agents': len([a for a in agents if a['active']]),
            'healthy_agents': healthy_count,
            'warning_agents': warning_count,
            'unhealthy_agents': unhealthy_count
        }
```

---

## 六、配置与部署

### 6.1 配置文件

```yaml
# patrol-agent-config.yaml

patrol:
  # 监控配置
  monitoring:
    heartbeat_interval: 30  # 心跳间隔（秒）
    timeout_threshold: 90   # 超时阈值（秒）
    resource_check_interval: 60  # 资源检查间隔（秒）
    
  # 恢复配置
  recovery:
    max_retries: 3          # 最大重试次数
    retry_delay: 60         # 重试延迟（秒）
    auto_recovery_enabled: true  # 启用自动恢复
    
  # 报告配置
  report:
    hourly_report: true     # 每小时报告
    daily_report: true      # 每日报告
    report_recipients:      # 报告接收者
      - "admin@example.com"
      - "ops@example.com"
    
  # 监控对象
  monitored_agents:
    - "御坂美琴一号"
    - "御坂妹妹 10 号"
    - "御坂妹妹 11 号"
    - "御坂妹妹 12 号"
    - "御坂妹妹 13 号"
    - "御坂妹妹 14 号"
    - "御坂妹妹 15 号"
    - "御坂妹妹 16 号"
    - "御坂妹妹 17 号"
    - "御坂妹妹 18 号"
    # 19 号本身不需要监控自己
    
  # 阈值配置
  thresholds:
    memory_warning: 80      # 内存警告阈值（%）
    memory_critical: 90     # 内存严重阈值（%）
    cpu_warning: 70         # CPU 警告阈值（%）
    cpu_critical: 90        # CPU 严重阈值（%）
    task_timeout: 1800      # 任务超时阈值（秒）
```

### 6.2 部署脚本

```bash
#!/bin/bash
# deploy-patrol-agent.sh

# 1. 创建目录
mkdir -p /home/claw/.openclaw/workspace/tools/patrol

# 2. 复制文件
cp patrol/__init__.py /home/claw/.openclaw/workspace/tools/patrol/
cp patrol/monitor.py /home/claw/.openclaw/workspace/tools/patrol/
cp patrol/recovery.py /home/claw/.openclaw/workspace/tools/patrol/

# 3. 创建配置文件
cat > /home/claw/.openclaw/workspace/tools/patrol/config.yaml <<EOF
patrol:
  monitoring:
    heartbeat_interval: 30
    timeout_threshold: 90
EOF

# 4. 设置权限
chmod +x /home/claw/.openclaw/workspace/tools/patrol/*.py

# 5. 启动服务
nohup python3 /home/claw/.openclaw/workspace/tools/patrol/main.py > /var/log/patrol.log 2>&1 &

# 6. 设置开机启动
echo "@reboot /home/claw/.openclaw/workspace/tools/patrol/start.sh" | crontab -

echo "Patrol Agent 部署完成！"
```

---

## 七、日志格式

### 7.1 日志类型

```json
{
  "timestamp": "2026-03-12T10:00:00",
  "level": "INFO",
  "agent": "御坂妹妹 19 号",
  "type": "heartbeat",
  "message": "Agent 心跳正常",
  "data": {
    "agent_id": "御坂妹妹 11 号",
    "elapsed": 30.5,
    "memory_usage": 4.2,
    "cpu_usage": 35
  }
}
```

### 7.2 日志文件

```
/logs/patrol/
├── patrol.log           # 主日志
├── patrol.alert.log     # 告警日志
├── patrol.recovery.log  # 恢复日志
└── patrol.report.log    # 报告日志
```

---

## 八、总结

### 8.1 核心功能

| 功能 | 状态 | 说明 |
|------|------|------|
| **心跳检测** | ✅ | 监控 Agent 心跳 |
| **任务超时检测** | ✅ | 检测超时任务 |
| **资源监控** | ✅ | 监控系统资源 |
| **审核质量监控** | ✅ | 监控审核质量 |
| **自动恢复** | ✅ | 自动恢复异常 |
| **健康报告** | ✅ | 定期输出报告 |
| **日志记录** | ✅ | 记录所有操作 |

### 8.2 预期效果

| 指标 | 目标值 |
|------|--------|
| **系统可用性** | 99% |
| **异常发现时间** | < 1 分钟 |
| **自动恢复成功率** | 90% |
| **健康报告准确性** | 95% |

---

**御坂妹妹 19 号（Patrol Agent）设计文档完成！** ⚡
