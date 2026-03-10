#!/usr/bin/env python3
"""
SmartSearch 独立测试脚本
========================
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试 1: 配置
print("测试 1: 配置加载")
try:
    from config import get_config
    config = get_config()
    print(f"  ✓ max_results: {config.search.max_results}")
    print(f"  ✓ timeout: {config.scraper.timeout_seconds}s")
    print(f"  ✓ fallback_chain: {config.scraper.fallback_chain}")
    print("  ✅ 通过")
except Exception as e:
    print(f"  ❌ 失败：{e}")

# 测试 2: 内容处理器
print("\n测试 2: 内容处理器")
try:
    from utils.content_processor import ContentProcessor
    processor = ContentProcessor()
    test = processor.clean_text("<p>测试</p>")
    print(f"  ✓ 清理文本：{test}")
    sim = processor.calculate_similarity("test", "test")
    print(f"  ✓ 相似度：{sim}")
    print("  ✅ 通过")
except Exception as e:
    print(f"  ❌ 失败：{e}")

# 测试 3: 降级链
print("\n测试 3: 降级链")
try:
    from utils.fallback_chain import FallbackChain, FetchResult
    print(f"  ✓ FallbackChain: {FallbackChain.__name__}")
    result = FetchResult(success=True, url="test", content="test", source="test")
    print(f"  ✓ FetchResult: {result.to_dict()['success']}")
    print("  ✅ 通过")
except Exception as e:
    print(f"  ❌ 失败：{e}")

# 测试 4: 搜索引擎
print("\n测试 4: 搜索引擎模块")
try:
    from engines.multi_search import MultiSearch
    print(f"  ✓ MultiSearch: {MultiSearch.__name__}")
    print(f"  ✓ 引擎数量：{len(MultiSearch.ENGINES)}")
    print(f"  ✓ 引擎：{', '.join(list(MultiSearch.ENGINES.keys())[:5])}...")
    print("  ✅ 通过")
except Exception as e:
    print(f"  ❌ 失败：{e}")

# 测试 5: Tavily
print("\n测试 5: Tavily 搜索")
try:
    from engines.tavily_search import TavilySearch
    print(f"  ✓ TavilySearch: {TavilySearch.__name__}")
    print("  ✅ 通过")
except Exception as e:
    print(f"  ❌ 失败：{e}")

# 测试 6: Web Markdown
print("\n测试 6: Web Markdown 搜索")
try:
    from engines.web_markdown import WebMarkdown
    print(f"  ✓ WebMarkdown: {WebMarkdown.__name__}")
    print("  ✅ 通过")
except Exception as e:
    print(f"  ❌ 失败：{e}")

# 测试 7: 抓取器
print("\n测试 7: 深度抓取器")
try:
    from scraper.r_jina_ai import RJinaAI
    from scraper.markdown_new import MarkdownNew
    from scraper.defuddle import Defuddle
    from scraper.scrapling_scraper import ScraplingScraper
    
    print(f"  ✓ RJinaAI: {RJinaAI.__name__}")
    print(f"  ✓ MarkdownNew: {MarkdownNew.__name__}")
    print(f"  ✓ Defuddle: {Defuddle.__name__}")
    print(f"  ✓ ScraplingScraper: {ScraplingScraper.__name__}")
    print("  ✅ 通过")
except Exception as e:
    print(f"  ❌ 失败：{e}")

print("\n" + "=" * 50)
print("SmartSearch 核心模块测试完成!")
print("=" * 50)
