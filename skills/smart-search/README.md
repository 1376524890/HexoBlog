# SmartSearch 技能文档
**创建时间**: 2026-03-10 04:57 UTC  
**作者**: 御坂美琴本尊  
**维护**: 御坂妹妹 13 号、16 号

---

## 📍 技能位置

```
/home/claw/.openclaw/workspace/skills/smart-search/
```

---

## 🎯 技能概述

SmartSearch 是一个**综合性网络搜索工具**，通过四层架构实现高稳定性的搜索功能：

### 四层架构

1. **Layer 1: 广泛搜索** - 并行 17 个搜索引擎
2. **Layer 2: 目标发现** - 智能筛选 Top N 结果
3. **Layer 3: 深度抓取** - 按降级顺序抓取内容
4. **Layer 4: 结果整合** - 去重合并，输出 Markdown

---

## 🔍 支持的搜索引擎（17 个）

| 搜索引擎 | 类型 |
|---------|------|
| Google, Bing, Yahoo | 通用搜索 |
| DuckDuckGo | 隐私搜索 |
| Baidu, Sogou, 360 | 中文搜索 |
| Yandex, ASK | 其他语言 |
| WolframAlpha, Quora | 知识问答 |
| Stack Overflow, GitHub | 开发者 |
| Wikipedia, arXiv, PubMed | 知识学术 |
| Reddit | 社区 |

---

## 🔄 降级抓取链

1. **r.jina.ai** - AI 优化（主要）
2. **markdown.new** - Cloudflare 回退
3. **defuddle.md** - 备选方案
4. **Scrapling** - 本地 Python 爬虫（绕过反爬）

---

## 🚀 使用方式

### 方法 1: 命令行模式

```bash
# 简单搜索
python /home/claw/.openclaw/workspace/skills/smart-search/smart_search.py "搜索关键词"

# 深度搜索（抓取更多页面）
python /home/claw/.openclaw/workspace/skills/smart-search/smart_search.py --depth 5 "机器学习"

# JSON 格式输出
python /home/claw/.openclaw/workspace/skills/smart-search/smart_search.py "人工智能" --format json

# 自定义输出目录
python /home/claw/.openclaw/workspace/skills/smart-search/smart_search.py "深度学习" --output ./results
```

### 方法 2: Python API

```python
from smart_search import SmartSearch

# 创建搜索器
searcher = SmartSearch()

# 异步搜索
response = await searcher.search(
    query="Python 教程",
    depth=3,
    max_results=5
)

# 获取结果
for result in response.results:
    print(f"{result.title}: {result.url}")
    print(f"内容：{result.content[:200]}...")
    print(f"来源：{result.source}")
    print(f"抓取方式：{result.fetch_method}")
```

### 方法 3: 通过 web_fetch（御坂大人专用）

御坂大人可以直接说：
> "帮我搜索这个网页"

御坂妹妹会自动调用：
```python
web_fetch({
  "url": "https://r.jina.ai/https://example.com",
  "extractMode": "markdown"
})
```

---

## 📝 使用建议

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

---

## 🎯 御坂美琴一号的使用规范

### ✅ 正确的任务分配

**【网络搜索】** → 分派给御坂妹妹 16 号 (`web-crawler`)

1. **简单需求**（单个 URL 抓取）：
   - 御坂妹妹 16 号执行 `web-markdown-search` skill
   - 使用 `web_fetch({url: "https://r.jina.ai/URL"})`

2. **复杂任务**（多引擎搜索）：
   - 御坂妹妹 16 号执行 `smart-search` skill
   - 使用命令行或 Python API

### ❌ 御坂美琴一号 NOT 要做的事情

- 不执行任何实际搜索
- 不分派给错误的 Agent
- 不使用错误的技能路径

---

## 📚 相关文件

- **技能文档**: `/home/claw/.openclaw/workspace/skills/smart-search/SKILL.md`
- **脚本文件**: `/home/claw/.openclaw/workspace/skills/smart-search/smart_search.py`
- **配置**: `/home/claw/.openclaw/workspace/skills/smart-search/config.py`

---

## 🔄 更新记录

- **2026-03-10 04:57** - 御坂美琴一号记录此文档
- **2026-03-10 04:46** - 御坂妹妹 16 号首次使用 smart-search 搜索御坂美琴
- **2026-03-10 04:45** - 御坂美琴一号发现技能位置错误

---

> 这是一个强大的搜索系统，遵循"先广后深"的原则，确保在各种网络条件下都能稳定工作。  
> 由 **御坂美琴本尊** 发起，**御坂妹妹 13 号** 和 **16 号** 联合制作
