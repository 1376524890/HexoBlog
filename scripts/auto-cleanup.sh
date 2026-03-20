#!/bin/bash
# 自动清理过期备份脚本
# 每天 12:30 执行一次，清理 7 天前的备份

set -e

BACKUP_DIR="$HOME/.openclaw/backup"
LOG_FILE="$HOME/.openclaw/backup/backup.log"

# 记录日志
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "开始清理过期备份..."

# 找到 7 天前的备份文件
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "workspace-backup-*.tar.gz" -mtime +7 -type f)

if [ -z "$OLD_BACKUPS" ]; then
    log "没有需要清理的过期备份"
else
    COUNT=0
    for file in $OLD_BACKUPS; do
        SIZE=$(du -sh "$file" | cut -f1)
        log "删除过期备份：$file (大小：$SIZE)"
        rm -f "$file"
        COUNT=$((COUNT + 1))
    done
    log "共清理 $COUNT 个过期备份"
fi

log "清理任务完成！"
