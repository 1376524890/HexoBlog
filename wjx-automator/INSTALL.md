# 安装指南 (INSTALL.md)

## 📦 系统安装

### 方法一：快速安装脚本（推荐）

```bash
cd wjx-automator
chmod +x quickstart.sh
./quickstart.sh setup
```

### 方法二：手动安装

#### 1. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 安装 ChromeDriver

**自动安装（推荐）**：

系统会自动下载与 Chrome 版本匹配的 ChromeDriver。

**手动安装**：

1. 访问 https://chromedriver.chromium.org/downloads
2. 下载与你的 Chrome 版本匹配的 ChromeDriver
3. 解压到任意目录
4. 在 `config.json` 中配置：

```json
{
  "browser": {
    "driver_path": "/path/to/chromedriver"
  }
}
```

## 🔧 配置步骤

### 1. 准备问卷数据

创建 CSV 文件，格式如下：

```csv
question_id,type,total_responses,options_distribution
1,single,210,"选项 A:35%,选项 B:25%,选项 C:20%,选项 D:20%"
2,multiple,210,"选项 A:40%,选项 B:35%,选项 C:25%"
...
```

保存为 `data/q28_response.csv`

### 2. 配置问卷 URL

编辑 `config.json`：

```json
{
  "questionnaire": {
    "url": "https://v.wjx.cn/vm/PhfZxRV.aspx"
  }
}
```

### 3. 测试运行

```bash
# 干燥测试（不提交）
python main.py --dry-run --data data/q28_response.csv

# 实际运行
python main.py --data data/q28_response.csv --workers 5
```

## ⚙️ 常见问题

### Q: ChromeDriver 版本不匹配？

**解决方案**：
```bash
pip install webdriver-manager
```

在 `config.json` 中不指定 `driver_path`，系统会自动下载。

### Q: 浏览器启动失败？

**原因**：可能缺少依赖库

**Linux 解决方案**：
```bash
sudo apt-get update
sudo apt-get install -y \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0
```

### Q: 元素定位失败？

**原因**：问卷结构可能变化

**解决方案**：
1. 检查 `xpath_config.json`
2. 手动调整 XPath 选择器
3. 使用浏览器开发者工具获取最新的 XPath

### Q: 填写速度太慢？

**解决方案**：
1. 增加并发线程数：`--workers 10`
2. 减少延迟：编辑 `config.json` 中的 `delay_between_submissions`
3. 使用更快的网络环境

### Q: 被问卷星封禁？

**预防措施**：
1. 增加填写间隔：`"delay_between_submissions": 10`
2. 减少并发线程：`"workers": 2`
3. 使用代理：在 `config.json` 中配置 `proxy`
4. 模拟真实用户：调整 `user_agent`

## 🚀 部署到服务器

### 1. 安装 Python 和 Chrome

```bash
# Ubuntu/Debian
apt-get update
apt-get install -y python3 python3-pip chromium

# 安装依赖
pip3 install selenium webdriver-manager
```

### 2. 上传代码

```bash
# 使用 SCP 或 Git
git clone <your-repo-url>
cd wjx-automator
```

### 3. 配置并运行

```bash
python3 main.py --data data/q28_response.csv --workers 5
```

### 4. 后台运行（可选）

```bash
nohup python3 main.py --data data/q28_response.csv > output.log 2>&1 &
```

## 📊 性能优化

### 并发调整

根据服务器性能和问卷难度调整并发数：

```
低配置（1-2 核）：workers = 2-3
中配置（4 核）：workers = 5-8
高配置（8 核+）：workers = 10-20
```

### 内存优化

如果内存不足：
1. 减少并发数
2. 设置 Chrome 参数：`--disable-gpu`
3. 使用 `--headless` 模式

### 网络优化

如果网络不稳定：
1. 增加重试次数：`"max_retries": 5`
2. 增加超时时间：`"wait_timeout": 60`
3. 使用本地代理缓存

## 🛡️ 安全建议

1. **数据隐私**：
   - 不要将 `config.json` 和 CSV 数据上传到公共仓库
   - 使用 `.gitignore` 排除敏感文件

2. **使用合规**：
   - 仅用于合法合规的用途
   - 遵守问卷星的服务条款
   - 控制填写频率，避免被封禁

3. **监控日志**：
   - 定期检查日志文件
   - 注意异常行为和错误信息

## 📞 技术支持

- GitHub Issues: https://github.com/yourusername/wjx-automator/issues
- Email: your.email@example.com

## 📝 更新日志

### v1.0.0 (2026-03-11)
- ✅ 初始版本发布
- ✅ 支持单选题、多选题、量表题、简答题
- ✅ 多线程并发填写
- ✅ 完整的异常处理和重试机制
- ✅ 详细的日志记录系统

---

_祝您使用愉快！⚡_
