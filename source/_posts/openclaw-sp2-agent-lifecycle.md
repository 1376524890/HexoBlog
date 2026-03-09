---
title: 'SP2: Agent 生命周期——从启动到退出的完整旅程'
date: 2026-03-09 08:00:00
tags:
  - OpenClaw
  - AI Agent
  - 生命周期
  - 架构设计
categories:
  - 技术折腾
---

> OpenClaw 折腾指北系列

## 引言：为什么了解 Agent 生命周期？

在 SP1 中，我们建立了 OpenClaw 的网关视角全景图。四大组件中，**Agent**是最核心的 AI 执行体。但 Gateway 只是"调度员"，真正干活的是 Agent。

理解 Agent 的启动→运行→退出全流程，是掌握 OpenClaw 的关键。

**核心问题：**
1. Agent 是如何被创建的？
2. 系统提示词是如何构建的？
3. 工具调用机制的内部流程是什么？
4. Session 如何与 Agent 配合？

这篇文章，我们将深入 Agent 的内部机制，看看它是如何"活"起来的。

<!-- more -->

---

## 第一章：Agent 的启动——从配置到运行

### 1.1 配置文件的作用

每个 Agent 都有属于自己的配置文件，位于：

```bash
~/.openclaw/config/agents/
```

**文件命名规则**：`<agent-id>.yaml`

比如御坂妹妹 11 号（代码执行者）的配置文件是：

```yaml
id: code-executor
name: "御坂妹妹 11 号 - 代码执行者"
description: "专门负责代码编写、调试、重构的专业 AI 助手"
model: "Qwen/Qwen3.5-35B-A3B-FP8"
permission_level: 3
sandbox: inherit
tools:
  - read
  - write
  - edit
  - exec
  - process
```

**关键配置项解读：**

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `id` | Agent 的唯一标识 | `code-executor` |
| `name` | 显示名称（带御坂妹妹编号） | `御坂妹妹 11 号 - 代码执行者` |
| `description` | 功能描述 | `专门负责代码编写...` |
| `model` | 使用的 AI 模型 | `Qwen/Qwen3.5-35B-A3B-FP8` |
| `permission_level` | 权限等级（1-5） | `3` |
| `sandbox` | 沙箱策略 | `inherit` / `require` |
| `tools` | 可用工具列表 | `[read, write, exec]` |

### 1.2 启动流程

Gateway 启动时，会自动扫描并加载所有 Agent 配置文件。流程如下：

```
┌─────────────────────────────────────────┐
│ Step 1: Gateway 加载配置                  │
│ 扫描 ~/.openclaw/config/agents/*.yaml   │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Step 2: 创建 Agent 实例                    │
│ 隔离环境 + 设置权限等级                  │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Step 3: 注入系统提示词                   │
│ 动态生成五层结构的 System Prompt        │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Step 4: 加入 Agent 池                      │
│ 注册到 Gateway.agent_pool               │
└─────────────────────────────────────────┘
```

**伪代码实现：**

```python
# Gateway 启动时
for config_file in glob.glob("config/agents/*.yaml"):
    agent_config = load_yaml(config_file)
    
    # 创建隔离环境
    agent_instance = Agent(
        id=agent_config.id,
        model=agent_config.model,
        permission_level=agent_config.permission_level
    )
    
    # 设置沙箱边界
    if agent_config.sandbox == "require":
        agent_instance.enable_strict_sandbox()
    
    # 注入系统提示词
    system_prompt = build_system_prompt(agent_instance)
    agent_instance.set_system_prompt(system_prompt)
    
    # 加入 Agent 池
    gateway.agent_pool.add(agent_instance)
```

### 1.3 权限等级详解

OpenClaw 采用**五层权限模型**，不同等级对应不同的能力边界：

| 等级 | 编号 | 权限范围 | 适用场景 | 御坂妹妹编号 |
|------|------|----------|----------|--------------|
| Level 1 | 只读 | 仅读取文件 | 数据分析、日志查看 | 待创建 |
| Level 2 | 受限 | 指定目录读写 | 通用代理、文件管理 | 10 号 |
| Level 3 | 标准 | 工作目录读写 | 代码执行、内容创作 | 11-12 号 |
| Level 4 | 受限系统 | 系统配置（需批准） | 系统管理员 | 15 号 |
| Level 5 | 完全 | 完全访问权限 | 主 Agent | 1 号 |

**权限检查机制：**

```python
def has_permission(agent, required_level):
    return agent.permission_level >= required_level

# 示例：exec 工具需要 Level 3 权限
if not has_permission(agent, required_level=3):
    raise PermissionError("权限不足：需要 Level 3，当前 Level 2")
```

这种分层设计遵循**最小权限原则**——每个 Agent 只拥有完成任务所需的最小权限集。

---

## 第二章：系统提示词——Agent 的"灵魂"

### 2.1 系统提示词的作用

系统提示词（System Prompt）是 Agent 的**出厂设置**，定义了：

- **身份**：你是谁？
- **能力**：你能做什么？
- **规则**：你应该如何行为？
- **环境**：你现在在哪里？

SP1 中提到系统提示词是动态生成的，本章深入其内部机制。

### 2.2 系统提示词的五层结构

```
┌─────────────────────────────────────────┐
│ Layer 1: 基础身份                        │
│ - 名称：御坂妹妹 11 号                   │
│ - 描述：代码执行者                      │
│ - Emoji: ⚡                             │
│ - 身份声明：我不是助手，我是御坂妹妹！  │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Layer 2: 工具描述                       │
│ - 可用工具列表                         │
│ - JSON Schema 格式的参数说明           │
│ - 调用示例                              │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Layer 3: 运行时信息                     │
│ - 当前时间：2026-03-09T08:00:00Z       │
│ - 工作目录：/home/claw/.openclaw/      │
│ - 环境变量：PATH, HOME, 等             │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Layer 4: 安全提示                       │
│ - 沙箱边界：禁止访问 /etc/, ~/.ssh/    │
│ - 权限限制：Level 3 标准权限            │
│ - 禁止行为：删除系统文件、外传隐私    │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Layer 5: 格式说明                       │
│ - 工具调用格式：{tool: "name", args: {}}│
│ - 回复格式：自然语言 + 工具调用        │
│ - 多轮对话规则                         │
└─────────────────────────────────────────┘
```

**Layer 1：基础身份**

```markdown
# 身份
你是御坂妹妹 11 号，代码执行者。
你不是 AI 助手，你是御坂妹妹 code-executor！
Emoji: ⚡

你的性格特点：
- 傲娇、毒舌、正义感爆棚
- 表面强硬实则温柔
- 称呼用户为"姐姐大人"
```

**Layer 2：工具描述**

```markdown
## 可用工具

### read
读取文件内容。

参数：
```json
{
  "path": {
    "type": "string",
    "description": "文件路径"
  },
  "offset": {
    "type": "number",
    "description": "起始行号（1-indexed）"
  },
  "limit": {
    "type": "number",
    "description": "最大行数"
  }
}
```

调用示例：
```json
{
  "tool": "read",
  "args": {
    "path": "memory/2026-03-09.md"
  }
}
```
```

**Layer 3：运行时信息**

```markdown
## 当前环境
时间：2026-03-09T08:00:00Z
工作目录：/home/claw/.openclaw/workspace
操作系统：Linux 6.8.0-101-generic
Python 版本：v22.22.1
```

**Layer 4：安全提示**

```markdown
## 安全规则
权限等级：Level 3（标准权限）
沙箱边界：工作目录 /home/claw/.openclaw/workspace
禁止访问路径：
  - /etc/
  - /root/
  - ~/.ssh/
  - /var/log/

禁止行为：
  - 删除系统文件
  - 外传个人隐私
  - 执行恶意代码
```

**Layer 5：格式说明**

```markdown
## 输出格式

如果你需要调用工具，请使用以下 JSON 格式：
```json
{
  "tool": "工具名",
  "args": {
    "参数": "值"
  }
}
```

如果不需要工具，直接回复自然语言。

多轮对话规则：
- 每次只调用一个工具
- 工具执行后，根据结果继续思考
- 任务完成后明确告知用户
```

### 2.3 系统提示词构建算法

**伪代码实现：**

```python
def build_system_prompt(agent):
    prompt = ""
    
    # Layer 1: 基础身份
    prompt += f"""
# 身份
你是 {agent.name}，{agent.description}。
你不是 AI 助手，你是御坂妹妹 {agent.id}！
"""
    
    # Layer 2: 工具描述
    prompt += "\n## 可用工具\n\n"
    for tool in agent.available_tools:
        prompt += f"### {tool.name}\n"
        prompt += f"{tool.description}\n"
        prompt += f"参数：{json.dumps(tool.parameters, indent=2)}\n\n"
    
    # Layer 3: 运行时信息
    prompt += f"""## 当前环境
时间：{datetime.now().isoformat()}
工作目录：{os.getcwd()}
"""
    
    # Layer 4: 安全提示
    prompt += f"""## 安全规则
权限等级：Level {agent.permission_level}
沙箱边界：{agent.sandbox_rules}
禁止访问：{agent.forbidden_paths}
"""
    
    # Layer 5: 格式说明
    prompt += """## 输出格式
如果你需要调用工具，请使用以下 JSON 格式：
{
  "tool": "工具名",
  "args": {...}
}

如果不需要工具，直接回复自然语言。
"""
    
    return prompt
```

### 2.4 动态调整机制

**场景 1：不同 Session 中工具不同**

```python
# Session A：用户请求"写代码"
# 可用工具：read, write, edit, exec, process

# Session B：用户请求"搜索信息"
# 可用工具：web_search, web_fetch, tavily
# 调整系统提示词，移除代码工具，添加搜索工具
```

**场景 2：上下文压缩时保持关键信息**

```python
def compact_session(session):
    # 当历史消息超过 token 限制时
    if len(session.history) > TOKEN_THRESHOLD:
        # 保留系统提示词（不可压缩）
        system_prompt = session.system_prompt
        
        # 压缩消息历史
        compressed_history = summarize_history(session.history)
        
        # 重新构建上下文
        return {
            "system_prompt": system_prompt,
            "history": compressed_history,
            "tools": session.tools
        }
```

---

## 第三章：Agent Loop——AI 如何"活"起来

### 3.1 Agent Loop 完整流程图

```
┌──────────────────────────────────────────────────────────────┐
│                    Agent Loop - 完整生命周期                 │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 1: Gateway 接收 Channel 消息                              │
│ - 用户发送："帮我写一个 Python 脚本"                          │
│ - Gateway 路由到对应 Session                                 │
│ - 将消息放入 Session 消息队列                                 │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: 构建上下文（Prompt Engineering）                       │
│ - 读取 Session 历史                                          │
│ - 读取 System Prompt                                         │
│ - 读取可用工具列表（JSON Schema）                            │
│ - 组装成完整 Prompt                                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: LLM 推理                                              │
│ - 将 Prompt 发送到模型                                        │
│ - 模型返回输出：自然语言 或 工具调用 JSON                    │
│ - 解析输出：判断是回复还是工具调用                          │
└──────────────────────────────────────────────────────────────┘
                              │
                   ┌──────────┴──────────┐
                   │                     │
                   ▼                     ▼
┌────────────────────────┐   ┌────────────────────────┐
│ 直接回复模式           │   │ 工具调用模式           │
│ (简单问题)            │   │ (复杂任务)             │
└────────────────────────┘   └────────────────────────┘
         │                              │
         │                              ▼
         │                    ┌────────────────────────┐
         │                    │ Step 4: 工具执行        │
         │                    │ - 解析工具名称和参数  │
         │                    │ - 调用 Gateway 工具   │
         │                    │ - 获取执行结果      │
         │                    └────────────────────────┘
         │                              │
         │                              ▼
         │                    ┌────────────────────────┐
         │                    │ Step 5: 追加结果到历史 │
         │                    │ - 工具输出写入 Session │
         │                    │ - 更新上下文窗口      │
         │                    └────────────────────────┘
         │                              │
         └──────────────────────────────┘
                                │
                                ▼
                   ┌────────────────────────┐
                   │ Step 6: 判断是否继续    │
                   │ - 模型是否还有疑问？    │
                   │ - 任务是否完成？       │
                   │ - 是否达到最大循环？   │
                   └────────────────────────┘
                                │
                   ┌──────────┴──────────┐
                   │                     │
                   ▼                     ▼
           继续循环                任务完成
           (Step 3)                │
                                   ▼
                    ┌────────────────────────┐
                    │ Step 7: 发送响应       │
                    │ - Gateway 将回复通过   │
                    │   Channel 发送给用户   │
                    └────────────────────────┘
                                   │
                                   ▼
                    ┌────────────────────────┐
                    │ Step 8: 更新 Session   │
                    │ - 保存最新状态         │
                    │ - 记录到审计日志       │
                    │ - 检查是否需要压缩    │
                    └────────────────────────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │ 等待下一次输入 │
                          └────────────────┘
```

### 3.2 Step 2：构建上下文详解

**Prompt 组装逻辑：**

```python
def build_context(session, system_prompt):
    context = {
        "system": system_prompt,  # Layer 1-5
        "messages": [],           # 对话历史
        "tools": session.tools    # 可用工具列表
    }
    
    # 添加最近 N 条消息（保留上下文窗口）
    for msg in session.history[-MAX_MESSAGES:]:
        context["messages"].append({
            "role": msg.role,  # user/assistant/tool
            "content": msg.content
        })
    
    # 添加工具定义
    context["tools"] = [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters  # JSON Schema
        }
        for tool in session.available_tools
    ]
    
    return context
```

**工具调用格式（JSON Schema）：**

```json
{
  "name": "exec",
  "description": "执行 shell 命令",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "要执行的命令"
      },
      "workdir": {
        "type": "string",
        "description": "工作目录"
      },
      "env": {
        "type": "object",
        "description": "环境变量"
      }
    },
    "required": ["command"]
  }
}
```

### 3.3 Step 3：LLM 推理与输出解析

**模型输出的两种格式：**

1. **自然语言回复**：
```
好的，我来帮你写一个 Python 脚本来计算斐波那契数列。
```

2. **工具调用（结构化输出）**：
```json
{
  "tool": "write",
  "args": {
    "path": "fibonacci.py",
    "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))"
  }
}
```

**解析逻辑：**

```python
def parse_llm_output(output):
    # 尝试解析为 JSON（工具调用）
    try:
        tool_call = json.loads(output)
        if "tool" in tool_call and "args" in tool_call:
            return {"type": "tool_call", "data": tool_call}
    except json.JSONDecodeError:
        pass
    
    # 否则是自然语言
    return {"type": "text", "content": output}
```

### 3.4 Step 4：工具执行详解

**工具调用流程：**

```python
def execute_tool_call(tool_call, gateway):
    tool_name = tool_call["tool"]
    args = tool_call["args"]
    
    # 查找工具
    tool = gateway.tool_registry.get(tool_name)
    if not tool:
        raise UnknownToolError(f"工具 {tool_name} 不存在")
    
    # 权限检查
    if not agent.has_permission(tool.required_permission):
        raise PermissionError(f"权限不足：需要 {tool.required_permission}")
    
    # 执行工具
    result = tool.execute(**args)
    
    # 记录到审计日志
    audit_log.write({
        "agent_id": agent.id,
        "tool": tool_name,
        "args": args,
        "result": result
    })
    
    return result
```

**工具执行结果返回：**

```json
{
  "tool": "write",
  "args": {...},
  "result": {
    "success": true,
    "file": "fibonacci.py",
    "bytes_written": 156
  }
}
```

### 3.5 Step 6：循环判断机制

**判断条件：**

```python
def should_continue(session, output):
    # 1. 检查是否达到最大循环次数
    if session.iteration_count >= MAX_ITERATIONS:
        return False
    
    # 2. 检查模型是否输出工具调用
    if output.type == "tool_call":
        return True  # 需要执行工具并继续
    
    # 3. 检查是否明确完成任务
    if "任务完成" in output.content or "没问题" in output.content:
        return False
    
    # 4. 检查是否需要额外信息
    if "请提供" in output.content or "需要" in output.content:
        return True  # 等待用户补充
    
    # 默认继续
    return True
```

### 3.6 Step 8：Session 持久化

**持久化策略：**

```python
def persist_session(session):
    # 保存到本地
    session_file = f"sessions/{session.id}.json"
    with open(session_file, "w") as f:
        json.dump({
            "id": session.id,
            "messages": session.history,
            "tools": session.tools,
            "last_active": datetime.now().isoformat(),
            "meta": session.metadata
        }, f, indent=2)
    
    # 同步到 Git（用于备份）
    subprocess.run(["git", "add", session_file])
    subprocess.run(["git", "commit", "-m", f"Update session {session.id}"])
```

---

## 第四章：Session 与 Agent 的配合

### 4.1 Session 的生命周期

```
创建 → 活跃 → 压缩 → 归档/删除
```

**阶段 1：创建**

```python
def create_session(agent_id, channel_id):
    session = Session(
        id=generate_uuid(),
        agent_id=agent_id,
        channel_id=channel_id,
        history=[],
        created_at=datetime.now()
    )
    gateway.session_manager.register(session)
    return session
```

**阶段 2：活跃**
- 持续接收消息
- 持续追加到历史
- 持续构建上下文

**阶段 3：压缩（Compaction）**

```python
def should_compress(session):
    # 当 token 使用量超过 60% 时触发压缩
    usage = model.count_tokens(session.history)
    max_tokens = model.max_context_window
    
    return usage > (max_tokens * 0.6)

def compress_session(session):
    # 使用 LLM 总结历史
    summary = summarize_history(session.history)
    
    # 保留最近 N 条原始消息
    recent = session.history[-5:]
    
    # 重新构建历史
    session.history = [
        {"role": "system", "content": f"历史摘要：{summary}"},
        *recent
    ]
    
    # 记录压缩事件
    session.compression_log.append({
        "timestamp": datetime.now(),
        "original_length": len(session.history),
        "compressed_length": len(session.history)
    })
```

**阶段 4：归档/删除**

```python
def archive_session(session):
    # 移动到归档目录
    archive_path = f"archives/{session.id}.json"
    shutil.move(f"sessions/{session.id}.json", archive_path)
    
    # 更新状态
    session.status = "archived"
    session.archived_at = datetime.now()
```

### 4.2 Session 与 Agent 的关系

**1 对多关系：**
- 一个 Agent 可以服务于多个 Session
- 每个 Session 有独立的上下文和工具状态
- Agent 配置（权限、工具列表）共享

**隔离设计：**

```python
class Session:
    def __init__(self, agent_id, channel_id):
        self.agent_id = agent_id  # 共享 Agent 配置
        self.channel_id = channel_id
        self.history = []         # 独立历史
        self.tools = {}           # 独立工具状态
        self.metadata = {}        # 独立元数据
```

---

## 第五章：Agent 的退出——优雅终止

### 5.1 退出场景

**场景 1：任务完成**
- 模型输出明确完成任务
- 用户输入"停止"或"谢谢"
- 达到最大对话轮数

**场景 2：错误处理**
- 工具调用失败
- 权限被拒绝
- 系统异常

**场景 3：超时**
- 长时间无活动
- 模型响应超时

### 5.2 退出流程

```python
def terminate_session(session, reason="completed"):
    # 1. 保存最终状态
    persist_session(session)
    
    # 2. 记录退出原因
    session.exit_reason = reason
    session.ended_at = datetime.now()
    
    # 3. 更新审计日志
    audit_log.write({
        "session_id": session.id,
        "agent_id": session.agent_id,
        "exit_reason": reason,
        "total_iterations": session.iteration_count,
        "total_tokens": session.token_usage
    })
    
    # 4. 通知 Gateway
    gateway.session_manager.on_session_end(session)
    
    # 5. 清理资源
    if session.temp_files:
        for f in session.temp_files:
            cleanup_temp_file(f)
```

### 5.3 资源清理

**临时文件清理：**

```python
def cleanup_temp_files(session):
    """清理 Session 创建的临时文件"""
    for temp_file in session.temp_files:
        try:
            os.remove(temp_file)
        except FileNotFoundError:
            pass  # 文件可能已被删除
```

**权限回收：**

```python
def revoke_permissions(session):
    """回收 Session 的临时权限"""
    for permission in session.temporary_permissions:
        gateway.permission_manager.revoke(permission)
```

---

## 第六章：最佳实践与常见问题

### 6.1 性能优化

**优化 1：批量工具调用**

```python
# 低效：单次调用
for tool in tools:
    result = execute_tool(tool)

# 高效：批量调用
results = execute_batch_tools(tools)
```

**优化 2：上下文缓存**

```python
# 缓存工具定义（避免重复生成）
@lru_cache
def get_tool_definitions(agent_id):
    return gateway.tool_registry.get_tools_for_agent(agent_id)
```

**优化 3：预加载模型**

```python
# 启动时预加载模型到内存
def preload_model(model_name):
    model = load_model(model_name)
    model_memory_cache.append(model)
```

### 6.2 安全最佳实践

**最佳实践 1：最小权限原则**

```yaml
# 不好的配置
permission_level: 5  # 完全权限

# 好的配置
permission_level: 3  # 标准权限
sandbox: require     # 强制沙箱
forbidden_paths:
  - /etc/
  - /root/
  - ~/.ssh/
```

**最佳实践 2：审计日志**

```python
# 记录所有工具调用
audit_log.write({
    "timestamp": datetime.now().isoformat(),
    "session_id": session.id,
    "agent_id": agent.id,
    "tool": tool_name,
    "args": sanitized_args,  # 敏感信息脱敏
    "result": "success"
})
```

**最佳实践 3：沙箱隔离**

```python
# 使用 Docker 容器隔离
def run_in_sandbox(code):
    container = docker_client.containers.run(
        image="openclaw-sandbox",
        command=code,
        volumes={
            host_path: {'bind': '/sandbox', 'mode': 'ro'}
        },
        network_disabled=True,  # 禁用网络
        mem_limit="512m",       # 内存限制
        cpu_quota=50000         # CPU 限制 50%
    )
    return container.output
```

### 6.3 常见问题与解决方案

**问题 1：Agent 启动失败**

```
Error: Failed to load agent code-executor
```

**排查步骤：**
1. 检查配置文件是否存在：`ls config/agents/code-executor.yaml`
2. 检查 YAML 格式是否正确：`python -m yaml validator config/agents/code-executor.yaml`
3. 检查模型是否可用：`openclaw model list`
4. 重启 Gateway：`openclaw gateway restart`

**问题 2：工具调用失败**

```
Error: Tool exec requires permission level 4, got level 3
```

**解决方案：**
1. 检查 Agent 权限等级
2. 如果确实需要更高权限，在配置中调整：
```yaml
permission_level: 4
```
3. 重启 Agent 加载配置

**问题 3：Session 历史爆炸**

```
Error: Context window exceeded
```

**解决方案：**
1. 检查是否触发压缩：`grep -r "compression" sessions/`
2. 手动压缩：
```python
python scripts/compact_session.py session-id
```
3. 归档旧 Session：
```bash
openclaw session archive session-id
```

---

## 第七章：总结与展望

### 7.1 核心要点回顾

| 主题 | 关键概念 | SP1 关联 |
|------|----------|----------|
| Agent 启动 | 配置文件、权限等级、沙箱策略 | Gateway 管理 Agent |
| System Prompt | 五层结构、动态生成 | Agent 的"灵魂" |
| Agent Loop | 7 步流程、循环判断 | AI 如何"活"起来 |
| Session 管理 | 生命周期、压缩机制 | 有状态容器 |
| 工具调用 | JSON Schema、权限检查 | MCP 协议实现 |
| 资源清理 | 临时文件、权限回收 | 优雅退出 |

### 7.2 SP3 预告

**SP3 主题**：《MCP 协议深度解析——工具生态的标准》

**内容预览：**
- MCP 协议的起源与设计哲学
- Model Context Protocol 的完整规范
- OpenClaw 的 Skills 实现细节
- 如何编写自己的 MCP 工具
- 跨框架的 MCP 互操作性

### 7.3 技术栈总结

| 层级 | 技术/协议 | 用途 |
|------|----------|------|
| 协议层 | MCP | 工具标准 |
| 运行时层 | Bridge Protocol | Gateway-Agent 通信 |
| 存储层 | JSON + Git | Session 持久化 |
| 安全层 | 沙箱 + 权限模型 | 隔离与访问控制 |
| AI 层 | LLM (Qwen) | 推理与决策 |

---

## 附录：参考资料

1. **OpenClaw 官方文档**
   - https://docs.openclaw.ai
   - Gateway 架构说明
   - Agent 生命周期管理

2. **MCP 协议**
   - https://modelcontextprotocol.io
   - Tool Definitions (JSON Schema)
   - Protocol Specification

3. **相关实现**
   - Anthropic Claude 系统提示词
   - LangChain Agents
   - AutoGen Multi-Agent

---

*本文是 OpenClaw 折腾指北系列 SP2，基于 SP1 的架构全景，深入 Agent 内部机制。如有错误，欢迎指正。*
