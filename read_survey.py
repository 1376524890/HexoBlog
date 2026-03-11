#!/usr/bin/env python3
"""读取问卷数据并转换为 JSON"""
import subprocess
import json
import sys

def read_survey_file():
    """使用 sudo 读取问卷文件"""
    file_path = '/home/claw/.openclaw/media/inbound/问卷 20260311---8a297b2d-5f1d-47a0-9061-21aa20eba025'
    
    try:
        # 使用 sudo 读取文件
        result = subprocess.run(
            ['sudo', '-S', 'cat', file_path],
            input='plk161211\n',
            text=True,
            capture_output=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"错误：{result.stderr}")
            return None
        
        return result.stdout
    except Exception as e:
        print(f"读取失败：{e}")
        return None

def analyze_csv(content):
    """分析 CSV 内容"""
    lines = content.strip().split('\n')
    
    if not lines:
        return None
    
    header = lines[0].split(',')
    data_rows = [line.split(',') for line in lines[1:] if line.strip()]
    
    return {
        'total_lines': len(lines),
        'data_rows': len(data_rows),
        'columns': header,
        'column_count': len(header),
        'sample_data': data_rows[:3] if data_rows else []
    }

def main():
    content = read_survey_file()
    if not content:
        sys.exit(1)
    
    analysis = analyze_csv(content)
    if not analysis:
        sys.exit(1)
    
    # 输出分析结果
    print("=== 问卷数据分析结果 ===")
    print(f"总行数：{analysis['total_lines']}")
    print(f"数据行数：{analysis['data_rows']}")
    print(f"列数：{analysis['column_count']}")
    print(f"列名：{', '.join(analysis['columns'])}")
    print("\n前 3 行数据示例：")
    for i, row in enumerate(analysis['sample_data'], 1):
        print(f"  第{i}行：{', '.join(row)}")
    
    # 将数据保存为 JSON
    output_data = {
        'summary': {
            'file_name': '问卷 20260311---8a297b2d-5f1d-47a0-9061-21aa20eba025',
            'total_rows': analysis['total_lines'],
            'data_rows': analysis['data_rows'],
            'columns': analysis['columns'],
            'column_count': analysis['column_count']
        },
        'data': [
            {
                'row_index': i,
                'values': {
                    col: row[j] if j < len(row) else ''
                    for j, col in enumerate(analysis['columns'])
                }
            }
            for i, row in enumerate(analysis['data_rows'], 1)
        ]
    }
    
    # 保存为 JSON 文件
    with open('/home/claw/.openclaw/workspace/问卷数据.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nJSON 文件已保存到：/home/claw/.openclaw/workspace/问卷数据.json")

if __name__ == '__main__':
    main()
