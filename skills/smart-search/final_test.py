#!/usr/bin/env python3
"""
SmartSearch 最终测试脚本
========================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("SmartSearch 系统完整性测试")
print("=" * 50)

tests_passed = 0
tests_failed = 0

def test(name, code):
    global tests_passed, tests_failed
    try:
        code()
        print(f"✓ {name}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"✗ {name}: {e}")
        tests_failed += 1
        return False

# 测试 1: 配置
print("\n[1/8] 配置模块")
test("配置加载", lambda: __import__('config', fromlist=['get_config']).get_config())

# 测试 2: 内容处理器
print("\n[2/8] 内容处理器")
test("内容处理器", lambda: __import__('utils.content_processor', fromlist=['ContentProcessor']).ContentProcessor())

# 测试 3: 降级链
print("\n[3/8] 降级链")
test("降级链", lambda: __import__('utils.fallback_chain', fromlist=['FallbackChain', 'FetchResult']).FallbackChain())
test("FetchResult", lambda: __import__('utils.fallback_chain', fromlist=['FetchResult']).FetchResult(success=True, url="test", content="test", source="test"))

# 测试 4: 搜索引擎
print("\n[4/8] 搜索引擎")
test("MultiSearch", lambda: __import__('engines.multi_search', fromlist=['MultiSearch']).MultiSearch)
ms = __import__('engines.multi_search', fromlist=['MultiSearch']).MultiSearch
test(f"引擎数量 ({len(ms.ENGINES)})", lambda: len(ms.ENGINES) == 17)

# 测试 5: Tavily AI
print("\n[5/8] Tavily AI 搜索")
test("TavilySearch", lambda: __import__('engines.tavily_search', fromlist=['TavilySearch']).TavilySearch)

# 测试 6: Web Markdown
print("\n[6/8] Web Markdown 搜索")
test("WebMarkdown", lambda: __import__('engines.web_markdown', fromlist=['WebMarkdown']).WebMarkdown)

# 测试 7: 深度抓取器
print("\n[7/8] 深度抓取器")
test("RJinaAI", lambda: __import__('scraper.r_jina_ai', fromlist=['RJinaAI']).RJinaAI)
test("MarkdownNew", lambda: __import__('scraper.markdown_new', fromlist=['MarkdownNew']).MarkdownNew)
test("Defuddle", lambda: __import__('scraper.defuddle', fromlist=['Defuddle']).Defuddle)
test("ScraplingScraper", lambda: __import__('scraper.scrapling_scraper', fromlist=['ScraplingScraper']).ScraplingScraper)

# 测试 8: 项目结构
print("\n[8/8] 项目结构")
import os
required_files = [
    'smart_search.py', 'config.py', 'requirements.txt',
    'README.md', 'SKILL.md', 'QUICKSTART.md',
    'engines/__init__.py', 'engines/multi_search.py',
    'scraper/__init__.py', 'scraper/r_jina_ai.py',
    'utils/__init__.py', 'utils/content_processor.py',
    'utils/fallback_chain.py', 'utils/logger.py'
]
for f in required_files:
    test(f"文件 {f}", lambda f=f: os.path.exists(f))

print("\n" + "=" * 50)
print(f"测试结果：{tests_passed} 通过，{tests_failed} 失败")
print("=" * 50)

if tests_failed == 0:
    print("\n🎉 所有测试通过！SmartSearch 系统准备就绪！")
else:
    print(f"\n⚠️ 有 {tests_failed} 个测试失败，请检查上述错误。")
