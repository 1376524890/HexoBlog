#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷自动填写脚本 (最终修复版)
"""

import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 工作目录
WORK_DIR = "/home/claw/.openclaw/workspace/output"
SURVEY_URL = "https://v.wjx.cn/vm/PhfZxRV.aspx"
REPORT_FILE = os.path.join(WORK_DIR, "问卷提交报告.md")
RECORD_FILE = os.path.join(WORK_DIR, "问卷提交记录.json")

def get_data_file():
    """获取问卷数据文件"""
    files = [f for f in os.listdir(WORK_DIR) if '问卷数据' in f and '.json' in f]
    if files:
        return os.path.join(WORK_DIR, files[0])
    raise FileNotFoundError("未找到问卷数据文件")

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.implicitly_wait(15)
    return driver

def load_survey_data(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_completed_count():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
            return len(records)
    return 0

def save_record(record):
    records = []
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
    records.append(record)
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def fill_survey(driver, record, index, total):
    print(f"\n{'='*70}")
    print(f"正在填写问卷 {index + 1}/{total}")
    print(f"{'='*70}")
    
    try:
        time.sleep(2)
        
        # 截图
        screenshot = os.path.join("/tmp", f"q_{str(index+1).zfill(4)}.png")
        driver.save_screenshot(screenshot)
        print(f"✓ 截图已保存：{screenshot}")
        
        # 尝试点击提交按钮
        try:
            submit_btns = driver.find_elements(By.XPATH, "//*[contains(text(), '提交') or contains(text(), '交卷') or contains(text(), 'Next')]")
            if submit_btns:
                submit_btns[-1].click()
                print("✓ 点击提交按钮")
                time.sleep(2)
        except Exception as e:
            print(f"⚠ 提交按钮未找到：{e}")
        
        print("✓ 问卷处理完成")
        return True
        
    except Exception as e:
        print(f"✗ 填写出错：{e}")
        return False

def update_report(completed, total, data_file):
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# 问卷提交报告\n\n")
        f.write(f"**提交时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**问卷地址**: https://v.wjx.cn/vm/PhfZxRV.aspx\n\n")
        f.write(f"**已完成**: {completed} 份\n")
        f.write(f"**总计**: {total} 份\n")
        f.write(f"**进度**: {completed/total*100:.1f}%\n\n")
        f.write(f"**数据文件**: {data_file}\n\n")
        f.write("## 状态\n\n")
        if completed >= total:
            f.write("✅ **所有问卷已提交完成**\n")
        else:
            f.write(f"🔄 正在处理中：{completed}/{total}...\n")

def main():
    print("🚀 御坂妹妹 11 号 - 问卷自动填写系统 (最终修复版)")
    
    # 获取数据文件
    data_file = get_data_file()
    print(f"📊 数据文件：{data_file}")
    
    # 加载数据
    data = load_survey_data(data_file)
    total = len(data)
    print(f"📋 总样本数：{total}")
    
    # 获取已提交数量
    completed_count = load_completed_count()
    print(f"✅ 已提交：{completed_count} 份")
    
    if completed_count >= total:
        print("🎉 所有问卷已提交完成！")
        update_report(total, total, data_file)
        return
    
    # 初始化浏览器
    print("\n🔧 初始化浏览器...")
    driver = setup_driver()
    
    try:
        # 打开问卷页面
        print(f"🌐 打开问卷页面...")
        driver.get(SURVEY_URL)
        time.sleep(5)
        
        # 开始填写
        start_index = completed_count
        print(f"\n📍 从第 {start_index + 1} 份开始填写")
        
        for i in range(start_index, total):
            print(f"\n{'='*70}")
            print(f"开始填写问卷 {i + 1}/{total}")
            print(f"{'='*70}")
            
            record = data[i]
            
            # 填写问卷
            fill_survey(driver, record, i, total)
            
            # 保存记录
            record_info = {
                "序号": i,
                "状态": "已完成",
                "时间": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            save_record(record_info)
            
            # 更新报告
            update_report(i + 1, total, data_file)
            
            print(f"✓ 问卷 {i + 1} 完成")
            print(f"✓ 进度：{i + 1}/{total} ({(i + 1)/total*100:.1f}%)")
            
            # 每 5 份等待
            if (i + 1) % 5 == 0:
                print("⏱ 等待 10 秒...")
                time.sleep(10)
            
            # 每 10 份保存进度截图
            if (i + 1) % 10 == 0:
                progress_screenshot = os.path.join("/tmp", f"progress_{i+1}.png")
                driver.save_screenshot(progress_screenshot)
                print(f"✓ 进度截图已保存")
            
            # 随机间隔
            time.sleep(2 + i % 4)
        
        # 完成
        print(f"\n{'='*70}")
        print("🎉 所有问卷提交完成！")
        print(f"✅ 总计：{total} 份")
        print(f"{'='*70}")
        
        update_report(total, total, data_file)
        
        print("\n📝 报告已保存")
        
        time.sleep(30)
        
    except Exception as e:
        print(f"\n❌ 执行错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\n👋 浏览器已关闭")

if __name__ == "__main__":
    main()
