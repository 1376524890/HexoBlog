"""
日志工具模块
Logger utility
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "wjx_automator",
    level: str = "INFO",
    output_dir: str = "logs"
) -> logging.Logger:
    """
    设置日志系统
    
    Args:
        name: 日志名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        output_dir: 日志输出目录
    
    Returns:
        配置好的 Logger 对象
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 获取或创建 logger
    logger = logging.getLogger(name)
    if isinstance(level, int):
        logger.setLevel(level)
    else:
        logger.setLevel(getattr(logging, level.upper()))
    
    # 清除已存在的 handler
    logger.handlers.clear()
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    if isinstance(level, int):
        console_handler.setLevel(level)
    else:
        console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件 handler (轮转日志)
    log_file = output_path / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "wjx_automator") -> logging.Logger:
    """
    获取已配置的 logger 实例
    
    Args:
        name: logger 名称
    
    Returns:
        Logger 对象
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    日志适配器，用于添加上下文信息
    """
    
    def process(self, msg, kwargs):
        """处理日志消息"""
        extra = self.extra if self.extra else {}
        return f"[{extra.get('worker_id', 'main')}] {msg}", kwargs
