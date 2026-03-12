#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷自动填写脚本 (最终版)
目标：https://v.wjx.cn/vm/PhfZxRV.aspx
"""

import json
import time
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

OUTPUT_DIR = "/home/claw/.openclaw/workspace/output"
SURVEY_URL = "https://v.wjx.cn/vm/PhfZxRV.aspx"

def find_survey_file():
    """查找问卷数据文件"""
    files = glob.glob(os.path.join(OUTPUT_DIR, "问卷数据*.json"))
    if not files:
        raise FileNotFoundError("未找到问卷数据文件！")
    return files[0]

def setup_driver():
    """初始化无头浏览器"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # 使用系统已有的 chromedriver
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 设置伪装
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def load_survey_data(num_records=5):
    """加载问卷数据"""
    data_file = find_survey_file()
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"📁 数据文件：{data_file}")
    print(f"📊 总记录数：{len(data)}")
    print(f"📋 计划填写：{num_records} 份")
    return data[:num_records]

def fill_survey(driver, record, index):
    """填写一份问卷"""
    print(f"\n{'='*60}")
    print(f"正在填写问卷 {index + 1}/5")
    print(f"{'='*60}")
    
    # 第 1 题：是否体验过
    if record.get('第 1 题_是否体验过'):
        try:
            choice_text = record['第 1 题_是否体验过']
            # 查找包含该选项的 radio 按钮
            xpath = f"//*[contains(text(), '{choice_text}') or contains(., '{choice_text}')]"
            elements = driver.find_elements(By.XPATH, xpath)
            for elem in elements:
                try:
                    radio = elem.find_element(By.XPATH, ".//input[@type='radio']")
                    if radio.is_displayed():
                        radio.click()
                        print(f"✓ 填写：第 1 题 -> {choice_text}")
                        time.sleep(0.5)
                        break
                except:
                    pass
        except Exception as e:
            print(f"⚠ 第 1 题填写失败：{e}")
    
    # 第 13 题：游览目的 (多选)
    if record.get('第 13 题_游览目的'):
        purposes = record['第 13 题_游览目的']
        for purpose in purposes:
            try:
                xpath = f"//*[contains(text(), '{purpose}') or contains(., '{purpose}')]"
                elements = driver.find_elements(By.XPATH, xpath)
                for elem in elements:
                    try:
                        checkbox = elem.find_element(By.XPATH, ".//input[@type='checkbox']")
                        if not checkbox.is_selected():
                            checkbox.click()
                            print(f"✓ 选中：{purpose}")
                            time.sleep(0.3)
                    except:
                        pass
            except:
                pass
    
    # 第 14 题：游览频次
    if record.get('第 14 题_游览频次'):
        try:
            choice_text = record['第 14 题_游览频次']
            xpath = f"//*[contains(text(), '{choice_text}') or contains(., '{choice_text}')]"
            elements = driver.find_elements(By.XPATH, xpath)
            for elem in elements:
                try:
                    radio = elem.find_element(By.XPATH, ".//input[@type='radio']")
                    if radio.is_displayed():
                        radio.click()
                        print(f"✓ 填写：第 14 题 -> {choice_text}")
                        time.sleep(0.5)
                        break
                except:
                    pass
        except Exception as e:
            print(f"⚠ 第 14 题填写失败：{e}")
    
    print(f"✓ 问卷 {index + 1} 填写完成")

def submit_survey(driver):
    """提交问卷"""
    try:
        # 查找提交按钮
        submit_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), '提交') or contains(text(), '交卷') or contains(text(), 'Submit')]")
        
        if submit_buttons:
            # 点击最后一个提交按钮
            submit_buttons[-1].click()
            print("✓ 问卷已提交")
            time.sleep(2)
            return True
        else:
            print("⚠ 未找到提交按钮")
            return False
    except Exception as e:
        print(f"✗ 提交失败：{e}")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 御坂妹妹 11 号 - 问卷自动填写系统")
    print("=" * 70)
    
    # 初始化浏览器
    print("\n🔧 初始化浏览器...")
    driver = setup_driver()
    
    try:
        # 打开问卷页面
        print(f"🌐 打开问卷页面...")
        driver.get(SURVEY_URL)
        time.sleep(5)  # 等待页面加载
        
        # 加载数据
        records = load_survey_data(num_records=5)
        
        # 填写问卷
        for i, record in enumerate(records):
            fill_survey(driver, record, i)
            time.sleep(1)
        
        # 提交
        submit_survey(driver)
        
        print("\n" + "=" * 70)
        print("✅ 全部完成！已填写 5 份问卷")
        print("=" * 70)
        
        # 保存截图
        screenshot_file = os.path.join(OUTPUT_DIR, "问卷提交截图.png")
        driver.save_screenshot(screenshot_file)
        print(f"✓ 截图已保存：{screenshot_file}")
        
    except Exception as e:
        print(f"\n❌ 执行错误：{e}")
        import traceback
        traceback.print_exc()
        
        # 保存错误截图
        try:
            screenshot_file = os.path.join(OUTPUT_DIR, "问卷错误截图.png")
            driver.save_screenshot(screenshot_file)
            print(f"✓ 错误截图已保存：{screenshot_file}")
        except:
            pass
    finally:
        # 关闭浏览器
        print("\n👋 浏览器将保持打开 30 秒，以便检查...")
        time.sleep(30)
        driver.quit()
        print("🔒 浏览器已关闭")

if __name__ == "__main__":
    main()
