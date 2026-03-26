#!/bin/bash
# 阿里云百炼平台 API 密钥测试脚本（curl 版本）

API_KEY="sk-510e5aa92b3b495b833d54a161bb8c82"
API_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

echo "🔍 阿里云百炼平台 API 密钥测试 (curl)"
echo "测试时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "API 密钥：${API_KEY:0:10}...${API_KEY: -10}"
echo ""

curl -X POST "$API_URL" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-plus",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "请回复'测试成功'四个字。"}
    ],
    "max_tokens": 10,
    "temperature": 0.7
  }' | python3 -m json.tool 2>/dev/null || curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-plus",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "请回复'测试成功'四个字。"}
    ],
    "max_tokens": 10,
    "temperature": 0.7
  }'
