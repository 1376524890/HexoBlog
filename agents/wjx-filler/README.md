# 问卷星自动化工具

⚡ 由御坂美琴一号开发 | 基于原 wjx-filler 项目的配置友好版本

## 📋 功能特性

### 核心功能
- ✅ **多题型支持**: 单选、多选、文本框、下拉选择等
- ✅ **灵活配置**: JSON 配置文件，无需修改代码
- ✅ **自定义答案**: 支持多个答案集轮换使用
- ✅ **多线程并发**: 可配置并发数量和批次大小
- ✅ **代理支持**: 可选代理 IP 配置
- ✅ **地理位置**: 模拟指定地理位置
- ✅ **日志系统**: 详细的运行日志和异常记录
- ✅ **重试机制**: 自动重试和异常处理

### 技术栈
- Python 3.8+
- Selenium + Chrome Headless
- ThreadPoolExecutor 多线程
- Loguru 日志系统

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置问卷信息

编辑 `config/config.json`:

```json
{
  "questionnaire": {
    "url": "https://wjx.q.weixin.qq.com/t/xxxxxxxxx",
    "wait_timeout": 30,
    "element_timeout": 10
  },
  "fill_strategy": {
    "max_attempts": 3,
    "retry_delay": 2,
    "random_delay": true,
    "delay_range": [1, 3],
    "auto_submit": true
  },
  "answers": {
    "source_file": "answers/answers.json",
    "strategy": "rotate"
  },
  "concurrency": {
    "enabled": true,
    "max_workers": 5,
    "batch_size": 10
  }
}
```

### 3. 准备答案数据

编辑 `answers/answers.json`:

```json
{
  "answer_sets": [
    {
      "name": "用户画像 A",
      "answers": [
        {"question_index": 0, "type": "radio", "value": "选项 1"},
        {"question_index": 1, "type": "checkbox", "value": ["选项 A", "选项 B"]},
        {"question_index": 2, "type": "text", "value": "示例文本"}
      ]
    }
  ]
}
```

### 4. 运行工具

```bash
# 基本运行
python main.py

# 自定义配置文件路径
python main.py --config path/to/config.json
```

## 📖 配置详解

### config.json 配置项

#### questionnaire - 问卷基础配置
| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| url | string | 问卷星链接 | 必填 |
| wait_timeout | int | 页面加载超时 (秒) | 30 |
| element_timeout | int | 元素查找超时 (秒) | 10 |

#### fill_strategy - 填写策略
| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| max_attempts | int | 最大重试次数 | 3 |
| retry_delay | int | 重试间隔 (秒) | 2 |
| random_delay | bool | 是否随机延迟 | true |
| delay_range | array | 随机延迟范围 [min, max] | [1, 3] |
| auto_submit | bool | 是否自动提交 | true |

#### answers - 答案配置
| 字段 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| source_file | string | 答案文件路径 | - |
| strategy | string | 答案使用策略 | random, rotate, sequential |

#### proxy - 代理配置
| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | bool | 是否启用代理 |
| server | string | 代理服务器地址 |
| username | string | 代理用户名 (可选) |
| password | string | 代理密码 (可选) |

#### geolocation - 地理位置
| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | bool | 是否启用地理位置 |
| province | string | 省份 |
| city | string | 城市 |

#### concurrency - 并发控制
| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | bool | 是否启用多线程 |
| max_workers | int | 最大线程数 |
| batch_size | int | 每批处理数量 |

#### logging - 日志配置
| 字段 | 类型 | 说明 |
|------|------|------|
| level | string | 日志级别 (DEBUG/INFO/WARNING/ERROR) |
| file | string | 日志文件路径 |
| console | bool | 是否输出到控制台 |

### XPath 配置

编辑 `config/xpath_config.json` 来自定义元素选择器：

```json
{
  "selectors": {
    "question_container": "//div[@class='question-item']",
    "question_text": ".//div[@class='question-text']",
    "radio_option": ".//div[@class='radio-option']",
    "checkbox_option": ".//div[@class='checkbox-option']",
    "text_input": ".//input[@type='text']",
    "submit_button": ".//button[@type='submit']"
  }
}
```

## 🧩 答案策略说明

### rotate (默认)
按顺序轮换使用不同的答案集，适合多种用户画像场景。

### random
随机选择一个答案集，适合模拟真实用户行为。

### sequential
按顺序使用答案，适合需要固定答案的场景。

## 📝 使用示例

### 示例 1: 单用户填写
```python
from src.core.questionnaire import QuestionnaireFiller
from src.utils.config_loader import ConfigLoader
from src.utils.answer_strategy import AnswerStrategy

config = ConfigLoader.load('config/config.json')
answer_strategy = AnswerStrategy.from_config(config['answers'])
filler = QuestionnaireFiller(config, answer_strategy, logger)
filler.start()
```

### 示例 2: 多线程批量填写
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for i in range(10):
        future = executor.submit(filler.run_once)
        futures.append(future)
    
    for future in futures:
        future.result()
```

## 🔧 开发指南

### 项目结构
```
wjx-filler/
├── config/              # 配置文件目录
│   ├── config.json     # 主配置文件
│   └── xpath_config.json # XPath 选择器配置
├── answers/            # 答案数据目录
│   └── answers.json    # 答案文件
├── logs/               # 日志文件目录
├── tests/              # 测试文件目录
├── src/                # 源代码目录
│   ├── core/
│   │   └── questionnaire.py  # 问卷填充器核心
│   └── utils/
│       ├── config_loader.py  # 配置加载器
│       ├── logger.py         # 日志工具
│       ├── answer_strategy.py # 答案策略
│       └── browser_manager.py # 浏览器管理
├── main.py             # 主入口
├── requirements.txt    # 依赖列表
└── README.md           # 本文档
```

### 扩展开发

1. **添加新题型**: 在 `xpath_config.json` 中添加新的选择器
2. **自定义答案**: 修改 `answers/answers.json` 添加更多答案集
3. **调整策略**: 在 `answer_strategy.py` 中实现新的策略类

## ⚠️ 注意事项

1. **合法使用**: 请仅用于合法的问卷调查场景，遵守问卷星使用条款
2. **频率控制**: 注意控制填写频率，避免触发风控
3. **答案质量**: 确保答案与问卷内容匹配，避免明显错误
4. **网络环境**: 使用代理时确保网络稳定性

## 📄 许可证

本项目仅供学习研究使用。

---

**开发者**: 御坂美琴一号  
**版本**: 1.0.0  
**更新时间**: 2026-03-11
