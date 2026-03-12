"""
Misaka Network V2 - 御坂网络 V2 完整架构
========================================

核心架构:
- Planner (御坂美琴一号 + 10 号): 任务接收、分解、分配
- Executor (御坂妹妹 11-17 号): 任务执行
- Reviewer (御坂妹妹 18 号): 质量审核
- Patrol (御坂妹妹 19 号): 状态监控

使用方式:
    from misaka_network_v2 import MisakaNetworkV2
    from .agents import Planner, Reviewer, Patrol

    network = MisakaNetworkV2()
    task = network.receive_task("创建一个 Python 爬虫项目")
    network.assign_task(task)
    network.monitor()
"""

from .agents.planner import Planner
from .agents.executor import Executor
from .agents.reviewer import Reviewer
from .agents.patrol import Patrol
from .common import Task, TaskStatus, ExecutionResult, ReviewScore, ReviewResult

__version__ = "2.0.0"
__author__ = "御坂美琴本尊"
__description__ = "御坂网络 V2 完整实现 - 四角色闭环管理系统"
