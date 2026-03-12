"""
持续运行 Agent - 队列管理器
============================

负责管理待分析项目的队列，确保最大积压数量不超过 5 个。

核心功能:
- 队列管理 (添加、移除、检查)
- 队列长度限制 (最大 5 个)
- 队列持久化 (JSON 文件保存)
- 项目去重
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Set
from enum import Enum

# 配置日志
logger = logging.getLogger(__name__)


class QueueStatus(Enum):
    """队列状态"""
    PENDING = "pending"  # 待分析
    ANALYZING = "analyzing"  # 分析中
    EVALUATED = "evaluated"  # 已评估，待批准
    REJECTED = "rejected"  # 已拒绝
    APPROVED = "approved"  # 已批准
    INTEGRATED = "integrated"  # 已集成


@dataclass
class QueueItem:
    """队列项"""
    project_name: str
    repo_url: str
    added_time: str = field(default_factory=lambda: datetime.now().isoformat())
    status: QueueStatus = QueueStatus.PENDING
    priority: int = 0  # 优先级，越高越优先
    analysis_result: Optional[Dict] = None
    evaluation_result: Optional[Dict] = None
    last_checked: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QueueItem':
        """从字典创建"""
        data['status'] = QueueStatus(data['status'])
        return cls(**data)


@dataclass
class QueueConfig:
    """队列配置"""
    max_queue_size: int = 5  # 最大队列长度
    queue_file: str = "approval_requests/pending_approvals.json"  # 队列文件路径
    auto_cleanup: bool = True  # 自动清理过期项
    cleanup_age_hours: int = 168  # 7 天清理
    
    # 项目过滤配置
    min_stars: int = 10  # 最小星标数
    min_forks: int = 2  # 最小分叉数
    exclude_keywords: List[str] = field(default_factory=lambda: ["archive", "deprecated", "outdated"])
    
    # 优先级配置
    star_weight: float = 0.4  # 星标权重
    fork_weight: float = 0.3  # 分叉权重
    update_weight: float = 0.3  # 活跃度权重


class QueueManager:
    """队列管理器"""
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """
        初始化 QueueManager
        
        Args:
            config: 配置对象
        """
        self.config = config or QueueConfig()
        self.queue: List[QueueItem] = []
        self.processed_projects: Set[str] = set()  # 已处理的项目去重
        self.queue_file = Path(self.config.queue_file)
        
        # 加载现有队列
        self._load_queue()
        
        logger.info(f"QueueManager initialized with max size: {self.config.max_queue_size}")
        logger.info(f"Current queue size: {len(self.queue)}")
    
    def _load_queue(self):
        """从文件加载队列"""
        if not self.queue_file.exists():
            logger.info("No existing queue file found, starting fresh")
            return
        
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.queue = [QueueItem.from_dict(item) for item in data.get('queue', [])]
            self.processed_projects = set(data.get('processed_projects', []))
            
            logger.info(f"Loaded {len(self.queue)} items from queue file")
            
            # 清理过期项目
            if self.config.auto_cleanup:
                self._cleanup_old_projects()
                
        except Exception as e:
            logger.error(f"Failed to load queue: {e}")
            self.queue = []
    
    def _save_queue(self):
        """保存队列到文件"""
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "queue": [item.to_dict() for item in self.queue],
            "processed_projects": list(self.processed_projects),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved queue with {len(self.queue)} items")
    
    def add_project(self, project_name: str, repo_url: str, 
                    stars: int = 0, forks: int = 0, 
                    updated_at: str = "") -> Optional[QueueItem]:
        """
        添加项目到队列
        
        Args:
            project_name: 项目名称
            repo_url: 仓库 URL
            stars: 星标数
            forks: 分叉数
            updated_at: 更新时间
            
        Returns:
            QueueItem 或 None (如果队列已满或项目已存在)
        """
        # 检查重复
        if repo_url in self.processed_projects:
            logger.warning(f"Project {project_name} already processed, skipping")
            return None
        
        # 检查队列是否已满
        if len(self.queue) >= self.config.max_queue_size:
            logger.warning(f"Queue full ({len(self.queue)}/{self.config.max_queue_size}), rejecting new project")
            return None
        
        # 过滤检查
        if not self._pass_filters(stars, forks):
            logger.info(f"Project {project_name} failed filters (stars: {stars}, forks: {forks})")
            return None
        
        # 计算优先级
        priority = self._calculate_priority(stars, forks, updated_at)
        
        # 创建队列项
        item = QueueItem(
            project_name=project_name,
            repo_url=repo_url,
            priority=priority
        )
        
        # 添加到队列
        self.queue.append(item)
        self.processed_projects.add(repo_url)
        
        # 排序 (优先级高的在前)
        self.queue.sort(key=lambda x: x.priority, reverse=True)
        
        # 保存
        self._save_queue()
        
        logger.info(f"Added {project_name} to queue with priority {priority}")
        
        return item
    
    def remove_project(self, repo_url: str) -> bool:
        """
        从队列移除项目
        
        Args:
            repo_url: 仓库 URL
            
        Returns:
            是否成功移除
        """
        for i, item in enumerate(self.queue):
            if item.repo_url == repo_url:
                removed = self.queue.pop(i)
                logger.info(f"Removed {item.project_name} from queue")
                self._save_queue()
                return True
        
        return False
    
    def update_project(self, repo_url: str, **kwargs) -> bool:
        """
        更新队列项
        
        Args:
            repo_url: 仓库 URL
            **kwargs: 要更新的字段
            
        Returns:
            是否成功更新
        """
        for item in self.queue:
            if item.repo_url == repo_url:
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                        item.last_checked = datetime.now().isoformat()
                
                # 重新保存
                self._save_queue()
                logger.info(f"Updated {item.project_name}")
                return True
        
        return False
    
    def get_next_project(self) -> Optional[QueueItem]:
        """获取下一个待处理的项目"""
        if not self.queue:
            return None
        
        # 返回优先级最高的
        return self.queue[0]
    
    def get_pending_projects(self) -> List[QueueItem]:
        """获取所有待处理的项目"""
        return [item for item in self.queue if item.status == QueueStatus.PENDING]
    
    def get_evaluation_queue(self) -> List[QueueItem]:
        """获取已评估待批准的项目"""
        return [item for item in self.queue if item.status == QueueStatus.EVALUATED]
    
    def get_queue_size(self) -> int:
        """获取当前队列大小"""
        return len(self.queue)
    
    def is_queue_full(self) -> bool:
        """检查队列是否已满"""
        return len(self.queue) >= self.config.max_queue_size
    
    def get_queue_status(self) -> Dict:
        """获取队列状态摘要"""
        status_counts = {status: 0 for status in QueueStatus}
        
        for item in self.queue:
            status_counts[item.status] += 1
        
        return {
            "total": len(self.queue),
            "max_size": self.config.max_queue_size,
            "full": self.is_queue_full(),
            "by_status": {k.value: v for k, v in status_counts.items()},
            "oldest_added": self.queue[0].added_time if self.queue else None,
            "newest_added": self.queue[-1].added_time if self.queue else None
        }
    
    def _calculate_priority(self, stars: int, forks: int, updated_at: str) -> float:
        """
        计算项目优先级
        
        Args:
            stars: 星标数
            forks: 分叉数
            updated_at: 更新时间
            
        Returns:
            优先级分数
        """
        score = 0.0
        
        # 星标分数 (0-40 分)
        if stars:
            score += min(stars / 10, 40) * self.config.star_weight
        
        # 分叉分数 (0-30 分)
        if forks:
            score += min(forks / 5, 30) * self.config.fork_weight
        
        # 活跃度分数 (0-30 分)
        if updated_at:
            try:
                from datetime import datetime
                updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_ago = (datetime.now(updated.tzinfo) - updated).days
                
                if days_ago < 7:
                    score += 30 * self.config.update_weight
                elif days_ago < 30:
                    score += 20 * self.config.update_weight
                elif days_ago < 90:
                    score += 10 * self.config.update_weight
                else:
                    score += 5 * self.config.update_weight
            except:
                pass
        
        return score
    
    def _pass_filters(self, stars: int, forks: int) -> bool:
        """检查项目是否通过过滤器"""
        if stars < self.config.min_stars:
            return False
        if forks < self.config.min_forks:
            return False
        
        # 检查排除关键词
        return True  # 这里简化，实际可以添加更多过滤逻辑
    
    def _cleanup_old_projects(self):
        """清理过期项目"""
        now = datetime.now()
        cleaned = 0
        
        for item in self.queue:
            try:
                added = datetime.fromisoformat(item.added_time)
                age_hours = (now - added).total_seconds() / 3600
                
                if age_hours > self.config.cleanup_age_hours:
                    self.queue.remove(item)
                    cleaned += 1
                    logger.info(f"Cleaned up old project: {item.project_name}")
            except:
                continue
        
        if cleaned > 0:
            self._save_queue()
            logger.info(f"Cleaned {cleaned} old projects")
    
    def export_pending_approvals(self, output_dir: str = "approval_requests/") -> str:
        """
        导出待批准项目列表
        
        Args:
            output_dir: 输出目录
            
        Returns:
            输出的文件路径
        """
        # 获取已评估的项目
        pending = [item for item in self.queue if item.status == QueueStatus.EVALUATED]
        
        if not pending:
            logger.info("No pending approvals to export")
            return ""
        
        # 生成审批文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir) / f"approval_request_{timestamp}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_pending": len(pending),
            "items": [
                {
                    "project_name": item.project_name,
                    "repo_url": item.repo_url,
                    "priority": item.priority,
                    "added_time": item.added_time,
                    "evaluation": item.evaluation_result
                }
                for item in pending
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(pending)} pending approvals to {output_path}")
        
        return str(output_path)
    
    def close(self):
        """清理资源"""
        self._save_queue()
        logger.info("QueueManager closed")


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Queue Manager for Running Agent")
    parser.add_argument("--add", nargs=2, metavar=("NAME", "URL"), help="Add project to queue")
    parser.add_argument("--remove", help="Remove project by URL")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--export", action="store_true", help="Export pending approvals")
    
    args = parser.parse_args()
    
    manager = QueueManager()
    
    try:
        if args.add:
            item = manager.add_project(args.add[0], args.add[1])
            if item:
                print(f"Added {args.add[0]} to queue")
            else:
                print("Failed to add to queue (full or duplicate)")
        
        elif args.remove:
            if manager.remove_project(args.remove):
                print(f"Removed {args.remove}")
            else:
                print("Project not found in queue")
        
        elif args.status:
            status = manager.get_queue_status()
            print(f"Queue Status:")
            print(f"  Total: {status['total']} / {status['max_size']}")
            print(f"  Full: {status['full']}")
            print(f"  By status: {status['by_status']}")
        
        elif args.export:
            path = manager.export_pending_approvals()
            if path:
                print(f"Exported to: {path}")
            else:
                print("Nothing to export")
        
        else:
            # 默认显示状态
            status = manager.get_queue_status()
            print(f"Queue Status: {status['total']} / {status['max_size']}")
            
    finally:
        manager.close()


if __name__ == "__main__":
    main()
