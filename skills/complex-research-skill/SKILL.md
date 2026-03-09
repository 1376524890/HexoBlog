# complex-research-skill - 复杂研究任务处理技能

**版本**: V1.0  
**创建时间**: 2026-03-09  
**用途**: 处理需要深度学习、多轮迭代、专家咨询的复杂研究任务

---

## 📋 技能定位

这个 skill 专门处理**需要多步骤、多 agent 协作、持续优化的复杂研究任务**，例如：
- 📚 arXiv 论文深度分析与架构对比
- 🔍 开源项目代码审查与技术评估
- 🧠 系统性技术调研与方案制定
- 📊 竞品分析与优化建议

---

## 🎯 核心流程

### 1️⃣ 任务理解与规划
```
御坂大人：帮我 [研究任务描述]
  │
  ▼
御坂美琴一号：
  - 理解任务范围
  - 识别所需技能/工具
  - 制定研究计划
  - 分派给子代理
```

### 2️⃣ 数据收集
御坂妹妹 16 号执行：
- 🌐 访问目标网站/文档
- 📄 读取相关论文/代码
- 🔎 搜索补充资料
- 📁 收集本地项目文件

### 3️⃣ 深度分析
御坂妹妹 13 号执行：
- 📊 对比现有系统与研究结果
- 🔍 找出差异点
- 💡 提出初步优化建议

### 4️⃣ 迭代优化循环 ⭐ 核心
**执行 N 次迭代**（通常 20 次）：

```python
for iteration in range(1, N+1):
    # 步骤 1: 深入研究
    subagent_analyst = sessions_spawn(
        agentId="research-analyst",
        task=f"迭代{iteration}: 深入研究 [具体优化点]"
    )
    
    # 步骤 2: 代码评估
    subagent_code = sessions_spawn(
        agentId="code-executor",
        task=f"迭代{iteration}: 评估实现复杂度"
    )
    
    # 步骤 3: 整合当前方案
    current_plan = compile_iteration_results()
    
    # 步骤 4: 向 Claude 寻求改进意见
    claude_feedback = sessions_send(
        agentId="code-executor",  # 或其他 Claude 实例
        message=f"""
        当前优化方案（迭代{iteration}/N）:
        {current_plan}
        
        请评估：
        1. 技术可行性
        2. 架构合理性
        3. 潜在风险
        4. 改进建议
        """
    )
    
    # 步骤 5: 整合反馈并记录
    integrate_feedback(claude_feedback)
    record_iteration(iteration, current_plan, claude_feedback)
```

### 5️⃣ 最终汇报
- 📄 输出完整优化方案
- 📊 改进前后对比
- 🗺️ 实施路线图
- ⚠️ 风险评估

---

## 🤖 御坂妹妹团队配置

| Agent | ID | 职责 | 使用场景 |
|-------|-----|------|----------|
| 御坂美琴一号 | main | **监督/调度/汇总** | 全程监督，确保迭代完成 |
| 御坂妹妹 13 号 | research-analyst | 论文研究/分析 | 深度分析，技术可行性评估 |
| 御坂妹妹 11 号 | code-executor | 代码分析 | 实现复杂度评估，代码审查 |
| 御坂妹妹 16 号 | web-crawler | 数据收集 | 网页抓取，论文下载 |
| 御坂妹妹 17 号 | memory-organizer | 记忆整理 | 迭代记录归档 |

---

## 🛠️ 工具使用指南

### 1. sessions_spawn（子代理）
```python
sessions_spawn(
    task="御坂大人要求 [具体任务描述]",
    label="任务标签",
    model="model_id",
    runtime="subagent"  # ✅ 正确
    # runtime="acp"  ❌ 不要用，需要 ACX 插件
)
```

### 2. sessions_send（向 Claude 求建议）
```python
sessions_send(
    agentId="code-executor",  # 或其他 Claude 实例
    message="当前方案 + 请求评估"
)
```

### 3. 记忆记录
```python
# 每次迭代记录
write(
    path=f"memory/archives/iteration-{iteration}.md",
    content=f"""
    ## 迭代 {iteration}/{TOTAL_ITERATIONS}
    **日期**: YYYY-MM-DD
    **核心改进**: [...]
    **Claude 建议**: [...]
    **待解决问题**: [...]
    """
)
```

### 4. web_fetch（网页转 Markdown）
```python
web_fetch(
    url="https://r.jina.ai/https://论文链接",
    extractMode="markdown"
)
```

---

## 📝 输出文档结构

### 最终方案文档
```
output/
└── [项目名称]-architecture.md
```

包含：
- 📋 执行摘要
- 🏗️ 架构对比表
- 🎯 核心优化点详解
- 🔄 实施路线图
- ⚠️ 技术风险评估
- 💡 创新点总结

### 迭代记录
```
memory/archives/
├── iteration-01.md (架构分析)
├── iteration-02.md (优化点 1)
├── ...
└── iteration-20.md (最终报告)
```

### 记忆更新
```
memory/YYYY-MM-DD.md
- 记录研究完成情况
- 重要决策和发现
```

---

## ⚠️ 注意事项

### ❌ 不要使用 acp runtime
```python
# 错误示例
sessions_spawn(
    runtime="acp",  # ❌ 错误！
    agentId="..."
)

# 正确示例
sessions_spawn(
    runtime="subagent",  # ✅ 正确！
    agentId="..."
)
```

### ❌ Feishu 不支持线程绑定
```python
# 错误示例
sessions_spawn(
    thread=True,  # ❌ Feishu 不支持
    ...
)

# 正确示例
sessions_spawn(
    thread=False,  # ✅ 正确
    ...
)
```

### ✅ 每次迭代都要记录
- 记录到 `memory/archives/iteration-XX.md`
- 记录到 `memory/YYYY-MM-DD.md`（当天总结）

### ✅ 每次迭代都要向 Claude 求建议
- 使用 `sessions_send` 发送当前方案
- 请求架构层面的改进建议
- 整合反馈到下一轮优化

---

## 💡 使用示例

### 示例 1: arXiv 论文研究
```
御坂大人：上网搜一下多智能体相关的 arXiv 论文，帮我分析并给出优化建议
```

御坂美琴一号会：
1. 分派御坂妹妹 16 号搜索 arXiv
2. 分派御坂妹妹 13 号深度分析
3. 启动 20 次迭代优化
4. 向 Claude 寻求架构建议
5. 输出完整优化方案

### 示例 2: 开源项目评估
```
御坂大人：帮我评估这个开源项目是否适合集成到御坂网络
https://github.com/xxx/xxx
```

御坂美琴一号会：
1. 分派御坂妹妹 16 号抓取代码
2. 分派御坂妹妹 11 号代码审查
3. 分析集成可行性和优化空间
4. 20 次迭代优化集成方案
5. 输出评估报告和集成路线图

---

## 🎯 最佳实践

### 1. 明确任务范围
在任务描述中：
- ✅ 明确研究目标
- ✅ 明确输出格式
- ✅ 明确迭代次数（默认 20 次）

### 2. 设置合理的模型
```python
model="local-vllm/Qwen/Qwen3.5-35B-A3B-FP8"  # ✅ 本地模型
# model="remote-model-id"  # 或使用远程模型
```

### 3. 监督迭代进度
御坂美琴一号需要：
- ✅ 跟踪每次迭代完成
- ✅ 确保每次都有 Claude 反馈
- ✅ 记录到 memory 文件
- ✅ 最终输出完整方案

### 4. 整理到记忆文档
研究完成后：
- ✅ 更新 `MEMORY.md`
- ✅ 记录到 `memory/YYYY-MM-DD.md`
- ✅ 更新 TOOLS.md（如果开发了新工具）

---

## 📊 性能指标

| 指标 | 说明 | 优化方向 |
|------|------|----------|
| **迭代次数** | 20 次（可调整） | 根据任务复杂度调整 |
| **研究深度** | 论文 + 代码 + 本地对比 | 深度 > 广度 |
| **专家咨询** | 每次向 Claude 求建议 | 确保建议质量 |
| **记录完整性** | 每次迭代都有文档 | 可追溯 |

---

## 🔧 扩展方向

### 1. 自动化迭代控制
- 自动判断迭代是否完成
- 自动评估质量
- 自动决定是否继续

### 2. 多 Claude 并行咨询
- 同时咨询多个 Claude 实例
- 综合不同意见
- 形成更全面的方案

### 3. 外部专家接入
- 接入人类专家反馈
- 社区众包评审
- 学术顾问咨询

---

## 📝 版本历史

### V1.0 (2026-03-09)
- ✅ 初始版本
- ✅ 20 次迭代循环机制
- ✅ Claude 咨询流程
- ✅ 完整输出文档模板

---

## 🚀 总结

这个 skill 的核心价值：
1. **复杂任务分解** - 将大任务拆解为可执行的子任务
2. **多 agent 协作** - 御坂妹妹各司其职，高效配合
3. **持续优化** - 20 次迭代确保方案质量
4. **专家咨询** - 每次迭代向 Claude 求建议
5. **完整记录** - 每次迭代都有文档，可追溯

**适用场景**:
- 📚 arXiv 论文研究
- 🔍 开源项目评估
- 🧠 系统性技术调研
- 📊 竞品分析

---

**维护者**: 御坂美琴一号  
**最后更新**: 2026-03-09  
**状态**: ✅ V1.0 已发布