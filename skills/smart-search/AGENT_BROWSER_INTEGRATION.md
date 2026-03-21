# Agent Browser 集成到 SmartSearch

## 🎉 集成完成！

### 已安装的技能

1. **agent-browser** (Vercel 官方)
   - 位置：`skills/agent-browser/`
   - 版本：0.21.4
   - 特点：
     - 原生 Rust 二进制，性能优秀
     - Chrome/Chromium CDP 直接连接
     - 支持 JavaScript 渲染页面
     - 交互操作（点击、填充、滚动等）
     - 访问树快照（accessibility tree）
     - 语义定位器（semantic locators）

2. **smart-search with BrowserFetcher**
   - 位置：`skills/smart-search/`
   - 集成：BrowserFetcher 现在使用 agent-browser
   - 特性：
     - 自动降级：agent-browser 不可用时使用 web_fetch
     - 会话管理：支持命名会话
     - 异步处理：支持并发抓取

## 📦 安装状态

✅ **agent-browser 已安装**
- 原生二进制：`~/.openclaw/workspace/skills/agent-browser/bin/agent-browser`
- Chrome 已下载并可用
- 系统路径：`agent-browser` 命令可用

✅ **智能搜索集成**
- `smart_search.py` 已更新
- `agent_browser.py` 已创建（封装模块）
- BrowserFetcher 已集成 agent-browser

## 🔧 使用方法

### 1. 直接使用 agent-browser CLI

```bash
# 打开页面并获取快照
agent-browser open https://example.com && agent-browser snapshot -i

# 交互式操作
agent-browser fill @e1 "用户名" && agent-browser fill @e2 "密码" && agent-browser click @e3

# 获取页面内容
agent-browser get text body
```

### 2. 使用 Python 封装模块

```python
from smart_search.agent_browser import get_agent_browser_instance

browser = get_agent_browser_instance(profile="openclaw")

# 打开页面
await browser.open("https://example.com", wait="networkidle")

# 获取快照
result = await browser.snapshot(interactive=True)
print(result.output)

# 获取标题
title_result = await browser.get_title()
print(title_result.output)

# 关闭浏览器
await browser.close()
```

### 3. 在 SmartSearch 中使用浏览器模式

```python
from smart_search import SmartSearch

# 启用浏览器模式
searcher = SmartSearch(use_browser=True, browser_profile="openclaw")

# 执行搜索（会尝试使用 agent-browser 抓取动态页面）
response = await searcher.search("Python 教程", depth=3, use_browser=True)

# 查看结果
for result in response.results:
    print(f"{result.title} ({result.source} - {result.fetch_method})")
    print(result.content[:500])
    print("-" * 50)
```

### 4. 命令行使用

```bash
# 传统搜索
python smart_search.py "Python 教程"

# 浏览器模式搜索（支持 JS 渲染页面）
python smart_search.py "动态网页内容" --browser

# 查看帮助
python smart_search.py --help
```

## 📋 配置选项

### BrowserFetcher 配置

```python
BrowserFetcher(
    browser_profile="openclaw"  # 或 "chrome"
)
```

### SmartSearch 配置

```python
SmartSearch(
    use_browser=True,           # 启用浏览器模式
    browser_profile="openclaw"  # 浏览器配置
)
```

### agent-browser 配置

环境变量：
- `AGENT_BROWSER_ENCRYPTION_KEY` - 加密密钥
- `AGENT_BROWSER_IDLE_TIMEOUT_MS` - 空闲超时
- `AGENT_BROWSER_MAX_OUTPUT` - 最大输出长度
- `AGENT_BROWSER_ALLOWED_DOMAINS` - 允许域名列表

## ⚡ 性能特点

- **原生 Rust 二进制** - 比 Python Playwright 快 10 倍
- **CDP 直接连接** - 无需 Node.js 依赖
- **异步支持** - 支持并发抓取
- **智能降级** - 自动回退到 web_fetch
- **会话复用** - 浏览器进程持久化

## 🛡️ 安全特性

- **域名白名单** - 限制导航到可信域名
- **输出限制** - 防止上下文溢出
- **操作策略** - 可配置允许的操作列表
- **状态文件加密** - 支持加密存储认证状态

## 📚 参考文档

- [agent-browser SKILL.md](skills/agent-browser/skills/agent-browser/SKILL.md) - 完整命令参考
- [agent-browser README](https://github.com/vercel-labs/agent-browser) - 官方文档
- [smart_search.py](skills/smart-search/smart_search.py) - 源代码

## 🔄 后续优化

- [ ] 添加更多代理支持（proxy）
- [ ] 优化会话管理
- [ ] 添加截图功能
- [ ] 支持 PDF 导出
- [ ] 添加批量处理功能

---

**创建时间**: 2026-03-21  
**状态**: ✅ 已完成集成
