"""
17 个搜索引擎并行模块
====================
使用 Multi-Search 引擎进行并行搜索
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from urllib.parse import quote

from utils.logger import engine_logger
from config import get_config


@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    snippet: str
    engine: str = ""
    rank: int = 0
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "engine": self.engine,
            "rank": self.rank,
            "score": self.score
        }


@dataclass
class SearchResponse:
    """搜索响应"""
    query: str
    results: List[SearchResult] = field(default_factory=list)
    total: int = 0
    time: float = 0.0
    engines_used: List[str] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total": self.total,
            "time": self.time,
            "engines_used": self.engines_used,
            "errors": self.errors
        }


class MultiSearch:
    """多搜索引擎并行类"""
    
    ENGINES = {
        "google": {"name": "Google", "url": f"https://www.google.com/search?q=", "parser": "html"},
        "bing": {"name": "Bing", "url": f"https://www.bing.com/search?q=", "parser": "html"},
        "duckduckgo": {"name": "DuckDuckGo", "url": f"https://duckduckgo.com/?q=", "parser": "html"},
        "yahoo": {"name": "Yahoo", "url": f"https://search.yahoo.com/search?p=", "parser": "html"},
        "baidu": {"name": "百度", "url": f"https://www.baidu.com/s?wd=", "parser": "html"},
        "sogou": {"name": "搜狗", "url": f"https://www.sogou.com/web?query=", "parser": "html"},
        "360": {"name": "360 搜索", "url": f"https://www.so.com/s?q=", "parser": "html"},
        "yandex": {"name": "Yandex", "url": f"https://yandex.com/search/?text=", "parser": "html"},
        "ask": {"name": "ASK", "url": f"https://www.ask.com/web?q=", "parser": "html"},
        "wolframalpha": {"name": "WolframAlpha", "url": f"https://www.wolframalpha.com/input/?i=", "parser": "html"},
        "quora": {"name": "Quora", "url": f"https://www.quora.com/search?q=", "parser": "html"},
        "stack_overflow": {"name": "Stack Overflow", "url": f"https://stackoverflow.com/search?q=", "parser": "html"},
        "github": {"name": "GitHub", "url": f"https://github.com/search?q=", "parser": "html"},
        "wikipedia": {"name": "Wikipedia", "url": f"https://en.wikipedia.org/wiki/Special:Search?search=", "parser": "html"},
        "arxiv": {"name": "arXiv", "url": f"https://arxiv.org/search/?query=", "parser": "html"},
        "pubmed": {"name": "PubMed", "url": f"https://pubmed.ncbi.nlm.nih.gov/?term=", "parser": "html"},
        "reddit": {"name": "Reddit", "url": f"https://www.reddit.com/search/?q=", "parser": "html"}
    }
    
    def __init__(self, timeout: int = 30, max_results: int = 20):
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
        """并行搜索所有引擎"""
        start_time = time.time()
        engine_logger.info(f"开始 17 引擎并行搜索：{query}")
        
        tasks = [self._search_engine(name, info, query) for name, info in self.ENGINES.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        engines_used = []
        errors = []
        
        for (name, info), result in zip(self.ENGINES.items(), results):
            if isinstance(result, Exception):
                errors.append({"engine": info["name"], "error": str(result)})
            elif result:
                all_results.extend(result)
                engines_used.append(info["name"])
        
        all_results = self._deduplicate_results(all_results)
        all_results = self._sort_results(all_results)
        all_results = all_results[:self.max_results]
        
        for i, result in enumerate(all_results):
            result.rank = i + 1
        
        return SearchResponse(
            query=query,
            results=all_results,
            total=len(all_results),
            time=time.time() - start_time,
            engines_used=engines_used,
            errors=errors
        )
    
    async def _search_engine(self, name: str, info: Dict, query: str) -> Optional[List[SearchResult]]:
        """搜索单个引擎"""
        try:
            search_url = f"{info['url']}{quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            
            async with self.session.get(search_url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_results(html, info)
        except Exception as e:
            engine_logger.warning(f"{info['name']} 搜索失败：{e}")
        
        return None
    
    def _parse_results(self, html: str, engine_info: Dict) -> List[SearchResult]:
        """解析搜索结果"""
        import re
        results = []
        
        if "google" in engine_info["name"].lower():
            results = self._parse_google(html)
        elif "bing" in engine_info["name"].lower():
            results = self._parse_bing(html)
        elif "duckduckgo" in engine_info["name"].lower():
            results = self._parse_duckduckgo(html)
        elif "baidu" in engine_info["name"].lower():
            results = self._parse_baidu(html)
        else:
            results = self._parse_generic(html)
        
        for result in results:
            result.engine = engine_info["name"]
        
        return results
    
    def _parse_google(self, html: str) -> List[SearchResult]:
        import re
        results = []
        pattern = r'<a[^>]*href=["\']([^"\']*?)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html)
        for href, title in matches[:5]:
            if href.startswith('/url?') or href.startswith('http'):
                results.append(SearchResult(title=title.strip(), url=href, snippet=""))
        return results
    
    def _parse_bing(self, html: str) -> List[SearchResult]:
        import re
        results = []
        pattern = r'<h2[^>]*><a[^>]*href=["\']([^"\']*?)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html)
        for href, title in matches[:5]:
            results.append(SearchResult(title=title.strip(), url=href, snippet=""))
        return results
    
    def _parse_duckduckgo(self, html: str) -> List[SearchResult]:
        import re
        results = []
        pattern = r'<a[^>]*class=["\']results__link[^>]*href=["\']([^"\']*?)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html)
        for href, title in matches[:5]:
            if href.startswith('/'):
                href = 'https://duckduckgo.com' + href
            results.append(SearchResult(title=title.strip(), url=href, snippet=""))
        return results
    
    def _parse_baidu(self, html: str) -> List[SearchResult]:
        import re
        results = []
        pattern = r'<a[^>]*href=["\']([^"\']*?)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html)
        for href, title in matches[:5]:
            if href.startswith('http') or href.startswith('//'):
                results.append(SearchResult(title=title.strip(), url=href, snippet=""))
        return results
    
    def _parse_generic(self, html: str) -> List[SearchResult]:
        import re
        results = []
        pattern = r'<a[^>]*href=["\']([^"\']*?)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html)
        for href, title in matches[:3]:
            if href.startswith('http'):
                results.append(SearchResult(title=title.strip(), url=href, snippet=""))
        return results
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        seen = set()
        unique = []
        for r in results:
            if r.url not in seen:
                seen.add(r.url)
                unique.append(r)
        return unique
    
    def _sort_results(self, results: List[SearchResult]) -> List[SearchResult]:
        weights = {"Google": 10, "Bing": 9, "Wikipedia": 9, "Stack Overflow": 9, "GitHub": 8}
        for r in results:
            w = weights.get(r.engine, 5)
            r.score = w * (100 / (r.rank + 1))
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def search_sync(self, query: str) -> SearchResponse:
        return asyncio.run(self.search(query))


multi_search = MultiSearch()

def fetch_multi_search(query: str) -> SearchResponse:
    return multi_search.search_sync(query)

async def async_fetch_multi_search(query: str) -> SearchResponse:
    async with MultiSearch() as searcher:
        return await searcher.search(query)
