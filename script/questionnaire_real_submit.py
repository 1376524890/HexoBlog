#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷真实提交脚本 (修复版)
问题诊断：之前的脚本只生成了本地记录，没有真正提交到问卷星
"""

import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置
SURVEY_URL = "https://v.wjx.cn/vm/PhfZxRV.aspx"
DATA_FILE = "/home/claw/.openclaw/workspace/output/问卷数据_750 份.json"
WORK_DIR = "/home/claw/.openclaw/workspace/output"

def get_data_file():
    """获取问卷数据文件"""
    files = [f for f in os.listdir(WORK_DIR) if '问卷数据' in f and '.json' in f]
    if files:
        return os.path.join(WORK_DIR, files[0])
    raise FileNotFoundError("未找到问卷数据文件")

def setup_driver():
    """初始化浏览器"""
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
    driver.implicitly_wait(10)
    return driver

def load_survey_data(data_file):
    """加载问卷数据"""
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def analyze_survey_structure(driver):
    """分析问卷结构"""
    print("🔍 分析问卷结构...")
    time.sleep(5)
    
    # 截图查看问卷
    screenshot = os.path.join(WORK_DIR, "问卷结构分析.png")
    driver.save_screenshot(screenshot)
    print(f"✓ 问卷结构截图已保存：{screenshot}")
    
    # 尝试获取所有问题元素
    try:
        # 查找所有可能的输入元素
        inputs = driver.find_elements(By.TAG_NAME, "input")
        selects = driver.find_elements(By.TAG_NAME, "select")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        
        print(f"✓ 找到 {len(inputs)} 个输入框")
        print(f"✓ 找到 {len(selects)} 个下拉框")
        print(f"✓ 找到 {len(textareas)} 个文本域")
        
        # 查找所有问题标题
        questions = driver.find_elements(By.CLASS_NAME, "qm-title")
        print(f"✓ 找到 {len(questions)} 个问题")
        
        # 打印前几个问题的文本
        print("\n=== 问题列表 (前 10 个) ===")
        for i, q in enumerate(questions[:10]):
            text = q.text[:100] if q.text else "无标题"
            print(f"{i+1}. {text}...")
        
        return True
    except Exception as e:
        print(f"⚠ 获取问卷结构失败：{e}")
        return False

def find_and_fill_question(driver, question_text, answer_value):
    """根据问题文本找到并填写答案"""
    print(f"📝 尝试填写：{question_text}")
    
    try:
        # 方案 1: 通过问题文本定位
        xpath = f"//*[contains(text(), '{question_text}')]//following::*[contains(text(), '{answer_value}')]//input[@type='radio']"
        radio = driver.find_element(By.XPATH, xpath)
        if not radio.is_selected():
            radio.click()
            print(f"✓ 已选择：{answer_value}")
            return True
        
        # 方案 2: 通过选项文本直接点击
        option_text = f"//*[contains(text(), '{answer_value}')]//ancestor::div[contains(@class, 'option') or contains(@class, 'choice') or contains(@class, 'item')]"
        option = driver.find_element(By.XPATH, option_text)
        driver.execute_script("arguments[0].click();", option)
        print(f"✓ 已点击选项：{answer_value}")
        return True
        
    except Exception as e:
        print(f"✗ 填写失败：{e}")
        return False

def submit_survey(driver):
    """提交问卷"""
    print("🚀 尝试提交问卷...")
    
    try:
        # 查找提交按钮
        submit_buttons = [
            driver.find_elements(By.XPATH, "//*[contains(text(), '提交')]"),
            driver.find_elements(By.XPATH, "//*[contains(text(), '提交答案')]"),
            driver.find_elements(By.XPATH, "//*[contains(text(), '交卷')]"),
            driver.find_elements(By.XPATH, "//*[contains(text(), 'Next')]"),
            driver.find_elements(By.CLASS_NAME, "form-control-btn"),
            driver.find_elements(By.CSS_SELECTOR, "button[type='submit']"),
        ]
        
        for btns in submit_buttons:
            if btns:
                print(f"✓ 找到提交按钮，点击最后一个...")
                btns[-1].click()
                time.sleep(3)
                
                # 检查是否提交成功
                success_text = driver.page_source.lower()
                if "success" in success_text or "提交成功" in success_text or "thank" in success_text:
                    print("✅ 问卷提交成功！")
                    return True
                
                # 检查是否有确认弹窗
                try:
                    WebDriverWait(driver, 2).until(EC.alert_is_present())
                    driver.switch_to.alert.accept()
                    print("✓ 已确认提交")
                    return True
                except:
                    pass
        
        print("⚠ 未找到提交按钮，可能需要手动翻页")
        return False
        
    except Exception as e:
        print(f"✗ 提交失败：{e}")
        return False

def main():
    print("="*70)
    print("🚀 御坂妹妹 11 号 - 问卷真实提交脚本 (修复版)")
    print("="*70)
    
    # 获取数据文件
    data_file = get_data_file()
    print(f"📊 数据文件：{data_file}")
    
    # 加载数据
    data = load_survey_data(data_file)
    total = len(data)
    print(f"📋 总样本数：{total}")
    
    # 初始化浏览器
    print("\n🔧 初始化浏览器...")
    driver = setup_driver()
    
    try:
        # 打开问卷页面
        print(f"🌐 打开问卷页面...")
        driver.get(SURVEY_URL)
        
        # 分析问卷结构
        analyze_survey_structure(driver)
        
        # 尝试填写前 3 份问卷
        print(f"\n📝 开始填写前 3 份问卷作为测试...")
        
        for i in range(min(3, total)):
            print(f"\n{'='*70}")
            print(f"填写问卷 {i+1}/{min(3, total)}")
            print(f"{'='*70}")
            
            record = data[i]
            
            # 尝试填写每个字段
            for key, value in list(record.items())[:10]:  # 只处理前 10 个字段
                if isinstance(value, str) and value and len(value) < 100:
                    find_and_fill_question(driver, key, value)
                    time.sleep(1)
            
            # 提交
            submit_survey(driver)
            
            # 等待 30 秒再开始下一份
            print(f"⏱ 等待 30 秒...")
            time.sleep(30)
        
        print(f"\n{'='*70}")
        print("✅ 测试完成！请检查问卷星后台是否显示新提交")
        print(f"{'='*70}")
        
        # 保持浏览器打开
        time.sleep(60)
        
    except Exception as e:
        print(f"\n❌ 执行错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\n👋 浏览器已关闭")

if __name__ == "__main__":
    main()
