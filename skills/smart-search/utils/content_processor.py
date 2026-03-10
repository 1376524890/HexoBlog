"""
内容处理工具模块
=================
提供内容提取、去重、格式化等功能
"""

import hashlib
import re
import html
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from difflib import SequenceMatcher


@dataclass
class ProcessedContent:
    """处理后的内容"""
    url: str
    title: str
    content: str
    source: str
    meta: Dict = field(default_factory=dict)
    processing_time: float = 0.0


class ContentProcessor:
    """内容处理器"""
    
    # 常见 HTML 标签
    HTML_TAGS = re.compile(r'<[^>]+>')
    
    # 多余空白
    WHITESPACE = re.compile(r'\s+')
    
    def __init__(self):
        pass
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        text = self.HTML_TAGS.sub('', text)
        text = html.unescape(text)
        text = self.WHITESPACE.sub(' ', text)
        text = text.strip()
        return text
    
    def extract_title(self, html_content: str) -> str:
        """从 HTML 中提取标题"""
        title_tag = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_tag:
            return self.clean_text(title_tag.group(1))
        h1_tag = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
        if h1_tag:
            return self.clean_text(h1_tag.group(1))
        return "无标题"
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        clean1 = re.sub(r'[^a-zA-Z0-9]', '', text1.lower())
        clean2 = re.sub(r'[^a-zA-Z0-9]', '', text2.lower())
        return SequenceMatcher(None, clean1, clean2).ratio()
    
    def deduplicate_results(
        self,
        results: List[ProcessedContent],
        threshold: float = 0.8
    ) -> List[ProcessedContent]:
        """去重"""
        unique_results = []
        
        for result in results:
            is_duplicate = False
            for existing in unique_results:
                url_similarity = self.calculate_similarity(result.url, existing.url)
                if url_similarity > threshold:
                    is_duplicate = True
                    break
                content_similarity = self.calculate_similarity(
                    result.content,
                    existing.content
                )
                if content_similarity > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
        
        return unique_results
    
    def extract_content(self, html_content: str) -> str:
        """从 HTML 中提取主要文章内容"""
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = self.HTML_TAGS.sub('', text)
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = ' '.join(paragraphs)
        return self.clean_text(text)
    
    def generate_hash(self, text: str) -> str:
        """生成文本哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def truncate_content(
        self,
        content: str,
        max_length: int,
        suffix: str = "..."
    ) -> str:
        """截断内容"""
        if len(content) <= max_length:
            return content
        return content[:max_length - len(suffix)] + suffix
    
    def format_output(
        self,
        results: List[ProcessedContent],
        output_format: str = "markdown"
    ) -> str:
        """格式化输出"""
        if output_format == "markdown":
            return self._format_markdown(results)
        elif output_format == "json":
            import json
            data = [{
                "url": r.url,
                "title": r.title,
                "content": r.content[:500],
                "source": r.source
            } for r in results]
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return self._format_text(results)
    
    def _format_markdown(self, results: List[ProcessedContent]) -> str:
        """Markdown 格式输出"""
        output = []
        output.append("# Search Results\n")
        
        for i, result in enumerate(results, 1):
            output.append(f"## {i}. {result.title}\n")
            output.append(f"**来源**: {result.source}\n")
            output.append(f"**URL**: {result.url}\n")
            output.append(f"\n{result.content}\n")
            output.append("---\n")
        
        return ''.join(output)
    
    def _format_text(self, results: List[ProcessedContent]) -> str:
        """纯文本格式输出"""
        output = []
        
        for i, result in enumerate(results, 1):
            output.append(f"\n=== Result {i} ===\n")
            output.append(f"Title: {result.title}\n")
            output.append(f"Source: {result.source}\n")
            output.append(f"URL: {result.url}\n")
            output.append(f"Content:\n{result.content}\n")
        
        return ''.join(output)


# 全局处理器实例
processor = ContentProcessor()
