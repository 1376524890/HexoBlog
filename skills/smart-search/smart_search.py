"""
SmartSearch 主程序
================
综合性网络搜索系统

使用方法：
  # 作为命令行工具
  python smart_search.py "搜索关键词" --depth 3 --max-results 5
  
  # 作为 Python 模块
  from smart_search import SmartSearch
  searcher = get_smart_search_instance()
  response = await searcher.search("Python 教程", depth=3)
"""

import asyncio
import argparse
import time
import sys
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# 确保包路径正确（用于直接运行时）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)


@dataclass
class SearchResultItem:
    """搜索结果项"""
    rank: int
    url: str
    title: str
    content: str
    source: str
    snippet: str = ""
    fetch_time: float = 0.0
    fetch_method: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "rank": self.rank,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "snippet": self.snippet,
            "fetch_time": self.fetch_time,
            "fetch_method": self.fetch_method
        }


@dataclass
class SmartSearchResponse:
    """智能搜索响应"""
    query: str
    results: List[SearchResultItem] = field(default_factory=list)
    total: int = 0
    total_time: float = 0.0
    layer1_time: float = 0.0
    layer2_time: float = 0.0
    layer3_time: float = 0.0
    layer4_time: float = 0.0
    errors: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total": self.total,
            "total_time": self.total_time,
            "layer1_time": self.layer1_time,
            "layer2_time": self.layer2_time,
            "layer3_time": self.layer3_time,
            "layer4_time": self.layer4_time,
            "errors": self.errors
        }


class SmartSearch:
    """智能搜索主类"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.processor = ContentProcessor()
    
    async def search(
        self,
        query: str,
        depth: int = 3,
        max_results: Optional[int] = None
    ) -> SmartSearchResponse:
        """
        执行智能搜索
        
        Args:
            query: 搜索查询
            depth: 搜索深度 (抓取页面数)
            max_results: 最大结果数
            
        Returns:
            SmartSearchResponse
        """
        start_time = time.time()
        errors = []
        
        # 设置最大结果数
        if max_results is None:
            max_results = self.config.search.top_n_results
        
        # === Layer 1: 广泛搜索层 ===
        layer1_start = time.time()
        search_response = await self._layer1_search(query)
        layer1_time = time.time() - layer1_start
        
        if not search_response.results:
            errors.append({
                "layer": 1,
                "error": "广泛搜索未返回结果"
            })
            return SmartSearchResponse(
                query=query,
                total=0,
                total_time=time.time() - start_time,
                layer1_time=layer1_time,
                errors=errors
            )
        
        # === Layer 2: 目标发现层 ===
        layer2_start = time.time()
        top_urls = self._layer2_filter(search_response, depth)
        layer2_time = time.time() - layer2_start
        
        # === Layer 3: 深度抓取层 ===
        layer3_start = time.time()
        fetched_contents = await self._layer3_fetch(top_urls)
        layer3_time = time.time() - layer3_start
        
        # === Layer 4: 结果整合层 ===
        layer4_start = time.time()
        final_results = self._layer4_process(fetched_contents, max_results)
        layer4_time = time.time() - layer4_start
        
        return SmartSearchResponse(
            query=query,
            results=final_results,
            total=len(final_results),
            total_time=time.time() - start_time,
            layer1_time=layer1_time,
            layer2_time=layer2_time,
            layer3_time=layer3_time,
            layer4_time=layer4_time,
            errors=errors
        )
    
    async def _layer1_search(self, query: str):
        """
        Layer 1: 广泛搜索
        
        并行使用 17 个搜索引擎进行搜索
        """
        async with MultiSearch() as searcher:
            return await searcher.search(query)
    
    def _layer2_filter(self, search_response, depth: int) -> List[str]:
        """
        Layer 2: 目标发现
        
        对搜索结果进行筛选、去重、排序
        """
        results = search_response.results
        
        # 按相关性排序 (已经由 MultiSearch 完成)
        # 选择 Top N 目标
        top_n = min(depth, len(results))
        top_results = results[:top_n]
        
        # 提取 URL
        urls = [result.url for result in top_results if result.url]
        
        return urls
    
    async def _layer3_fetch(self, urls: List[str]) -> List:
        """
        Layer 3: 深度抓取
        
        对每个 URL 按降级顺序抓取
        """
        fetch_results = []
        
        async with FallbackChain() as fallback_chain:
            # 并行抓取多个 URL
            tasks = [
                fallback_chain.fetch(url)
                for url in urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for url, result in zip(urls, results):
                if isinstance(result, Exception):
                    fetch_results.append(FetchResult(
                        success=False,
                        url=url,
                        error=str(result),
                        method="all_fallbacks"
                    ))
                else:
                    fetch_results.append(result)
        
        return fetch_results
    
    def _layer4_process(
        self,
        fetched_contents: List,
        max_results: int
    ) -> List[SearchResultItem]:
        """
        Layer 4: 结果整合
        
        合并、去重、格式化最终结果
        """
        # 筛选成功抓取的结果
        successful = [
            result for result in fetched_contents
            if result.success and result.content
        ]
        
        # 创建搜索结果项
        results = []
        for i, result in enumerate(successful[:max_results], 1):
            # 提取标题
            title = result.title or self.processor._extract_title(result.content) or "无标题"
            
            # 截断内容
            content = self.processor.truncate_content(
                result.content,
                max_length=self.config.scraper.max_content_length
            )
            
            # 创建结果项
            item = SearchResultItem(
                rank=i,
                url=result.url,
                title=title,
                content=content,
                source=result.source,
                snippet=result.content[:200] if result.content else "",
                fetch_time=result.fetch_time,
                fetch_method=result.method
            )
            results.append(item)
        
        return results
    
    def search_sync(
        self,
        query: str,
        depth: int = 3,
        max_results: Optional[int] = None
    ) -> SmartSearchResponse:
        """
        同步方式搜索
        
        Args:
            query: 搜索查询
            depth: 搜索深度
            max_results: 最大结果数
            
        Returns:
            SmartSearchResponse
        """
        return asyncio.run(self.search(query, depth, max_results))


# 全局实例（延迟初始化）
_smart_search_instance = None

def get_smart_search_instance():
    """获取全局智能搜索实例"""
    global _smart_search_instance
    if _smart_search_instance is None:
        _smart_search_instance = SmartSearch()
    return _smart_search_instance


def get_processor():
    """获取 processor 实例"""
    return ContentProcessor()


# 主程序入口
async def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="SmartSearch - 智能降级网络搜索系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python smart_search.py "Python 教程"
  python smart_search.py --depth 5 "机器学习"
  python smart_search.py "人工智能" --output ./results
        """
    )
    
    parser.add_argument(
        "query",
        help="搜索查询"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        help="搜索深度 (默认：3)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="最大结果数 (默认：5)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="输出目录 (默认：./output)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "json", "text"],
        default="markdown",
        help="输出格式 (默认：markdown)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式"
    )
    
    args = parser.parse_args()
    
    # 创建 processor
    processor = get_processor()
    
    # 创建搜索器
    searcher = get_smart_search_instance()
    
    # 执行搜索
    if not args.quiet:
        print(f"\n🔍 开始搜索：{args.query}")
        print(f"深度：{args.depth}")
        print(f"最大结果：{args.max_results}\n")
    
    start_time = time.time()
    response = await searcher.search(args.query, args.depth, args.max_results)
    total_time = time.time() - start_time
    
    # 输出结果
    if args.format == "markdown":
        output = processor.format_output(
            [SearchResultItem(
                rank=r.rank,
                url=r.url,
                title=r.title,
                content=r.content,
                source=r.source,
                snippet=r.snippet
            ) for r in response.results],
            output_format="markdown"
        )
    elif args.format == "json":
        output = json.dumps(response.to_dict(), indent=2, ensure_ascii=False)
    else:  # text
        output = processor._format_text(
            [SearchResultItem(
                rank=r.rank,
                url=r.url,
                title=r.title,
                content=r.content,
                source=r.source,
                snippet=r.snippet
            ) for r in response.results]
        )
    
    # 打印或保存
    if args.output == "stdout":
        print(output)
    else:
        os.makedirs(args.output, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_{args.query[:20].replace(' ', '_')}_{timestamp}.{args.format}"
        filepath = os.path.join(args.output, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output)
        
        if not args.quiet:
            print(f"\n✅ 搜索完成!")
            print(f"总时间：{total_time:.2f}秒")
            print(f"结果数：{response.total}")
            print(f"输出：{filepath}\n")
    
    return response


# 条件导入：在 __main__ 块中执行，避免类定义时导入失败
if __name__ == "__main__":
    # 导入需要在运行时执行
    from config import get_config
    from utils import ContentProcessor, FallbackChain, FetchResult
    from engines import MultiSearch, SearchResult, SearchResponse
    
    asyncio.run(main())
