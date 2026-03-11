#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问卷 20260311.csv 数据处理脚本
生成 750 个样本的完整答案数据
"""

import json
import random
import os
from datetime import datetime

# 设置随机种子确保可重复性
random.seed(42)

# 读取问卷数据
filename = '/home/claw/.openclaw/workspace/问卷 20260311.csv'

print("🔍 正在读取问卷数据...")
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print(f"✓ 成功读取文件，共 {len(lines)} 行")

# 提取题目和选项
questions = []
current_q = None

for line in lines:
    if '第' in line and '题' in line:
        if current_q:
            questions.append(current_q)
        current_q = {
            'text': line.strip(),
            'options': [],
            'counts': [],
            'percentages': []
        }
    elif current_q and ',' in line:
        parts = line.split(',')
        if len(parts) >= 4:
            option = parts[1].strip()
            count_str = parts[2].strip()
            percentage_str = parts[3].strip()
            
            # 尝试转换数字
            try:
                count = int(count_str) if count_str.isdigit() else 0
                percentage = float(percentage_str) if percentage_str.replace('.', '').replace('-', '').isdigit() else 0.0
            except:
                count = 0
                percentage = 0.0
            
            if option and count > 0:
                current_q['options'].append(option)
                current_q['counts'].append(count)
                current_q['percentages'].append(percentage)

if current_q:
    questions.append(current_q)

print(f"✓ 共提取 {len(questions)} 道题目")

# 显示题目概览
print("\n📋 题目概览:")
for i, q in enumerate(questions):
    q_type = "多选" if "多选" in q['text'] else ("量表题" if "量表题" in q['text'] else "单选")
    print(f"  {i+1:2d}. {q_type}: {q['text'][:60]}... [{len(q['options'])}选项]")

# 生成 750 个样本的答案
print(f"\n🔄 正在生成 750 个样本的答案...")

# 人口统计学信息生成规则
def generate_demographics(sample_id):
    """生成人口统计学信息"""
    # 年龄分布（基于问卷统计）
    age_weights = [0.06, 0.304, 0.26, 0.18, 0.124, 0.072]
    age_groups = ["18 岁以下", "18-25 岁", "26-35 岁", "36-45 岁", "46-55 岁", "56 岁以上"]
    age = random.choices(age_groups, weights=age_weights, k=1)[0]
    
    # 学历分布
    edu_weights = [0.104, 0.168, 0.504, 0.224]
    edu_groups = ["高中及以下", "大专", "本科", "硕士及以上"]
    education = random.choices(edu_groups, weights=edu_weights, k=1)[0]
    
    # 职业分布
    job_weights = [0.22, 0.264, 0.16, 0.116, 0.096, 0.08, 0.064]
    job_groups = ["学生", "企业职员", "事业单位/公务员", "自由职业者", "个体经营者", "退休人员", "其他"]
    occupation = random.choices(job_groups, weights=job_weights, k=1)[0]
    
    return {
        "sample_id": f"S{sample_id:04d}",
        "age": age,
        "education": education,
        "occupation": occupation
    }

# 根据选项生成答案（按比例）
def generate_single_choice_answer(question, demographics):
    """生成单选题答案"""
    options = question['options']
    percentages = question['percentages']
    
    # 归一化百分比
    total = sum(percentages)
    weights = [p/total for p in percentages]
    
    # 随机选择
    answer = random.choices(options, weights=weights, k=1)[0]
    return answer

# 生成多选题答案
def generate_multi_choice_answer(question, demographics, max_options=3):
    """生成多选题答案"""
    options = question['options']
    percentages = question['percentages']
    
    # 归一化百分比
    total = sum(percentages)
    weights = [p/total for p in percentages]
    
    # 根据权重选择 1-3 个选项
    num_options = random.randint(1, min(max_options, len(options)))
    
    # 使用轮盘赌算法选择
    selected = []
    remaining_weights = weights.copy()
    remaining_options = options.copy()
    
    for _ in range(num_options):
        if not remaining_weights:
            break
        
        # 归一化剩余权重
        total = sum(remaining_weights)
        normalized = [w/total for w in remaining_weights]
        
        # 选择一个
        chosen_idx = random.choices(range(len(remaining_weights)), weights=normalized, k=1)[0]
        selected.append(remaining_options[chosen_idx])
        
        # 移除已选
        remaining_weights.pop(chosen_idx)
        remaining_options.pop(chosen_idx)
    
    return selected

# 生成量表题答案（1-5 分）
def generate_scale_answer(question, demographics):
    """生成量表题答案（1-5 分）"""
    # 根据人口统计学信息调整分布
    if demographics['age'] in ['18-25 岁', '26-35 岁']:
        # 年轻人更倾向于高分
        weights = [0.05, 0.10, 0.25, 0.35, 0.25]
    elif demographics['age'] in ['36-45 岁', '46-55 岁']:
        weights = [0.10, 0.20, 0.30, 0.25, 0.15]
    else:
        weights = [0.15, 0.25, 0.30, 0.20, 0.10]
    
    answers = ['1 分', '2 分', '3 分', '4 分', '5 分']
    answer = random.choices(answers, weights=weights, k=1)[0]
    return answer

# 生成主观题答案
def generate_open_ended_answer(question, demographics, sample_answers):
    """生成主观题答案"""
    # 基于前面答案的倾向生成连贯的主观题
    age = demographics['age']
    education = demographics['education']
    occupation = demographics['occupation']
    
    # 根据年龄和职业生成不同风格的答案
    if age in ['18-25 岁', '26-35 岁']:
        style = "年轻、热情、有探索精神"
    elif age in ['36-45 岁']:
        style = "理性、务实、注重体验"
    else:
        style = "温和、包容、富有文化情怀"
    
    # 简单模板生成答案
    templates = [
        f"作为{education}学历的{occupation}，我认为这个项目非常有意义。{style}，希望能有更多创新体验。",
        f"从{age}年龄段的角度来看，这个体验很棒。作为{occupation}，我期待未来能有更多类似的文化项目。",
        f"整体体验不错，尤其是在文化传承方面做得很好。作为{style}的人，我认为这类项目值得推广。",
        f"这个项目的创意很棒，希望能看到更多技术应用于文化领域。作为{occupation}，我对这样的创新很感兴趣。",
        f"体验很好，感受到了传统文化与现代科技的完美结合。希望能有更多这样的文化活动。"
    ]
    
    answer = random.choice(templates)
    return answer

# 生成所有样本
print("📝 开始生成样本数据...")
all_samples = []

for sample_id in range(1, 751):
    # 生成人口统计学信息
    demographics = generate_demographics(sample_id)
    
    # 生成本次样本的答案
    sample_answers = {}
    
    for i, q in enumerate(questions):
        q_text = q['text']
        
        # 判断题目类型
        if "多选" in q_text:
            answers = generate_multi_choice_answer(q, demographics)
        elif "量表题" in q_text or ("1-5 分" in q_text and "主观题" not in q_text):
            answers = generate_scale_answer(q, demographics)
        elif "主观题" in q_text:
            answers = generate_open_ended_answer(q, demographics, sample_answers)
        else:
            answers = generate_single_choice_answer(q, demographics)
        
        # 存储答案
        question_key = f"question_{i+1}"
        sample_answers[question_key] = {
            "question_text": q_text[:100],
            "question_type": "多选" if "多选" in q_text else ("量表题" if "量表题" in q_text or ("1-5 分" in q_text and "主观题" not in q_text) else "主观题" if "主观题" in q_text else "单选"),
            "answer": answers
        }
        
        # 记录以便后续引用
        sample_answers[f"q{i+1}_answer"] = answers
    
    # 合并人口统计学信息和答案
    sample = {
        **demographics,
        **sample_answers
    }
    
    all_samples.append(sample)
    
    if sample_id % 100 == 0:
        print(f"  已完成 {sample_id}/750 个样本")

# 保存结果
output_dir = '/home/claw/.openclaw/workspace/output'
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, 'questionnaire_results_20260311.json')
print(f"\n💾 正在保存结果到 {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_samples, f, ensure_ascii=False, indent=2)

print(f"✓ 成功保存 {len(all_samples)} 个样本的答案")
print(f"✓ 文件大小：{os.path.getsize(output_file) / 1024:.2f} KB")

# 显示结果示例
print("\n📊 结果示例（前 3 个样本）:")
for i, sample in enumerate(all_samples[:3]):
    print(f"\n样本 {sample['sample_id']}:")
    print(f"  年龄：{sample['age']}")
    print(f"  学历：{sample['education']}")
    print(f"  职业：{sample['occupation']}")
    print(f"  第 1 题答案：{sample.get('question_1', {}).get('answer', 'N/A')}")
    print(f"  第 2 题答案：{sample.get('question_2', {}).get('answer', 'N/A')}")

print("\n✅ 问卷数据处理完成！")
print(f"📁 结果文件：{output_file}")
