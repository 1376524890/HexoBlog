#!/bin/bash
# 记忆检查点脚本 - 自动生成记忆检查点
# 用于定期整理和归档记忆文件

set -e

TIMESTAMP=$(date +%Y%m%d)
CHECKPOINT_DIR="/home/claw/.openclaw/workspace/memory"
CHECKPOINT_FILE="$CHECKPOINT_DIR/checkpoint-${TIMESTAMP}.md"
MEMORY_FILE="/home/claw/.openclaw/workspace/MEMORY.md"

echo "=== 记忆检查点开始 ==="
echo "时间：$(date -u +%Y-%m-%d\ %H:%M:%S\ UTC)"
echo "检查点文件：$CHECKPOINT_FILE"

# 创建检查点文件
cat > "$CHECKPOINT_FILE" << EOF
# 记忆检查点 - $TIMESTAMP

## 检查时间
$(date -u +%Y-%m-%d\ %H:%M:%S\ UTC)

## 检查内容

### 内存状态
EOF

# 添加 MEMORY.md 大小和最后修改时间
if [ -f "$MEMORY_FILE" ]; then
    MEMORY_SIZE=$(stat -c%s "$MEMORY_FILE" 2>/dev/null || echo "0")
    MEMORY_MTIME=$(stat -c%Y "$MEMORY_FILE" 2>/dev/null || echo "0")
    MEMORY_DATE=$(date -u -d @$MEMORY_MTIME +%Y-%m-%d\ %H:%M\ UTC 2>/dev/null || echo "未知")
    echo "- MEMORY.md 大小：$MEMORY_SIZE bytes" >> "$CHECKPOINT_FILE"
    echo "- MEMORY.md 最后修改：$MEMORY_DATE" >> "$CHECKPOINT_FILE"
else
    echo "- MEMORY.md 不存在" >> "$CHECKPOINT_FILE"
fi

# 统计记忆文件数量
MEMORY_COUNT=$(find "$CHECKPOINT_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
echo "- 记忆文件总数：$MEMORY_COUNT" >> "$CHECKPOINT_FILE"

# 添加最近的日志文件
echo "" >> "$CHECKPOINT_FILE"
echo "### 最近日志文件" >> "$CHECKPOINT_FILE"
ls -1t "$CHECKPOINT_DIR"/*.md 2>/dev/null | head -5 | while read f; do
    echo "- $(basename "$f")" >> "$CHECKPOINT_FILE"
done

echo "" >> "$CHECKPOINT_FILE"
echo "---" >> "$CHECKPOINT_FILE"
echo "*此检查点由 cron:memory-checkpoint 自动创建*" >> "$CHECKPOINT_FILE"

# Git 提交
cd /home/claw/.openclaw/workspace
git add memory/checkpoint-${TIMESTAMP}.md
git commit -m "memory: 自动创建记忆检查点 $TIMESTAMP" 2>/dev/null || echo "Git commit 失败（可能没有更改）"

# 推送到远程
git push origin main 2>/dev/null || git push backup main 2>/dev/null || echo "Push 失败"

echo ""
echo "=== 记忆检查点完成 ==="
echo "检查点文件：$CHECKPOINT_FILE"
cat "$CHECKPOINT_FILE"
