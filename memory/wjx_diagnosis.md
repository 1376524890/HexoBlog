# 问卷星页面元素分析结果

**URL:** https://v.wjx.cn/vm/PhfZxRV.aspx  
**分析时间:** 2026-03-11 03:37 GMT+8  
**技术栈:** Puppeteer + Node.js

---

## 问卷星页面元素分析

### 【单选题】
- **题目:** 您是否在近 1 年内，体验过以下历史文化主题实景戏剧项目？
- **ID:** div1
- **Class:** field ui-field-contain
- **HTML:** `<div class="field ui-field-contain" id="div1" req="1" hasjump="1" anyjump="0" data-role="fieldcontain" type="3">...</div>`
- **推荐 XPath:** `//div[@id='div1'] | //div[contains(@class, 'field') and @type='3'][1]`
- **内部元素:**
  - 单选按钮：`input[type="radio"]` (name="q1", id="q1_1", "q1_2", "q1_3")
  - 标签容器：`div.ui-radio`
  - 题目文本：`div.topichtml`

### 【多选题】
- **题目:** 若您体验过相关项目，请问您在游览时是否接触过以下 AI/智能技术相关的体验项目？（未体验过项目请选最后一项）【多选题】
- **ID:** div2
- **Class:** field ui-field-contain
- **HTML:** `<div class="field ui-field-contain" id="div2" req="0" hasjump="0" anyjump="0" data-role="fieldcontain" type="4">...</div>`
- **推荐 XPath:** `//div[@id='div2'] | //div[contains(@class, 'field') and @type='4'][1]`
- **内部元素:**
  - 复选框：`input[type="checkbox"]` (name="q2", id="q2_1" ~ q2_8")
  - 标签容器：`div.ui-checkbox`
  - 题目文本：`div.topichtml`

### 【量表题】
- **结果:** 当前页面未找到典型的量表题（type="8"）
- **说明:** 该问卷可能未包含量表题，或量表题在后续页面

### 【简答题】
- **题目:** 结合您的真实体验，您认为目前历史文化实景戏剧里，AI 技术应用最大的亮点和最需要改进的地方分别是什么？
- **ID:** div25
- **Class:** field ui-field-contain
- **HTML:** `<div class="field ui-field-contain" id="div25" req="0" hasjump="0" anyjump="0" data-role="fieldcontain" type="1">...</div>`
- **推荐 XPath:** `//div[contains(@class, 'field') and @type='1'][1]`
- **内部元素:**
  - 输入框：`textarea` (class="form-control", name="q25")
  - 题目文本：`div.topichtml`

---

## 导航按钮

### 【上一页】
- **HTML:** `<a href="javascript:;" class="button white" style="margin: 0px;" onclick="show_prev_page();">上一页</a>`
- **推荐 XPath:** `//a[contains(@onclick, "show_prev_page")]`
- **Class:** button white

### 【下一页】
- **HTML:** `<a href="javascript:;" class="button mainBgColor" style="margin: 0px; background-color: #0095ff; color: #fff;" onclick="show_next_page();">下一页</a>`
- **推荐 XPath:** `//a[contains(@onclick, "show_next_page")]`
- **Class:** button mainBgColor

---

## JavaScript 函数

问卷星页面提供的可用函数：

1. **`show_next_page()`** - 跳转到下一页
2. **`show_prev_page()`** - 返回上一页
3. **`checkAnswer()`** - 验证答案
4. **`closeAll()`** - 关闭所有弹窗
5. **`ShareByLink()`** - 分享问卷链接
6. **`saveCanvas()`** - 保存画布内容

---

## 页面结构特征

### 主要 class 命名模式
- **题目容器:** `field ui-field-contain`
- **单选按钮:** `ui-radio`, `jqradio`, `jqradiowrapper`
- **复选框:** `ui-checkbox`, `jqcheckbox`, `jqcheckboxwrapper`
- **输入框:** `form-control`, `wj_q_answer`
- **题目文本:** `topichtml`
- **题目编号:** `topicnumber`
- **必填标记:** `req`
- **跳转标记:** `hasjump`, `anyjump`

### 题目 type 属性值
| Type | 题型 | 说明 |
|------|------|------|
| 1 | 简答题 | 文本输入框/文本域 |
| 3 | 单选题 | 单选按钮 |
| 4 | 多选题 | 复选框 |
| 8 | 量表题 | 矩阵量表 |

---

## 自动化填写建议

### 1. 单选题填写
```python
driver.find_element(By.XPATH, "//div[@id='div1']//input[@type='radio'][@value='1']").click()
```

### 2. 多选题填写
```python
driver.find_element(By.XPATH, "//div[@id='div2']//input[@type='checkbox'][@value='1']").click()
```

### 3. 简答题填写
```python
driver.find_element(By.XPATH, "//div[@id='div25']//textarea").send_keys("您的回答...")
```

### 4. 翻页操作
```python
# 下一页
driver.find_element(By.XPATH, "//a[contains(@onclick, 'show_next_page')]").click()

# 上一页
driver.find_element(By.XPATH, "//a[contains(@onclick, 'show_prev_page')]").click()
```

---

## 诊断总结

✅ **单选题** - 结构清晰，使用 `type="3"` 和 `div.field`  
✅ **多选题** - 结构清晰，使用 `type="4"` 和 `div.field`  
⚠️ **量表题** - 当前页面未发现，可能在后续页面  
✅ **简答题** - 使用 `type="1"` 和 `textarea`  
✅ **导航按钮** - 提供 `show_next_page()` 和 `show_prev_page()` 函数
