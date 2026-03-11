#!/usr/bin/env python3
"""
测试答案生成器
Test answer generator
"""

import sys
sys.path.insert(0, '.')

from src.utils.stats import load_question_stats
from src.utils.generators import AnswerGenerator

def main():
    print("="*70)
    print("问卷星自动填写系统 - 答案生成测试")
    print("="*70)
    
    # 加载数据
    stats = load_question_stats('data/q28_response.csv')
    print(f"\n✓ 加载了 {len(stats)} 个问题的统计信息")
    
    # 创建生成器
    generator = AnswerGenerator(stats)
    
    # 测试每种题型
    test_questions = {
        '1': ('单选题', generator.generate_single_choice),
        '2': ('多选题', generator.generate_multiple_choice),
        '7': ('量表题', generator.generate_scale_question),
        '25': ('简答题', generator.generate_short_answer),
    }
    
    print("\n答案生成示例：")
    print("-"*70)
    
    for qid, (qtype, generate_func) in test_questions.items():
        try:
            if qtype == '简答题':
                answer = generate_func(qid)
                print(f"\n{qid}. ({qtype}):")
                print(f"   {answer}")
            else:
                answer = generate_func(qid)
                print(f"\n{qid}. ({qtype}): {answer}")
        except Exception as e:
            print(f"\n{qid}. ({qtype}): 生成失败 - {e}")
    
    # 批量测试
    print("\n" + "="*70)
    print("批量测试（生成 5 份完整答案）")
    print("-"*70)
    
    for i in range(5):
        print(f"\n【第{i+1}份问卷】")
        for qid in sorted(stats.keys()):
            qtype = stats[qid].get('type', 'unknown')
            
            if 'single' in qtype:
                answer = generator.generate_single_choice(qid)
            elif 'multi' in qtype:
                answer = generator.generate_multiple_choice(qid)
            elif 'scale' in qtype:
                answer = generator.generate_scale_question(qid)
            else:
                answer = generator.generate_short_answer(qid)
            
            # 只显示部分题目
            if qid in ['1', '2', '7', '25']:
                print(f"  Q{qid}: {answer}")
    
    print("\n" + "="*70)
    print("✓ 测试完成")
    print("="*70)

if __name__ == '__main__':
    main()
