# 御坂网络 V2 (Misaka Network V2)

> **御坂美琴本尊设计** | **版本：2.0.0**  
> 四角色闭环管理系统

---

## 📋 目录

1. [概述](#概述)
2. [核心架构](#核心架构)
3. [快速开始](#快速开始)
4. [API 文档](#api-文档)
5. [最佳实践](#最佳实践)
6. [版本历史](#版本历史)

---

## 概述

御坂网络 V2 是御坂美琴本尊设计的**四角色闭环管理系统**，在御坂网络第一代基础上增加了：

- ✅ **御坂妹妹 18 号** (Reviewer) - 质量审核
- ✅ **御坂妹妹 19 号** (Patrol) - 状态监控

**目标**：实现 95% 任务闭环率，100% 审核覆盖率

---

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    御坂大人                              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              御坂美琴一号 (Planner)                       │
│         - 任务接收、分解、分配、协调                      │
└─────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────┬───────────┬───────────┬───────────┐
        ↓           ↓           ↓           ↓           ↓
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ 御坂妹妹  │ │ 御坂妹妹  │ │ 御坂妹妹  │ │ 御坂妹妹  │
│  11-17 号  │ │  18 号     │ │  19 号     │ │  10 号     │
│(Executor) │ │(Reviewer) │ │(Patrol)  │ │(辅助规划) │
└───────────┘ └───────────┘ └───────────┘ └───────────┘
```

---

## 快速开始

### 1. 安装依赖

```bash
cd /home/claw/.openclaw/workspace/src/misaka-network-v2
pip install -e .
```

### 2. 基本使用

```python
from misaka_network_v2 import MisakaNetworkV2

# 创建网络实例
network = MisakaNetworkV2()

# 接收任务
task = network.receive_task("创建一个 Python 爬虫项目")
print(f"任务 ID: {task.task_id}")
print(f"任务描述：{task.description}")

# 分配任务
network.assign_task(task)
print(f"分配给：{task.executor}")

# 执行任务
result = network.execute_task(task.task_id)
print(f"执行结果：{result.result_type}")

# 提交审核
review_result = network.submit_for_review(task.task_id)
if review_result:
    print(f"审核结果：{review_result.decision}")
    print(f"得分：{review_result.total_score}/100")
    if review_result.feedback:
        print("审核反馈:")
        for feedback in review_result.feedback:
            print(f"  - {feedback}")

# 启动监控
network.start_monitoring()
print("监控已启动")

# 获取系统状态
summary = network.get_status_summary()
print(f"系统状态：{summary['network_status']}")
print(f"任务统计：{summary['planner']}")

# 获取任务历史
history = network.get_task_history()
print(f"任务历史：{len(history)} 条")

# 停止监控
network.stop_monitoring()
```

### 3. 完整工作流示例

```python
from misaka_network_v2 import MisakaNetworkV2

# 初始化
network = MisakaNetworkV2()

# 1. 接收任务
task = network.receive_task("分析股票数据并生成报告", priority="high")

# 2. 分配任务
network.assign_task(task)

# 3. 执行任务
result = network.execute_task(task.task_id)

# 4. 提交审核
review_result = network.submit_for_review(task.task_id)

# 5. 检查审核结果
if review_result.is_approved():
    print(f"✅ 审核通过，得分：{review_result.total_score}/100")
else:
    print(f"❌ 需要重做，得分：{review_result.total_score}/100")
    print("修改建议:")
    for feedback in review_result.feedback:
        print(f"  - {feedback}")
    
    # 手动触发恢复
    network.auto_recovery(task.task_id)

# 6. 监控系统状态
health = network.patrol.get_health_summary()
print(f"健康状态：{health}")

# 7. 获取任务历史
history = network.get_task_history(limit=5)
print(f"最近任务：{len(history)} 条")
```

---

## API 文档

### MisakaNetworkV2 类

#### 初始化
```python
network = MisakaNetworkV2()
```

#### 任务管理
- `receive_task(description, priority)` - 接收任务
- `assign_task(task)` - 分配任务
- `execute_task(task_id)` - 执行任务
- `submit_for_review(task_id)` - 提交审核
- `get_task_status(task_id)` - 获取任务状态
- `auto_recovery(task_id)` - 手动恢复

#### 监控管理
- `start_monitoring()` - 启动监控
- `stop_monitoring()` - 停止监控
- `get_status_summary()` - 获取状态摘要
- `get_task_history(limit)` - 获取任务历史
- `get_review_feedback(task_id)` - 获取审核反馈

### Planner 类

- `receive_task(description, priority)` - 接收任务
- `assign_task(task)` - 分配任务
- `decompose_task(task)` - 分解任务
- `get_task(task_id)` - 获取任务
- `get_all_tasks()` - 获取所有任务
- `get_status_summary()` - 获取状态摘要

### Reviewer 类

- `review(submission)` - 审核提交
- `get_review_stats()` - 获取审核统计
- `get_review_history(limit)` - 获取审核历史

### Patrol 类

- `start()` - 启动监控
- `stop()` - 停止监控
- `record_heartbeat(agent_id)` - 记录心跳
- `register_task(task_id, executor)` - 注册任务
- `update_task_state(task_id, status)` - 更新状态
- `get_health_summary()` - 获取健康摘要

---

## 最佳实践

### 1. 任务优先级管理

```python
# 高优先级任务
high_priority_task = network.receive_task("紧急修复安全漏洞", priority="high")

# 普通任务
normal_task = network.receive_task("优化代码结构", priority="normal")

# 低优先级任务
low_priority_task = network.receive_task("整理文档", priority="low")
```

### 2. 审核标准理解

御坂妹妹 18 号审核标准：

| 维度 | 权重 | 最高分 | 通过最低分 |
|------|------|--------|-----------|
| 闭环性 | 40% | 40 | 32 |
| 规范度 | 30% | 30 | 24 |
| 适配性 | 20% | 20 | 16 |
| 完整性 | 10% | 10 | 8 |
| **总分** | **100%** | **100** | **80** |

### 3. 监控配置

```python
# 自定义监控参数
patrol = Patrol(
    check_interval=60,      # 60 秒检查
    timeout_threshold=600   # 10 分钟超时
)

network.patrol = patrol
```

### 4. 错误处理

```python
try:
    result = network.execute_task(task_id)
    if result.result_type == "error":
        print(f"执行失败：{result.error}")
        # 触发自动恢复
        network.auto_recovery(task_id)
except Exception as e:
    print(f"系统错误：{e}")
```

---

## 版本历史

### v2.0.0 (2026-03-12)
- ✅ 新增御坂妹妹 18 号 (Reviewer)
- ✅ 新增御坂妹妹 19 号 (Patrol)
- ✅ 实现四角色完整架构
- ✅ 实现审核标准体系
- ✅ 实现自动恢复机制
- ✅ 完整 API 文档

### v1.0.0 (早期版本)
- ✅ 御坂妹妹 10-17 号分工体系
- ✅ 核心中枢 (御坂美琴一号) 调度机制
- ❌ 缺少审核机制
- ❌ 缺少状态监控

---

## 相关文件

- `research/misaka-network-v2-complete.md` - 完整设计方案
- `src/misaka-network-v2/` - 源代码
- `tests/` - 测试代码

---

**御坂网络 V2** - 持续学习进化系统 ⚡
