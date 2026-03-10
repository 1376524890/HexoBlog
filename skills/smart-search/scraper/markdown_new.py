"""
markdown.new 爬虫实现
=====================
使用 markdown.new (Cloudflare) 进行网页抓取
"""

import asyncio
import aiohttp
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

from utils.logger import scraper_logger
from config import get_config


@dataclass
class MarkdownNewResult:
    """markdown.new 抓取结果"""
    success: bool
    url: str
    content: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None
    fetch_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {"success": self.success, "url": self.url, "content": self.content,
                "title": self.title, "error": self.error, "fetch_time": self.fetch_time}


class MarkdownNew:
    """markdown.new 爬虫"""
    
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
    
    async def fetch(self, url: str) -> MarkdownNewResult:
        """使用 markdown.new 抓取 URL"""
        start_time = time.time()
        
        try:
            markdown_url = f"{self.BASE_URL}/{url}"
            scraper_logger.info(f"抓取 markdown.new: {markdown_url}")
            
            async with self.session.get(markdown_url, allow_redirects=True) as response:
                if response.status == 200:
                    content = await response.text()
                    return MarkdownNewResult(
                        success=True, url=url, content=content,
                        title=self._extract_title(content), fetch_time=time.time() - start_time
                    )
                else:
                    return MarkdownNewResult(
                        success=False, url=url,
                        error=f"markdown.new 返回状态码：{response.status}",
                        fetch_time=time.time() - start_time
                    )
        
        except asyncio.TimeoutError:
            return MarkdownNewResult(
                success=False, url=url, error="请求超时",
                fetch_time=time.time() - start_time
            )
        except Exception as e:
            return MarkdownNewResult(
                success=False, url=url, error=str(e),
                fetch_time=time.time() - start_time
            )
    
    def _extract_title(self, content: str) -> Optional[str]:
        lines = content.split('\n')
        return lines[0].strip() if lines and lines[0] else None
    
    def fetch_sync(self, url: str) -> MarkdownNewResult:
        return asyncio.run(self.fetch(url))


markdown_new = MarkdownNew()

def fetch_markdown_new(url: str) -> MarkdownNewResult:
    return markdown_new.fetch_sync(url)

async def async_fetch_markdown_new(url: str) -> MarkdownNewResult:
    async with MarkdownNew() as scraper:
        return await scraper.fetch(url)
