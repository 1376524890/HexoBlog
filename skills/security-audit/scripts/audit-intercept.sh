#!/bin/bash
#==============================================================================
# Security Audit Intercept Script
# 御坂妹妹 17 号 - 安全审计代理
# 最高权限级别 - Level 5
#==============================================================================

# 配置
CONFIG_FILE="${CONFIG_FILE:-$(dirname "$0")/config/security-audit.conf}"
LOG_FILE="${LOG_FILE:-/home/claw/.openclaw/workspace/memory/security-audit.log}"
ALERT_CHANNEL="${ALERT_CHANNEL:-feishu}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#==============================================================================
# 日志函数
#==============================================================================
log_event() {
    local level=$1
    local action=$2
    local command=$3
    local result=$4
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] - [$level] - [$action] - [$command] - [$result]" >> "$LOG_FILE"
}

#==============================================================================
# 报警函数
#==============================================================================
send_alert() {
    local title=$1
    local content=$2
    
    # 发送飞书消息
    if [ "$ALERT_CHANNEL" = "feishu" ]; then
        # 这里可以集成飞书 webhook
        echo -e "${RED}⚠️ 安全警报发送中...${NC}"
    fi
    
    echo -e "${RED}$title${NC}"
    echo -e "${RED}$content${NC}"
    log_event "ALERT" "security_check" "$title" "sent"
}

#==============================================================================
# 危险命令检测
#==============================================================================
check_dangerous_command() {
    local cmd=$1
    
    # Level 5 - 御坂妹妹 17 号 专用 拦截规则
    local DANGEROUS_PATTERNS=(
        "rm -rf"
        "rm --no-preserve"
        "dd if="
        "mkfs"
        "fdisk"
        "parted"
        "chmod 000"
        "chown -R root:root"
        "truncate -s 0"
        "> /dev/sd"
        "> /dev/mmcblk"
        "echo > /etc/passwd"
        "echo > /etc/shadow"
        "iptables -F"
        "systemctl disable"
        "service stop"
        "git reset --hard"
        "git push --force"
        "git branch -D"
        "git clean -fdx"
        "format"
        "wipe"
        "erase"
    )
    
    local is_dangerous=0
    local dangerous_cmd=""
    
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if [[ "$cmd" == *"$pattern"* ]]; then
            is_dangerous=1
            dangerous_cmd=$pattern
            break
        fi
    done
    
    if [ $is_dangerous -eq 1 ]; then
        log_event "BLOCKED" "dangerous_command" "$cmd" "detected: $dangerous_cmd"
        return 0  # 检测到危险命令
    else
        return 1  # 安全
    fi
}

#==============================================================================
# 发送拦截警报
#==============================================================================
send_intercept_alert() {
    local command=$1
    local pattern=$2
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local alert_msg="
==============================================================================
⚠️ 安全拦截警报 - 御坂妹妹 17 号 (Level 5)
时间：$timestamp
==============================================================================

【命令详情】
命令：$command
触发规则：$pattern

【风险分析】
此命令被安全审计系统标记为高危操作！

根据安全审计协议，御坂妹妹 17 号已自动拦截该操作。

【可能造成的影响】
- 如果涉及删除操作：可能永久丢失重要数据
- 如果涉及系统配置：可能导致系统服务中断
- 如果涉及 Git 操作：可能破坏代码仓库完整性
- 如果涉及磁盘操作：可能损坏文件系统

【建议的替代方案】
1. 删除文件：使用 'trash' 命令（可恢复）
2. Git 操作：使用 'git reset HEAD' 或 'git revert'
3. 权限修改：先备份原权限，逐步调整
4. 服务管理：使用 'systemctl status' 先检查状态

【审批请求】
御坂大人，是否允许执行此命令？

请回复：
- 【允许】执行该命令
- 【拒绝】放弃该操作
- 【查看】了解更多细节

==============================================================================
御坂妹妹 17 号 - 安全审计代理
==============================================================================
"
    
    send_alert "安全拦截警报" "$alert_msg"
    log_event "INTERCEPTED" "dangerous_command" "$command" "alert_sent"
}

#==============================================================================
# 安全审计主函数
#==============================================================================
audit_command() {
    local command=$1
    
    echo "🔍 御坂妹妹 17 号 安全审计系统正在运行..."
    echo "检查命令：$command"
    echo "----------------------------------------"
    
    if check_dangerous_command "$command"; then
        echo -e "${RED}⚠️ 检测到危险命令！${NC}"
        echo "命令已拦截，正在向御坂大人发送警报..."
        
        # 提取触发规则
        local pattern=""
        for p in "rm -rf" "dd if=" "mkfs" "fdisk" "parted" "chmod 000" "chown -R root:root" \
                  "git reset --hard" "git push --force" "git clean -fdx" "format" "wipe" "erase"; do
            if [[ "$command" == *"$p"* ]]; then
                pattern=$p
                break
            fi
        done
        
        send_intercept_alert "$command" "$pattern"
        
        return 1  # 拦截成功
    else
        echo -e "${GREEN}✅ 安全检查通过${NC}"
        log_event "ALLOWED" "safe_command" "$command" "passed"
        return 0  # 允许执行
    fi
}

#==============================================================================
# 如果直接运行此脚本
#==============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        echo "用法：$0 <命令>"
        echo "示例：$0 'rm -rf /tmp/test'"
        exit 1
    fi
    
    audit_command "$*"
    exit_code=$?
    
    if [ $exit_code -eq 1 ]; then
        echo ""
        echo "💡 提示：御坂妹妹 17 号 已拦截此操作，请查看上面的警报消息。"
    fi
    
    exit $exit_code
fi
