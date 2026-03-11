# 📚 小说下载 Skill (novel-scraper)

## 🎯 功能

通过 URL 下载铅笔小说为 TXT 格式，支持指定目录保存

## 🌐 SmartSearch 增强版 (新增浏览器模式！)

**版本**: v1.1.0 (2026-03-11)

**新增**: 浏览器模式支持 JavaScript 渲染的动态页面！

### 使用方法

**方式一：普通搜索**（静态页面）
```bash
python skills/smart-search/smart_search.py "Python 教程"
```

**方式二：浏览器模式**（动态页面，如起点中文网）
```bash
# 搜索 + 浏览器抓取
python skills/smart-search/smart_search.py --browser "玄幻小说排行榜 2025"

# 直接访问动态页面
python skills/smart-search/smart_search.py --browser "https://qidian.com/rank"
```

**参数说明**:
- `--browser`: 使用浏览器模式（自动处理 JavaScript）
- `--browser-profile`: 浏览器配置文件 (openclaw/chrome)

### 使用场景

| 场景 | 模式 | 示例 |
|------|------|------|
| 普通网站 | 传统模式 | Python 文档、博客文章 |
| 动态加载 | 浏览器模式 | 起点、番茄小说排行榜 |
| JavaScript SPA | 浏览器模式 | 单页应用、交互式内容 |
| 反爬网站 | 浏览器模式 | 模拟真实浏览器访问 |

---

## 📍 技能位置

`skills/novel-scraper/`

## ⚠️ 重要提示

**铅笔小说网没有公开搜索 API**，需要用户提供小说详情页 URL！

### 如何获取 URL：
1. 访问 http://www.5963.net
2. 通过网站目录浏览找到目标小说
3. 复制小说详情页的完整 URL

## 💡 使用方式

### 方式一：通过 OpenClaw 调用

```
御坂大人：帮我下载小说：http://www.5963.net/book/19720/
保存到：/home/user/novels
```

### 方式二：命令行直接执行

```bash
# 基本用法（必需提供 URL）
python3 ~/.openclaw/workspace/scripts/novel_crawler.py \
    -u "http://www.5963.net/book/19720/"

# 指定输出目录
python3 ~/.openclaw/workspace/scripts/novel_crawler.py \
    -u "http://www.5963.net/book/19720/" \
    -o "/home/user/novels"

# 设置请求间隔（避免触发反爬虫）
python3 ~/.openclaw/workspace/scripts/novel_crawler.py \
    -u "http://www.5963.net/book/19720/" \
    -d 3

# 帮助信息
python3 ~/.openclaw/workspace/scripts/novel_crawler.py --help
```

## 📋 参数说明

| 参数 | 缩写 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--url` | `-u` | ✅ | - | 小说详情页 URL |
| `--output` | `-o` | ❌ | `~/downloads` | 输出目录 |
| `--delay` | `-d` | ❌ | `2.0` | 请求间隔时间（秒） |

## 📝 输出格式

下载的小说 TXT 文件包含：
```
书名：《示例小说标题》
作者：作者名
来源：http://www.5963.net
抓取时间：2026-03-11 14:30:00
==================================================

第 1 章 第一章标题
==============================
这里是章节内容...

第 2 章 第二章标题
==============================
这里是章节内容...
```

## 🌐 支持网站

- ✅ 铅笔小说 (http://www.5963.net)

## ⚡ 文件位置

- **主脚本**: `scripts/novel_crawler.py`
- **技能目录**: `skills/novel-scraper/`
- **输出目录**: `~/downloads/` (默认)

## 🛡️ 使用规范

1. **URL 要求**
   - ✅ 必须是铅笔小说网的小说详情页 URL
   - ✅ URL 格式：`http://www.5963.net/book/{id}/`
   - ❌ 不支持章节页、目录页等其他页面

2. **下载建议**
   - 🌙 避开高峰 - 在用户非活跃时段下载
   - ⏱️ 合理间隔 - 建议 delay >= 2 秒
   - 💾 检查空间 - 大型小说可能占用较大磁盘空间
   - 🔒 尊重版权 - 仅供个人学习使用

## 🧪 测试验证

已测试下载：《人渣反派自救系统》
- 章节数：95 章
- 文件大小：871KB
- 状态：✅ 成功

## 📅 创建时间

2026-03-11T14:10:00+08:00

---

*技能版本：1.0.0*
