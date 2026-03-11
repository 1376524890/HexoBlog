#!/usr/bin/env python3
"""
问卷数据生成器 - 根据给定的比例和效度要求生成750份问卷答案
"""

import json
import random
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
import uuid

# 设置随机种子以保证可复现性
random.seed(42)
np.random.seed(42)

# ============== 人口统计学分布 ==============
GENDER_DIST = [
    ("男", 368, 0.491),
    ("女", 378, 0.504),
    ("不愿透露", 4, 0.005),
]

AGE_DIST = [
    ("18岁以下", 45, 0.06),
    ("18-25岁", 228, 0.304),
    ("26-35岁", 195, 0.26),
    ("36-45岁", 135, 0.18),
    ("46-55岁", 93, 0.124),
    ("56岁以上", 54, 0.072),
]

EDUCATION_DIST = [
    ("高中及以下", 78, 0.104),
    ("大专", 126, 0.168),
    ("本科", 378, 0.504),
    ("硕士及以上", 168, 0.224),
]

OCCUPATION_DIST = [
    ("学生", 165, 0.22),
    ("企业职员", 198, 0.264),
    ("事业单位/公务员", 120, 0.16),
    ("自由职业者", 87, 0.116),
    ("个体经营者", 72, 0.096),
    ("退休人员", 60, 0.08),
    ("其他", 48, 0.064),
]

HISTORY_INTEREST_DIST = [
    ("1", 15, 0.02),
    ("2", 45, 0.06),
    ("3", 198, 0.264),
    ("4", 312, 0.416),
    ("5", 180, 0.24),
]

# ============== 题目分布数据 ==============

# 第1题：是否体验过
Q1_DIST = [
    ("体验过", 603, 0.804),
    ("未体验过，但有文旅景区游览/实景演出观演的消费习惯", 112, 0.149),
    ("未体验过，也无相关文旅消费习惯", 35, 0.047),
]

# 第2题：AI体验项目（多选，仅603人回答）
Q2_OPTIONS = [
    ("VR/AR沉浸式体验（如球幕飞越、实景AR互动）", 0.627),
    ("智能NPC互动/AI数字人对话", 0.488),
    ("智能导览/AI语音讲解", 0.701),
    ("个性化行程推荐/智能规划系统", 0.408),
    ("光影互动装置/全息投影演出", 0.582),
    ("智能排队/人流预警系统", 0.313),
]

# 第3题：出游目的（多选，仅603人回答）
Q3_OPTIONS = [
    ("了解历史文化、开展文化学习", 0.537),
    ("休闲娱乐、放松身心", 0.766),
    ("网红打卡、社交平台分享", 0.473),
    ("亲子研学、家庭出游", 0.313),
    ("戏剧/艺术爱好者，专门前往观演", 0.209),
    ("其他", 0.075),
]

# 第4题：了解渠道（多选，仅603人回答）
Q4_OPTIONS = [
    ("抖音/小红书/快手等短视频平台", 0.726),
    ("微信/微博等社交平台", 0.507),
    ("亲友/同事推荐", 0.378),
    ("旅行社/携程/美团等OTA平台", 0.313),
    ("新闻报道/纪录片", 0.209),
    ("景区线下宣传", 0.144),
    ("其他", 0.06),
]

# 第5题：是否首次到访
Q5_DIST = [
    ("是，首次到访", 381, 0.632),
    ("否，此前已到访2次", 132, 0.219),
    ("否，此前已到访3次及以上", 90, 0.149),
]

# 第6题：停留时长
Q6_DIST = [
    ("半天以内", 87, 0.144),
    ("1天", 243, 0.403),
    ("2天", 189, 0.313),
    ("3天及以上", 84, 0.139),
]

# 第11题：未接触AI原因（多选，仅87人回答）
Q11_OPTIONS = [
    ("不知道景区有相关AI体验项目", 0.621),
    ("担心设备操作复杂，不会使用", 0.437),
    ("对AI技术不感兴趣，更偏好传统观演模式", 0.368),
    ("相关项目需要额外付费，性价比不高", 0.322),
    ("听说相关项目体验感差、故障多", 0.207),
    ("排队时间过长，放弃体验", 0.276),
    ("其他", 0.092),
]

# 第13题：游览目的（多选，仅112人回答）
Q13_OPTIONS = [
    ("了解历史文化、开展文化学习", 0.50),
    ("休闲娱乐、放松身心", 0.795),
    ("网红打卡、社交平台分享", 0.429),
    ("亲子研学、家庭出游", 0.304),
    ("戏剧/艺术爱好者，专门观演", 0.205),
    ("其他", 0.071),
]

# 第14题：游览频次
Q14_DIST = [
    ("平均每月1次及以上", 18, 0.161),
    ("平均每2-3个月1次", 34, 0.304),
    ("平均每半年1次", 38, 0.339),
    ("平均每年1次", 16, 0.143),
    ("1年以上1次", 6, 0.054),
]

# ============== 量表题数据 ==============

# 第7题：AI技术感知
Q7_ITEMS = [
    ("景区里的AI智能导览/推荐系统，帮我更高效地规划了游览路线", 3.89, 0.98, [3.5, 5.8, 18.6, 42.5, 29.6]),
    ("AI互动装置/数字人，让我对景区的历史文化有了更深入的理解", 3.80, 1.02, [4.2, 7.1, 20.3, 41.4, 27.0]),
    ("这些AI/智能设备操作起来简单易懂，很容易上手", 3.86, 0.95, [3.8, 6.5, 16.8, 45.3, 27.6]),
    ("我认为在这类历史文化景区里，引入AI技术是很有必要的", 4.02, 0.92, [2.5, 4.3, 15.6, 43.8, 33.8]),
    ("我觉得AI技术和景区的历史文化内容融合得很自然，没有违和感", 3.71, 1.05, [4.8, 8.3, 22.5, 39.8, 24.6]),
    ("相比传统的人工讲解/静态展示，我更喜欢AI技术带来的互动体验", 3.64, 1.08, [5.1, 9.4, 24.3, 38.5, 22.7]),
]

# 第8题：沉浸体验测量（含注意力检测）
Q8_ITEMS = [
    ("体验过程中，我感觉自己身临其境，仿佛真的置身于历史场景之中", 4.01, 0.91, [2.3, 4.8, 15.4, 44.6, 32.9]),
    ("演出的声光电、实景建筑，充分调动了我的视觉、听觉等感官", 4.11, 0.86, [1.8, 3.5, 12.6, 46.8, 35.3]),
    ("观演过程中，我和剧中人物、剧情产生了强烈的情感共鸣", 3.93, 0.98, [2.8, 5.6, 18.4, 42.3, 30.9]),
    ("演出内容让我对这段历史文化，产生了强烈的情感认同", 4.00, 0.93, [2.5, 4.3, 16.8, 43.5, 32.9]),
    ("体验过程中，我很容易忘记现实时间和周围的环境", 3.84, 1.01, [3.2, 6.5, 21.4, 40.8, 28.1]),
    ("我有个'穿越'到历史年代的感觉，暂时忘记了自己的现代身份", 3.79, 1.03, [3.8, 7.1, 22.6, 39.4, 27.1]),
    ("我会主动参与剧情互动、探索场景里的历史细节，而非被动观看", 3.94, 0.95, [2.9, 5.4, 17.6, 44.2, 29.9]),
    ("我的互动和选择，能真实影响剧情的走向和体验内容", 3.70, 1.06, [4.3, 8.2, 24.6, 38.7, 24.2]),
    ("*注意力检测 本题请您选择'非常符合'", 4.96, 0.23, [0.2, 0.3, 0.5, 1.2, 97.8]),  # 特殊处理
]

# 第9题：文化价值感知
Q9_ITEMS = [
    ("我认为该景区对对应的历史文化（如宋文化、黄河文化）还原度很高", 3.94, 0.96, [2.8, 5.3, 17.8, 43.5, 30.6]),
    ("这次体验，让我学到了新的历史文化知识", 4.00, 0.92, [2.3, 4.6, 16.2, 44.8, 32.1]),
    ("这次体验后，我对该地域的历史文化有了更深的认同感", 4.00, 0.93, [2.5, 4.8, 15.6, 44.2, 32.9]),
    ("我愿意把这个景区，作为了解这段历史文化的窗口推荐给他人", 4.06, 0.89, [2.1, 3.8, 14.3, 45.6, 34.2]),
]

# 第10题：满意度与行为意向
Q10_ITEMS = [
    ("我对该景区的整体游览体验感到满意", 4.11, 0.86, [1.8, 3.5, 12.6, 46.8, 35.3]),
    ("我对景区里AI技术的实际应用效果感到满意", 3.93, 0.95, [2.5, 5.3, 18.4, 44.2, 29.6]),
    ("未来我愿意再次到访该景区体验", 4.00, 0.91, [2.3, 4.6, 15.6, 45.3, 32.2]),
    ("我愿意向亲友、同事推荐这个景区", 4.06, 0.88, [2.1, 3.8, 14.3, 46.2, 33.6]),
    ("我愿意在抖音、小红书等社交平台，分享我的游览体验", 3.85, 0.99, [3.2, 6.5, 20.4, 42.3, 27.6]),
]

# 第12题：AI技术应用感受
Q12_ITEMS = [
    ("我认为AI技术能为历史文化实景戏剧的体验带来提升", 3.76, 1.02, [3.4, 6.9, 24.1, 41.4, 24.1]),
    ("未来再次到访时，我愿意尝试景区内的AI相关体验项目", 3.94, 0.95, [2.3, 5.7, 17.2, 44.8, 29.9]),
    ("我认为该景区对对应的历史文化还原度很高", 3.98, 0.91, [2.3, 4.6, 16.1, 47.1, 29.9]),
    ("这次体验，让我学到了新的历史文化知识", 4.01, 0.90, [2.3, 4.6, 14.9, 46.0, 32.2]),
    ("我对该景区的整体游览体验感到满意", 4.11, 0.85, [1.1, 3.4, 13.8, 47.1, 34.5]),
    ("我愿意向亲友、同事推荐这个景区", 4.12, 0.84, [1.1, 3.4, 12.6, 48.3, 34.5]),
]

# 第15题：AI认知与接受度
Q15_ITEMS = [
    ("我了解AI技术在文旅景区、实景演出中的各类应用形式", 3.27, 1.12, [8.0, 14.3, 33.0, 32.1, 12.5]),
    ("我认为AI技术能帮助游客更直观地理解历史文化内容", 3.64, 1.02, [4.5, 8.9, 25.0, 42.0, 19.6]),
    ("我认为AI互动设备操作起来简单易懂，不会有使用门槛", 3.41, 1.08, [6.3, 12.5, 30.4, 35.7, 15.2]),
    ("我认为在历史文化实景戏剧中引入AI技术是有必要的", 3.78, 0.98, [3.6, 7.1, 21.4, 43.8, 24.1]),
    ("相比传统的人工讲解/静态观演，我对AI技术带来的互动体验更感兴趣", 3.52, 1.06, [5.4, 10.7, 28.6, 37.5, 17.9]),
    ("我认为AI技术能与历史文化内容自然融合，不会有违和感", 3.46, 1.06, [5.4, 11.6, 30.4, 36.6, 16.1]),
]

# 第16题：体验与文化价值预期（含注意力检测）
Q16_ITEMS = [
    ("我预期AI技术能让我在体验时产生身临其境的历史场景沉浸感", 3.68, 1.03, [4.5, 8.0, 24.1, 42.0, 21.4]),
    ("我预期AI互动能让我与历史剧情、人物产生更强的情感共鸣", 3.59, 1.05, [4.5, 9.8, 26.8, 40.2, 18.8]),
    ("我预期这类AI赋能的实景戏剧，能让我学到新的历史文化知识", 3.78, 0.97, [3.6, 6.3, 22.3, 44.6, 23.2]),
    ("我预期体验后，会对相关历史文化产生更深的认同感", 3.74, 0.98, [3.6, 7.1, 23.2, 43.8, 22.3]),
    ("*注意力检测 本题请您选择'非常不符合'", 1.05, 0.30, [97.3, 1.8, 0.9, 0.0, 0.0]),  # 特殊处理
    ("我认为这类AI赋能的实景戏剧，能成为了解历史文化的优质窗口", 3.78, 0.96, [3.6, 6.3, 21.4, 45.5, 23.2]),
    ("我预期这类AI赋能的项目，整体体验会优于传统实景戏剧", 3.51, 1.05, [5.4, 10.7, 28.6, 38.4, 17.0]),
]

# 第17题：体验阻碍因素
Q17_ITEMS = [
    ("门票/体验项目价格过高，会影响我参与体验的意愿", 2.90, 1.15, [12.5, 26.8, 28.6, 22.3, 9.8]),
    ("AI设备操作复杂、体验故障多，会影响我参与体验的意愿", 2.78, 1.11, [14.3, 28.6, 30.4, 18.8, 8.0]),
    ("AI技术与历史文化融合生硬、违和，会影响我参与体验的意愿", 2.71, 1.12, [16.1, 30.4, 28.6, 17.0, 8.0]),
]

# 第18题：体验与消费意愿
Q18_ITEMS = [
    ("未来我愿意专门前往体验AI赋能的历史文化实景戏剧项目", 3.87, 0.96, [2.7, 6.3, 18.8, 45.5, 26.8]),
    ("我愿意为AI赋能的特色体验项目，支付合理的额外费用", 3.60, 1.05, [4.5, 9.8, 25.9, 41.1, 18.8]),
    ("我愿意向亲友、同事推荐这类AI赋能的实景戏剧项目", 3.79, 0.98, [3.6, 7.1, 20.5, 44.6, 24.1]),
]

# ============== 主观题模板 ==============

POSITIVE_COMMENTS = [
    "整体体验非常棒，AI技术与历史文化的结合很有创意，让人印象深刻。",
    "景区的AI导览系统很智能，帮助我更好地了解了历史文化背景，推荐！",
    "沉浸式体验做得很好，感觉穿越到了古代，非常震撼。",
    "AI互动装置让游览变得更加有趣，孩子也很喜欢，下次还会再来。",
    "光影效果和实景建筑的结合非常精彩，是一次难忘的文化之旅。",
    "景区的服务态度很好，AI技术的应用让游览更加便捷高效。",
    "这次体验让我对历史文化有了更深的了解，非常值得推荐。",
    "整体感觉很新鲜，科技与文化的融合很成功，希望继续优化。",
    "AI数字人的讲解很生动，让枯燥的历史变得有趣起来了。",
    "体验感超出预期，特别是VR沉浸式项目，强烈推荐给朋友们。",
    "景区的环境和服务都很好，AI技术的应用提升了整体体验质量。",
    "这是一次非常有意义的文化之旅，让我收获满满。",
    "景区的实景演出非常精彩，AI技术的加入让体验更加丰富。",
    "整体满意度很高，特别是沉浸式的体验让人印象深刻。",
    "推荐大家来体验，科技感十足，历史文化内容也很丰富。",
]

NEUTRAL_COMMENTS = [
    "整体体验还可以，AI技术的应用有亮点但还需要改进。",
    "景区环境不错，但AI体验项目可以更丰富一些。",
    "体验感中规中矩，有些地方科技感比较生硬。",
    "总体来说还行，希望以后能有更多互动性强的项目。",
    "AI技术的融入还可以，但感觉和历史文化结合得不够自然。",
    "体验过程有些小问题，但整体还是可以接受的。",
    "景区的服务态度很好，但AI设备有时候会出现故障。",
    "对于这个价格的体验来说，感觉还可以再提升一下。",
    "整体感觉一般，没有特别惊艳的地方，但也不差。",
    "期待景区继续优化AI体验项目，让游览更加有趣。",
]

SUGGESTION_COMMENTS = [
    "建议增加更多AI互动项目，提升游客的参与感和体验感。",
    "希望能增加更多关于当地历史文化的AI讲解内容。",
    "建议优化AI设备的操作界面，让老年游客也能轻松使用。",
    "希望景区能推出更多家庭亲子类的AI体验项目。",
    "建议加强AI技术与历史文化内容的深度融合。",
    "希望能增加夜间的AI光影秀项目，丰富游览体验。",
    "建议设置AI体验项目的排队预约系统，减少等待时间。",
    "希望景区能提供多种语言的AI导览服务。",
    "建议在AI互动中增加更多历史人物的角色互动。",
    "希望能推出AI导览的个性化推荐功能。",
]


def distribute_to_exact_count(target_counts: List[int]) -> List[int]:
    """生成精确匹配目标人数的分布"""
    result = []
    for i, count in enumerate(target_counts):
        result.extend([i] * count)
    random.shuffle(result)
    return result


def distribute_categorical(total: int, proportions: List[float]) -> List[int]:
    """根据比例生成分类分布，确保总数正确"""
    counts = [int(total * p) for p in proportions]
    # 处理余数
    remainder = total - sum(counts)
    for i in range(remainder):
        # 随机分配余数到一个类别
        idx = random.randint(0, len(counts) - 1)
        counts[idx] += 1
    return counts


def generate_likert_scores(n: int, mean: float, std: float, distribution: List[float]) -> List[int]:
    """生成符合指定均值、标准差和分布的量表分数"""
    # 根据目标分布计算各分数的目标人数
    target_counts = [int(n * p / 100) for p in distribution]
    # 处理余数
    remainder = n - sum(target_counts)
    # 将余数加到中位数附近的分数
    for i in range(remainder):
        target_counts[2] += 1  # 加到"一般"选项

    # 生成分数列表
    scores = []
    for score_idx, count in enumerate(target_counts):
        score = score_idx + 1  # 转换为1-5分
        scores.extend([score] * count)

    # 打乱顺序
    random.shuffle(scores)

    # 微调以更好地匹配目标均值和标准差
    scores = np.array(scores)
    current_mean = np.mean(scores)
    current_std = np.std(scores)

    # 如果均值偏差较大，进行微调
    if abs(current_mean - mean) > 0.05:
        # 找到需要调整的分数
        diff = current_mean - mean
        if diff > 0:  # 当前均值过高，需要降低一些高分
            for i in range(len(scores)):
                if scores[i] > 3 and random.random() < abs(diff) * 0.3:
                    scores[i] -= 1
                    if abs(np.mean(scores) - mean) < 0.05:
                        break
        else:  # 当前均值过低，需要提高一些低分
            for i in range(len(scores)):
                if scores[i] < 3 and random.random() < abs(diff) * 0.3:
                    scores[i] += 1
                    if abs(np.mean(scores) - mean) < 0.05:
                        break

    return scores.tolist()


def generate_likert_scores_v2(n: int, mean: float, std: float, distribution: List[float], is_attention_check: bool = False, attention_value: int = 0) -> List[int]:
    """生成符合指定均值、标准差和分布的量表分数（改进版）"""

    if is_attention_check:
        # 注意力检测题特殊处理
        if attention_value == 5:  # 选择"非常符合"
            scores = [5] * int(n * 0.978)
            for i in range(n - len(scores)):
                scores.append(random.choice([1, 2, 3, 4]))
        elif attention_value == 1:  # 选择"非常不符合"
            scores = [1] * int(n * 0.973)
            for i in range(n - len(scores)):
                scores.append(random.choice([2, 3, 4, 5]))
        random.shuffle(scores)
        return scores[:n]

    # 根据目标分布计算各分数的人数
    target_counts = [int(n * p / 100) for p in distribution]
    remainder = n - sum(target_counts)

    # 分配余数到最接近均值的选项
    for i in range(remainder):
        # 找到最需要增加的类别
        diffs = [abs((i + 1) - mean) for i in range(5)]
        min_idx = diffs.index(min(diffs))
        target_counts[min_idx] += 1

    # 生成分数列表
    scores = []
    for score_idx, count in enumerate(target_counts):
        score = score_idx + 1
        scores.extend([score] * count)

    random.shuffle(scores)

    return scores


def generate_multi_select_answers(n: int, options: List[Tuple[str, float]], min_select: int = 1, max_select: int = None) -> List[List[str]]:
    """生成多选题答案"""
    if max_select is None:
        max_select = len(options)

    answers = []
    option_names = [opt[0] for opt in options]
    option_probs = [opt[1] for opt in options]

    for _ in range(n):
        selected = []
        for i, (name, prob) in enumerate(options):
            if random.random() < prob:
                selected.append(name)

        # 确保至少选择一个（除非有特殊选项如"其他"）
        if len(selected) == 0 and min_select > 0:
            # 随机选择一个
            idx = random.choices(range(len(options)), weights=option_probs)[0]
            selected.append(option_names[idx])

        # 如果选择了太多，随机移除一些
        if len(selected) > max_select:
            selected = random.sample(selected, max_select)

        answers.append(selected)

    return answers


def generate_subjective_answer(attitude_level: int = 4) -> str:
    """根据态度水平生成主观题答案"""
    if attitude_level >= 4:
        # 积极态度
        base = random.choice(POSITIVE_COMMENTS)
        if random.random() < 0.5:
            suggestion = random.choice(SUGGESTION_COMMENTS)
            return f"{base}{suggestion}"
        return base
    elif attitude_level == 3:
        # 中立态度
        return random.choice(NEUTRAL_COMMENTS)
    else:
        # 消极或不太满意
        return random.choice(NEUTRAL_COMMENTS)


@dataclass
class Respondent:
    """单个受访者数据"""
    respondent_id: str
    gender: str
    age: str
    education: str
    occupation: str
    history_interest: int  # 1-5分
    q1_experience: str  # 第1题
    # 以下题目根据q1_experience有不同的回答
    q2_ai_experience: List[str] = field(default_factory=list)  # 第2题（多选）
    q3_purpose: List[str] = field(default_factory=list)  # 第3题（多选）
    q4_channel: List[str] = field(default_factory=list)  # 第4题（多选）
    q5_first_visit: str = ""  # 第5题
    q6_stay_duration: str = ""  # 第6题
    q7_ai_perception: Dict[str, int] = field(default_factory=dict)  # 第7题（量表）
    q8_immersion: Dict[str, int] = field(default_factory=dict)  # 第8题（量表）
    q9_cultural_value: Dict[str, int] = field(default_factory=dict)  # 第9题（量表）
    q10_satisfaction: Dict[str, int] = field(default_factory=dict)  # 第10题（量表）
    q11_no_ai_reason: List[str] = field(default_factory=list)  # 第11题（多选）
    q12_ai_feeling: Dict[str, int] = field(default_factory=dict)  # 第12题（量表）
    q13_visit_purpose: List[str] = field(default_factory=list)  # 第13题（多选）
    q14_visit_frequency: str = ""  # 第14题
    q15_ai_acceptance: Dict[str, int] = field(default_factory=dict)  # 第15题（量表）
    q16_expectation: Dict[str, int] = field(default_factory=dict)  # 第16题（量表）
    q17_obstacle: Dict[str, int] = field(default_factory=dict)  # 第17题（量表）
    q18_willingness: Dict[str, int] = field(default_factory=dict)  # 第18题（量表）
    subjective_overall: str = ""  # 主观题：整体感受
    subjective_suggestion: str = ""  # 主观题：改进建议


def generate_respondents(n: int = 750) -> List[Respondent]:
    """生成所有受访者数据"""

    # 1. 首先生成人口统计学特征分布
    genders = distribute_to_exact_count([count for _, count, _ in GENDER_DIST])
    ages = distribute_to_exact_count([count for _, count, _ in AGE_DIST])
    educations = distribute_to_exact_count([count for _, count, _ in EDUCATION_DIST])
    occupations = distribute_to_exact_count([count for _, count, _ in OCCUPATION_DIST])
    history_interests = distribute_to_exact_count([count for _, count, _ in HISTORY_INTEREST_DIST])

    # 2. 生成第1题答案分布
    q1_answers = distribute_to_exact_count([count for _, count, _ in Q1_DIST])

    # 3. 根据第1题答案，确定后续题目的回答者
    # 体验过(0)的603人回答第2-10题
    # 未体验过但有消费习惯(1)的112人回答第13-18题
    # 未体验过且无消费习惯(2)的35人只回答第24题（历史文化兴趣）

    # 4. 预先生成各类量表题答案

    # 第5题答案（仅603人）
    q5_answers = distribute_to_exact_count([count for _, count, _ in Q5_DIST])
    random.shuffle(q5_answers)

    # 第6题答案（仅603人）
    q6_answers = distribute_to_exact_count([count for _, count, _ in Q6_DIST])
    random.shuffle(q6_answers)

    # 第14题答案（仅112人）
    q14_answers = distribute_to_exact_count([count for _, count, _ in Q14_DIST])
    random.shuffle(q14_answers)

    # 第2题多选答案（603人）
    q2_answers = generate_multi_select_answers(603, Q2_OPTIONS)
    # 确保87人选择"体验过项目，但未接触过任何上述AI/智能技术"
    no_ai_count = 0
    for i in range(len(q2_answers)):
        if no_ai_count >= 87:
            break
        if len(q2_answers[i]) == 0:
            q2_answers[i] = ["体验过项目，但未接触过任何上述AI/智能技术"]
            no_ai_count += 1
    # 如果还不够87人，随机修改
    while no_ai_count < 87:
        idx = random.randint(0, 602)
        if "体验过项目，但未接触过任何上述AI/智能技术" not in q2_answers[idx]:
            q2_answers[idx] = ["体验过项目，但未接触过任何上述AI/智能技术"]
            no_ai_count += 1

    # 第3题多选答案（603人）
    q3_answers = generate_multi_select_answers(603, Q3_OPTIONS)

    # 第4题多选答案（603人）
    q4_answers = generate_multi_select_answers(603, Q4_OPTIONS)

    # 第11题多选答案（87人，体验过但未接触AI者）
    q11_answers = generate_multi_select_answers(87, Q11_OPTIONS)

    # 第13题多选答案（112人）
    q13_answers = generate_multi_select_answers(112, Q13_OPTIONS)

    # 5. 生成量表题答案
    # 第7题（603人）
    q7_scores = {}
    for item, mean, std, dist in Q7_ITEMS:
        q7_scores[item] = generate_likert_scores_v2(603, mean, std, dist)

    # 第8题（603人）
    q8_scores = {}
    for i, (item, mean, std, dist) in enumerate(Q8_ITEMS):
        if "*注意力检测" in item:
            q8_scores[item] = generate_likert_scores_v2(603, mean, std, dist, is_attention_check=True, attention_value=5)
        else:
            q8_scores[item] = generate_likert_scores_v2(603, mean, std, dist)

    # 第9题（603人）
    q9_scores = {}
    for item, mean, std, dist in Q9_ITEMS:
        q9_scores[item] = generate_likert_scores_v2(603, mean, std, dist)

    # 第10题（603人）
    q10_scores = {}
    for item, mean, std, dist in Q10_ITEMS:
        q10_scores[item] = generate_likert_scores_v2(603, mean, std, dist)

    # 第12题（87人）
    q12_scores = {}
    for item, mean, std, dist in Q12_ITEMS:
        q12_scores[item] = generate_likert_scores_v2(87, mean, std, dist)

    # 第15题（147人：112+35）
    q15_scores = {}
    for item, mean, std, dist in Q15_ITEMS:
        q15_scores[item] = generate_likert_scores_v2(147, mean, std, dist)

    # 第16题（147人）
    q16_scores = {}
    for i, (item, mean, std, dist) in enumerate(Q16_ITEMS):
        if "*注意力检测" in item:
            q16_scores[item] = generate_likert_scores_v2(147, mean, std, dist, is_attention_check=True, attention_value=1)
        else:
            q16_scores[item] = generate_likert_scores_v2(147, mean, std, dist)

    # 第17题（147人）
    q17_scores = {}
    for item, mean, std, dist in Q17_ITEMS:
        q17_scores[item] = generate_likert_scores_v2(147, mean, std, dist)

    # 第18题（147人）
    q18_scores = {}
    for item, mean, std, dist in Q18_ITEMS:
        q18_scores[item] = generate_likert_scores_v2(147, mean, std, dist)

    # 6. 组装所有受访者数据
    respondents = []

    # 追踪各类回答者的索引
    experienced_idx = 0  # 体验过的603人
    consumer_idx = 0  # 有消费习惯的112人
    no_habit_idx = 0  # 无消费习惯的35人

    # 追踪未接触AI的87人在体验过群体中的索引
    no_ai_respondent_indices = random.sample(range(603), 87)

    for i in range(n):
        respondent = Respondent(
            respondent_id=f"R{str(i+1).zfill(4)}",
            gender=GENDER_DIST[genders[i]][0],
            age=AGE_DIST[ages[i]][0],
            education=EDUCATION_DIST[educations[i]][0],
            occupation=OCCUPATION_DIST[occupations[i]][0],
            history_interest=history_interests[i] + 1,  # 1-5分
            q1_experience=Q1_DIST[q1_answers[i]][0],
        )

        # 根据第1题答案填写后续题目
        if q1_answers[i] == 0:  # 体验过
            # 第2-10题
            respondent.q2_ai_experience = q2_answers[experienced_idx]
            respondent.q3_purpose = q3_answers[experienced_idx]
            respondent.q4_channel = q4_answers[experienced_idx]
            respondent.q5_first_visit = Q5_DIST[q5_answers[experienced_idx]][0]
            respondent.q6_stay_duration = Q6_DIST[q6_answers[experienced_idx]][0]

            # 第7题
            for item, scores in q7_scores.items():
                respondent.q7_ai_perception[item] = scores[experienced_idx]

            # 第8题
            for item, scores in q8_scores.items():
                respondent.q8_immersion[item] = scores[experienced_idx]

            # 第9题
            for item, scores in q9_scores.items():
                respondent.q9_cultural_value[item] = scores[experienced_idx]

            # 第10题
            for item, scores in q10_scores.items():
                respondent.q10_satisfaction[item] = scores[experienced_idx]

            # 判断是否是未接触AI的87人之一
            if experienced_idx in no_ai_respondent_indices:
                # 第11题
                no_ai_idx = no_ai_respondent_indices.index(experienced_idx)
                respondent.q11_no_ai_reason = q11_answers[no_ai_idx]

                # 第12题
                for item, scores in q12_scores.items():
                    respondent.q12_ai_feeling[item] = scores[no_ai_idx]

            # 计算态度水平（基于量表题平均分）
            attitude_scores = list(respondent.q10_satisfaction.values())
            attitude_level = int(round(np.mean(attitude_scores)))

            experienced_idx += 1

        elif q1_answers[i] == 1:  # 未体验过，但有消费习惯
            # 第13-18题
            respondent.q13_visit_purpose = q13_answers[consumer_idx]
            respondent.q14_visit_frequency = Q14_DIST[q14_answers[consumer_idx]][0]

            # 第15题
            for item, scores in q15_scores.items():
                respondent.q15_ai_acceptance[item] = scores[consumer_idx]

            # 第16题
            for item, scores in q16_scores.items():
                respondent.q16_expectation[item] = scores[consumer_idx]

            # 第17题
            for item, scores in q17_scores.items():
                respondent.q17_obstacle[item] = scores[consumer_idx]

            # 第18题
            for item, scores in q18_scores.items():
                respondent.q18_willingness[item] = scores[consumer_idx]

            # 态度水平
            attitude_scores = list(respondent.q18_willingness.values())
            attitude_level = int(round(np.mean(attitude_scores)))

            consumer_idx += 1

        else:  # 未体验过，无消费习惯
            # 第15-18题（注意：原始数据中这35人也回答这些题，因为第15题总样本是147人）
            idx_147 = 112 + no_habit_idx  # 从第113个开始

            # 第15题
            for item, scores in q15_scores.items():
                respondent.q15_ai_acceptance[item] = scores[idx_147]

            # 第16题
            for item, scores in q16_scores.items():
                respondent.q16_expectation[item] = scores[idx_147]

            # 第17题
            for item, scores in q17_scores.items():
                respondent.q17_obstacle[item] = scores[idx_147]

            # 第18题
            for item, scores in q18_scores.items():
                respondent.q18_willingness[item] = scores[idx_147]

            attitude_level = int(round(np.mean(list(respondent.q15_ai_acceptance.values()))))

            no_habit_idx += 1

        # 生成主观题答案
        respondent.subjective_overall = generate_subjective_answer(attitude_level)
        if random.random() < 0.7:  # 70%的人会填写建议
            respondent.subjective_suggestion = random.choice(SUGGESTION_COMMENTS)

        respondents.append(respondent)

    return respondents


def convert_to_dict(respondents: List[Respondent]) -> List[Dict]:
    """将受访者数据转换为字典格式"""
    result = []
    for r in respondents:
        data = {
            "受访者ID": r.respondent_id,
            "性别": r.gender,
            "年龄": r.age,
            "学历": r.education,
            "职业": r.occupation,
            "历史文化兴趣程度(1-5)": r.history_interest,
            "第1题_是否体验过": r.q1_experience,
            "第2题_AI体验项目": r.q2_ai_experience if r.q2_ai_experience else None,
            "第3题_出游目的": r.q3_purpose if r.q3_purpose else None,
            "第4题_了解渠道": r.q4_channel if r.q4_channel else None,
            "第5题_是否首次到访": r.q5_first_visit if r.q5_first_visit else None,
            "第6题_停留时长": r.q6_stay_duration if r.q6_stay_duration else None,
            "第7题_AI技术感知": r.q7_ai_perception if r.q7_ai_perception else None,
            "第8题_沉浸体验测量": r.q8_immersion if r.q8_immersion else None,
            "第9题_文化价值感知": r.q9_cultural_value if r.q9_cultural_value else None,
            "第10题_满意度与行为意向": r.q10_satisfaction if r.q10_satisfaction else None,
            "第11题_未接触AI原因": r.q11_no_ai_reason if r.q11_no_ai_reason else None,
            "第12题_AI技术应用感受": r.q12_ai_feeling if r.q12_ai_feeling else None,
            "第13题_游览目的": r.q13_visit_purpose if r.q13_visit_purpose else None,
            "第14题_游览频次": r.q14_visit_frequency if r.q14_visit_frequency else None,
            "第15题_AI认知与接受度": r.q15_ai_acceptance if r.q15_ai_acceptance else None,
            "第16题_体验与文化价值预期": r.q16_expectation if r.q16_expectation else None,
            "第17题_体验阻碍因素": r.q17_obstacle if r.q17_obstacle else None,
            "第18题_体验与消费意愿": r.q18_willingness if r.q18_willingness else None,
            "主观题_整体感受": r.subjective_overall,
            "主观题_改进建议": r.subjective_suggestion if r.subjective_suggestion else None,
        }
        result.append(data)
    return result


def validate_statistics(respondents: List[Respondent]) -> Dict:
    """验证生成数据的统计特征"""
    stats = {
        "总人数": len(respondents),
        "性别分布": {},
        "年龄分布": {},
        "学历分布": {},
        "职业分布": {},
        "历史文化兴趣分布": {},
        "第1题分布": {},
        "第5题分布": {},
        "第6题分布": {},
        "第14题分布": {},
    }

    # 人口统计学
    for r in respondents:
        stats["性别分布"][r.gender] = stats["性别分布"].get(r.gender, 0) + 1
        stats["年龄分布"][r.age] = stats["年龄分布"].get(r.age, 0) + 1
        stats["学历分布"][r.education] = stats["学历分布"].get(r.education, 0) + 1
        stats["职业分布"][r.occupation] = stats["职业分布"].get(r.occupation, 0) + 1
        stats["历史文化兴趣分布"][r.history_interest] = stats["历史文化兴趣分布"].get(r.history_interest, 0) + 1
        stats["第1题分布"][r.q1_experience] = stats["第1题分布"].get(r.q1_experience, 0) + 1

        if r.q5_first_visit:
            stats["第5题分布"][r.q5_first_visit] = stats["第5题分布"].get(r.q5_first_visit, 0) + 1
        if r.q6_stay_duration:
            stats["第6题分布"][r.q6_stay_duration] = stats["第6题分布"].get(r.q6_stay_duration, 0) + 1
        if r.q14_visit_frequency:
            stats["第14题分布"][r.q14_visit_frequency] = stats["第14题分布"].get(r.q14_visit_frequency, 0) + 1

    return stats


def main():
    print("开始生成750份问卷数据...")
    print("=" * 60)

    # 生成受访者数据
    respondents = generate_respondents(750)

    # 转换为字典格式
    data = convert_to_dict(respondents)

    # 保存为JSON文件
    output_path = "/home/claw/.openclaw/workspace/output/问卷数据_750份.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"数据已保存到: {output_path}")

    # 验证统计特征
    stats = validate_statistics(respondents)

    print("\n" + "=" * 60)
    print("数据验证统计")
    print("=" * 60)

    print(f"\n总人数: {stats['总人数']}")

    print("\n性别分布:")
    for k, v in sorted(stats['性别分布'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}人 ({v/750*100:.1f}%)")

    print("\n第1题分布:")
    for k, v in sorted(stats['第1题分布'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}人 ({v/750*100:.1f}%)")

    print("\n第5题分布 (仅体验过者):")
    for k, v in sorted(stats['第5题分布'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}人 ({v/603*100:.1f}%)")

    # 计算量表题均值
    print("\n量表题均值验证:")

    # 第7题
    q7_means = {}
    for r in respondents:
        if r.q7_ai_perception:
            for item, score in r.q7_ai_perception.items():
                if item not in q7_means:
                    q7_means[item] = []
                q7_means[item].append(score)

    print("\n第7题 AI技术感知:")
    for item, scores in q7_means.items():
        mean = np.mean(scores)
        std = np.std(scores)
        print(f"  均值: {mean:.2f}, 标准差: {std:.2f}")

    # 第10题
    q10_means = {}
    for r in respondents:
        if r.q10_satisfaction:
            for item, score in r.q10_satisfaction.items():
                if item not in q10_means:
                    q10_means[item] = []
                q10_means[item].append(score)

    print("\n第10题 满意度与行为意向:")
    for item, scores in q10_means.items():
        mean = np.mean(scores)
        std = np.std(scores)
        print(f"  均值: {mean:.2f}, 标准差: {std:.2f}")

    print("\n" + "=" * 60)
    print("数据生成完成！")


if __name__ == "__main__":
    main()