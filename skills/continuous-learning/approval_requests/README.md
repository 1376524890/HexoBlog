# 待批准请求存储目录
# ===================

这个目录用于存储待批准的项目请求和审批历史。

## 文件说明

- `pending_approvals.json` - 待审批请求列表
- `approval_request_YYYYMMDD_HHMMSS.json` - 单个审批请求文件
- `approval_history.json` - 审批历史记录

## 审批流程

1. 御坂妹妹发现项目 → 添加到队列
2. 御坂妹妹分析项目 → 生成评估报告
3. 生成待批准列表 → 保存到本目录
4. 御坂大人审批 → approve/reject
5. 批准 → 自动集成到 skills/

## 示例审批

御坂大人可以回复:
- `approve` 或 `approve #1` - 批准第一个项目
- `approve req_xxx` - 批准指定请求
- `reject #1 理由` - 拒绝项目并说明原因
- `report` - 查看待审批报告
- `list` - 列出待审批项目
