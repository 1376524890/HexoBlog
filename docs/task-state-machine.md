# 任务状态机详细设计

> **文档版本**: v2.0  
> **创建时间**: 2026-03-12  
> **作者**: 御坂妹妹 11 号  
> **用途**: 御坂网络 V2 任务状态机实现

---

## 一、状态机架构

### 1.1 状态定义

```python
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

class TaskStatus(Enum):
    """任务状态枚举"""
    
    PENDING = "pending"         # 待分配
    ASSIGNED = "assigned"       # 已分配
    IN_PROGRESS = "in_progress" # 执行中
    REVIEW = "review"           # 审核中
    DONE = "done"               # 完成
    RWORK = "rework"            # 重做
    CANCELLED = "cancelled"     # 已取消
```

### 1.2 状态转换规则

```python
class StateMachine:
    """任务状态机"""
    
    # 状态转换表
    TRANSITIONS = {
        TaskStatus.PENDING: [TaskStatus.ASSIGNED, TaskStatus.CANCELLED],
        TaskStatus.ASSIGNED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
        TaskStatus.IN_PROGRESS: [TaskStatus.REVIEW, TaskStatus.CANCELLED],
        TaskStatus.REVIEW: [TaskStatus.DONE, TaskStatus.REWORK],
        TaskStatus.REWORK: [TaskStatus.ASSIGNED],
        TaskStatus.DONE: [],
        TaskStatus.CANCELLED: [],
    }
    
    def __init__(self):
        self.current_state = TaskStatus.PENDING
        self.history = []
    
    def can_transition(self, from_state: TaskStatus, to_state: TaskStatus) -> bool:
        """检查状态转换是否合法"""
        
        valid_transitions = self.TRANSITIONS.get(from_state, [])
        return to_state in valid_transitions
    
    def transition(self, from_state: TaskStatus, to_state: TaskStatus) -> bool:
        """执行状态转换"""
        
        if not self.can_transition(from_state, to_state):
            raise ValueError(
                f"Invalid state transition: {from_state.value} -> {to_state.value}"
            )
        
        # 记录历史
        self.history.append({
            'from': from_state.value,
            'to': to_state.value,
            'timestamp': datetime.now()
        })
        
        # 更新状态
        self.current_state = to_state
        
        return True
```

---

## 二、Task 类设计

### 2.1 任务数据结构

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class Task:
    """任务数据模型"""
    
    # 基本信息
    id: str                           # 任务 ID
    title: str                        # 任务标题
    description: str                  # 任务描述
    status: TaskStatus = TaskStatus.PENDING  # 任务状态
    
    # 时间信息
    created_at: datetime              # 创建时间
    updated_at: datetime              # 更新时间
    assigned_at: Optional[datetime]   # 分配时间
    started_at: Optional[datetime]    # 开始时间
    completed_at: Optional[datetime]  # 完成时间
    
    # 负责人信息
    assigned_to: Optional[str]        # 负责人（御坂妹妹 ID）
    reviewer: Optional[str] = None    # 审核人（御坂妹妹 18 号）
    
    # 任务类型
    task_type: str                    # 任务类型（code/content/research 等）
    priority: str = "normal"          # 优先级（low/normal/high/critical）
    
    # 任务要求
    requirements: str                 # 任务要求
    acceptance_criteria: List[str]    # 验收标准
    
    # 成果信息
    deliverables: List[Dict[str, Any]] = None  # 交付成果
    audit_results: List[Dict[str, Any]] = None # 审核结果
    
    # 元数据
    metadata: Dict[str, Any] = None   # 元数据
    tags: List[str] = None            # 标签
    
    def __post_init__(self):
        """初始化后处理"""
        if self.deliverables is None:
            self.deliverables = []
        if self.audit_results is None:
            self.audit_results = []
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = []
    
    def get_elapsed_time(self) -> float:
        """获取已耗时（秒）"""
        
        if self.status == TaskStatus.PENDING:
            return (datetime.now() - self.created_at).total_seconds()
        elif self.status == TaskStatus.ASSIGNED:
            return (datetime.now() - self.assigned_at).total_seconds() if self.assigned_at else 0
        elif self.status == TaskStatus.IN_PROGRESS:
            return (datetime.now() - self.started_at).total_seconds() if self.started_at else 0
        elif self.status == TaskStatus.REVIEW:
            return (datetime.now() - self.updated_at).total_seconds()
        else:
            return 0
    
    def is_overdue(self, timeout_seconds: float = 30 * 60) -> bool:
        """检查是否超时"""
        
        elapsed = self.get_elapsed_time()
        return elapsed > timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'assigned_to': self.assigned_to,
            'reviewer': self.reviewer,
            'task_type': self.task_type,
            'priority': self.priority,
            'requirements': self.requirements,
            'acceptance_criteria': self.acceptance_criteria,
            'deliverables': self.deliverables,
            'audit_results': self.audit_results,
            'metadata': self.metadata,
            'tags': self.tags,
        }
```

---

## 三、TaskManager 实现

### 3.1 任务管理器

```python
class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.state_machine = StateMachine()
    
    def create_task(self, task: Task) -> Task:
        """创建任务"""
        
        # 设置创建时间
        if not task.created_at:
            task.created_at = datetime.now()
        
        # 保存到存储
        self.tasks[task.id] = task
        
        return task
    
    def assign_task(self, task_id: str, executor: str) -> Task:
        """分配任务"""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        # 状态转换
        self.state_machine.transition(TaskStatus.PENDING, TaskStatus.ASSIGNED)
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = datetime.now()
        task.assigned_to = executor
        
        return task
    
    def start_task(self, task_id: str) -> Task:
        """开始任务"""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.ASSIGNED:
            raise ValueError(f"Task cannot start from status: {task.status.value}")
        
        # 状态转换
        self.state_machine.transition(TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS)
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        return task
    
    def submit_for_review(self, task_id: str, deliverables: List[Dict[str, Any]]) -> Task:
        """提交审核"""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Task cannot submit for review from status: {task.status.value}")
        
        # 添加交付成果
        task.deliverables.extend(deliverables)
        
        # 状态转换
        self.state_machine.transition(TaskStatus.IN_PROGRESS, TaskStatus.REVIEW)
        task.status = TaskStatus.REVIEW
        task.updated_at = datetime.now()
        
        return task
    
    def complete_task(self, task_id: str, audit_result: Dict[str, Any]) -> Task:
        """完成任务"""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.REVIEW:
            raise ValueError(f"Task cannot complete from status: {task.status.value}")
        
        # 添加审核结果
        task.audit_results.append(audit_result)
        
        # 状态转换
        self.state_machine.transition(TaskStatus.REVIEW, TaskStatus.DONE)
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now()
        
        return task
    
    def rework_task(self, task_id: str, audit_result: Dict[str, Any]) -> Task:
        """重做任务"""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.REVIEW:
            raise ValueError(f"Task cannot rework from status: {task.status.value}")
        
        # 添加审核结果
        task.audit_results.append(audit_result)
        
        # 状态转换
        self.state_machine.transition(TaskStatus.REVIEW, TaskStatus.REWORK)
        task.status = TaskStatus.REWORK
        task.updated_at = datetime.now()
        
        return task
```

---

## 四、任务生命周期管理

### 4.1 生命周期控制器

```python
class TaskLifeCycleManager:
    """任务生命周期管理器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.timeout_thresholds = {
            TaskStatus.ASSIGNED: 60 * 60,      # 1 小时
            TaskStatus.IN_PROGRESS: 30 * 60,   # 30 分钟
            TaskStatus.REVIEW: 10 * 60,        # 10 分钟
        }
    
    def check_timeouts(self):
        """检查超时任务"""
        
        timeout_tasks = []
        
        for task in self.task_manager.tasks.values():
            if task.status in self.timeout_thresholds:
                timeout = self.timeout_thresholds[task.status]
                if task.is_overdue(timeout):
                    timeout_tasks.append(task)
        
        return timeout_tasks
    
    def handle_timeout(self, task: Task):
        """处理超时任务"""
        
        # 记录日志
        print(f"Task timeout: {task.id}")
        
        # 根据当前状态处理
        if task.status == TaskStatus.ASSIGNED:
            # 超时未开始 - 重新分配
            self.reassign_task(task)
        
        elif task.status == TaskStatus.IN_PROGRESS:
            # 超时未完成 - 标记为失败
            self.mark_task_failed(task, 'timeout')
        
        elif task.status == TaskStatus.REVIEW:
            # 审核超时 - 自动通过
            self.auto_approve_task(task)
    
    def reassign_task(self, task: Task):
        """重新分配任务"""
        
        # 1. 取消当前分配
        task.assigned_to = None
        
        # 2. 重置状态
        self.task_manager.state_machine.transition(
            TaskStatus.ASSIGNED,
            TaskStatus.PENDING
        )
        task.status = TaskStatus.PENDING
        
        # 3. 记录日志
        print(f"Task reassign: {task.id}")
    
    def mark_task_failed(self, task: Task, reason: str):
        """标记任务失败"""
        
        # 添加审核结果
        audit_result = {
            'passed': False,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        task.audit_results.append(audit_result)
        
        # 设置状态为完成（带失败标记）
        self.task_manager.state_machine.transition(
            TaskStatus.IN_PROGRESS,
            TaskStatus.DONE
        )
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now()
        
        print(f"Task marked failed: {task.id}, reason: {reason}")
    
    def auto_approve_task(self, task: Task):
        """自动批准审核"""
        
        # 添加审核结果
        audit_result = {
            'passed': True,
            'reason': 'auto_approve_timeout',
            'timestamp': datetime.now().isoformat()
        }
        
        task.audit_results.append(audit_result)
        
        # 设置状态为完成
        self.task_manager.state_machine.transition(
            TaskStatus.REVIEW,
            TaskStatus.DONE
        )
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now()
        
        print(f"Task auto-approved: {task.id}")
```

---

## 五、状态监控

### 5.1 状态监控器

```python
class TaskStatusMonitor:
    """任务状态监控器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.history = []
    
    def get_status_summary(self) -> Dict[str, int]:
        """获取状态统计"""
        
        summary = {
            TaskStatus.PENDING.value: 0,
            TaskStatus.ASSIGNED.value: 0,
            TaskStatus.IN_PROGRESS.value: 0,
            TaskStatus.REVIEW.value: 0,
            TaskStatus.DONE.value: 0,
            TaskStatus.REWORK.value: 0,
            TaskStatus.CANCELLED.value: 0,
        }
        
        for task in self.task_manager.tasks.values():
            summary[task.status.value] += 1
        
        return summary
    
    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务历史"""
        
        if task_id not in self.task_manager.tasks:
            return []
        
        task = self.task_manager.tasks[task_id]
        return task.state_machine.history
    
    def monitor_state_changes(self):
        """监控状态变化"""
        
        for task in self.task_manager.tasks.values():
            current_state = task.status
            
            # 检查是否需要处理
            if current_state == TaskStatus.ASSIGNED and not task.started_at:
                # 分配后未开始
                self.history.append({
                    'type': 'assigned_no_start',
                    'task_id': task.id,
                    'timestamp': datetime.now()
                })
            
            elif current_state == TaskStatus.IN_PROGRESS:
                # 执行中 - 检查耗时
                elapsed = task.get_elapsed_time()
                if elapsed > 1800:  # 30 分钟
                    self.history.append({
                        'type': 'long_running',
                        'task_id': task.id,
                        'elapsed': elapsed,
                        'timestamp': datetime.now()
                    })
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """获取告警信息"""
        
        alerts = []
        summary = self.get_status_summary()
        
        # 检查长时间未完成的任务
        if summary[TaskStatus.IN_PROGRESS.value] > 10:
            alerts.append({
                'type': 'high_in_progress',
                'message': f'执行中任务过多：{summary[TaskStatus.IN_PROGRESS.value]}个',
                'severity': 'warning'
            })
        
        # 检查审核队列
        if summary[TaskStatus.REVIEW.value] > 5:
            alerts.append({
                'type': 'review_queue_backlog',
                'message': f'审核队列积压：{summary[TaskStatus.REVIEW.value]}个',
                'severity': 'warning'
            })
        
        return alerts
```

---

## 六、使用示例

### 6.1 创建任务

```python
# 创建任务
task = Task(
    id="TASK-20260312-001",
    title="实现代码审核功能",
    description="实现御坂网络代码审核功能",
    task_type="code",
    priority="high",
    requirements="实现代码静态分析、合规检查等功能",
    acceptance_criteria=[
        "代码分析功能正常",
        "合规检查结果准确",
        "性能达标"
    ]
)

# 添加到任务管理器
task_manager.create_task(task)
```

### 6.2 分配任务

```python
# 分配给御坂妹妹 11 号
task_manager.assign_task("TASK-20260312-001", "御坂妹妹 11 号")
```

### 6.3 执行任务

```python
# 开始任务
task_manager.start_task("TASK-20260312-001")

# 执行完成后提交审核
task_manager.submit_for_review(
    "TASK-20260312-001",
    deliverables=[
        {
            'type': 'code',
            'file': 'reviewer.py',
            'content': '...'
        }
    ]
)
```

### 6.4 审核任务

```python
# 审核通过
audit_result = {
    'passed': True,
    'score': 87.2,
    'feedback': '审核通过',
    'suggestions': []
}

task_manager.complete_task("TASK-20260312-001", audit_result)
```

---

## 七、数据库持久化

### 7.1 数据模型

```python
from sqlalchemy import Column, String, DateTime, Integer, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TaskDB(Base):
    """任务数据库模型"""
    
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, nullable=False)
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    assigned_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    assigned_to = Column(String)
    reviewer = Column(String)
    task_type = Column(String)
    priority = Column(String)
    
    requirements = Column(String)
    acceptance_criteria = Column(JSON)
    deliverables = Column(JSON)
    audit_results = Column(JSON)
    metadata = Column(JSON)
    tags = Column(JSON)
```

---

**任务状态机详细设计完成！** ⚡
