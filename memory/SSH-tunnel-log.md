## SSH 隧道管理 - 2026-03-13 18:25

### 启动成功

**时间**: 2026-03-13 18:25:39
**状态**: ✅ 隧道已激活

**连接信息**:
- 远程主机：`codeserver@39.102.210.43:6122`
- 本地端口：`localhost:8000`
- 进程 PID: `734667`

**操作日志**:
```
[2026-03-13 18:25:39] 🚀 Starting SSH tunnel to codeserver@39.102.210.43:6122 -> localhost:8000
[2026-03-13 18:25:39] ✅ Tunnel started with PID 734667
[2026-03-13 18:25:41] ✅ Tunnel is active on port 8000
[2026-03-13 18:25:41] 🎉 Tunnel successfully established!
```

### 隧道状态检查

可通过以下命令检查隧道状态：
```bash
ps aux | grep "ssh -L"
netstat -tlnp | grep 8000
```

### 管理命令

- **启动**: `/home/claw/.openclaw/scripts/tunnel-manager.sh start`
- **停止**: `/home/claw/.openclaw/scripts/tunnel-manager.sh stop`
- **重启**: `/home/claw/.openclaw/scripts/tunnel-manager.sh restart`

---
*记录于 2026-03-13*
