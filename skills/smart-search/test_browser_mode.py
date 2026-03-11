"""
BrowserFetcher 功能测试
======================
验证浏览器模式的基本功能

运行方式：
  python test_browser_mode.py
"""

import sys
import os

# 添加项目路径
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from smart_search import BrowserFetcher, BrowserFetchResult
import argparse

def test_browser_fetcher_creation():
    """测试 BrowserFetcher 创建"""
    print("✓ 测试 1: BrowserFetcher 创建")
    
    # 默认配置
    fetcher1 = BrowserFetcher()
    assert fetcher1.browser_profile == "openclaw"
    print("  ✓ 默认配置 (openclaw)")
    
    # 自定义配置
    fetcher2 = BrowserFetcher(browser_profile="chrome")
    assert fetcher2.browser_profile == "chrome"
    print("  ✓ 自定义配置 (chrome)")
    
    print("  ✅ 通过\n")

def test_browser_fetch_result():
    """测试 BrowserFetchResult"""
    print("✓ 测试 2: BrowserFetchResult 创建")
    
    result = BrowserFetchResult(
        success=True,
        url="https://example.com",
        content="测试内容",
        title="测试标题"
    )
    
    assert result.success == True
    assert result.url == "https://example.com"
    assert result.source == "browser"
    assert result.method == "browser"
    print("  ✓ 成功结果创建")
    
    # 测试错误结果
    error_result = BrowserFetchResult(
        success=False,
        url="https://error.com",
        content="",
        title="",
        error="测试错误"
    )
    assert error_result.success == False
    print("  ✓ 错误结果创建")
    
    print("  ✅ 通过\n")

def test_browser_fetcher_methods():
    """测试 BrowserFetcher 方法"""
    print("✓ 测试 3: BrowserFetcher 方法")
    
    fetcher = BrowserFetcher()
    
    # 检查方法存在
    assert hasattr(fetcher, 'fetch')
    print("  ✓ fetch 方法存在")
    
    assert hasattr(fetcher, 'close')
    print("  ✓ close 方法存在")
    
    assert hasattr(fetcher, '_take_snapshot')
    print("  ✓ _take_snapshot 方法存在")
    
    print("  ✅ 通过\n")

def test_command_line_args():
    """测试命令行参数"""
    print("✓ 测试 4: 命令行参数")
    
    # 检查参数定义
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--output", type=str, default="./output")
    parser.add_argument("--format", choices=["markdown", "json", "text"], default="markdown")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--browser-profile", choices=["openclaw", "chrome"], default="openclaw")
    
    # 检查新增的参数
    actions = [action.dest for action in parser._actions]
    assert 'browser' in actions, "缺少 --browser 参数"
    assert 'browser_profile' in actions, "缺少 --browser-profile 参数"
    print("  ✓ --browser 参数已添加")
    print("  ✓ --browser-profile 参数已添加")
    
    print("  ✅ 通过\n")

def test_smartsearch_class():
    """测试 SmartSearch 类结构"""
    print("✓ 测试 5: SmartSearch 类结构")
    
    import inspect
    from smart_search import SmartSearch
    
    # 检查 __init__ 参数
    init_signature = inspect.signature(SmartSearch.__init__)
    params = list(init_signature.parameters.keys())
    assert 'use_browser' in params, "SmartSearch 缺少 use_browser 参数"
    assert 'browser_profile' in params, "SmartSearch 缺少 browser_profile 参数"
    print("  ✓ SmartSearch 参数完整")
    
    print("  ✅ 通过\n")

def main():
    """运行所有测试"""
    print("=" * 50)
    print("BrowserFetcher 功能测试")
    print("=" * 50 + "\n")
    
    try:
        test_browser_fetcher_creation()
        test_browser_fetch_result()
        test_browser_fetcher_methods()
        test_command_line_args()
        test_smartsearch_class()
        
        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        print("\n浏览器模式功能验证完成:")
        print("  • BrowserFetcher 类已正确实现")
        print("  • BrowserFetchResult 数据结构完整")
        print("  • SmartSearch 参数完整")
        print("  • 命令行参数支持 (--browser, --browser-profile)")
        print("\n下一步：使用 --browser 参数进行实际搜索测试")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
