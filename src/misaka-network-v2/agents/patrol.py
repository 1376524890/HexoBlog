"""
Patrol Agent - 御坂妹妹 19 号 (状态监控者)

核心职责:
1. 监控任务状态
2. 检测超时任务
3. 自动恢复异常
4. 质量监控

心跳检测: 30 秒间隔
超时阈值：5 分钟
自动恢复：重试 3 次
"""

import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from threading import Thread, Event
import threading


# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@dataclass
class Heartbeat:
    """心跳记录"""
    agent_id: str
    last_heartbeat: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active/inactive/error


@dataclass
class TaskState:
    """任务状态"""
    task_id: str
    status: str
    last_update: datetime = field(default_factory=datetime.now)
    executor: Optional[str] = None
    recovery_attempts: int = 0


class Patrol:
    """御坂妹妹 19 号 - 状态监控者"""
    
    def __init__(self, check_interval: int = 30, timeout_threshold: int = 300):
        """
        初始化 Patrol
        
        Args:
            check_interval: 检查间隔 (秒)，默认 30 秒
            timeout_threshold: 超时阈值 (秒)，默认 5 分钟
        """
        self.check_interval = check_interval
        self.timeout_threshold = timeout_threshold
        self.max_recovery_attempts = 3
        
        # 状态追踪
        self.heartbeats: Dict[str, Heartbeat] = {}
        self.task_states: Dict[str, TaskState] = {}
        self.agent_stats: Dict[str, Dict] = {}
        
        # 监控线程
        self._monitor_thread: Optional[Thread] = None
        self._stop_event = Event()
        
        # 统计信息
        self.stats = {
            "tasks_monitored": 0,
            "timeouts_detected": 0,
            "recovery_attempts": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0
        }
    
    def start(self) -> None:
        """启动监控"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            logger.warning("Patrol is already running")
            return
        
        self._stop_event.clear()
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Patrol started")
    
    def stop(self) -> None:
        """停止监控"""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Patrol stopped")
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        while not self._stop_event.is_set():
            try:
                self._monitor_all_tasks()
                self._monitor_all_agents()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Patrol monitor error: {e}")
                time.sleep(self.check_interval)
    
    def _monitor_all_tasks(self) -> None:
        """监控所有任务"""
        for task_id, state in self.task_states.items():
            self._monitor_task(task_id, state)
    
    def _monitor_task(self, task_id: str, state: TaskState) -> None:
        """监控单个任务"""
        # 检查超时
        if self._is_timeout(state):
            self._handle_timeout(task_id, state)
        
        # 检查卡顿
        if self._is_stuck(state):
            self._auto_recovery(task_id, state)
    
    def _is_timeout(self, state: TaskState) -> bool:
        """检查是否超时"""
        elapsed = datetime.now() - state.last_update
        return elapsed.total_seconds() > self.timeout_threshold
    
    def _is_stuck(self, state: TaskState) -> bool:
        """检查是否卡顿"""
        # 检查任务是否在某个状态停留过久
        elapsed = datetime.now() - state.last_update
        return elapsed.total_seconds() > self.timeout_threshold * 2
    
    def _handle_timeout(self, task_id: str, state: TaskState) -> None:
        """处理超时任务"""
        logger.warning(f"Task {task_id} timeout, initiating recovery")
        self.stats["timeouts_detected"] += 1
        self._auto_recovery(task_id, state)
    
    def _auto_recovery(self, task_id: str, state: TaskState) -> bool:
        """自动恢复任务"""
        recovery_attempts = state.recovery_attempts + 1
        state.recovery_attempts = recovery_attempts
        
        self.stats["recovery_attempts"] += 1
        
        if recovery_attempts >= self.max_recovery_attempts:
            logger.error(f"Task {task_id} failed after {recovery_attempts} recovery attempts")
            self.stats["failed_recoveries"] += 1
            return False
        
        # 根据状态执行不同的恢复逻辑
        status = state.status
        if status == "in_progress":
            # 重新分配任务
            success = self._reassign_task(task_id, state)
        elif status == "review":
            # 重新提交审核
            success = self._resubmit_review(task_id, state)
        elif status == "assigned":
            # 重新分配执行者
            success = self._reassign_executor(task_id, state)
        else:
            success = False
        
        if success:
            self.stats["successful_recoveries"] += 1
            logger.info(f"Task {task_id} recovered successfully (attempt {recovery_attempts})")
        else:
            logger.error(f"Task {task_id} recovery failed (attempt {recovery_attempts})")
        
        return success
    
    def _reassign_task(self, task_id: str, state: TaskState) -> bool:
        """重新分配任务"""
        logger.info(f"Reassigning task {task_id}")
        # TODO: 实际重新分配逻辑
        return True
    
    def _resubmit_review(self, task_id: str, state: TaskState) -> bool:
        """重新提交审核"""
        logger.info(f"Resubmitting task {task_id} for review")
        # TODO: 实际重新提交审核逻辑
        return True
    
    def _reassign_executor(self, task_id: str, state: TaskState) -> bool:
        """重新分配执行者"""
        logger.info(f"Reassigning executor for task {task_id}")
        # TODO: 实际重新分配执行者逻辑
        return True
    
    def _monitor_all_agents(self) -> None:
        """监控所有 Agent"""
        current_time = datetime.now()
        
        for agent_id, heartbeat in self.heartbeats.items():
            elapsed = current_time - heartbeat.last_heartbeat
            if elapsed.total_seconds() > self.timeout_threshold * 2:
                heartbeat.status = "inactive"
                logger.warning(f"Agent {agent_id} heartbeat timeout")
            elif elapsed.total_seconds() > self.timeout_threshold:
                heartbeat.status = "error"
                logger.error(f"Agent {agent_id} heartbeat delayed")
            else:
                heartbeat.status = "active"
    
    def record_heartbeat(self, agent_id: str) -> None:
        """记录 Agent 心跳"""
        if agent_id not in self.heartbeats:
            self.heartbeats[agent_id] = Heartbeat(agent_id=agent_id)
        
        self.heartbeats[agent_id].last_heartbeat = datetime.now()
        self.heartbeats[agent_id].status = "active"
        
        # 更新 Agent 统计
        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = {
                "total_heartbeats": 0,
                "last_heartbeat": None,
                "status": "active"
            }
        
        self.agent_stats[agent_id]["total_heartbeats"] += 1
        self.agent_stats[agent_id]["last_heartbeat"] = datetime.now().isoformat()
        self.agent_stats[agent_id]["status"] = "active"
    
    def register_task(self, task_id: str, executor: Optional[str] = None) -> None:
        """注册任务"""
        if task_id not in self.task_states:
            self.task_states[task_id] = TaskState(
                task_id=task_id, 
                executor=executor,
                status="pending"
            )
            self.stats["tasks_monitored"] += 1
            logger.info(f"Registered task {task_id}")
    
    def update_task_state(self, task_id: str, status: str) -> None:
        """更新任务状态"""
        if task_id in self.task_states:
            self.task_states[task_id].status = status
            self.task_states[task_id].last_update = datetime.now()
            logger.debug(f"Task {task_id} status updated to {status}")
        else:
            logger.warning(f"Task {task_id} not registered")
    
    def get_task_state(self, task_id: str) -> Optional[TaskState]:
        """获取任务状态"""
        return self.task_states.get(task_id)
    
    def get_all_task_states(self) -> Dict[str, TaskState]:
        """获取所有任务状态"""
        return self.task_states.copy()
    
    def get_agent_stats(self) -> Dict[str, Dict]:
        """获取 Agent 统计"""
        return self.agent_stats.copy()
    
    def get_patrol_stats(self) -> Dict:
        """获取 Patrol 统计"""
        return self.stats.copy()
    
    def get_health_summary(self) -> Dict:
        """获取健康摘要"""
        active_agents = sum(1 for hb in self.heartbeats.values() if hb.status == "active")
        inactive_agents = sum(1 for hb in self.heartbeats.values() if hb.status == "inactive")
        error_agents = sum(1 for hb in self.heartbeats.values() if hb.status == "error")
        
        return {
            "total_agents": len(self.heartbeats),
            "active_agents": active_agents,
            "inactive_agents": inactive_agents,
            "error_agents": error_agents,
            "total_tasks": len(self.task_states),
            "patrol_stats": self.stats
        }
