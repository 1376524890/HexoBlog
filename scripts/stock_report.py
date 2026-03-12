#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股市数据定时报告 - 每 3 小时自动执行 (修复版)
在 stock-analysis 虚拟环境中运行

Author: 御坂美琴一号
"""

import subprocess
import sys
import os
from datetime import datetime

SCRIPT_DIR = '/home/claw/.openclaw/skills/stock-analysis'
REPORT_SCRIPT = f'{SCRIPT_DIR}/report_generator.py'

def generate_and_send_report():
    """生成报告并输出到标准输出"""
    
    # 使用虚拟环境运行报告生成器
    cmd = [
        f'{SCRIPT_DIR}/venv/bin/python3',
        REPORT_SCRIPT
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        report = result.stdout
        if result.returncode != 0:
            report = f"""# 📈 股市数据报告

**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

---

## ⚠️ 数据获取异常

**错误信息**: {result.stderr}

**建议操作**:
1. 检查网络连接
2. 等待 API 恢复
3. 稍后重试

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

御坂美琴一号 ⚡
"""
        
        # 输出到标准输出（由 OpenClaw 捕获并发送到飞书）
        print(report)
        return 0
        
    except Exception as e:
        error_msg = f"""# 📈 股市数据报告

**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

---

## ❌ 执行失败

**错误信息**: {str(e)}

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

御坂美琴一号 ⚡
"""
        print(error_msg)
        return 1

def main():
    """主函数"""
    print("🔄 正在生成股市数据报告...")
    return generate_and_send_report()

if __name__ == "__main__":
    sys.exit(main())
