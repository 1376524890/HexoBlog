# 输出目录

这个目录用于存储分析结果和评估报告。

## 文件说明

- `analysis_result.json` - 项目分析结果
- `evaluation_result.json` - 项目评估结果
- `integration_result.json` - 集成结果

## 分析流程

1. Discovery 发现项目 → 保存到 `discovery_results.json`
2. Analysis 深度分析 → 保存到 `analysis_result.json`
3. Evaluation 评估 → 保存到 `evaluation_result.json`
4. 待批准 → 发送到 approval_requests/
