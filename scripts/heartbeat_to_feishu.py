#!/usr/bin/env python3
"""
Heartbeat Notification Script - 心跳检测通知脚本

用于将心跳检测结果自动发送到飞书当前会话
"""

import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional


class HeartbeatNotifier:
    """心跳通知器"""
    
    def __init__(self):
        self.results = {}
    
    def get_current_session_key(self) -> Optional[str]:
        """获取当前会话 Key"""
        try:
            result = subprocess.run(
                ["openclaw", "sessions"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 解析最近的飞书会话
            lines = result.stdout.split('\n')
            for line in lines:
                if 'feishu' in line.lower() and 'active' in line.lower():
                    # 提取会话 key
                    parts = line.split()
                    for part in parts:
                        if part.startswith('agent:main:feishu'):
                            return part
            
            # 如果找不到，返回默认值
            return "agent:main:feishu:direct:heartbeat"
            
        except Exception as e:
            print(f"获取会话失败：{e}")
            return None
    
    def check_gateway(self) -> Dict:
        """检查网关状态"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            is_running = "Runtime: running" in result.stdout
            
            return {
                "status": "✅" if is_running else "❌",
                "message": "网关正常运行" if is_running else "网关未运行",
                "detail": result.stdout[:200] if is_running else "需要检查"
            }
        except Exception as e:
            return {
                "status": "❌",
                "message": f"检查失败：{str(e)}",
                "detail": ""
            }
    
    def check_agents(self) -> Dict:
        """检查 Agent 状态"""
        try:
            result = subprocess.run(
                ["openclaw", "agents", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 统计 Agent 数量
            agent_count = result.stdout.count("Identity:")
            active_count = result.stdout.count("✅ 活跃")
            
            return {
                "status": "✅",
                "message": f"全部活跃 ({active_count}/{agent_count})",
                "detail": f"{agent_count}个 Agent, {active_count}个活跃"
            }
        except Exception as e:
            return {
                "status": "❌",
                "message": f"检查失败：{str(e)}",
                "detail": ""
            }
    
    def check_sessions(self) -> Dict:
        """检查会话状态"""
        try:
            result = subprocess.run(
                ["openclaw", "sessions"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 解析会话数量
            for line in result.stdout.split('\n'):
                if "Sessions listed:" in line:
                    count = line.split("listed:")[1].strip()
                    return {
                        "status": "✅",
                        "message": f"{count}个活跃会话",
                        "detail": count
                    }
            
            return {
                "status": "❓",
                "message": "无法解析会话数量",
                "detail": ""
            }
        except Exception as e:
            return {
                "status": "❌",
                "message": f"检查失败：{str(e)}",
                "detail": ""
            }
    
    def check_channels(self) -> Dict:
        """检查通道状态"""
        try:
            result = subprocess.run(
                ["openclaw", "channels", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            feishu_status = "enabled" in result.stdout and "configured" in result.stdout
            
            return {
                "status": "✅" if feishu_status else "❌",
                "message": "飞书通道正常" if feishu_status else "飞书通道异常",
                "detail": "飞书通道状态"
            }
        except Exception as e:
            return {
                "status": "❌",
                "message": f"检查失败：{str(e)}",
                "detail": ""
            }
    
    def generate_report(self) -> str:
        """生成飞书报告"""
        checks = {
            "gateway": self.check_gateway(),
            "agents": self.check_agents(),
            "sessions": self.check_sessions(),
            "channels": self.check_channels()
        }
        
        # 计算总体状态
        all_ok = all(c["status"] == "✅" for c in checks.values())
        overall_status = "✅ 全部正常" if all_ok else "⚠️ 存在异常"
        
        report = f"""# 🔄 心跳检测结果

**检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

**总体状态**: {overall_status}

---

## 📊 检查结果

### 系统状态
- {checks["gateway"]["status"]} 网关运行：{checks["gateway"]["message"]}
  - {checks["gateway"]["detail"]}

### Agent 状态
- {checks["agents"]["status"]} Agent 状态：{checks["agents"]["message"]}
  - {checks["agents"]["detail"]}

### 会话状态
- {checks["sessions"]["status"]} 会话状态：{checks["sessions"]["message"]}
  - {checks["sessions"]["detail"]}

### 通道状态
- {checks["channels"]["status"]} 通道状态：{checks["channels"]["message"]}
  - {checks["channels"]["detail"]}

---

## 💡 状态说明

- ✅ 正常 - 所有检查通过
- ⚠️ 异常 - 存在异常，需要检查
- ❓ 未知 - 无法确定状态

---

**检测者**: 御坂美琴一号 ⚡
"""
        return report
    
    def send_to_feishu(self, session_key: str) -> bool:
        """发送到飞书当前会话"""
        try:
            from sessions_send import sessions_send
            
            report = self.generate_report()
            
            result = sessions_send({
                "sessionKey": session_key,
                "message": report
            })
            
            print(f"✅ 报告已发送到会话：{session_key}")
            return True
            
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False


def main():
    """主函数"""
    notifier = HeartbeatNotifier()
    
    # 获取当前会话
    session_key = notifier.get_current_session_key()
    print(f"当前会话：{session_key}")
    
    # 生成报告
    report = notifier.generate_report()
    print("=== 心跳检测报告中 ===")
    print(report)
    print("=== 报告结束 ===\n")
    
    # 发送到飞书
    if session_key:
        success = notifier.send_to_feishu(session_key)
        if success:
            print("✅ 报告已发送到飞书")
        else:
            print("⚠️ 报告发送失败，但已在控制台输出")
    else:
        print("⚠️ 无法获取会话 Key，报告已在控制台输出")


if __name__ == "__main__":
    main()
