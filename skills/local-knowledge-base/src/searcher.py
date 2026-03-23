#!/usr/bin/env python3
"""
Knowledge Searcher - 知识检索器
支持语义搜索和关键词搜索
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class KnowledgeSearcher:
    """知识检索器类"""
    
    def __init__(self, index_path: str = None):
        """
        初始化检索器
        
        Args:
            index_path: 索引文件路径
        """
        if index_path is None:
            index_path = Path(__file__).parent.parent / 'index' / 'doc_index.json'
        
        self.index_path = Path(index_path)
        self.documents = []
        
        self._load_index()
    
    def _load_index(self) -> bool:
        """加载索引文件"""
        if not self.index_path.exists():
            return False
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            self.documents = index_data.get('documents', [])
            return True
            
        except Exception as e:
            print(f"加载索引失败：{e}")
            return False
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 简单的英文分词
        return text.lower().split()
    
    def _calculate_tfidf(self, doc: Dict, query_tokens: List[str]) -> float:
        """
        计算 TF-IDF 相关度
        
        Args:
            doc: 文档信息
            query_tokens: 查询分词
            
        Returns:
            TF-IDF 分数
        """
        # 提取文档的所有分块
        all_tokens = []
        for chunk in doc.get('chunks', []):
            all_tokens.extend(self._tokenize(chunk['text']))
        
        if not all_tokens:
            return 0.0
        
        # 计算词频
        doc_freq = {}
        for token in all_tokens:
            doc_freq[token] = doc_freq.get(token, 0) + 1
        
        # 计算匹配分数
        match_count = 0
        for token in query_tokens:
            if token in doc_freq:
                match_count += doc_freq[token]
        
        # 归一化分数
        return match_count / len(all_tokens)
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        use_semantic: bool = True,
        filters: Dict = None
    ) -> List[Dict]:
        """
        搜索文档
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            use_semantic: 是否使用语义搜索
            filters: 过滤条件
            
        Returns:
            搜索结果列表，包含文档信息和相关度
        """
        if not self.documents:
            return []
        
        # 应用过滤
        if filters:
            docs = self._apply_filters(self.documents, filters)
        else:
            docs = self.documents
        
        # 计算相关度
        results = []
        query_tokens = self._tokenize(query)
        
        for doc in docs:
            score = 0.0
            
            # 1. TF-IDF 关键词搜索
            tfidf_score = self._calculate_tfidf(doc, query_tokens)
            score += tfidf_score * 0.7
            
            # 2. 语义搜索（如果可用）
            if use_semantic and 'embedding' in doc:
                semantic_score = self._calculate_semantic(doc, query)
                score += semantic_score * 0.3
            
            if score > 0:
                results.append({
                    'document': doc,
                    'score': score
                })
        
        # 排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def _calculate_semantic(self, doc: Dict, query: str) -> float:
        """
        计算语义相关度（简化版）
        
        Args:
            doc: 文档信息
            query: 查询文本
            
        Returns:
            语义相似度分数
        """
        if 'embedding' not in doc:
            return 0.0
        
        # 简化：基于文本重叠度
        query_words = set(query.lower().split())
        doc_text = doc.get('content', '').lower()
        
        overlap = sum(1 for word in query_words if word in doc_text)
        return overlap / len(query_words) if query_words else 0.0
    
    def _apply_filters(self, docs: List[Dict], filters: Dict) -> List[Dict]:
        """应用过滤条件"""
        result = docs
        
        if 'path_contains' in filters:
            result = [d for d in result if filters['path_contains'] in d['path']]
        
        if 'file_type' in filters:
            result = [d for d in result if d['type'] == filters['file_type']]
        
        return result
