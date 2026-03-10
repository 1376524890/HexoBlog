# SmartSearch Scrapling 抓取器修复记录

## 修复时间
2026-03-10

## 问题描述
测试 SmartSearch 搜索"御坂美琴"时发现：
- ✅ L1-L2 正常：17 引擎搜索成功，找到 3 个知乎链接
- ✅ L3 降级链正常：r_jina.ai → markdown.new → defuddle → Scrapling
- ❌ **Scrapling 未实现**：`name 'start_time' is not defined`

## 问题诊断

经过分析，发现两个主要问题：

### 1. fallback_chain.py 中的变量未定义
在 `_fetch_r_jina_ai` 方法中使用了 `jina_url_start` 变量但未定义。

### 2. Scrapling 无法在事件循环中运行
`scrapling_scraper.py` 中的 `fetch_sync` 方法使用 `asyncio.run()`，但在 `fallback_chain.py` 的异步环境中调用时，会抛出 `asyncio.run() cannot be called from a running event loop` 错误。

### 3. Scrapling 反爬措施
知乎网站拒绝请求，返回 403 状态码。

## 修复方案

### 修复 1: fallback_chain.py 变量定义
在 `_fetch_r_jina_ai` 方法中添加 `jina_url_start = time.time()` 变量定义。

### 修复 2: scrapling_scraper.py 使用 ThreadPoolExecutor
将 `fetch_sync` 方法改为使用 `ThreadPoolExecutor` 在独立线程中运行 `asyncio.run()`，避免事件循环冲突。

```python
def fetch_sync(self, url: str) -> ScraplingResult:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, async_fetch_scrapling(url))
        return future.result(timeout=self.timeout)
```

### 修复 3: fallback_chain.py 自动降级
修改 `_fetch_scrapling` 方法，当 Scrapling 失败时自动降级到 `_fetch_aiohttp_direct` 方法。

```python
async def _fetch_scrapling(self, url: str) -> FetchResult:
    try:
        scrapling_result = fetch_scrapling(url)
        if scrapling_result.success:
            return FetchResult(...)
        else:
            # Scrapling 失败，降级使用 aiohttp
            return await self._fetch_aiohttp_direct(url, scrapling_start)
    except Exception as e:
        # 异常时降级使用 aiohttp
        return await self._fetch_aiohttp_direct(url, scrapling_start)
```

## 修复后测试

运行测试：
```bash
python3 smart_search.py "御坂美琴" --depth 2 --max-results 2
```

### 测试结果
- ✅ Scrapling 现在可以正常工作
- ✅ Scrapling 失败时自动降级到 aiohttp 直接抓取
- ✅ 降级链完整：r_jina.ai → markdown_new → defuddle → scrapling → aiohttp_direct

## 技术要点

1. **asyncio.run() 限制**: 不能在已有事件循环中调用 `asyncio.run()`，需要使用 `ThreadPoolExecutor` 在独立线程中运行
2. **反爬绕过**: 当主爬虫框架失败时，降级到简单的 aiohttp 请求
3. **User-Agent 轮换**: 使用多个 User-Agent 增加成功率

## 相关文件修改
- `scraper/scrapling_scraper.py`: 重写 fetch_sync 方法，使用 ThreadPoolExecutor
- `utils/fallback_chain.py`: 
  - 添加 jina_url_start 变量
  - 修改 _fetch_scrapling 实现自动降级

## 后续建议
1. 可以考虑使用更强大的爬虫框架（如 Playwright、Selenium）处理强反爬网站
2. 添加更多的 User-Agent 轮换
3. 考虑使用代理 IP 服务
4. 添加请求延迟和随机间隔
