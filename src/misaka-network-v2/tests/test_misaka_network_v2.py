"""
测试套件 - 验证御坂网络 V2 功能
"""

import unittest
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/home/claw/.openclaw/workspace/src')

from misaka_network_v2 import MisakaNetworkV2
from misaka_network_v2.common import TaskStatus


class TestPlanner(unittest.TestCase):
    """测试 Planner 功能"""
    
    def setUp(self):
        self.network = MisakaNetworkV2()
    
    def test_receive_task(self):
        """测试接收任务"""
        task = self.network.receive_task("测试任务", priority="high")
        
        self.assertIsNotNone(task)
        self.assertEqual(task.description, "测试任务")
        self.assertEqual(task.metadata["priority"], "high")
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_assign_task(self):
        """测试分配任务"""
        task = self.network.receive_task("测试任务")
        self.network.assign_task(task)
        
        self.assertEqual(task.status, TaskStatus.ASSIGNED)
        self.assertIsNotNone(task.executor)
    
    def test_decompose_task(self):
        """测试任务分解"""
        task = self.network.receive_task("编写 Python 代码", priority="high")
        self.network.assign_task(task)
        
        self.assertGreater(len(task.subtasks), 0)
        for subtask in task.subtasks:
            self.assertIsNotNone(subtask.executor)


class TestExecutor(unittest.TestCase):
    """测试 Executor 功能"""
    
    def test_executor_creation(self):
        """测试执行器创建"""
        network = MisakaNetworkV2()
        
        # 测试各个执行器
        expected_executors = [
            "御坂妹妹 11 号",
            "御坂妹妹 12 号",
            "御坂妹妹 13 号",
            "御坂妹妹 14 号",
            "御坂妹妹 15 号",
            "御坂妹妹 16 号",
            "御坂妹妹 17 号",
        ]
        
        for executor_name in expected_executors:
            self.assertIn(executor_name, network.executors)
    
    def test_execute_task(self):
        """测试执行任务"""
        network = MisakaNetworkV2()
        task = network.receive_task("测试执行")
        network.assign_task(task)
        
        result = network.execute_task(task.task_id)
        
        self.assertEqual(result.result_type, "success")
        self.assertIsNotNone(result.metadata)


class TestReviewer(unittest.TestCase):
    """测试 Reviewer 功能"""
    
    def test_review_process(self):
        """测试审核流程"""
        network = MisakaNetworkV2()
        task = network.receive_task("测试审核")
        network.assign_task(task)
        network.execute_task(task.task_id)
        
        review_result = network.submit_for_review(task.task_id)
        
        self.assertIsNotNone(review_result)
        self.assertIn(review_result.decision, ["approved", "rework"])
        self.assertGreaterEqual(review_result.total_score, 0)
        self.assertLessEqual(review_result.total_score, 100)
    
    def test_review_scores(self):
        """测试审核得分"""
        network = MisakaNetworkV2()
        task = network.receive_task("测试审核")
        network.assign_task(task)
        network.execute_task(task.task_id)
        
        review_result = network.submit_for_review(task.task_id)
        
        if review_result:
            # 检查各项得分
            for score in review_result.scores:
                self.assertGreaterEqual(score.score, 0)
                self.assertLessEqual(score.score, score.max_score)


class TestPatrol(unittest.TestCase):
    """测试 Patrol 功能"""
    
    def test_heartbeat_record(self):
        """测试心跳记录"""
        network = MisakaNetworkV2()
        
        # 模拟心跳
        for i in range(5):
            network.patrol.record_heartbeat(f"test_agent_{i}")
        
        # 验证心跳记录
        heartbeats = network.patrol.heartbeats
        self.assertEqual(len(heartbeats), 5)
        
        for agent_id, heartbeat in heartbeats.items():
            self.assertEqual(heartbeat.status, "active")
    
    def test_monitoring_start_stop(self):
        """测试监控启动和停止"""
        network = MisakaNetworkV2()
        
        # 启动监控
        network.start_monitoring()
        self.assertTrue(network.is_running)
        
        # 停止监控
        network.stop_monitoring()
        self.assertFalse(network.is_running)
    
    def test_task_state_tracking(self):
        """测试任务状态追踪"""
        network = MisakaNetworkV2()
        
        # 注册任务
        task = network.receive_task("测试状态追踪")
        network.assign_task(task)
        
        # 注册到 Patrol
        network.patrol.register_task(task.task_id, task.executor)
        
        # 更新状态
        network.patrol.update_task_state(task.task_id, "in_progress")
        
        # 验证状态
        state = network.patrol.get_task_state(task.task_id)
        self.assertEqual(state.status, "in_progress")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        network = MisakaNetworkV2()
        
        # 1. 接收任务
        task = network.receive_task("完整工作流测试", priority="high")
        self.assertIsNotNone(task)
        
        # 2. 分配任务
        network.assign_task(task)
        self.assertEqual(task.status, TaskStatus.ASSIGNED)
        
        # 3. 执行任务
        result = network.execute_task(task.task_id)
        self.assertEqual(result.result_type, "success")
        
        # 4. 提交审核
        review_result = network.submit_for_review(task.task_id)
        self.assertIsNotNone(review_result)
        
        # 5. 获取状态
        status = network.get_task_status(task.task_id)
        self.assertIsNotNone(status)
        
        # 6. 获取摘要
        summary = network.get_status_summary()
        self.assertEqual(summary["network_status"], "stopped")
    
    def test_auto_recovery(self):
        """测试自动恢复"""
        network = MisakaNetworkV2()
        
        # 创建任务
        task = network.receive_task("恢复测试")
        network.assign_task(task)
        
        # 模拟卡住的任务
        network.patrol.update_task_state(task.task_id, "in_progress")
        
        # 手动触发恢复
        success = network.auto_recovery(task.task_id)
        
        # 验证恢复结果
        self.assertIsInstance(success, bool)


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_concurrent_tasks(self):
        """测试并发任务"""
        network = MisakaNetworkV2()
        
        # 创建多个任务
        task_count = 10
        tasks = []
        
        for i in range(task_count):
            task = network.receive_task(f"并发任务 {i}")
            network.assign_task(task)
            tasks.append(task)
        
        # 执行所有任务
        results = []
        for task in tasks:
            result = network.execute_task(task.task_id)
            results.append(result)
        
        # 验证结果
        self.assertEqual(len(results), task_count)
        for result in results:
            self.assertEqual(result.result_type, "success")
    
    def test_memory_usage(self):
        """测试内存使用"""
        import tracemalloc
        
        tracemalloc.start()
        
        network = MisakaNetworkV2()
        
        # 创建大量任务
        for i in range(100):
            task = network.receive_task(f"内存测试任务 {i}")
            network.assign_task(task)
            network.execute_task(task.task_id)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"峰值内存使用：{peak / 1024 / 1024:.2f} MB")
        self.assertLess(peak, 100 * 1024 * 1024)  # 小于 100MB


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestPlanner))
    suite.addTests(loader.loadTestsFromTestCase(TestExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestReviewer))
    suite.addTests(loader.loadTestsFromTestCase(TestPatrol))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    print(f"总测试数：{result.testsRun}")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
