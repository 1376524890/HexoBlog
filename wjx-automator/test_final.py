#!/usr/bin/env python3
"""
问卷星自动填写系统 - 独立测试版
不依赖 src 模块结构
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

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuestionnaireAutoFiller:
    """问卷星自动填写器（独立版）"""
    
    def __init__(self, question_stats: Dict[str, Any]):
        self.question_stats = question_stats
        self.logger = logger
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
        logger.info("✓ Chrome 浏览器启动成功")
        
    def fill_question(self, question_container, question_id: str) -> Tuple[bool, str]:
        """填充单个问题"""
        try:
            # 生成答案
            answer = self._generate_answer(question_id)
            q_type = self.question_stats.get(str(question_id), {}).get('type', '').lower()
            
            logger.debug(f"填充问题 Q{question_id}，类型：{q_type}, 答案：{answer}")
            
            if 'single' in q_type or 'radio' in q_type:
                return self._fill_single_choice(question_container, answer)
            elif 'multi' in q_type or 'checkbox' in q_type:
                return self._fill_multiple_choice(question_container, answer)
            elif 'scale' in q_type or 'rating' in q_type:
                return self._fill_scale_question(question_container, answer)
            elif 'short' in q_type or 'text' in q_type:
                return self._fill_short_answer(question_container, answer)
            else:
                return False, "未知题型"
        except Exception as e:
            logger.error(f"填充问题 Q{question_id} 失败：{e}")
            return False, str(e)
    
    def _generate_answer(self, question_id: str) -> Any:
        """生成答案（简化版）"""
        q_id = int(question_id) if question_id.isdigit() else 0
        
        # 单选题
        if q_id in [1, 5, 6, 14, 19, 20, 21, 22, 23, 24]:
            return random.choice(["1", "2", "3", "4", "5"])
        
        # 多选题
        if q_id in [2, 3, 4, 11, 13]:
            return [f"选项{i}" for i in random.sample(range(1, 9), random.randint(1, 4))]
        
        # 量表题
        if q_id in [7, 8, 9, 10, 12, 15, 16, 17, 18, 24]:
            return random.randint(3, 5)
        
        # 简答题
        if q_id in [25, 26, 27, 28]:
            templates = [
                "AI 技术在历史文化实景戏剧中的应用前景广阔，特别是在虚拟现实和动作捕捉方面。",
                "建议增加更多交互环节，让观众能够更深入地参与到戏剧表演中。",
                "希望未来能看到更多 AI 技术与传统文化结合的创意作品。",
                "当前技术应用已经很不错了，期待未来能有更沉浸式的体验。"
            ]
            return random.choice(templates)
        
        return "默认答案"
    
    def _fill_single_choice(self, container, answer: str) -> Tuple[bool, str]:
        """单选题填充"""
        answer_value = str(answer).strip('"').strip("'")
        logger.debug(f"单选题填充：{answer_value}")
        
        try:
            radio_inputs = container.find_elements(By.XPATH, ".//input[@type='radio']")
            
            for radio in radio_inputs:
                radio_id = radio.get_attribute('id') or ''
                radio_value = radio.get_attribute('value') or ''
                
                if answer_value in radio_id or answer_value == radio_value:
                    self.driver.execute_script("arguments[0].click();", radio)
                    time.sleep(0.5)
                    logger.debug(f"✓ 单选题填充成功：{answer_value}")
                    return True, answer_value
            
        except Exception as e:
            logger.warning(f"单选题填充失败：{e}")
        
        logger.warning(f"✗ 未找到单选题选项：{answer_value}")
        return False, f"未找到选项：{answer_value}"
    
    def _fill_multiple_choice(self, container, answers: List[str]) -> Tuple[bool, str]:
        """多选题填充"""
        success_count = 0
        
        for answer in answers:
            answer_value = str(answer).strip('"').strip("'")
            logger.debug(f"多选题填充：{answer_value}")
            
            checkboxes = container.find_elements(By.XPATH, ".//input[@type='checkbox']")
            
            for checkbox in checkboxes:
                checkbox_value = checkbox.get_attribute('value') or ''
                
                if answer_value == checkbox_value:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.3)
                    success_count += 1
                    logger.debug(f"✓ 多选题填充成功：{answer_value}")
                    break
        
        return success_count > 0, f"选择了 {success_count}/{len(answers)} 个选项"
    
    def _fill_scale_question(self, container, score: int) -> Tuple[bool, str]:
        """量表题填充"""
        score_str = str(score)
        logger.debug(f"量表题填充：{score_str}")
        
        try:
            radios = container.find_elements(By.XPATH, ".//input[@type='radio']")
            
            for radio in radios:
                radio_value = radio.get_attribute('value') or ''
                radio_id = radio.get_attribute('id') or ''
                
                if radio_value == score_str or radio_id.endswith(f"_{score_str}"):
                    self.driver.execute_script("arguments[0].click();", radio)
                    time.sleep(0.5)
                    logger.debug(f"✓ 量表题填充成功：{score_str}")
                    return True, score_str
        except Exception as e:
            logger.warning(f"量表题填充失败：{e}")
        
        logger.warning(f"✗ 未找到量表题选项：{score_str}")
        return False, f"未找到选项：{score_str}"
    
    def _fill_short_answer(self, container, answer: str) -> Tuple[bool, str]:
        """简答题填充"""
        textareas = container.find_elements(By.XPATH, ".//textarea")
        
        for textarea in textareas:
            try:
                self.driver.execute_script("arguments[0].value = arguments[1];", 
                                          textarea, answer)
                self.driver.execute_script("""
                    arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                    arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                """, textarea)
                
                logger.debug(f"✓ 简答题填充成功：长度={len(answer)}")
                return True, "已填写"
            except Exception as e:
                logger.warning(f"Textarea 填写失败：{e}")
                continue
        
        logger.warning("✗ 未找到简答题输入框")
        return False, "未找到输入框"
    
    def submit_questionnaire(self) -> bool:
        """提交问卷"""
        try:
            logger.debug("开始提交问卷")
            
            # 方案 1：调用 show_next_page() 函数
            try:
                logger.debug("尝试调用 show_next_page()")
                self.driver.execute_script("return show_next_page();")
                time.sleep(3)
                logger.info("✓ show_next_page() 调用成功")
                return True
            except Exception as e:
                logger.warning(f"show_next_page() 失败：{e}")
            
            # 方案 2：查找下一页按钮并点击
            try:
                next_btn = self.driver.find_element(By.XPATH, 
                    "//a[contains(@onclick, 'show_next_page')]")
                self.driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3)
                logger.info("✓ 点击下一页成功")
                return True
            except:
                pass
            
            # 方案 3：查找提交按钮
            try:
                submit_btn = self.driver.find_element(By.XPATH, "//div[@id='ctlNext']")
                self.driver.execute_script("arguments[0].click();", submit_btn)
                time.sleep(3)
                logger.info("✓ 点击提交按钮成功")
                return True
            except:
                pass
            
            logger.warning("✗ 所有提交方式都失败")
            return False
            
        except Exception as e:
            logger.error(f"提交失败：{e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("✓ 浏览器已关闭")


def test_quick():
    """快速测试"""
    print("="*60)
    print("问卷星自动填写系统 - 快速测试")
    print("="*60)
    
    # 加载问卷统计（简化版）
    question_stats = {
        "1": {"type": "single", "distribution": {"1": 30, "2": 40, "3": 30}},
        "2": {"type": "multiple", "distribution": {"选项 1": 50, "选项 2": 40, "选项 3": 30}},
        "3": {"type": "single", "distribution": {"1": 30, "2": 40, "3": 30}},
        "25": {"type": "short_answer"},
    }
    
    # 初始化填充器
    filler = QuestionnaireAutoFiller(question_stats)
    filler.start()
    
    try:
        # 打开问卷
        filler.driver.get("https://v.wjx.cn/vm/PhfZxRV.aspx")
        time.sleep(3)
        print("✓ 问卷页面加载成功")
        
        # 获取题目容器
        containers = filler.driver.find_elements(By.XPATH, 
            "//div[contains(@class, 'field ui-field-contain')]")
        print(f"✓ 找到 {len(containers)} 个题目容器")
        
        # 填充前 3 个题目测试
        for i, container in enumerate(containers[:3], 1):
            question_id = str(i)
            # 提取问题类型
            q_type_elem = container.get_attribute('type')
            if q_type_elem == '3':
                q_type = 'single'
            elif q_type_elem == '4':
                q_type = 'multiple'
            elif q_type_elem == '8':
                q_type = 'scale'
            elif q_type_elem == '1':
                q_type = 'short_answer'
            else:
                q_type = 'unknown'
            
            question_stats[question_id]["type"] = q_type
            
            success, result = filler.fill_question(container, question_id)
            print(f"Q{i} ({q_type}): {'✓ 成功' if success else '✗ 失败'} - {result}")
        
        # 测试提交
        print("\n测试提交...")
        # filler.submit_questionnaire()
        
    finally:
        filler.close()
    
    print("="*60)
    print("✓ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    test_quick()
