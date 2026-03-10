"""
Tavily AI 搜索模块
================
AI 优化的网络搜索服务
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from utils.logger import engine_logger
from engines.multi_search import SearchResult, SearchResponse


@dataclass
class TavilyResult(SearchResult):
    """Tavily 搜索结果"""
    score: float = 0.0
    content: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["score"] = self.score
        data["content"] = self.content
        return data


class TavilySearch:
    """Tavily AI 搜索类"""
    
    API_URL = "https://api.tavily.com/search"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_results: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.max_results = max_results
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search(self, query: str) -> SearchResponse:
        """使用 Tavily 搜索"""
        engine_logger.info(f"Tavily 搜索：{query}")
        start_time = time.time()
        
        if not self.api_key:
            engine_logger.warning("Tavily API key 未设置，使用模拟数据")
            return self._mock_search(query)
        
        try:
            headers = {"Content-Type": "application/json"}
            payload = {"query": query, "search_depth": "advanced", "include_images": False}
            
            async with self.session.post(self.API_URL, headers=headers, json=payload,
                                         auth=aiohttp.BasicAuth(self.api_key)) as response:
                if response.status == 200:
                    data = await response.json()
                    results = self._parse_response(data, query)
                    return SearchResponse(query=query, results=results, total=len(results),
                                         time=time.time() - start_time, engines_used=["Tavily AI"], errors=[])
                else:
                    return SearchResponse(query=query, results=[], total=0, time=time.time() - start_time,
                                         engines_used=["Tavily AI"], errors=[{"engine": "Tavily AI", "error": str(response.status)}])
        except Exception as e:
            engine_logger.error(f"Tavily 搜索异常：{e}")
            return self._mock_search(query)
    
    def _parse_response(self, data: Dict, query: str) -> List[TavilyResult]:
        """解析 Tavily API 响应"""
        results = []
        for item in data.get("results", [])[:self.max_results]:
            result = TavilyResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                engine="Tavily AI",
                rank=len(results) + 1,
                score=item.get("score", 0.0),
                content=item.get("content", "")
            )
            results.append(result)
        return results
    
    def _mock_search(self, query: str) -> SearchResponse:
        """模拟搜索结果"""
        results = [
            SearchResult(title=f"{query} - 结果 1", url=f"https://example.com/1?q={query}",
                        snippet=f"关于 {query} 的信息", engine="Tavily AI (模拟)", rank=1, score=10.0),
            SearchResult(title=f"{query} - 结果 2", url=f"https://example.com/2?q={query}",
                        snippet=f"更多 {query} 内容", engine="Tavily AI (模拟)", rank=2, score=9.0),
            SearchResult(title=f"{query} - 结果 3", url=f"https://example.com/3?q={query}",
                        snippet=f"深入了解 {query}", engine="Tavily AI (模拟)", rank=3, score=8.0)
        ]
        return SearchResponse(query=query, results=results, total=len(results),
                             time=time.time(), engines_used=["Tavily AI"], errors=[])
    
    def search_sync(self, query: str) -> SearchResponse:
        return asyncio.run(self.search(query))


tavily_search = TavilySearch()

def fetch_tavily(query: str, api_key: Optional[str] = None) -> SearchResponse:
    search = TavilySearch(api_key=api_key)
    return search.search_sync(query)

async def async_fetch_tavily(query: str, api_key: Optional[str] = None) -> SearchResponse:
    search = TavilySearch(api_key=api_key)
    async with search:
        return await search.search(query)
