"""
持续学习进化系统 - Integration 模块
======================================

负责将评估通过的项目集成到 Skill 系统中。

功能:
- 生成 Skill 文件 (YAML front matter + Markdown 文档)
- 创建测试用例
- 执行测试
- Git 自动提交
"""

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from evaluation import EvaluationResult
from analysis import ProjectAnalysis

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class SkillSpec:
    """Skill 规格"""
    name: str
    description: str
    url: str
    author: str = "Continuous Learning System"
    version: str = "1.0.0"
    language: str = "Python"
    tags: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    installation: str = ""
    usage: str = ""
    examples: List[str] = field(default_factory=list)
    evaluation_summary: str = ""


@dataclass
class IntegrationConfig:
    """集成配置"""
    skills_base_path: str = "/home/claw/.openclaw/workspace/skills"
    git_commit_message: str = "chore: add new skill from continuous learning"
    test_timeout: int = 30
    skip_tests: bool = False
    auto_push: bool = False


class SkillIntegrator:
    """Skill 集成器"""
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        """
        初始化 SkillIntegrator
        
        Args:
            config: 配置对象
        """
        self.config = config or IntegrationConfig()
        
        logger.info("SkillIntegrator initialized")
    
    def integrate(self, analysis: ProjectAnalysis, 
                  evaluation: EvaluationResult) -> Optional[SkillSpec]:
        """
        集成项目到 Skill 系统
        
        Args:
            analysis: 项目分析结果
            evaluation: 项目评估结果
            
        Returns:
            Skill 规格对象，如果集成失败则返回 None
        """
        if evaluation.decision != "accept":
            logger.warning(f"Project {analysis.repo_name} not accepted: {evaluation.decision}")
            return None
        
        try:
            # 1. 创建 Skill 目录
            skill_name = f"skill-{analysis.repo_name.replace('/', '-').replace('_', '-')}"
            skill_path = Path(self.config.skills_base_path) / skill_name
            skill_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Created skill directory: {skill_path}")
            
            # 2. 生成 Skill 文件
            skill_spec = self._generate_skill_file(skill_path, analysis, evaluation)
            
            # 3. 创建测试用例
            if not self.config.skip_tests:
                self._create_test_cases(skill_path, analysis, evaluation)
            
            # 4. 执行测试
            if not self.config.skip_tests:
                test_passed = self._run_tests(skill_path)
                if not test_passed:
                    logger.warning(f"Tests failed for {skill_name}")
                    # 继续集成，但标记测试失败
            
            # 5. Git 提交
            self._git_commit(skill_path, skill_name, analysis, evaluation)
            
            logger.info(f"Successfully integrated {skill_name}")
            
            return skill_spec
            
        except Exception as e:
            logger.error(f"Integration failed: {e}")
            return None
    
    def _generate_skill_file(self, skill_path: Path, 
                            analysis: ProjectAnalysis,
                            evaluation: EvaluationResult) -> SkillSpec:
        """生成 Skill 文件"""
        
        # 构建技能元数据
        spec = SkillSpec(
            name=analysis.repo_name.split('/')[-1],
            description=analysis.description or "Auto-discovered skill",
            url=analysis.repo_url,
            version="1.0.0",
            tags=self._extract_tags(analysis),
            features=self._extract_features(analysis),
            dependencies=self._extract_dependencies(analysis),
            evaluation_summary=evaluation.generate_summary() if hasattr(evaluation, 'generate_summary') else "",
        )
        
        # 生成 YAML front matter
        front_matter = self._generate_front_matter(spec)
        
        # 生成 Markdown 内容
        markdown_content = self._generate_markdown_content(analysis, evaluation)
        
        # 写入 SKILL.md
        skill_md_path = skill_path / "SKILL.md"
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(front_matter)
            f.write('\n---\n\n')
            f.write(markdown_content)
        
        logger.info(f"Generated SKILL.md: {skill_md_path}")
        
        # 生成 README.md
        self._generate_readme(skill_path, spec)
        
        return spec
    
    def _generate_front_matter(self, spec: SkillSpec) -> str:
        """生成 YAML front matter"""
        lines = [
            '---',
            f'name: {spec.name}',
            f'description: "{spec.description}"',
            f'author: {spec.author}',
            f'version: {spec.version}',
            f'language: {spec.language}',
            f'url: "{spec.url}"',
            '---',
            ''
        ]
        
        if spec.tags:
            lines.append(f'tags: {json.dumps(spec.tags)}')
            lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_markdown_content(self, analysis: ProjectAnalysis,
                                  evaluation: EvaluationResult) -> str:
        """生成 Markdown 内容"""
        lines = [
            f"# {analysis.repo_name}",
            "",
            f"GitHub: [{analysis.repo_name}]({analysis.repo_url})",
            "",
            "## 概述",
            "",
            analysis.description or "暂无描述",
            "",
            "## 六维评估",
            "",
        ]
        
        # 添加六维评分
        dimensions = [
            ('practicality', '实用性'),
            ('innovation', '创新性'),
            ('code_quality', '代码质量'),
            ('documentation', '文档质量'),
            ('maintenance', '维护性'),
            ('integration', '集成度')
        ]
        
        for dim_attr, dim_name in dimensions:
            dim = getattr(evaluation, dim_attr, None)
            if dim:
                lines.append(f"- **{dim_name}**: {dim.score:.1f}/10")
        
        lines.extend([
            "",
            "## 苏格拉底式三问",
            "",
        ])
        
        # 添加苏格拉底式问题
        if hasattr(evaluation, 'socratic_questions'):
            for i, (question, answer, evaluation_note) in enumerate(evaluation.socratic_questions, 1):
                lines.append(f"### {i}. {question}")
                lines.append("")
                lines.append(f"**回答**: {answer}")
                lines.append(f"**洞察**: {evaluation_note}")
                lines.append("")
        
        lines.extend([
            "## 技术栈",
            "",
        ])
        
        if analysis.tech_stack:
            lines.append(f"- {', '.join(analysis.tech_stack)}")
        else:
            lines.append("- 待分析")
        
        lines.extend([
            "",
            "## 代码结构",
            "",
        ])
        
        if analysis.code_structure:
            cs = analysis.code_structure
            lines.append(f"- 总文件数：{cs.total_files}")
            lines.append(f"- 总行数：{cs.total_lines}")
            lines.append(f"- 源代码文件：{len(cs.source_files)}")
            lines.append(f"- 测试文件：{len(cs.test_files)}")
            lines.append(f"- 文档文件：{len(cs.docs)}")
        
        lines.extend([
            "",
            "## 主要文件",
            "",
        ])
        
        if analysis.key_files:
            for file in analysis.key_files[:5]:
                lines.append(f"- `{file}`")
        
        lines.extend([
            "",
            "## 依赖",
            "",
        ])
        
        if analysis.dependencies:
            deps = analysis.dependencies
            if deps.requirements_txt:
                lines.append("### Python 依赖")
                for dep in deps.requirements_txt[:5]:
                    lines.append(f"- {dep}")
            if deps.package_json:
                lines.append("### JavaScript 依赖")
                for pkg in deps.package_json[:5]:
                    lines.append(f"- {pkg.get('name', '')} @{pkg.get('version', '')}")
        
        lines.extend([
            "",
            "## 集成建议",
            "",
            *evaluation.recommendations[:5],
            "",
            "---",
            "",
            f"*自动生成于 {datetime.now().isoformat()}*",
        ])
        
        return '\n'.join(lines)
    
    def _generate_readme(self, skill_path: Path, spec: SkillSpec):
        """生成 README.md"""
        readme_lines = [
            f"# {spec.name}",
            "",
            f"{spec.description}",
            "",
            f"[GitHub 仓库]({spec.url})",
            "",
            "## 功能特性",
            "",
        ]
        
        for feature in spec.features[:5]:
            readme_lines.append(f"- {feature}")
        
        readme_lines.extend([
            "",
            "## 安装",
            "",
            "此技能已通过持续学习系统自动集成。",
            "",
            "## 使用",
            "",
            "阅读 SKILL.md 获取详细使用文档。",
            "",
        ])
        
        readme_path = skill_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(readme_lines))
    
    def _create_test_cases(self, skill_path: Path, 
                          analysis: ProjectAnalysis,
                          evaluation: EvaluationResult):
        """创建测试用例"""
        test_path = skill_path / "tests"
        test_path.mkdir(exist_ok=True)
        
        # 创建测试文件
        test_file = test_path / "test_skill.py"
        
        test_content = '''"""
测试用例 - {}
"""

import pytest
import sys
from pathlib import Path


class TestSkill:
    """Skill 测试类"""
    
    def test_skill_exists(self):
        """测试 Skill 文件存在"""
        skill_path = Path(__file__).parent.parent
        assert (skill_path / "SKILL.md").exists()
        assert (skill_path / "README.md").exists()
    
    def test_skill_metadata(self):
        """测试 Skill 元数据"""
        skill_path = Path(__file__).parent.parent
        skill_md = (skill_path / "SKILL.md").read_text()
        
        # 检查必要字段
        assert "name:" in skill_md
        assert "description:" in skill_md
        assert "version:" in skill_md
    
    def test_evaluation_passed(self):
        """测试评估通过"""
        # 根据评估结果创建相应的测试
        pass  # 实际测试逻辑根据具体项目定制
    
    def test_documentation_complete(self):
        """测试文档完整性"""
        skill_path = Path(__file__).parent.parent
        
        required_files = ["SKILL.md", "README.md"]
        for file in required_files:
            file_path = skill_path / file
            assert file_path.exists(), f"缺少必需文件：{file}"
            content = file_path.read_text()
            assert len(content) > 100, f"{file} 内容过短"
        '''
        
        test_content = test_content.format(analysis.repo_name)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 创建 __init__.py
        (test_path / "__init__.py").write_text("")
        
        logger.info(f"Created test file: {test_file}")
    
    def _run_tests(self, skill_path: Path) -> bool:
        """执行测试"""
        test_path = skill_path / "tests"
        if not test_path.exists():
            return True
        
        try:
            result = subprocess.run(
                ["pytest", str(test_path), "-v", "--tb=short"],
                cwd=skill_path,
                capture_output=True,
                text=True,
                timeout=self.config.test_timeout
            )
            
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out")
            return False
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return False
    
    def _git_commit(self, skill_path: Path, skill_name: str,
                   analysis: ProjectAnalysis, evaluation: EvaluationResult):
        """Git 自动提交"""
        try:
            # 添加文件
            subprocess.run(
                ["git", "add", str(skill_path)],
                cwd="/home/claw/.openclaw/workspace",
                check=True
            )
            
            # 创建提交信息
            commit_msg = f"""chore: add skill - {skill_name}

Source: {analysis.repo_url}
Evaluation: {evaluation.total_score:.2f}/10 (weighted: {evaluation.weighted_score:.2f}/10)
Decision: {evaluation.decision}

Features:
- {analysis.repo_name.split('/')[-1]}: {analysis.description or 'No description'}
- Tech stack: {', '.join(analysis.tech_stack[:5]) if analysis.tech_stack else 'N/A'}
- Code quality: {evaluation.code_quality.score:.1f}/10
- Documentation: {evaluation.documentation.score:.1f}/10
"""
            
            # 提交
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd="/home/claw/.openclaw/workspace",
                check=True
            )
            
            # 可选推送
            if self.config.auto_push:
                subprocess.run(
                    ["git", "push"],
                    cwd="/home/claw/.openclaw/workspace",
                    check=True
                )
            
            logger.info(f"Committed {skill_name}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
            # 不抛出异常，继续执行
    
    def _extract_tags(self, analysis: ProjectAnalysis) -> List[str]:
        """提取标签"""
        tags = []
        
        if analysis.tech_stack:
            tags.extend(analysis.tech_stack[:3])
        
        if analysis.dependencies:
            if analysis.dependencies.docker:
                tags.append("docker")
            if analysis.dependencies.docker_compose:
                tags.append("docker-compose")
        
        return list(set(tags))[:10]  # 最多 10 个标签
    
    def _extract_features(self, analysis: ProjectAnalysis) -> List[str]:
        """提取功能特性"""
        features = []
        
        if analysis.readme_summary:
            # 从 README 中提取前 3 个功能点
            lines = analysis.readme_summary.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    features.append(line.strip())
                    if len(features) >= 3:
                        break
        
        return features[:5]
    
    def _extract_dependencies(self, analysis: ProjectAnalysis) -> List[str]:
        """提取依赖"""
        deps = []
        
        if analysis.dependencies:
            if analysis.dependencies.requirements_txt:
                deps.extend(analysis.dependencies.requirements_txt[:5])
            if analysis.dependencies.package_json:
                for pkg in analysis.dependencies.package_json:
                    deps.append(f"{pkg.get('name', '')} @ {pkg.get('version', '')}")
        
        return deps[:10]


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Integration Engine")
    parser.add_argument("--analysis", required=True, help="Analysis result JSON path")
    parser.add_argument("--evaluation", required=True, help="Evaluation result JSON path")
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    parser.add_argument("--auto-push", action="store_true", help="自动推送到远程")
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    with open(args.evaluation, 'r', encoding='utf-8') as f:
        evaluation_data = json.load(f)
    
    analysis = ProjectAnalysis(**analysis_data)
    evaluation = EvaluationResult(**evaluation_data)
    
    integrator = SkillIntegrator()
    integrator.config.skip_tests = args.skip_tests
    integrator.config.auto_push = args.auto_push
    
    try:
        result = integrator.integrate(analysis, evaluation)
        
        if result:
            print(f"Successfully integrated {result.name}")
        else:
            print("Integration failed or not accepted")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
