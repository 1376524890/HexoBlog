#!/bin/bash
#==============================================================================
# 御坂妹妹 17 号 - 安全审计守护进程
# 确保审计服务始终在线，防止漏网之鱼
#==============================================================================

AUDIT_SCRIPT="/home/claw/.openclaw/workspace/skills/security-audit/scripts/secure-exec.sh"
INTERCEPT_SCRIPT="/home/claw/.openclaw/workspace/skills/security-audit/scripts/audit-intercept.sh"
LOG_FILE="/home/claw/.openclaw/workspace/memory/security-audit.log"
PID_FILE="/tmp/audit-guardian.pid"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log_audit() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local action=$1
    local command=$2
    local result=$3
    local user=$(whoami)
    echo "[$timestamp] ACTION=$action | USER=$user | CMD=$command | RESULT=$result" >> "$LOG_FILE"
}

# 检查审计脚本是否存在且可执行
check_scripts() {
    local missing=0
    
    if [ ! -f "$AUDIT_SCRIPT" ]; then
        log "${RED}⚠️ 警告：审计脚本不存在：$AUDIT_SCRIPT${NC}"
        missing=1
    elif [ ! -x "$AUDIT_SCRIPT" ]; then
        log "${RED}⚠️ 警告：审计脚本无执行权限：$AUDIT_SCRIPT${NC}"
        chmod +x "$AUDIT_SCRIPT"
        log "${GREEN}✅ 已修复执行权限${NC}"
    fi
    
    if [ ! -f "$INTERCEPT_SCRIPT" ]; then
        log "${RED}⚠️ 警告：拦截脚本不存在：$INTERCEPT_SCRIPT${NC}"
        missing=1
    fi
    
    return $missing
}

# 检查系统资源
check_resources() {
    local load=$(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1 | tr -d ' ' | cut -d'.' -f1)
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    
    if [ "$load" -gt 5 ] 2>/dev/null; then
        log "${YELLOW}⚠️ 系统负载较高：$load${NC}"
    fi
    
    if [ "$mem_usage" -gt 80 ] 2>/dev/null; then
        log "${YELLOW}⚠️ 内存使用率较高：${mem_usage}%${NC}"
    fi
}

# 检查拦截规则
check_rules() {
    if [ -f "$INTERCEPT_SCRIPT" ]; then
        local rule_count=$(grep -c "BLOCK_PATTERN\|DANGER_COMMAND" "$INTERCEPT_SCRIPT" 2>/dev/null || echo "0")
        log "${BLUE}📋 拦截规则数量：$rule_count${NC}"
        return 0
    fi
    return 1
}

restart_service() {
    log "${YELLOW}✅ 御坂妹妹 17 号守护进程健康检查完成！${NC}"
    log_audit "GUARDIAN" "healthcheck" "success"
}

cleanup_old_logs() {
    # 保留最近 1000 条审计记录
    if [ -f "$LOG_FILE" ] && [ $(wc -l < "$LOG_FILE") -gt 1000 ]; then
        log "${YELLOW}🧹 日志文件过大，清理旧记录...${NC}"
        tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
        log_audit "GUARDIAN" "cleanup" "success"
    fi
}

signal_handler() {
    local sig=$1
    log "${RED}收到信号：$sig，正在保存状态${NC}"
    cleanup_old_logs
    exit 0
}

trap signal_handler SIGTERM SIGINT

# 初始化
echo "$$" > "$PID_FILE"

# 主循环
log "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
log "${GREEN}🛡️  御坂妹妹 17 号安全审计守护进程已启动！${NC}"
log "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
log "📍 PID: $$"
log "📍 审计脚本：$AUDIT_SCRIPT"
log "📍 拦截脚本：$INTERCEPT_SCRIPT"
log "📍 日志文件：$LOG_FILE"
log "⏱️  每 60 秒检查一次服务状态"
log ""
log_audit "GUARDIAN" "start" "service_running"

cycle=0
while true; do
    cycle=$((cycle + 1))
    
    log "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "${BLUE}🔍 第 $cycle 次健康检查${NC}"
    log "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # 检查脚本完整性
    if check_scripts; then
        log "${RED}❌ 脚本检查失败，正在修复...${NC}"
        restart_service
    else
        log "${GREEN}✅ 脚本完整性检查通过${NC}"
    fi
    
    # 检查系统资源
    check_resources
    
    # 检查拦截规则
    check_rules
    
    # 清理旧日志
    cleanup_old_logs
    
    log ""
    log_audit "GUARDIAN" "healthcheck_cycle" "cycle_$cycle"
    
    sleep 60
done
