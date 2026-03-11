#!/usr/bin/env python3
"""分析问卷数据并保存为 JSON 格式"""
import json
import re

def parse_survey_content(content):
    """解析问卷内容"""
    lines = content.strip().split('\n')
    
    # 统计行数
    total_lines = len(lines)
    
    # 提取所有问题
    questions = []
    current_question = None
    
    for line in lines:
        # 匹配问题标题
        q_match = re.match(r',第 (\d+) 题：(.+)', line)
        if q_match:
            if current_question:
                questions.append(current_question)
            current_question = {
                'number': q_match.group(1),
                'title': q_match.group(2),
                'data': []
            }
        elif current_question and line.strip():
            current_question['data'].append(line)
    
    if current_question:
        questions.append(current_question)
    
    # 分析列结构
    header_samples = []
    for line in lines:
        if line.strip() and line.count(',') >= 3:
            parts = line.split(',')
            if len(parts) > 3:
                header_samples.append(parts)
                break
    
    # 判断列结构
    column_count = 0
    if header_samples:
        column_count = max(len(h) for h in header_samples)
    
    # 提取列含义
    column_meanings = [
        "序号/选项",
        "数值/标签",
        "人数",
        "占比 (%)",
        "均值",
        "标准差",
        "分布说明"
    ]
    
    # 保存为 JSON
    output_data = {
        'file_info': {
            'original_filename': '问卷 20260311---8a297b2d-5f1d-47a0-9061-21aa20eba025',
            'total_lines': total_lines,
            'file_size_bytes': len(content)
        },
        'structure': {
            'column_count': column_count,
            'columns': column_meanings[:column_count] if column_count <= len(column_meanings) else column_meanings
        },
        'questions_summary': [
            {
                'question_number': q['number'],
                'question_title': q['title'],
                'data_rows': len(q['data']),
                'has_statistics': any('人数' in d or '占比' in d for d in q['data'])
            }
            for q in questions
        ]
    }
    
    return output_data

def main():
    # 读取文件内容
    file_path = '/tmp/问卷数据.csv'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"文件不存在：{file_path}")
        return
    
    # 解析内容
    analysis = parse_survey_content(content)
    
    # 保存为 JSON
    output_path = '/home/claw/.openclaw/workspace/问卷数据.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成！")
    print(f"总行数：{analysis['file_info']['total_lines']}")
    print(f"列数：{analysis['structure']['column_count']}")
    print(f"问题数量：{len(analysis['questions_summary'])}")
    print(f"\nJSON 文件已保存到：{output_path}")
    
    # 输出问题列表
    print("\n=== 问卷问题列表 ===")
    for q in analysis['questions_summary']:
        print(f"第{q['question_number']}题：{q['question_title'][:50]}...")

if __name__ == '__main__':
    main()
