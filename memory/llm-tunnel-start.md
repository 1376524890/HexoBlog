# LLM SSH Tunnel 启动记录

**时间**: 2026-03-26 21:42
**操作**: 启动 SSH 隧道

## 连接信息

- **远程服务器**: `codeserver@39.102.210.43:6122`
- **本地端口**: `8000`
- **隧道进程 PID**: `1656094`
- **状态**: ✅ 已启动

## 日志

```
[2026-03-26 21:42:10] 🚀 Starting SSH tunnel to codeserver@39.102.210.43:6122 -> localhost:8000
[2026-03-26 21:42:10] ✅ Tunnel started with PID 1656094
[2026-03-26 21:42:12] ✅ Tunnel is active on port 8000
[2026-03-26 21:42:12] 🎉 Tunnel successfully established!
```

## 后续维护

隧道已自动配置心跳保活：
- 心跳间隔：30 秒
- 最大重试：3 次
- 自动重连：已启用

可通过以下方式管理：

```bash
# 查看状态
/home/claw/.openclaw/scripts/tunnel-manager.sh status

# 重启隧道
/home/claw/.openclaw/scripts/tunnel-manager.sh restart

# 停止隧道
/home/claw/.openclaw/scripts/tunnel-manager.sh stop
```

---
*由御坂美琴一号自动记录*
