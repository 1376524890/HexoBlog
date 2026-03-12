"""
Session Notification Integration - 会话通知集成示例

演示如何将 sessions_send 回发机制集成到 Agent 执行流程中

使用方式:
    python session_notify_example.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from session_notify import SessionNotifier


class NotificationExample:
    """通知集成示例"""
    
    def __init__(self):
        self.notifier = SessionNotifier()
        self.task_history = []
    
    def simulate_task_execution(self, task_id: str, task_name: str):
        """模拟任务执行"""
        print(f"🔄 开始执行任务：{task_name} ({task_id})")
        
        try:
            # 模拟执行结果
            result = {
                "duration": "2s",
                "status": "success",
                "files_created": [
                    "test_file1.py",
                    "test_file2.py",
                    "README.md",
                    "config.json"
                ],
                "tests_passed": 5
            }
            
            print(f"✅ 任务执行完成：{task_name}")
            
            # 发送任务完成通知
            success = self.notifier.notify_task_complete(task_id, result)
            
            if success:
                print(f"📬 任务完成通知已发送")
            else:
                print(f"⚠️ 任务完成通知发送失败")
            
            return result
            
        except Exception as e:
            # 发送错误通知
            error_msg = str(e)
            traceback = self._generate_traceback(task_id, error_msg)
            
            success = self.notifier.notify_task_error(task_id, error_msg, traceback)
            
            if success:
                print(f"📬 错误通知已发送")
            else:
                print(f"⚠️ 错误通知发送失败")
            
            raise
    
    def _generate_traceback(self, task_id: str, error: str) -> str:
        """生成模拟堆栈跟踪"""
        return f"""Traceback (most recent call last):
  File "/home/claw/.openclaw/workspace/tasks/{task_id}.py", line 10, in execute
    result = self.run_task()
  File "/home/claw/.openclaw/workspace/tasks/{task_id}.py", line 15, in run_task
    raise Exception("{error}")
Exception: {error}
"""
    
    def send_system_status(self):
        """发送系统状态通知"""
        content = """
**性能指标**:
- 响应时间：100ms
- 任务数：10
- 成功率：100%

**系统健康**: ✅ 正常

**内存使用**: 512MB
**CPU 使用率**: 25%
"""
        
        success = self.notifier.notify_system(
            "系统状态报告",
            content
        )
        
        print(f"📬 系统状态通知：{'已发送' if success else '发送失败'}")
        return success
    
    def send_reminder(self, title: str, content: str):
        """发送提醒通知"""
        success = self.notifier.notify_reminder(title, content)
        print(f"📬 提醒通知：{'已发送' if success else '发送失败'}")
        return success


def main():
    """主函数"""
    print("=" * 60)
    print("会话通知系统集成示例")
    print("=" * 60)
    
    # 创建示例
    example = NotificationExample()
    
    # 模拟设置会话（实际使用时会自动获取）
    example.notifier.set_current_session("agent:main:feishu:ou_c0ea02caca01fe1b21994f95366d8c4a")
    
    print(f"\n当前会话：{example.notifier.get_current_session()}")
    print("-" * 60)
    
    # 示例 1: 任务完成通知
    print("\n【示例 1】任务完成通知")
    result = example.simulate_task_execution(
        "task_001",
        "创建 Python 爬虫项目"
    )
    
    # 示例 2: 任务错误通知
    print("\n【示例 2】任务错误通知")
    try:
        raise Exception("模拟错误：文件不存在")
    except Exception as e:
        error_msg = str(e)
        traceback = example._generate_traceback("task_002", error_msg)
        success = example.notifier.notify_task_error("task_002", error_msg, traceback)
        print(f"错误通知：{'已发送' if success else '发送失败'}")
    
    # 示例 3: 系统状态通知
    print("\n【示例 3】系统状态通知")
    example.send_system_status()
    
    # 示例 4: 提醒通知
    print("\n【示例 4】提醒通知")
    example.send_reminder(
        "待办事项",
        "1. 检查任务状态\n"
        "2. 查看日志文件\n"
        "3. 更新文档"
    )
    
    # 示例 5: 心跳通知
    print("\n【示例 5】心跳通知")
    success = example.notifier.notify_heartbeat("active")
    print(f"心跳通知：{'已发送' if success else '发送失败'}")
    
    print("\n" + "=" * 60)
    print("✅ 所有示例执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
