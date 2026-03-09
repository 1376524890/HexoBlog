#!/usr/bin/env python3
# Memory organization script - Three-tier architecture automated maintenance
# Runs in OpenClaw main session, every 6 hours, 3-day backup retention

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = WORKSPACE / "life" / "archives"
BACKUP_DIR = WORKSPACE / "memory" / "backups"

# Retention policies
BACKUP_RETENTION_DAYS = 3
ARCHIVE_RETENTION_DAYS = 7

def read_daily_log(date_str: str) -> str:
    """Read daily log file"""
    log_file = MEMORY_DIR / f"{date_str}.md"
    if log_file.exists():
        return log_file.read_text(encoding='utf-8')
    return ""

def extract_essence(log_content: str) -> list:
    """Extract essence from log content"""
    essence = []
    
    # Find important markers
    markers = [
        ("✅", "Completed"),
        ("⚡", "Important"),
        ("🎯", "Goal"),
        ("📝", "Record"),
        ("🔧", "Technical"),
    ]
    
    for line in log_content.split('\n'):
        for marker, category in markers:
            if marker in line:
                essence.append({
                    "marker": marker,
                    "category": category,
                    "content": line.strip()
                })
                break
    
    return essence

def backup_file(file_path: Path) -> str:
    """Backup file, return backup path"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{file_path.name}.{timestamp}.bak"
    shutil.copy2(file_path, backup_path)
    return str(backup_path)

def cleanup_old_backups(days: int = 3):
    """Clean old backups"""
    if not BACKUP_DIR.exists():
        return
    
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    
    for file in BACKUP_DIR.glob("*.bak"):
        if file.stat().st_mtime < cutoff.timestamp():
            file.unlink()
            deleted += 1
    
    return deleted

def cleanup_old_archives(days: int = 7):
    """Clean expired archives"""
    if not ARCHIVE_DIR.exists():
        return
    
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    
    for file in ARCHIVE_DIR.glob("*.md"):
        if file.stat().st_mtime < cutoff.timestamp():
            file.unlink()
            deleted += 1
    
    return deleted

def move_to_archive(file_path: Path):
    """Move file to long-term archive"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    new_name = f"{file_path.name}.{timestamp}.archived"
    shutil.move(str(file_path), str(ARCHIVE_DIR / new_name))

def update_memory_file(essence: list):
    """Update MEMORY.md"""
    if not MEMORY_FILE.exists():
        return
    
    content = MEMORY_FILE.read_text(encoding='utf-8')
    
    # Find Recent Achievements section
    recent_section_marker = "## 📝 近期成果"
    if recent_section_marker not in content:
        return
    
    # Build new Recent Achievements section
    new_essence_lines = []
    for item in essence:
        new_essence_lines.append(f"- {item['marker']} **{item['category']}** {item['content']}")
    
    new_section = f"""
## 📝 近期成果 ({datetime.now().strftime("%Y-%m-%d")})

{chr(10).join(new_essence_lines)}
"""
    
    # Replace old content
    start_idx = content.find(recent_section_marker)
    if start_idx >= 0:
        next_section_marker = "## 🏠"
        end_idx = content.find(next_section_marker, start_idx)
        if end_idx > 0:
            new_content = content[:start_idx] + new_section + content[end_idx:]
            MEMORY_FILE.write_text(new_content, encoding='utf-8')

def main():
    """Main function"""
    print(f"Memory organization script started - {datetime.now()}")
    
    # 1. Read latest daily log
    today = datetime.now().strftime("%Y-%m-%d")
    log_content = read_daily_log(today)
    
    if not log_content:
        print("No daily log found for today")
        return
    
    # 2. Extract essence
    essence = extract_essence(log_content)
    print(f"Extracted {len(essence)} essence items")
    
    if not essence:
        print("No essence content to extract")
        return
    
    # 3. Backup current file
    backup_path = backup_file(MEMORY_FILE)
    print(f"Backed up MEMORY.md to {backup_path}")
    
    # 4. Update MEMORY.md
    update_memory_file(essence)
    print("Updated MEMORY.md")
    
    # 5. Clean old backups
    deleted_backups = cleanup_old_backups(days=BACKUP_RETENTION_DAYS)
    if deleted_backups:
        print(f"Cleaned {deleted_backups} old backups")
    
    # 6. Clean expired archives
    deleted_archives = cleanup_old_archives(days=ARCHIVE_RETENTION_DAYS)
    if deleted_archives:
        print(f"Cleaned {deleted_archives} expired archives")
    
    print("Memory organization completed successfully!")

if __name__ == "__main__":
    main()
