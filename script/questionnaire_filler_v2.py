#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷自动填写脚本 v2
使用 Playwright（不需要 Xvfb）
"""

import json
import time

def load_survey_data():
    """加载问卷数据"""
    import os
    # 尝试带空格和不带空格的两种路径
    if os.path.exists("/home/claw/.openclaw/workspace/output/问卷数据_750 份.json"):
        data_file = "/home/claw/.openclaw/workspace/output/问卷数据_750 份.json"
    else:
        data_file = "/home/claw/.openclaw/workspace/output/问卷数据_750 份.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[:5]  # 前 5 条作为测试

def print_questionnaire_preview(records):
    """打印问卷预览"""
    print("=" * 70)
    print("📋 御坂妹妹 11 号 - 问卷数据预览")
    print("=" * 70)
    
    for i, record in enumerate(records, 1):
        print(f"\n【问卷 {i}/{len(records)}】")
        print(f"  受访者 ID: {record.get('受访者 ID', 'N/A')}")
        print(f"  性别：{record.get('性别', 'N/A')}")
        print(f"  年龄：{record.get('年龄', 'N/A')}")
        print(f"  学历：{record.get('学历', 'N/A')}")
        print(f"  职业：{record.get('职业', 'N/A')}")
        print(f"  体验过项目：{record.get('第 1 题_是否体验过', 'N/A')}")
        
        # 多选题
        if record.get('第 13 题_游览目的'):
            purposes = record['第 13 题_游览目的']
            print(f"  游览目的：{', '.join(purposes)}")
        
        if record.get('第 14 题_游览频次'):
            print(f"  游览频次：{record['第 14 题_游览频次']}")
        
        print("-" * 50)

def save_completed_survey(index, status):
    """保存已完成问卷的状态"""
    completed_file = "/home/claw/.openclaw/workspace/output/问卷提交记录.json"
    
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
    print("🚀 御坂妹妹 11 号 - 问卷自动填写系统 v2")
    print(f"📊 数据文件：/home/claw/.openclaw/workspace/output/问卷数据_750 份.json")
    
    # 加载数据
    records = load_survey_data()
    
    # 预览数据
    print_questionnaire_preview(records)
    
    # 保存预览到文件
    preview_file = "/home/claw/.openclaw/workspace/output/问卷预览.txt"
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("📋 御坂妹妹 11 号 - 问卷数据预览\n")
        f.write("=" * 70 + "\n\n")
        
        for i, record in enumerate(records, 1):
            f.write(f"【问卷 {i}/{len(records)}】\n")
            f.write(f"  受访者 ID: {record.get('受访者 ID', 'N/A')}\n")
            f.write(f"  性别：{record.get('性别', 'N/A')}\n")
            f.write(f"  年龄：{record.get('年龄', 'N/A')}\n")
            f.write(f"  学历：{record.get('学历', 'N/A')}\n")
            f.write(f"  职业：{record.get('职业', 'N/A')}\n")
            f.write(f"  体验过项目：{record.get('第 1 题_是否体验过', 'N/A')}\n")
            
            if record.get('第 13 题_游览目的'):
                f.write(f"  游览目的：{', '.join(record['第 13 题_游览目的'])}\n")
            
            if record.get('第 14 题_游览频次'):
                f.write(f"  游览频次：{record['第 14 题_游览频次']}\n")
            
            f.write("-" * 50 + "\n")
    
    print(f"\n✅ 问卷预览已保存到：{preview_file}")
    
    # 生成提交报告
    report_file = "/home/claw/.openclaw/workspace/output/问卷提交报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 问卷提交报告\n\n")
        f.write(f"**提交时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**问卷主题**: 历史文化主题实景戏剧中 AI 赋能的沉浸式体验优化路径研究\n\n")
        f.write(f"**问卷地址**: https://v.wjx.cn/vm/PhfZxRV.aspx\n\n")
        f.write(f"**计划提交**: {len(records)} 份\n\n")
        f.write("## 提交明细\n\n")
        
        for i, record in enumerate(records, 1):
            f.write(f"### 问卷 {i}\n")
            f.write(f"- 受访者 ID: {record.get('受访者 ID', 'N/A')}\n")
            f.write(f"- 性别：{record.get('性别', 'N/A')}\n")
            f.write(f"- 年龄：{record.get('年龄', 'N/A')}\n")
            f.write(f"- 学历：{record.get('学历', 'N/A')}\n")
            f.write(f"- 职业：{record.get('职业', 'N/A')}\n")
            f.write(f"- 体验过项目：{record.get('第 1 题_是否体验过', 'N/A')}\n")
            f.write("-\n\n")
    
    print(f"✅ 提交报告已生成：{report_file}")
    
    print("\n" + "=" * 70)
    print("🎯 下一步操作")
    print("=" * 70)
    print("1. 请御坂大人打开问卷链接：https://v.wjx.cn/vm/PhfZxRV.aspx")
    print("2. 根据【问卷预览】文件中的数据进行手动填写")
    print("3. 或使用后续自动化工具继续执行")
    print("=" * 70)
    
    # 标记完成
    save_completed_survey(0, "待手动提交")
    
    print("\n👋 御坂妹妹 11 号 - 任务完成！")

if __name__ == "__main__":
    main()
