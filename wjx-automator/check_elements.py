"""
问卷元素检查工具
用于调试和获取正确的 XPath 选择器
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.stats import load_question_stats
from src.utils.generators import AnswerGenerator


def check_question_types():
    """检查题目类型分布"""
    stats = load_question_stats('data/q28_response_750.csv')
    
    types = {
        'single': 0,
        'multiple': 0,
        'scale': 0,
        'short_answer': 0
    }
    
    for qid, data in stats.items():
        q_type = data.get('type', 'unknown').lower()
        if 'single' in q_type or 'radio' in q_type:
            types['single'] += 1
        elif 'multi' in q_type or 'multiple' in q_type:
            types['multiple'] += 1
        elif 'scale' in q_type or 'rating' in q_type or 'liker' in q_type:
            types['scale'] += 1
        elif 'short' in q_type or 'text' in q_type or 'answer' in q_type:
            types['short_answer'] += 1
    
    print("="*70)
    print("问卷题目类型统计")
    print("="*70)
    print(f"单选题：{types['single']} 题")
    print(f"多选题：{types['multiple']} 题")
    print(f"量表题：{types['scale']} 题")
    print(f"简答题：{types['short_answer']} 题")
    print(f"总计：{sum(types.values())} 题")
    print("="*70)


def test_all_answers():
    """测试所有问题的答案生成"""
    stats = load_question_stats('data/q28_response_750.csv')
    generator = AnswerGenerator(stats)
    
    print("="*70)
    print("所有题目答案生成测试 (1 份样本)")
    print("="*70)
    
    for qid in sorted(stats.keys(), key=int):
        q_type = stats[qid].get('type', 'unknown')
        distribution = stats[qid].get('distribution', {})
        
        # 根据类型生成答案
        if 'single' in q_type:
            answer = generator.generate_single_choice(qid)
        elif 'multi' in q_type:
            answer = generator.generate_multiple_choice(qid)
        elif 'scale' in q_type:
            answer = generator.generate_scale_question(qid)
        else:
            answer = generator.generate_short_answer(qid)
        
        print(f"\nQ{qid} [{q_type}]")
        print(f"  分布：{json.dumps(distribution, ensure_ascii=False)}")
        print(f"  答案：{answer}")
    
    print("\n" + "="*70)
    print("✓ 所有题目测试完成")
    print("="*70)


def test_batch_generation(count=10):
    """批量生成测试"""
    stats = load_question_stats('data/q28_response_750.csv')
    generator = AnswerGenerator(stats)
    
    print("="*70)
    print(f"批量生成测试 ({count} 份样本)")
    print("="*70)
    
    for i in range(count):
        print(f"\n【第{i+1}份问卷】")
        
        # 生成所有答案
        answers = {}
        for qid in sorted(stats.keys(), key=int):
            q_type = stats[qid].get('type', 'unknown')
            
            if 'single' in q_type:
                answers[qid] = generator.generate_single_choice(qid)
            elif 'multi' in q_type:
                answers[qid] = generator.generate_multiple_choice(qid)
            elif 'scale' in q_type:
                answers[qid] = generator.generate_scale_question(qid)
            else:
                answers[qid] = generator.generate_short_answer(qid)
        
        # 显示部分答案（前 5 题）
        for qid in sorted(answers.keys(), key=int)[:5]:
            print(f"  Q{qid}: {answers[qid]}")
        
        # 如果最后一题是简答题，显示答案
        if '28' in answers:
            print(f"  Q28: {answers['28'][:50]}...")
    
    print("\n" + "="*70)
    print("✓ 批量生成测试完成")
    print("="*70)


if __name__ == '__main__':
    print("\n问卷元素检查工具 v1.0")
    print("Author: Misaka妹妹 12 号\n")
    
    # 检查题目类型
    check_question_types()
    
    # 测试答案生成
    print("\n")
    test_all_answers()
    
    # 批量测试
    print("\n")
    test_batch_generation(count=3)
