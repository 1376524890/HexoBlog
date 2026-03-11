"""
问卷星自动填写核心 - 新版本
使用御坂大人提供的 HTML 结构
"""

from selenium.webdriver.common.by import By
import time

# 单选题填充 - 修复版
def _fill_single_choice_new(container, answer, driver, logger):
    """
    问卷星结构：
    <div class="ui-radio">
      <input type="radio" id="q1_1" name="q1" value="1">
      <a class="jqradio"><span>选项文本</span></a>
    </div>
    """
    answer_value = str(answer).strip('"').strip("'")
    logger.debug(f"单选题填充：{answer_value}")
    
    # 方案 1：查找所有 jqradio 并检查关联的 input
    jqradios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
    
    for jqradio in jqradios:
        try:
            # 获取同 div 下的 input
            parent = jqradio.find_element(By.XPATH, "../..")
            input_elem = parent.find_element(By.XPATH, ".//input[@type='radio']")
            
            # 检查是否匹配
            input_id = input_elem.get_attribute('id') or ''
            input_value = input_elem.get_attribute('value') or ''
            
            if answer_value in input_id or answer_value == input_value:
                # 使用 JS 点击 jqradio
                driver.execute_script("arguments[0].click();", jqradio)
                time.sleep(0.5)
                logger.debug(f"✓ 单选题填充成功")
                return True, answer_value
        except Exception as e:
            logger.warning(f"方案 1 失败：{e}")
            continue
    
    # 方案 2：通过 label 文本查找
    labels = container.find_elements(By.XPATH, ".//div[@class='label']")
    for label in labels:
        if answer_value in label.text:
            try:
                jqradio = label.find_element(By.XPATH, "../..//a[@class='jqradio']")
                driver.execute_script("arguments[0].click();", jqradio)
                time.sleep(0.5)
                logger.debug(f"✓ 单选题填充成功（通过 label）")
                return True, answer_value
            except:
                continue
    
    logger.warning(f"✗ 未找到单选题选项：{answer_value}")
    return False, f"未找到选项：{answer_value}"


# 多选题填充 - 修复版
def _fill_multiple_choice_new(container, answers, driver, logger):
    """
    问卷星结构：
    <div class="ui-checkbox">
      <input type="checkbox" name="q2" value="选项 1">
      <a class="jqcheckbox">...</a>
    </div>
    """
    success_count = 0
    
    for answer in answers:
        answer_value = str(answer).strip('"').strip("'")
        logger.debug(f"多选题填充：{answer_value}")
        
        # 方案 1：查找所有 jqcheckbox 并检查关联的 input
        jqcheckboxes = container.find_elements(By.XPATH, ".//a[@class='jqcheckbox']")
        
        for jqcheckbox in jqcheckboxes:
            try:
                parent = jqcheckbox.find_element(By.XPATH, "../..")
                checkbox_elem = parent.find_element(By.XPATH, ".//input[@type='checkbox']")
                
                checkbox_name = checkbox_elem.get_attribute('name') or ''
                checkbox_value = checkbox_elem.get_attribute('value') or ''
                
                if answer_value in checkbox_name or answer_value == checkbox_value:
                    driver.execute_script("arguments[0].click();", jqcheckbox)
                    time.sleep(0.3)
                    success_count += 1
                    logger.debug(f"✓ 多选题填充成功：{answer_value}")
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
                    logger.debug(f"✓ 多选题填充成功（通过 label）：{answer_value}")
                    break
                except:
                    continue
    
    return success_count > 0, f"选择了 {success_count}/{len(answers)} 个选项"


# 量表题填充 - 修复版
def _fill_scale_question_new(container, score, driver, logger):
    """
    问卷星结构：
    <div class="ui-radio">
      <input type="radio" id="q7_1">
      <a class="jqradio">1</a>  ← 检查文本内容！
    </div>
    """
    score_str = str(score)
    logger.debug(f"量表题填充：{score_str}")
    
    # 查找所有 jqradio
    jqradios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
    
    for jqradio in jqradios:
        try:
            # 检查 jqradio 的文本内容
            jqradio_text = jqradio.text.strip()
            
            # 检查是否匹配分数
            if jqradio_text == score_str:
                driver.execute_script("arguments[0].click();", jqradio)
                time.sleep(0.5)
                logger.debug(f"✓ 量表题填充成功（通过文本）：{score_str}")
                return True, score_str
            
            # 同时检查关联的 input id
            parent = jqradio.find_element(By.XPATH, "../..")
            input_elem = parent.find_element(By.XPATH, ".//input[@type='radio']")
            input_id = input_elem.get_attribute('id') or ''
            
            if input_id.endswith(f"_{score_str}"):
                driver.execute_script("arguments[0].click();", jqradio)
                time.sleep(0.5)
                logger.debug(f"✓ 量表题填充成功（通过 id）：{score_str}")
                return True, score_str
        except:
            continue
    
    logger.warning(f"✗ 未找到量表题选项：{score_str}")
    return False, f"未找到选项：{score_str}"


# 简答题填充 - 修复版
def _fill_short_answer_new(container, answer, driver, logger):
    """
    简答题填充
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
            
            logger.debug(f"✓ 简答题填充成功：长度={len(answer)}")
            return True, "已填写"
        except Exception as e:
            logger.warning(f"文本框填写失败：{e}")
            continue
    
    logger.warning("✗ 未找到简答题输入框")
    return False, "未找到输入框"


# 提交函数 - 修复版
def submit_questionnaire_new(driver, logger):
    """
    提交问卷
    问卷星使用 show_next_page() 函数
    """
    try:
        logger.debug("开始提交问卷")
        
        # 方案 1：直接调用 show_next_page()
        try:
            logger.debug("尝试调用 show_next_page()")
            driver.execute_script("return show_next_page();")
            time.sleep(3)
            logger.info("✓ show_next_page() 调用成功")
            return True
        except Exception as e:
            logger.warning(f"show_next_page() 失败：{e}")
        
        # 方案 2：查找下一页按钮
        try:
            next_btn = driver.find_element(By.XPATH, "//a[contains(@onclick, 'show_next_page')]")
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
