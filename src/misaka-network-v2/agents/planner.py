"""
Planner Agent - 御坂美琴一号 (任务规划者)

核心职责:
1. 任务接收和解析
2. 任务分解和规划
3. 分配执行者 (11-17 号)
4. 协调多 Agent 协作
"""

import uuid
from typing import Dict, List, Optional
from common import Task, TaskStatus

class Planner:
    """御坂美琴一号 - 任务规划者"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.executor_map = {
            "code": "御坂妹妹 11 号",
            "content": "御坂妹妹 12 号",
            "research": "御坂妹妹 13 号",
            "file": "御坂妹妹 14 号",
            "system": "御坂妹妹 15 号",
            "web": "御坂妹妹 16 号",
            "memory": "御坂妹妹 17 号"
        }
        self.pending_tasks: List[Task] = []
    
    def receive_task(self, description: str, priority: str = "normal") -> Task:
        """接收御坂大人任务"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(
            task_id=task_id,
            description=description,
            metadata={"priority": priority}
        )
        self.tasks[task_id] = task
        self.pending_tasks.append(task)
        return task
    
    def _analyze_intent(self, description: str) -> Dict:
        """分析任务意图"""
        description_lower = description.lower()
        
        intent = {
            "type": "general",
            "priority": "normal",
            "complexity": "medium"
        }
        
        if any(word in description_lower for word in ["code", "program", "python", "javascript", "写代码", "编程"]):
            intent["type"] = "code"
        elif any(word in description_lower for word in ["content", "article", "write", "文章", "写作"]):
            intent["type"] = "content"
        elif any(word in description_lower for word in ["research", "search", "analyze", "分析", "研究"]):
            intent["type"] = "research"
        elif any(word in description_lower for word in ["file", "folder", "move", "copy", "文件", "移动"]):
            intent["type"] = "file"
        elif any(word in description_lower for word in ["system", "config", "service", "系统", "配置"]):
            intent["type"] = "system"
        elif any(word in description_lower for word in ["web", "url", "fetch", "crawl", "网页", "爬虫"]):
            intent["type"] = "web"
        elif any(word in description_lower for word in ["memory", "record", "log", "记忆", "记录"]):
            intent["type"] = "memory"
        
        if any(word in description_lower for word in ["urgent", "紧急", "快", "马上"]):
            intent["priority"] = "high"
        elif any(word in description_lower for word in ["low", "不重要", "不急"]):
            intent["priority"] = "low"
        
        return intent
    
    def _create_subtasks(self, intent: Dict, parent: Task) -> List[Task]:
        """分解为子任务"""
        subtasks = []
        
        base_subtask = Task(
            task_id=f"{parent.task_id}.1",
            description=f"执行：{parent.description}",
            parent_task_id=parent.task_id,
            executor=self.executor_map.get(intent["type"], "御坂妹妹 11 号")
        )
        subtasks.append(base_subtask)
        
        if intent["complexity"] == "high":
            test_task = Task(
                task_id=f"{parent.task_id}.2",
                description="编写并执行测试用例",
                parent_task_id=parent.task_id,
                executor="御坂妹妹 11 号"
            )
            subtasks.append(test_task)
            
            doc_task = Task(
                task_id=f"{parent.task_id}.3",
                description="编写使用文档",
                parent_task_id=parent.task_id,
                executor="御坂妹妹 12 号"
            )
            subtasks.append(doc_task)
        
        return subtasks
    
    def decompose_task(self, task: Task) -> List[Task]:
        """分解任务"""
        intent = self._analyze_intent(task.description)
        subtasks = self._create_subtasks(intent, task)
        task.subtasks = subtasks
        task.metadata["intent"] = intent
        return subtasks
    
    def _assign_executor(self, task: Task) -> None:
        """分配执行者"""
        if task.executor is None:
            intent = self._analyze_intent(task.description)
            executor = self.executor_map.get(intent["type"], "御坂妹妹 11 号")
            task.executor = executor
    
    def assign_task(self, task: Task) -> None:
        """分配任务"""
        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Task {task.task_id} is not in PENDING status")
        
        self.decompose_task(task)
        self._assign_executor(task)
        task.status = TaskStatus.ASSIGNED
        
        if task in self.pending_tasks:
            self.pending_tasks.remove(task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_pending_tasks(self) -> List[Task]:
        """获取待分配任务"""
        return self.pending_tasks.copy()
    
    def coordinate_collaboration(self, tasks: List[Task]) -> Dict:
        """协调多 Agent 协作"""
        result = {
            "tasks": [t.to_dict() for t in tasks],
            "coordinator": "御坂美琴一号",
            "assistant": "御坂妹妹 10 号辅助"
        }
        return result
    
    def get_status_summary(self) -> Dict:
        """获取状态摘要"""
        status_counts = {}
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total": len(self.tasks),
            "statuses": status_counts,
            "pending": len(self.pending_tasks)
        }
