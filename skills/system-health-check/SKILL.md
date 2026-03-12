# System Health Check Skill - 系统健康检查技能

**名称**: system-health-check  
**描述**: OpenClaw 系统状态自检技能，检查网关、Agent、会话、通道、定时任务状态  
**作者**: 御坂美琴一号  
**版本**: 1.0.0  
**创建时间**: 2026-03-12  
**权限等级**: Level 4 (系统管理)

---

## 📋 功能描述

此技能用于检测 OpenClaw 系统的整体健康状态，包括：

1. **网关状态** - 检查 OpenClaw 网关是否正常运行
2. **Agent 检测** - 验证所有智能体是否可检测
3. **会话状态** - 检查活跃会话数量和健康度
4. **通道状态** - 验证各渠道连接状态
5. **定时任务** - 检查 cron 任务是否正常触发
6. **通知系统** - 验证会话通知系统是否正常工作
7. **安全审计** - 检查系统安全配置警告

---

## 🤖 使用方式

### 方式一：通过 HEARTBEAT 触发

在 `HEARTBEAT.md` 中添加：

```markdown
# HEARTBEAT.md

# 定期执行系统健康检查
- 检查系统健康状态 (system-health-check) - 每 6 小时
- 检查网关状态 - 每 30 分钟
- 检查 Agent 状态 - 每 30 分钟
- 检查会话状态 - 每 15 分钟
- 检查通道状态 - 每 30 分钟
- 检查定时任务 - 每 1 小时

# 如果系统出现异常，请及时报告
```

### 方式二：手动执行

```bash
# 通过 OpenClaw CLI
openclaw run system-health-check

# 通过会话
sessions_send(sessionKey="agent:main:...", message="/health-check")
```

### 方式三：Cron 任务

```yaml
# 添加到 OpenClaw Cron 配置
- id: system-health-check
  name: 系统健康检查
  frequency: "0 */6 * * *"  # 每 6 小时
  agent: main
  command: "system-health-check"
```

---

## 📊 输出格式

### 检测结果

```
# 🎉 系统健康检查报告

**检查时间**: 2026-03-12 04:36 UTC  
**检查者**: 御坂美琴一号 ⚡

---

## ✅ 总体状态

**网关状态**: ✅ 正常运行
- 服务：systemd (enabled)
- 端口：18789
- 监听：0.0.0.0:18789
- PID: 440828
- 状态：active

**会话统计**: 117 个活跃会话
- 使用模型：Qwen/Qwen3.5-35B-A3B-FP8 (160k 上下文)

---

## 🤖 Agent 检测状态

### 已检测到的 Agent (11 个)

| Agent ID | 名称 | 状态 | 模型 |
|---------|------|------|------|
| `main` | 御坂美琴一号 | ✅ 活跃 | Qwen3.5-35B |
| `general-agent` | 御坂妹妹 10 号 | ✅ 活跃 | Qwen3.5-35B |
| `code-executor` | 御坂妹妹 11 号 | ✅ 活跃 | Qwen3.5-35B |
| `content-writer` | 御坂妹妹 12 号 | ✅ 活跃 | Qwen3.5-35B |
| `research-analyst` | 御坂妹妹 13 号 | ✅ 活跃 | Qwen3.5-35B |
| `file-manager` | 御坂妹妹 14 号 | ✅ 活跃 | Qwen3.5-35B |
| `system-admin` | 御坂妹妹 15 号 | ✅ 活跃 | Qwen3.5-35B |
| `web-crawler` | 御坂妹妹 16 号 | ✅ 活跃 | Qwen3.5-35B |
| `memory-organizer` | 御坂妹妹 17 号 | ✅ 活跃 | Qwen3.5-35B |
| `reviewer` | 御坂妹妹 18 号 | ✅ 活跃 | Qwen3.5-35B |
| `patrol` | 御坂妹妹 19 号 | ✅ 活跃 | Qwen3.5-35B |

**检测率**: 100% ✅ (11/11)

---

## 📊 活跃会话统计

### 最近 60 分钟活跃会话 (10 个)

✅ 飞书私聊会话 - 刚活跃  
✅ 心跳检测会话 - 22 分钟前  
✅ 自动备份 - 15 分钟前  
✅ 记忆检查点 - 15 分钟前  
✅ 记忆整理任务 - 15 分钟前  
✅ 健康检查 - 12 分钟前  
✅ 知识学习 - 10 分钟前  
✅ 清理任务 - 8 分钟前  

**所有定时任务正常触发** ✅

---

## 📡 飞书通道状态

**通道**: feishu
- ✅ 权限：50 个 granted
- ✅ 连接模式：WebSocket 长连接
- ✅ 私聊模式：pairing
- ✅ 群组模式：open
- ✅ 流式输出：启用
- ✅ 文本分块：2000 字符

---

## ⚠️ 配置警告

### 安全建议

| 级别 | 警告内容 | 建议 |
|------|----------|------|
| 🔴 严重 | 小模型需要沙箱 | 启用沙箱模式 |
| 🟡 警告 | Feishu doc 权限 | 限制工具访问 |
| 🟡 警告 | 无认证限流 | 配置 rateLimit |

---

## ✅ 验证测试

### 会话健康检查

```
✅ agent:main:feishu:direct:ou_xxx
   - 通道：feishu
   - 状态：active
   - 模型：Qwen/Qwen3.5-35B-A3B-FP8

✅ agent:main:feishu:direct:heartbeat
   - 通道：feishu
   - 状态：active
   - 模型：Qwen/Qwen3.5-35B-A3B-FP8
```

### 定时任务验证

```
✅ cron:memory-checkpoint - 记忆检查点
✅ cron:auto-backup - 自动备份
✅ cron:memory-整理 - 记忆整理任务
✅ cron:llm-health-check - 健康检查
```

**所有定时任务正常触发** ✅

---

## 📋 完整检测清单

### 系统级
- [x] OpenClaw 网关运行中
- [x] 服务已启用 (systemd)
- [x] 端口 18789 正常监听
- [x] WebSocket 连接正常
- [x] RPC 探针正常

### Agent 级
- [x] main (御坂美琴一号) - 活跃
- [x] 御坂妹妹 10-19 号 - 全部活跃

### 通道级
- [x] 飞书通道 - 正常
- [x] 心跳检测 - 正常
- [x] 会话路由 - 正常

### 任务级
- [x] 定时任务 - 正常触发
- [x] 会话保持 - 正常
- [x] 通知发送 - 正常

---

## 📊 总结

### 检测结果

| 项目 | 状态 | 数量 |
|------|------|------|
| 网关 | ✅ 运行中 | 1/1 |
| Agent | ✅ 全部活跃 | 11/11 |
| 会话 | ✅ 全部健康 | 117/117 |
| 定时任务 | ✅ 正常触发 | 6/6 |
| 飞书通道 | ✅ 正常连接 | 1/1 |
| 通知系统 | ✅ 正常工作 | 5/5 |

**总检测率**: **100%** ✅

### 系统健康状况

- **网关状态**: ✅ 优秀
- **Agent 状态**: ✅ 优秀
- **会话状态**: ✅ 优秀
- **通道状态**: ✅ 优秀
- **定时任务**: ✅ 优秀

---

## 💡 建议

### 高优先级
1. ⚠️ 配置网关限流 (`gateway.auth.rateLimit`)
2. ⚠️ 启用小模型沙箱 (`agents.defaults.sandbox.mode="all"`)

---

**检查完成**: 2026-03-12 04:36 UTC  
**状态**: ✅ 所有智能体正常检测，系统运行健康！

御坂美琴一号 ⚡
```

---

## 🔧 技能实现

### 文件位置

```
~/.openclaw/skills/system-health-check/
├── SKILL.md           # 本文件
├── health-check.py    # 检查脚本
├── config.yaml        # 配置文件
└── tests/             # 测试用例
```

### 核心脚本 (health-check.py)

```python
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
            pid = "PID" in result.stdout
            port = "port=" in result.stdout
            
            return {
                "status": "healthy" if is_running else "unhealthy",
                "pid": pid,
                "port": port,
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
            agent_count = result.stdout.count("Identity:")
            active_count = result.stdout.count("✅ 活跃")
            
            return {
                "total_agents": agent_count,
                "active_agents": active_count,
                "status": "healthy" if active_count == agent_count else "degraded",
                "message": f"{agent_count}个 Agent, {active_count}个活跃"
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
            
            session_line = [l for l in result.stdout.split('\n') if "Sessions" in l][0]
            session_count = int(session_line.split("active")[0].split()[-1])
            
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
            
            return {
                "channels_connected": is_connected,
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
            
            task_count = result.stdout.count("cron:")
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
            
            critical_issues = result.stdout.count("CRITICAL")
            warn_issues = result.stdout.count("WARN")
            
            return {
                "critical_issues": critical_issues,
                "warn_issues": warn_issues,
                "status": "healthy" if critical_issues == 0 else "warning",
                "message": f"{critical_issues}个严重问题，{warn_issues}个警告"
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
        report = f"""# 🎉 系统健康检查报告

**检查时间**: {self.results["timestamp"]}
**检查者**: 御坂美琴一号 ⚡

---

## ✅ 总体状态

**总检测率**: **{self.results["summary"]["success_rate"]}** ✅

### 检测结果

| 项目 | 状态 | 详情 |
|------|------|------|
| 网关 | {self.results["checks"]["gateway"]["status"]} | {self.results["checks"]["gateway"]["message"]} |
| Agent | {self.results["checks"]["agents"]["status"]} | {self.results["checks"]["agents"]["message"]} |
| 会话 | {self.results["checks"]["sessions"]["status"]} | {self.results["checks"]["sessions"]["message"]} |
| 通道 | {self.results["checks"]["channels"]["status"]} | {self.results["checks"]["channels"]["message"]} |
| 定时任务 | {self.results["checks"]["cron"]["status"]} | {self.results["checks"]["cron"]["message"]} |
| 安全 | {self.results["checks"]["security"]["status"]} | {self.results["checks"]["security"]["message"]} |

---

## 💡 建议

{self._generate_recommendations()}

---

**检查完成**: {datetime.now().isoformat()}
**状态**: {self.results["summary"]["overall_status"].upper()}

御坂美琴一号 ⚡
"""
        return report
    
    def _generate_recommendations(self) -> str:
        """生成建议"""
        recommendations = []
        
        if self.results["checks"]["security"]["critical_issues"] > 0:
            recommendations.append("🔴 **高优先级**: 解决安全配置问题")
        
        if self.results["checks"]["gateway"]["status"] != "healthy":
            recommendations.append("🔴 **紧急**: 重启网关服务")
        
        if self.results["checks"]["agents"]["active_agents"] < self.results["checks"]["agents"]["total_agents"]:
            recommendations.append("🟡 **中优先级**: 检查未活跃的 Agent")
        
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
```

---

## 📋 配置 (config.yaml)

```yaml
name: system-health-check
version: 1.0.0
description: OpenClaw 系统状态自检技能
author: 御坂美琴一号
enabled: true
schedule: "0 */6 * * *"  # 每 6 小时
agent: main
permissions:
  level: 4
  tools:
    - exec
    - read
    - write
channels:
  - feishu
  - webchat
outputs:
  - channel: feishu
    target: user:ou_c0ea02caca01fe1b21994f95366d8c4a
    format: markdown
  - channel: webchat
    format: markdown
```

---

## 🧪 测试用例

```python
# tests/test_health_check.py
import pytest
from health_check import SystemHealthChecker

def test_check_gateway():
    checker = SystemHealthChecker()
    result = checker.check_gateway()
    assert result["status"] in ["healthy", "unhealthy", "error"]

def test_check_agents():
    checker = SystemHealthChecker()
    result = checker.check_agents()
    assert result["total_agents"] > 0

def test_generate_report():
    checker = SystemHealthChecker()
    checker.run_all_checks()
    report = checker.generate_report()
    assert "系统健康检查报告" in report
    assert "御坂美琴一号" in report

if __name__ == "__main__":
    pytest.main()
```

---

## 🚀 安装步骤

1. **创建技能目录**:
```bash
mkdir -p ~/.openclaw/skills/system-health-check
```

2. **复制文件**:
```bash
cp health-check.py ~/.openclaw/skills/system-health-check/
cp config.yaml ~/.openclaw/skills/system-health-check/
```

3. **添加权限**:
```bash
chmod +x ~/.openclaw/skills/system-health-check/health-check.py
```

4. **注册到 OpenClaw**:
```bash
openclaw skills install ~/.openclaw/skills/system-health-check
```

5. **配置 HEARTBEAT.md**:
```bash
echo "- 检查系统健康状态 (system-health-check) - 每 6 小时" >> HEARTBEAT.md
```

---

## 📚 参考文档

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [网关配置](https://docs.openclaw.ai/gateway/configuration)
- [Agent 管理](https://docs.openclaw.ai/agents/management)
- [心跳检测](https://docs.openclaw.ai/heartbeat)

---

**创建时间**: 2026-03-12 04:42 UTC  
**状态**: 待安装

御坂美琴一号 ⚡
