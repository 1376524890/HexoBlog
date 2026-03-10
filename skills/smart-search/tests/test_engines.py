"""
搜索引擎测试
============
测试 17 个搜索引擎的并行搜索功能
"""

import asyncio
import pytest
from engines.multi_search import MultiSearch, SearchResult
from engines.tavily_search import TavilySearch
from engines.web_markdown import WebMarkdown


class TestMultiSearch:
    """MultiSearch 测试"""
    
    @pytest.mark.asyncio
    async def test_search_basic(self):
        """基础搜索测试"""
        async with MultiSearch() as searcher:
            response = await searcher.search("Python")
        
        assert response.query == "Python"
        assert response.total >= 0
        assert response.time > 0
    
    @pytest.mark.asyncio
    async def test_search_multiple_engines(self):
        """多引擎搜索测试"""
        async with MultiSearch() as searcher:
            response = await searcher.search("人工智能")
        
        # 验证多个引擎被使用
        assert len(response.engines_used) > 0
    
    @pytest.mark.asyncio
    async def test_deduplication(self):
        """去重测试"""
        async with MultiSearch() as searcher:
            response = await searcher.search("机器学习")
        
        # 验证 URL 去重
        urls = [r.url for r in response.results]
        assert len(urls) == len(set(urls))
    
    def test_sync_search(self):
        """同步搜索测试"""
        searcher = MultiSearch()
        response = searcher.search_sync("测试查询")
        
        assert response.query == "测试查询"


class TestTavilySearch:
    """TavilySearch 测试"""
    
    @pytest.mark.asyncio
    async def test_search_basic(self):
        """基础搜索测试"""
        async with TavilySearch() as searcher:
            response = await searcher.search("Python 教程")
        
        assert response.query == "Python 教程"
        # Tavily 可能使用模拟数据，不强制要求结果数
    
    @pytest.mark.asyncio
    async def test_search_with_api_key(self):
        """带 API key 的搜索测试"""
        # 注意：实际测试需要有效的 API key
        # api_key = os.getenv("TAVILY_API_KEY")
        # if api_key:
        #     async with TavilySearch(api_key=api_key) as searcher:
        #         response = await searcher.search("Test")
        #         assert response.total >= 0
        pass
    
    def test_sync_search(self):
        """同步搜索测试"""
        searcher = TavilySearch()
        response = searcher.search_sync("测试")
        assert response.query == "测试"


class TestWebMarkdown:
    """WebMarkdown 测试"""
    
    @pytest.mark.asyncio
    async def test_search_basic(self):
        """基础搜索测试"""
        async with WebMarkdown() as searcher:
            response = await searcher.search("Python")
        
        assert response.query == "Python"
        assert response.total >= 0


@pytest.mark.asyncio
async def test_full_pipeline():
    """完整流程测试"""
    from smart_search import SmartSearch
    
    searcher = SmartSearch()
    response = await searcher.search("测试查询", depth=2, max_results=3)
    
    assert response.query == "测试查询"
    assert response.total >= 0
    assert response.total_time > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
