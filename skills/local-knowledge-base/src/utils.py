#!/usr/bin/env python3
"""
Utility Functions - 工具函数
提供通用工具函数
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional


def load_config(config_path: str) -> Dict:
    """加载配置文件"""
    path = Path(config_path)
    
    if not path.exists():
        return {}
    
    suffix = path.suffix.lower()
    
    if suffix == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif suffix in ['.yaml', '.yml']:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"不支持的配置文件类型：{suffix}")


def save_config(config: Dict, config_path: str):
    """保存配置文件"""
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    suffix = path.suffix.lower()
    
    if suffix == '.json':
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    elif suffix in ['.yaml', '.yml']:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
    else:
        raise ValueError(f"不支持的配置文件类型：{suffix}")


def format_bytes(size: int) -> str:
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def format_timestamp(timestamp: float) -> str:
    """格式化时间戳"""
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def highlight_text(text: str, keywords: List[str]) -> str:
    """高亮关键词"""
    for keyword in keywords:
        if keyword in text:
            text = text.replace(keyword, f"**{keyword}**")
    return text


def truncate_text(text: str, max_length: int = 500) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
