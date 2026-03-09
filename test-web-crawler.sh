#!/bin/bash
# 测试 web-crawler 配置

echo "🌐 测试御坂妹妹 16 号 (web-crawler) 配置"
echo "======================================"

# 检查配置文件
echo ""
echo "1️⃣  检查配置文件"
if [ -f ~/.openclaw/config/agents/web-crawler/openclaw.json ]; then
    echo "✅ 配置文件存在：~/.openclaw/config/agents/web-crawler/openclaw.json"
    echo ""
    echo "📄 配置文件内容:"
    cat ~/.openclaw/config/agents/web-crawler/openclaw.json | jq '.' 2>/dev/null || cat ~/.openclaw/config/agents/web-crawler/openclaw.json
else
    echo "❌ 配置文件不存在"
    exit 1
fi

# 检查 agent 注册
echo ""
echo "2️⃣  检查 agent 注册状态"
openclaw agents list 2>&1 | grep -A5 "web-crawler" || echo "❌ web-crawler 未注册"

# 检查工作空间
echo ""
echo "3️⃣  检查工作空间"
ls -la ~/.openclaw/agents/web-crawler/ || echo "❌ 工作空间不存在"

echo ""
echo "======================================"
echo "✅ 配置验证完成！"
echo "御坂妹妹 16 号准备就绪！🌐⚡"
