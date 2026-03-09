#!/usr/bin/env python3
"""
claude_code_connector.py - 真正的 Claude Code 集成工具

版本：V1.0
创建时间：2026-03-09 13:00 UTC
用途：提供真实的 Claude Code 外部专家咨询功能

说明：
- 直接调用本地 Claude Code
- 替代不可用的 sessions_send（Feishu）
- 实现真正的"外部专家咨询"
"""

import subprocess
import sys
from datetime import datetime


def call_claude_code(
    task: str,
    context_file: str = None,
    permission_mode: str = "bypassPermissions"
) -> str:
    """
    调用 Claude Code 进行分析
    
    Args:
        task: 要完成的任务描述
        context_file: 上下文文件路径（可选）
        permission_mode: 权限模式
    
    Returns:
        Claude Code 的响应文本
    """
    # 构建命令
    cmd = [
        "claude",
        "--print",
        f"--permission-mode={permission_mode}"
    ]
    
    # 添加上下文文件（如果有）
    if context_file:
        cmd.extend(["--file", context_file])
    
    # 添加任务
    cmd.append(task)
    
    print(f"🤖 正在调用 Claude Code...")
    print(f"📝 任务：{task[:100]}...")
    
    try:
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )
        
        # 检查返回值
        if result.returncode != 0:
            print(f"⚠️ Claude Code 返回错误：{result.stderr}")
            return f"错误：{result.stderr}"
        
        # 返回结果
        return result.stdout
        
    except subprocess.TimeoutExpired:
        print("⏰ Claude Code 调用超时（5 分钟）")
        return "超时：Claude Code 调用超过 5 分钟"
    except FileNotFoundError:
        print("❌ Claude Code 未安装")
        return "错误：请安装 Claude Code (npm install -g @anthropic-ai/claude-code)"
    except Exception as e:
        print(f"❌ 调用 Claude Code 失败：{e}")
        return f"错误：{str(e)}"


def format_claude_request(plan: str, socratic_questions: str) -> str:
    """
    格式化向 Claude 的请求
    
    Args:
        plan: 当前优化方案
        socratic_questions: 苏格拉底式反问结果
    
    Returns:
        格式化的请求文本
    """
    return f"""
当前优化方案（外部专家咨询）:
{plan}

苏格拉底式反问结果:
{socratic_questions}

请从以下角度评估：
1. 技术可行性
2. 架构合理性
3. 潜在风险
4. 改进建议

请以 Markdown 格式输出。
"""


def integrate_claude_feedback(claude_feedback: str, iteration: int) -> None:
    """
    集成 Claude 反馈到迭代记录
    
    Args:
        claude_feedback: Claude 的反馈
        iteration: 当前迭代编号
    """
    record_path = f"memory/archives/iteration-{iteration:02d}.md"
    
    # 读取现有记录（如果有）
    try:
        with open(record_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    
    # 添加 Claude 反馈
    claude_section = f"""
## 外部专家咨询（Claude Code）
**时间**: {datetime.now().isoformat()}

{claude_feedback}
"""
    
    # 更新记录
    new_content = content + claude_section
    
    with open(record_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Claude 反馈已记录到 {record_path}")


if __name__ == "__main__":
    # 示例用法
    plan = "引入幂律任务分配机制"
    socratic = """
问题 1: 为什么需要这个改进？
- 回答：现有架构是静态任务分配
- 追问：哪些局限性？
- 再追问：如何证明？
"""
    
    request = format_claude_request(plan, socratic)
    feedback = call_claude_code(request)
    
    if feedback and not feedback.startswith("错误"):
        print("\n" + "="*50)
        print("🤖 Claude Code 反馈:")
        print("="*50)
        print(feedback[:500] + "...")
    else:
        print("\n❌ Claude Code 调用失败")
