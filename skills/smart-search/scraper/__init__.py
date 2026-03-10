"""
爬虫模块初始化
==============
"""

from .r_jina_ai import RJinaAI, fetch_r_jina_ai
from .markdown_new import MarkdownNew, fetch_markdown_new
from .defuddle import Defuddle, fetch_defuddle
from .scrapling_scraper import ScraplingScraper, fetch_scrapling

__all__ = [
    "RJinaAI",
    "MarkdownNew",
    "Defuddle",
    "ScraplingScraper",
    "fetch_r_jina_ai",
    "fetch_markdown_new",
    "fetch_defuddle",
    "fetch_scrapling",
]
