"""
Web Markdown 搜索模块
===================
使用 r.jina.ai 等 Markdown 转换服务
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from utils.logger import engine_logger
from engines.multi_search import SearchResult, SearchResponse


@dataclass
class WebMarkdownResult(SearchResult):
    """Web Markdown 搜索结果"""
    content: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["content"] = self.content
        return data


class WebMarkdown:
    """Web Markdown 搜索类"""
    
    BASE_URL = "https://r.jina.ai"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search(self, query: str) -> SearchResponse:
        """使用 Web Markdown 搜索"""
        engine_logger.info(f"Web Markdown 搜索：{query}")
        start_time = time.time()
        
        search_url = f"{self.BASE_URL}/https://www.google.com/search?q={query.replace(' ', '+')}"
        
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    results = self._parse_content(content, query)
                    return SearchResponse(query=query, results=results, total=len(results),
                                         time=time.time() - start_time, engines_used=["Web Markdown"], errors=[])
                else:
                    return SearchResponse(query=query, results=[], total=0,
                                         time=time.time() - start_time,
                                         engines_used=["Web Markdown"],
                                         errors=[{"engine": "Web Markdown", "error": str(response.status)}])
        except Exception as e:
            engine_logger.error(f"Web Markdown 搜索异常：{e}")
            return SearchResponse(query=query, results=[], total=0,
                                 time=time.time() - start_time,
                                 engines_used=["Web Markdown"],
                                 errors=[{"engine": "Web Markdown", "error": str(e)}])
    
    def _parse_content(self, content: str, query: str) -> List[WebMarkdownResult]:
        """解析 Markdown 内容"""
        results = []
        lines = content.split('\n')
        current_result = None
        result_count = 0
        
        for i, line in enumerate(lines):
            if line.startswith('### ') or line.startswith('## '):
                if current_result:
                    results.append(current_result)
                
                title = line.lstrip('# ').strip()
                url = lines[i+1] if i+1 < len(lines) and lines[i+1].startswith('http') else f"https://example.com/search?q={query}"
                
                current_result = WebMarkdownResult(
                    title=title, url=url, snippet="", engine="Web Markdown",
                    rank=result_count + 1, content=""
                )
                result_count += 1
            elif current_result and line and not line.startswith('### ') and not line.startswith('## '):
                if current_result.content:
                    current_result.content += ' ' + line
                else:
                    current_result.content = line
        
        if current_result:
            results.append(current_result)
        
        return results[:5]
    
    def search_sync(self, query: str) -> SearchResponse:
        return asyncio.run(self.search(query))


web_markdown = WebMarkdown()

def fetch_web_markdown(query: str) -> SearchResponse:
    return web_markdown.search_sync(query)

async def async_fetch_web_markdown(query: str) -> SearchResponse:
    async with WebMarkdown() as searcher:
        return await searcher.search(query)
