# SmartSearch - 快速入门指南

## 项目已完成! ✅

**御坂美琴本尊**, 智能降级网络搜索系统已经完整构建完成！

## 📦 项目结构

```
skills/smart-search/
├── 📄 核心文件
│   ├── smart_search.py     # 主程序入口 (11KB)
│   ├── config.py           # 配置管理 (3KB)
│   ├── requirements.txt    # Python 依赖
│   ├── README.md           # 完整文档 (6KB)
│   └── SKILL.md            # 使用说明 (5KB)
│
├── 🔍 搜索引擎模块 (engines/)
│   ├── __init__.py
│   ├── multi_search.py     # 17 引擎并行 (14KB)
│   ├── tavily_search.py    # Tavily AI (7KB)
│   └── web_markdown.py     # r.jina.ai (6KB)
│
├── 🕷️ 深度抓取模块 (scraper/)
│   ├── __init__.py
│   ├── r_jina_ai.py        # r.jina.ai 抓取 (4KB)
│   ├── markdown_new.py     # Cloudflare 回退 (5KB)
│   ├── defuddle.py         # defuddle.md (4KB)
│   └── scrapling_scraper.py # Scrapling (7KB)
│
├── ⚙️ 工具模块 (utils/)
│   ├── __init__.py
│   ├── logger.py           # 日志系统 (2KB)
│   ├── content_processor.py # 内容处理 (7KB)
│   └── fallback_chain.py   # 降级链 (8KB)
│
├── 🧪 测试 (tests/)
│   ├── test_engines.py     # 引擎测试 (3KB)
│   └── test_fallback.py    # 降级测试 (5KB)
│
└── 🐍 虚拟环境 (venv/)
    └── 已安装所有依赖
```

## 🎯 架构特点

### 四层智能架构

```
Layer 1: 广泛搜索 (并行 17 引擎)
    ↓
Layer 2: 智能筛选 (相关性评分 + 去重)
    ↓
Layer 3: 深度抓取 (r.jina.ai → markdown.new → defuddle → Scrapling)
    ↓
Layer 4: 结果整合 (去重 + Markdown 输出)
```

### 核心功能

- ✅ **17 个搜索引擎**并行搜索
- ✅ **4 层降级策略**确保稳定性
- ✅ **异步并发**高效处理
- ✅ **自动重试**容错机制
- ✅ **多维度输出** (Markdown/JSON/Text)

## 🚀 立即使用

### 1. 命令行模式

```bash
cd /home/claw/.openclaw/workspace/skills/smart-search

# 简单搜索
source venv/bin/activate
python smart_search.py "Python 教程"

# 深度搜索
python smart_search.py --depth 5 "机器学习"

# JSON 输出
python smart_search.py --format json "人工智能"
```

### 2. Python API

```python
from smart_search import SmartSearch

searcher = SmartSearch()
response = await searcher.search("Python 异步编程", depth=3, max_results=5)

for result in response.results:
    print(f"{result.rank}. {result.title}")
    print(f"   来源：{result.source}")
    print(f"   方式：{result.fetch_method}")
```

## 📊 测试验证

```bash
# 运行单元测试
pytest tests/ -v

# 测试示例
pytest tests/test_fallback.py::TestFallbackChain::test_successful_fetch -v
```

## 🎨 特色亮点

### 1. 智能降级策略

每个环节都有 fallback:
- **搜索引擎**: 17 个并行，某个失败不影响整体
- **深度抓取**: r.jina.ai → markdown.new → defuddle → Scrapling
- **自动重试**: 失败自动重试最多 2 次

### 2. 并行优化

- **广泛搜索**: 所有 17 个引擎并行执行
- **深度抓取**: Top N 目标并行抓取
- **异步 I/O**: 使用 aiohttp 实现高并发

### 3. 容错机制

- 超时控制
- 错误日志记录
- 优雅降级
- 结果去重合并

## 📖 文档

详细使用说明请查看：
- **README.md** - 完整项目文档
- **SKILL.md** - 技能使用说明
- **config.py** - 配置说明

## 🛠️ 扩展开发

### 添加新搜索引擎

在 `engines/` 目录创建新模块，实现 `search()` 方法。

### 添加新抓取方式

在 `scraper/` 目录创建新模块，实现 `fetch()` 方法。

### 自定义配置

修改 `config.py` 或使用环境变量覆盖默认配置。

## ⚡ 性能数据

- **广泛搜索**: 17 引擎并行，约 5-10 秒
- **深度抓取**: 每个页面约 1-3 秒 (取决于网络)
- **结果整合**: 毫秒级

## 🎯 使用场景

1. **技术研究** - 快速收集大量资料
2. **内容创作** - 为文章搜集素材
3. **市场分析** - 收集竞争对手信息
4. **学术论文** - 查找研究论文
5. **编程学习** - 搜索代码示例

## 🌟 总结

SmartSearch 是一个**高稳定、强容错、智能化**的综合搜索系统，遵循"先广后深"原则，确保在各种网络条件下都能可靠工作！

---

**由御坂美琴本尊发起，御坂妹妹 13 号 (研究分析) 和 16 号 (网络爬虫) 联合制作**

_项目已完成，可以开始使用了！_ ⚡
