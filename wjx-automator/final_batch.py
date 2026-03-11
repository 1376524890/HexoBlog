#!/usr/bin/env python3
"""
问卷星自动填写系统 - 批量填写版
基于测试成功的逻辑
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import logging
from datetime import datetime
from pathlib import Path
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/wjx_batch.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 问卷统计
QUESTION_STATS = {
    "1": {"type": "single", "options": ["体验过", "未体验过，但有消费习惯", "未体验过，也无消费习惯"]},
    "2": {"type": "multiple"},
    "3": {"type": "multiple"},
    "4": {"type": "multiple"},
    "5": {"type": "single"},
    "6": {"type": "single"},
    "7": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "8": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "9": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "10": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
    "11": {"type": "multiple"},
    "12": {"type": "scale", "options": ["1", "2", "3", "4", "5"]},
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

# 简答题模板
SHORT_ANSWER_TEMPLATES = [
    "AI 技术在历史文化实景戏剧中的应用前景广阔，特别是在虚拟现实和动作捕捉方面。",
    "建议增加更多交互环节，让观众能够更深入地参与到戏剧表演中。",
    "希望未来能看到更多 AI 技术与传统文化结合的创意作品。",
    "当前技术应用已经很不错了，期待未来能有更沉浸式的体验。",
    "AI 技术可以极大地提升观众的参与感和沉浸感，是值得大力发展的方向。",
    "建议在保持传统戏剧精髓的基础上，适度引入 AI 技术增强体验。",
    "AI 技术能让历史文化以更生动的方式呈现给观众，非常有意义。",
    "希望未来能看到更多创新的应用场景，让传统文化焕发新的活力。"
]


def generate_answer(q_type, question_id):
    """生成答案"""
    if 'single' in q_type:
        return random.choice(["1", "2", "3", "4", "5"])
    elif 'multiple' in q_type:
        return f"选项{random.randint(1, 8)}"
    elif 'scale' in q_type:
        return random.choice(["3", "4", "5"])
    elif 'short_answer' in q_type:
        return random.choice(SHORT_ANSWER_TEMPLATES)
    return "默认答案"


def fill_question(container, question_id, q_type):
    """填充单个问题"""
    answer = generate_answer(q_type, question_id)
    logger.debug(f"填充 Q{question_id} ({q_type}): {answer}")
    
    try:
        if 'single' in q_type:
            # 单选题 - 通过 name 属性查找
            radios = container.find_elements(By.XPATH, f".//input[@name='q{question_id}']")
            if radios:
                idx = random.randint(0, len(radios) - 1)
                driver.execute_script("arguments[0].click();", radios[idx])
                return True
                
        elif 'multiple' in q_type:
            # 多选题 - 通过 name 属性查找
            checkboxes = container.find_elements(By.XPATH, f".//input[@name='q{question_id}']")
            if checkboxes:
                num_select = min(random.randint(1, 3), len(checkboxes))
                selected = random.sample(checkboxes, num_select)
                for checkbox in selected:
                    driver.execute_script("arguments[0].click();", checkbox)
                return True
                    
        elif 'scale' in q_type:
            # 量表题 - 通过 name 属性查找
            radios = container.find_elements(By.XPATH, f".//input[@name='q{question_id}']")
            if radios:
                idx = random.randint(0, len(radios) - 1)
                driver.execute_script("arguments[0].click();", radios[idx])
                return True
                    
        elif 'short_answer' in q_type:
            # 简答题
            textareas = container.find_elements(By.XPATH, f".//textarea[@name='q{question_id}']")
            if textareas:
                driver.execute_script("arguments[0].value = arguments[1];", 
                                      textareas[0], answer)
                return True
                
    except Exception as e:
        logger.warning(f"Q{question_id} 填充失败：{e}")
        return False
    
    return False


def fill_questionnaire():
    """填写一份问卷"""
    try:
        # 打开问卷
        driver.get("https://v.wjx.cn/vm/PhfZxRV.aspx")
        time.sleep(2)
        
        # 获取所有题目容器
        containers = driver.find_elements(By.XPATH, 
            "//div[contains(@class, 'field ui-field-contain')]")
        
        logger.info(f"找到 {len(containers)} 个题目容器")
        
        success_count = 0
        for container in containers:
            # 获取题目 ID 和类型
            q_type_elem = container.get_attribute('type')
            container_id = container.get_attribute('id')
            
            if not container_id or not container_id.startswith('div'):
                continue
                
            question_id = container_id.replace('div', '')
            q_type = QUESTION_STATS.get(question_id, {}).get('type', 'unknown')
            
            if q_type == 'unknown':
                continue
            
            if fill_question(container, question_id, q_type):
                success_count += 1
        
        logger.info(f"成功填充 {success_count}/{len(containers)} 个题目")
        
        # 等待并点击提交
        time.sleep(2)
        try:
            next_btn = driver.find_element(By.XPATH, 
                "//a[contains(@onclick, 'show_next_page')]")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            logger.info("✓ 提交成功，进入下一页")
            return True
        except:
            logger.warning("未找到下一页按钮")
            return False
            
    except Exception as e:
        logger.error(f"填写失败：{e}")
        return False


def main():
    """主程序"""
    global driver
    
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("="*60)
    logger.info("问卷星自动填写系统 - 批量填写版")
    logger.info("="*60)
    
    # 启动浏览器
    logger.info("启动 Chromium 浏览器...")
    options = Options()
    options.binary_location = '/usr/bin/chromium-browser'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(
        service=Service('/usr/bin/chromedriver'),
        options=options
    )
    logger.info("✓ Chromium 启动成功")
    
    try:
        # 填写 210 份问卷
        total = 210
        success = 0
        failed = 0
        
        for i in range(1, total + 1):
            logger.info(f"\n{'='*40}")
            logger.info(f"正在填写第 {i} 份问卷...")
            
            if fill_questionnaire():
                success += 1
            else:
                failed += 1
            
            # 间隔时间，避免被封
            if i % 10 == 0:
                wait_time = random.randint(30, 60)
                logger.info(f"已填写 {i} 份，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            
            # 每 50 份打印统计
            if i % 50 == 0:
                logger.info(f"\n进度统计：{i}/{total}")
                logger.info(f"成功：{success}, 失败：{failed}")
        
        # 总结
        logger.info("\n" + "="*60)
        logger.info("批量填写完成！")
        logger.info("="*60)
        logger.info(f"总计：{total} 份")
        logger.info(f"成功：{success} 份 ({success/total*100:.1f}%)")
        logger.info(f"失败：{failed} 份 ({failed/total*100:.1f}%)")
        
        # 保存结果
        result = {
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": f"{success/total*100:.1f}%"
        }
        
        with open("logs/batch_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n结果已保存到 logs/batch_result.json")
        
    finally:
        driver.quit()
        logger.info("\n✓ 浏览器已关闭")


if __name__ == "__main__":
    main()
