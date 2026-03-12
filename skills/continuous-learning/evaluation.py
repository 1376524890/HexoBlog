"""
持续学习进化系统 - Evaluation 模块
======================================

负责评估项目是否适合作为 Skill 集成。

功能:
- 实现六维评估矩阵 (实用性、创新性、代码质量等)
- 苏格拉底式三问检查
- 计算综合评分和决策阈值
- 生成评估报告
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from analysis import ProjectAnalysis, Dependencies, CodeStructure

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class DimensionScore:
    """单个维度评分"""
    name: str
    score: float  # 0-10
    max_score: float = 10.0
    weight: float = 1.0
    notes: List[str] = field(default_factory=list)
    
    def weighted_score(self) -> float:
        """返回加权分数"""
        return (self.score / self.max_score) * self.weight


@dataclass
class EvaluationResult:
    """评估结果"""
    project_name: str
    repo_url: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 六维评分
    practicality: DimensionScore = field(default_factory=lambda: DimensionScore(name="实用性", score=5.0))
    innovation: DimensionScore = field(default_factory=lambda: DimensionScore(name="创新性", score=5.0))
    code_quality: DimensionScore = field(default_factory=lambda: DimensionScore(name="代码质量", score=5.0))
    documentation: DimensionScore = field(default_factory=lambda: DimensionScore(name="文档质量", score=5.0))
    maintenance: DimensionScore = field(default_factory=lambda: DimensionScore(name="维护性", score=5.0))
    integration: DimensionScore = field(default_factory=lambda: DimensionScore(name="集成度", score=5.0))
    
    # 苏格拉底式三问
    socratic_questions: List[Tuple[str, str, str]] = field(default_factory=list)
    
    # 综合评分
    total_score: float = 0.0
    weighted_score: float = 0.0
    decision: str = "pending"  # accept, reject, review
    decision_threshold: float = 7.0
    
    # 详细报告
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class EvaluationConfig:
    """评估配置"""
    # 维度权重
    practicality_weight: float = 1.5
    innovation_weight: float = 1.0
    code_quality_weight: float = 1.5
    documentation_weight: float = 1.0
    maintenance_weight: float = 1.2
    integration_weight: float = 1.3
    
    # 决策阈值
    accept_threshold: float = 7.5
    review_threshold: float = 6.0
    
    # 苏格拉底式三问模板
    socratic_templates: List[str] = field(default_factory=lambda: [
        "这个项目解决的核心问题是什么？为什么重要？",
        "这个项目与其他类似方案相比，独特价值在哪里？",
        "这个项目如果集成到 Skill 系统，会带来什么价值？"
    ])


class ProjectEvaluator:
    """项目评估器"""
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        """
        初始化 ProjectEvaluator
        
        Args:
            config: 配置对象
        """
        self.config = config or EvaluationConfig()
        self._setup_weights()
        
        logger.info("ProjectEvaluator initialized")
    
    def _setup_weights(self):
        """设置维度权重"""
        weights = {
            'practicality': self.config.practicality_weight,
            'innovation': self.config.innovation_weight,
            'code_quality': self.config.code_quality_weight,
            'documentation': self.config.documentation_weight,
            'maintenance': self.config.maintenance_weight,
            'integration': self.config.integration_weight,
        }
        
        for dim_name in ['practicality', 'innovation', 'code_quality', 
                         'documentation', 'maintenance', 'integration']:
            dim = getattr(self, dim_name, None)
            if dim and hasattr(dim, 'weight'):
                dim.weight = weights[dim_name]
    
    def evaluate(self, analysis: ProjectAnalysis) -> EvaluationResult:
        """
        评估单个项目
        
        Args:
            analysis: 项目分析结果
            
        Returns:
            评估结果
        """
        result = EvaluationResult(
            project_name=analysis.repo_name,
            repo_url=analysis.repo_url
        )
        
        try:
            # 1. 六维评分
            logger.info("Scoring dimensions...")
            result.practicality = self._score_practicality(analysis)
            result.innovation = self._score_innovation(analysis)
            result.code_quality = self._score_code_quality(analysis)
            result.documentation = self._score_documentation(analysis)
            result.maintenance = self._score_maintenance(analysis)
            result.integration = self._score_integration(analysis)
            
            # 2. 计算综合评分
            logger.info("Calculating overall score...")
            self._calculate_total_score(result)
            
            # 3. 苏格拉底式三问
            logger.info("Running Socratic questions...")
            result.socratic_questions = self._run_socratic_questions(analysis)
            
            # 4. 生成决策
            logger.info("Making decision...")
            result.decision = self._make_decision(result)
            
            # 5. 生成详细报告
            logger.info("Generating report...")
            self._generate_report(result, analysis)
            
            logger.info(f"Evaluation completed for {analysis.repo_name}: {result.decision}")
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            result.decision = "error"
            result.weaknesses.append(f"评估错误：{str(e)}")
        
        return result
    
    def _score_practicality(self, analysis: ProjectAnalysis) -> DimensionScore:
        """评分：实用性"""
        score = 5.0
        notes = []
        
        # 检查功能完整性
        if analysis.main_entry:
            score += 1.0
            notes.append(f"有明确的主入口：{analysis.main_entry}")
        else:
            notes.append("未找到明确的主入口")
        
        # 检查依赖完整性
        if analysis.dependencies:
            deps = analysis.dependencies
            if deps.requirements_txt or deps.package_json:
                score += 0.5
                notes.append("有依赖管理文件")
        
        # 检查是否有测试
        if analysis.code_structure:
            if analysis.code_structure.test_files:
                score += 1.0
                notes.append("包含测试文件")
            else:
                notes.append("缺少测试文件")
        
        # 检查技术栈流行度
        popular_techs = ['python', 'javascript', 'typescript', 'rust']
        if analysis.tech_stack:
            if any(tech in popular_techs for tech in analysis.tech_stack):
                score += 0.5
                notes.append("使用流行技术栈")
        
        return DimensionScore(
            name="实用性",
            score=min(score, 10.0),
            notes=notes
        )
    
    def _score_innovation(self, analysis: ProjectAnalysis) -> DimensionScore:
        """评分：创新性"""
        score = 5.0
        notes = []
        
        # 检查 README 是否有创新点描述
        if analysis.readme_summary:
            innovation_keywords = ['创新', 'novel', 'unique', 'new', 'first', '首创']
            readme_lower = analysis.readme_summary.lower()
            
            if any(kw in readme_lower for kw in innovation_keywords):
                score += 1.5
                notes.append("README 中提到创新点")
            else:
                notes.append("README 中未明确提及创新点")
        
        # 检查是否有独特的架构模式
        if analysis.analysis_notes:
            architecture_keywords = ['architecture', 'pattern', 'design', 'framework']
            notes_content = '\n'.join(analysis.analysis_notes).lower()
            
            if any(kw in notes_content for kw in architecture_keywords):
                score += 1.0
                notes.append("采用独特的架构模式")
        
        # 检查话题标签
        if hasattr(analysis, 'topics') and analysis.topics:
            unique_topics = [t for t in analysis.topics if len(t) > 4]
            if len(unique_topics) >= 2:
                score += 0.5
                notes.append(f"独特的话题标签：{unique_topics[:3]}")
        
        return DimensionScore(
            name="创新性",
            score=min(score, 10.0),
            notes=notes
        )
    
    def _score_code_quality(self, analysis: ProjectAnalysis) -> DimensionScore:
        """评分：代码质量"""
        score = 5.0
        notes = []
        
        # 检查代码结构
        if analysis.code_structure:
            structure = analysis.code_structure
            
            # 文件组织合理性
            if structure.source_files and len(structure.source_files) < 50:
                score += 1.0
                notes.append("代码文件组织良好")
            else:
                notes.append("代码文件数量异常")
            
            # 测试覆盖率估计
            if structure.test_files:
                test_ratio = len(structure.test_files) / max(len(structure.source_files), 1)
                if test_ratio > 0.3:
                    score += 1.5
                    notes.append(f"测试覆盖率高 ({test_ratio:.1%})")
                elif test_ratio > 0.1:
                    score += 0.8
                    notes.append(f"测试覆盖率中等 ({test_ratio:.1%})")
                else:
                    notes.append(f"测试覆盖率低 ({test_ratio:.1%})")
        
        # 检查是否有依赖管理
        if analysis.dependencies:
            deps = analysis.dependencies
            if deps.requirements_txt:
                score += 0.5
                notes.append("有 Python 依赖管理")
            if deps.package_json:
                score += 0.5
                notes.append("有 JavaScript 依赖管理")
        
        # 检查技术栈清晰度
        if analysis.tech_stack:
            score += 0.5
            notes.append(f"技术栈明确：{analysis.tech_stack[:5]}")
        else:
            notes.append("技术栈不明确")
        
        return DimensionScore(
            name="代码质量",
            score=min(score, 10.0),
            notes=notes
        )
    
    def _score_documentation(self, analysis: ProjectAnalysis) -> DimensionScore:
        """评分：文档质量"""
        score = 5.0
        notes = []
        
        # 检查 README
        if analysis.readme_content:
            readme_lines = analysis.readme_content.split('\n')
            
            # README 长度检查
            if len(readme_lines) > 20:
                score += 1.5
                notes.append("README 内容完整")
            elif len(readme_lines) > 10:
                score += 1.0
                notes.append("README 内容中等")
            else:
                notes.append("README 内容过短")
            
            # 检查是否有示例代码
            if '```' in analysis.readme_content:
                score += 1.0
                notes.append("包含示例代码")
            
            # 检查是否有安装说明
            install_keywords = ['install', 'setup', 'pip', 'npm', '安装']
            if any(kw in analysis.readme_content.lower() for kw in install_keywords):
                score += 0.5
                notes.append("包含安装说明")
        
        # 检查其他文档
        if analysis.code_structure:
            docs_count = len(analysis.code_structure.docs)
            if docs_count > 0:
                score += 0.5
                notes.append(f"额外文档：{docs_count}个")
        
        return DimensionScore(
            name="文档质量",
            score=min(score, 10.0),
            notes=notes
        )
    
    def _score_maintenance(self, analysis: ProjectAnalysis) -> DimensionScore:
        """评分：维护性"""
        score = 5.0
        notes = []
        
        # 检查更新频率 (从 analysis 的时间戳判断)
        if analysis.analysis_time:
            try:
                from datetime import datetime
                update_time = datetime.fromisoformat(analysis.analysis_time.replace('Z', '+00:00'))
                days_old = (datetime.now(update_time.tzinfo) - update_time).days
                
                if days_old < 30:
                    score += 1.5
                    notes.append("项目活跃度高")
                elif days_old < 90:
                    score += 1.0
                    notes.append("项目维护正常")
                else:
                    score += 0.5
                    notes.append("项目可能已不活跃")
            except:
                notes.append("无法判断项目活跃度")
        
        # 检查是否有 CI/CD 配置
        ci_files = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile']
        has_ci = False
        for ci_file in ci_files:
            # 这里简化处理，实际需要检查文件是否存在
            pass
        
        if has_ci:
            score += 1.0
            notes.append("有 CI/CD 配置")
        
        # 检查 Issue/PR 活跃度 (从分析笔记中判断)
        if analysis.analysis_notes:
            notes_content = '\n'.join(analysis.analysis_notes).lower()
            if 'issue' in notes_content or 'pr' in notes_content:
                score += 0.5
                notes.append("有社区互动")
        
        return DimensionScore(
            name="维护性",
            score=min(score, 10.0),
            notes=notes
        )
    
    def _score_integration(self, analysis: ProjectAnalysis) -> DimensionScore:
        """评分：集成度"""
        score = 5.0
        notes = []
        
        # 检查是否与 OpenClaw 兼容
        compatibility_keywords = ['openclaw', 'agent', 'skill', 'api', 'plugin']
        readme_lower = (analysis.readme_content or '').lower()
        analysis_notes = '\n'.join(analysis.analysis_notes or []).lower()
        combined = readme_lower + ' ' + analysis_notes
        
        if any(kw in combined for kw in compatibility_keywords):
            score += 2.0
            notes.append("与 OpenClaw 兼容")
        
        # 检查是否有清晰的 API
        api_keywords = ['api', 'interface', 'function', 'method', 'class']
        if any(kw in combined for kw in api_keywords):
            score += 1.5
            notes.append("有清晰的 API 设计")
        
        # 检查是否易于集成
        integration_indicators = ['import', 'require', 'install', 'pip', 'npm']
        if any(kw in combined for kw in integration_indicators):
            score += 1.0
            notes.append("易于集成")
        
        return DimensionScore(
            name="集成度",
            score=min(score, 10.0),
            notes=notes
        )
    
    def _calculate_total_score(self, result: EvaluationResult):
        """计算综合评分"""
        # 计算加权总分
        dimensions = [
            result.practicality,
            result.innovation,
            result.code_quality,
            result.documentation,
            result.maintenance,
            result.integration
        ]
        
        total_weighted = 0.0
        total_weight = 0.0
        
        for dim in dimensions:
            total_weighted += dim.weighted_score()
            total_weight += dim.weight
        
        # 归一化
        result.weighted_score = (total_weighted / total_weight * 10) if total_weight > 0 else 0
        result.total_score = sum(d.score for d in dimensions) / len(dimensions)
    
    def _run_socratic_questions(self, analysis: ProjectAnalysis) -> List[Tuple[str, str, str]]:
        """运行苏格拉底式三问"""
        questions = []
        
        for template in self.config.socratic_templates:
            # 替换占位符
            question = template.replace("{project}", analysis.repo_name)
            
            # 基于分析结果生成回答
            answer = self._generate_socratic_answer(question, analysis)
            
            # 记录问题
            evaluation = self._evaluate_socratic_insight(question, answer)
            
            questions.append((question, answer, evaluation))
        
        return questions
    
    def _generate_socratic_answer(self, question: str, analysis: ProjectAnalysis) -> str:
        """基于分析生成苏格拉底式回答"""
        # 简化实现
        if "核心问题" in question:
            return f"根据分析，{analysis.repo_name} 的核心功能是：{analysis.description or '待进一步分析'}"
        elif "独特价值" in question:
            return f"{analysis.repo_name} 的独特之处在于：{analysis.readme_summary or '需要深入分析'}"
        else:
            return f"集成到 Skill 系统的价值：{analysis.tech_stack or '待确定'}"
    
    def _evaluate_socratic_insight(self, question: str, answer: str) -> str:
        """评估苏格拉底式洞察"""
        # 简化实现
        if len(answer) > 50:
            return "深刻"
        else:
            return "需要进一步思考"
    
    def _make_decision(self, result: EvaluationResult) -> str:
        """生成决策"""
        if result.weighted_score >= self.config.accept_threshold:
            return "accept"
        elif result.weighted_score >= self.config.review_threshold:
            return "review"
        else:
            return "reject"
    
    def _generate_report(self, result: EvaluationResult, analysis: ProjectAnalysis):
        """生成详细报告"""
        # 收集优势
        for dim in [result.practicality, result.code_quality, result.documentation]:
            for note in dim.notes:
                if any(kw in note.lower() for kw in ['有', '包含', '良好', '明确']):
                    result.strengths.append(note)
        
        # 收集劣势
        for dim in [result.maintenance, result.integration]:
            for note in dim.notes:
                if any(kw in note.lower() for kw in ['缺少', '低', '过短', '异常']):
                    result.weaknesses.append(note)
        
        # 生成建议
        if result.decision == "review":
            result.recommendations.append("建议人工审核后再决定")
        
        if result.documentation.score < 7:
            result.recommendations.append("需要完善文档")
        
        if result.maintenance.score < 6:
            result.recommendations.append("项目活跃度存疑，需进一步调查")
    
    def save_evaluation(self, result: EvaluationResult, output_path: str) -> None:
        """保存评估结果"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved evaluation to {output_path}")
    
    def generate_summary(self, result: EvaluationResult) -> str:
        """生成评估摘要"""
        lines = [
            f"评估报告：{result.project_name}",
            f"URL: {result.repo_url}",
            f"综合评分：{result.total_score:.2f} / 10.0",
            f"加权评分：{result.weighted_score:.2f} / 10.0",
            f"决策：{result.decision.upper()}",
            "",
            "六维评分:",
        ]
        
        dimensions = [
            result.practicality,
            result.innovation,
            result.code_quality,
            result.documentation,
            result.maintenance,
            result.integration
        ]
        
        for dim in dimensions:
            lines.append(f"  - {dim.name}: {dim.score:.1f}/10 (权重：{dim.weight})")
        
        lines.extend(["", "优势:", *result.strengths[:3]])
        lines.extend(["", "劣势:", *result.weaknesses[:3]])
        
        if result.recommendations:
            lines.extend(["", "建议:", *result.recommendations])
        
        return '\n'.join(lines)


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Project Evaluation Engine")
    parser.add_argument("--analysis", required=True, help="Analysis result JSON path")
    parser.add_argument("--output", default="evaluation_result.json")
    
    args = parser.parse_args()
    
    # 加载分析结果
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # 重建 ProjectAnalysis 对象
    analysis = ProjectAnalysis(**analysis_data)
    
    evaluator = ProjectEvaluator()
    
    try:
        result = evaluator.evaluate(analysis)
        evaluator.save_evaluation(result, args.output)
        
        print(evaluator.generate_summary(result))
        
    finally:
        pass


if __name__ == "__main__":
    main()
