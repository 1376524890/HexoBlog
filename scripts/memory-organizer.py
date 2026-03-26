#!/usr/bin/env python3
# Memory organization script - Three-tier architecture automated maintenance
# For 御坂妹妹 17 号 - Memory Organization Specialist

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = WORKSPACE / "life" / "archives"
BACKUP_DIR = WORKSPACE / "memory" / "backups"

# 保留策略
BACKUP_RETENTION_DAYS = 3
ARCHIVE_RETENTION_DAYS = 7

# 最大文件大小 (字符)
MAX_FILE_SIZE = 3000

def read_daily_log(date_str: str) -> str:
    """读取每日日志文件"""
    log_file = MEMORY_DIR / f"{date_str}.md"
    if log_file.exists():
        content = log_file.read_text(encoding='utf-8')
        logger.info(f"读取每日日志：{log_file.name} ({len(content)} 字符)")
        return content
    logger.warning(f"未找到日志文件：{log_file.name}")
    return ""

def extract_essence(log_content: str) -> list:
    """从日志中提取精华内容"""
    essence = []
    
    # 重要标记
    markers = {
        "✅": "Completed",
        "⚡": "Important",
        "🎯": "Goal",
        "📝": "Record",
        "🔧": "Technical",
        "🧠": "Memory",
        "💡": "Insight",
        "🚀": "Progress",
    }
    
    for line in log_content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        for marker, category in markers.items():
            if marker in line:
                essence.append({
                    "marker": marker,
                    "category": category,
                    "content": line
                })
                break
    
    logger.info(f"提取到 {len(essence)} 条精华内容")
    return essence

def backup_file(file_path: Path) -> str:
    """备份文件，返回备份路径"""
    try:
        # 创建备份目录
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"{file_path.name}.{timestamp}.bak"
        
        # 执行备份
        shutil.copy2(file_path, backup_path)
        
        # 验证备份完整性
        if backup_path.exists() and backup_path.stat().st_size > 0:
            logger.info(f"备份成功：{backup_path.name}")
            return str(backup_path)
        else:
            logger.error(f"备份文件为空或不存在")
            raise Exception("Backup verification failed")
            
    except Exception as e:
        logger.error(f"备份失败：{e}")
        raise

def cleanup_old_backups(days: int = 3) -> int:
    """清理旧备份"""
    if not BACKUP_DIR.exists():
        return 0
    
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    
    try:
        for file in BACKUP_DIR.glob("*.bak"):
            if file.stat().st_mtime < cutoff.timestamp():
                file.unlink()
                deleted += 1
                logger.info(f"清理旧备份：{file.name}")
    except Exception as e:
        logger.error(f"清理备份时出错：{e}")
    
    return deleted

def cleanup_old_archives(days: int = 7) -> int:
    """清理过期归档"""
    if not ARCHIVE_DIR.exists():
        return 0
    
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    
    try:
        for file in ARCHIVE_DIR.glob("*.md"):
            if file.stat().st_mtime < cutoff.timestamp():
                file.unlink()
                deleted += 1
                logger.info(f"清理过期归档：{file.name}")
    except Exception as e:
        logger.error(f"清理归档时出错：{e}")
    
    return deleted

def move_to_archive(file_path: Path):
    """移动文件到长期归档"""
    try:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        
        # 检查文件是否已归档
        if file_path.parent == ARCHIVE_DIR:
            logger.info(f"文件已归档：{file_path.name}")
            return
        
        # 生成归档文件名
        timestamp = datetime.now().strftime("%Y%m%d")
        new_name = f"{file_path.name}.{timestamp}.archived"
        
        # 移动文件
        shutil.move(str(file_path), str(ARCHIVE_DIR / new_name))
        logger.info(f"归档文件：{new_name}")
        
    except Exception as e:
        logger.error(f"归档文件时出错：{e}")

def update_memory_file(essence: list) -> bool:
    """更新 MEMORY.md"""
    if not MEMORY_FILE.exists():
        logger.error("MEMORY.md 不存在")
        return False
    
    try:
        content = MEMORY_FILE.read_text(encoding='utf-8')
        
        # 查找 Recent Achievements 部分
        recent_section_marker = "## 📝 近期成果"
        if recent_section_marker not in content:
            logger.warning("未找到近期成果部分")
            return False
        
        # 构建新的近期成果部分
        new_essence_lines = []
        for item in essence:
            new_essence_lines.append(f"- {item['marker']} **{item['category']}** {item['content']}")
        
        # 检查是否超过最大长度
        new_section = f"""
## 📝 近期成果 ({datetime.now().strftime("%Y-%m-%d")})

{chr(10).join(new_essence_lines)}
"""
        
        # 截断过长的内容
        if len(new_section) > MAX_FILE_SIZE:
            new_section = new_section[:MAX_FILE_SIZE - 10] + "\n... (内容过长，已截断)"
            logger.warning(f"内容过长，已截断至 {MAX_FILE_SIZE} 字符")
        
        # 替换旧内容
        start_idx = content.find(recent_section_marker)
        if start_idx >= 0:
            next_section_marker = "## 🏠"
            end_idx = content.find(next_section_marker, start_idx)
            if end_idx > 0:
                new_content = content[:start_idx] + new_section + content[end_idx:]
                MEMORY_FILE.write_text(new_content, encoding='utf-8')
                logger.info("已更新 MEMORY.md")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"更新 MEMORY.md 时出错：{e}")
        return False

def run_dry_run():
    """干运行模式 - 仅展示计划"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_content = read_daily_log(today)
    
    if not log_content:
        print("无内容可整理")
        return
    
    essence = extract_essence(log_content)
    
    print(f"\n🧠 记忆整理 - 干运行模式")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ 计划处理：{today}.md")
    print(f"📊 计划提取：{len(essence)} 条精华")
    print(f"🔐 计划备份：MEMORY.md")
    print(f"📝 计划更新：MEMORY.md 近期成果")
    print(f"🗑️ 计划清理：3 天内备份")
    print(f"📦 计划归档：7 天前日志")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("干运行完成 - 未执行实际修改")

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🧠 记忆整理脚本启动 - 御坂妹妹 17 号")
    logger.info(f"⏰ 时间：{datetime.now()}")
    logger.info("=" * 60)
    
    try:
        # 1. 读取最新每日日志
        today = datetime.now().strftime("%Y-%m-%d")
        log_content = read_daily_log(today)
        
        if not log_content:
            logger.warning("没有找到今日日志，跳过整理")
            return
        
        # 2. 提取精华
        essence = extract_essence(log_content)
        
        if not essence:
            logger.warning("没有可提取的精华内容")
            return
        
        # 3. 备份当前文件
        backup_path = backup_file(MEMORY_FILE)
        
        # 4. 更新 MEMORY.md
        if update_memory_file(essence):
            # 5. 清理旧备份
            deleted_backups = cleanup_old_backups(days=BACKUP_RETENTION_DAYS)
            if deleted_backups:
                logger.info(f"🗑️ 清理了 {deleted_backups} 个旧备份")
            
            # 6. 清理过期归档
            deleted_archives = cleanup_old_archives(days=ARCHIVE_RETENTION_DAYS)
            if deleted_archives:
                logger.info(f"🗑️ 清理了 {deleted_archives} 个过期归档")
            
            # 7. 输出成功报告
            print("\n" + "=" * 60)
            print("🧠 记忆整理完成报告")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"✅ 处理文件：{today}.md")
            print(f"📊 提取精华：{len(essence)} 条内容")
            print(f"🔐 备份文件：{backup_path}")
            print(f"📝 更新状态：MEMORY.md 已更新")
            if deleted_backups:
                print(f"🗑️ 清理结果：{deleted_backups} 个旧备份")
            if deleted_archives:
                print(f"🗑️ 清理结果：{deleted_archives} 个过期归档")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("✨ 所有操作完成！御坂妹妹 17 号随时待命！⚡")
            print("=" * 60 + "\n")
        else:
            logger.error("更新失败")
            
    except Exception as e:
        logger.error(f"记忆整理失败：{e}")
        print(f"\n⚠️ 记忆整理遇到问题：{e}")
        print("请检查日志或联系御坂美琴一号 ⚡")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        run_dry_run()
    else:
        main()
