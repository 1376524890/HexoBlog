"""
Reviewer Agent - 御坂妹妹 18 号 (质量审核者)

核心职责:
1. 审核成果质量
2. 检查规范符合性
3. 返回审核结果
4. 提供修改建议

审核标准:
- 闭环性 (40 分): 任务生命周期完整、四角色分工明确
- 规范度 (30 分): 代码/文档/测试规范
- 适配性 (20 分): OpenClaw 兼容、低耦合、易扩展
- 完整性 (10 分): 功能完整、文档完整

通过标准: 总分≥80 分
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from common import ReviewScore, ReviewResult


class Reviewer:
    """御坂妹妹 18 号 - 质量审核者"""
    
    def __init__(self):
        # 审核标准配置
        self.max_scores = {
            "closing": 40,      # 闭环性
            "compliance": 30,   # 规范度
            "compatibility": 20, # 适配性
            "completeness": 10  # 完整性
        }
        self.approval_threshold = 80  # 通过分数线
        
        # 审核历史
        self.review_history: List[ReviewResult] = []
    
    def review(self, submission: Dict) -> ReviewResult:
        """审核提交成果"""
        scores = []
        total = 0
        
        # 逐项检查
        for category, max_score in self.max_scores.items():
            score, issues = self._check_category(category, submission)
            scores.append(ReviewScore(
                category=category,
                score=score,
                max_score=max_score,
                issues=issues
            ))
            total += score
        
        # 做出决策
        decision = "approved" if total >= self.approval_threshold else "rework"
        
        # 生成反馈
        feedback = self._generate_feedback(scores)
        
        # 生成审核结果
        review_result = ReviewResult(
            submission_id=submission.get("id", "unknown"),
            scores=scores,
            total_score=total,
            max_score=sum(self.max_scores.values()),
            decision=decision,
            feedback=feedback
        )
        
        # 记录审核历史
        self.review_history.append(review_result)
        
        return review_result
    
    def _check_category(self, category: str, submission: Dict) -> tuple:
        """检查单个类别"""
        if category == "closing":
            return self._check_closing(submission)
        elif category == "compliance":
            return self._check_compliance(submission)
        elif category == "compatibility":
            return self._check_compatibility(submission)
        elif category == "completeness":
            return self._check_completeness(submission)
        else:
            return 0, ["未知的审核类别"]
    
    def _check_closing(self, submission: Dict) -> tuple:
        """检查闭环性 (40 分)"""
        score = 0
        issues = []
        
        # 任务生命周期 (15 分)
        if "receive" in submission or "task_id" in submission:
            score += 3
        if "decompose" in submission or "subtasks" in submission:
            score += 3
        if "execute" in submission or "execution_result" in submission:
            score += 3
        if "submit" in submission or "result_type" in submission:
            score += 3
        if "review" in submission or "reviewed" in submission:
            score += 3
        
        # 四角色分工 (10 分)
        has_planner = "planner" in str(submission).lower() or "御坂美琴" in str(submission)
        has_executor = "executor" in str(submission).lower() or "御坂妹妹" in str(submission)
        has_reviewer = "reviewer" in str(submission).lower() or "御坂妹妹 18 号" in str(submission)
        has_patrol = "patrol" in str(submission).lower() or "御坂妹妹 19 号" in str(submission)
        
        if has_planner and has_executor and has_reviewer and has_patrol:
            score += 10
        elif has_planner and has_executor:
            score += 5
        
        # 错误处理闭环 (10 分)
        has_error_handling = "error" in str(submission).lower()
        has_logging = "log" in str(submission).lower() or "记录" in str(submission)
        if has_error_handling and has_logging:
            score += 10
        elif has_error_handling or has_logging:
            score += 5
        
        # 上下文隔离 (5 分)
        has_isolation = "isolation" in str(submission).lower() or "独立" in str(submission)
        if has_isolation:
            score += 5
        
        return score, issues
    
    def _check_compliance(self, submission: Dict) -> tuple:
        """检查规范度 (30 分)"""
        score = 0
        issues = []
        
        # 代码规范 (10 分)
        has_type_annotation = "type" in str(submission).lower() or "类型" in str(submission)
        has_docstring = "doc" in str(submission).lower() or "文档" in str(submission)
        if has_type_annotation and has_docstring:
            score += 10
        elif has_type_annotation or has_docstring:
            score += 5
        
        # 文档规范 (8 分)
        has_readme = "readme" in str(submission).lower()
        has_api_doc = "api" in str(submission).lower() or "接口" in str(submission)
        has_example = "example" in str(submission).lower() or "示例" in str(submission)
        if has_readme and has_api_doc and has_example:
            score += 8
        elif has_readme and has_api_doc:
            score += 6
        elif has_readme:
            score += 4
        
        # 测试规范 (6 分)
        has_test = "test" in str(submission).lower()
        has_coverage = "coverage" in str(submission).lower()
        if has_test and has_coverage:
            score += 6
        elif has_test:
            score += 3
        
        # 依赖管理规范 (6 分)
        has_requirements = "requirements" in str(submission).lower() or "依赖" in str(submission)
        has_version_constraint = "version" in str(submission).lower()
        if has_requirements and has_version_constraint:
            score += 6
        elif has_requirements:
            score += 3
        
        return score, issues
    
    def _check_compatibility(self, submission: Dict) -> tuple:
        """检查适配性 (20 分)"""
        score = 0
        issues = []
        
        # OpenClaw 兼容 (8 分)
        has_openclaw_api = "openclaw" in str(submission).lower() or "openclaw" in str(submission)
        has_permission = "permission" in str(submission).lower() or "权限" in str(submission)
        has_tool_call = "tool" in str(submission).lower() or "工具" in str(submission)
        if has_openclaw_api and has_permission and has_tool_call:
            score += 8
        elif has_openclaw_api and has_permission:
            score += 6
        elif has_openclaw_api:
            score += 4
        
        # 模块耦合度 (6 分)
        has_low_coupling = "coupling" in str(submission).lower() or "低耦合" in str(submission)
        has_modular = "modular" in str(submission).lower() or "模块化" in str(submission)
        if has_low_coupling and has_modular:
            score += 6
        elif has_modular:
            score += 3
        
        # 扩展性 (6 分)
        has_interface = "interface" in str(submission).lower() or "接口" in str(submission)
        has_plugin = "plugin" in str(submission).lower() or "插件" in str(submission)
        has_config = "config" in str(submission).lower() or "配置" in str(submission)
        if has_interface and has_plugin and has_config:
            score += 6
        elif has_interface and has_plugin:
            score += 4
        elif has_interface:
            score += 2
        
        return score, issues
    
    def _check_completeness(self, submission: Dict) -> tuple:
        """检查完整性 (10 分)"""
        score = 0
        issues = []
        
        # 功能完整性 (5 分)
        has_core_function = "function" in str(submission).lower() or "功能" in str(submission)
        has_edge_case = "edge" in str(submission).lower() or "边界" in str(submission)
        has_error_handling = "error" in str(submission).lower()
        has_log = "log" in str(submission).lower()
        if has_core_function and has_edge_case and has_error_handling and has_log:
            score += 5
        elif has_core_function and has_error_handling:
            score += 3
        
        # 文档完整性 (5 分)
        has_readme = "readme" in str(submission).lower()
        has_api_doc = "api" in str(submission).lower()
        has_example = "example" in str(submission).lower()
        if has_readme and has_api_doc and has_example:
            score += 5
        elif has_readme and has_api_doc:
            score += 4
        elif has_readme:
            score += 2
        
        return score, issues
    
    def _generate_feedback(self, scores: List[ReviewScore]) -> List[str]:
        """生成修改建议"""
        feedback = []
        
        for score in scores:
            if score.score < score.max_score:
                gap = score.max_score - score.score
                if gap > 20:
                    severity = "严重"
                elif gap > 10:
                    severity = "中等"
                else:
                    severity = "轻微"
                
                feedback.append(
                    f"[{severity}] {score.category}: 得分{score.score}/{score.max_score}"
                )
        
        return feedback
    
    def get_review_stats(self) -> Dict:
        """获取审核统计"""
        if not self.review_history:
            return {
                "total": 0,
                "approved": 0,
                "rework": 0,
                "avg_score": 0
            }
        
        approved = sum(1 for r in self.review_history if r.is_approved())
        avg_score = sum(r.total_score for r in self.review_history) / len(self.review_history)
        
        return {
            "total": len(self.review_history),
            "approved": approved,
            "rework": len(self.review_history) - approved,
            "avg_score": avg_score,
            "approval_rate": approved / len(self.review_history)
        }
    
    def get_review_history(self, limit: int = 10) -> List[ReviewResult]:
        """获取审核历史"""
        return self.review_history[-limit:]
