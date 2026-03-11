"""
答案生成器
Answer generators for different question types
"""

import random
import re
from typing import Any, Dict, List, Optional, Tuple


class AnswerGenerator:
    """
    答案生成器 - 根据统计分布生成合理的问卷答案
    
    支持:
    - 单选题：按分布随机选择
    - 多选题：智能组合选项（考虑占比）
    - 量表题：按分布采样 1-5 分
    - 简答题：生成符合主题的答案
    """
    
    # 问卷主题：AI 技术在历史文化实景戏剧中的应用
    THEMES = {
        "ai_technology": [
            "人工智能", "机器学习", "深度学习", "计算机视觉", 
            "自然语言处理", "虚拟现实", "增强现实", "混合现实",
            "动作捕捉", "面部识别", "情感计算", "智能推荐"
        ],
        "drama_theater": [
            "历史文化实景戏剧", "沉浸式戏剧", "实景演出",
            "文化演艺", "历史剧", "传统戏剧", "现代舞剧"
        ],
        "application": [
            "场景应用", "技术实现", "观众体验", "文化传承",
            "艺术创新", "数字化转型", "智能化升级"
        ]
    }
    
    def __init__(self, question_stats: Dict[str, Any]):
        """
        初始化答案生成器
        
        Args:
            question_stats: 问题统计数据
        """
        self.question_stats = question_stats
    
    def generate_answer(self, question_id: str) -> Any:
        """
        生成单个问题的答案
        
        Args:
            question_id: 问题 ID
        
        Returns:
            生成的答案（类型根据问题类型变化）
        """
        stats = self.question_stats.get(str(question_id))
        
        if not stats:
            return self._generate_default_answer(question_id)
        
        q_type = stats.get('type', 'unknown').lower()
        
        if 'single' in q_type or 'radio' in q_type:
            return self.generate_single_choice(question_id)
        elif 'multi' in q_type or 'checkbox' in q_type or 'multiple' in q_type:
            return self.generate_multiple_choice(question_id)
        elif 'scale' in q_type or 'rating' in q_type or 'liker' in q_type:
            return self.generate_scale_question(question_id)
        elif 'short' in q_type or 'text' in q_type or 'answer' in q_type:
            return self.generate_short_answer(question_id)
        else:
            return self._generate_default_answer(question_id)
    
    def generate_single_choice(self, question_id: str) -> str:
        """
        生成单选题答案
        
        Args:
            question_id: 问题 ID
        
        Returns:
            选中的选项文本
        """
        stats = self.question_stats.get(str(question_id))
        
        if not stats:
            return self._get_default_single_option(question_id)
        
        distribution = stats.get('distribution', {})
        
        if not distribution:
            return self._get_default_single_option(question_id)
        
        # 按概率随机选择
        options = list(distribution.keys())
        probabilities = list(distribution.values())
        
        # 归一化概率
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        
        try:
            selected = random.choices(options, weights=probabilities, k=1)[0]
            return str(selected)
        except (ValueError, IndexError):
            return options[0] if options else "选项 1"
    
    def generate_multiple_choice(self, question_id: str) -> List[str]:
        """
        生成多选题答案
        
        智能策略：
        1. 根据每个选项的独立分布概率
        2. 考虑选项之间的相关性（如果某个选项 A 选了，选项 B 更可能也选）
        3. 生成合理的选项组合
        
        Args:
            question_id: 问题 ID
        
        Returns:
            选中的选项列表
        """
        stats = self.question_stats.get(str(question_id))
        
        if not stats:
            return self._get_default_multiple_options(question_id)
        
        distribution = stats.get('distribution', {})
        
        if not distribution:
            return self._get_default_multiple_options(question_id)
        
        options = list(distribution.keys())
        probabilities = list(distribution.values())
        
        # 归一化
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        
        # 策略 1: 独立采样（简单版本）
        selected = []
        for i, option in enumerate(options):
            if random.random() < probabilities[i] * len(options):  # 调整阈值
                selected.append(option)
        
        # 确保至少选一个，最多选所有
        if not selected:
            # 选择概率最高的
            max_idx = probabilities.index(max(probabilities))
            selected.append(options[max_idx])
        
        if len(selected) >= len(options):
            selected = options.copy()
        
        # 策略 2: 基于总选择数量的采样
        if len(selected) < 2 and random.random() < 0.3:
            # 有 30% 概率再选一个
            remaining = [o for o in options if o not in selected]
            if remaining:
                remaining_probs = [probabilities[options.index(o)] for o in remaining]
                try:
                    extra = random.choices(remaining, weights=remaining_probs, k=1)[0]
                    selected.append(extra)
                except (ValueError, IndexError):
                    pass
        
        return selected
    
    def generate_scale_question(self, question_id: str) -> int:
        """
        生成量表题答案（1-5 分）
        
        Args:
            question_id: 问题 ID
        
        Returns:
            评分（1-5 的整数）
        """
        stats = self.question_stats.get(str(question_id))
        
        if not stats:
            return self._get_default_scale(question_id)
        
        distribution = stats.get('distribution', {})
        
        if not distribution:
            return self._get_default_scale(question_id)
        
        # 尝试解析 1-5 分布
        scale_options = ['1', '2', '3', '4', '5']
        options = []
        probabilities = []
        
        for i in range(1, 6):
            key = str(i)
            if key in distribution:
                options.append(i)
                probabilities.append(distribution[key])
        
        if not options:
            # 尝试使用期望值附近的分数
            expected = self._calculate_expected_value(distribution)
            if expected:
                return max(1, min(5, round(expected)))
            return 3  # 默认中位数
        
        # 归一化
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        
        try:
            return random.choices(options, weights=probabilities, k=1)[0]
        except (ValueError, IndexError):
            return 3
    
    def generate_short_answer(self, question_id: str) -> str:
        """
        生成简答题答案
        
        基于主题生成合理的答案：
        - 主题：AI 技术在历史文化实景戏剧中的应用
        
        Args:
            question_id: 问题 ID
        
        Returns:
            生成的答案文本
        """
        # 根据不同的简答题生成不同风格的答案
        templates = [
            self._generate_technology_focused,
            self._generate_experience_focused,
            self._generate_culture_focused,
            self._generate_innovation_focused,
        ]
        
        generator = random.choice(templates)
        return generator(question_id)
    
    def _generate_technology_focused(self, question_id: str) -> str:
        """生成技术导向的答案"""
        templates = [
            "我认为 {ai_tech} 在历史文化实景戏剧中的应用前景非常广阔，特别是在 {drama_type} 方面。",
            "通过 {ai_tech} 技术，可以实现更加逼真的 {drama_type} 表演效果，提升观众体验。",
            "我支持 {ai_tech} 技术在这类戏剧中的应用，它能帮助更好地展现 {theme}。",
            "从技术角度看，{ai_tech} 可以为 {drama_type} 带来很多创新可能。",
        ]
        
        return self._fill_template(random.choice(templates))
    
    def _generate_experience_focused(self, question_id: str) -> str:
        """生成体验导向的答案"""
        templates = [
            "作为观众，我认为 {ai_tech} 技术让 {drama_type} 更加生动有趣，沉浸感更强。",
            "这种技术应用提升了观剧体验，使 {theme} 更加立体可感。",
            "我认为这种技术创新对提升观众的参与度和体验感有很大帮助。",
            "从观众角度，我很期待看到更多 {ai_tech} 与 {drama_type} 结合的作品。",
        ]
        
        return self._fill_template(random.choice(templates))
    
    def _generate_culture_focused(self, question_id: str) -> str:
        """生成文化导向的答案"""
        templates = [
            "这种创新技术有助于 {theme} 的传播和传承，是文化数字化的一种表现。",
            "我认为 {ai_tech} 可以帮助更好地诠释历史文化的内涵，增强 {drama_type} 的文化价值。",
            "技术为文化赋能，{ai_tech} 在 {drama_type} 中的应用是一种很好的尝试。",
            "这是传统文化与现代科技的很好融合，有助于 {theme} 的创新表达。",
        ]
        
        return self._fill_template(random.choice(templates))
    
    def _generate_innovation_focused(self, question_id: str) -> str:
        """生成创新导向的答案"""
        templates = [
            "这代表了演艺行业的数字化转型方向，{ai_tech} 的应用很有前瞻性。",
            "我认为这是一种艺术创新的表现，{ai_tech} 为 {drama_type} 带来了新的可能性。",
            "从创新角度看，{ai_tech} 在 {drama_type} 中的应用是行业发展的必然趋势。",
            "这种跨界融合很有创意，{ai_tech} 可以帮助实现更多艺术上的突破。",
        ]
        
        return self._fill_template(random.choice(templates))
    
    def _fill_template(self, template: str) -> str:
        """填充模板中的占位符"""
        ai_tech = random.choice(self.THEMES['ai_technology'])
        drama_type = random.choice(self.THEMES['drama_theater'])
        theme = random.choice(self.THEMES['application'])
        
        result = template.replace('{ai_tech}', ai_tech)
        result = result.replace('{drama_type}', drama_type)
        result = result.replace('{theme}', theme)
        
        return result
    
    def _calculate_expected_value(self, distribution: Dict[str, float]) -> Optional[float]:
        """计算期望值"""
        if not distribution:
            return None
        
        try:
            return sum(float(k) * v for k, v in distribution.items())
        except (ValueError, TypeError):
            return None
    
    def _get_default_single_option(self, question_id: str) -> str:
        """获取单选题默认选项"""
        stats = self.question_stats.get(str(question_id), {})
        distribution = stats.get('distribution', {})
        
        if distribution:
            # 选择概率最高的
            return max(distribution.items(), key=lambda x: x[1])[0]
        
        return "选项 1"
    
    def _get_default_multiple_options(self, question_id: str) -> List[str]:
        """获取多选题默认选项"""
        stats = self.question_stats.get(str(question_id), {})
        distribution = stats.get('distribution', {})
        
        if distribution:
            # 选择概率最高的前两个
            sorted_options = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
            return [opt for opt, _ in sorted_options[:2]]
        
        return ["选项 1", "选项 2"]
    
    def _get_default_scale(self, question_id: str) -> int:
        """获取量表题默认答案"""
        return 3  # 中位数
    
    def _generate_default_answer(self, question_id: str) -> Any:
        """
        生成默认答案（当统计数据缺失时）
        
        Args:
            question_id: 问题 ID
        
        Returns:
            默认答案
        """
        # 根据问题 ID 判断类型并返回默认值
        q_id = int(question_id) if question_id.isdigit() else 0
        
        if q_id in [25, 26, 27, 28]:  # 简答题
            return "AI 技术在历史文化实景戏剧中的应用前景广阔，建议加强技术创新和观众体验提升。"
        elif q_id in [7, 8, 9, 10, 12, 15, 16, 17, 18, 24]:  # 量表题
            return 3  # 中等评分
        elif q_id in [2, 3, 4, 11, 13]:  # 多选题
            return ["选项 1", "选项 2"]
        else:  # 单选题
            return "选项 1"
