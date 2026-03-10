"""
SmartSearch 日志模块
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class LogConfig:
    """日志配置"""
    def __init__(self):
        self.level = "INFO"
        self.output_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.output_file = "logs/smartsearch.log"
        self.max_bytes = 10485760
        self.backup_count = 5


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# 预定义日志器
engine_logger = get_logger("SmartSearch.Engines")
scraper_logger = get_logger("SmartSearch.Scraper")
search_logger = get_logger("SmartSearch.Search")
utils_logger = get_logger("SmartSearch.Utils")
