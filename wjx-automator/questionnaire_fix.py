#!/usr/bin/env python3
"""
问卷星自动填写系统 - 完整修复版
使用御坂大人提供的 HTML 结构
"""

import json
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 单选题填充函数 - 使用御坂大人提供的 HTML 结构
def fill_single_choice_v2(driver, container, answer):
    """
    填充单选题
    问卷星结构：
    <div class="ui-radio">
      <input type="radio" id="q1_1">
      <a class="jqradio">...</a>  ← 需要点击这个！
      <div class="label">选项文本</div>
    </div>
    """
    answer_value = str(answer).strip('"').strip("'")
    
    # 方案 1：通过 jqradio 元素查找
    jqradios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
    
    for jqradio in jqradios:
        try:
            parent_div = jqradio.find_element(By.XPATH, "../..")
            input_elem = parent_div.find_element(By.XPATH, ".//input[@type='radio']")
            input_id = input_elem.get_attribute('id')
            
            if input_id and input_id.endswith(answer_value):
                # 使用 JS 点击
                driver.execute_script("arguments[0].click();", jqradio)
                time.sleep(0.5)
                print(f"✓ 单选题填充成功：{answer_value}")
                return True, answer_value
        except:
            continue
    
    # 方案 2：通过 label 文本查找
    labels = container.find_elements(By.XPATH, ".//div[@class='label']")
    for label in labels:
        if answer_value in label.text:
            try:
                jqradio = label.find_element(By.XPATH, "../..//a[@class='jqradio']")
                driver.execute_script("arguments[0].click();", jqradio)
                time.sleep(0.5)
                print(f"✓ 单选题填充成功（通过 label）：{answer_value}")
                return True, answer_value
            except:
                continue
    
    print(f"✗ 未找到单选题选项：{answer_value}")
    return False, f"未找到选项：{answer_value}"


# 多选题填充函数
def fill_multiple_choice_v2(driver, container, answers):
    """
    填充多选题
    问卷星结构：
    <div class="ui-checkbox">
      <input type="checkbox" name="q2" value="选项 1">
      <a class="jqcheckbox">...</a>
      <div class="label">选项文本</div>
    </div>
    """
    success_count = 0
    
    for answer in answers:
        answer_value = str(answer).strip('"').strip("'")
        
        # 方案 1：通过 jqcheckbox 元素查找
        jqcheckboxes = container.find_elements(By.XPATH, ".//a[@class='jqcheckbox']")
        
        for jqcheckbox in jqcheckboxes:
            try:
                parent_div = jqcheckbox.find_element(By.XPATH, "../..")
                checkbox_elem = parent_div.find_element(By.XPATH, ".//input[@type='checkbox']")
                checkbox_name = checkbox_elem.get_attribute('name')
                checkbox_value = checkbox_elem.get_attribute('value')
                
                if checkbox_name and answer_value in checkbox_name:
                    driver.execute_script("arguments[0].click();", jqcheckbox)
                    time.sleep(0.3)
                    success_count += 1
                    print(f"✓ 多选题填充成功：{answer_value}")
                    break
            except:
                continue
        
        # 方案 2：通过 label 文本查找
        labels = container.find_elements(By.XPATH, ".//div[@class='label']")
        for label in labels:
            if answer_value in label.text:
                try:
                    jqcheckbox = label.find_element(By.XPATH, "../..//a[@class='jqcheckbox']")
                    driver.execute_script("arguments[0].click();", jqcheckbox)
                    time.sleep(0.3)
                    success_count += 1
                    print(f"✓ 多选题填充成功（通过 label）：{answer_value}")
                    break
                except:
                    continue
    
    return success_count > 0, f"选择了 {success_count}/{len(answers)} 个选项"


# 量表题填充函数
def fill_scale_question_v2(driver, container, score):
    """
    填充量表题（1-5 分）
    问卷星结构：
    <div class="ui-radio">
      <input type="radio" id="q7_1">
      <a class="jqradio">1</a>
    </div>
    """
    score_str = str(score)
    
    # 查找 jqradio 元素
    jqradios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
    
    for jqradio in jqradios:
        try:
            # 检查 jqradio 的文本内容或关联的 input id
            jqradio_text = jqradio.text.strip()
            parent_div = jqradio.find_element(By.XPATH, "../..")
            input_elem = parent_div.find_element(By.XPATH, ".//input[@type='radio']")
            input_id = input_elem.get_attribute('id')
            
            if jqradio_text == score_str or (input_id and input_id.endswith(score_str)):
                driver.execute_script("arguments[0].click();", jqradio)
                time.sleep(0.5)
                print(f"✓ 量表题填充成功：{score_str}")
                return True, score_str
        except:
            continue
    
    print(f"✗ 未找到量表题选项：{score_str}")
    return False, f"未找到选项：{score_str}"


# 简答题填充函数
def fill_short_answer_v2(driver, container, answer):
    """
    填充简答题
    """
    # 查找所有文本输入框
    text_inputs = container.find_elements(By.XPATH, 
        ".//input[@type='text'] | .//textarea"
    )
    
    for text_input in text_inputs:
        try:
            # 使用 JS 设置 value
            driver.execute_script("arguments[0].value = arguments[1];", 
                                  text_input, answer)
            
            # 触发事件
            driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, text_input)
            
            print(f"✓ 简答题填充成功：长度={len(answer)}")
            return True, "已填写"
        except:
            continue
    
    print("✗ 未找到简答题输入框")
    return False, "未找到输入框"


# 提交函数
def submit_questionnaire_v2(driver):
    """
    提交问卷
    问卷星使用 show_next_page() 函数导航
    """
    try:
        print("开始提交问卷...")
        
        # 方案 1：直接调用 show_next_page()
        try:
            print("尝试调用 show_next_page()...")
            driver.execute_script("return show_next_page();")
            time.sleep(3)
            print("✓ show_next_page() 调用成功")
            return True
        except Exception as e:
            print(f"show_next_page() 失败：{e}")
        
        # 方案 2：查找下一页按钮并点击
        try:
            next_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, 'show_next_page')]")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            print("✓ 点击下一页成功")
            return True
        except:
            pass
        
        # 方案 3：查找提交按钮
        try:
            submit_btn = driver.find_element(By.XPATH, "//div[@id='ctlNext']")
            driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(3)
            print("✓ 点击提交按钮成功")
            return True
        except:
            pass
        
        print("✗ 所有提交方式都失败")
        return False
            
    except Exception as e:
        print(f"提交失败：{e}")
        return False


if __name__ == "__main__":
    print("问卷星填充修复脚本已加载！")
    print()
    print("使用方式：")
    print("  from questionnaire_fix import fill_single_choice_v2")
    print("  fill_single_choice_v2(driver, container, '选项 1')")
    print()
    print("测试：")
    print("  python3 questionnaire_fix.py")
