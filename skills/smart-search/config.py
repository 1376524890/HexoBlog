"""
SmartSearch - 智能降级网络搜索系统配置文件
============================================

配置项说明：
- SEARCH_CONFIG: 搜索层配置
- SCRAPER_CONFIG: 深度抓取配置
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class SearchConfig:
    """搜索配置"""
    max_results: int = 20
    timeout_seconds: int = 30
    retries: int = 2
    concurrency: int = 10
    relevance_threshold: float = 0.5
    top_n_results: int = 5
    similarity_threshold: float = 0.8


@dataclass
class ScraperConfig:
    """深度抓取配置"""
    fallback_chain: List[str] = field(default_factory=lambda: [
        "r_jina_ai", "markdown_new", "defuddle", "scrapling"
    ])
    timeout_seconds: int = 30
    max_content_length: int = 50000
    retries: int = 2
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ])


@dataclass
class AppConfig:
    """主配置"""
    search: SearchConfig = field(default_factory=SearchConfig)
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    root_dir: str = "./"
    cache_dir: str = "./cache"
    output_dir: str = "./output"


# 全局配置实例
config = AppConfig()


def get_config() -> AppConfig:
    """获取配置实例"""
    return config
