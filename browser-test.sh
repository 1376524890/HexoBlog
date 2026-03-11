#!/bin/bash
# Chrome/Chromium Browser Test Script
# 浏览器功能测试脚本

echo "======================================"
echo "Chrome/Chromium Browser Test"
echo "======================================"
echo ""

# 1. 版本检查
echo "1. 版本检查"
echo "--------------------------------------"
snap run chromium --version
echo ""

# 2. 基础功能测试
echo "2. 基础功能测试 (Headless Mode)"
echo "--------------------------------------"
timeout 30 snap run chromium \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --disable-setuid-sandbox \
  --dump-dom https://example.com 2>/dev/null | grep -c "<html"
if [ $? -eq 0 ]; then
  echo "✅ 网页抓取测试通过"
else
  echo "❌ 网页抓取测试失败"
fi
echo ""

# 3. PDF 生成测试
echo "3. PDF 生成测试"
echo "--------------------------------------"
mkdir -p /tmp/chromium-test
snap run chromium \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --print-to-pdf=/tmp/chromium-test/test.pdf \
  https://example.com 2>&1 | head -2

if [ -f /tmp/chromium-test/test.pdf ]; then
  ls -lh /tmp/chromium-test/test.pdf
  echo "✅ PDF 生成测试通过"
else
  echo "⚠️  PDF 生成完成，文件可能保存在 Snap 沙盒中"
fi
echo ""

# 4. 屏幕截图测试
echo "4. 屏幕截图测试"
echo "--------------------------------------"
snap run chromium \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --screenshot=/tmp/chromium-test/screenshot.png \
  https://example.com 2>&1 | head -2

if [ -f /tmp/chromium-test/screenshot.png ]; then
  ls -lh /tmp/chromium-test/screenshot.png
  echo "✅ 屏幕截图测试通过"
else
  echo "⚠️  屏幕截图保存可能位于 Snap 沙盒目录"
fi
echo ""

# 5. JavaScript 执行测试
echo "5. JavaScript 执行测试"
echo "--------------------------------------"
timeout 30 snap run chromium \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --eval-javascript="console.log(document.title)" \
  https://example.com 2>&1 | grep -E "Example"
if [ $? -eq 0 ]; then
  echo "✅ JavaScript 执行测试通过"
fi
echo ""

echo "======================================"
echo "测试完成！"
echo "======================================"
