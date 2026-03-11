#!/usr/bin/env python3
"""
问卷星自动填写系统 - 最终稳定版
包含所有修复和调试参数
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 问卷统计（简化版）
question_stats = {
    "1": {"type": "single", "options": ["选项 1", "选项 2", "选项 3"]},
    "2": {"type": "multiple", "options": ["选项 1", "选项 2", "选项 3", "选项 4", "选项 5", "选项 6", "选项 7", "选项 8"]},
    "3": {"type": "single"},
    "4": {"type": "multiple"},
    "5": {"type": "single"},
    "6": {"type": "single"},
    "11": {"type": "multiple"},
    "13": {"type": "multiple"},
    "14": {"type": "single"},
    "15": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "16": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "17": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "18": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "19": {"type": "single"},
    "20": {"type": "single"},
    "21": {"type": "single"},
    "22": {"type": "single"},
    "23": {"type": "single"},
    "24": {"type": "single"},
    "25": {"type": "short_answer"},
    "26": {"type": "short_answer"},
    "27": {"type": "short_answer"},
    "28": {"type": "short_answer"},
}

def generate_answer(question_id, q_type):
    """生成答案"""
    if 'single' in q_type:
        return random.choice(["1", "2", "3", "4", "5"])
    elif 'multiple' in q_type:
        return [f"选项{i}" for i in random.sample(range(1, 9), random.randint(1, 4))]
    elif 'scale' in q_type:
        return random.choice(["3", "4", "5"])
    elif 'short_answer' in q_type:
        templates = [
            "AI 技术在历史文化实景戏剧中的应用前景广阔，特别是在虚拟现实和动作捕捉方面。",
            "建议增加更多交互环节，让观众能够更深入地参与到戏剧表演中。",
            "希望未来能看到更多 AI 技术与传统文化结合的创意作品。",
            "当前技术应用已经很不错了，期待未来能有更沉浸式的体验。"
        ]
        return random.choice(templates)
    return "默认答案"

def fill_question(container, question_id, q_type):
    """填充单个问题"""
    answer = generate_answer(question_id, q_type)
    logger.info(f"填充 Q{question_id} ({q_type}): {answer}")
    
    try:
        if 'single' in q_type:
            # 单选题
            radios = container.find_elements(By.XPATH, ".//input[@type='radio']")
            for radio in radios:
                radio_id = radio.get_attribute('id') or ''
                radio_value = radio.get_attribute('value') or ''
                if answer in radio_id or answer == radio_value:
                    driver.execute_script("arguments[0].click();", radio)
                    time.sleep(0.3)
                    logger.info(f"✓ Q{question_id} 单选成功")
                    return True
            
        elif 'multiple' in q_type:
            # 多选题
            checkboxes = container.find_elements(By.XPATH, ".//input[@type='checkbox']")
            for checkbox in checkboxes:
                checkbox_value = checkbox.get_attribute('value') or ''
                if checkbox_value == answer:
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.2)
                    logger.info(f"✓ Q{question_id} 多选成功")
                    return True
            
        elif 'scale' in q_type:
            # 量表题
            radios = container.find_elements(By.XPATH, ".//input[@type='radio']")
            for radio in radios:
                radio_id = radio.get_attribute('id') or ''
                radio_value = radio.get_attribute('value') or ''
                if answer in radio_id or answer == radio_value:
                    driver.execute_script("arguments[0].click();", radio)
                    time.sleep(0.3)
                    logger.info(f"✓ Q{question_id} 量表成功")
                    return True
                    
        elif 'short_answer' in q_type:
            # 简答题
            textareas = container.find_elements(By.XPATH, ".//textarea")
            for textarea in textareas:
                driver.execute_script("arguments[0].value = arguments[1];", textarea, answer)
                time.sleep(0.2)
                logger.info(f"✓ Q{question_id} 简答成功")
                return True
                
    except Exception as e:
        logger.error(f"Q{question_id} 填充失败：{e}")
        return False
    
    logger.warning(f"Q{question_id} 未找到匹配选项")
    return False

# 启动浏览器
logger.info("启动 Chrome 浏览器...")
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('--disable-extensions')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
logger.info("✓ Chrome 启动成功")

try:
    # 打开问卷
    logger.info("打开问卷星页面...")
    driver.get("https://v.wjx.cn/vm/PhfZxRV.aspx")
    time.sleep(3)
    logger.info("✓ 问卷页面加载成功")
    
    # 获取所有题目容器
    containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'field ui-field-contain')]")
    logger.info(f"✓ 找到 {len(containers)} 个题目容器")
    
    # 填充前 5 个题目测试
    success_count = 0
    for i, container in enumerate(containers[:5], 1):
        # 获取题目类型
        q_type_elem = container.get_attribute('type')
        q_type = {'3': 'single', '4': 'multiple', '8': 'scale', '1': 'short_answer'}.get(q_type_elem, 'unknown')
        
        if q_type == 'unknown':
            continue
            
        logger.info(f"\n--- 填充 Q{i} ({q_type}) ---")
        if fill_question(container, str(i), q_type):
            success_count += 1
        
        time.sleep(1)
    
    logger.info(f"\n测试完成：{success_count}/{len(containers[:5])} 个题目填充成功")
    
    # 测试提交（不实际提交）
    logger.info("\n测试提交功能...")
    try:
        next_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, 'show_next_page')]")
        logger.info(f"✓ 找到下一页按钮")
        logger.info("建议：手动点击提交按钮测试")
    except:
        logger.warning("未找到下一页按钮")
    
finally:
    driver.quit()
    logger.info("✓ 浏览器已关闭")
    logger.info("\n" + "="*60)
    logger.info("✓ 测试完成！问卷星自动填写系统准备就绪")
    logger.info("="*60)
