# LLM 隧道自动启动

## SSH 隧道状态

**启动时间**: 2026-03-25 14:26:27
**隧道连接**: codeserver@39.102.210.43:6122 -> localhost:8000
**PID**: 1634117
**状态**: ✅ 活跃运行中

## 配置信息

- **远程服务器**: codeserver@39.102.210.43
- **远程端口**: 6122
- **本地端口**: 8000
- **模型**: Qwen/Qwen3.5-35B-A3B-FP8

## 管理命令

```bash
# 启动隧道
bash /home/claw/.openclaw/scripts/tunnel-manager.sh start

# 停止隧道
bash /home/claw/.openclaw/scripts/tunnel-manager.sh stop

# 查看状态
bash /home/claw/.openclaw/scripts/tunnel-manager.sh status
```

## Cron 任务

- **任务 ID**: `llm-tunnel-auto-start`
- **频率**: 自动启动/每 6 小时检查
- **状态**: ✅ 已启用

---

*自动生成 - LLM 隧道管理系统*
