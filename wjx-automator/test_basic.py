#!/usr/bin/env python3
"""
简化版测试脚本 - 仅测试答案生成功能
不需要 selenium 依赖
"""

import sys
sys.path.insert(0, '.')

from src.utils.stats import load_question_stats
from src.utils.generators import AnswerGenerator

def test_basic():
    """基础测试"""
    print("="*70)
    print("问卷星自动填写系统 - 答案生成测试")
    print("="*70)
    
    # 加载数据
    stats = load_question_stats('data/q28_response.csv')
    print(f"\n✓ 加载了 {len(stats)} 个问题的统计信息")
    
    # 创建生成器
    generator = AnswerGenerator(stats)
    
    # 测试每种题型
    tests = [
        ('1', '单选题'),
        ('2', '多选题'),
        ('7', '量表题'),
        ('25', '简答题'),
    ]
    
    print("\n答案生成示例：")
    print("-"*70)
    
    for qid, qtype in tests:
        if qtype == '单选题':
            answer = generator.generate_single_choice(qid)
        elif qtype == '多选题':
            answer = generator.generate_multiple_choice(qid)
        elif qtype == '量表题':
            answer = generator.generate_scale_question(qid)
        else:
            answer = generator.generate_short_answer(qid)
        
        print(f"Q{qid} ({qtype}): {answer}")
    
    print("\n" + "="*70)
    print("✓ 测试完成 - 答案生成功能正常")
    print("="*70)

if __name__ == '__main__':
    test_basic()
