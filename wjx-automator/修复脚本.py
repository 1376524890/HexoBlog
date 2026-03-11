"""
问卷星自动填写系统 - 单选题/多选题填充修复脚本
"""

# 单选题填充函数 - 使用御坂大人提供的 HTML 结构
def fill_single_choice(container, answer):
    """
    填充单选题
    问卷星结构：
    <div class="ui-radio">
      <input type="radio" id="q1_1">
      <a class="jqradio">...</a>
      <div class="label">选项文本</div>
    </div>
    """
    from selenium.webdriver.common.by import By
    
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
                return True, answer_value
            except:
                continue
    
    return False, f"未找到选项：{answer_value}"


# 多选题填充函数
def fill_multiple_choice(container, answers):
    """
    填充多选题
    问卷星结构：
    <div class="ui-checkbox">
      <input type="checkbox" name="q2" value="选项 1">
      <a class="jqcheckbox">...</a>
      <div class="label">选项文本</div>
    </div>
    """
    from selenium.webdriver.common.by import By
    
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
                    break
                except:
                    continue
    
    return success_count > 0, f"选择了 {success_count}/{len(answers)} 个选项"


# 量表题填充函数
def fill_scale_question(container, score):
    """
    填充量表题（1-5 分）
    问卷星结构：
    <div class="ui-radio">
      <input type="radio" id="q7_1">
      <a class="jqradio">1</a>
    </div>
    """
    from selenium.webdriver.common.by import By
    
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
                return True, score_str
        except:
            continue
    
    return False, f"未找到选项：{score}"


print("修复脚本已加载！")
print("单选题：fill_single_choice(container, answer)")
print("多选题：fill_multiple_choice(container, answers)")
print("量表题：fill_scale_question(container, score)")
