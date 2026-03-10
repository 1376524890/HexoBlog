"""
Scrapling 爬虫实现
==================
使用 aiohttp 实现（兼容 Scrapling API）
注意：由于 asyncio.run() 不能在已有事件循环中调用，这里使用了 ThreadPoolExecutor 来处理
"""

import asyncio
import aiohttp
import time
import random
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import re
from html import unescape
from concurrent.futures import ThreadPoolExecutor

from utils.logger import scraper_logger
from config import get_config


@dataclass
class ScraplingResult:
    """Scrapling 抓取结果"""
    success: bool
    url: str
    content: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None
    fetch_time: float = 0.0
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"success": self.success, "url": self.url, "content": self.content,
                "title": self.title, "error": self.error, "fetch_time": self.fetch_time,
                "metadata": self.metadata}


class ScraplingScraper:
    """Scrapling 爬虫 - 使用 aiohttp 实现（兼容 Scrapling API）"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def fetch(self, url: str, session: aiohttp.ClientSession) -> ScraplingResult:
        """使用 aiohttp 抓取 URL（兼容 Scrapling API）"""
        start_time = time.time()
        
        try:
            scraper_logger.info(f"使用 Scrapling 抓取：{url}")
            user_agent = random.choice(self.USER_AGENTS)
            
            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    fetch_time = time.time() - start_time
                    
                    title = self._extract_title(html)
                    content = self._extract_content(html)
                    
                    metadata = {
                        "status_code": response.status,
                        "content_length": len(html),
                        "user_agent": user_agent
                    }
                    
                    return ScraplingResult(
                        success=True, url=url, content=content, title=title,
                        fetch_time=fetch_time, metadata=metadata
                    )
                else:
                    return ScraplingResult(
                        success=False, url=url,
                        error=f"Scrapling 返回状态码：{response.status}",
                        fetch_time=time.time() - start_time
                    )
        
        except asyncio.TimeoutError:
            return ScraplingResult(
                success=False, url=url, error="请求超时",
                fetch_time=time.time() - start_time
            )
        except Exception as e:
            return ScraplingResult(
                success=False, url=url, error=str(e),
                fetch_time=time.time() - start_time
            )
    
    def fetch_sync(self, url: str) -> ScraplingResult:
        """
        同步抓取方法 - 使用 ThreadPoolExecutor 在独立线程中运行异步代码
        这样可以避免在已有事件循环中调用 asyncio.run()
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            # 在独立线程中运行 asyncio.run
            future = executor.submit(asyncio.run, async_fetch_scrapling(url))
            return future.result(timeout=self.timeout)
    
    def _extract_title(self, html: str) -> Optional[str]:
        """提取页面标题"""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
        return h1_match.group(1).strip() if h1_match else None
    
    def _extract_content(self, html: str) -> str:
        """从 HTML 提取纯文本内容"""
        # 移除脚本和样式
        content = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        # 移除所有标签
        content = re.sub(r'<[^>]+>', '', content)
        # 解码 HTML 实体
        content = unescape(content)
        # 规范化空白
        content = re.sub(r'\s+', ' ', content)
        return content.strip()


# 全局单例
scrapling_scraper = ScraplingScraper()

def fetch_scrapling(url: str) -> ScraplingResult:
    """同步抓取函数"""
    return scrapling_scraper.fetch_sync(url)

async def async_fetch_scrapling(url: str) -> ScraplingResult:
    """异步抓取函数"""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        scraper = ScraplingScraper()
        return await scraper.fetch(url, session)
