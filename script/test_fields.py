#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 测试脚本
"""

import json
import glob
import os

OUTPUT_DIR = "/home/claw/.openclaw/workspace/output"

# 查找文件
files = glob.glob(os.path.join(OUTPUT_DIR, "问卷数据*.json"))
DATA_FILE = files[0]

# 读取数据
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

record = data[0]

# 测试字段名
field1 = "第 1 题_是否体验过"  # 正确的字段名
print(f"测试字段：{field1}")
print(f"值：{record.get(field1, 'N/A')}")

# 显示前 10 个字段
print("\n前 10 个字段:")
for i, key in enumerate(list(record.keys())[:10]):
    print(f"  {i+1}. '{key}': {record[key]}")
