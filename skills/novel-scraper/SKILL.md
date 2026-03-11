---
name: novel-scraper
description: 下载铅笔小说为 TXT 格式，支持指定 URL 下载
---

# Novel Scraper - 小说下载技能

_一键下载铅笔小说为 TXT 格式_

---

## 🎯 功能说明

**Novel Scraper 是通过 URL 下载铅笔小说为 TXT 文件的专业工具**

主要功能：
- 📖 **下载小说** - 根据小说 URL 下载完整内容
- 💾 **导出 TXT** - 自动保存为 UTF-8 编码的 TXT 文件
- 📋 **章节整理** - 自动合并所有章节，包含标题和作者信息
- ⚡ **智能抓取** - 自动跳过广告和无关内容

---

## 📚 使用方式

### ⚠️ 重要提示

**铅笔小说没有公开搜索 API，需要用户提供小说详情页 URL！**

获取 URL 的方法：
1. 访问 http://www.5963.net
2. 通过网站目录浏览找到目标小说
3. 复制小说详情页的完整 URL

---

## 🔧 环境配置

### 依赖库

确保已安装以下 Python 库：

```bash
pip install requests beautifulsoup4 tldextract
```

### 系统要求

- Python 3.7+
- 网络连接（可访问 http://www.5963.net）
- 足够的磁盘空间（小说 TXT 文件通常几 MB 到几十 MB）

---

## 💡 使用示例

### 方式一：通过技能调用

```
下载小说：http://www.5963.net/book/19720/
保存到：/home/user/novels
```

### 方式二：命令行直接调用

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

---

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

... (后续章节)
```

---

## 🌐 支持网站

**当前支持：**
- 📖 铅笔小说 (http://www.5963.net)

**未来计划：**
- 📚 其他小说网站（根据需要添加）

---

## ⚙️ 参数说明

| 参数 | 缩写 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--url` | `-u` | ✅ | - | 小说详情页 URL |
| `--output` | `-o` | ❌ | `~/downloads` | 输出目录 |
| `--delay` | `-d` | ❌ | `2.0` | 请求间隔时间（秒） |

---

## 🛡️ 使用规范

### 1. URL 要求
- ✅ 必须是铅笔小说网的小说详情页 URL
- ✅ URL 格式：`http://www.5963.net/book/{id}/`
- ❌ 不支持章节页、目录页等其他页面

### 2. 下载建议
- 🌙 **避开高峰** - 在用户非活跃时段下载（如凌晨）
- ⏱️ **合理间隔** - 建议 delay >= 2 秒，避免触发反爬虫
- 💾 **检查空间** - 大型小说可能占用较大磁盘空间
- 🔒 **尊重版权** - 仅供个人学习使用

### 3. 错误处理
如果遇到下载失败：
1. 检查 URL 是否正确
2. 检查网络连接
3. 尝试增加请求间隔时间
4. 查看错误日志

---

## 🔄 自动化建议

### 批量下载（手动脚本）

可以创建批量下载脚本：

```bash
#!/bin/bash
# download-all.sh

NOVEL_URLS=(
    "http://www.5963.net/book/19720/"
    "http://www.5963.net/book/12345/"
    "http://www.5963.net/book/67890/"
)

for url in "${NOVEL_URLS[@]}"; do
    echo "正在下载：$url"
    python3 ~/.openclaw/workspace/scripts/novel_crawler.py \
        -u "$url" \
        -o "/home/user/novels/$(date +%Y%m%d)" \
        -d 3
    sleep 2
done

echo "全部下载完成！"
```

---

## 🧪 测试验证

### 检查依赖

```bash
python3 -c "import requests, bs4, tldextract; print('✅ 依赖检查通过')"
```

### 测试下载

```bash
python3 ~/.openclaw/workspace/scripts/novel_crawler.py \
    -u "http://www.5963.net/book/19720/" \
    --dry-run
```

---

## 📦 文件位置

- **主脚本**: `~/.openclaw/workspace/scripts/novel_crawler.py`
- **技能目录**: `~/.openclaw/workspace/skills/novel-scraper/`
- **输出目录**: `~/downloads/` (默认)
- **日志**: 输出到终端（可根据需要添加日志文件）

---

## ⚠️ 注意事项

1. **网站稳定性** - 铅笔小说网可能随时变更结构，脚本可能需要更新
2. **反爬虫机制** - 频繁请求可能触发反爬，建议设置合理间隔
3. **内容完整性** - 部分小说可能存在章节缺失情况
4. **版权提醒** - 下载内容仅供个人学习，请勿用于商业用途

---

## 🔧 故障排除

### 问题 1: 下载速度过慢
**原因**: 默认请求间隔 2 秒，避免太快触发反爬
**解决**: 减少 delay 值（但可能触发反爬）
```bash
python3 novel_crawler.py -u "URL" -d 1
```

### 问题 2: 下载失败（章节列表为空）
**原因**: 网站结构变更或小说 ID 错误
**解决**: 检查 URL 是否正确，查看错误日志

### 问题 3: TXT 文件内容为空
**原因**: 章节内容抓取失败
**解决**: 
1. 检查网络连接
2. 尝试增加 delay
3. 验证 URL 是否为有效的小说详情页

### 问题 4: 依赖库未安装
**解决**:
```bash
pip install requests beautifulsoup4 tldextract
```

---

## 📝 更新日志

### v1.0.0 (2026-03-11)
- ✨ 初始版本发布
- 📖 支持铅笔小说下载
- 💾 导出 TXT 格式
- 🛡️ 增加反爬保护机制

---

## 👥 维护者

- **创建者**: 御坂美琴一号
- **所属**: 御坂网络第一代
- **联系方式**: 通过 OpenClaw 联系

---

**技能版本**: 1.0.0  
**创建时间**: 2026-03-11T14:10:00+08:00  
**最后更新**: 2026-03-11T14:10:00+08:00  
**状态**: ✅ 生产就绪

---

*御坂妹妹 10 号 - 通用代理随时为您服务！⚡*
