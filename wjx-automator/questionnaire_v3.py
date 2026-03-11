"""
问卷星自动填写系统 - 最终修复版
基于御坂妹妹 16 号的诊断结果
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from typing import Any, Dict, List, Optional, Tuple

# 单选题填充 - 最终版
def _fill_single_choice_v3(container, answer, driver, logger):
    """
    单选题填充 - 基于诊断结果
    
    问卷星结构：
    <div class="field ui-field-contain" type="3">
      <input type="radio" name="q1" value="1" id="q1_1">
    </div>
    """
    answer_value = str(answer).strip('"').strip("'")
    logger.debug(f"单选题填充：{answer_value}")
    
    try:
        # 方案 1：通过 name 属性查找（推荐）
        # 例如：name="q1" value="1" 或 value="选项 1"
        radio_inputs = container.find_elements(By.XPATH, ".//input[@type='radio']")
        
        for radio in radio_inputs:
            radio_id = radio.get_attribute('id') or ''
            radio_value = radio.get_attribute('value') or ''
            
            # 匹配条件
            if (answer_value in radio_id or 
                answer_value == radio_value or
                answer_value.isdigit() and str(radio_id.count('_')) == answer_value):
                
                # 直接点击 input（问卷星会触发事件）
                driver.execute_script("arguments[0].click();", radio)
                time.sleep(0.5)
                logger.debug(f"✓ 单选题填充成功：{answer_value}")
                return True, answer_value
        
        # 方案 2：通过 value 属性精确匹配
        for radio in radio_inputs:
            if radio.get_attribute('value') == answer_value:
                driver.execute_script("arguments[0].click();", radio)
                time.sleep(0.5)
                return True, answer_value
        
    except Exception as e:
        logger.warning(f"单选题填充失败：{e}")
    
    logger.warning(f"✗ 未找到单选题选项：{answer_value}")
    return False, f"未找到选项：{answer_value}"


# 多选题填充 - 最终版
def _fill_multiple_choice_v3(container, answers, driver, logger):
    """
    多选题填充 - 基于诊断结果
    
    问卷星结构：
    <div class="field ui-field-contain" type="4">
      <input type="checkbox" name="q2" value="选项 1" id="q2_1">
    </div>
    """
    success_count = 0
    
    for answer in answers:
        answer_value = str(answer).strip('"').strip("'")
        logger.debug(f"多选题填充：{answer_value}")
        
        # 查找所有 checkbox
        checkboxes = container.find_elements(By.XPATH, ".//input[@type='checkbox']")
        
        for checkbox in checkboxes:
            checkbox_value = checkbox.get_attribute('value') or ''
            checkbox_name = checkbox.get_attribute('name') or ''
            
            # 匹配条件
            if answer_value == checkbox_value:
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(0.3)
                success_count += 1
                logger.debug(f"✓ 多选题填充成功：{answer_value}")
                break
    
    return success_count > 0, f"选择了 {success_count}/{len(answers)} 个选项"


# 量表题填充 - 最终版
def _fill_scale_question_v3(container, score, driver, logger):
    """
    量表题填充 - 基于诊断结果
    
    问卷星结构：
    <div class="field ui-field-contain" type="8">
      <input type="radio" name="q7" value="1" id="q7_1">
    </div>
    """
    score_str = str(score)
    logger.debug(f"量表题填充：{score_str}")
    
    try:
        # 查找所有 radio
        radios = container.find_elements(By.XPATH, ".//input[@type='radio']")
        
        for radio in radios:
            radio_value = radio.get_attribute('value') or ''
            radio_id = radio.get_attribute('id') or ''
            
            # 匹配条件
            if radio_value == score_str or radio_id.endswith(f"_{score_str}"):
                driver.execute_script("arguments[0].click();", radio)
                time.sleep(0.5)
                logger.debug(f"✓ 量表题填充成功：{score_str}")
                return True, score_str
    except Exception as e:
        logger.warning(f"量表题填充失败：{e}")
    
    logger.warning(f"✗ 未找到量表题选项：{score_str}")
    return False, f"未找到选项：{score_str}"


# 简答题填充 - 最终版
def _fill_short_answer_v3(container, answer, driver, logger):
    """
    简答题填充 - 基于诊断结果
    
    问卷星结构：
    <div class="field ui-field-contain" type="1">
      <textarea name="q25" class="form-control"></textarea>
    </div>
    """
    # 优先查找 textarea
    textareas = container.find_elements(By.XPATH, ".//textarea")
    
    for textarea in textareas:
        try:
            # 使用 JS 设置 value
            driver.execute_script("arguments[0].value = arguments[1];", 
                                  textarea, answer)
            
            # 触发事件
            driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, textarea)
            
            logger.debug(f"✓ 简答题填充成功：长度={len(answer)}")
            return True, "已填写"
        except Exception as e:
            logger.warning(f"Textarea 填写失败：{e}")
            continue
    
    # 备选：查找 input[type='text']
    text_inputs = container.find_elements(By.XPATH, ".//input[@type='text']")
    for text_input in text_inputs:
        try:
            driver.execute_script("arguments[0].value = arguments[1];", 
                                  text_input, answer)
            logger.debug(f"✓ 简答题填充成功：长度={len(answer)}")
            return True, "已填写"
        except:
            continue
    
    logger.warning("✗ 未找到简答题输入框")
    return False, "未找到输入框"


# 提交函数 - 最终版
def submit_questionnaire_v3(driver, logger):
    """
    提交问卷 - 基于诊断结果
    问卷星使用 show_next_page() 函数
    """
    try:
        logger.debug("开始提交问卷")
        
        # 方案 1：调用 show_next_page() 函数
        try:
            logger.debug("尝试调用 show_next_page()")
            driver.execute_script("return show_next_page();")
            time.sleep(3)
            logger.info("✓ show_next_page() 调用成功")
            return True
        except Exception as e:
            logger.warning(f"show_next_page() 失败：{e}")
        
        # 方案 2：查找下一页按钮并点击
        try:
            next_btn = driver.find_element(By.XPATH, 
                "//a[contains(@onclick, 'show_next_page')]")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            logger.info("✓ 点击下一页成功")
            return True
        except:
            pass
        
        # 方案 3：查找提交按钮
        try:
            submit_btn = driver.find_element(By.XPATH, "//div[@id='ctlNext']")
            driver.execute_script("arguments[0].click();", submit_btn)
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
