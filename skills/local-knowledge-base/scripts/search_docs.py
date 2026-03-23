#!/usr/bin/env python3
"""
Search Docs Script - 搜索脚本
命令行搜索文档
"""

import os
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from searcher import KnowledgeSearcher


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='搜索本地知识库')
    parser.add_argument('query', type=str, help='搜索关键词')
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='返回结果数量（默认：5）'
    )
    parser.add_argument(
        '--no-semantic',
        action='store_true',
        help='禁用语义搜索'
    )
    parser.add_argument(
        '--path-filter',
        type=str,
        default=None,
        help='路径过滤（只搜索包含此路径的文件）'
    )
    parser.add_argument(
        '--file-type',
        type=str,
        default=None,
        help='文件类型过滤（如：markdown, python）'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 本地知识库搜索")
    print("=" * 60)
    print(f"❓ 搜索：{args.query}")
    print(f"📊 返回结果：{args.top_k}")
    print("-" * 60)
    
    # 创建搜索器
    searcher = KnowledgeSearcher()
    
    if not searcher.documents:
        print("❌ 索引为空，请先运行重建索引")
        return
    
    # 构建过滤条件
    filters = {}
    if args.path_filter:
        filters['path_contains'] = args.path_filter
    if args.file_type:
        filters['file_type'] = args.file_type
    
    # 执行搜索
    results = searcher.search(
        args.query,
        top_k=args.top_k,
        use_semantic=not args.no_semantic,
        filters=filters
    )
    
    if not results:
        print("📭 没有找到相关结果")
        return
    
    # 显示结果
    print(f"\n📝 找到 {len(results)} 个相关结果:\n")
    
    for i, result in enumerate(results, 1):
        doc = result['document']
        score = result['score']
        
        print(f"【{i}】 {doc['title']}")
        print(f"   📄 路径：{doc['path']}")
        print(f"   📊 相关度：{score:.2%}")
        print(f"   🏷️  类型：{doc['type']}")
        
        # 显示匹配片段
        chunks = doc.get('chunks', [])
        if chunks:
            # 找最相关的分块（这里简化处理，显示第一个）
            chunk = chunks[0]
            text = chunk['text'][:200].replace('\n', ' ')
            print(f"   💡 片段：{text}...")
        
        print()
    
    print("=" * 60)


if __name__ == '__main__':
    main()
