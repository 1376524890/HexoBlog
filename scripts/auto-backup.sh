#!/bin/bash
# 自动备份和清理脚本
# 每 6 小时执行一次，超过 7 天的备份自动清理

set -e

WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_DIR="$HOME/.openclaw/backup"
LOG_FILE="$HOME/.openclaw/backup/backup.log"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 记录日志
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "开始备份..."

# 生成备份文件名
BACKUP_FILE="$BACKUP_DIR/workspace-backup-$(date +%Y%m%d-%H%M%S).tar.gz"

# 执行备份
log "正在创建备份：$BACKUP_FILE"
cd "$WORKSPACE"

tar -czf "$BACKUP_FILE" \
    --exclude='*.tar.gz' \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='venv*' \
    --exclude='venv-playwright' \
    --exclude='*.log' \
    --exclude='tmp/' \
    --exclude='temp/' \
    --exclude='*.tmp' \
    .

# 计算备份大小
BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
log "备份完成！大小：$BACKUP_SIZE"

# 记录备份信息
echo "$(date +'%Y-%m-%d %H:%M:%S') - $BACKUP_FILE - $BACKUP_SIZE" >> "$BACKUP_DIR/backup-schedule.log"

log "备份任务完成！"
