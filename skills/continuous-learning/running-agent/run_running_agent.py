#!/usr/bin/env python3
"""
持续运行 Agent - 可执行脚本
==========================

运行持续运行的 AI 项目发现 Agent

用法:
    python3 run_running_agent.py          # 启动持续运行模式
    python3 run_running_agent.py status   # 查看状态
    python3 run_running_agent.py report   # 查看待审批报告
    python3 run_running_agent.py approve  # 批准项目
    python3 run_running_agent.py reject   # 拒绝项目
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从 running-agent 模块导入
from running_agent import RunningAgent


def print_banner():
    """打印欢迎横幅"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║    ⚡ 持续运行 Agent - AI 项目发现与集成系统 ⚡             ║
║                                                           ║
║    御坂美琴的持续学习进化系统                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def main():
    """主函数"""
    # 打印横幅
    print_banner()
    
    # 创建 Agent 实例
    agent = RunningAgent()
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            command = ' '.join(sys.argv[1:])
            
            if command == 'status':
                print(agent.get_status())
            
            elif command == 'report':
                report = agent.approval_system.generate_approval_report()
                print(report)
            
            elif command == 'help':
                print("""
持续运行 Agent 命令:
  status     - 查看系统状态
  report     - 查看待审批报告  
  approve    - 批准项目集成 (approve #1 或 approve req_xxx)
  reject     - 拒绝项目集成 (reject #1 理由)
  list       - 列出待审批项目
  run        - 启动持续运行模式
  """)
            
            else:
                # 默认作为批准命令处理
                result = agent.process_command(command)
                print(result)
        
        else:
            # 默认启动持续运行模式
            print("\n🚀 启动持续运行模式...")
            print("按 Ctrl+C 停止\n")
            agent.run()
    
    except KeyboardInterrupt:
        print("\n\n👋 收到中断信号，正在关闭...")
        agent.close()
    
    except Exception as e:
        print(f"\n❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
        agent.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
