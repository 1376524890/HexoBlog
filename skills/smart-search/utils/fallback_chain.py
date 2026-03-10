"""
降级链工具模块
==============
实现智能降级策略，确保在最坏情况下仍能获取内容
"""

import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import aiohttp
import time
import logging


@dataclass
class FetchResult:
    """抓取结果"""
    success: bool
    url: str
    content: Optional[str] = None
    title: Optional[str] = None
    source: str = ""
    error: Optional[str] = None
    fetch_time: float = 0.0
    method: str = ""
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "success": self.success,
            "url": self.url,
            "content": self.content,
            "title": self.title,
            "source": self.source,
            "error": self.error,
            "fetch_time": self.fetch_time,
            "method": self.method,
            "retry_count": self.retry_count
        }


class FallbackChain:
    """降级链处理器"""
    
    logger = logging.getLogger("SmartSearch.Scraper")
    
    def __init__(self, timeout: int = 30, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        self.results_log: List[FetchResult] = []
    
    async def __aenter__(self):
        """异步上下文进入"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文退出"""
        if self.session:
            await self.session.close()
    
    async def fetch(
        self,
        url: str,
        methods: Optional[List[str]] = None,
        retries: Optional[int] = None
    ) -> FetchResult:
        """
        使用降级链抓取内容
        
        Args:
            url: 目标 URL
            methods: 抓取的降级顺序
            retries: 重试次数
            
        Returns:
            FetchResult
        """
        if methods is None:
            methods = ["r_jina_ai", "markdown_new", "defuddle", "scrapling"]
        
        if retries is None:
            retries = self.max_retries
        
        last_error = None
        
        for method in methods:
            for attempt in range(retries + 1):
                try:
                    self.logger.info(f"尝试 [{method}] 抓取：{url} (第 {attempt + 1} 次尝试)")
                    
                    result = await self._fetch_with_method(url, method)
                    
                    if result.success:
                        self.logger.info(f"[{method}] 成功抓取：{url}")
                        self.results_log.append(result)
                        return result
                    
                except Exception as e:
                    last_error = str(e)
                    self.logger.warning(f"[{method}] 失败 (第 {attempt + 1} 次): {e}")
                
                # 如果还没到最大重试次数，等待后重试
                if attempt < retries:
                    await asyncio.sleep(1 * (attempt + 1))
        
        # 所有方法都失败
        self.logger.error(f"所有降级策略都失败：{url}")
        error_result = FetchResult(
            success=False,
            url=url,
            error=f"所有方法都失败：{last_error}",
            method="all_fallbacks",
            retry_count=retries
        )
        self.results_log.append(error_result)
        return error_result
    
    async def _fetch_with_method(
        self,
        url: str,
        method: str
    ) -> FetchResult:
        """使用指定方法抓取"""
        start_time = time.time()
        
        if method == "r_jina_ai":
            return await self._fetch_r_jina_ai(url)
        elif method == "markdown_new":
            return await self._fetch_markdown_new(url)
        elif method == "defuddle":
            return await self._fetch_defuddle(url)
        elif method == "scrapling":
            return await self._fetch_scrapling(url)
        else:
            return FetchResult(
                success=False,
                url=url,
                error=f"未知的抓取方法：{method}",
                method=method,
                fetch_time=time.time() - start_time
            )
    
    async def _fetch_r_jina_ai(self, url: str) -> FetchResult:
        """使用 r.jina.ai 抓取"""
        jina_url = f"https://r.jina.ai/{url}"
        jina_start = time.time()
        
        async with self.session.get(jina_url, allow_redirects=True) as response:
            if response.status == 200:
                content = await response.text()
                return FetchResult(
                    success=True,
                    url=url,
                    content=content,
                    title=self._extract_title(content),
                    source="r.jina.ai",
                    method="r_jina_ai",
                    fetch_time=time.time() - jina_start
                )
            else:
                return FetchResult(
                    success=False,
                    url=url,
                    error=f"r.jina.ai 返回状态码：{response.status}",
                    method="r_jina_ai",
                    fetch_time=time.time() - start_time
                )
    
    async def _fetch_markdown_new(self, url: str) -> FetchResult:
        """使用 markdown.new (Cloudflare) 抓取"""
        markdown_url = f"https://r.jina.ai/{url}"
        md_start = time.time()
        
        async with self.session.get(markdown_url, allow_redirects=True) as response:
            if response.status == 200:
                content = await response.text()
                return FetchResult(
                    success=True,
                    url=url,
                    content=content,
                    title=self._extract_title(content),
                    source="markdown.new",
                    method="markdown_new",
                    fetch_time=time.time() - md_start
                )
            else:
                return FetchResult(
                    success=False,
                    url=url,
                    error=f"markdown.new 返回状态码：{response.status}",
                    method="markdown_new",
                    fetch_time=time.time() - start_time
                )
    
    async def _fetch_defuddle(self, url: str) -> FetchResult:
        """使用 defuddle.md 抓取"""
        defuddle_url = f"https://r.jina.ai/{url}"
        defuddle_start = time.time()
        
        async with self.session.get(defuddle_url, allow_redirects=True) as response:
            if response.status == 200:
                content = await response.text()
                return FetchResult(
                    success=True,
                    url=url,
                    content=content,
                    title=self._extract_title(content),
                    source="defuddle.md",
                    method="defuddle",
                    fetch_time=time.time() - defuddle_start
                )
            else:
                return FetchResult(
                    success=False,
                    url=url,
                    error=f"defuddle.md 返回状态码：{response.status}",
                    method="defuddle",
                    fetch_time=time.time() - start_time
                )
    
    async def _fetch_scrapling(self, url: str) -> FetchResult:
        """使用 Scrapling 本地爬虫抓取，失败时自动降级到 aiohttp 直接抓取"""
        scrapling_start = time.time()
        
        try:
            from scraper.scrapling_scraper import fetch_scrapling
            
            # 使用 Scrapling 同步抓取
            scrapling_result = fetch_scrapling(url)
            
            if scrapling_result.success:
                # 将 ScraplingResult 转换为 FetchResult
                return FetchResult(
                    success=True,
                    url=url,
                    content=scrapling_result.content,
                    title=scrapling_result.title,
                    source="Scrapling",
                    method="scrapling",
                    fetch_time=time.time() - scrapling_start
                )
            else:
                # Scrapling 失败，记录原因并降级使用 aiohttp
                self.logger.warning(f"Scrapling 失败：{scrapling_result.error}，降级使用 aiohttp")
                return await self._fetch_aiohttp_direct(url, scrapling_start)
                
        except ImportError as e:
            self.logger.warning(f"Scrapling 库未安装，直接使用 aiohttp: {e}")
            return await self._fetch_aiohttp_direct(url, scrapling_start)
        except Exception as e:
            self.logger.error(f"Scrapling 抓取异常：{e}，降级使用 aiohttp")
            return await self._fetch_aiohttp_direct(url, scrapling_start)
    
    async def _fetch_aiohttp_direct(self, url: str, start_time: float) -> FetchResult:
        """降级：直接使用 aiohttp 抓取（当 Scrapling 未安装或失败时）"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            async with self.session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    content = self._extract_content(html)
                    title = self._extract_title_from_html(html)
                    
                    return FetchResult(
                        success=True,
                        url=url,
                        content=content,
                        title=title,
                        source="aiohttp (fallback)",
                        method="scrapling",
                        fetch_time=time.time() - start_time
                    )
                else:
                    return FetchResult(
                        success=False,
                        url=url,
                        error=f"HTTP 状态码：{response.status}",
                        method="scrapling",
                        fetch_time=time.time() - start_time
                    )
        except Exception as e:
            return FetchResult(
                success=False,
                url=url,
                error=str(e),
                method="scrapling",
                fetch_time=time.time() - start_time
            )
    
    def _extract_title(self, content: str) -> str:
        """从 r.jina.ai 返回的内容中提取标题"""
        lines = content.split('\n')
        if lines and lines[0]:
            return lines[0].strip()
        return "无标题"
    
    def _extract_content(self, html: str) -> str:
        """从 HTML 提取纯文本内容"""
        import re
        from html import unescape
        
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
    
    def _extract_title_from_html(self, html: str) -> Optional[str]:
        """从 HTML 中提取标题"""
        import re
        from html import unescape
        
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return unescape(title_match.group(1).strip())
        
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
        if h1_match:
            return unescape(h1_match.group(1).strip())
        
        return None
    
    def get_results_log(self) -> List[FetchResult]:
        """获取抓取结果日志"""
        return self.results_log
    
    def clear_results_log(self):
        """清空结果日志"""
        self.results_log.clear()
