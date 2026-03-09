#!/bin/bash
#==============================================================================
# 御坂妹妹 17 号守护进程启动脚本
# 御坂妹妹 18 号 - 守护进程管理器
#==============================================================================

LOG_FILE="/home/claw/.openclaw/workspace/memory/guardian-launch.log"
PID_FILE="/tmp/audit-guardian-manager.pid"
GUARDIAN_SCRIPT="/home/claw/.openclaw/workspace/skills/security-audit/scripts/audit-guardian.sh"

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

start_guardian() {
    # 检查是否已在运行
    if pgrep -f "audit-guardian.sh" > /dev/null; then
        log "⚡ 御坂妹妹 17 号守护进程已在运行，跳过启动"
        return 0
    fi
    
    log "🚀 启动御坂妹妹 17 号守护进程..."
    
    # 使用 nohup 后台启动
    nohup bash "$GUARDIAN_SCRIPT" > /home/claw/.openclaw/workspace/memory/audit-guardian-nohup.log 2>&1 &
    
    local pid=$!
    echo $pid > "$PID_FILE"
    
    sleep 2
    
    if pgrep -f "audit-guardian.sh" > /dev/null; then
        log "✅ 御坂妹妹 17 号守护进程启动成功！PID: $pid"
        return 0
    else
        log "❌ 御坂妹妹 17 号守护进程启动失败！"
        return 1
    fi
}

stop_guardian() {
    log "🛑 停止御坂妹妹 17 号守护进程..."
    pkill -f "audit-guardian.sh"
    rm -f "$PID_FILE"
    log "✅ 御坂妹妹 17 号守护进程已停止"
}

restart_guardian() {
    log "🔄 重启御坂妹妹 17 号守护进程..."
    stop_guardian
    sleep 3
    start_guardian
}

status_guardian() {
    if pgrep -f "audit-guardian.sh" > /dev/null; then
        local pid=$(pgrep -f "audit-guardian.sh" | head -1)
        echo "✅ 御坂妹妹 17 号守护进程正在运行 (PID: $pid)"
        return 0
    else
        echo "❌ 御坂妹妹 17 号守护进程未运行"
        return 1
    fi
}

case "$1" in
    start)
        start_guardian
        ;;
    stop)
        stop_guardian
        ;;
    restart)
        restart_guardian
        ;;
    status)
        status_guardian
        ;;
    *)
        echo "用法：$0 {start|stop|restart|status}"
        exit 1
        ;;
esac
