"""
Core Misaka Network V2 Controller
==================================

完整网络控制器：整合 Planner, Executor, Reviewer, Patrol
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

from agents.planner import Planner
from agents.executor import Executor
from agents.reviewer import Reviewer
from agents.patrol import Patrol
from common import Task, TaskStatus, ExecutionResult, ReviewResult


class MisakaNetworkV2:
    """御坂网络 V2 - 完整控制器"""
    
    def __init__(self):
        """初始化御坂网络 V2"""
        self.planner = Planner()
        self.reviewer = Reviewer()
        self.patrol = Patrol()
        
        self.executors: Dict[str, Executor] = {
            "御坂妹妹 11 号": Executor("御坂妹妹 11 号", "code", "御坂妹妹 11 号"),
            "御坂妹妹 12 号": Executor("御坂妹妹 12 号", "content", "御坂妹妹 12 号"),
            "御坂妹妹 13 号": Executor("御坂妹妹 13 号", "research", "御坂妹妹 13 号"),
            "御坂妹妹 14 号": Executor("御坂妹妹 14 号", "file", "御坂妹妹 14 号"),
            "御坂妹妹 15 号": Executor("御坂妹妹 15 号", "system", "御坂妹妹 15 号"),
            "御坂妹妹 16 号": Executor("御坂妹妹 16 号", "web", "御坂妹妹 16 号"),
            "御坂妹妹 17 号": Executor("御坂妹妹 17 号", "memory", "御坂妹妹 17 号"),
            "御坂妹妹 18 号": Executor("御坂妹妹 18 号", "review", "御坂妹妹 18 号"),
        }
        
        self.execution_results: Dict[str, ExecutionResult] = {}
        self.review_results: Dict[str, ReviewResult] = {}
        
        self.is_running = False
        self._lock = threading.Lock()
        self.start_time: Optional[datetime] = None
    
    def receive_task(self, description: str, priority: str = "normal") -> Task:
        """接收御坂大人任务"""
        return self.planner.receive_task(description, priority)
    
    def assign_task(self, task: Task) -> None:
        """分配任务给执行者"""
        self.planner.assign_task(task)
        self.patrol.register_task(task.task_id, task.executor)
    
    def execute_task(self, task_id: str) -> ExecutionResult:
        """执行任务"""
        task = self.planner.get_task(task_id)
        if not task:
            return ExecutionResult(
                result_type="error",
                error=f"Task {task_id} not found"
            )
        
        executor_name = task.executor
        if executor_name not in self.executors:
            return ExecutionResult(
                result_type="error",
                error=f"Executor {executor_name} not found"
            )
        
        executor = self.executors[executor_name]
        self.patrol.update_task_state(task_id, "in_progress")
        self.patrol.record_heartbeat(executor.agent_id)
        
        result = executor.execute({
            "task_id": task_id,
            "description": task.description,
            "executor": executor_name
        })
        
        self.execution_results[task_id] = result
        
        if result.result_type == "success":
            self.patrol.update_task_state(task_id, "submitted")
        
        return result
    
    def submit_for_review(self, task_id: str) -> Optional[ReviewResult]:
        """提交任务给 18 号审核"""
        execution_result = self.execution_results.get(task_id)
        if not execution_result:
            return None
        
        submission = {
            "id": task_id,
            "task_id": task_id,
            "description": self.planner.get_task(task_id).description if self.planner.get_task(task_id) else "unknown",
            "executor": execution_result.metadata.get("agent_id") if execution_result.metadata else "unknown",
            "execution_result": str(execution_result),
            "execute": True,
            "result_type": execution_result.result_type
        }
        
        review_result = self.reviewer.review(submission)
        self.review_results[task_id] = review_result
        
        if review_result.is_approved():
            self.patrol.update_task_state(task_id, "done")
        else:
            self.patrol.update_task_state(task_id, "rework")
        
        return review_result
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        task = self.planner.get_task(task_id)
        if not task:
            return None
        
        task_state = self.patrol.get_task_state(task_id)
        execution_result = self.execution_results.get(task_id)
        review_result = self.review_results.get(task_id)
        
        return {
            "task": task.to_dict(),
            "patrol_state": task_state.to_dict() if task_state else None,
            "execution_result": execution_result.to_dict() if execution_result else None,
            "review_result": review_result.to_dict() if review_result else None
        }
    
    def start_monitoring(self) -> None:
        """启动监控"""
        if self.is_running:
            return
        self.is_running = True
        self.start_time = datetime.now()
        self.patrol.start()
    
    def stop_monitoring(self) -> None:
        """停止监控"""
        self.is_running = False
        self.patrol.stop()
    
    def get_status_summary(self) -> Dict:
        """获取系统状态摘要"""
        planner_summary = self.planner.get_status_summary()
        patrol_health = self.patrol.get_health_summary()
        reviewer_stats = self.reviewer.get_review_stats()
        
        return {
            "network_status": "running" if self.is_running else "stopped",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "planner": planner_summary,
            "patrol": patrol_health,
            "reviewer": reviewer_stats,
            "executors": {name: executor.get_stats() for name, executor in self.executors.items()}
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """获取任务历史"""
        tasks = self.planner.get_all_tasks()
        history = []
        
        for task in tasks[-limit:]:
            task_status = self.get_task_status(task.task_id)
            if task_status:
                history.append(task_status)
        
        return history
    
    def auto_recovery(self, task_id: str) -> bool:
        """手动触发任务恢复"""
        task = self.planner.get_task(task_id)
        if not task:
            return False
        
        state = self.patrol.get_task_state(task_id)
        if not state:
            return False
        
        return self.patrol._auto_recovery(task_id, state)
    
    def get_review_feedback(self, task_id: str) -> Optional[List[str]]:
        """获取任务审核反馈"""
        review_result = self.review_results.get(task_id)
        return review_result.feedback if review_result else None
