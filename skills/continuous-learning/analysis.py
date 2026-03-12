"""
持续学习进化系统 - Analysis 模块
====================================

负责深度分析 GitHub 项目，生成详细的分析报告。

功能:
- 临时克隆仓库
- 调用 Claude Code 进行深度代码分析
- 提取关键信息 (README、依赖、代码结构)
- 生成分析报告
"""

import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

from git import Repo, GitCommandError
from github3.repos import Repository

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class CodeStructure:
    """代码结构信息"""
    root_files: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    docs: List[str] = field(default_factory=list)
    total_lines: int = 0
    total_files: int = 0


@dataclass
class Dependencies:
    """依赖信息"""
    requirements_txt: List[str] = field(default_factory=list)
    package_json: List[Dict] = field(default_factory=list)
    pyproject: List[Dict] = field(default_factory=list)
    cargo_toml: List[Dict] = field(default_factory=list)
    go_mod: List[Dict] = field(default_factory=list)
    docker: bool = False
    docker_compose: bool = False


@dataclass
class ProjectAnalysis:
    """项目分析结果"""
    repo_url: str
    repo_name: str
    clone_path: str
    readme_content: Optional[str] = None
    readme_summary: Optional[str] = None
    description: Optional[str] = None
    code_structure: Optional[CodeStructure] = None
    dependencies: Optional[Dependencies] = None
    key_files: List[str] = field(default_factory=list)
    main_entry: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    analysis_notes: List[str] = field(default_factory=list)
    analysis_time: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class AnalysisConfig:
    """Analysis 模块配置"""
    claude_command: str = "claude --print --permission-mode bypassPermissions"
    max_clone_time: int = 300  # 秒
    include_tests: bool = True
    max_file_size: int = 100 * 1024  # 100KB
    analysis_depth: str = "full"  # quick, full, deep


class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        初始化 ProjectAnalyzer
        
        Args:
            config: 配置对象
        """
        self.config = config or AnalysisConfig()
        self.temporary_dirs: List[str] = []
        
        logger.info("ProjectAnalyzer initialized")
    
    def analyze(self, repo_url: str, repo_name: str) -> ProjectAnalysis:
        """
        分析单个项目
        
        Args:
            repo_url: GitHub 仓库 URL
            repo_name: 仓库名称
            
        Returns:
            分析结果
        """
        analysis = ProjectAnalysis(
            repo_url=repo_url,
            repo_name=repo_name,
            clone_path=""
        )
        
        temp_dir = None
        try:
            # 1. 临时克隆仓库
            logger.info(f"Cloning {repo_name}...")
            temp_dir = self._clone_repo(repo_url)
            analysis.clone_path = temp_dir
            
            # 2. 读取 README
            logger.info("Reading README...")
            readme_content = self._read_readme(temp_dir)
            analysis.readme_content = readme_content
            analysis.readme_summary = self._summarize_readme(temp_dir)
            
            # 3. 分析代码结构
            logger.info("Analyzing code structure...")
            analysis.code_structure = self._analyze_structure(temp_dir)
            
            # 4. 提取依赖信息
            logger.info("Extracting dependencies...")
            analysis.dependencies = self._extract_dependencies(temp_dir)
            
            # 5. 识别关键文件
            logger.info("Identifying key files...")
            analysis.key_files = self._identify_key_files(temp_dir)
            
            # 6. 确定主入口
            logger.info("Finding main entry point...")
            analysis.main_entry = self._find_main_entry(temp_dir)
            
            # 7. 识别技术栈
            logger.info("Identifying tech stack...")
            analysis.tech_stack = self._identify_tech_stack(temp_dir)
            
            # 8. 调用 Claude Code 进行深度分析
            logger.info("Running Claude Code analysis...")
            analysis.analysis_notes = self._run_claude_analysis(temp_dir, repo_url)
            
            analysis.success = True
            logger.info(f"Analysis completed for {repo_name}")
            
        except GitCommandError as e:
            analysis.error = f"Git clone failed: {str(e)}"
            logger.error(f"Git clone error for {repo_name}: {e}")
        except Exception as e:
            analysis.error = f"Analysis failed: {str(e)}"
            logger.error(f"Analysis error for {repo_name}: {e}")
        finally:
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                if temp_dir in self.temporary_dirs:
                    self.temporary_dirs.remove(temp_dir)
        
        return analysis
    
    def _clone_repo(self, repo_url: str) -> str:
        """临时克隆仓库"""
        temp_dir = tempfile.mkdtemp(prefix="repo_clone_")
        self.temporary_dirs.append(temp_dir)
        
        repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True)
        return temp_dir
    
    def _read_readme(self, repo_path: str) -> Optional[str]:
        """读取 README 文件"""
        readme_files = [
            "README.md",
            "README.rst",
            "README.txt",
            "readme.md",
            "readme.rst",
            "readme.txt"
        ]
        
        for readme in readme_files:
            path = Path(repo_path) / readme
            if path.exists():
                try:
                    content = path.read_text(encoding='utf-8')
                    return content[:10000]  # 限制长度
                except Exception as e:
                    logger.warning(f"Error reading {readme}: {e}")
        
        return None
    
    def _summarize_readme(self, repo_path: str) -> Optional[str]:
        """生成 README 摘要"""
        readme = Path(repo_path) / "README.md"
        if not readme.exists():
            return None
        
        try:
            content = readme.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 提取标题和前三段
            summary_lines = []
            paragraph_count = 0
            
            for line in lines:
                if line.startswith('#'):
                    summary_lines.append(line)
                elif line.strip() and paragraph_count < 3:
                    summary_lines.append(line)
                    if line.strip() == '':
                        paragraph_count += 1
            
            return '\n'.join(summary_lines[:50])
            
        except Exception as e:
            logger.warning(f"Error summarizing README: {e}")
            return None
    
    def _analyze_structure(self, repo_path: str) -> CodeStructure:
        """分析代码结构"""
        structure = CodeStructure()
        repo_path = Path(repo_path)
        
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.tox'}
        ignore_extensions = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin'}
        
        for root, dirs, files in os.walk(repo_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(repo_path)
                
                # 跳过大文件
                try:
                    if file_path.stat().st_size > self.config.max_file_size:
                        continue
                except:
                    continue
                
                structure.total_files += 1
                structure.total_lines += len(file_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                
                # 分类文件
                ext = file_path.suffix.lower()
                
                if ext in {'.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h'}:
                    structure.source_files.append(str(rel_path))
                elif ext in {'.txt', '.md', '.rst'} or file.startswith('README'):
                    structure.docs.append(str(rel_path))
                elif file in {'requirements.txt', 'setup.py', 'pyproject.toml', 'package.json'}:
                    structure.config_files.append(str(rel_path))
                elif 'test' in rel_path.parts or file.startswith(('test_', 'test.')):
                    structure.test_files.append(str(rel_path))
                
                # 根目录文件
                if len(rel_path.parts) == 1:
                    structure.root_files.append(str(rel_path))
            
            # 记录目录
            for d in dirs:
                if d not in structure.directories:
                    structure.directories.append(d)
        
        return structure
    
    def _extract_dependencies(self, repo_path: str) -> Dependencies:
        """提取依赖信息"""
        deps = Dependencies()
        repo_path = Path(repo_path)
        
        # requirements.txt
        req_file = repo_path / "requirements.txt"
        if req_file.exists():
            try:
                deps.requirements_txt = [
                    line.strip()
                    for line in req_file.read_text(encoding='utf-8').split('\n')
                    if line.strip() and not line.startswith('#')
                ]
            except:
                pass
        
        # package.json
        pkg_file = repo_path / "package.json"
        if pkg_file.exists():
            try:
                data = json.loads(pkg_file.read_text(encoding='utf-8'))
                deps.package_json = [
                    {"name": k, "version": v}
                    for k, v in data.get('dependencies', {}).items()
                ]
            except:
                pass
        
        # Docker
        if (repo_path / "Dockerfile").exists():
            deps.docker = True
        if (repo_path / "docker-compose.yml").exists() or (repo_path / "docker-compose.yaml").exists():
            deps.docker_compose = True
        
        return deps
    
    def _identify_key_files(self, repo_path: str) -> List[str]:
        """识别关键文件"""
        key_patterns = [
            "main.py", "index.py", "app.py", "server.py",
            "main.js", "index.js", "app.js",
            "__init__.py", "setup.py",
            "cli.py", "entrypoint.sh"
        ]
        
        repo_path = Path(repo_path)
        key_files = []
        
        for pattern in key_patterns:
            file_path = repo_path / pattern
            if file_path.exists():
                key_files.append(str(pattern))
        
        return key_files[:10]  # 最多返回 10 个
    
    def _find_main_entry(self, repo_path: str) -> Optional[str]:
        """寻找主入口文件"""
        entry_points = ["main.py", "index.py", "app.py", "server.py", "cli.py"]
        
        for entry in entry_points:
            if (Path(repo_path) / entry).exists():
                return entry
        
        # 尝试找 package.json 中的 main
        pkg_file = Path(repo_path) / "package.json"
        if pkg_file.exists():
            try:
                data = json.loads(pkg_file.read_text(encoding='utf-8'))
                return data.get('main')
            except:
                pass
        
        return None
    
    def _identify_tech_stack(self, repo_path: str) -> List[str]:
        """识别技术栈"""
        tech_stack = []
        repo_path = Path(repo_path)
        
        # 检查语言
        languages = []
        for ext in ['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp']:
            if any((repo_path / p).exists() for p in repo_path.rglob(f"*{ext}")):
                languages.append(ext[1:])
        
        tech_stack.extend(languages)
        
        # 检查框架
        if (repo_path / "requirements.txt").exists():
            req = repo_path / "requirements.txt"
            content = req.read_text(encoding='utf-8').lower()
            if 'flask' in content:
                tech_stack.append('Flask')
            if 'django' in content:
                tech_stack.append('Django')
            if 'fastapi' in content:
                tech_stack.append('FastAPI')
        
        return list(set(tech_stack))
    
    def _run_claude_analysis(self, repo_path: str, repo_url: str) -> List[str]:
        """调用 Claude Code 进行深度分析"""
        notes = []
        
        # 准备分析提示
        prompt = f"""
分析这个 GitHub 项目，重点关注:
1. 项目的主要功能和用途
2. 代码质量和架构
3. 是否适合作为 OpenClaw Skill
4. 可能的改进方向

项目 URL: {repo_url}
项目路径：{repo_path}

请提供详细的分析报告。
"""
        
        try:
            # 调用 Claude Code (简化版本，实际使用中需要完整实现)
            import subprocess
            result = subprocess.run(
                f"cd {repo_path} && {self.config.claude_command} '{prompt}'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                notes.extend(result.stdout.split('\n'))
            else:
                notes.append(f"Claude Code 执行失败：{result.stderr[:500]}")
                
        except Exception as e:
            notes.append(f"Claude Code 调用错误：{str(e)}")
        
        return notes[:20]  # 限制分析笔记数量
    
    def save_analysis(self, analysis: ProjectAnalysis, output_path: str) -> None:
        """保存分析结果到 JSON"""
        data = analysis.to_dict()
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved analysis to {output_path}")
    
    def close(self):
        """清理临时资源"""
        for temp_dir in self.temporary_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        self.temporary_dirs.clear()
        logger.info("ProjectAnalyzer closed")


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Project Analysis Engine")
    parser.add_argument("--url", required=True, help="GitHub repository URL")
    parser.add_argument("--name", required=True, help="Repository name")
    parser.add_argument("--output", default="analysis_result.json")
    
    args = parser.parse_args()
    
    analyzer = ProjectAnalyzer()
    
    try:
        analysis = analyzer.analyze(args.url, args.name)
        analyzer.save_analysis(analysis, args.output)
        
        if analysis.success:
            print(f"Analysis completed successfully for {args.name}")
        else:
            print(f"Analysis failed: {analysis.error}")
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
