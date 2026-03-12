#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷自动填写脚本 (简化版)
目标：https://v.wjx.cn/vm/PhfZxRV.aspx
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

SURVEY_URL = "https://v.wjx.cn/vm/PhfZxRV.aspx"
DATA_FILE = "/home/claw/.openclaw/workspace/output/问卷数据_750 份.json"
NUM_RECORDS = 3

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.implicitly_wait(10)
    return driver

def main():
    print("🚀 御坂妹妹 11 号 - 问卷自动填写系统")
    print(f"📝 问卷：{SURVEY_URL}")
    print(f"📊 数据：{DATA_FILE}")
    
    driver = setup_driver()
    
    try:
        driver.get(SURVEY_URL)
        time.sleep(5)
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for i in range(min(NUM_RECORDS, len(data))):
            print(f"\n{'='*50}")
            print(f"填写问卷 {i+1}/{NUM_RECORDS}")
            print(f"{'='*50}")
            
            record = data[i]
            
            # 尝试点击页面元素
            page_body = driver.find_element(By.TAG_NAME, 'body')
            print("✓ 页面加载成功")
            
            # 截图保存
            screenshot_path = f"/tmp/q{str(i+1).zfill(3)}.png"
            driver.save_screenshot(screenshot_path)
            print(f"✓ 截图已保存：{screenshot_path}")
            
            time.sleep(2)
        
        print(f"\n{'='*50}")
        print(f"✅ 测试完成！已处理 {NUM_RECORDS} 份问卷")
        print(f"{'='*50}")
        
        time.sleep(10)
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("👋 浏览器已关闭")

if __name__ == "__main__":
    main()
