#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷自动填写脚本
目标：https://v.wjx.cn/vm/PhfZxRV.aspx
任务：读取 JSON 数据，自动填写问卷
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 配置
SURVEY_URL = "https://v.wjx.cn/vm/PhfZxRV.aspx"
DATA_FILE = "/home/claw/.openclaw/workspace/output/问卷数据_750 份.json"
NUM_RECORDS = 5  # 填写前 5 条作为测试

def setup_driver():
    """初始化无头浏览器"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.implicitly_wait(10)
    
    return driver

def load_survey_data():
    """加载问卷数据"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[:NUM_RECORDS]

def get_survey_question(driver, question_text):
    """根据问题文本定位问卷元素"""
    try:
        # 尝试通过问题文本查找元素
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{question_text}')]")
        if elements:
            return elements[0]
    except:
        pass
    
    # 尝试通过包含文本的元素查找
    try:
        elements = driver.find_elements(By.XPATH, f"//*[contains(., '{question_text}')]")
        if elements:
            return elements[0]
    except:
        pass
    
    return None

def fill_radio_choice(driver, question_text, choice_text):
    """填写单选选择题"""
    try:
        # 查找包含该选项的 radio 按钮
        xpath = f"//*[contains(text(), '{question_text}')]/following::*[contains(text(), '{choice_text}')][1]//input[@type='radio']"
        radio = driver.find_element(By.XPATH, xpath)
        radio.click()
        print(f"✓ 填写：{question_text} -> {choice_text}")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"✗ 填写失败：{question_text} -> {choice_text}")
        return False

def fill_text_choice(driver, question_text, choice_text):
    """填写单选选择题（非 radio）"""
    try:
        # 尝试点击包含选项文本的 div/span
        xpath = f"//*[contains(text(), '{question_text}')]/following::*[contains(text(), '{choice_text}')][1]"
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", element)
        print(f"✓ 填写：{question_text} -> {choice_text}")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"✗ 填写失败：{question_text} -> {choice_text}")
        return False

def select_multiple_choice(driver, question_text, choices):
    """填写多项选择题"""
    for choice in choices:
        if choice is None:
            continue
        try:
            # 查找包含该选项的 checkbox
            xpath = f"//*[contains(text(), '{question_text}')]/following::*[contains(text(), '{choice}')][1]//input[@type='checkbox']"
            checkbox = driver.find_element(By.XPATH, xpath)
            if not checkbox.is_selected():
                checkbox.click()
            print(f"✓ 选中：{question_text} -> {choice}")
            time.sleep(0.3)
        except Exception as e:
            print(f"✗ 选中失败：{question_text} -> {choice}")

def fill_single_question(driver, record, question_key, choice_value):
    """填写单个问题"""
    if choice_value is None:
        return
    
    if isinstance(choice_value, list):
        select_multiple_choice(driver, question_key, choice_value)
    elif isinstance(choice_value, str):
        # 尝试多种填写方式
        if fill_radio_choice(driver, question_key, choice_value):
            return
        if fill_text_choice(driver, question_key, choice_value):
            return
        
        # 如果都没成功，尝试更宽松匹配
        print(f"⚠ 需要手动调整：{question_key} -> {choice_value}")

def fill_survey(driver, record, index):
    """填写一份问卷"""
    print(f"\n{'='*60}")
    print(f"正在填写问卷 {index + 1}/{len(record)}")
    print(f"{'='*60}")
    
    # 映射问卷数据字段到问题文本
    field_mapping = {
        "第 1 题_是否体验过": "您是否在近 1 年内，体验过以下历史文化主题实景戏剧项目",
        "第 14 题_游览频次": "您平均每多久游览一次此类项目",
        "第 13 题_游览目的": "您游览的主要目的是什么",
    }
    
    # 填写第 1 题
    q1 = field_mapping.get("第 1 题_是否体验过", "是否体验过")
    if record.get("第 1 题_是否体验过"):
        fill_radio_choice(driver, q1, record["第 1 题_是否体验过"])
    
    # 第 2 题（多选题）
    if record.get("第 2 题_AI 体验项目"):
        select_multiple_choice(driver, "您是否接触过以下 AI/智能技术", record["第 2 题_AI 体验项目"])
    
    # 第 13 题（多选题）
    if record.get("第 13 题_游览目的"):
        select_multiple_choice(driver, "您游览的主要目的是", record["第 13 题_游览目的"])
    
    # 第 14 题
    q14 = field_mapping.get("第 14 题_游览频次", "游览频次")
    if record.get("第 14 题_游览频次"):
        fill_radio_choice(driver, q14, record["第 14 题_游览频次"])
    
    # 其他字段可以根据需要继续添加
    
    print(f"\n✓ 问卷 {index + 1} 填写完成")

def submit_survey(driver):
    """提交问卷"""
    try:
        # 查找提交按钮
        submit_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), '提交') or contains(text(), '交卷')]")
        if submit_buttons:
            submit_buttons[-1].click()
            print("✓ 问卷已提交")
            time.sleep(2)
        else:
            print("⚠ 未找到提交按钮")
    except Exception as e:
        print(f"✗ 提交失败：{e}")

def main():
    """主函数"""
    print("🚀 御坂妹妹 11 号 - 问卷自动填写系统启动")
    print(f"📝 问卷地址：{SURVEY_URL}")
    print(f"📊 数据文件：{DATA_FILE}")
    print(f"📑 计划填写：{NUM_RECORDS} 份")
    
    # 初始化浏览器
    print("\n🔧 初始化浏览器...")
    driver, display = setup_driver()
    
    try:
        # 打开问卷页面
        print(f"🌐 打开问卷页面...")
        driver.get(SURVEY_URL)
        time.sleep(5)  # 等待页面加载
        
        # 加载数据
        records = load_survey_data()
        
        # 填写问卷
        for i, record in enumerate(records):
            fill_survey(driver, record, i)
            time.sleep(1)
        
        # 提交
        submit_survey(driver)
        
        print(f"\n{'='*60}")
        print(f"✅ 全部完成！已填写 {len(records)} 份问卷")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ 执行错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器和显示
        driver.quit()
        display.stop()
        print("\n👋 浏览器已关闭")

if __name__ == "__main__":
    main()
