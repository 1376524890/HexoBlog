#!/bin/bash
#==============================================================================
# 御坂妹妹 17 号开机自启配置脚本
# 御坂妹妹 18 号 - 守护进程管理器
#==============================================================================

CONFIG_DIR="/home/claw/.config/systemd/user"
MANAGER_SCRIPT="/home/claw/.openclaw/workspace/skills/security-audit/scripts/guardian-manager.sh"

echo "=========================================="
echo "🛡️  御坂妹妹 17 号开机自启配置"
echo "=========================================="

# 方法 1: 使用 crontab
echo ""
echo "📋 配置 crontab 开机启动..."
(crontab -l 2>/dev/null | grep -v "guardian-manager.sh"; echo "@reboot /bin/bash $MANAGER_SCRIPT start") | crontab -
echo "✅ crontab 配置完成"

# 方法 2: 尝试 systemd（需要密码，可能失败）
echo ""
echo "⚙️  尝试配置 systemd..."
if sudo systemctl --user status audit-guardian > /dev/null 2>&1; then
    echo "✅ systemd 已配置"
else
    echo "⚠️  systemd 配置需要密码，已跳过（但 crontab 已生效）"
fi

echo ""
echo "=========================================="
echo "🎉 配置完成！守护进程将在下次登录时自动启动"
echo "=========================================="
