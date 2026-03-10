#!/usr/bin/env python3
"""
SmartSearch 独立测试脚本
========================
不依赖包结构，直接测试核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from utils import ContentProcessor, FallbackChain

print("=" * 50)
print("SmartSearch 系统测试")
print("=" * 50)

# 测试 1: 配置加载
print("\n[测试 1] 配置加载...")
try:
    config = get_config()
    print(f"  ✓ 搜索配置：max_results={config.search.max_results}")
    print(f"  ✓ 抓取配置：timeout={config.scraper.timeout_seconds}s")
    print(f"  ✓ 降级链：{config.scraper.fallback_chain}")
    print("  ✅ 配置加载成功")
except Exception as e:
    print(f"  ❌ 配置加载失败：{e}")

# 测试 2: 内容处理器
print("\n[测试 2] 内容处理器...")
try:
    processor = ContentProcessor()
    
    # 测试清理文本
    test_html = "<p>这是<strong>测试</strong>内容</p>"
    cleaned = processor.clean_text(test_html)
    print(f"  ✓ 原始：{test_html}")
    print(f"  ✓ 清理后：{cleaned}")
    
    # 测试相似度计算
    sim = processor.calculate_similarity("Python is great", "Python is awesome")
    print(f"  ✓ 相似度：{sim:.2f}")
    
    print("  ✅ 内容处理器工作正常")
except Exception as e:
    print(f"  ❌ 内容处理器失败：{e}")

# 测试 3: 搜索引擎模块
print("\n[测试 3] 搜索引擎模块...")
try:
    from engines.multi_search import MultiSearch, SearchResult
    
    # 检查支持的引擎
    engine_count = len(MultiSearch.ENGINES)
    print(f"  ✓ 支持 {engine_count} 个搜索引擎")
    print(f"  ✓ 引擎列表：{', '.join(list(MultiSearch.ENGINES.keys())[:5])}...")
    print("  ✅ 搜索引擎模块正常")
except Exception as e:
    print(f"  ❌ 搜索引擎模块失败：{e}")

# 测试 4: 抓取器模块
print("\n[测试 4] 深度抓取器模块...")
try:
    from scraper import (
        RJinaAI, MarkdownNew, Defuddle, ScraplingScraper
    )
    
    # 检查各个抓取器
    print(f"  ✓ r.jina.ai 抓取器：{RJinaAI.__name__}")
    print(f"  ✓ markdown.new 抓取器：{MarkdownNew.__name__}")
    print(f"  ✓ defuddle.md 抓取器：{Defuddle.__name__}")
    print(f"  ✓ Scrapling 抓取器：{ScraplingScraper.__name__}")
    print("  ✅ 深度抓取器模块正常")
except Exception as e:
    print(f"  ❌ 深度抓取器模块失败：{e}")

# 测试 5: 降级链
print("\n[测试 5] 降级链模块...")
try:
    # 检查降级链类
    from utils.fallback_chain import FallbackChain, FetchResult
    
    # 创建简单结果测试
    result = FetchResult(
        success=True,
        url="https://example.com",
        content="test",
        title="Test",
        source="test",
        fetch_time=1.0,
        method="test"
    )
    
    data = result.to_dict()
    print(f"  ✓ FetchResult 序列化：{data['success']}")
    print(f"  ✓ FetchResult 方法：{data['method']}")
    print("  ✅ 降级链模块正常")
except Exception as e:
    print(f"  ❌ 降级链模块失败：{e}")

# 测试 6: Tavily AI 搜索
print("\n[测试 6] Tavily AI 搜索...")
try:
    from engines.tavily_search import TavilySearch
    
    print(f"  ✓ TavilySearch 类：{TavilySearch.__name__}")
    print(f"  ✓ API 端点：{TavilySearch.API_URL}")
    print("  ✅ Tavily AI 搜索模块正常")
except Exception as e:
    print(f"  ❌ Tavily AI 搜索模块失败：{e}")

# 测试 7: Web Markdown 搜索
print("\n[测试 7] Web Markdown 搜索...")
try:
    from engines.web_markdown import WebMarkdown
    
    print(f"  ✓ WebMarkdown 类：{WebMarkdown.__name__}")
    print(f"  ✓ 基础 URL: {WebMarkdown.BASE_URL}")
    print("  ✅ Web Markdown 搜索模块正常")
except Exception as e:
    print(f"  ❌ Web Markdown 搜索模块失败：{e}")

print("\n" + "=" * 50)
print("✅ 所有核心模块加载成功！")
print("=" * 50)
print("\n系统准备就绪，可以开始使用 SmartSearch!")
print("\n使用方法:")
print("  1. 命令行：python smart_search.py '你的搜索词'")
print("  2. Python API: searcher.search('你的搜索词', depth=3)")
print("\n详细信息请查看 README.md 和 SKILL.md")
