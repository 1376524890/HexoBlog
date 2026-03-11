# Novel Scraper - 小说下载工具

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)

<p align="center">
  <strong>铅笔小说下载工具 - 一键下载小说为 TXT 格式</strong>
</p>

---

## 📖 项目简介

Novel Scraper 是一个专门用于下载铅笔小说（www.5963.net）内容的工具，可将整本小说保存为 TXT 格式，方便离线阅读。

### ✨ 特性

- ✅ **简单高效** - 只需提供小说 URL，一键下载整本
- ✅ **格式规范** - 自动整理章节，输出标准 TXT 格式
- ✅ **反爬保护** - 智能请求间隔，避免触发反爬虫机制
- ✅ **容错能力强** - 完善的错误处理和日志输出
- ✅ **易于扩展** - 支持添加其他小说网站

---

## 🚀 快速开始

### 安装依赖

```bash
pip install requests beautifulsoup4 tldextract
```

### 基本使用

```bash
# 下载小说
python3 novel_crawler.py -u "http://www.5963.net/book/19720/"

# 指定输出目录
python3 novel_crawler.py -u "http://www.5963.net/book/19720/" -o "/home/user/novels"

# 设置请求间隔
python3 novel_crawler.py -u "http://www.5963.net/book/19720/" -d 3
```

---

## 📚 详细文档

请查看 [SKILL.md](./SKILL.md) 获取完整的使用说明和配置指南。

---

## ⚠️ 重要提示

### 🔍 URL 获取方式

由于铅笔小说没有公开搜索 API，需要手动获取小说 URL：

1. 访问 [铅笔小说网](http://www.5963.net)
2. 通过网站目录浏览找到目标小说
3. 复制小说详情页的完整 URL

**URL 格式**: `http://www.5963.net/book/{小说 ID}/`

### 🛡️ 使用规范

- 仅供个人学习使用
- 尊重版权，勿用于商业用途
- 合理设置请求间隔，避免触发反爬
- 下载内容仅供个人收藏

---

## 📦 输出示例

下载的 TXT 文件包含：

```
书名：《示例小说》
作者：作者名
来源：http://www.5963.net
抓取时间：2026-03-11 14:30:00
==================================================

第 1 章 第一章
==============================
这里是章节内容...

第 2 章 第二章
==============================
这里是章节内容...
```

---

## 🛠️ 技术栈

- **Python 3.7+** - 主要开发语言
- **requests** - HTTP 请求库
- **BeautifulSoup4** - HTML 解析库
- **tldextract** - URL 域名解析

---

## 📝 目录结构

```
novel-scraper/
├── SKILL.md              # 技能说明文档
├── README.md             # 项目说明文档
├── novel_crawler.py      # 主程序脚本
└── requirements.txt      # Python 依赖列表

/scripts/
└── novel_crawler.py      # 系统级脚本链接
```

---

## 🔧 参数说明

| 参数 | 缩写 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--url` | `-u` | ✅ | - | 小说详情页 URL |
| `--output` | `-o` | ❌ | `~/downloads` | 输出目录 |
| `--delay` | `-d` | ❌ | `2.0` | 请求间隔时间（秒） |

---

## 🌟 示例

### 下载《示例小说》

```bash
# 使用默认设置（2 秒间隔，下载到 ~/downloads）
python3 novel_crawler.py -u "http://www.5963.net/book/19720/"

# 快速下载（1 秒间隔，注意可能触发反爬）
python3 novel_crawler.py -u "http://www.5963.net/book/19720/" -d 1

# 安全下载（3 秒间隔，稳定可靠）
python3 novel_crawler.py -u "http://www.5963.net/book/19720/" -d 3 -o ~/my_novels
```

---

## ⚙️ 高级用法

### 批量下载

```bash
#!/bin/bash
# download-batch.sh

NOVELS=(
    "http://www.5963.net/book/19720/"
    "http://www.5963.net/book/12345/"
    "http://www.5963.net/book/67890/"
)

for url in "${NOVELS[@]}"; do
    echo "正在下载：$url"
    python3 novel_crawler.py -u "$url" -o "./downloads" -d 3
    sleep 2
done
```

---

## 🐛 故障排除

### 1. 下载速度慢

**原因**: 默认 2 秒请求间隔
**解决**: 适当减少 delay 值
```bash
python3 novel_crawler.py -u "URL" -d 1
```

### 2. 下载失败

**检查项**:
- URL 是否正确
- 网络连接是否正常
- 是否需要更新依赖

### 3. 依赖缺失

**解决**:
```bash
pip install -r requirements.txt
```

---

## 📄 许可证

MIT License

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

## 🙏 致谢

- [铅笔小说网](http://www.5963.net) - 小说资源提供方
- [requests](https://docs.python-requests.org/) - 优秀的 HTTP 库
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - 强大的 HTML 解析库

---

<div align="center">

**由御坂网络第一代提供支持 ⚡**

*御坂妹妹 10 号 - 通用代理为您服务*

</div>
