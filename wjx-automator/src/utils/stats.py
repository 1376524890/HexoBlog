"""
统计数据处理模块
Statistics data processing
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_question_stats(filepath: str) -> Dict[str, Any]:
    """
    加载问题统计数据
    
    Args:
        filepath: CSV 或 JSON 数据文件路径
    
    Returns:
        问题统计字典
    """
    path = Path(filepath)
    
    if path.suffix == '.csv':
        return _load_from_csv(filepath)
    elif path.suffix == '.json':
        return _load_from_json(filepath)
    else:
        raise ValueError(f"不支持的文件格式：{path.suffix}")


def _load_from_csv(filepath: str) -> Dict[str, Any]:
    """从 CSV 文件加载统计数据"""
    stats = {}
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            question_id = row.get('question_id', row.get('QID', row.get('question', '')))
            if not question_id:
                continue
            
            question_id = str(question_id).strip()
            
            # 解析选项分布 - 支持多种格式
            options_field = row.get('options', row.get('options_distribution', row.get('distribution', row.get('options_distribution', ''))))
            
            # 对于简答题，options 字段可能为空，但仍需加载
            if options_field:
                distribution = _parse_distribution_string(options_field)
            else:
                distribution = {}
            
            stats[question_id] = {
                'type': row.get('type', row.get('question_type', 'unknown')),
                'total_responses': int(row.get('total_responses', row.get('total', 0))),
                'distribution': distribution,
                'raw_data': row
            }
    
    return stats


def _parse_distribution_string(distribution_str: str) -> Dict[str, float]:
    """
    解析分布字符串
    
    支持格式:
    - "选项 A (30%), 选项 B (50%), 选项 C (20%)"
    - "选项 A: 30%, 选项 B: 50%, 选项 C: 20%"
    - "A:30,B:50,C:20"
    
    Args:
        distribution_str: 分布字符串
    
    Returns:
        {选项名称：概率}
    """
    distribution = {}
    
    # 模式 1: "选项 A (30%)" 或 "选项 A(30%)"
    pattern1 = r'([^,(]+?)\s*\(\s*(\d+)%?\)'
    matches = re.findall(pattern1, distribution_str)
    if matches:
        for option, percent in matches:
            option = option.strip()
            try:
                distribution[option] = float(percent) / 100.0
            except ValueError:
                continue
        
        if distribution:
            # 归一化
            total = sum(distribution.values())
            if total > 0:
                distribution = {k: v / total for k, v in distribution.items()}
            return distribution
    
    # 模式 2: "选项 A: 30%" 或 "选项 A:30%"
    pattern2 = r'([^:(]+?):\s*(\d+)%?'
    matches = re.findall(pattern2, distribution_str)
    if matches:
        for option, percent in matches:
            option = option.strip()
            try:
                distribution[option] = float(percent) / 100.0
            except ValueError:
                continue
        
        if distribution:
            total = sum(distribution.values())
            if total > 0:
                distribution = {k: v / total for k, v in distribution.items()}
            return distribution
    
    # 模式 3: "A:30,B:50,C:20"
    pattern3 = r'([^,;:]+):(\d+)'
    matches = re.findall(pattern3, distribution_str)
    if matches:
        for option, percent in matches:
            option = option.strip()
            try:
                distribution[option] = float(percent) / 100.0
            except ValueError:
                continue
        
        if distribution:
            total = sum(distribution.values())
            if total > 0:
                distribution = {k: v / total for k, v in distribution.items()}
            return distribution
    
    return distribution


def _load_from_json(filepath: str) -> Dict[str, Any]:
    """从 JSON 文件加载统计数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 确保数据结构正确
    stats = {}
    for question_id, question_data in data.items():
        if isinstance(question_data, dict):
            # 如果有 options 列表，转换为分布
            if 'options' in question_data:
                question_data['distribution'] = _calculate_distribution(question_data['options'])
            stats[question_id] = question_data
    
    return stats


def _calculate_distribution(options: List[Dict]) -> Dict[str, float]:
    """
    从选项列表计算分布
    
    Args:
        options: [{'name': '选项 A', 'count': 30}, ...]
    
    Returns:
        {选项名称：概率}
    """
    total = sum(opt.get('count', opt.get('frequency', 0)) for opt in options)
    
    if total == 0:
        return {}
    
    return {
        opt['name']: opt.get('count', opt.get('frequency', 0)) / total
        for opt in options
    }


def calculate_distribution(counts: Dict[str, int]) -> Dict[str, float]:
    """
    从计数字典计算概率分布
    
    Args:
        counts: {'选项 A': 30, '选项 B': 50, ...}
    
    Returns:
        {'选项 A': 0.3, '选项 B': 0.5, ...}
    """
    total = sum(counts.values())
    
    if total == 0:
        return {}
    
    return {k: v / total for k, v in counts.items()}


def get_expected_value(distribution: Dict[str, float]) -> Optional[float]:
    """
    计算期望值（用于量表题）
    
    Args:
        distribution: {'1': 0.1, '2': 0.2, '3': 0.4, '4': 0.2, '5': 0.1}
    
    Returns:
        期望值
    """
    if not distribution:
        return None
    
    return sum(float(k) * v for k, v in distribution.items())


def validate_distribution(distribution: Dict[str, float]) -> bool:
    """
    验证分布是否有效
    
    Args:
        distribution: 分布字典
    
    Returns:
        是否有效
    """
    if not distribution:
        return False
    
    total = sum(distribution.values())
    return 0.99 <= total <= 1.01  # 允许浮点误差
