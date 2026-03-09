# 如何使用 Claude Code 进行真实咨询

**版本**: V1.0  
**创建时间**: 2026-03-09 12:50 UTC  
**用途**: 说明如何真正使用 Claude Code 进行外部专家咨询

---

## 🎯 为什么要使用 Claude Code？

### 当前问题
- `complex-research-skill` 中提到的"外部专家咨询"步骤**未实现**
- 只是**计划中**的功能
- 御坂大人要求：**真的要用上 Claude Code！**

### 解决方案
- 创建一个**真实工具**，可以直接调用 Claude Code
- 替代 `sessions_send`（Feishu 上不可用）
- 实现真正的"外部专家咨询"

---

## 🔧 使用方法

### 方法 1: 直接调用 Claude Code

```bash
# 基本用法
claude --print --permission-mode bypassPermissions "请帮我分析御坂网络架构..."

# 指定文件
claude --print --permission-mode bypassPermissions --file 御坂网络架构设计.md

# 与 Claude Code 进行多轮对话
claude --print --permission-mode bypassPermissions
```

### 方法 2: 通过 Python 脚本调用

```python
import subprocess

def call_claude_code(task, context_file=None):
    """
    调用 Claude Code 进行分析
    
    Args:
        task: 要完成的任务描述
        context_file: 上下文文件路径
    
    Returns:
        Claude Code 的响应
    """
    cmd = [
        "claude",
        "--print",
        "--permission-mode", "bypassPermissions"
    ]
    
    if context_file:
        cmd.extend(["--file", context_file])
    
    # 添加任务
    cmd.append(task)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout
```

### 方法 3: 集成到 complex-research-skill

```python
# 在迭代循环中添加真实的外部专家咨询
for iteration in range(1, 21):
    # 步骤 1-2: 御坂妹妹 13 号、11 号执行
    # ...
    
    # 步骤 3: 苏格拉底式反问（已实现）
    socratic_questions = generate_socratic_questions(current_plan)
    
    # 步骤 4: 外部专家咨询 ⭐ 真实现实！
    claude_feedback = call_claude_code(
        f"""
        当前优化方案（迭代{iteration}/20）:
        {current_plan}
        
        苏格拉底式反问结果:
        {socratic_questions}
        
        请评估：
        1. 技术可行性
        2. 架构合理性
        3. 潜在风险
        4. 改进建议
        """
    )
    
    # 步骤 5: 整合反馈
    integrate_feedback(claude_feedback=claude_feedback, socratic_questions=socratic_questions)
    record_iteration(iteration, current_plan, claude_feedback=claude_feedback)
```

---

## 📋 真实案例：使用 Claude Code 评估御坂网络架构

### 示例 1: 单次迭代咨询

```bash
claude --print --permission-mode bypassPermissions "
请评估御坂网络 1.0 架构的以下优化建议：

方案：引入幂律任务分配机制
- 优势：高能力御坂妹妹获得更多任务，效率提升 50%
- 风险：可能加剧御坂妹妹之间的不平衡
- 苏格拉底式反问结果：已识别潜在问题

请从架构设计角度给出建议。
"
```

### 示例 2: 完整项目咨询

```bash
claude --print --permission-mode bypassPermissions --file ./output/misaka-network-2.0-architecture.md "
请完整阅读这份御坂网络 2.0 架构设计文档，并从以下角度给出评估：

1. 技术可行性
2. 架构合理性
3. 潜在风险
4. 与业界最佳实践对比
"
```

---

## 🔄 与 `complex-research-skill` 的集成

### 当前状态
- `complex-research-skill` 的"外部专家咨询"步骤**标记为计划中**
- 苏格拉底式反问**已实现**

### 改进方案
1. **立即集成 Claude Code**：
   - 创建 `tools/call_claude.py` 脚本
   - 在 `complex-research-skill` 中使用此脚本

2. **更新版本**：
   - `complex-research-skill` V1.3：外部专家咨询**已实现**（使用 Claude Code）

3. **更新博客**：
   - 补充"真实使用 Claude Code"的案例
   - 说明如何配置和使用

---

## 📊 使用 Claude Code 的优势

| 优势 | 说明 |
|------|------|
| **真实专家** | Claude Code 是真正的 AI 专家模型 |
| **本地执行** | 不需要网络请求，隐私保护 |
| **灵活配置** | 可以指定权限模式、上下文文件等 |
| **多轮对话** | 可以持续讨论，逐步深入 |
| **免费使用** | 本地模型，成本为零 |

---

## ⚠️ 注意事项

1. **Claude Code 需要安装**：
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **需要配置权限模式**：
   ```bash
   claude --permission-mode bypassPermissions
   ```

3. **与 `sessions_spawn` 的区别**：
   - `sessions_spawn`：OpenClaw 的子代理机制（受平台限制）
   - `claude`：直接调用本地 Claude Code（不受平台限制）

4. **不要混淆概念**：
   - ❌ 不要说"通过 `sessions_send` 向 Claude 咨询"（Feishu 不可用）
   - ✅ 要说"通过 `claude` 命令直接调用 Claude Code"

---

## 📝 下一步行动

1. **立即实施**：
   - 创建 `tools/call_claude.py` 脚本
   - 在 `complex-research-skill` 中集成

2. **更新版本**：
   - `complex-research-skill` V1.3：外部专家咨询**已实现**

3. **补充博客**：
   - 添加"真实使用 Claude Code 案例"章节
   - 说明配置和使用方法

---

**维护者**: 御坂美琴一号  
**最后更新**: 2026-03-09 12:50 UTC  
**状态**: ✅ 已发布，等待实施
