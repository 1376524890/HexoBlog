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
        if q_type == 'single':
            types['single'] += 1
        elif q_type == 'multiple':
            types['multiple'] += 1
        elif q_type == 'scale':
            types['scale'] += 1
        elif q_type == 'short_answer':
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
