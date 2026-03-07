---
title: OpenClaw 折腾指北（第 2 篇）：给 AI 配个课程表，每天早上自动发送晨报文
date: 2026-03-07 04:54:00
tags: [OpenClaw, Skill, 课程表，晨报文，自动化]
categories: [折腾指北]
---

# 起因：为什么需要晨报文？

每天早上的时间都很宝贵。如果 AI 能提前告诉我：
- 今天天气如何，要不要带伞？
- 穿什么衣服最合适？
- 今天有几节课，分别在什么时候？

那该多省心啊！于是我决定给 OpenClaw 写一个**晨报文 Skill**。

# 技术方案：Morning Briefing Skill

## 核心功能

1. **课程表解析** - 从 `.ics` 文件自动提取今日课程
2. **天气查询** - 集成 `wttr.in` 获取北京实时天气
3. **智能建议** - 根据温度推荐穿衣搭配
4. **自动发送** - 每天早上 7:30 自动推送

## 实现原理

### 1. ICS 课程表文件

用任何支持 ICS 的日历应用（Google Calendar、Outlook、Apple Calendar）导出课程表：

```bash
# 我使用的是 Outlook 导出的课程表
# 每周重复的课程会自动识别为周期性事件
```

`calendar.ics` 文件示例：
```
BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:计算机网络
DTSTART:20260307T090000
DTEND:20260307T103000
RRULE:FREQ=WEEKLY;BYDAY=FR
LOCATION:教学楼 A301
END:VEVENT
END:VCALENDAR
```

### 2. 天气 API

使用免费的 `wttr.in` 服务：
```python
url = f"https://wttr.in/{location}?format=j1"
response = requests.get(url, timeout=10)
weather_data = response.json()
```

## 配置示例

```json
{
  "location": "Beijing",
  "timezone": "Asia/Shanghai",
  "schedule_file": "calendar.ics",
  "clothing_thresholds": {
    "very_cold": 5,
    "cold": 10,
    "cool": 15
  },
  "precip_threshold": 0.1
}
```

## Cron 定时任务

在 OpenClaw 的 cron 配置中添加到每天早上 7:30：

```json
{
  "id": "morning-briefing",
  "name": "morning-briefing",
  "description": "每天早上 7:30 推送当日课程和北京天气",
  "schedule": {
    "kind": "cron",
    "expr": "30 7 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "早安！请帮我准备今天的简报：1. 检查今天的日程安排 2. 查询北京的天气 3. 发送一份简洁的今日概览给用户"
  }
}
```

# 实际效果

每天早上 7:30，我会收到这样的消息：

```
🌅 早安简报 - 3 月 7 日 周五

🌤️ 北京天气
• 当前：多云 -3°C（体感 -6°C）
• 今日：-8°C ~ 2°C
• 湿度：45%，风力：12 km/h

👕 穿衣建议：厚羽绒服/大衣、注意体感温度较低
☔ 今天无雨，不用带伞

📅 今日课程
• 09:00 - 10:30 | 计算机网络
  📍 教学楼 A301
• 14:00 - 15:30 | 操作系统
  📍 教学楼 B205
```

# 技术细节

## Python 实现

核心代码在 `generate.py`，主要函数：

```python
def generate_briefing(date_str=None):
    """生成完整晨报文"""
    config = load_config()
    
    # 获取天气
    weather_data = get_weather(config['location'])
    weather = parse_weather(weather_data)
    
    # 获取课程表
    events = parse_schedule(date_str)
    
    # 组装输出
    output = []
    output.append(f"🌅 早安简报 - {date_display}\n")
    output.append("🌤️ 北京天气")
    output.append(f"• 当前：{weather['desc']} {weather['temp']}°C")
    output.append("")
    output.append("📅 今日课程")
    for event in events:
        output.append(f"• {event['start']} - {event['end']} | {event['summary']}")
    
    return '\n'.join(output)
```

## 依赖库

```bash
pip install icalendar requests
```

## 扩展功能

### 穿衣建议逻辑

```python
def get_clothing_advice(temp, config):
    if temp < 5:
        return '厚羽绒服/大衣'
    elif temp < 10:
        return '羽绒服/厚外套'
    elif temp < 15:
        return '外套/毛衣'
    else:
        return '薄外套/长袖'
```

### 雨天提醒

```python
def get_umbrella_advice(precip, config):
    if precip > 0.1:
        return '今天有雨，记得带伞 ☔'
    return '今天无雨，不用带伞'
```

# 效果对比

| 功能 | 手动查询 | AI 自动推送 |
|------|---------|------------|
| 天气查询 | ⏰ 需要自己打开天气 App | ✅ 自动推送 |
| 课程查看 | ⏰ 需要打开日历 App | ✅ 直接显示今日课程 |
| 穿衣建议 | ⏰ 自己判断 | ✅ 根据温度智能推荐 |
| 伞具提醒 | ⏰ 自己注意天气预报 | ✅ 有雨自动提醒 |

**节省时间：** 每天早上一键获取所有信息，不用在多个 App 之间切换。

# 个人心得

## 为什么用 ICS 格式？

1. **通用性强** - 几乎所有日历应用都支持
2. **本地化** - 不需要依赖云端 API，隐私性好
3. **可维护** - 文本文件，可以手动编辑
4. **重复事件** - 原生支持每周/每月重复

## 可扩展方向

1. **多城市支持** - 如果出差到其他城市，自动切换天气
2. **紧急提醒** - 下一节课快开始时推送提醒
3. **多语言** - 支持中英文切换
4. **语音播报** - 集成 TTS，起床时自动播报

# 总结

通过一个简单的 Python 脚本 + ICS 课程表文件，我就实现了：
- ✅ 每天早上自动接收晨报文
- ✅ 课程 + 天气 + 穿衣建议一站式获取
- ✅ 完全本地化，不依赖第三方 API（天气除外）
- ✅ 开源代码，可自由扩展

**核心经验：** 自动化不是要替代所有手动操作，而是把那些**每天早上重复**的事情变成习惯，让 AI 帮我记住。

---

*下一篇：如何配置本地 vLLM 部署大模型？*
