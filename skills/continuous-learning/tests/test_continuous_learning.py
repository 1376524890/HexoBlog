"""
测试套件 - 持续学习进化系统
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加当前目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent))

from discovery import DiscoveryEngine, DiscoveryConfig, GitHubProject
from analysis import ProjectAnalyzer, AnalysisConfig, ProjectAnalysis
from evaluation import ProjectEvaluator, EvaluationConfig, EvaluationResult


class TestDiscoveryEngine:
    """Discovery 模块测试"""

    def test_init(self):
        """测试初始化"""
        config = DiscoveryConfig(keywords=["test"])
        engine = DiscoveryEngine(config=config)

        assert engine.config.keywords == ["test"]
        assert engine.github is not None

        engine.close()

    def test_discovery_config_defaults(self):
        """测试配置默认值"""
        config = DiscoveryConfig()

        assert config.keywords == ["skill", "agent", "ai"]
        assert config.min_stars == 10
        assert config.min_forks == 2
        assert config.limit == 50

    def test_save_to_json(self):
        """测试 JSON 输出"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_results.json"

            engine = DiscoveryEngine()

            projects = [
                GitHubProject(
                    name="test-repo",
                    full_name="test/test-repo",
                    description="Test repository",
                    html_url="https://github.com/test/test-repo",
                    stars=100,
                    forks=10,
                    language="Python",
                    updated_at="2024-01-01T00:00:00Z",
                    created_at="2024-01-01T00:00:00Z",
                    score=8.5
                )
            ]

            engine.save_to_json(projects, str(output_path))

            assert output_path.exists()

            with open(output_path, 'r') as f:
                data = json.load(f)

            assert "search_time" in data
            assert len(data["projects"]) == 1
            assert data["projects"][0]["name"] == "test-repo"

            engine.close()


class TestProjectAnalyzer:
    """Analysis 模块测试"""

    def test_init(self):
        """测试初始化"""
        config = AnalysisConfig()
        analyzer = ProjectAnalyzer(config=config)

        assert analyzer.config.max_clone_time == 300
        assert analyzer.temporary_dirs == []

        analyzer.close()

    def test_analysis_config_defaults(self):
        """测试配置默认值"""
        config = AnalysisConfig()

        assert config.claude_command == "claude --print --permission-mode bypassPermissions"
        assert config.include_tests is True
        assert config.max_file_size == 102400

    @patch('analysis.Repo')
    def test_clone_repo(self, mock_repo):
        """测试克隆仓库"""
        config = AnalysisConfig()
        analyzer = ProjectAnalyzer(config=config)
        
        mock_repo_instance = Mock()
        mock_repo.clone_from.return_value = mock_repo_instance
        
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_repo_instance.working_tree_dir = tmpdir
            clone_path = analyzer._clone_repo("https://github.com/test/repo.git")
            
            # 验证创建了临时目录
            assert "repo_clone" in clone_path
            assert os.path.exists(clone_path)
        
        analyzer.close()
    
    def test_calculate_score(self):
        """测试评分计算"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            repo_path.mkdir()
            
            # 创建测试文件
            (repo_path / "README.md").write_text("# Test\n\nThis is a test repository.")
            (repo_path / "main.py").write_text("print('hello')")
            (repo_path / "requirements.txt").write_text("requests>=2.0")
            
            analyzer = ProjectAnalyzer()
            structure = analyzer._analyze_structure(tmpdir)
            
            assert structure.total_files > 0
            assert structure.total_lines > 0
            # 验证文件被正确识别
            assert "repo/README.md" in structure.docs or "README.md" in structure.docs

            analyzer.close()


class TestProjectEvaluator:
    """Evaluation 模块测试"""

    def test_init(self):
        """测试初始化"""
        config = EvaluationConfig()
        evaluator = ProjectEvaluator(config=config)

        assert evaluator.config.accept_threshold == 7.5
        assert evaluator.config.review_threshold == 6.0

        # 初始化时六维维度还未创建，通过 evaluate() 方法创建
        analysis = ProjectAnalysis(
            repo_url="https://test.com",
            repo_name="test",
            clone_path="/tmp/test"
        )
        result = evaluator.evaluate(analysis)

        assert result.practicality.weight == 1.5

        evaluator.close()
        assert evaluator.code_quality.weight == 1.5

    def test_evaluation_config_defaults(self):
        """测试配置默认值"""
        config = EvaluationConfig()

        assert config.practicality_weight == 1.5
        assert config.innovation_weight == 1.0
        assert len(config.socratic_templates) == 3

    def test_score_practicality(self):
        """测试实用性评分"""
        evaluator = ProjectEvaluator()

        analysis = ProjectAnalysis(
            repo_url="https://github.com/test/repo",
            repo_name="test-repo",
            clone_path="/tmp/test",
            main_entry="main.py",
            code_structure=None,
            tech_stack=["python"]
        )

        result = evaluator._score_practicality(analysis)

        assert result.name == "实用性"
        assert 0 <= result.score <= 10
        assert isinstance(result.notes, list)

    def test_score_documentation(self):
        """测试文档质量评分"""
        evaluator = ProjectEvaluator()

        analysis = ProjectAnalysis(
            repo_url="https://github.com/test/repo",
            repo_name="test-repo",
            clone_path="/tmp/test",
            readme_content="# Title\n\n## Section\n\nContent here.",
            readme_summary="Test summary",
            code_structure=None
        )

        result = evaluator._score_documentation(analysis)

        assert result.name == "文档质量"
        assert 0 <= result.score <= 10

    def test_make_decision(self):
        """测试决策生成"""
        evaluator = ProjectEvaluator()
        
        # 测试决策阈值 - 直接检查_make_decision 方法
        # 高分评估应该接受
        high_score_eval = EvaluationResult(
            project_name="test",
            repo_url="https://test.com"
        )
        high_score_eval.weighted_score = 8.5
        decision = evaluator._make_decision(high_score_eval)
        assert decision == "accept"
        
        # 低分评估应该拒绝
        low_score_eval = EvaluationResult(
            project_name="test",
            repo_url="https://test.com"
        )
        low_score_eval.weighted_score = 2.5
        decision = evaluator._make_decision(low_score_eval)
        assert decision == "reject"
        
        evaluator.close()

    def test_socratic_questions(self):
        """测试苏格拉底式三问"""
        evaluator = ProjectEvaluator()

        analysis = ProjectAnalysis(
            repo_url="https://github.com/test/repo",
            repo_name="test-repo",
            clone_path="/tmp/test",
            description="Test project description"
        )

        questions = evaluator._run_socratic_questions(analysis)

        assert len(questions) == 3
        assert all(isinstance(q, tuple) and len(q) == 3 for q in questions)


class TestIntegration:
    """Integration 模块测试"""

    def test_skill_spec(self):
        """测试 Skill 规格"""
        from integration import SkillSpec

        spec = SkillSpec(
            name="test-skill",
            description="Test description",
            url="https://github.com/test/repo",
            tags=["python", "ai"],
            features=["feature1", "feature2"]
        )

        assert spec.name == "test-skill"
        assert spec.version == "1.0.0"
        assert len(spec.tags) == 2
        assert len(spec.features) == 2

    def test_generate_front_matter(self):
        """测试生成 YAML front matter"""
        from integration import SkillIntegrator, SkillSpec

        integrator = SkillIntegrator()

        spec = SkillSpec(
            name="test-skill",
            description="Test",
            url="https://test.com",
            tags=["test"],
            version="1.0.0"
        )

        front_matter = integrator._generate_front_matter(spec)

        assert "---" in front_matter
        assert "name: test-skill" in front_matter
        assert "description:" in front_matter
        assert "tags:" in front_matter


class TestContinuousLearningSystem:
    """主程序测试"""

    def test_init(self):
        """测试系统初始化"""
        from continuous_learning import ContinuousLearningSystem, Config

        config = Config()
        system = ContinuousLearningSystem(config=config)

        assert system.config is not None
        assert system.discovery_engine is not None
        assert system.analyzer is not None
        assert system.evaluator is not None
        assert system.integrator is not None

    def test_process_state(self):
        """测试流程状态"""
        from continuous_learning import ProcessState, Step
        from datetime import datetime

        state = ProcessState()
        state.step = Step.DISCOVERY
        state.total_projects = 10
        state.successful = 5

        state_dict = state.to_dict()

        assert state_dict["step"] == "discovery"
        assert state_dict["total_projects"] == 10
        assert state_dict["successful"] == 5

        # 测试时间字段
        state.start_time = datetime.now()
        state.end_time = datetime.now()

        assert "start_time" in state_dict
        assert "end_time" in state_dict

    def test_run_discovery(self):
        """测试 Discovery 步骤"""
        from continuous_learning import ContinuousLearningSystem, Config

        # 只测试初始化，不实际执行 Discovery
        config = Config()
        system = ContinuousLearningSystem(config=config)

        # 验证引擎已正确初始化
        assert system.discovery_engine is not None

        system.discovery_engine.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
