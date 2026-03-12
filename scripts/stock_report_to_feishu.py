#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Market Report - 股市数据定时报告
每 3 小时获取 A 股市场数据并发送飞书通知

Author: 御坂美琴一号
"""

import subprocess
import sys
import os
from datetime import datetime

REPORT_SCRIPT = "/home/claw/.openclaw/skills/stock-analysis/report_generator.py"

def run_report():
    """运行股票报告脚本"""
    
    # 使用虚拟环境
    cmd = [
        "/home/claw/.openclaw/skills/stock-analysis/venv/bin/python3",
        REPORT_SCRIPT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 报告生成成功")
        return result.stdout
    else:
        print(f"❌ 报告生成失败：{result.stderr}")
        return None

def main():
    """主函数"""
    # 生成报告
    report = run_report()
    
    if report:
        try:
            # 发送到飞书
            from sessions_send import sessions_send
            
            result = sessions_send({
                "sessionKey": "agent:main:feishu:direct:ou_c0ea02caca01fe1b21994f95366d8c4a",
                "message": report
            })
            
            print(f"✅ 报告已发送，结果：{result}")
            return 0
            
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return 1
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
