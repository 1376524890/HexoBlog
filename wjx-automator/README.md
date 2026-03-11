# 问卷星自动填写系统 (WJX Automator)

> 基于统计分布的问卷星批量自动填写系统 ⚡

## 📖 项目简介

这是一个专业的问卷星（WJX）自动填写系统，根据 CSV 统计数据智能生成答案，支持批量并发填写。

**当前数据**: 750 份样本，19 道题目（单选 4 + 多选 5 + 量表 10 + 简答 4）

**核心特性**：
- ✅ 基于 Selenium 浏览器自动化
- ✅ 根据 CSV 统计分布智能生成答案
- ✅ 支持多线程并发填写（加速）
- ✅ 完整的异常处理和重试机制
- ✅ 详细的日志记录系统
- ✅ 配置化设计，易于扩展

## 🎯 适用场景

- 学术研究：批量收集问卷数据
- 市场调研：模拟不同用户群体的回答
- 压力测试：测试问卷系统承载能力
- 数据分析：验证问卷统计合理性

## 📋 系统要求

- Python 3.8+
- Google Chrome 浏览器
- ChromeDriver（自动下载）
- 问卷星问卷链接

## 🚀 快速开始

### 1. 安装依赖

```bash
cd wjx-automator
pip install -r requirements.txt
```

### 2. 准备数据

将你的问卷统计数据准备好，格式为 CSV：

```csv
question_id,type,total_responses,options
1,single,750,"选项 A (35%),选项 B (25%),选项 C (20%),选项 D (20%)"
2,multiple,750,"选项 A (40%),选项 B (35%),选项 C (25%)"
...
```

**当前数据文件**: `data/q28_response_750.csv`

### 3. 配置系统

编辑 `config.json`：

```json
{
  "questionnaire": {
    "url": "https://v.wjx.cn/vm/PhfZxRV.aspx",
    "total_questions": 28
  },
  "execution": {
    "workers": 5,
    "max_retries": 3
  },
  "data": {
    "stats_file": "data/q28_response_750.csv"
  }
}
```

### 4. 运行

**模式 1: 实际填写问卷**

```bash
python main.py --data data/q28_response_750.csv --workers 5
```

**模式 2: 干燥测试（仅生成答案示例）**

```bash
python main.py --dry-run --data data/q28_response_750.csv
```

**模式 3: 详细日志模式**

```bash
python main.py --verbose --data data/q28_response_750.csv
```

**模式 4: 仅测试答案生成**

```bash
python3 test_basic.py
```

## 📚 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--config` | `-c` | 配置文件路径 | config.json |
| `--data` | `-d` | 统计数据文件路径 | data/q28_response_750.csv |
| `--xpath` | `-x` | XPath 配置路径 | xpath_config.json |
| `--workers` | `-w` | 并发线程数 | 5 |
| `--dry-run` | - | 仅测试，不提交 | False |
| `--verbose` | `-v` | 详细日志模式 | False |
| `--output-dir` | - | 日志输出目录 | logs |

## 🏗️ 项目结构

```
wjx-automator/
├── main.py                 # 主程序入口
├── config.json             # 主配置文件
├── xpath_config.json       # XPath 选择器配置
├── README.md               # 项目文档
├── requirements.txt        # Python 依赖
├── quickstart.sh           # 快速启动脚本
├── test_basic.py           # 基础测试脚本
├── check_elements.py       # 元素检查工具
├── data/
│   ├── q28_response_750.csv  # 750 份问卷统计数据
│   └── question_stats.json # 数据统计 JSON 示例
├── logs/                   # 日志输出目录
└── src/
    ├── __init__.py
    ├── core/
    │   └── questionnaire.py # 核心问卷填充器
    ├── utils/
    │   ├── logger.py       # 日志工具
    │   ├── stats.py        # 统计数据处理
    │   └── generators.py   # 答案生成器
    └── models/
        └── config.py       # 配置模型
```

## 🧠 核心功能详解

### 1. 智能答案生成

系统根据 CSV 中的统计分布智能生成答案：

**单选题**：按分布概率随机选择
```python
# 示例：选项分布 A:35%, B:25%, C:20%, D:20%
# 系统会按这个比例随机选择答案
```

**多选题**：智能组合选项
```python
# 示例：选项分布 技术认知:40%, 应用场景:35%, ...
# 系统会根据每个选项的概率智能组合
```

**量表题**：按分布采样 1-5 分
```python
# 示例：1:10%, 2:15%, 3:30%, 4:30%, 5:15%
# 系统会严格按照这个分布选择评分
```

**简答题**：AI 生成合理答案
```python
# 基于主题自动生成符合上下文的答案
# 主题：AI 技术在历史文化实景戏剧中的应用
```

### 2. 并发加速

使用 `ThreadPoolExecutor` 实现并发填写：

```python
# 默认 5 个线程并发执行
python main.py --workers 10  # 可以调整线程数
```

### 3. 异常处理

完善的异常处理和重试机制：

- 元素定位失败 → 自动重试
- 网络超时 → 重新加载页面
- 提交失败 → 自动重试
- 浏览器崩溃 → 自动重启

### 4. 日志记录

详细的日志系统：

```
2026-03-11 02:45:23 - INFO - 问卷星自动填写系统启动
2026-03-11 02:45:24 - INFO - Chrome 浏览器初始化成功
2026-03-11 02:45:26 - INFO - 问卷页面加载成功
2026-03-11 02:45:30 - INFO - 记录 1 填写完成
2026-03-11 02:45:35 - INFO - 进度：50.0% (成功：105, 失败：0)
```

## 📊 数据统计格式说明

### CSV 文件格式

```csv
question_id,type,total_responses,options
```

**字段说明**：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `question_id` | string | 问题编号 | "1", "2", ... |
| `type` | string | 问题类型 | single, multiple, scale, short_answer |
| `total_responses` | int | 总样本数 | 750 |
| `options` | string | 选项分布 | "选项 A (35%), 选项 B (25%)" |

**问题类型**：

- `single`: 单选题
- `multiple`: 多选题
- `scale`: 量表题（1-5 分）
- `short_answer`: 简答题

**选项分布格式**：

```
选项 1 (30%), 选项 2 (50%), 选项 3 (20%)
```

或 JSON 格式：

```json
{"选项 1": 0.3, "选项 2": 0.5, "选项 3": 0.2}
```

## ⚙️ 配置说明

### config.json

```json
{
  "questionnaire": {
    "url": "问卷链接",
    "total_questions": 28,
    "question_types": {
      "single_choice": [1, 5, 6, 14],
      "multiple_choice": [2, 3, 4, 11, 13],
      "scale": [7, 8, 9, 10, 12, 15, 16, 17, 18, 24],
      "short_answer": [25, 26, 27, 28]
    },
    "total_responses": 750
  },
  "browser": {
    "headless": true,
    "window_size": [1920, 1080],
    "explicit_wait": 10
  },
  "execution": {
    "workers": 5,
    "max_retries": 3,
    "retry_delay": 2
  }
}
```

### xpath_config.json

XPath 选择器配置，用于定位问卷元素。系统提供了默认配置，如需自定义问卷结构，可调整 XPath 选择器。

## 🛠️ 高级用法

### 自定义答案生成器

继承 `AnswerGenerator` 类，实现自己的答案生成逻辑：

```python
from src.utils.generators import AnswerGenerator

class CustomGenerator(AnswerGenerator):
    def generate_answer(self, question_id):
        # 自定义逻辑
        return "自定义答案"
```

### 监控进度

查看实时日志输出：

```bash
tail -f logs/wjx_automator.log
```

### 断点续填

系统会自动记录日志，可以通过日志查看进度。如需重新开始，修改 `start_id` 参数。

## ⚠️ 注意事项

1. **使用规范**：请仅在合法合规的场景使用本系统
2. **频率控制**：设置合理的 `delay_between_submissions` 避免被封禁
3. **数据准确性**：CSV 数据质量直接影响结果
4. **网络环境**：确保网络稳定，避免频繁掉线
5. **浏览器版本**：保持 Chrome 和 ChromeDriver 版本一致

## 📝 开发计划

- [ ] 支持问卷分页处理
- [ ] 添加验证码识别
- [ ] 支持 Cookie 持久化
- [ ] 添加可视化进度条
- [ ] 支持自定义 XPath 配置
- [ ] 添加单元测试

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

## 👥 作者

**御坂网络** - Misaka Network

- GitHub: @yourusername
- Email: your.email@example.com

---

**免责声明**：本项目仅供学习研究使用，请遵守相关法律法规，勿用于非法用途。
