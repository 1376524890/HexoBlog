"""
Common Data Structures - 通用数据结构
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


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


@dataclass
class Task:
    """任务实体"""
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    executor: Optional[str] = None
    parent_task_id: Optional[str] = None
    subtasks: List['Task'] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "executor": self.executor,
            "parent_task_id": self.parent_task_id,
            "subtasks": [t.to_dict() for t in self.subtasks],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        return f"Task({self.task_id}, {self.status.value}, {self.description[:30]}...)"


@dataclass
class ExecutionResult:
    """执行结果"""
    result_type: str
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None
    task_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReviewScore:
    """审核得分"""
    category: str  # closing/compliance/compatibility/completeness
    score: int
    max_score: int
    issues: List[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """审核结果"""
    submission_id: str
    scores: List[ReviewScore]
    total_score: int
    max_score: int = 100
    decision: str = "pending"  # approved/rework
    feedback: List[str] = field(default_factory=list)
    reviewed_at: datetime = field(default_factory=datetime.now)
    
    def is_approved(self) -> bool:
        """是否通过审核"""
        return self.decision == "approved"
    
    def get_ratio(self) -> float:
        """得分比例"""
        return self.total_score / self.max_score if self.max_score > 0 else 0


__all__ = ["Task", "TaskStatus", "ExecutionResult", "ReviewScore", "ReviewResult"]
