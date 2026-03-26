#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼平台 API 密钥测试脚本
测试密钥：sk-510e5aa92b3b495b833d54a161bb8c82

使用方法：
    python test_alibaba_bailian.py

注意：
    - 此脚本仅用于测试密钥有效性，不会存储密钥
    - 建议将密钥保存在环境变量中，不要硬编码
"""

import os
import sys
import json
import requests
from datetime import datetime


# 配置
API_KEY = "sk-510e5aa92b3b495b833d54a161bb8c82"
API_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 测试模型列表（按优先级）
TEST_MODELS = [
    "qwen-max",
    "qwen-plus",
    "qwen-turbo",
    "qwen2.5-72b-instruct",
]


def test_api_key(api_key: str, model: str) -> dict:
    """
    测试 API 密钥是否有效
    
    Args:
        api_key: API 密钥
        model: 测试模型
    
    Returns:
        dict: 测试结果
    """
    result = {
        "model": model,
        "success": False,
        "error": None,
        "response_time_ms": None,
        "data": None
    }
    
    url = f"{API_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Service-Parameters": json.dumps({"enable_search": False})
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个有用的助手。"
            },
            {
                "role": "user",
                "content": "请回复'测试成功'四个字。"
            }
        ],
        "max_tokens": 10,
        "temperature": 0.7
    }
    
    start_time = datetime.now()
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        result["response_time_ms"] = round(response_time, 2)
        
        if response.status_code == 200:
            data = response.json()
            result["success"] = True
            result["data"] = {
                "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "usage": data.get("usage", {})
            }
        else:
            result["error"] = f"HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        result["error"] = "请求超时（30 秒）"
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"连接错误：{str(e)}"
    except Exception as e:
        result["error"] = f"未知错误：{str(e)}"
    
    return result


def print_result(result: dict):
    """打印测试结果"""
    print("\n" + "="*60)
    print(f"模型：{result['model']}")
    print(f"状态：{'✅ 成功' if result['success'] else '❌ 失败'}")
    print(f"响应时间：{result['response_time_ms']} ms")
    
    if result['error']:
        print(f"错误信息：{result['error']}")
    
    if result['data']:
        print(f"回复内容：{result['data']['content']}")
        if result['data'].get('usage'):
            usage = result['data']['usage']
            print(f"Token 使用：{usage.get('prompt_tokens', 0)} + {usage.get('completion_tokens', 0)} = {usage.get('total_tokens', 0)}")
    
    print("="*60 + "\n")


def main():
    """主函数"""
    print("\n🔍 阿里云百炼平台 API 密钥测试")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 密钥：{API_KEY[:10]}...{API_KEY[-10:]}")
    print(f"测试模型数：{len(TEST_MODELS)}")
    print()
    
    results = []
    
    for model in TEST_MODELS:
        print(f"🧪 测试模型：{model}")
        result = test_api_key(API_KEY, model)
        results.append(result)
        print_result(result)
        
        # 如果第一个模型成功，可以选择不继续测试其他模型
        if result['success']:
            print("✨ 第一个可用模型测试成功！")
            break
    
    # 统计
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print("\n" + "="*60)
    print("📊 测试总结")
    print(f"成功：{success_count}/{total_count}")
    print(f"失败：{total_count - success_count}/{total_count}")
    
    if success_count > 0:
        print("\n✅ API 密钥有效！可以使用。")
        successful_models = [r['model'] for r in results if r['success']]
        print(f"可用模型：{', '.join(successful_models)}")
    else:
        print("\n❌ API 密钥无效或所有模型都不可用。")
        print("\n可能的原因：")
        print("  1. API 密钥格式错误")
        print("  2. API 密钥已过期或被禁用")
        print("  3. 账户余额不足")
        print("  4. 网络连接问题")
        print("  5. 请求频率限制")
    
    print("="*60 + "\n")
    
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
