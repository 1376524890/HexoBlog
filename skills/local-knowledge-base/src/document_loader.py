#!/usr/bin/env python3
"""
Document Loader - 文档加载器
支持多种文档类型的加载和解析
"""

import os
import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class DocumentLoader:
    """文档加载器类"""
    
    SUPPORTED_EXTENSIONS = {
        '.md', '.txt', '.rst', '.org', '.asciidoc',  # 文本类
        '.json', '.yaml', '.yml', '.toml', '.ini',    # 配置类
        '.py', '.js', '.ts', '.java', '.c', '.cpp',   # 代码类
        '.html', '.css', '.sql', '.xml'               # 标记语言
    }
    
    def __init__(self, max_chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化文档加载器
        
        Args:
            max_chunk_size: 最大分块大小
            chunk_overlap: 分块重叠部分
        """
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _split_text(self, text: str) -> List[str]:
        """
        简单的文本分块函数
        
        Args:
            text: 要分块的文本
            
        Returns:
            分块列表
        """
        # 按段落分割
        paragraphs = re.split(r'\n\n+', text)
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.max_chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 如果段落本身超过最大长度，按句子分割
                if len(para) > self.max_chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= self.max_chunk_size:
                            if current_chunk:
                                current_chunk += " " + sentence
                            else:
                                current_chunk = sentence
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sentence[:self.max_chunk_size]
                
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text]
    
    def load_file(self, file_path: str) -> Optional[Dict]:
        """
        加载单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档信息字典，包括 path, title, content 等
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        if not self._is_supported(file_path):
            return None
        
        try:
            # 读取文件内容
            content = path.read_text(encoding='utf-8')
            
            # 解析文档
            doc_info = self._parse_document(path, content)
            
            # 分块处理
            doc_info['chunks'] = self._chunk_document(content)
            
            return doc_info
            
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return None
    
    def load_directory(self, dir_path: str, recursive: bool = True) -> List[Dict]:
        """
        批量加载目录下的所有文档
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归子目录
            
        Returns:
            文档列表
        """
        documents = []
        path = Path(dir_path)
        
        if not path.exists():
            return documents
        
        # 查找文件
        if recursive:
            files = path.rglob('*')
        else:
            files = path.iterdir()
        
        for file_path in files:
            if file_path.is_file() and self._is_supported(str(file_path)):
                doc = self.load_file(str(file_path))
                if doc:
                    documents.append(doc)
        
        return documents
    
    def _is_supported(self, file_path: str) -> bool:
        """检查文件类型是否支持"""
        return Path(file_path).suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def _parse_document(self, path: Path, content: str) -> Dict:
        """
        解析文档信息
        
        Args:
            path: 文件路径
            content: 文件内容
            
        Returns:
            文档信息字典
        """
        # 提取标题（从文件第一行或标题标记）
        title = self._extract_title(path, content)
        
        return {
            'path': str(path),
            'title': title,
            'type': self._get_file_type(path),
            'size': path.stat().st_size,
            'last_modified': path.stat().st_mtime,
            'content': content
        }
    
    def _extract_title(self, path: Path, content: str) -> str:
        """提取文档标题"""
        # 优先从 Markdown 标题提取
        if path.suffix.lower() == '.md':
            lines = content.split('\n')
            for line in lines[:10]:  # 只看前 10 行
                if line.startswith('# '):
                    return line[2:].strip()
        
        # 否则使用文件名
        return path.stem
    
    def _get_file_type(self, path: Path) -> str:
        """获取文件类型"""
        ext = path.suffix.lower()
        type_map = {
            '.md': 'markdown',
            '.txt': 'text',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.xml': 'xml'
        }
        return type_map.get(ext, 'unknown')
    
    def _chunk_document(self, content: str) -> List[Dict]:
        """
        将文档分块
        
        Returns:
            分块列表，每个块包含 id, text, start, end
        """
        chunks = self._split_text(content)
        
        chunk_list = []
        current_pos = 0
        
        for i, chunk in enumerate(chunks):
            chunk_list.append({
                'id': f"chunk-{i}",
                'text': chunk,
                'start': current_pos,
                'end': current_pos + len(chunk)
            })
            current_pos += len(chunk) + 2  # +2 for double newline
        
        return chunk_list
