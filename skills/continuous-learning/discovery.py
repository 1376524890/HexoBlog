"""
持续学习进化系统 - Discovery 模块
=====================================

负责从 GitHub 搜索和发现潜在的 Skill 项目。

功能:
- GitHub API 搜索（关键词、星标数、活跃度）
- 结果去重和过滤
- 输出项目列表（JSON 格式）
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Set
from pathlib import Path

import github3
from requests.exceptions import RequestException

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class GitHubProject:
    """GitHub 项目信息"""
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    stars: int
    forks: int
    language: Optional[str]
    updated_at: str
    created_at: str
    topics: List[str] = field(default_factory=list)
    score: float = 0.0
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class DiscoveryConfig:
    """Discovery 模块配置"""
    keywords: List[str] = field(default_factory=lambda: ["skill", "agent", "ai"])
    min_stars: int = 10
    min_forks: int = 2
    min_language: str = "Python"
    sort_by: str = "stars"  # stars, updated, created
    order: str = "desc"  # asc, desc
    limit: int = 50
    exclude_keywords: List[str] = field(default_factory=list)
    include_topics: List[str] = field(default_factory=list)


class DiscoveryEngine:
    """GitHub 项目发现引擎"""
    
    def __init__(self, token: Optional[str] = None, config: Optional[DiscoveryConfig] = None):
        """
        初始化 DiscoveryEngine
        
        Args:
            token: GitHub API token (可选，未提供则有速率限制)
            config: 配置对象
        """
        self.token = token
        self.config = config or DiscoveryConfig()
        self.github = github3.login(token=token) if token else github3.GitHub()
        self.seen_repos: Set[str] = set()
        
        logger.info(f"DiscoveryEngine initialized with token: {bool(token)}")
    
    def search(self, keyword: Optional[str] = None) -> List[GitHubProject]:
        """
        搜索 GitHub 项目
        
        Args:
            keyword: 搜索关键词，如果为 None 则使用配置中的关键词
            
        Returns:
            项目列表
        """
        search_query = keyword or self._build_query()
        logger.info(f"Searching GitHub with query: {search_query}")
        
        try:
            results = self.github.search_repositories(search_query, per_page=100)
            projects = []
            
            for repo in results:
                project = self._process_repo(repo)
                if project and self._filter_project(project):
                    projects.append(project)
                    
                if len(projects) >= self.config.limit:
                    break
            
            logger.info(f"Found {len(projects)} projects matching criteria")
            return projects
            
        except RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []
    
    def _build_query(self) -> str:
        """构建 GitHub 搜索查询"""
        parts = []
        
        # 关键词
        if self.config.keywords:
            keywords = " OR ".join(self.config.keywords)
            parts.append(f"({keywords})")
        
        # 排除关键词
        if self.config.exclude_keywords:
            for kw in self.config.exclude_keywords:
                parts.append(f"-{kw}")
        
        # 语言
        if self.config.min_language:
            parts.append(f"language:{self.config.min_language}")
        
        # 星标和分叉
        if self.config.min_stars > 0:
            parts.append(f"stars:>{self.config.min_stars}")
        if self.config.min_forks > 0:
            parts.append(f"forks:>{self.config.min_forks}")
        
        # 话题
        if self.config.include_topics:
            for topic in self.config.include_topics:
                parts.append(f"topic:{topic}")
        
        return " ".join(parts)
    
    def _process_repo(self, repo) -> Optional[GitHubProject]:
        """处理单个仓库对象"""
        try:
            full_name = repo.full_name
            if full_name in self.seen_repos:
                return None
            
            self.seen_repos.add(full_name)
            
            # 计算综合评分
            score = self._calculate_score(repo)
            
            # 处理日期，兼容多种格式
            def safe_isoformat(dt_obj):
                """安全转换日期为 ISO 格式"""
                if not dt_obj:
                    return ""
                try:
                    # 如果已经是字符串，直接返回
                    if isinstance(dt_obj, str):
                        return dt_obj
                    # 尝试转换
                    return dt_obj.isoformat()
                except Exception:
                    # 如果失败，尝试重新解析
                    try:
                        return datetime.fromisoformat(str(dt_obj).replace('Z', '+00:00')).isoformat()
                    except:
                        return ""
            
            # 处理 topics，兼容 list 和对象
            def get_topics(repo):
                """获取项目话题列表"""
                if not hasattr(repo, 'topics'):
                    return []
                topics_obj = repo.topics
                if isinstance(topics_obj, list):
                    return topics_obj
                elif hasattr(topics_obj, 'names'):
                    return list(topics_obj.names)
                return []
            
            return GitHubProject(
                name=repo.name,
                full_name=full_name,
                description=repo.description,
                html_url=repo.html_url,
                stars=repo.stargazers_count or 0,
                forks=repo.forks_count or 0,
                language=repo.language,
                updated_at=safe_isoformat(repo.updated_at),
                created_at=safe_isoformat(repo.created_at),
                topics=get_topics(repo),
                score=score
            )
            
        except Exception as e:
            logger.warning(f"Error processing repo {repo.full_name}: {e}")
            return None
    
    def _calculate_score(self, repo) -> float:
        """计算项目综合评分"""
        score = 0.0
        
        # 星标分数 (0-40 分)
        if repo.stargazers_count:
            score += min(repo.stargazers_count / 10, 40)
        
        # 分叉分数 (0-20 分)
        if repo.forks_count:
            score += min(repo.forks_count / 5, 20)
        
        # 语言分数 (0-20 分)
        if repo.language == self.config.min_language:
            score += 20
        
        # 活跃度分数 (0-20 分)
        try:
            if repo.updated_at:
                updated = datetime.fromisoformat(repo.updated_at.replace('Z', '+00:00'))
                days_ago = (datetime.now(updated.tzinfo) - updated).days
                if days_ago < 7:
                    score += 20
                elif days_ago < 30:
                    score += 15
                elif days_ago < 90:
                    score += 10
                else:
                    score += 5
        except:
            pass
        
        return score
    
    def _filter_project(self, project: GitHubProject) -> bool:
        """过滤项目"""
        # 检查排除关键词
        if self.config.exclude_keywords:
            text = f"{project.name} {project.description or ''}".lower()
            for kw in self.config.exclude_keywords:
                if kw.lower() in text:
                    return False
        
        # 检查话题
        if self.config.include_topics:
            if not any(topic in project.topics for topic in self.config.include_topics):
                return False
        
        return True
    
    def save_to_json(self, projects: List[GitHubProject], output_path: str) -> None:
        """将结果保存到 JSON 文件"""
        data = {
            "search_time": datetime.now().isoformat(),
            "total_found": len(projects),
            "projects": [p.to_dict() for p in projects]
        }
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(projects)} projects to {output_path}")
    
    def close(self):
        """关闭连接"""
        self.github = None
        logger.info("DiscoveryEngine closed")


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Skill Discovery Engine")
    parser.add_argument("--token", help="GitHub API token")
    parser.add_argument("--keywords", nargs="+", default=["skill", "agent"])
    parser.add_argument("--min-stars", type=int, default=10)
    parser.add_argument("--min-forks", type=int, default=2)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", default="discovery_results.json")
    parser.add_argument("--exclude", nargs="+", default=[])
    
    args = parser.parse_args()
    
    config = DiscoveryConfig(
        keywords=args.keywords,
        min_stars=args.min_stars,
        min_forks=args.min_forks,
        limit=args.limit,
        exclude_keywords=args.exclude
    )
    
    engine = DiscoveryEngine(token=args.token, config=config)
    
    try:
        projects = engine.search()
        engine.save_to_json(projects, args.output)
        print(f"Discovered {len(projects)} projects, saved to {args.output}")
    finally:
        engine.close()


if __name__ == "__main__":
    main()
