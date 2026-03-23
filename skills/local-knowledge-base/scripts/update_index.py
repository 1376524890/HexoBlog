#!/usr/bin/env python3
"""
Update Index Script - 增量更新索引脚本
只更新修改的文件
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from indexer import DocumentIndexer
from document_loader import DocumentLoader


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增量更新本地知识库索引')
    parser.add_argument(
        '--path', 
        type=str, 
        default='.',
        help='要检查的目录路径（默认：当前目录）'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制全量更新'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 本地知识库索引更新工具")
    print("=" * 60)
    print(f"📂 检查目录：{args.path}")
    print("-" * 60)
    
    # 创建索引器
    indexer = DocumentIndexer()
    loader = DocumentLoader()
    
    # 获取所有支持的文件
    path = Path(args.path)
    files = list(path.rglob('*'))
    supported_files = [
        f for f in files if f.is_file() and loader._is_supported(str(f))
    ]
    
    print(f"📄 发现 {len(supported_files)} 个支持的文件")
    
    if args.force:
        print("⚠️  强制更新模式，将重新索引所有文件")
        count = indexer.rebuild_index(args.path)
    else:
        # 检查需要更新的文件
        existing_paths = {doc['path'] for doc in indexer.index['documents']}
        new_files = []
        modified_files = []
        
        for file_path in supported_files:
            path_str = str(file_path)
            
            if path_str not in existing_paths:
                new_files.append(file_path)
            else:
                # 检查文件是否修改
                doc = next((d for d in indexer.index['documents'] if d['path'] == path_str), None)
                if doc and file_path.stat().st_mtime > doc.get('last_modified', 0):
                    modified_files.append(file_path)
        
        print(f"📋 分析结果:")
        print(f"  🆕 新文件：{len(new_files)}")
        print(f"  ✏️  修改文件：{len(modified_files)}")
        
        if len(new_files) == 0 and len(modified_files) == 0:
            print("✨ 没有发现需要更新的文件")
            return
        
        # 更新文件
        count = 0
        
        if new_files:
            print(f"\n📥 索引 {len(new_files)} 个新文件...")
            for file_path in new_files:
                doc = indexer.index_file(str(file_path))
                if doc:
                    count += 1
                    print(f"  ✅ {file_path}")
        
        if modified_files:
            print(f"\n✏️  更新 {len(modified_files)} 个修改文件...")
            for file_path in modified_files:
                doc = indexer.index_file(str(file_path))
                if doc:
                    count += 1
                    print(f"  ✅ {file_path}")
        
        print("\n" + "=" * 60)
        print(f"✅ 索引更新完成！")
        print(f"📄 更新文件数：{count}")
        
        stats = indexer.get_statistics()
        print(f"📊 总文件数：{stats['total_documents']}")
        print(f"🕐 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


if __name__ == '__main__':
    main()
