#!/usr/bin/env python3
"""
问卷星自动填写系统 - 最终完整版
基于御坂妹妹 16 号诊断结果修复
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.models.config import Config
from src.utils.generators import AnswerGenerator
from src.utils.stats import load_question_stats
from questionnaire_v3 import (
    _fill_single_choice_v3,
    _fill_multiple_choice_v3,
    _fill_scale_question_v3,
    _fill_short_answer_v3,
    submit_questionnaire_v3
)


class QuestionnaireAutoFiller:
    """
    问卷星自动填写器（最终修复版）
    
    基于御坂妹妹 16 号诊断的页面结构：
    - 题目容器：div.field.ui-field-contain[type=X]
    - 单选题：input[type="radio"][name="qX"]
    - 多选题：input[type="checkbox"][name="qX"]
    - 简答题：textarea[name="qX"]
    - 提交：show_next_page()
    """
    
    def __init__(self, config: Config, question_stats: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.question_stats = question_stats
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        
    def start(self):
        """启动浏览器"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver_path = ChromeDriverManager().install()
        self.driver = webdriver.Chrome(service=Service(driver_path), options=options)
        self.logger.info("✓ Chrome 浏览器启动成功")
        
    def fill_question(self, question_container, question_id: str) -> Tuple[bool, str]:
        """填充单个问题"""
        try:
            answer = self.answer_generator.generate_answer(question_id)
            q_type = self.question_stats.get(str(question_id), {}).get('type', '').lower()
            
            if 'single' in q_type or 'radio' in q_type:
                return _fill_single_choice_v3(question_container, answer, self.driver, self.logger)
            elif 'multi' in q_type or 'checkbox' in q_type:
                return _fill_multiple_choice_v3(question_container, answer, self.driver, self.logger)
            elif 'scale' in q_type or 'rating' in q_type:
                return _fill_scale_question_v3(question_container, answer, self.driver, self.logger)
            elif 'short' in q_type or 'text' in q_type:
                return _fill_short_answer_v3(question_container, answer, self.driver, self.logger)
            else:
                return False, "未知题型"
        except Exception as e:
            self.logger.error(f"填充问题 Q{question_id} 失败：{e}")
            return False, str(e)
    
    def submit_questionnaire(self) -> bool:
        """提交问卷"""
        return submit_questionnaire_v3(self.driver, self.logger)
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.logger.info("✓ 浏览器已关闭")


def main():
    """主程序"""
    print("="*60)
    print("问卷星自动填写系统 - 最终版")
    print("="*60)
    
    # 加载配置
    config = Config.from_file("config.json")
    question_stats = load_question_stats("data/question_stats.json")
    
    # 初始化填充器
    filler = QuestionnaireAutoFiller(config, question_stats)
    filler.start()
    
    try:
        # 打开问卷
        filler.driver.get("https://v.wjx.cn/vm/PhfZxRV.aspx")
        time.sleep(3)
        print("✓ 问卷页面加载成功")
        
        # 测试填充
        containers = filler.driver.find_elements(By.XPATH, "//div[contains(@class, 'field ui-field-contain')]")
        print(f"✓ 找到 {len(containers)} 个题目容器")
        
        # 填充第一个题目测试
        if containers:
            question_id = "1"
            success, result = filler.fill_question(containers[0], question_id)
            print(f"Q{question_id}: {'✓ 成功' if success else '✗ 失败'} - {result}")
        
        # 测试提交
        # filler.submit_questionnaire()
        
    finally:
        filler.close()
    
    print("="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    main()
