"""
持续学习进化系统 - 主程序
==========================

完整流程编排器，集成 Discovery、Analysis、Evaluation、Integration 四个模块。

功能:
- 命令行接口 (支持分步执行)
- 完整流程 orchestrator
- 进度跟踪和错误处理
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from enum import Enum

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from discovery import DiscoveryEngine, DiscoveryConfig, GitHubProject
from analysis import ProjectAnalyzer, AnalysisConfig, ProjectAnalysis
from evaluation import ProjectEvaluator, EvaluationConfig, EvaluationResult
from integration import SkillIntegrator, IntegrationConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Step(Enum):
    """执行步骤枚举"""
    DISCOVERY = "discovery"
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    INTEGRATION = "integration"
    ALL = "all"


@dataclass
class ProcessState:
    """流程状态"""
    step: Optional[Step] = None
    total_projects: int = 0
    processed: int = 0
    successful: int = 0
    failed: int = 0
    
    discoveries: List[GitHubProject] = field(default_factory=list)
    analyses: List[ProjectAnalysis] = field(default_factory=list)
    evaluations: List[EvaluationResult] = field(default_factory=list)
    integrations: List[Dict] = field(default_factory=list)
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "step": self.step.value if self.step else None,
            "total_projects": self.total_projects,
            "processed": self.processed,
            "successful": self.successful,
            "failed": self.failed,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class Config:
    """全局配置"""
    # GitHub token (可选)
    github_token: Optional[str] = None
    
    # Discovery 配置
    search_keywords: List[str] = field(default_factory=lambda: ["skill", "agent", "ai"])
    min_stars: int = 10
    min_forks: int = 2
    search_limit: int = 50
    
    # Analysis 配置
    max_clone_time: int = 300
    
    # Evaluation 配置
    accept_threshold: float = 7.5
    review_threshold: float = 6.0
    
    # Integration 配置
    skip_tests: bool = False
    auto_push: bool = False
    
    # 输出配置
    output_dir: str = "output"
    
    # 执行配置
    steps: List[Step] = field(default_factory=lambda: [Step.ALL])
    max_projects: int = 10  # 最多处理的项目数


class ContinuousLearningSystem:
    """持续学习系统"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化系统
        
        Args:
            config: 配置对象
        """
        self.config = config or Config()
        self.state = ProcessState()
        
        # 初始化引擎
        self.discovery_engine = self._init_discovery()
        self.analyzer = self._init_analyzer()
        self.evaluator = self._init_evaluator()
        self.integrator = self._init_integrator()
        
        # 创建输出目录
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("ContinuousLearningSystem initialized")
    
    def _init_discovery(self) -> DiscoveryEngine:
        """初始化 Discovery 引擎"""
        config = DiscoveryConfig(
            keywords=self.config.search_keywords,
            min_stars=self.config.min_stars,
            min_forks=self.config.min_forks,
            limit=self.config.search_limit
        )
        return DiscoveryEngine(token=self.config.github_token, config=config)
    
    def _init_analyzer(self) -> ProjectAnalyzer:
        """初始化 Analyzer"""
        config = AnalysisConfig()
        config.max_clone_time = self.config.max_clone_time
        return ProjectAnalyzer(config=config)
    
    def _init_evaluator(self) -> ProjectEvaluator:
        """初始化 Evaluator"""
        config = EvaluationConfig()
        config.accept_threshold = self.config.accept_threshold
        config.review_threshold = self.config.review_threshold
        return ProjectEvaluator(config=config)
    
    def _init_integrator(self) -> SkillIntegrator:
        """初始化 Integrator"""
        config = IntegrationConfig()
        config.skip_tests = self.config.skip_tests
        config.auto_push = self.config.auto_push
        return SkillIntegrator(config=config)
    
    def run(self, steps: Optional[List[Step]] = None) -> ProcessState:
        """
        运行完整流程
        
        Args:
            steps: 要执行的步骤，如果为 None 则使用默认配置
            
        Returns:
            流程状态
        """
        self.state = ProcessState()
        self.state.start_time = datetime.now()
        
        steps = steps or self.config.steps
        
        logger.info(f"Starting Continuous Learning System")
        logger.info(f"Steps: {[s.value for s in steps]}")
        
        try:
            if Step.DISCOVERY in steps or Step.ALL in steps:
                self._run_discovery()
            
            if Step.ANALYSIS in steps or Step.ALL in steps:
                self._run_analysis()
            
            if Step.EVALUATION in steps or Step.ALL in steps:
                self._run_evaluation()
            
            if Step.INTEGRATION in steps or Step.ALL in steps:
                self._run_integration()
            
            self.state.end_time = datetime.now()
            self.state.processed = self.state.successful + self.state.failed
            
        except Exception as e:
            logger.error(f"System error: {e}")
            self.state.failed += 1
            import traceback
            logger.error(traceback.format_exc())
        
        finally:
            # 保存状态
            self._save_state()
            self._cleanup()
        
        return self.state
    
    def _run_discovery(self):
        """执行 Discovery 步骤"""
        logger.info("=" * 60)
        logger.info("STEP 1: DISCOVERY")
        logger.info("=" * 60)
        
        self.state.step = Step.DISCOVERY
        
        # 搜索项目
        projects = self.discovery_engine.search()
        self.state.discoveries = projects
        self.state.total_projects = len(projects)
        
        logger.info(f"Discovered {len(projects)} projects")
        
        # 保存结果
        output_path = Path(self.config.output_dir) / "discovery_results.json"
        self.discovery_engine.save_to_json(projects, str(output_path))
        
        # 显示摘要
        if projects:
            top_projects = sorted(projects, key=lambda p: p.score, reverse=True)[:5]
            logger.info("\nTop 5 discovered projects:")
            for i, project in enumerate(top_projects, 1):
                logger.info(f"  {i}. {project.full_name} ({project.score:.1f}分)")
        
        self.state.successful += len(projects)
    
    def _run_analysis(self):
        """执行 Analysis 步骤"""
        logger.info("=" * 60)
        logger.info("STEP 2: ANALYSIS")
        logger.info("=" * 60)
        
        self.state.step = Step.ANALYSIS
        
        # 限制处理的项目数
        max_projects = min(self.config.max_projects, len(self.state.discoveries))
        
        for i, project in enumerate(self.state.discoveries[:max_projects], 1):
            logger.info(f"\n[{i}/{max_projects}] Analyzing {project.full_name}...")
            
            try:
                analysis = self.analyzer.analyze(
                    repo_url=project.html_url,
                    repo_name=project.full_name
                )
                self.state.analyses.append(analysis)
                
                # 保存分析结果
                output_path = Path(self.config.output_dir) / f"analysis_{i}.json"
                self.analyzer.save_analysis(analysis, str(output_path))
                
                if analysis.success:
                    logger.info(f"  ✓ Analysis completed")
                    self.state.successful += 1
                else:
                    logger.info(f"  ✗ Analysis failed: {analysis.error}")
                    self.state.failed += 1
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                self.state.failed += 1
        
        logger.info(f"\nAnalysis completed: {self.state.successful} successful, {self.state.failed} failed")
    
    def _run_evaluation(self):
        """执行 Evaluation 步骤"""
        logger.info("=" * 60)
        logger.info("STEP 3: EVALUATION")
        logger.info("=" * 60)
        
        self.state.step = Step.EVALUATION
        
        for i, analysis in enumerate(self.state.analyses, 1):
            logger.info(f"\n[{i}/{len(self.state.analyses)}] Evaluating {analysis.repo_name}...")
            
            try:
                evaluation = self.evaluator.evaluate(analysis)
                self.state.evaluations.append(evaluation)
                
                # 保存评估结果
                output_path = Path(self.config.output_dir) / f"evaluation_{i}.json"
                self.evaluator.save_evaluation(evaluation, str(output_path))
                
                # 显示评估摘要
                summary = self.evaluator.generate_summary(evaluation)
                logger.info(f"\n  Score: {evaluation.total_score:.2f}/10")
                logger.info(f"  Decision: {evaluation.decision.upper()}")
                
                if evaluation.decision == "accept":
                    self.state.successful += 1
                else:
                    self.state.failed += 1
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                self.state.failed += 1
        
        logger.info(f"\nEvaluation completed: {self.state.successful} accepted, {self.state.failed} rejected")
    
    def _run_integration(self):
        """执行 Integration 步骤"""
        logger.info("=" * 60)
        logger.info("STEP 4: INTEGRATION")
        logger.info("=" * 60)
        
        self.state.step = Step.INTEGRATION
        
        # 只集成被接受的项目
        accepted = [
            (analysis, eval_result)
            for analysis, eval_result in zip(
                self.state.analyses,
                self.state.evaluations
            )
            if eval_result.decision == "accept"
        ]
        
        if not accepted:
            logger.info("No projects accepted for integration")
            return
        
        logger.info(f"Integrating {len(accepted)} accepted projects...")
        
        for i, (analysis, evaluation) in enumerate(accepted, 1):
            logger.info(f"\n[{i}/{len(accepted)}] Integrating {analysis.repo_name}...")
            
            try:
                skill_spec = self.integrator.integrate(analysis, evaluation)
                
                if skill_spec:
                    logger.info(f"  ✓ Integrated: {skill_spec.name}")
                    self.state.integrations.append({
                        "name": skill_spec.name,
                        "url": skill_spec.url,
                        "score": evaluation.total_score
                    })
                    self.state.successful += 1
                else:
                    logger.info(f"  ✗ Integration failed")
                    self.state.failed += 1
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                self.state.failed += 1
        
        logger.info(f"\nIntegration completed")
    
    def _save_state(self):
        """保存流程状态"""
        state_file = Path(self.config.output_dir) / "process_state.json"
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved process state to {state_file}")
    
    def _cleanup(self):
        """清理资源"""
        self.discovery_engine.close()
        self.analyzer.close()
        logger.info("Cleanup completed")


def main():
    """主函数 - CLI 入口"""
    parser = argparse.ArgumentParser(
        description="Continuous Learning System - Automatically discover, analyze, evaluate, and integrate new skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程
  python continuous_learning.py --all
  
  # 只执行 Discovery
  python continuous_learning.py --step discovery
  
  # 指定关键词搜索
  python continuous_learning.py --keywords "skill" "agent" --max-stars 50
  
  # 跳过测试
  python continuous_learning.py --skip-tests
  
  # 分步执行
  python continuous_learning.py --step discovery --step analysis
        """
    )
    
    # 执行步骤
    parser.add_argument(
        "--step",
        choices=[s.value for s in Step],
        action="append",
        help="执行步骤 (可多次指定)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="执行所有步骤"
    )
    
    # Discovery 参数
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["skill", "agent", "ai"],
        help="搜索关键词"
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=10,
        help="最少星标数"
    )
    parser.add_argument(
        "--min-forks",
        type=int,
        default=2,
        help="最少分叉数"
    )
    parser.add_argument(
        "--search-limit",
        type=int,
        default=50,
        help="搜索限制"
    )
    
    # Analysis 参数
    parser.add_argument(
        "--max-clone-time",
        type=int,
        default=300,
        help="克隆超时时间 (秒)"
    )
    parser.add_argument(
        "--max-projects",
        type=int,
        default=10,
        help="最多处理的项目数"
    )
    
    # Evaluation 参数
    parser.add_argument(
        "--accept-threshold",
        type=float,
        default=7.5,
        help="接受阈值"
    )
    parser.add_argument(
        "--review-threshold",
        type=float,
        default=6.0,
        help="待审查阈值"
    )
    
    # Integration 参数
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="跳过测试"
    )
    parser.add_argument(
        "--auto-push",
        action="store_true",
        help="自动推送到 Git"
    )
    
    # 其他参数
    parser.add_argument(
        "--token",
        help="GitHub API token"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="输出目录"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 确定执行步骤
    steps = []
    if args.all:
        steps = [Step.ALL]
    elif args.step:
        steps = [Step(s) for s in args.step]
    else:
        steps = [Step.ALL]
    
    # 创建配置
    config = Config(
        github_token=args.token,
        search_keywords=args.keywords,
        min_stars=args.min_stars,
        min_forks=args.min_forks,
        search_limit=args.search_limit,
        max_clone_time=args.max_clone_time,
        max_projects=args.max_projects,
        accept_threshold=args.accept_threshold,
        review_threshold=args.review_threshold,
        skip_tests=args.skip_tests,
        auto_push=args.auto_push,
        output_dir=args.output_dir,
        steps=steps
    )
    
    # 运行系统
    system = ContinuousLearningSystem(config=config)
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        state = system.run()
        
        # 输出报告
        print("\n" + "=" * 60)
        print("执行报告")
        print("=" * 60)
        print(f"开始时间：{state.start_time}")
        print(f"结束时间：{state.end_time}")
        print(f"总计项目：{state.total_projects}")
        print(f"成功：{state.successful}")
        print(f"失败：{state.failed}")
        print(f"处理进度：{state.processed}/{state.total_projects}")
        
        if state.integrations:
            print(f"\n已集成的 Skill:")
            for skill in state.integrations:
                print(f"  - {skill['name']} (评分：{skill['score']:.2f})")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n中断执行")
        return 1
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
