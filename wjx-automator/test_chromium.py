#!/usr/bin/env python3
"""
问卷星自动填写系统 - 使用系统 Chromium
无需 webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 问卷统计
question_stats = {
    "1": {"type": "single"},
    "2": {"type": "multiple"},
    "3": {"type": "single"},
    "4": {"type": "multiple"},
    "5": {"type": "single"},
    "6": {"type": "single"},
}

def generate_answer(q_type):
    """生成答案"""
    if 'single' in q_type:
        return random.choice(["1", "2", "3", "4", "5"])
    elif 'multiple' in q_type:
        return f"选项{random.randint(1, 8)}"
    return "默认答案"

# 启动浏览器 - 使用系统 Chromium
logger.info("启动系统 Chromium 浏览器...")
options = Options()
options.binary_location = '/usr/bin/chromium-browser'
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('--window-size=1920,1080')

# 使用系统 chromedriver
chromedriver_path = '/usr/bin/chromium-chromedriver'
logger.info(f"使用 ChromeDriver: {chromedriver_path}")

driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
logger.info("✓ Chromium 启动成功")

try:
    # 打开问卷
    logger.info("打开问卷星页面...")
    driver.get("https://v.wjx.cn/vm/PhfZxRV.aspx")
    time.sleep(5)
    logger.info("✓ 问卷页面加载成功")
    
    # 获取所有题目容器
    containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'field ui-field-contain')]")
    logger.info(f"✓ 找到 {len(containers)} 个题目容器")
    
    # 填充前 6 个题目测试
    success_count = 0
    for i, container in enumerate(containers[:6], 1):
        # 获取题目类型
        q_type_elem = container.get_attribute('type')
        q_type = {'3': 'single', '4': 'multiple', '8': 'scale', '1': 'short_answer'}.get(q_type_elem, 'unknown')
        
        if q_type == 'unknown':
            logger.info(f"Q{i}: 跳过 (type={q_type_elem})")
            continue
            
        logger.info(f"\n--- 填充 Q{i} ({q_type}) ---")
        
        answer = generate_answer(q_type)
        logger.info(f"答案：{answer}")
        
        try:
            if 'single' in q_type:
                # 单选题 - 通过 name 属性查找
                radios = container.find_elements(By.XPATH, f".//input[@name='q{i}']")
                if radios:
                    # 选择第一个或随机选择
                    idx = random.randint(0, len(radios) - 1)
                    driver.execute_script("arguments[0].click();", radios[idx])
                    time.sleep(0.5)
                    logger.info(f"✓ Q{i} 单选成功")
                    success_count += 1
                else:
                    logger.warning(f"Q{i}: 未找到单选按钮")
                    
            elif 'multiple' in q_type:
                # 多选题 - 通过 name 属性查找
                checkboxes = container.find_elements(By.XPATH, f".//input[@name='q{i}']")
                if checkboxes:
                    # 随机选择 1-3 个
                    num_select = min(random.randint(1, 3), len(checkboxes))
                    selected = random.sample(checkboxes, num_select)
                    for checkbox in selected:
                        driver.execute_script("arguments[0].click();", checkbox)
                        time.sleep(0.3)
                    logger.info(f"✓ Q{i} 多选成功 (选择 {num_select} 个)")
                    success_count += 1
                else:
                    logger.warning(f"Q{i}: 未找到多选按钮")
                    
        except Exception as e:
            logger.error(f"Q{i} 填充失败：{e}")
        
        time.sleep(1)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"测试完成：{success_count}/{len(containers[:6])} 个题目填充成功")
    logger.info(f"{'='*60}")
    
    # 测试提交
    logger.info("\n检查提交按钮...")
    try:
        next_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, 'show_next_page')]")
        logger.info(f"✓ 找到下一页按钮")
        logger.info("点击测试...")
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(3)
        logger.info("✓ 下一页功能正常")
    except Exception as e:
        logger.warning(f"未找到下一页按钮：{e}")
    
finally:
    driver.quit()
    logger.info("\n✓ 浏览器已关闭")
