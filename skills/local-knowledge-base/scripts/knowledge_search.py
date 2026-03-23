#!/usr/bin/env python3
"""
本地知识检索 - 快速使用脚本
在 OpenClaw 中调用本地知识库检索相关文档
"""

import sys
from pathlib import Path

# 添加路径
kb_path = Path(__file__).parent / 'skills' / 'local-knowledge-base'
sys.path.insert(0, str(kb_path / 'src'))

from searcher import KnowledgeSearcher


def search_workspace(query: str, top_k: int = 5) -> str:
    """
    在工作空间中搜索相关文档
    
    Args:
        query: 搜索查询
        top_k: 返回结果数量
        
    Returns:
        格式化后的搜索结果
    """
    # 创建搜索器
    searcher = KnowledgeSearcher(
        index_path=kb_path / 'index' / 'doc_index.json'
    )
    
    if not searcher.documents:
        return "索引为空，请先运行重建索引"
    
    # 执行搜索
    results = searcher.search(query, top_k=top_k)
    
    if not results:
        return "未找到相关结果"
    
    # 格式化输出
    output = f"找到 {len(results)} 个相关文档:\n\n"
    
    for i, result in enumerate(results, 1):
        doc = result['document']
        score = result['score']
        
        output += f"【{i}】 {doc['title']}\n"
        output += f"   📄 路径：{doc['path']}\n"
        output += f"   📊 相关度：{score:.2%}\n"
        
        # 显示片段
        chunks = doc.get('chunks', [])
        if chunks:
            text = chunks[0]['text'][:150].replace('\n', ' ')
            output += f"   💡 片段：{text}...\n"
        
        output += "\n"
    
    return output


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='在工作空间中搜索文档')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--top-k', type=int, default=5, help='返回结果数量')
    
    args = parser.parse_args()
    
    print(search_workspace(args.query, args.top_k))
