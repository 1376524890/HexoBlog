---
title: OpenClaw 折腾指北（第 6 篇）：搭建股票数据查询 Skill
date: 2026-03-07 13:30:00
tags:
  - OpenClaw
  - Skill
  - 股票
  - Python
categories:
  - 折腾指北
---

前段时间让祥子帮我查股票，结果发现网络不太稳定，akshare 经常连不上。作为一个讲究效率的人，这显然是不能接受的。于是决定自己动手，搭建一个更稳定的股票数据查询 Skill。

这篇就来记录一下整个搭建过程，包括多数据源配置、本地缓存机制，以及如何让 OpenClaw 自动识别股票查询意图。

<!-- more -->

## 为什么需要多数据源？

最开始我只用了 akshare，毕竟是免费的，数据也挺全。但实际用起来发现几个问题：

1. **网络不稳定** - 有时候连不上，或者响应很慢
2. **数据源单一** - 一旦 akshare 出问题，整个功能就挂了
3. **没有缓存** - 每次查询都要重新请求，浪费 API 调用次数

于是我决定采用**多数据源 + 本地缓存**的方案，优先级如下：

1. **腾讯财经** - 稳定、快速、无需认证
2. **新浪财经** - 老牌数据源，可靠性高
3. **Tushare** - 数据准确，但有调用次数限制
4. **Akshare** - 免费丰富，作为最后备选

## 项目结构

整个 Skill 放在 `~/openclaw/skills/stock-analysis/` 目录下：

```
stock-analysis/
├── SKILL.md           # 技能说明文档
├── GUIDE.md           # LLM 使用指南
├── README.md          # 简要说明
├── stock_tool.py      # 核心工具代码
├── requirements.txt   # 依赖列表
└── cache/             # 本地缓存目录
    ├── stock_600028.json
    └── stock_600028.timestamp
```

## 核心代码实现

### 1. 腾讯数据源

腾讯的接口非常稳定，格式也很简单：

```python
class TencentSource:
    def get_realtime(self, stock_code: str) -> dict:
        symbol = f"sh{stock_code}" if stock_code.startswith('6') else f"sz{stock_code}"
        url = f"https://qt.gtimg.cn/q={symbol}"
        
        # 返回格式: v_sh600028="1~中国石化~600028~6.88~..."
        # 字段索引: 1-名称, 2-代码, 3-现价, 31-涨跌额, 32-涨跌幅
```

实测下来，腾讯的响应速度基本在 200ms 以内，而且很少出现连接问题。

### 2. 本地缓存机制

为了减少 API 调用次数（特别是 Tushare 有次数限制），我实现了一个简单的本地缓存：

```python
class CacheManager:
    CACHE_TTL = 300  # 5 分钟有效期
    
    def get(self, symbol: str) -> Optional[dict]:
        # 检查缓存是否存在且未过期
        if cache_exists and not_expired:
            return cached_data
        return None
    
    def set(self, symbol: str, data: dict):
        # 保存数据和时间戳
        save_json(data)
        save_timestamp()
```

缓存文件用 JSON 格式存储，方便查看和调试。时间戳单独存一个文件，避免解析 JSON 的开销。

### 3. 自动降级机制

当主数据源失败时，自动切换到备用源：

```python
class StockQueryManager:
    def __init__(self):
        self.sources = [
            TencentSource(),    # 优先
            SinaSource(),       # 备用1
            TushareSource(),    # 备用2
            AkshareSource()     # 最后
        ]
    
    def query(self, stock_code: str):
        for source in self.sources:
            result = source.get_realtime(stock_code)
            if result.success:
                return result
        return error("所有数据源均不可用")
```

这样即使某个数据源挂了，也能保证服务可用。

## Tushare 集成

Tushare 的数据质量很高，但免费版有调用次数限制。我的解决方案是：

1. **优先使用腾讯/新浪** - 不消耗 Tushare 额度
2. **Tushare 作为备用** - 只有前面都失败时才用
3. **缓存 Tushare 结果** - 5 分钟内重复查询直接读缓存

Token 保存在代码里（反正也是个人使用）：

```python
TUSHARE_TOKEN = "cab8e22a8a441ce9d816359fa54b06dee2ccc1809bc4402197f71f4a"
```

## 让 OpenClaw 自动识别

为了让祥子能自动识别股票查询意图，我写了一份详细的 LLM 使用指南 (`GUIDE.md`)：

```markdown
## 识别股票查询意图

当用户提到以下关键词时，触发股票查询：

| 关键词 | 操作 |
|--------|------|
| "查一下", "看看", "查询" | 个股信息 |
| "行情", "股价", "今天怎么样" | 实时行情 |
| "大盘", "指数" | 大盘指数 |
| "涨幅榜", "排行" | 涨幅榜 |
```

还提供了完整的 Python 调用示例，方便集成到对话流程中。

## 实际使用效果

现在查询股票是这样的：

```
> 帮我查一下中国石化

📊 **股票信息** (来源: tencent)

• **名称**: 中国石化
• **代码**: 600028
• **现价**: 6.88
• **涨跌额**: -0.15
• **涨跌幅**: -2.13%
• **成交量**: 57,518手
• **成交额**: 39.28万
• **市盈率**: 23.08
• **总市值**: 6518.97亿
```

响应速度基本在 1 秒以内，而且数据来源清晰，方便排查问题。

## 踩过的坑

### 1. 腾讯数据格式坑

腾讯返回的数据是 GBK 编码，而且字段位置不直观。我花了好一会儿才搞清楚：

```
字段 1: 名称（乱码）
字段 2: 代码
字段 3: 现价
字段 31: 涨跌额
字段 32: 涨跌幅
```

建议先用 curl 测试，看清楚字段位置再写解析代码。

### 2. 缓存路径问题

一开始把缓存放在项目目录下，结果每次更新代码都要手动清理。后来改成固定的 `cache/` 目录，并加入 `.gitignore`，方便管理。

### 3. 虚拟环境隔离

最开始把依赖装在全局环境里，结果和其他项目冲突。后来改成每个项目独立的 venv，虽然多占点空间，但干净多了。

## 后续优化方向

1. **添加历史数据查询** - 目前已经能用，但还可以优化展示方式
2. **支持港股/美股** - 腾讯接口其实支持港股，只是字段位置不一样
3. **添加图表展示** - 用 matplotlib 生成 K 线图
4. **定时推送** - 设置价格预警，自动推送消息

## 总结

搭建这个 Skill 花了一下午时间，但用起来确实方便多了。多数据源 + 缓存的方案虽然增加了代码复杂度，但稳定性和响应速度都有明显提升。

最重要的是，现在祥子能准确理解我的股票查询意图，再也不用我手动敲命令了。这就是 AI 助手的意义吧——把重复的工作自动化，让我专注于更重要的事情。

如果你也有类似的需求，可以参考我的代码：[GitHub 仓库链接]

---

**相关文章：**
- [OpenClaw 折腾指北（第 0 篇）：部署指南](/)
- [OpenClaw 折腾指北（第 5 篇）：本地 vLLM 部署大模型实现 Token 自由](/)
