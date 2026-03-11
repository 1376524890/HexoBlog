#!/usr/bin/env python3
"""
修改 questionnaire.py 使用新的修复函数
"""

import re

# 读取原文件
with open('/home/claw/.openclaw/workspace/wjx-automator/src/core/questionnaire.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加新的导入
old_imports = """from src.models.config import Config
from src.utils.generators import AnswerGenerator
from src.utils.stats import load_question_stats"""

new_imports = """from src.models.config import Config
from src.utils.generators import AnswerGenerator
from src.utils.stats import load_question_stats
from questionnaire_new import (
    _fill_single_choice_new,
    _fill_multiple_choice_new,
    _fill_scale_question_new,
    _fill_short_answer_new,
    submit_questionnaire_new
)"""

content = content.replace(old_imports, new_imports)

# 2. 修改 _fill_single_choice 函数调用
content = content.replace(
    'return self._fill_single_choice(question_container, answer)',
    'return _fill_single_choice_new(question_container, answer, self.driver, self.logger)'
)

# 3. 修改 _fill_multiple_choice 函数调用
content = content.replace(
    'return self._fill_multiple_choice(question_container, answer)',
    'return _fill_multiple_choice_new(question_container, answer, self.driver, self.logger)'
)

# 4. 修改 _fill_scale_question 函数调用
content = content.replace(
    'return self._fill_scale_question(question_container, answer)',
    'return _fill_scale_question_new(question_container, answer, self.driver, self.logger)'
)

# 5. 修改 _fill_short_answer 函数调用
content = content.replace(
    'return self._fill_short_answer(question_container, answer)',
    'return _fill_short_answer_new(question_container, answer, self.driver, self.logger)'
)

# 6. 修改 submit_questionnaire 函数
# 找到旧的 submit_questionnaire 方法并替换
old_submit = """def submit_questionnaire(self) -> bool:
        \"\"\"
        提交问卷 - 修复版
        
        问卷星提交机制:
        1. 直接调用 show_next_page() 或 submitQuestionnaire() JavaScript 函数
        2. 或者点击 div#ctlNext 使用 JS click
        \"\"\"
        try:
            self.logger.debug("开始提交问卷")
            
            # 方案 1：直接调用问卷星的 JavaScript 函数（最可靠）
            try:
                self.logger.debug("尝试调用 show_next_page()")
                result = self.driver.execute_script("return show_next_page();")
                time.sleep(2)
                
                # 检查是否成功
                if self._check_submission_success():
                    self.logger.info("通过 show_next_page() 成功提交")
                    return True
            except Exception as e:
                self.logger.warning(f"show_next_page() 调用失败：{e}")
            
            # 方案 2：调用 submitQuestionnaire()
            try:
                self.logger.debug("尝试调用 submitQuestionnaire()")
                self.driver.execute_script("return submitQuestionnaire();")
                time.sleep(2)
                
                if self._check_submission_success():
                    self.logger.info("通过 submitQuestionnaire() 成功提交")
                    return True
            except Exception as e:
                self.logger.warning(f"submitQuestionnaire() 调用失败：{e}")
            
            # 方案 3：查找提交按钮并使用 JS 点击
            try:
                # 查找提交按钮或下一页按钮
                submit_buttons = self.driver.find_elements(By.XPATH,
                    "//div[@id='ctlNext'] | //a[contains(@onclick, 'show_next_page')] | "
                    "//a[contains(@onclick, 'submitQuestionnaire')] | "
                    "//button[contains(., '提交')] | //button[contains(., '下一页')]"
                )
                
                if submit_buttons:
                    self.logger.debug(f"找到 {{len(submit_buttons)}} 个提交按钮")
                    
                    for btn in submit_buttons:
                        try:
                            self.js_click(btn, "提交按钮")
                            time.sleep(2)
                            
                            if self._check_submission_success():
                                self.logger.info("通过 JS 点击提交成功")
                                return True
                        except Exception as e:
                            continue
            except Exception as e:
                self.logger.warning(f"查找提交按钮失败：{{e}}")
            
            self.logger.warning("未找到提交按钮或提交失败")
            return False
                
        except Exception as e:
            self.logger.error(f"提交失败：{{e}}")
            return False"""

new_submit = """def submit_questionnaire(self) -> bool:
        \"\"\"
        提交问卷 - 使用新的修复函数
        \"\"\"
        return submit_questionnaire_new(self.driver, self.logger)"""

content = content.replace(old_submit, new_submit)

# 写入新文件
with open('/home/claw/.openclaw/workspace/wjx-automator/src/core/questionnaire.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ questionnaire.py 修改完成！")
print("  - 添加了新的导入")
print("  - 更新了填充函数调用")
print("  - 更新了 submit_questionnaire 方法")
