"""
问卷星自动填写系统 - 修复版本
使用 JavaScript 直接操作问卷星内部元素
"""

import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.models.config import Config
from src.utils.generators import AnswerGenerator
from src.utils.stats import load_question_stats
from questionnaire_new import (
    _fill_single_choice_new,
    _fill_multiple_choice_new,
    _fill_scale_question_new,
    _fill_short_answer_new,
    submit_questionnaire_new
)


class QuestionnaireAutoFiller:
    """
    问卷星自动填写器（修复版）
    
    关键修复:
    1. 所有点击操作使用 JavaScript execute_script()
    2. 单选题：点击 <a class="jqradio"> 而不是 <input>
    3. 多选题：点击 <a class="jqcheckbox"> 而不是 <input>
    4. 量表题：点击 <a class="jqradio"> 而不是 <input>
    5. 提交问卷：直接调用问卷星的 JavaScript 函数
    """
    
    def __init__(
        self,
        config: Config,
        question_stats: Dict[str, Any],
        xpath_config: str = "xpath_config.json",
        logger: Optional[logging.Logger] = None
    ):
        """初始化问卷填充器"""
        self.config = config
        self.question_stats = question_stats
        self.xpath_config = self._load_xpath_config(xpath_config)
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化答案生成器
        self.answer_generator = AnswerGenerator(question_stats)
        
        # 驱动初始化
        self.driver = None
        self._init_driver()
    
    def _load_xpath_config(self, filepath: str) -> Dict[str, Any]:
        """加载 XPath 配置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"加载 XPath 配置失败：{e}, 使用默认配置")
            return {}
    
    def _init_driver(self):
        """初始化 Chrome 浏览器"""
        try:
            chrome_options = Options()
            
            # 头模模式
            if self.config.browser.headless:
                chrome_options.add_argument("--headless")
            
            # 窗口设置
            chrome_options.add_argument(f"--window-size={self.config.browser.window_size[0]},{self.config.browser.window_size[1]}")
            
            # 用户代理
            chrome_options.add_argument(f"--user-agent={self.config.browser.user_agent}")
            
            # 性能优化
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-software-rasterizer")
            
            # 隐私和安全
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            
            # 无日志
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--silent")
            
            # 创建驱动
            if self.config.browser.driver_path:
                service = Service(self.config.browser.driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # 设置超时
            self.driver.set_page_load_timeout(self.config.browser.wait_timeout)
            
            # 隐藏 Automation 特征
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            self.logger.info("Chrome 浏览器初始化成功")
            
        except Exception as e:
            self.logger.error(f"浏览器初始化失败：{e}")
            raise
    
    def _navigate_to_questionnaire(self):
        """导航到问卷"""
        try:
            self.logger.info(f"正在打开问卷：{self.config.questionnaire.url}")
            self.driver.get(self.config.questionnaire.url)
            
            # 等待页面加载
            WebDriverWait(self.driver, self.config.browser.explicit_wait).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.logger.info("问卷页面加载成功")
            time.sleep(2)  # 等待动态内容
            
        except Exception as e:
            self.logger.error(f"导航失败：{e}")
            raise
    
    def find_element_safe(self, locator, timeout=10):
        """安全地查找元素"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            return None
    
    def js_click(self, element, description="元素") -> bool:
        """
        使用 JavaScript 点击元素（关键修复！）
        
        Args:
            element: Selenium 元素对象
            description: 元素描述（用于日志）
        
        Returns:
            是否成功
        """
        try:
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(0.3)
            self.logger.debug(f"JavaScript 点击成功：{description}")
            return True
        except Exception as e:
            self.logger.debug(f"JavaScript 点击失败 {description}: {e}")
            return False
    
    def js_click_by_xpath(self, xpath: str, description="元素", timeout: int = 10) -> bool:
        """
        使用 XPath 查找并使用 JavaScript 点击元素（推荐方式）
        
        Args:
            xpath: XPath 表达式
            description: 元素描述
            timeout: 等待超时时间
        
        Returns:
            是否成功
        """
        try:
            # 查找元素
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            
            # 使用 JavaScript 点击
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(0.3)
            
            self.logger.debug(f"JavaScript 点击成功 (XPath): {description}")
            return True
            
        except TimeoutException:
            self.logger.warning(f"找不到元素 (XPath): {description}")
            return False
        except Exception as e:
            self.logger.warning(f"点击失败 (XPath): {description} - {e}")
            return False
    
    def fill_question(self, question_container, question_id: str) -> Tuple[bool, str]:
        """
        填充单个问题
        
        Args:
            question_container: 问题容器元素
            question_id: 问题 ID
        
        Returns:
            (是否成功，答案内容)
        """
        try:
            # 生成答案
            answer = self.answer_generator.generate_answer(question_id)
            
            # 根据问题类型填充
            q_type = self.question_stats.get(str(question_id), {}).get('type', '').lower()
            
            if 'single' in q_type or 'radio' in q_type:
                return _fill_single_choice_new(question_container, answer, self.driver, self.logger)
            elif 'multi' in q_type or 'checkbox' in q_type:
                return _fill_multiple_choice_new(question_container, answer, self.driver, self.logger)
            elif 'scale' in q_type or 'rating' in q_type:
                return _fill_scale_question_new(question_container, answer, self.driver, self.logger)
            elif 'short' in q_type or 'text' in q_type or 'answer' in q_type:
                return _fill_short_answer_new(question_container, answer, self.driver, self.logger)
            else:
                # 默认：尝试自动识别
                return self._fill_auto(question_container, answer)
                
        except Exception as e:
            self.logger.error(f"填充问题 Q{question_id} 失败：{e}", exc_info=True)
            return False, str(e)
    
    def _fill_single_choice(self, container, answer: str) -> Tuple[bool, str]:
        """
        填充单选题 - 修复版
        
        问卷星结构:
        <div class="ui-radio">
          <input type="radio" id="q1_1" name="q1" value="1">
          <a class="jqradio"><span>选项文本</span></a>  <!-- 需要点击这个 -->
        </div>
        
        修复方法:
        1. 查找 input 的 id 或 name
        2. 查找对应的 jqradio 元素
        3. 使用 JavaScript click()
        """
        answer_value = str(answer).strip('"').strip("'")
        self.logger.debug(f"单选题填充：问题 ID={answer_value}")
        
        # 方案 1：通过 name 属性查找（问卷星单选使用 name 分组）
        # 格式：name="q1"，value="1" 或 value="选项文本"
        try:
            # 查找该容器内的所有 input[type='radio']
            radio_inputs = container.find_elements(By.XPATH, ".//input[@type='radio']")
            
            for radio in radio_inputs:
                radio_id = radio.get_attribute('id') or ''
                radio_name = radio.get_attribute('name') or ''
                radio_value = radio.get_attribute('value') or ''
                radio_text = radio.get_attribute('data-label') or ''
                
                # 检查是否匹配
                matches = (
                    answer_value in radio_id or  # 如：q1_1
                    answer_value == radio_value or  # 如：value="1"
                    answer_value in radio_text or  # 如：data-label="选项文本"
                    radio_text.endswith(answer_value)  # 选项文本包含答案
                )
                
                if matches:
                    # 找到对应的 jqradio，使用 JavaScript 点击
                    try:
                        jqradio = radio.find_element(By.XPATH, "..//a[@class='jqradio']")
                        self.js_click(jqradio, f"单选题选项 (ID={radio_id})")
                        return True, answer_value
                    except NoSuchElementException:
                        self.logger.warning(f"未找到 jqradio 元素")
                        continue
            
        except Exception as e:
            self.logger.warning(f"方案 1 失败：{e}")
        
        # 方案 2：通过 XPath 直接查找包含特定文本的 jqradio
        try:
            # 查找所有 jqradio，检查其文本内容
            jqradios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
            
            for jqradio in jqradios:
                text = jqradio.text.strip()
                # 检查文本是否包含答案
                if answer_value in text or text == answer_value:
                    self.js_click(jqradio, f"单选题选项 (文本={text})")
                    return True, answer_value
        except Exception as e:
            self.logger.warning(f"方案 2 失败：{e}")
        
        # 方案 3：如果答案看起来是数字（选项编号），按索引查找
        try:
            if answer_value.isdigit():
                idx = int(answer_value) - 1
                all_radios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
                if 0 <= idx < len(all_radios):
                    self.js_click(all_radios[idx], f"单选题选项 (索引={idx})")
                    return True, answer_value
        except Exception as e:
            self.logger.warning(f"方案 3 失败：{e}")
        
        self.logger.error(f"单选题填充失败，未找到选项：{answer_value}")
        return False, f"未找到选项：{answer_value}"
    
    def _fill_multiple_choice(self, container, answers: List[str]) -> Tuple[bool, str]:
        """
        填充多选题 - 修复版
        
        问卷星结构:
        <div class="ui-checkbox">
          <input type="checkbox" id="q2_1" name="q2" value="1">
          <a class="jqcheckbox"><span>选项文本</span></a>  <!-- 需要点击这个 -->
        </div>
        
        修复方法:
        1. 遍历所有答案
        2. 对每个答案查找对应的 jqcheckbox
        3. 使用 JavaScript click()
        """
        success_count = 0
        answer_list = answers if isinstance(answers, list) else [str(answers)]
        
        self.logger.debug(f"多选题填充：答案数={len(answer_list)}")
        
        # 方案 1：遍历所有 jqcheckbox，根据文本匹配
        try:
            jqcheckboxes = container.find_elements(By.XPATH, ".//a[@class='jqcheckbox']")
            
            for jqcheckbox in jqcheckboxes:
                text = jqcheckbox.text.strip()
                
                # 检查是否匹配任一答案
                for answer in answer_list:
                    answer_value = str(answer).strip('"').strip("'")
                    if answer_value in text or text == answer_value:
                        self.js_click(jqcheckbox, f"多选题选项 (文本={text})")
                        success_count += 1
                        break
        except Exception as e:
            self.logger.warning(f"方案 1 失败：{e}")
        
        # 方案 2：通过 input[type='checkbox'] 查找
        try:
            checkbox_inputs = container.find_elements(By.XPATH, ".//input[@type='checkbox']")
            
            for checkbox in checkbox_inputs:
                checkbox_id = checkbox.get_attribute('id') or ''
                checkbox_value = checkbox.get_attribute('value') or ''
                checkbox_name = checkbox.get_attribute('name') or ''
                
                # 检查是否匹配任一答案
                for answer in answer_list:
                    answer_value = str(answer).strip('"').strip("'")
                    
                    matches = (
                        answer_value in checkbox_id or
                        answer_value == checkbox_value or
                        answer_value in checkbox_name
                    )
                    
                    if matches:
                        try:
                            jqcheckbox = checkbox.find_element(By.XPATH, "..//a[@class='jqcheckbox']")
                            self.js_click(jqcheckbox, f"多选题选项 (ID={checkbox_id})")
                            success_count += 1
                            break
                        except NoSuchElementException:
                            continue
        except Exception as e:
            self.logger.warning(f"方案 2 失败：{e}")
        
        result = success_count > 0
        self.logger.info(f"多选题填充结果：{success_count}/{len(answer_list)} 个选项成功")
        return result, f"选择了 {success_count}/{len(answer_list)} 个选项"
    
    def _fill_scale_question(self, container, score: int) -> Tuple[bool, str]:
        """
        填充量表题（1-5 分）- 修复版
        
        问卷星量表：
        <div class="ui-radio">
          <input type="radio" id="q7_1" name="q7" value="1">
          <a class="jqradio">非常不同意</a>
        </div>
        <div class="ui-radio">
          <input type="radio" id="q7_2" name="q7" value="2">
          <a class="jqradio">不同意</a>
        </div>
        
        修复方法:
        1. 查找所有 a.jqradio 元素
        2. 根据分数或位置匹配
        3. 使用 JavaScript click()
        """
        score = int(score)
        self.logger.debug(f"量表题填充：分数={score}")
        
        # 方案 1：通过 jqradio 的文本内容匹配
        # 常见量表文本：非常不同意，不同意，一般，同意，非常同意
        scale_texts = {
            1: ['非常不同意', '非常差', '极差', '1'],
            2: ['不同意', '差', '较少', '2'],
            3: ['一般', '中立', '中等', '3'],
            4: ['同意', '好', '较多', '4'],
            5: ['非常同意', '非常好', '极好', '5']
        }
        
        try:
            jqradios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
            
            # 检查目标分数是否有对应的文本
            expected_texts = scale_texts.get(score, [])
            
            for jqradio in jqradios:
                text = jqradio.text.strip()
                
                # 如果是指定文本，直接点击
                if any(t in text for t in expected_texts) or text == str(score):
                    self.js_click(jqradio, f"量表题选项 (文本={text}, 分数={score})")
                    return True, str(score)
        except Exception as e:
            self.logger.warning(f"方案 1 失败：{e}")
        
        # 方案 2：通过 input 的 id 匹配（格式：q{question}_{score}）
        try:
            radio_inputs = container.find_elements(By.XPATH, ".//input[@type='radio']")
            
            for radio in radio_inputs:
                radio_id = radio.get_attribute('id') or ''
                
                # 检查是否匹配分数（例如：q7_3 表示第 7 题选 3 分）
                if radio_id.endswith(f"_{score}"):
                    try:
                        jqradio = radio.find_element(By.XPATH, "..//a[@class='jqradio']")
                        self.js_click(jqradio, f"量表题选项 (ID={radio_id})")
                        return True, str(score)
                    except NoSuchElementException:
                        continue
        except Exception as e:
            self.logger.warning(f"方案 2 失败：{e}")
        
        # 方案 3：通过值匹配（value="{score}"）
        try:
            radio_inputs = container.find_elements(By.XPATH, ".//input[@type='radio']")
            
            for radio in radio_inputs:
                radio_value = radio.get_attribute('value') or ''
                
                if radio_value == str(score):
                    try:
                        jqradio = radio.find_element(By.XPATH, "..//a[@class='jqradio']")
                        self.js_click(jqradio, f"量表题选项 (value={radio_value})")
                        return True, str(score)
                    except NoSuchElementException:
                        continue
        except Exception as e:
            self.logger.warning(f"方案 3 失败：{e}")
        
        self.logger.error(f"量表题填充失败，未找到选项：{score}")
        return False, f"未找到选项：{score}"
    
    def _fill_short_answer(self, container, answer: str) -> Tuple[bool, str]:
        """填充简答题"""
        try:
            # 查找所有文本输入框
            text_inputs = container.find_elements(By.XPATH, 
                ".//input[@type='text'] | .//textarea | .//input[contains(@class, 'input')]"
            )
            
            for text_input in text_inputs:
                try:
                    # 清空并填写
                    self.driver.execute_script("arguments[0].value = '';", text_input)
                    self.driver.execute_script("arguments[0].value = arguments[1];", 
                                              text_input, answer)
                    
                    # 触发事件（某些框架需要）
                    self.driver.execute_script("""
                        arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                        arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                    """, text_input)
                    
                    self.logger.debug(f"简答题填写成功：长度={len(answer)}")
                    return True, "已填写"
                except Exception as e:
                    self.logger.warning(f"文本框填写失败：{e}")
                    continue
            
            self.logger.error("简答题填充失败，未找到输入框")
            return False, "未找到输入框"
            
        except Exception as e:
            self.logger.error(f"简答题填充错误：{e}")
            return False, str(e)
    
    def _fill_auto(self, container, answer: Any) -> Tuple[bool, str]:
        """自动识别并填充"""
        answer_str = str(answer).strip('"').strip("'")
        
        # 尝试单选
        try:
            radios = container.find_elements(By.XPATH, ".//a[@class='jqradio']")
            if radios:
                # 如果答案看起来是数字（选项编号）
                if answer_str.isdigit():
                    idx = int(answer_str) - 1
                    if 0 <= idx < len(radios):
                        self.js_click(radios[idx], "自动填充 - 单选 (索引)")
                        return True, answer_str
        except Exception as e:
            self.logger.warning(f"单选自动填充失败：{e}")
        
        # 尝试文本输入
        try:
            text_inputs = container.find_elements(By.XPATH, 
                ".//input[@type='text'] | .//textarea"
            )
            if text_inputs:
                self.driver.execute_script("arguments[0].value = arguments[1];", 
                                          text_inputs[0], answer_str)
                self.logger.debug(f"自动填充 - 文本成功")
                return True, answer_str
        except Exception as e:
            self.logger.warning(f"文本自动填充失败：{e}")
        
        self.logger.warning("自动填充失败")
        return False, "自动填充失败"
    
    def submit_questionnaire(self) -> bool:
        """
        提交问卷 - 修复版
        
        问卷星提交机制:
        1. 直接调用 show_next_page() 或 submitQuestionnaire() JavaScript 函数
        2. 或者点击 div#ctlNext 使用 JS click
        """
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
                    self.logger.debug(f"找到 {len(submit_buttons)} 个提交按钮")
                    
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
                self.logger.warning(f"查找提交按钮失败：{e}")
            
            # 方案 4：查找下一页按钮
            try:
                next_btn = self.find_element_safe((By.XPATH, 
                    "//a[contains(@onclick, 'show_next_page') or contains(text(), '下一页')]"))
                
                if next_btn:
                    self.js_click(next_btn, "下一页按钮")
                    time.sleep(3)
                    
                    # 递归处理下一页
                    return self.submit_questionnaire()
            except Exception as e:
                self.logger.warning(f"下一页按钮处理失败：{e}")
            
            self.logger.error("所有提交方法都失败")
            return False
            
        except Exception as e:
            self.logger.error(f"提交过程错误：{e}", exc_info=True)
            return False
    
    def _check_submission_success(self) -> bool:
        """检查是否成功提交"""
        try:
            # 检查是否有提交成功页面或提示
            success_indicators = [
                "//div[contains(text(), '提交成功')]",
                "//div[contains(text(), '感谢您的参与')]",
                "//div[contains(@class, 'success')]",
                "//h1[contains(text(), '提交成功')]",
                "//div[contains(text(), '已提交')]"
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        self.logger.debug(f"找到成功标识：{indicator}")
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def fill_one_record(self, record_id: int) -> Dict[str, Any]:
        """
        填写单个问卷记录
        
        Args:
            record_id: 记录 ID（用于日志）
        
        Returns:
            结果字典
        """
        result = {
            'record_id': record_id,
            'success': False,
            'answers': {},
            'error': None,
            'start_time': None,
            'end_time': None
        }
        
        result['start_time'] = datetime.now().isoformat()
        
        try:
            # 刷新页面
            self.logger.debug(f"填写记录 {record_id}: 刷新页面")
            self.driver.refresh()
            time.sleep(2)
            
            # 导航到问卷
            self._navigate_to_questionnaire()
            
            # 查找所有问题容器
            # 问卷星结构：class="field ui-field-contain" id="div1", id="div2"...
            questions = self.driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'field') and contains(@class, 'ui-field-contain')]"
            )
            
            self.logger.debug(f"找到 {len(questions)} 个问题")
            
            # 填充每个问题
            for question in questions:
                # 尝试提取问题 ID
                q_id = self._extract_question_id(question)
                
                if not q_id:
                    continue
                
                self.logger.debug(f"填充问题 Q{q_id}")
                success, answer = self.fill_question(question, q_id)
                result['answers'][q_id] = {
                    'success': success,
                    'answer': answer
                }
                
                if not success:
                    self.logger.warning(f"问题 Q{q_id} 填充失败：{answer}")
                
                time.sleep(0.5)  # 避免过快
            
            # 提交问卷
            if self.submit_questionnaire():
                result['success'] = True
                self.logger.info(f"记录 {record_id} 填写完成")
            else:
                self.logger.error(f"记录 {record_id} 提交失败")
            
        except Exception as e:
            self.logger.error(f"记录 {record_id} 填写失败：{e}", exc_info=True)
            result['error'] = str(e)
        
        result['end_time'] = datetime.now().isoformat()
        
        return result
    
    def _extract_question_id(self, question_element) -> Optional[str]:
        """从问题元素中提取问题 ID"""
        # 问卷星结构：id="div1", id="div2"...
        div_id = question_element.get_attribute('id')
        
        if div_id and div_id.startswith('div'):
            try:
                return div_id.replace('div', '')
            except:
                pass
        
        return None
    
    def generate_fill_examples(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        生成填充示例（不实际提交）
        
        Args:
            count: 示例数量
        
        Returns:
            示例列表
        """
        examples = []
        
        for i in range(count):
            record_id = i + 1
            example = {
                'record_id': record_id,
                'answers': {}
            }
            
            for question_id in self.question_stats.keys():
                answer = self.answer_generator.generate_answer(question_id)
                example['answers'][question_id] = answer
            
            examples.append(example)
        
        return examples
    
    def batch_fill(
        self,
        total_records: int = 210,
        workers: int = 5,
        start_id: int = 1
    ) -> Dict[str, Any]:
        """
        批量填写问卷
        
        Args:
            total_records: 总记录数
            workers: 并发线程数
            start_id: 起始记录 ID
        
        Returns:
            统计结果
        """
        self.logger.info(f"开始批量填写：总记录={total_records}, 线程数={workers}")
        
        results = {
            'total': total_records,
            'success': 0,
            'failed': 0,
            'success_rate': 0.0,
            'records': []
        }
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # 提交所有任务
            future_to_record = {
                executor.submit(self.fill_one_record, record_id): record_id
                for record_id in range(start_id, start_id + total_records)
            }
            
            # 收集结果
            for future in as_completed(future_to_record):
                record_id = future_to_record[future]
                try:
                    result = future.result()
                    results['records'].append(result)
                    
                    if result['success']:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                    
                    # 显示进度
                    progress = (record_id - start_id + 1) / total_records * 100
                    self.logger.info(f"进度：{progress:.1f}% (成功：{results['success']}, 失败：{results['failed']})")
                    
                    # 间隔控制
                    time.sleep(self.config.execution.delay_between_submissions)
                    
                except Exception as e:
                    self.logger.error(f"记录 {record_id} 处理失败：{e}")
                    results['failed'] += 1
        
        # 计算成功率
        if results['total'] > 0:
            results['success_rate'] = results['success'] / results['total'] * 100
        
        self.logger.info(f"批量填写完成，成功率：{results['success_rate']:.2f}%")
        
        return results
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.logger.info("关闭浏览器")
            self.driver.quit()
            self.driver = None
