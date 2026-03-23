#!/usr/bin/env python3
"""
Document Indexer - 文档索引器
负责建立和维护文档索引
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class DocumentIndexer:
    """文档索引器类"""
    
    def __init__(
        self, 
        index_dir: str = None,
        embed_model: str = "all-MiniLM-L6-v2"
    ):
        """
        初始化索引器
        
        Args:
            index_dir: 索引目录
            embed_model: embedding 模型名称
        """
        if index_dir is None:
            index_dir = Path(__file__).parent.parent / 'index'
        
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.index_dir / 'doc_index.json'
        self.metadata_path = self.index_dir / 'metadata.json'
        
        from document_loader import DocumentLoader
        self.loader = DocumentLoader()
        self.embed_model = embed_model
        self.index = self._load_or_create_index()
    
    def _load_or_create_index(self) -> Dict:
        """加载现有索引或创建新索引"""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载索引失败：{e}")
        
        # 创建新索引
        return {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'documents': []
        }
    
    def _generate_doc_id(self, file_path: str) -> str:
        """生成文档唯一 ID"""
        content = Path(file_path).read_text(encoding='utf-8')
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _compute_embedding(self, text: str) -> Optional[List[float]]:
        """计算文本的 embedding（简化版）"""
        # 简化版：使用文本长度和字符编码生成简单特征
        # 实际应该使用 SentenceTransformer
        try:
            import numpy as np
            # 生成简单的哈希特征
            hash_val = hashlib.md5(text.encode()).hexdigest()
            # 转换为固定长度的特征向量（简化版）
            return [float(int(hash_val[i:i+2], 16) / 255.0) for i in range(0, 384, 2)]
        except:
            return None
    
    def index_file(self, file_path: str) -> Optional[Dict]:
        """
        索引单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            索引后的文档信息
        """
        # 加载文档
        doc = self.loader.load_file(file_path)
        if not doc:
            return None
        
        # 生成文档 ID
        doc['id'] = self._generate_doc_id(file_path)
        
        # 计算 embedding
        doc['embedding'] = self._compute_embedding(doc['content'])
        
        # 存储到索引
        self._store_document(doc)
        
        # 更新索引时间
        self.index['updated_at'] = datetime.now().isoformat()
        self._save_index()
        
        return doc
    
    def index_directory(
        self, 
        dir_path: str, 
        recursive: bool = True,
        incremental: bool = True
    ) -> int:
        """
        批量索引目录
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归
            incremental: 是否增量更新
            
        Returns:
            索引的文件数量
        """
        paths = []
        path = Path(dir_path)
        
        if recursive:
            paths = list(path.rglob('*'))
        else:
            paths = list(path.iterdir())
        
        # 过滤出文件
        file_paths = [p for p in paths if p.is_file()]
        
        # 筛选支持的类型
        file_paths = [p for p in file_paths if self.loader._is_supported(str(p))]
        
        # 增量更新：只处理新文件
        if incremental:
            existing_paths = {doc['path'] for doc in self.index['documents']}
            new_files = [p for p in file_paths if str(p) not in existing_paths]
            
            if new_files:
                print(f"发现 {len(new_files)} 个新文件，开始索引...")
            else:
                print("没有新文件，无需更新")
                return 0
        
        # 索引所有文件
        count = 0
        for file_path in file_paths:
            doc = self.index_file(str(file_path))
            if doc:
                count += 1
        
        return count
    
    def _store_document(self, doc: Dict):
        """存储文档到索引"""
        # 检查是否已存在
        for i, existing_doc in enumerate(self.index['documents']):
            if existing_doc['id'] == doc['id']:
                self.index['documents'][i] = doc
                return
        
        # 新增文档
        self.index['documents'].append(doc)
    
    def _save_index(self):
        """保存索引到文件"""
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
            
            # 保存元数据
            self._save_metadata()
            
        except Exception as e:
            print(f"保存索引失败：{e}")
    
    def _save_metadata(self):
        """保存元数据"""
        metadata = {
            'total_documents': len(self.index['documents']),
            'last_indexed': self.index['updated_at'],
            'index_version': self.index['version']
        }
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def rebuild_index(self, dir_path: str = None) -> int:
        """
        重建整个索引
        
        Args:
            dir_path: 要索引的目录，默认是当前工作目录
            
        Returns:
            索引的文件数量
        """
        if dir_path is None:
            dir_path = '.'
        
        print("开始重建索引...")
        
        # 清空现有索引
        self.index['documents'] = []
        self.index['updated_at'] = datetime.now().isoformat()
        
        # 重新索引
        count = self.index_directory(dir_path, recursive=True, incremental=False)
        
        self._save_index()
        
        print(f"索引重建完成，共索引 {count} 个文件")
        return count
    
    def get_statistics(self) -> Dict:
        """获取索引统计信息"""
        return {
            'total_documents': len(self.index['documents']),
            'last_updated': self.index['updated_at'],
            'index_version': self.index['version']
        }
