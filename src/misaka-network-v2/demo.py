"""
御坂网络 V2 演示脚本
直接运行此脚本验证功能
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入模块
from common import Task, TaskStatus, ExecutionResult
from agents.planner import Planner
from agents.executor import Executor
from agents.reviewer import Reviewer
from agents.patrol import Patrol
from network import MisakaNetworkV2

print("="*60)
print("御坂网络 V2 - 功能验证")
print("="*60)

# 创建网络实例
print("\n1. 创建网络实例...")
network = MisakaNetworkV2()
print(f"✅ 创建成功：{network}")
print(f"   - Planner: {network.planner}")
print(f"   - Reviewer: {network.reviewer}")
print(f"   - Patrol: {network.patrol}")
print(f"   - 执行者数量：{len(network.executors)}")

# 接收任务
print("\n2. 接收任务...")
task = network.receive_task("创建一个 Python 爬虫项目", priority="high")
print(f"✅ 任务 ID: {task.task_id}")
print(f"   - 描述：{task.description}")
print(f"   - 优先级：{task.metadata['priority']}")
print(f"   - 状态：{task.status}")

# 分配任务
print("\n3. 分配任务...")
network.assign_task(task)
print(f"✅ 状态更新：{task.status}")
print(f"   - 执行者：{task.executor}")
print(f"   - 子任务数：{len(task.subtasks)}")

# 执行任务
print("\n4. 执行任务...")
result = network.execute_task(task.task_id)
print(f"✅ 执行结果：{result.result_type}")
print(f"   - 执行时间：{result.metadata.get('execution_time', 0):.2f}s")

# 提交审核
print("\n5. 提交审核...")
review_result = network.submit_for_review(task.task_id)
if review_result:
    print(f"✅ 审核结果：{review_result.decision}")
    print(f"   - 得分：{review_result.total_score}/{review_result.max_score}")
    print(f"   - 反馈数：{len(review_result.feedback)}")
    
    if review_result.feedback:
        print("   - 审核反馈:")
        for feedback in review_result.feedback[:3]:
            print(f"      {feedback}")

# 启动监控
print("\n6. 启动监控...")
network.start_monitoring()
print("✅ 监控已启动")

# 获取状态
print("\n7. 获取系统状态...")
summary = network.get_status_summary()
print(f"   - 网络状态：{summary['network_status']}")
print(f"   - 任务统计：{summary['planner']}")
print(f"   - Patrol 健康：{summary['patrol']}")

# 停止监控
print("\n8. 停止监控...")
network.stop_monitoring()
print("✅ 监控已停止")

print("\n" + "="*60)
print("✅ 所有功能验证完成！")
print("="*60)
