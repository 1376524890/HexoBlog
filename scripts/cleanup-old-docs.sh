#!/bin/bash
# 清理 OpenClaw 学习总结文档
# 创建时间：2026-03-11 12:35 UTC
# 说明：删除重复和过期的学习总结文档

set -e

# 定义要删除的文档（重复的）
declare -a TO_DELETE=(
    # 2026-03-09 重复
    "docs/OpenClaw-Report-2026-03-09.md"
    "docs/OpenClaw-Report-2026-03-09-Final.md"
    "docs/OpenClaw-Report-Final-2026-03-09.md"
    "docs/OpenClaw-Study-Summary-2026-03-09.md"
    
    # 2026-03-10 重复
    "docs/OpenClaw-Report-2026-03-10.md"
    "docs/OpenClaw-Report-2026-03-10-Final.md"
    "docs/OpenClaw-Report-Final-2026-03-10.md"
    "docs/OpenClaw-Study-Completion-2026-03-10.md"
    
    # 其他重复
    "docs/OpenClaw-Report-Final-Preparation.md"
    "docs/OpenClaw-Report-Summary.md"
)

echo "🔍 检查要删除的文件..."
for file in "${TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ 存在：$file"
    else
        echo "⚠️ 不存在：$file"
    fi
done

# 使用 trash 而不是 rm，确保可恢复
echo ""
echo "🗑️ 开始清理（使用 trash 确保可恢复）..."
for file in "${TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        trash "$file"
        echo "✅ 已移动：$file"
    fi
done

echo ""
echo "✅ 清理完成！"
echo "💡 提示：如果后悔，可以从回收站恢复这些文件。"
