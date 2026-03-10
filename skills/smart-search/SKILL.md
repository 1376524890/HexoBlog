# SmartSearch Skill - 使用说明

> **御坂妹妹 13 号 (研究分析师)** 和 **御坂妹妹 16 号 (网络爬虫)** 联合制作

## 🎯 技能概述

SmartSearch 是一个综合性网络搜索工具，通过四层架构实现高稳定性的搜索功能。

## 📋 技能信息

- **名称**: SmartSearch - 智能降级网络搜索
- **版本**: 1.0.0
- **类型**: 搜索工具
- **权限**: Level 3 (工作目录读写 + 网络搜索)
- **作者**: 御坂美琴本尊
- **维护**: 御坂妹妹 13 号、16 号

## 🚀 快速使用

### 命令行模式

```bash
# 进入项目目录
cd /home/claw/.openclaw/workspace/skills/smart-search

# 简单搜索
python smart_search.py "Python 教程"

# 深度搜索 (抓取更多页面)
python smart_search.py --depth 5 "机器学习"

# JSON 格式输出
python smart_search.py "人工智能" --format json

# 自定义输出目录
python smart_search.py "深度学习" --output ./results
```

### Python API 模式

```python
# 直接在代码中使用
from smart_search import SmartSearch

# 创建搜索器
searcher = SmartSearch()

# 异步搜索
response = await searcher.search(
    query="Python 教程",
    depth=3,
    max_results=5
)

# 同步搜索
# response = searcher.search_sync("Python 教程", depth=3, max_results=5)

# 获取结果
for result in response.results:
    print(f"{result.title}: {result.url}")
    print(f"内容：{result.content[:200]}...")
    print(f"来源：{result.source}")
    print(f"抓取方式：{result.fetch_method}")
    print()
```

## 📊 功能说明

### 四层架构

1. **Layer 1: 广泛搜索** - 并行 17 个搜索引擎
2. **Layer 2: 目标发现** - 智能筛选 Top N 结果
3. **Layer 3: 深度抓取** - 按降级顺序抓取内容
4. **Layer 4: 结果整合** - 去重合并，输出 Markdown

### 支持的搜索引擎 (17 个)

| 搜索引擎 | 类型 |
|---------|------|
| Google | 通用搜索 |
| Bing | 通用搜索 |
| DuckDuckGo | 隐私搜索 |
| Yahoo | 通用搜索 |
| Baidu | 中文搜索 |
| Sogou | 中文搜索 |
| 360 | 中文搜索 |
| Yandex | 俄语搜索 |
| ASK | 问答搜索 |
| WolframAlpha | 知识计算 |
| Quora | 问答社区 |
| Stack Overflow | 编程问答 |
| GitHub | 代码搜索 |
| Wikipedia | 百科搜索 |
| arXiv | 学术论文 |
| PubMed | 生物医学 |
| Reddit | 社区论坛 |

### 深度抓取降级链

1. **r.jina.ai** - 主要方式 (AI 优化)
2. **markdown.new** - Cloudflare 回退
3. **defuddle.md** - 备选方案
4. **Scrapling** - 本地 Python 爬虫 (绕过反爬)

## ⚙️ 配置说明

### 搜索配置 (`config.py`)

```python
from config import config

# 搜索参数
config.search.max_results = 20          # 最大返回结果数
config.search.timeout_seconds = 30      # 超时时间 (秒)
config.search.retries = 2               # 失败重试次数
config.search.concurrency = 10          # 并发数

# 结果筛选
config.search.top_n_results = 5         # 最终选择 Top N
config.search.relevance_threshold = 0.5 # 相关性阈值
config.search.similarity_threshold = 0.8 # 去重阈值

# 深度抓取配置
config.scraper.timeout_seconds = 30
config.scraper.max_content_length = 50000
config.scraper.retries = 2

# 降级策略顺序
config.scraper.fallback_chain = [
    "r_jina_ai",
    "markdown_new",
    "defuddle",
    "scrapling"
]
```

## 📈 使用建议

### 场景 1: 快速研究一个主题

```bash
python smart_search.py "Python 异步编程" --depth 2 --max-results 3
```

### 场景 2: 深入收集资料

```bash
python smart_search.py "机器学习入门" --depth 5 --max-results 10
```

### 场景 3: 批量搜索

```python
import asyncio
from smart_search import SmartSearch

async def batch_search(queries):
    searcher = SmartSearch()
    for query in queries:
        response = await searcher.search(query, depth=3)
        print(f"\n=== {query} ===")
        print(f"找到 {response.total} 个结果")
        for result in response.results[:3]:
            print(f"  - {result.title}")

# 批量搜索
queries = ["Python 教程", "JavaScript 基础", "React 入门"]
asyncio.run(batch_search(queries))
```

## 🔍 结果示例

```markdown
# Search Results

## 1. Python 异步编程指南
**来源**: r.jina.ai
**URL**: https://realpython.com/async-io-python/

Python 异步编程使用 asyncio 库...

---

## 2. 异步/并发指南
**来源**: markdown.new
**URL**: https://docs.python.org/3/library/asyncio.html

Python 官方 asyncio 文档...

---
```

## 🎓 扩展开发

### 添加自定义搜索引擎

在 `engines/` 目录创建新文件：

```python
from engines import SearchResult, SearchResponse

class CustomSearch:
    async def search(self, query: str) -> SearchResponse:
        # 实现搜索逻辑
        results = [
            SearchResult(
                title="结果标题",
                url="https://example.com",
                snippet="结果摘要",
                engine="Custom"
            )
        ]
        return SearchResponse(query=query, results=results)
```

### 添加自定义抓取方式

在 `scraper/` 目录创建新文件：

```python
from scraper import FetchResult

class CustomScraper:
    async def fetch(self, url: str) -> FetchResult:
        # 实现抓取逻辑
        return FetchResult(
            success=True,
            url=url,
            content="<markdown content>",
            title="Page Title",
            source="Custom",
            method="custom"
        )
```

## 📝 日志和调试

查看日志文件：

```bash
tail -f logs/smartsearch.log
```

启用调试模式：

```python
from config import LogConfig, LogLevel
LogConfig.level = LogLevel.DEBUG
```

## ⚠️ 注意事项

1. **API 配额**: 外部 API 有使用限制
2. **网络延迟**: 降级策略会耗费更多时间
3. **资源消耗**: 大量抓取占用带宽和 CPU
4. **合法使用**: 遵守 robots.txt 和使用条款

## 🔄 更新日志

### v1.0.0 (2024-03-10)
- ✨ 初始版本发布
- 🚀 17 个搜索引擎并行支持
- 🔄 四层智能降级架构
- 📊 完整的测试套件
- 📝 详细文档和使用指南

---

> 这是一个强大的搜索系统，遵循"先广后深"的原则，确保在各种网络条件下都能稳定工作。  
> 由 **御坂美琴本尊** 发起，**御坂妹妹 13 号** 和 **16 号** 联合制作
