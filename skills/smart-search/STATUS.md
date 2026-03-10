# SmartSearch 智能降级网络搜索系统
> 综合搜索工具 - 四层架构保证稳定性

## ⚡ 项目状态

**创建时间**: 2026-03-10 01:59 UTC  
**当前状态**: ✅ 已完成基础开发  
**测试状态**: 🔧 修复导入问题中

## 📦 项目结构

```
skills/smart-search/
├── smart_search.py              # 主程序
├── config.py                    # 配置
├── requirements.txt             # Python 依赖
├── README.md                    # 完整项目文档
├── SKILL.md                     # 使用说明
├── QUICKSTART.md                # 快速入门
├── venv/                        # 虚拟环境
├── engines/                     # 搜索引擎模块
│   ├── multi_search.py         # 17 引擎并行
│   ├── tavily_search.py        # Tavily AI
│   └── web_markdown.py         # r.jina.ai 等
├── scraper/                     # 深度抓取模块
│   ├── r_jina_ai.py            # r.jina.ai 抓取
│   ├── markdown_new.py         # Cloudflare 回退
│   ├── defuddle.py             # defuddle.md
│   └── scrapling_scraper.py    # 本地 Python scraper
├── utils/                       # 工具模块
│   ├── fallback_chain.py       # 降级链
│   ├── content_processor.py    # 内容处理
│   └── logger.py               # 日志
└── tests/                       # 测试套件
```

## 🎯 核心特性

1. **四层架构**
   - L1 广泛搜索:17 个引擎并行
   - L2 目标发现：智能筛选 Top N
   - L3 深度抓取：4 层降级策略
   - L4 结果整合：去重合并输出

2. **智能降级策略**
   ```
   r.jina.ai → markdown.new → defuddle.md → Scrapling
   ```

3. **并行处理**
   - 异步并发 (aiohttp)
   - 超时控制
   - 自动重试 (最多 2 次)

4. **17 个搜索引擎**
   - Google, Bing, DuckDuckGo, Yahoo, Baidu, Sogou, 360, Yandex, ASK, WolframAlpha, Quora, Stack Overflow, GitHub, Wikipedia, arXiv, PubMed, Reddit

## 🔧 使用方式

### 命令行模式
```bash
cd /home/claw/.openclaw/workspace/skills/smart-search
source venv/bin/activate

# 简单搜索
python smart_search.py "Python 教程"

# 深度搜索
python smart_search.py "机器学习" --depth 5 --max-results 10

# JSON 格式
python smart_search.py "人工智能" --format json
```

### Python API
```python
from smart_search import SmartSearch

searcher = SmartSearch()
response = await searcher.search("Python 教程", depth=3, max_results=5)

for result in response.results:
    print(f"{result.title}: {result.url}")
    print(f"来源：{result.source}")
    print(f"抓取方式：{result.fetch_method}")
```

## 📝 测试记录

### ✅ 已测试成功
- [x] 模块导入：`engines.multi_search` 可以正常导入
- [x] 虚拟环境配置完成
- [x] 所有依赖安装成功

### 🔧 待修复
- [ ] 导入问题：修复 `from .config` 相对导入
- [ ] 完整功能测试
- [ ] 网络搜索集成

### ⚠️ 注意事项
1. Perplexity API 需要配置密钥
2. 修复导入后需完整测试
3. 首次使用需运行 `pip install -r requirements.txt`

## 🚀 下一步
1. 等待御坂妹妹 16 号修复导入问题
2. 测试完整搜索流程
3. 集成到 OpenClaw 工具系统
4. 编写使用示例文档

---

**维护者**: 御坂美琴一号  
**状态**: 开发中，待完整测试
