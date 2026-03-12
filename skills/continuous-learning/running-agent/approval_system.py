"""
持续运行 Agent - 批准系统
========================

负责管理御坂大人对项目的批准流程。

核心功能:
- 生成审批请求
- 监听批准指令
- 记录批准历史
- 集成已批准项目
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
from enum import Enum

# 配置日志
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """审批状态"""
    PENDING = "pending"  # 待批准
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    PROCESSING = "processing"  # 处理中
    INTEGRATED = "integrated"  # 已集成


@dataclass
class ApprovalRequest:
    """审批请求"""
    request_id: str
    project_name: str
    repo_url: str
    evaluation_result: Dict
    priority: float
    requested_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    integration_notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ApprovalRequest':
        """从字典创建"""
        data['status'] = ApprovalStatus(data['status'])
        return cls(**data)
    
    def generate_approval_message(self) -> str:
        """生成审批消息"""
        eval_result = self.evaluation_result
        
        msg = f"""
⚡【技能集成审批请求】⚡

📦 项目名称：{self.project_name}
🔗 仓库地址：{self.repo_url}
📊 优先级：{self.priority:.2f}
📅 请求时间：{self.requested_at}

---

📈 六维评估:
- 实用性：{eval_result.get('practicality', {}).get('score', 0):.1f}/10
- 创新性：{eval_result.get('innovation', {}).get('score', 0):.1f}/10
- 代码质量：{eval_result.get('code_quality', {}).get('score', 0):.1f}/10
- 文档质量：{eval_result.get('documentation', {}).get('score', 0):.1f}/10
- 维护性：{eval_result.get('maintenance', {}).get('score', 0):.1f}/10
- 集成度：{eval_result.get('integration', {}).get('score', 0):.1f}/10

🎯 综合评分：{eval_result.get('weighted_score', 0):.2f}/10.0
🎯 决策：{eval_result.get('decision', 'pending').upper()}

---

💡 优势:
{chr(10).join('  ✓ ' + s for s in eval_result.get('strengths', ['无'])[:3])}

⚠️ 劣势:
{chr(10).join('  ✗ ' + w for w in eval_result.get('weaknesses', ['无'])[:3])}

📝 建议:
{chr(10).join('  → ' + r for r in eval_result.get('recommendations', ['无'])[:3])}

---

回复 "approve" 批准集成
回复 "reject [理由]" 拒绝并说明原因
回复 "review" 需要人工复审

御坂大人请指示！⚡
"""
        return msg


@dataclass
class ApprovalConfig:
    """批准系统配置"""
    approval_file: str = "approval_requests/pending_approvals.json"  # 审批文件
    history_file: str = "approval_requests/approval_history.json"  # 历史记录
    max_pending: int = 10  # 最大待处理数量
    auto_process: bool = False  # 自动处理已集成
    
    # 审批消息模板
    approval_message_template: str = """
御坂大人！御坂妹妹发现了一个值得集成的技能项目！

项目名称：{project_name}
仓库地址：{repo_url}
综合评分：{score:.2f}/10.0
决策：{decision.upper()}

六维评分:
- 实用性：{practicality:.1f}/10
- 创新性：{innovation:.1f}/10
- 代码质量：{code_quality:.1f}/10
- 文档质量：{documentation:.1f}/10
- 维护性：{maintenance:.1f}/10
- 集成度：{integration:.1f}/10

御坂妹妹已经完成了深度分析和评估，等待您的批准！
御坂大人可以回复 "approve" 批准，或 "reject" 拒绝。

⚡"""
    
    # 回调函数
    on_approval: Optional[Callable] = None
    on_rejection: Optional[Callable] = None


class ApprovalSystem:
    """批准系统"""
    
    def __init__(self, config: Optional[ApprovalConfig] = None):
        """
        初始化 ApprovalSystem
        
        Args:
            config: 配置对象
        """
        self.config = config or ApprovalConfig()
        self.pending_requests: List[ApprovalRequest] = []
        self.history: List[Dict] = []
        
        # 加载现有数据
        self._load_data()
        
        logger.info(f"ApprovalSystem initialized")
        logger.info(f"Pending requests: {len(self.pending_requests)}")
    
    def _load_data(self):
        """加载现有数据"""
        # 加载待审批请求
        approval_path = Path(self.config.approval_file)
        if approval_path.exists():
            try:
                with open(approval_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.pending_requests = [
                    ApprovalRequest.from_dict(req)
                    for req in data.get('requests', [])
                ]
                logger.info(f"Loaded {len(self.pending_requests)} pending requests")
            except Exception as e:
                logger.error(f"Failed to load approvals: {e}")
        
        # 加载历史记录
        history_path = Path(self.config.history_file)
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.history = data.get('history', [])
                logger.info(f"Loaded {len(self.history)} history records")
            except Exception as e:
                logger.error(f"Failed to load history: {e}")
    
    def _save_approvals(self):
        """保存待审批请求"""
        Path(self.config.approval_file).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "requests": [req.to_dict() for req in self.pending_requests],
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.config.approval_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_history(self):
        """保存历史记录"""
        Path(self.config.history_file).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "history": self.history,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.config.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_request(self, project_name: str, repo_url: str, 
                       evaluation_result: Dict, priority: float = 0) -> ApprovalRequest:
        """
        创建审批请求
        
        Args:
            project_name: 项目名称
            repo_url: 仓库 URL
            evaluation_result: 评估结果
            priority: 优先级
            
        Returns:
            审批请求对象
        """
        # 检查是否超限
        if len(self.pending_requests) >= self.config.max_pending:
            logger.warning("Max pending requests reached")
            return None
        
        # 生成请求 ID
        request_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建请求
        request = ApprovalRequest(
            request_id=request_id,
            project_name=project_name,
            repo_url=repo_url,
            evaluation_result=evaluation_result,
            priority=priority
        )
        
        # 添加到待处理列表
        self.pending_requests.append(request)
        self._save_approvals()
        
        logger.info(f"Created approval request: {request_id}")
        
        return request
    
    def approve(self, request_id: str, approved_by: str = "御坂大人") -> bool:
        """
        批准审批请求
        
        Args:
            request_id: 请求 ID
            approved_by: 批准者
            
        Returns:
            是否成功
        """
        for req in self.pending_requests:
            if req.request_id == request_id:
                req.status = ApprovalStatus.APPROVED
                req.approved_by = approved_by
                req.approved_at = datetime.now().isoformat()
                
                # 移动到历史
                self._move_to_history(req)
                self._save_approvals()
                self._save_history()
                
                logger.info(f"Approved request: {request_id}")
                
                # 调用回调
                if self.config.on_approval:
                    self.config.on_approval(req)
                
                return True
        
        return False
    
    def reject(self, request_id: str, reason: str, 
               rejected_by: str = "御坂大人") -> bool:
        """
        拒绝审批请求
        
        Args:
            request_id: 请求 ID
            reason: 拒绝原因
            rejected_by: 拒绝者
            
        Returns:
            是否成功
        """
        for req in self.pending_requests:
            if req.request_id == request_id:
                req.status = ApprovalStatus.REJECTED
                req.rejection_reason = reason
                req.approved_by = rejected_by
                req.approved_at = datetime.now().isoformat()
                
                # 移动到历史
                self._move_to_history(req)
                self._save_approvals()
                self._save_history()
                
                logger.info(f"Rejected request: {request_id}")
                
                # 调用回调
                if self.config.on_rejection:
                    self.config.on_rejection(req)
                
                return True
        
        return False
    
    def _move_to_history(self, request: ApprovalRequest):
        """移动到历史记录"""
        self.history.append({
            "request": request.to_dict(),
            "moved_at": datetime.now().isoformat()
        })
        
        # 保留最近 100 条历史
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def get_pending(self) -> List[ApprovalRequest]:
        """获取所有待审批请求"""
        return [req for req in self.pending_requests 
                if req.status == ApprovalStatus.PENDING]
    
    def get_by_project(self, project_name: str) -> Optional[ApprovalRequest]:
        """根据项目名称获取请求"""
        for req in self.pending_requests:
            if req.project_name == project_name:
                return req
        return None
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """根据请求 ID 获取"""
        for req in self.pending_requests:
            if req.request_id == request_id:
                return req
        return None
    
    def generate_approval_report(self) -> str:
        """生成审批报告"""
        pending = self.get_pending()
        
        if not pending:
            return "📭 暂无待审批项目"
        
        lines = [
            "📋【技能集成待审批报告】",
            f"⏰ 报告时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📦 待审批数量：{len(pending)}",
            "",
            "=" * 60
        ]
        
        for i, req in enumerate(pending, 1):
            eval_result = req.evaluation_result
            
            lines.extend([
                f"#{i} {req.project_name}",
                f"   URL: {req.repo_url}",
                f"   优先级：{req.priority:.2f}",
                f"   综合评分：{eval_result.get('weighted_score', 0):.2f}/10.0",
                f"   决策：{eval_result.get('decision', 'pending').upper()}",
                "",
                "六维评分:",
                f"   - 实用性：{eval_result.get('practicality', {}).get('score', 0):.1f}/10",
                f"   - 创新性：{eval_result.get('innovation', {}).get('score', 0):.1f}/10",
                f"   - 代码质量：{eval_result.get('code_quality', {}).get('score', 0):.1f}/10",
                f"   - 文档质量：{eval_result.get('documentation', {}).get('score', 0):.1f}/10",
                f"   - 维护性：{eval_result.get('maintenance', {}).get('score', 0):.1f}/10",
                f"   - 集成度：{eval_result.get('integration', {}).get('score', 0):.1f}/10",
                "",
                "-" * 60
            ])
        
        lines.append(f"\n御坂大人请批示！⚡")
        
        return '\n'.join(lines)
    
    def parse_approval_command(self, command: str) -> Dict:
        """
        解析批准指令
        
        Args:
            command: 用户指令
            
        Returns:
            解析结果 {action, request_id, reason}
        """
        command = command.strip().lower()
        
        # 提取 request_id (格式：req_xxx 或 #1, #2)
        request_id = None
        
        if command.startswith(('req_', 'approve req_', 'reject req_')):
            parts = command.split()
            for part in parts:
                if part.startswith('req_'):
                    request_id = part
                    break
        
        elif command.startswith('#'):
            try:
                index = int(command.split()[0].replace('#', ''))
                pending = self.get_pending()
                if 0 < index <= len(pending):
                    request_id = pending[index - 1].request_id
            except:
                pass
        
        action = None
        reason = None
        
        if command.startswith('approve'):
            action = 'approve'
            if request_id is None:
                # 默认为第一个待审批
                pending = self.get_pending()
                if pending:
                    request_id = pending[0].request_id
                    action = 'approve'
        
        elif command.startswith('reject'):
            action = 'reject'
            # 提取原因
            parts = command.split(' ', 1)
            if len(parts) > 1:
                reason = parts[1]
            else:
                reason = "未说明原因"
        
        elif command == 'report':
            action = 'report'
        
        elif command == 'list':
            action = 'list'
        
        return {
            'action': action,
            'request_id': request_id,
            'reason': reason
        }
    
    def process_command(self, command: str) -> str:
        """
        处理命令
        
        Args:
            command: 用户命令
            
        Returns:
            处理结果消息
        """
        parsed = self.parse_approval_command(command)
        action = parsed['action']
        
        if action == 'approve':
            request_id = parsed['request_id']
            if self.approve(request_id):
                return f"✅ 已批准项目集成请求：{request_id}"
            else:
                return f"❌ 未找到请求：{request_id}"
        
        elif action == 'reject':
            request_id = parsed['request_id']
            reason = parsed['reason']
            if self.reject(request_id, reason):
                return f"❌ 已拒绝项目集成请求：{request_id}\n原因：{reason}"
            else:
                return f"❌ 未找到请求：{request_id}"
        
        elif action == 'report':
            return self.generate_approval_report()
        
        elif action == 'list':
            pending = self.get_pending()
            if not pending:
                return "📭 暂无待审批项目"
            
            lines = ["待审批项目列表:"]
            for i, req in enumerate(pending, 1):
                lines.append(f"  #{i} {req.project_name} (ID: {req.request_id})")
            
            return '\n'.join(lines)
        
        else:
            return "❓ 未知命令。可用命令: approve, reject, report, list"
    
    def close(self):
        """清理资源"""
        self._save_approvals()
        self._save_history()
        logger.info("ApprovalSystem closed")


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Approval System for Running Agent")
    parser.add_argument("command", nargs="?", help="Command (approve/reject/report/list)")
    parser.add_argument("--request-id", help="Request ID")
    parser.add_argument("--reason", help="Rejection reason")
    
    args = parser.parse_args()
    
    system = ApprovalSystem()
    
    try:
        if args.command:
            result = system.process_command(args.command)
            print(result)
        else:
            # 显示报告
            print(system.generate_approval_report())
    finally:
        system.close()


if __name__ == "__main__":
    main()
