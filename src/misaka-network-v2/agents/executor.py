"""
Executor Agent - 御坂妹妹 11-17 号 (任务执行者)

核心职责:
1. 接收分配的任务
2. 执行具体操作
3. 提交执行结果
4. 处理异常情况
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from common import ExecutionResult, Task


@dataclass
class ExecutorStats:
    """执行器统计信息"""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    total_time: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": self.successful_tasks / self.total_tasks if self.total_tasks > 0 else 0
        }


class Executor:
    """御坂妹妹 X 号 - 任务执行者"""
    
    def __init__(self, agent_id: str, role: str, name: str = ""):
        self.agent_id = agent_id
        self.role = role
        self.name = name or f"御坂妹妹{agent_id.split()[-1]}"
        self.current_task: Optional[str] = None
        self.stats = ExecutorStats()
        self.execution_history: list = []
        
        # 角色特定配置
        self.role_config = self._init_role_config()
    
    def _init_role_config(self) -> Dict:
        """初始化角色配置"""
        configs = {
            "code": {
                "allowed_tools": ["exec", "process", "edit", "read", "write"],
                "max_execution_time": 300,
                "sandbox": True
            },
            "content": {
                "allowed_tools": ["read", "write", "edit"],
                "max_execution_time": 180,
                "sandbox": False
            },
            "research": {
                "allowed_tools": ["web_search", "web_fetch"],
                "max_execution_time": 300,
                "sandbox": False
            },
            "file": {
                "allowed_tools": ["exec"],
                "max_execution_time": 120,
                "sandbox": True
            },
            "system": {
                "allowed_tools": ["exec"],
                "max_execution_time": 300,
                "sandbox": True,
                "elevated": False
            },
            "web": {
                "allowed_tools": ["web_fetch"],
                "max_execution_time": 300,
                "sandbox": False
            },
            "memory": {
                "allowed_tools": ["read", "write"],
                "max_execution_time": 120,
                "sandbox": False
            },
            "general": {
                "allowed_tools": ["read", "write", "exec"],
                "max_execution_time": 300,
                "sandbox": True
            }
        }
        return configs.get(self.role, configs["general"])
    
    def execute(self, task: Dict) -> ExecutionResult:
        """执行任务"""
        self.current_task = task["task_id"]
        start_time = datetime.now()
        
        try:
            # 执行具体工作
            result = self._do_work(task)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.stats.total_tasks += 1
            self.stats.successful_tasks += 1
            self.stats.total_time += execution_time
            
            self.execution_history.append({
                "task_id": task["task_id"],
                "status": "success",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return ExecutionResult(
                result_type="success",
                data=result,
                metadata={
                    "task_id": task["task_id"],
                    "agent_id": self.agent_id,
                    "execution_time": execution_time
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.stats.total_tasks += 1
            self.stats.failed_tasks += 1
            
            self.execution_history.append({
                "task_id": task["task_id"],
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return ExecutionResult(
                result_type="error",
                error=str(e),
                metadata={
                    "task_id": task["task_id"],
                    "agent_id": self.agent_id,
                    "execution_time": execution_time
                }
            )
    
    def _do_work(self, task: Dict) -> Any:
        """执行具体工作"""
        # 根据角色执行不同工作
        if self.role == "code":
            return self._execute_code_task(task)
        elif self.role == "content":
            return self._execute_content_task(task)
        elif self.role == "research":
            return self._execute_research_task(task)
        elif self.role == "file":
            return self._execute_file_task(task)
        elif self.role == "system":
            return self._execute_system_task(task)
        elif self.role == "web":
            return self._execute_web_task(task)
        elif self.role == "memory":
            return self._execute_memory_task(task)
        else:
            return self._execute_general_task(task)
    
    def _execute_code_task(self, task: Dict) -> Dict:
        """执行代码任务"""
        return {
            "type": "code",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def _execute_content_task(self, task: Dict) -> Dict:
        """执行内容任务"""
        return {
            "type": "content",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def _execute_research_task(self, task: Dict) -> Dict:
        """执行研究任务"""
        return {
            "type": "research",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def _execute_file_task(self, task: Dict) -> Dict:
        """执行文件任务"""
        return {
            "type": "file",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def _execute_system_task(self, task: Dict) -> Dict:
        """执行系统任务"""
        return {
            "type": "system",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def _execute_web_task(self, task: Dict) -> Dict:
        """执行网页任务"""
        return {
            "type": "web",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def _execute_memory_task(self, task: Dict) -> Dict:
        """执行记忆任务"""
        return {
            "type": "memory",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def _execute_general_task(self, task: Dict) -> Dict:
        """执行通用任务"""
        return {
            "type": "general",
            "task_id": task["task_id"],
            "description": task["description"],
            "status": "executed"
        }
    
    def submit(self, result: ExecutionResult) -> bool:
        """提交执行结果"""
        # 提交给 18 号审核
        return True
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.to_dict()
    
    def get_history(self, limit: int = 10) -> list:
        """获取执行历史"""
        return self.execution_history[-limit:]
