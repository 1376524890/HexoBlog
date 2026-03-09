# 御坂妹妹 17 号开机自启配置
# 御坂妹妹 18 号 - 守护进程管理器

# 在用户登录时自动启动守护进程
if ! pgrep -f "audit-guardian.sh" > /dev/null 2>&1; then
    nohup bash /home/claw/.openclaw/workspace/skills/security-audit/scripts/audit-guardian.sh \
        > /home/claw/.openclaw/workspace/memory/audit-guardian-nohup.log 2>&1 &
fi
