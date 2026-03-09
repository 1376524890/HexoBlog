#!/usr/bin/env python3
"""
记忆文件安全检查脚本
功能：在执行任何记忆操作前检查文件完整性和安全性
"""

import os
import subprocess
from datetime import datetime

# 配置
MEMORY_DIR = "memory"
BACKUPS_DIR = "memory/backups"
ARCHIVES_DIR = "life/archives"
GIT_WORKSPACE = "/home/claw/.openclaw/workspace"

def check_git_status():
    """检查 Git 状态"""
    print("🔍 检查 Git 状态...")
    os.chdir(GIT_WORKSPACE)
    
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"⚠️ Git 命令失败：{result.stderr}")
            return False
        
        lines = result.stdout.strip().split("\n")
        modified_files = []
        deleted_files = []
        
        for line in lines:
            if not line:
                continue
            status = line[:2].strip()
            file_path = line[3:].strip()
            
            if "deleted" in status or status == "D ":
                deleted_files.append(file_path)
            elif "modified" in status:
                modified_files.append(file_path)
        
        if deleted_files:
            print(f"❌ 发现已删除的文件：{deleted_files}")
            return False
        
        if "MEMORY.md" in modified_files:
            print(f"⚠️ MEMORY.md 已被修改但未提交")
            return False
        
        print("✅ Git 状态检查通过")
        return True
        
    except Exception as e:
        print(f"❌ Git 检查失败：{e}")
        return False

def check_backup_exists(filename):
    """检查备份是否存在"""
    print(f"🔍 检查 {filename} 的备份...")
    
    # 检查 memory/backups/
    backup_path = f"{BACKUPS_DIR}/{filename}.bak"
    if os.path.exists(backup_path):
        print(f"✅ 找到备份：{backup_path}")
        return True
    
    # 检查最新的备份
    try:
        backups = sorted(
            [f for f in os.listdir(BACKUPS_DIR) if f.startswith(filename)],
            reverse=True
        )
        if backups:
            print(f"✅ 找到备份：{backups[0]}")
            return True
    except FileNotFoundError:
        pass
    
    print(f"⚠️ 没有找到 {filename} 的备份")
    return False

def check_file_exists(filename):
    """检查文件是否存在"""
    print(f"🔍 检查 {filename} 是否存在...")
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在：{filename}")
        return False
    
    size = os.path.getsize(filename)
    print(f"✅ 文件存在：{filename} ({size} bytes)")
    
    # 检查文件大小是否异常
    if size < 100:
        print(f"⚠️ 文件大小异常 (仅 {size} bytes)")
        return False
    
    return True

def check_git_has_changes():
    """检查 Git 是否有未提交的更改"""
    print("🔍 检查 Git 是否有未提交的更改...")
    os.chdir(GIT_WORKSPACE)
    
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"⚠️ Git 命令失败")
            return False
        
        if result.stdout.strip():
            print("⚠️ 发现未提交的更改:")
            for line in result.stdout.strip().split("\n"):
                print(f"  - {line}")
            return False
        
        print("✅ Git 干净，没有未提交的更改")
        return True
        
    except Exception as e:
        print(f"❌ Git 检查失败：{e}")
        return False

def run_safety_check():
    """运行完整的安全检查"""
    print("=" * 60)
    print("🧠 记忆文件安全检查")
    print("=" * 60)
    
    checks = [
        ("Git 状态", check_git_status),
        ("文件存在性", lambda: check_file_exists("MEMORY.md")),
        ("备份存在性", lambda: check_backup_exists("MEMORY.md")),
        ("Git 干净状态", check_git_has_changes),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print()
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {name} 检查失败：{e}")
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✅ 所有安全检查通过！可以安全操作。")
    else:
        print("❌ 安全检查未通过！请先解决问题。")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    os.chdir(GIT_WORKSPACE)
    
    # 检查命令行参数
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("⚡ 强制跳过安全检查")
        exit(0)
    
    # 运行安全检查
    if not run_safety_check():
        print()
        print("🛑 请解决以下问题后再继续：")
        print("  1. 检查 Git 状态：git status")
        print("  2. 备份重要文件")
        print("  3. 确保文件存在")
        print()
        print("如需跳过检查（不推荐），使用 --force 参数")
        exit(1)
