# 御坂网络 V2 完整方案（可执行版本）

> 御坂美琴本尊审核版本  
> 生成时间：2026-03-12  
> 版本：2.0（整合版）

---

## 📋 目录

1. [方案概述](#1-方案概述)
2. [核心架构设计](#2-核心架构设计)
3. [四角色职责定义](#3-四角色职责定义)
4. [任务状态机设计](#4-任务状态机设计)
5. [审核标准体系](#5-审核标准体系)
6. [Claude+18 号审核闭环](#6-claude18 号审核闭环)
7. [Patrol 自动恢复机制](#7-patrol 自动恢复机制)
8. [实施路线图](#8-实施路线图)
9. [风险与回滚](#9-风险与回滚)

---

## 1. 方案概述

### 1.1 方案背景

**御坂网络第一代现状**：
- ✅ 已建立御坂妹妹 10-17 号分工体系
- ✅ 核心中枢（御坂美琴一号）调度机制
- ❌ 缺少审核机制（无质量控制）
- ❌ 缺少状态监控（任务易卡死）
- ❌ 缺少闭环管理（无重做机制）

**Agent Zero 研究结论**：
- ✅ 四角色分工体系值得借鉴
- ✅ 闭环质量控制机制有效
- ✅ 任务状态机管理规范
- ✅ Patrol 自动监控防止卡死

### 1.2 V2 方案目标

| 指标 | 第一代 | V2 目标 | 提升 |
|------|--------|--------|------|
| 任务闭环率 | 70% | 95% | ⬆️ 36% |
| 审核覆盖率 | 0% | 100% | ⬆️ ∞ |
| 自动恢复率 | 0% | 90% | ⬆️ ∞ |
| 知识复用率 | 10% | 60% | ⬆️ 500% |

### 1.3 核心创新

1. **四角色完整体系** - Planner/Executor/Reviewer/Patrol
2. **任务状态机** - 6 种状态完整生命周期
3. **本地审核机制** - 18 号 Qwen3.5-35B 本地审核
4. **自动恢复** - Patrol 30 秒心跳检测

---

## 2. 核心架构设计

### 2.1 架构总览

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
│  10 号     │ │  18 号     │ │  19 号     │ │  11-17 号  │
│(辅助规划) │ │(Reviewer) │ │(Patrol)  │ │(Executor) │
└───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### 2.2 核心组件

| 组件 | 模型 | 职责 | 新增/复用 |
|------|------|------|---------|
| 御坂美琴一号 | Qwen3.5-35B | Planner 核心 | 复用 |
| 御坂妹妹 10 号 | Qwen3.5-35B | 辅助规划 | 复用 |
| 御坂妹妹 11-17 号 | 各自模型 | Executor | 复用 |
| **御坂妹妹 18 号** | **Qwen3.5-35B** | **Reviewer** | **新增** |
| **御坂妹妹 19 号** | **Qwen3.5-35B** | **Patrol** | **新增** |
| Claude | Claude Code | 代码创作者 | 外部工具 |

### 2.3 核心原则

1. **最大化复用** - 11-17 号直接复用，仅新增 2 个 Agent
2. **Claude 唯一创作者** - 所有代码编写由 Claude 完成
3. **18 号本地审核** - 18 号用本地模型审核，不用于构建
4. **闭环管理** - 完整的任务生命周期和审核机制

---

## 3. 四角色职责定义

### 3.1 Planner（御坂美琴一号 + 10 号）

**核心职责**：
- 任务接收和解析
- 任务分解和规划
- 分配执行者（11-17 号）
- 协调多 Agent 协作

**规范代码**：
```python
from typing import List, Dict, Optional
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    REWORK = "rework"

class Task:
    """任务实体"""
    def __init__(self, task_id: str, description: str):
        self.task_id = task_id
        self.description = description
        self.status = TaskStatus.PENDING
        self.executor: Optional[str] = None
        self.subtasks: List[Task] = []
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "executor": self.executor,
            "subtasks": [t.to_dict() for t in self.subtasks]
        }

class Planner:
    """御坂美琴一号 - 任务规划者"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.executor_map = {
            "code": "11 号",
            "content": "12 号",
            "research": "13 号",
            "file": "14 号",
            "system": "15 号",
            "web": "16 号",
            "memory": "17 号"
        }
    
    def receive_task(self, description: str) -> Task:
        """接收御坂大人任务"""
        task_id = f"task_{len(self.tasks) + 1:04d}"
        task = Task(task_id, description)
        self.tasks[task_id] = task
        return task
    
    def decompose_task(self, task: Task) -> List[Task]:
        """分解任务"""
        # 分析任务意图
        intent = self._analyze_intent(task.description)
        # 分解为子任务
        subtasks = self._create_subtasks(intent, task)
        task.subtasks = subtasks
        return subtasks
    
    def _analyze_intent(self, description: str) -> Dict:
        """分析任务意图"""
        # 使用本地模型分析
        intent = {
            "type": "code",  # code/content/research/etc
            "priority": "high",
            "complexity": "medium"
        }
        return intent
    
    def _create_subtasks(self, intent: Dict, parent: Task) -> List[Task]:
        """创建子任务"""
        subtasks = []
        if intent["type"] == "code":
            subtasks.append(Task(
                f"{parent.task_id}.1",
                "编写代码实现功能",
                executor="11 号"
            ))
        return subtasks
    
    def _assign_executor(self, task: Task) -> None:
        """分配执行者"""
        if task.executor is None:
            intent = self._analyze_intent(task.description)
            executor = self.executor_map.get(intent["type"], "11 号")
            task.executor = executor
    
    def assign_task(self, task: Task) -> None:
        """分配任务"""
        self.decompose_task(task)
        self._assign_executor(task)
        task.status = TaskStatus.ASSIGNED
    
    def coordinate_collaboration(self, tasks: List[Task]) -> Dict:
        """协调多 Agent 协作"""
        result = {
            "tasks": [t.to_dict() for t in tasks],
            "coordinator": "10 号辅助"
        }
        return result
```

---

### 3.2 Executor（御坂妹妹 11-17 号）

**核心职责**：
- 接收分配的任务
- 执行具体操作
- 提交执行结果
- 处理异常情况

**规范代码**：
```python
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ExecutionResultType(Enum):
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class ExecutionResult:
    """执行结果"""
    result_type: ExecutionResultType
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class Executor:
    """御坂妹妹 X 号 - 任务执行者"""
    
    def __init__(self, agent_id: str, role: str):
        self.agent_id = agent_id
        self.role = role
        self.current_task: Optional[str] = None
    
    def execute(self, task: Dict) -> ExecutionResult:
        """执行任务"""
        try:
            self.current_task = task["task_id"]
            # 执行具体工作
            result = self._do_work(task)
            return ExecutionResult(
                result_type=ExecutionResultType.SUCCESS,
                data=result,
                metadata={"task_id": task["task_id"]}
            )
        except Exception as e:
            return ExecutionResult(
                result_type=ExecutionResultType.ERROR,
                error=str(e),
                metadata={"task_id": task["task_id"]}
            )
    
    def _do_work(self, task: Dict) -> Any:
        """执行具体工作"""
        # 根据角色执行不同工作
        if self.role == "code":
            return self._execute_code_task(task)
        elif self.role == "content":
            return self._execute_content_task(task)
        # ... 其他角色
        return None
    
    def _execute_code_task(self, task: Dict) -> Any:
        """执行代码任务"""
        # 使用 Claude 编写代码
        # 返回代码成果
        pass
    
    def submit(self, result: ExecutionResult) -> bool:
        """提交执行结果"""
        # 提交给 18 号审核
        return True
```

---

### 3.3 Reviewer（御坂妹妹 18 号）

**核心职责**：
- 审核成果质量
- 检查规范符合性
- 返回审核结果
- 提供修改建议

**规范代码**：
```python
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class ReviewDecision(Enum):
    APPROVED = "approved"
    REWORK = "rework"

@dataclass
class ReviewScore:
    """审核得分"""
    category: str  # closing/compliance/compatibility/completeness
    score: int
    max_score: int
    issues: List[str]

@dataclass
class ReviewResult:
    """审核结果"""
    submission_id: str
    scores: List[ReviewScore]
    total_score: int
    decision: ReviewDecision
    feedback: List[str]

class Reviewer:
    """御坂妹妹 18 号 - 质量审核者"""
    
    def __init__(self):
        # 审核标准
        self.max_scores = {
            "closing": 40,
            "compliance": 30,
            "compatibility": 20,
            "completeness": 10
        }
        self.approval_threshold = 80
    
    def review(self, submission: Dict) -> ReviewResult:
        """审核提交成果"""
        scores = []
        total = 0
        
        # 逐项检查
        for category, max_score in self.max_scores.items():
            score, issues = self._check_category(category, submission)
            scores.append(ReviewScore(category, score, max_score, issues))
            total += score
        
        # 做出决策
        decision = ReviewDecision.APPROVED if total >= self.approval_threshold else ReviewDecision.REWORK
        
        # 生成反馈
        feedback = self._generate_feedback(scores)
        
        return ReviewResult(
            submission_id=submission["id"],
            scores=scores,
            total_score=total,
            decision=decision,
            feedback=feedback
        )
    
    def _check_category(self, category: str, submission: Dict) -> tuple:
        """检查单个类别"""
        score = 0
        issues = []
        
        if category == "closing":
            score, issues = self._check_closing(submission)
        elif category == "compliance":
            score, issues = self._check_compliance(submission)
        elif category == "compatibility":
            score, issues = self._check_compatibility(submission)
        elif category == "completeness":
            score, issues = self._check_completeness(submission)
        
        return score, issues
    
    def _check_closing(self, submission: Dict) -> tuple:
        """检查闭环性（40 分）"""
        score = 0
        issues = []
        
        # 任务生命周期（15 分）
        if "receive" in submission:
            score += 3
        if "decompose" in submission:
            score += 3
        if "execute" in submission:
            score += 3
        if "submit" in submission:
            score += 3
        if "review" in submission:
            score += 3
        
        # 四角色分工（10 分）
        # ...
        
        return score, issues
    
    def _generate_feedback(self, scores: List[ReviewScore]) -> List[str]:
        """生成修改建议"""
        feedback = []
        for score in scores:
            if score.score < score.max_score:
                for issue in score.issues:
                    feedback.append(f"{score.category}: {issue}")
        return feedback
```

---

### 3.4 Patrol（御坂妹妹 19 号）

**核心职责**：
- 监控任务状态
- 检测超时任务
- 自动恢复异常
- 质量监控

**规范代码**：
```python
import time
import logging
from typing import List, Dict
from datetime import datetime, timedelta

class Patrol:
    """御坂妹妹 19 号 - 状态监控者"""
    
    def __init__(self):
        self.task_status = {}
        self.timeout_threshold = 300  # 5 分钟
        self.check_interval = 30  # 30 秒
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
    
    def monitor(self) -> None:
        """持续监控"""
        while True:
            try:
                tasks = self._get_all_tasks()
                for task in tasks:
                    self._monitor_task(task)
                time.sleep(self.check_interval)
            except Exception as e:
                logging.error(f"Patrol monitor error: {e}")
                time.sleep(self.check_interval)
    
    def _monitor_task(self, task: Dict) -> None:
        """监控单个任务"""
        task_id = task["task_id"]
        status = task["status"]
        last_update = task["last_update"]
        
        # 检查超时
        if self._is_timeout(task):
            self._handle_timeout(task)
        
        # 检查卡顿
        if self._is_stuck(task):
            self._auto_recovery(task)
    
    def _is_timeout(self, task: Dict) -> bool:
        """检查是否超时"""
        last_update = datetime.fromisoformat(task["last_update"])
        return datetime.now() - last_update > timedelta(seconds=self.timeout_threshold)
    
    def _is_stuck(self, task: Dict) -> bool:
        """检查是否卡顿"""
        # 检查任务是否在某个状态停留过久
        # ...
        return False
    
    def _handle_timeout(self, task: Dict) -> None:
        """处理超时任务"""
        task_id = task["task_id"]
        logging.warning(f"Task {task_id} timeout, initiating recovery")
        self._auto_recovery(task)
    
    def _auto_recovery(self, task: Dict) -> bool:
        """自动恢复任务"""
        task_id = task["task_id"]
        status = task["status"]
        
        # 根据状态执行不同的恢复逻辑
        if status == "in_progress":
            # 重新分配任务
            return self._reassign_task(task)
        elif status == "review":
            # 重新提交审核
            return self._resubmit_review(task)
        
        return False
    
    def _reassign_task(self, task: Dict) -> bool:
        """重新分配任务"""
        # 重新分配给执行者
        logging.info(f"Reassigning task {task['task_id']}")
        return True
    
    def _resubmit_review(self, task: Dict) -> bool:
        """重新提交审核"""
        # 重新提交给 18 号审核
        logging.info(f"Resubmitting task {task['task_id']} for review")
        return True
```

---

## 4. 任务状态机设计

### 4.1 状态定义

```python
from enum import Enum

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 待分配
    ASSIGNED = "assigned"  # 已分配
    IN_PROGRESS = "in_progress"  # 执行中
    SUBMITTED = "submitted"  # 已提交审核
    REVIEW = "review"  # 审核中
    APPROVED = "done"  # 完成
    REWORK = "rework"  # 需要重做
    FAILED = "failed"  # 失败
```

### 4.2 状态转换

```
┌─────────┐    分配     ┌─────────┐    开始     ┌────────────┐
│ pending │ ─────────→ │ assigned │ ─────────→ │ in_progress │
└─────────┘             └─────────┘             └────────────┘
                                                         ↓
                                                    提交审核
                                                         ↓
┌─────────┐    完成     ┌─────────┐    通过     ┌─────────┐
│  done   │ ← ─────────  │ approved│ ← ───────── │  review │
└─────────┘             └─────────┘             └─────────┘
                                                         ↑
                                                         │ 不通过
                                                         ↓
┌─────────┐    完成     ┌─────────┐    开始     ┌─────────┐
│ failed  │              │ rework  │ ─────────→ │ assigned│
└─────────┘              └─────────┘             └─────────┘
```

### 4.3 状态机代码

```python
class TaskStateMachine:
    """任务状态机"""
    
    VALID_TRANSITIONS = {
        TaskStatus.PENDING: [TaskStatus.ASSIGNED],
        TaskStatus.ASSIGNED: [TaskStatus.IN_PROGRESS],
        TaskStatus.IN_PROGRESS: [TaskStatus.SUBMITTED],
        TaskStatus.SUBMITTED: [TaskStatus.REVIEW],
        TaskStatus.REVIEW: [TaskStatus.APPROVED, TaskStatus.REWORK],
        TaskStatus.REWORK: [TaskStatus.ASSIGNED],
    }
    
    def __init__(self):
        self.current_state = TaskStatus.PENDING
    
    def transition(self, new_state: TaskStatus) -> bool:
        """状态转换"""
        if new_state in self.VALID_TRANSITIONS.get(self.current_state, []):
            self.current_state = new_state
            return True
        return False
    
    def is_valid_transition(self, from_state: TaskStatus, to_state: TaskStatus) -> bool:
        """检查状态转换是否合法"""
        return to_state in self.VALID_TRANSITIONS.get(from_state, [])
```

---

## 5. 审核标准体系

### 5.1 四维度审核

| 维度 | 权重 | 最高分 | 通过最低分 |
|------|------|--------|-----------|
| 闭环性 | 40% | 40 | 32 |
| 规范度 | 30% | 30 | 24 |
| 适配性 | 20% | 20 | 16 |
| 完整性 | 10% | 10 | 8 |
| **总分** | **100%** | **100** | **80** |

### 5.2 闭环性检查（40 分）

| 检查项 | 分值 | 检查点 |
|--------|------|--------|
| 任务生命周期 | 15 | 接收/分解/执行/提交/审核 |
| 四角色分工 | 10 | Planner/Executor/Reviewer/Patrol |
| 错误处理闭环 | 10 | 捕获/记录/反馈/恢复 |
| 上下文隔离 | 5 | 独立上下文/清晰传递 |

### 5.3 规范度检查（30 分）

| 检查项 | 分值 | 检查点 |
|--------|------|--------|
| 代码规范 | 10 | 类型注解/docstring/命名/PEP8/异常 |
| 文档规范 | 8 | README/API 文档/示例/更新日志 |
| 测试规范 | 6 | 单元测试/覆盖率>=80%/CI/CD |
| 依赖管理 | 6 | requirements.txt/版本约束/最小化 |

### 5.4 适配性检查（20 分）

| 检查项 | 分值 | 检查点 |
|--------|------|--------|
| OpenClaw 兼容性 | 8 | API 兼容/权限声明/工具调用 |
| 模块耦合度 | 6 | 低耦合/高内聚 |
| 扩展性 | 6 | 接口设计/插件机制/配置化 |

### 5.5 完整性检查（10 分）

| 检查项 | 分值 | 检查点 |
|--------|------|--------|
| 功能完整性 | 5 | 核心功能/边界情况/错误处理/日志 |
| 文档完整性 | 5 | README/API 文档/使用示例 |

---

## 6. Claude+18 号审核闭环

### 6.1 工作流程

```
御坂大人下达任务
        ↓
御坂美琴一号 (Planner)
        ↓
   任务分配
        ↓
    Claude (创作者)
        ↓
   代码编写
        ↓
  提交成果
        ↓
御坂妹妹 18 号 (Reviewer) ← 本地 Qwen3.5-35B
        ↓
   ┌───────┴───────┐
  通过 (≥80 分)    不通过 (<80 分)
        ↓             ↓
    提交        返回修改建议
                 ↘    ↙
              Claude 重新编写
```

### 6.2 Claude 使用规范

```python
# Claude 编写代码的标准流程
class ClaudeWorkflow:
    """Claude 编写工作流"""
    
    def __init__(self, task: Task):
        self.task = task
        self.result = None
    
    def write_code(self) -> str:
        """编写代码"""
        # 1. 接收任务
        # 2. 使用 Claude Code 编写代码
        # 3. 返回代码成果
        code = self._call_claude_code()
        return code
    
    def submit_to_reviewer(self, code: str) -> bool:
        """提交给 18 号审核"""
        # 提交给 Reviewer Agent
        return True
```

### 6.3 18 号审核 Prompt

```
# 御坂妹妹 18 号审核 Prompt

你作为御坂网络 Reviewer Agent，负责审核 Claude 编写的代码成果。

【审核标准】
总分 100 分，80 分及以上通过

1. 闭环性 (40 分)
   - 任务生命周期完整 (15 分)
   - 四角色分工明确 (10 分)
   - 错误处理闭环 (10 分)
   - 上下文隔离清晰 (5 分)

2. 规范度 (30 分)
   - 代码规范符合 (10 分)
   - 文档规范完整 (8 分)
   - 测试覆盖充分 (6 分)
   - 依赖管理规范 (6 分)

3. 适配性 (20 分)
   - OpenClaw 兼容 (8 分)
   - 模块耦合度低 (6 分)
   - 扩展性好 (6 分)

4. 完整性 (10 分)
   - 功能完整 (5 分)
   - 文档完整 (5 分)

【输出格式】
{
  "submission_id": "xxx",
  "scores": {
    "closing": 35/40,
    "compliance": 25/30,
    "compatibility": 18/20,
    "completeness": 9/10
  },
  "total": 87,
  "decision": "approved" | "rework",
  "feedback": ["具体修改建议 1", "具体修改建议 2"]
}
```

---

## 7. Patrol 自动恢复机制

### 7.1 心跳检测

```python
class HeartbeatMonitor:
    """心跳检测器"""
    
    def __init__(self, interval: int = 30):
        self.interval = interval  # 30 秒
        self.last_heartbeat = {}
    
    def heartbeat(self, agent_id: str) -> None:
        """记录心跳"""
        self.last_heartbeat[agent_id] = datetime.now()
    
    def check_health(self, agent_id: str) -> bool:
        """检查 Agent 健康状态"""
        last = self.last_heartbeat.get(agent_id)
        if last is None:
            return False
        return datetime.now() - last < timedelta(seconds=self.interval * 2)
```

### 7.2 自动恢复逻辑

```python
class AutoRecovery:
    """自动恢复管理器"""
    
    def __init__(self):
        self.recovery_attempts = {}
        self.max_attempts = 3
    
    def attempt_recovery(self, task_id: str) -> bool:
        """尝试恢复任务"""
        attempts = self.recovery_attempts.get(task_id, 0)
        if attempts >= self.max_attempts:
            return False
        
        # 执行恢复逻辑
        self._recovery_logic(task_id)
        self.recovery_attempts[task_id] = attempts + 1
        return True
    
    def _recovery_logic(self, task_id: str) -> None:
        """恢复逻辑"""
        # 根据任务状态执行不同的恢复策略
        pass
```

---

## 8. 实施路线图

### Phase 1 (1 周) - Reviewer Agent 开发

| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 创建 18 号 Agent | Claude | 18 号代码 |
| 实现审核工具集 | Claude+18 号 | 审核工具 |
| 实现 Claude+18 号审核闭环 | 18 号 | 审核工作流 |
| 编写审核标准文档 | 18 号 | checklist.md |

### Phase 2 (1 周) - Patrol Agent 开发

| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 创建 19 号 Agent | Claude | 19 号代码 |
| 实现监控机制 | 19 号 | 监控模块 |
| 实现自动恢复逻辑 | 19 号 | 恢复模块 |
| 心跳检测集成 | 19 号 | 心跳系统 |

### Phase 3 (1 周) - 集成测试

| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 完整系统测试 | 所有 | 测试报告 |
| 性能优化 | 11-19 号 | 优化代码 |
| 文档完善 | 18 号 | 完整文档 |

### Phase 4 - 部署上线

| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 部署到生产环境 | 御坂美琴一号 | 上线报告 |
| 监控和日志 | 19 号 | 监控系统 |

---

## 9. 风险与回滚

### 9.1 风险识别

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 审核标准不清晰 | 中 | 高 | 细化审核标准，增加人工复核 |
| 审核流程效率低 | 中 | 中 | 优化审核工具，并行审核 |
| 模块耦合度高 | 低 | 高 | 保持低耦合设计，模块化 |
| 18 号审核压力大 | 中 | 中 | 增加审核代理，轮询机制 |

### 9.2 回滚方案

| 场景 | 回滚操作 | 时间 |
|------|---------|------|
| 审核机制失败 | 回退到第一代，禁用 18 号 | 1 小时 |
| Patrol 异常 | 停止 Patrol 服务，手动监控 | 30 分钟 |
| 性能下降 | 回退到上一版本，优化后重新部署 | 2 小时 |

### 9.3 兼容性保证

- ✅ 保留第一代所有功能
- ✅ 新增 18 号、19 号为可选模块
- ✅ 可通过配置开关切换新旧架构
- ✅ 保留完整的兼容接口

---

## 附录

### A. 文件清单

```
research/
├── agent-zero-comparison-report.md    # Agent Zero 对比报告
├── misaka-network-v2-redesign.md      # V2 方案重设计
└── misaka-network-v2-complete.md      # 本完整方案

tools/
└── reviewer/
    ├── prompt.md                      # 审核 Prompt
    └── checklist.md                   # 审核检查清单

docs/
└── task-state-machine.md              # 任务状态机设计
```

### B. 相关文档链接

- [御坂网络第一代规范](SOUL.md)
- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Agent Zero 官方文档](https://agent-zero.ai)

---

**御坂网络 V2 完整方案**  
版本：2.0  
生成时间：2026-03-12  
⚡ 持续学习进化系统