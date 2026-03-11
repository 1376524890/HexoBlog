# 快速上手指南 (QUICKSTART.md)

## 🚀 5 分钟快速开始

### 第 1 步：安装依赖

```bash
cd wjx-automator
pip install -r requirements.txt
```

### 第 2 步：准备数据

数据格式：`data/q28_response.csv`

```csv
question_id,type,total_responses,options
1,single,210,"选项 A (35%),选项 B (25%),选项 C (20%),选项 D (20%)"
2,multiple,210,"选项 A (40%),选项 B (35%),选项 C (25%)"
...
```

**问题类型**：
- `single` - 单选题
- `multiple` - 多选题
- `scale` - 量表题（1-5 分）
- `short_answer` - 简答题

### 第 3 步：配置问卷

编辑 `config.json`：

```json
{
  "questionnaire": {
    "url": "https://v.wjx.cn/vm/PhfZxRV.aspx"
  }
}
```

### 第 4 步：测试答案生成

```bash
python3 test_basic.py
```

### 第 5 步：实际填写问卷

```bash
python3 main.py --data data/q28_response.csv --workers 5
```

## 📊 数据格式详解

### CSV 数据结构

| 列名 | 说明 | 示例 |
|------|------|------|
| `question_id` | 问题编号 | "1", "2", ... |
| `type` | 问题类型 | single/multiple/scale/short_answer |
| `total_responses` | 总样本数 | 210 |
| `options` | 选项分布 | "选项 A (35%), 选项 B (25%)" |

### 选项分布格式

```
选项名称 1 (百分比%), 选项名称 2 (百分比%), ...
```

**示例**：
```csv
"非常了解 (15%),比较了解 (30%),一般了解 (35%),不太了解 (20%)"
"1 (10%),2 (15%),3 (30%),4 (30%),5 (15%)"
```

## 🎯 核心功能

### 1. 智能答案生成

**单选题** - 按分布随机选择
```python
# 分布：A:35%, B:25%, C:20%, D:20%
# 系统会按此比例随机选择答案
```

**多选题** - 智能组合选项
```python
# 分布：A:40%, B:35%, C:25%
# 系统会根据概率智能组合选项
```

**量表题** - 按分布采样 1-5 分
```python
# 分布：1:10%, 2:15%, 3:30%, 4:30%, 5:15%
# 严格按照分布选择评分
```

**简答题** - AI 生成合理答案
```python
# 基于主题自动生成符合上下文的答案
# 主题：AI 技术在历史文化实景戏剧中的应用
```

### 2. 并发加速

```bash
python3 main.py --workers 10  # 10 个线程并发
```

### 3. 干燥测试

```bash
python3 main.py --dry-run  # 仅生成答案，不提交
```

## 🔧 常见问题

### Q: 如何生成自己的数据文件？

**方法 1**：从 Excel 转换
1. 在 Excel 中整理数据
2. 导出为 CSV 格式
3. 调整列名和问题类型

**方法 2**：使用脚本生成
```python
import csv

data = [
    ['question_id', 'type', 'total_responses', 'options'],
    ['1', 'single', 210, '"选项 A (35%),选项 B (25%),选项 C (20%),选项 D (20%)"'],
    # ...
]

with open('data/my_questions.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)
```

### Q: 如何调整问卷 URL？

编辑 `config.json`：
```json
{
  "questionnaire": {
    "url": "https://v.wjx.cn/vm/YOUR_QUESTION_ID.aspx"
  }
}
```

### Q: 如何查看日志？

日志保存在 `logs/` 目录：
```bash
tail -f logs/wjx_automator.log
```

### Q: 如何调整并发数？

命令行参数：
```bash
python3 main.py --workers 10
```

配置文件：
```json
{
  "execution": {
    "workers": 10
  }
}
```

## 📝 使用建议

### 1. 数据准备
- ✅ 确保 CSV 数据准确
- ✅ 百分比总和应为 100%
- ✅ 问题类型标注正确

### 2. 运行测试
- ✅ 先用 `--dry-run` 测试
- ✅ 检查生成的答案是否符合预期

### 3. 实际填写
- ✅ 设置合理的并发数（2-10）
- ✅ 设置合理的填写间隔
- ✅ 监控日志输出

### 4. 性能调优
- 增加并发数 → 提高速度
- 减少延迟 → 提高速度
- 使用更快的网络 → 提高稳定性

## 🎓 进阶使用

### 自定义答案生成器

继承 `AnswerGenerator` 类：

```python
from src.utils.generators import AnswerGenerator

class CustomGenerator(AnswerGenerator):
    def generate_single_choice(self, question_id):
        # 自定义逻辑
        return "自定义答案"
```

### 调整 XPath 配置

编辑 `xpath_config.json`，修改元素定位器。

### 添加代理

```json
{
  "advanced": {
    "proxy": "http://proxy:port"
  }
}
```

## ⚠️ 注意事项

1. **使用合规**：请仅在合法场景使用
2. **频率控制**：避免被封禁
3. **数据准确性**：CSV 质量决定结果
4. **网络稳定**：确保填写过程不中断

---

_祝你使用愉快！_ ⚡
