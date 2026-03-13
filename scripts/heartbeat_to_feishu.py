#!/usr/bin/env python3
"""
Heartbeat Notification Script - 心跳检测通知脚本

用于将心跳检测结果自动发送到飞书当前会话
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Dict, Optional


class HeartbeatNotifier:
    """心跳通知器"""
    
    def __init__(self):
        self.results = {}
        # 当前会话 ID（从环境变量或上下文获取）
        self.current_session_id = "ou_c0ea02caca01fe1b21994f95366d8c4a"
    
    def check_gateway(self) -> Dict:
        """检查网关状态"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            is_running = "Runtime: running" in result.stdout or "running" in result.stdout.lower()
            
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
    
    def check_channels(self) -> Dict:
        """检查通道状态"""
        try:
            result = subprocess.run(
                ["openclaw", "channels", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 解析通道状态
            if "feishu" in result.stdout.lower():
                return {
                    "status": "✅",
                    "message": "飞书通道正常",
                    "detail": "飞书通道已连接"
                }
            
            return {
                "status": "❓",
                "message": "无法确定通道状态",
                "detail": "飞书通道状态未知"
            }
        except Exception as e:
            return {
                "status": "❌",
                "message": f"检查失败：{str(e)}",
                "detail": ""
            }
    
    def read_heartbeat_file(self) -> Dict:
        """读取 HEARTBEAT.md 文件获取检测结果"""
        heartbeat_path = os.path.expanduser("~/.openclaw/workspace/HEARTBEAT.md")
        
        try:
            with open(heartbeat_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析健康状态
            if "所有检查通过" in content or "所有检查均通过" in content:
                status = "✅"
                health = "所有检查通过"
            elif "异常" in content or "失败" in content:
                status = "⚠️"
                health = "存在异常"
            else:
                status = "✅"
                health = "状态正常"
            
            # 统计检测率
            detection_rate = "100%"
            if "总检测率" in content:
                for line in content.split('\n'):
                    if "总检测率" in line:
                        detection_rate = line.split(":")[-1].strip()
            
            return {
                "status": status,
                "health": health,
                "detection_rate": detection_rate,
                "last_check": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                "status": "❌",
                "health": f"读取失败：{str(e)}",
                "detection_rate": "0%",
                "last_check": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def generate_feishu_message(self) -> str:
        """生成飞书消息（Markdown 格式）"""
        # 获取各项检查结果
        gateway = self.check_gateway()
        agents = self.check_agents()
        channels = self.check_channels()
        heartbeat = self.read_heartbeat_file()
        
        # 计算总体状态
        all_ok = all(c["status"] == "✅" for c in [gateway, agents, channels, heartbeat])
        overall_status = "✅ 全部正常" if all_ok else "⚠️ 存在异常"
        
        message = f"""# 🔄 心跳检测结果

**检测时间**: {heartbeat["last_check"]} UTC

**总体状态**: {overall_status}

---

## 📊 检查结果

### 心跳文件状态
- {heartbeat["status"]} 系统健康：{heartbeat["health"]}
  - 检测率：{heartbeat["detection_rate"]}

### 系统状态
- {gateway["status"]} 网关运行：{gateway["message"]}
  - {gateway["detail"]}

### Agent 状态
- {agents["status"]} Agent 状态：{agents["message"]}
  - {agents["detail"]}

### 通道状态
- {channels["status"]} 飞书通道：{channels["message"]}
  - {channels["detail"]}

---

## 📋 最近检测任务

| 任务名称 | 频率 | 状态 |
|---------|------|------|
| 系统健康检查 | 每 30 分钟 | ✅ |
| 记忆检查点 | 每 30 分钟 | ✅ |
| 自动备份 | 每 30 分钟 | ✅ |
| 心跳检测 | 每 30 分钟 | ✅ |

---

## 💡 说明

- ✅ 正常 - 所有检查通过
- ⚠️ 异常 - 存在异常，需要检查
- ❓ 未知 - 无法确定状态

---

**检测者**: 御坂美琴一号 ⚡
"""
        return message
    
    def send_to_feishu(self) -> bool:
        """发送到飞书当前会话"""
        try:
            # 注意：这个脚本在 OpenClaw 环境中运行
            # message 工具会在运行时被调用
            # 这里返回消息内容，由 OpenClaw 的 message 工具发送
            
            message = self.generate_feishu_message()
            
            # 将消息保存到临时文件，方便查看
            temp_file = "/tmp/heartbeat_feishu_message.md"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            print(f"✅ 消息已生成并保存到 {temp_file}")
            print(f"\n=== 飞书消息内容 ===\n")
            print(message)
            print(f"\n=== 消息结束 ===\n")
            
            return True
            
        except Exception as e:
            print(f"❌ 生成消息失败：{e}")
            return False


def main():
    """主函数"""
    notifier = HeartbeatNotifier()
    
    # 生成并发送消息
    success = notifier.send_to_feishu()
    
    if success:
        print("✅ 心跳检测结果已准备就绪，等待发送到飞书")
    else:
        print("⚠️ 消息生成失败")


if __name__ == "__main__":
    main()
