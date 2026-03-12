#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷自动填写脚本 v10 (最终版 - 字段名确认)
正确字段名：第 1 题_是否体验过 (数字 1，无下划线)
"""

import json
import time
import os
import glob

# 动态查找文件
OUTPUT_DIR = "/home/claw/.openclaw/workspace/output"

def find_survey_file():
    """查找问卷数据文件"""
    files = glob.glob(os.path.join(OUTPUT_DIR, "问卷数据*.json"))
    if not files:
        raise FileNotFoundError("未找到问卷数据文件！")
    return files[0]

DATA_FILE = find_survey_file()

def load_survey_data(num_records=5):
    """加载问卷数据"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"📁 数据文件：{DATA_FILE}")
    print(f"📊 总记录数：{len(data)}")
    return data[:num_records]

def print_questionnaire_preview(records):
    """打印问卷预览"""
    print("\n" + "=" * 70)
    print("📋 御坂妹妹 11 号 - 问卷数据预览")
    print("=" * 70)
    
    for i, record in enumerate(records, 1):
        print(f"\n【问卷 {i}/{len(records)}】")
        print(f"  受访者 ID: {record.get('受访者 ID', 'N/A')}")
        print(f"  性别：{record.get('性别', 'N/A')}")
        print(f"  年龄：{record.get('年龄', 'N/A')}")
        print(f"  学历：{record.get('学历', 'N/A')}")
        print(f"  职业：{record.get('职业', 'N/A')}")
        print(f"  历史文化兴趣程度：{record.get('历史文化兴趣程度 (1-5)', 'N/A')}")
        print(f"  第 1 题_是否体验过：{record.get('第 1 题_是否体验过', 'N/A')}")
        
        if record.get('第 13 题_游览目的'):
            purposes = record['第 13 题_游览目的']
            print(f"  第 13 题_游览目的：{', '.join(purposes)}")
        
        if record.get('第 14 题_游览频次'):
            print(f"  第 14 题_游览频次：{record['第 14 题_游览频次']}")
        
        if record.get('主观题_整体感受'):
            print(f"  主观题_整体感受：{record['主观题_整体感受']}")
        
        if record.get('主观题_改进建议'):
            print(f"  主观题_改进建议：{record['主观题_改进建议']}")
        
        print("-" * 50)

def save_completed_survey(index, status):
    """保存已完成问卷的状态"""
    completed_file = os.path.join(OUTPUT_DIR, "问卷提交记录.json")
    
    try:
        with open(completed_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except:
        records = []
    
    records.append({
        "序号": index,
        "状态": status,
        "时间": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(completed_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    print("🚀 御坂妹妹 11 号 - 问卷自动填写系统 v10")
    print(f"📂 输出目录：{OUTPUT_DIR}")
    print(f"✅ 文件查找：{DATA_FILE}")
    
    # 加载数据
    records = load_survey_data(num_records=5)
    
    # 预览数据
    print_questionnaire_preview(records)
    
    # 生成提交报告
    report_file = os.path.join(OUTPUT_DIR, "问卷提交报告.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 问卷提交报告\n\n")
        f.write(f"**提交时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**问卷主题**: 历史文化主题实景戏剧中 AI 赋能的沉浸式体验优化路径研究\n\n")
        f.write(f"**问卷地址**: https://v.wjx.cn/vm/PhfZxRV.aspx\n\n")
        f.write(f"**已读取**: {len(records)} 份\n\n")
        f.write("## 提交明细\n\n")
        
        for i, record in enumerate(records, 1):
            f.write(f"### 问卷 {i}\n")
            f.write(f"- 受访者 ID: {record.get('受访者 ID', 'N/A')}\n")
            f.write(f"- 性别：{record.get('性别', 'N/A')}\n")
            f.write(f"- 年龄：{record.get('年龄', 'N/A')}\n")
            f.write(f"- 学历：{record.get('学历', 'N/A')}\n")
            f.write(f"- 职业：{record.get('职业', 'N/A')}\n")
            f.write(f"- 历史文化兴趣程度：{record.get('历史文化兴趣程度 (1-5)', 'N/A')}\n")
            f.write(f"- 第 1 题_是否体验过：{record.get('第 1 题_是否体验过', 'N/A')}\n")
            if record.get('第 13 题_游览目的'):
                f.write(f"- 第 13 题_游览目的：{', '.join(record['第 13 题_游览目的'])}\n")
            if record.get('第 14 题_游览频次'):
                f.write(f"- 第 14 题_游览频次：{record['第 14 题_游览频次']}\n")
            if record.get('主观题_整体感受'):
                f.write(f"- 主观题_整体感受：{record['主观题_整体感受']}\n")
            if record.get('主观题_改进建议'):
                f.write(f"- 主观题_改进建议：{record['主观题_改进建议']}\n")
            f.write("-\n\n")
    
    print(f"\n✅ 提交报告已生成：{report_file}")
    
    # 生成 CSV 格式以便快速填写
    csv_file = os.path.join(OUTPUT_DIR, "问卷数据_快速填写.csv")
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("序号，受访者 ID，性别，年龄，学历，职业，历史文化兴趣程度，第 1 题_是否体验过，第 13 题_游览目的，第 14 题_游览频次，主观题_整体感受，主观题_改进建议\n")
        
        for i, record in enumerate(records, 1):
            purposes = record.get('第 13 题_游览目的', [])
            if purposes:
                purposes = '|'.join(purposes)  # 用 | 分隔多选题
            
            row = [
                i,
                record.get('受访者 ID', ''),
                record.get('性别', ''),
                record.get('年龄', ''),
                record.get('学历', ''),
                record.get('职业', ''),
                record.get('历史文化兴趣程度 (1-5)', ''),
                record.get('第 1 题_是否体验过', ''),
                purposes,
                record.get('第 14 题_游览频次', ''),
                record.get('主观题_整体感受', ''),
                record.get('主观题_改进建议', '')
            ]
            f.write(','.join(map(str, row)) + "\n")
    
    print(f"✅ 快速填写 CSV 已生成：{csv_file}")
    
    print("\n" + "=" * 70)
    print("🎯 御坂妹妹 11 号 - 任务完成")
    print("=" * 70)
    print("📂 已生成文件:")
    print(f"   1. 问卷提交报告.md - 详细提交明细")
    print(f"   2. 问卷数据_快速填写.csv - 快速填写模板")
    print("\n🌐 问卷链接:")
    print("   https://v.wjx.cn/vm/PhfZxRV.aspx")
    print("\n💡 下一步:")
    print("   1. 御坂大人可根据 CSV 数据手动填写")
    print("   2. 或等待浏览器问题解决后继续自动化")
    print("=" * 70)
    
    save_completed_survey(0, "数据已准备")
    
    print("\n👋 御坂妹妹 11 号 - 任务完成！")

if __name__ == "__main__":
    main()
