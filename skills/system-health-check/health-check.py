#!/usr/bin/env python3
"""
System Health Check - 系统健康检查脚本

用于检测 OpenClaw 系统整体健康状态
"""

import subprocess
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional


class SystemHealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {},
            "warnings": []
        }
    
    def check_gateway(self) -> Dict:
        """检查网关状态"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            is_running = "Runtime: running" in result.stdout
            pid_exists = "PID" in result.stdout
            port_listening = "port=" in result.stdout
            
            return {
                "status": "healthy" if is_running else "unhealthy",
                "pid_exists": pid_exists,
                "port_listening": port_listening,
                "message": "网关正常运行" if is_running else "网关未运行"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查失败：{str(e)}"
            }
    
    def check_agents(self) -> Dict:
        """检查 Agent 状态"""
        try:
            result = subprocess.run(
                ["openclaw", "agents", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析 Agent 列表
            lines = result.stdout.split('\n')
            agent_count = sum(1 for line in lines if '- ' in line and 'Identity:' in line)
            active_count = result.stdout.count("✅ 活跃")
            
            # 如果 agent_count 为 0，尝试另一种解析方式
            if agent_count == 0:
                agent_count = result.stdout.count("Agent ID")
            
            return {
                "total_agents": max(agent_count, active_count),
                "active_agents": active_count,
                "status": "healthy" if active_count >= 10 else "degraded",
                "message": f"{active_count}/{max(agent_count, active_count)}个 Agent 活跃"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查失败：{str(e)}"
            }
    
    def check_sessions(self) -> Dict:
        """检查会话状态"""
        try:
            result = subprocess.run(
                ["openclaw", "sessions"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析会话数量
            session_line = [l for l in result.stdout.split('\n') if "Sessions" in l and "active" in l]
            if session_line:
                session_count = int(session_line[0].split("active")[0].split()[-1])
            else:
                session_count = 0
            
            return {
                "active_sessions": session_count,
                "status": "healthy" if session_count > 0 else "warning",
                "message": f"{session_count}个活跃会话"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查失败：{str(e)}"
            }
    
    def check_channels(self) -> Dict:
        """检查通道状态"""
        try:
            result = subprocess.run(
                ["openclaw", "channels", "status"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            is_connected = "connected" in result.stdout.lower() or "active" in result.stdout.lower()
            feishu_connected = "feishu" in result.stdout.lower() and "connected" in result.stdout.lower()
            
            return {
                "channels_connected": is_connected,
                "feishu_connected": feishu_connected,
                "status": "healthy" if is_connected else "warning",
                "message": "通道连接正常" if is_connected else "通道未连接"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查失败：{str(e)}"
            }
    
    def check_cron(self) -> Dict:
        """检查定时任务"""
        try:
            result = subprocess.run(
                ["openclaw", "cron", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析定时任务数量
            task_lines = [l for l in result.stdout.split('\n') if "cron:" in l.lower()]
            task_count = len(task_lines)
            failed_tasks = result.stdout.count("failed")
            
            return {
                "total_tasks": task_count,
                "failed_tasks": failed_tasks,
                "status": "healthy" if failed_tasks == 0 else "warning",
                "message": f"{task_count}个定时任务"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查失败：{str(e)}"
            }
    
    def check_security(self) -> Dict:
        """检查安全配置"""
        try:
            result = subprocess.run(
                ["openclaw", "status"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 统计安全警告
            critical_issues = result.stdout.count("CRITICAL")
            warn_issues = result.stdout.count("WARN")
            info_issues = result.stdout.count("INFO")
            
            return {
                "critical_issues": critical_issues,
                "warn_issues": warn_issues,
                "info_issues": info_issues,
                "status": "healthy" if critical_issues == 0 else "warning",
                "message": f"{critical_issues}严重，{warn_issues}警告，{info_issues}信息"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查失败：{str(e)}"
            }
    
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        checks = {
            "gateway": self.check_gateway(),
            "agents": self.check_agents(),
            "sessions": self.check_sessions(),
            "channels": self.check_channels(),
            "cron": self.check_cron(),
            "security": self.check_security()
        }
        
        self.results["checks"] = checks
        
        # 计算总体健康状态
        healthy_count = sum(1 for c in checks.values() if c["status"] == "healthy")
        error_count = sum(1 for c in checks.values() if c["status"] == "error")
        
        if error_count > 0:
            overall_status = "error"
        elif healthy_count == len(checks):
            overall_status = "healthy"
        else:
            overall_status = "warning"
        
        self.results["summary"] = {
            "overall_status": overall_status,
            "healthy_checks": healthy_count,
            "total_checks": len(checks),
            "success_rate": f"{healthy_count/len(checks)*100:.1f}%"
        }
        
        return self.results
    
    def generate_report(self) -> str:
        """生成报告"""
        checks = self.results["checks"]
        summary = self.results["summary"]
        
        report = f"""# 🎉 系统健康检查报告

**检查时间**: {self.results["timestamp"]}
**检查者**: 御坂美琴一号 ⚡

---

## ✅ 总体状态

**总检测率**: **{summary["success_rate"]}** ✅

### 检测结果

| 项目 | 状态 | 详情 |
|------|------|------|
| 网关 | {checks["gateway"]["status"]} | {checks["gateway"]["message"]} |
| Agent | {checks["agents"]["status"]} | {checks["agents"]["message"]} |
| 会话 | {checks["sessions"]["status"]} | {checks["sessions"]["message"]} |
| 通道 | {checks["channels"]["status"]} | {checks["channels"]["message"]} |
| 定时任务 | {checks["cron"]["status"]} | {checks["cron"]["message"]} |
| 安全 | {checks["security"]["status"]} | {checks["security"]["message"]} |

---

## 💡 建议

{self._generate_recommendations()}

---

**检查完成**: {datetime.now().isoformat()}
**状态**: {summary["overall_status"].upper()}

御坂美琴一号 ⚡
"""
        return report
    
    def _generate_recommendations(self) -> str:
        """生成建议"""
        checks = self.results["checks"]
        recommendations = []
        
        if checks["security"]["critical_issues"] > 0:
            recommendations.append("🔴 **高优先级**: 解决安全配置问题")
        
        if checks["gateway"]["status"] != "healthy":
            recommendations.append("🔴 **紧急**: 重启网关服务")
        
        if checks["agents"]["active_agents"] < checks["agents"]["total_agents"]:
            recommendations.append("🟡 **中优先级**: 检查未活跃的 Agent")
        
        if checks["sessions"]["active_sessions"] == 0:
            recommendations.append("🟡 **中优先级**: 检查会话状态")
        
        if not recommendations:
            return "✅ 系统运行正常，无需操作"
        
        return "\n".join(recommendations)


def main():
    """主函数"""
    checker = SystemHealthChecker()
    results = checker.run_all_checks()
    
    # 输出报告
    report = checker.generate_report()
    print(report)
    
    # 如果状态不正常，输出 JSON 结果
    if results["summary"]["overall_status"] != "healthy":
        print("\n--- JSON 结果 ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
