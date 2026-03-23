#!/usr/bin/env python3
"""
Rebuild Index Script - 重建索引脚本
手动重建整个索引
"""

import os
import sys
from pathlib import Path

# 添加 src 和脚本目录到路径
script_dir = Path(__file__).parent
src_dir = script_dir / 'src'
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(src_dir))

from indexer import DocumentIndexer


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='重建本地知识库索引')
    parser.add_argument(
        '--path', 
        type=str, 
        default='.',
        help='要索引的目录路径（默认：当前目录）'
    )
    parser.add_argument(
        '--embed-model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='embedding 模型名称（默认：all-MiniLM-L6-v2）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅显示将要索引的文件，不实际执行'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📚 本地知识库索引重建工具")
    print("=" * 60)
    print(f"📂 索引目录：{args.path}")
    print(f"🧠 Embedding 模型：{args.embed_model}")
    print("-" * 60)
    
    # 创建索引器
    indexer = DocumentIndexer(embed_model=args.embed_model)
    
    if args.dry_run:
        # 干跑模式：显示将要索引的文件
        from document_loader import DocumentLoader
        loader = DocumentLoader()
        
        path = Path(args.path)
        files = list(path.rglob('*'))
        supported_files = [
            f for f in files if f.is_file() and loader._is_supported(str(f))
        ]
        
        print(f"📄 发现 {len(supported_files)} 个支持的文件：")
        for file in sorted(supported_files)[:20]:  # 只显示前 20 个
            print(f"  - {file}")
        if len(supported_files) > 20:
            print(f"  ... 还有 {len(supported_files) - 20} 个文件")
    else:
        # 实际执行
        count = indexer.rebuild_index(args.path)
        
        print("=" * 60)
        print(f"✅ 索引重建完成！")
        print(f"📄 索引文件数：{count}")
        
        # 显示统计信息
        stats = indexer.get_statistics()
        print(f"📊 索引版本：{stats['index_version']}")
        print(f"🕐 最后更新：{stats['last_updated']}")
        print("=" * 60)


if __name__ == '__main__':
    main()
