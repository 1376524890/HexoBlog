#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 系统学习 - 自动化记忆整理脚本
用于整理 OpenClaw 学习相关的记忆文件

作者：御坂美琴一号 ⚡
"""

import os
from datetime import datetime, timedelta

# 路径定义
LEARNING_DIR = "/home/claw/.openclaw/workspace/docs"
BACKUP_DIR = "/home/claw/.openclaw/workspace/.learnings"

def create_backup(filename):
    """创建学习总结备份"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/{filename}.{timestamp}.bak"
    
    # 读取源文件
    with open(f"{LEARNING_DIR}/{filename}", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 写入备份
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ 已备份：{backup_path}")
    return backup_path

def summarize_learning_files():
    """汇总学习文件信息"""
    learning_files = []
    
    # 遍历 docs 目录
    for file in os.listdir(LEARNING_DIR):
        if file.startswith("OpenClaw") and file.endswith(".md"):
            file_path = os.path.join(LEARNING_DIR, file)
            file_size = os.path.getsize(file_path)
            
            learning_files.append({
                "filename": file,
                "size": file_size,
                "size_human": f"{file_size / 1024:.1f} KB"
            })
    
    # 按大小排序
    learning_files.sort(key=lambda x: x["size"], reverse=True)
    
    return learning_files

def print_summary(learning_files):
    """打印汇总信息"""
    print("=" * 60)
    print("🧠 OpenClaw 系统学习笔记汇总")
    print("=" * 60)
    print()
    
    # 基本信息
    total_files = len(learning_files)
    total_size = sum(f["size"] for f in learning_files)
    
    print(f"📊 文件统计:")
    print(f"   - 学习文件总数：{total_files}")
    print(f"   - 总大小：{total_size / 1024:.1f} KB")
    print()
    
    # 前 5 个最大的文件
    print(f"📚 前 5 个学习文件:")
    for i, f in enumerate(learning_files[:5], 1):
        print(f"   {i}. {f['filename']}")
        print(f"      大小：{f['size_human']}")
    print()
    
    # 创建备份
    print("💾 创建备份...")
    for f in learning_files[:3]:  # 备份前 3 个最大的文件
        create_backup(f["filename"])
    print()
    
    print("=" * 60)
    print("✨ OpenClaw 学习总结完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        learning_files = summarize_learning_files()
        print_summary(learning_files)
    except Exception as e:
        print(f"❌ 错误：{e}")
