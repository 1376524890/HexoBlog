"""
Session Notification System - 会话通知系统

按照方案一：sessions_send 回发实现
- 自动获取当前会话 Key
- 发送任务完成通知
- 保持会话上下文
- 错误处理与降级机制

使用方式:
    from session_notify import SessionNotifier
    
    notifier = SessionNotifier()
    
    # 发送任务完成通知
    await notifier.notify_task_complete(task_id, result)
    
    # 发送错误通知
    await notifier.notify_error(task_id, error_message)
    
    # 发送系统通知
    await notifier.notify_system("系统状态报告", content)
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

# 配置日志
logger = logging.getLogger(__name__)


class SessionNotifier:
    """会话通知器 - 使用 sessions_send 回发"""
    
    def __init__(self):
        """初始化会话通知器"""
        self.current_session_key: Optional[str] = None
        self.notification_cache: Dict[str, List[Dict]] = {}
        self.retry_count: int = 0
        self.max_retries: int = 3
        
        # 通知模板
        self.templates = {
            "task_complete": self._format_task_complete,
            "task_error": self._format_task_error,
            "system_status": self._format_system_status,
            "heartbeat": self._format_heartbeat,
            "reminder": self._format_reminder,
        }
    
    async def set_current_session(self, session_key: str) -> None:
        """设置当前会话 Key"""
        self.current_session_key = session_key
        logger.info(f"设置当前会话：{session_key}")
    
    def get_current_session(self) -> Optional[str]:
        """获取当前会话 Key"""
        return self.current_session_key
    
    async def notify_task_complete(self, task_id: str, result: Dict) -> bool:
        """
        发送任务完成通知
        
        Args:
            task_id: 任务 ID
            result: 任务执行结果
            
        Returns:
            bool: 是否发送成功
        """
        if not self.current_session_key:
            logger.warning("当前会话 Key 为空，无法发送通知")
            return False
        
        # 格式化通知内容
        message = self._format_task_complete(task_id, result)
        
        # 发送通知
        return await self._send_session_message(message)
    
    async def notify_task_error(self, task_id: str, error: str, traceback: Optional[str] = None) -> bool:
        """
        发送任务错误通知
        
        Args:
            task_id: 任务 ID
            error: 错误信息
            traceback: 堆栈跟踪（可选）
            
        Returns:
            bool: 是否发送成功
        """
        if not self.current_session_key:
            logger.warning("当前会话 Key 为空，无法发送通知")
            return False
        
        # 格式化通知内容
        message = self._format_task_error(task_id, error, traceback)
        
        # 发送通知
        return await self._send_session_message(message)
    
    async def notify_system(self, title: str, content: str) -> bool:
        """
        发送系统通知
        
        Args:
            title: 通知标题
            content: 通知内容
            
        Returns:
            bool: 是否发送成功
        """
        if not self.current_session_key:
            logger.warning("当前会话 Key 为空，无法发送通知")
            return False
        
        # 格式化通知内容
        message = self._format_system_status(title, content)
        
        # 发送通知
        return await self._send_session_message(message)
    
    async def notify_heartbeat(self, status: str = "active") -> bool:
        """
        发送心跳通知
        
        Args:
            status: 状态 (active/inactive/error)
            
        Returns:
            bool: 是否发送成功
        """
        if not self.current_session_key:
            logger.warning("当前会话 Key 为空，无法发送通知")
            return False
        
        # 格式化通知内容
        message = self._format_heartbeat(status)
        
        # 发送通知
        return await self._send_session_message(message)
    
    async def notify_reminder(self, title: str, content: str) -> bool:
        """
        发送提醒通知
        
        Args:
            title: 提醒标题
            content: 提醒内容
            
        Returns:
            bool: 是否发送成功
        """
        if not self.current_session_key:
            logger.warning("当前会话 Key 为空，无法发送通知")
            return False
        
        # 格式化通知内容
        message = self._format_reminder(title, content)
        
        # 发送通知
        return await self._send_session_message(message)
    
    async def _send_session_message(self, message: str) -> bool:
        """
        发送会话消息
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 调用 sessions_send
            # 注意：在实际使用时需要导入 sessions_send 工具
            from sessions_send import sessions_send
            
            result = await sessions_send({
                "sessionKey": self.current_session_key,
                "message": message,
                "timeoutSeconds": 30
            })
            
            logger.info(f"✅ 会话消息发送成功：{self.current_session_key[:20]}...")
            self.retry_count = 0  # 重置重试计数
            return True
            
        except Exception as e:
            self.retry_count += 1
            logger.error(f"❌ 会话消息发送失败（第 {self.retry_count}/{self.max_retries} 次）: {e}")
            
            # 重试机制
            if self.retry_count < self.max_retries:
                logger.info(f"🔄 将在 5 秒后重试...")
                await asyncio.sleep(5)
                return await self._send_session_message(message)
            else:
                logger.error(f"⚠️ 超过最大重试次数，通知发送失败")
                return False
    
    def _format_task_complete(self, task_id: str, result: Dict) -> str:
        """格式化任务完成通知"""
        duration = result.get("duration", "0s")
        status = result.get("status", "success")
        files = result.get("files_created", [])
        tests = result.get("tests_passed", 0)
        
        return f"""🎉 **任务完成**

**任务 ID**: `{task_id}`
**执行时间**: {duration}
**状态**: ✅ {'成功' if status == 'success' else '失败'}

**执行结果**:
- 文件创建：{len(files)} 个
- 测试通过：{tests} 个

**执行文件**:
""" + "\n".join(f"  - `{f}`" for f in files[:5]) + (f"\n  ... 共 {len(files)} 个文件" if len(files) > 5 else "") + f"""

---
御坂网络助手 ⚡
"""
    
    def _format_task_error(self, task_id: str, error: str, traceback: Optional[str] = None) -> str:
        """格式化任务错误通知"""
        return f"""❌ **任务执行失败**

**任务 ID**: `{task_id}`
**错误时间**: {datetime.now().isoformat()}
**错误原因**: `{error}`

**错误详情**:
```
{traceback or '无堆栈信息'}
```

**建议操作**:
1. 检查输入参数
2. 查看详细日志
3. 重试执行

---
御坂网络助手 ⚡
"""
    
    def _format_system_status(self, title: str, content: str) -> str:
        """格式化系统状态通知"""
        return f"""🔔 **{title}**

**时间**: {datetime.now().isoformat()}

{content}

---
御坂网络助手 ⚡
"""
    
    def _format_heartbeat(self, status: str) -> str:
        """格式化心跳通知"""
        status_emoji = {"active": "✅", "inactive": "⚠️", "error": "❌"}
        return f"""🔔 **系统心跳检测**

**时间**: {datetime.now().isoformat()}
**状态**: {status_emoji.get(status, "❓")} {status}

---
御坂网络助手 ⚡
"""
    
    def _format_reminder(self, title: str, content: str) -> str:
        """格式化提醒通知"""
        return f"""📌 **提醒**

**标题**: {title}

**内容**:
{content}

---
御坂网络助手 ⚡
"""
    
    def clear_session(self) -> None:
        """清除当前会话"""
        self.current_session_key = None
        logger.info("清除当前会话")
    
    def get_notification_history(self) -> Dict[str, List[Dict]]:
        """获取通知历史"""
        return self.notification_cache.copy()


# 使用示例
if __name__ == "__main__":
    async def test_notifiers():
        notifier = SessionNotifier()
        
        # 模拟设置会话
        notifier.set_current_session("agent:main:feishu:ou_xxx")
        
        # 测试任务完成通知
        result = await notifier.notify_task_complete(
            "task_123",
            {
                "duration": "5s",
                "status": "success",
                "files_created": ["file1.py", "file2.py"],
                "tests_passed": 10
            }
        )
        print(f"任务完成通知发送：{result}")
        
        # 测试错误通知
        result = await notifier.notify_task_error(
            "task_456",
            "File not found",
            "Traceback: ... "
        )
        print(f"错误通知发送：{result}")
        
        # 测试系统通知
        result = await notifier.notify_system(
            "系统状态报告",
            "- 响应时间：100ms\n- 任务数：5\n- 成功率：100%"
        )
        print(f"系统通知发送：{result}")
    
    asyncio.run(test_notifiers())
