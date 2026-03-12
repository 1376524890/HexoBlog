"""
持续运行 Agent - 主程序
======================

持续运行的智能代理，负责从 GitHub 持续搜索、分析、评估 AI 项目，
等待御坂大人批准后自动集成到 OpenClaw Skill 系统。
"""

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# 添加当前目录和父目录到路径，以便导入现有模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

# 导入队列管理和批准系统
from queue_manager import QueueManager, QueueStatus
from approval_system import ApprovalSystem, ApprovalStatus

# 导入现有模块
from discovery import DiscoveryEngine, DiscoveryConfig
from evaluation import ProjectEvaluator, EvaluationConfig
from analysis import ProjectAnalyzer, AnalysisConfig
from integration import SkillIntegrator, IntegrationConfig


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('running-agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RunningAgent:
    """持续运行 Agent 主程序"""
    
    def __init__(self):
        """初始化 RunningAgent"""
        self.running = True
        self.config = self._load_config()
        
        # 初始化组件
        self.queue_manager = QueueManager()
        self.approval_system = ApprovalSystem()
        
        # 初始化工具
        self.discovery_engine = DiscoveryEngine(
            token=self.config.get('github_token'),
            config=DiscoveryConfig(
                keywords=self.config.get('discovery_keywords', ['skill', 'agent', 'ai']),
                min_stars=self.config.get('min_stars', 10),
                min_forks=self.config.get('min_forks', 2),
                limit=self.config.get('discovery_limit', 50)
            )
        )
        
        self.evaluator = ProjectEvaluator(config=EvaluationConfig())
        self.analyzer = ProjectAnalyzer(config=AnalysisConfig())
        self.integrator = SkillIntegrator(config=IntegrationConfig())
        
        # 统计信息
        self.stats = {
            "projects_discovered": 0,
            "projects_analyzed": 0,
            "projects_approved": 0,
            "projects_rejected": 0,
            "projects_integrated": 0,
            "start_time": datetime.now().isoformat(),
            "last_run": None
        }
        
        logger.info("=" * 60)
        logger.info("⚡ 持续运行 Agent 已启动！⚡")
        logger.info(f"启动时间：{self.stats['start_time']}")
        logger.info(f"当前队列大小：{self.queue_manager.get_queue_size()}")
        logger.info("=" * 60)
        
        self._setup_signals()
    
    def _load_config(self) -> dict:
        """加载配置"""
        config_file = Path(__file__).parent / "running_agent_config.yaml"
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except ImportError:
                return {}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                return {}
        return {}
    
    def _setup_signals(self):
        """设置信号处理"""
        def signal_handler(sig, frame):
            logger.info("收到终止信号，正在关闭...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """主循环"""
        logger.info("开始运行主循环...")
        
        while self.running:
            try:
                # 1. 检查队列状态
                queue_status = self.queue_manager.get_queue_status()
                logger.info(f"队列状态：{queue_status['total']} / {queue_status['max_size']}")
                
                # 2. 检查是否有待批准的项目
                pending_approvals = self.approval_system.get_pending()
                if pending_approvals:
                    logger.info(f"发现 {len(pending_approvals)} 个待批准项目")
                    report = self.approval_system.generate_approval_report()
                    logger.info(report)
                
                # 3. 检查队列是否已满
                if self.queue_manager.is_queue_full():
                    logger.info("队列已满，等待处理...")
                    self._save_stats()
                    time.sleep(self.config.get('check_interval', 300))
                    continue
                
                # 4. 执行 Discovery 搜索
                logger.info("执行 GitHub 项目搜索...")
                projects = self.discovery_engine.search()
                
                if projects:
                    logger.info(f"发现 {len(projects)} 个项目")
                    self.stats['projects_discovered'] += len(projects)
                    
                    # 添加到队列
                    added_count = 0
                    for project in projects:
                        item = self.queue_manager.add_project(
                            project_name=project.name,
                            repo_url=project.html_url,
                            stars=project.stars,
                            forks=project.forks,
                            updated_at=project.updated_at
                        )
                        if item:
                            added_count += 1
                    
                    logger.info(f"成功添加 {added_count} 个项目到队列")
                    if added_count == 0:
                        logger.info("队列已满，进入等待模式")
                
                # 5. 处理已批准的项目
                self._process_approved_projects()
                
                # 6. 保存统计
                self.stats['last_run'] = datetime.now().isoformat()
                self._save_stats()
                
                # 7. 等待下一次循环
                sleep_time = self.config.get('check_interval', 300)
                logger.info(f"等待 {sleep_time} 秒后继续...")
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"主循环错误：{e}", exc_info=True)
                time.sleep(60)
        
        self.close()
    
    def _process_approved_projects(self):
        """处理已批准的项目"""
        pending_approvals = self.queue_manager.get_evaluation_queue()
        
        for item in pending_approvals:
            if item.evaluation_result and item.evaluation_result.get('decision') == 'accept':
                logger.info(f"处理已批准的项目：{item.project_name}")
                
                try:
                    integration_result = self.integrator.integrate_project(
                        repo_url=item.repo_url,
                        repo_name=item.project_name,
                        evaluation_result=item.evaluation_result
                    )
                    
                    if integration_result:
                        logger.info(f"成功集成：{item.project_name}")
                        self.stats['projects_integrated'] += 1
                        self.queue_manager.update_project(
                            item.repo_url,
                            status=QueueStatus.INTEGRATED
                        )
                    else:
                        logger.warning(f"集成失败：{item.project_name}")
                        
                except Exception as e:
                    logger.error(f"集成过程中出错：{e}", exc_info=True)
    
    def notify_user(self, message: str):
        """通知用户 (御坂大人)"""
        notification_file = Path(__file__).parent / "notifications" / "latest_notification.txt"
        notification_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(f"通知时间：{datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n")
            f.write(message + "\n")
        
        logger.info("通知已保存到文件")
    
    def _save_stats(self):
        """保存统计信息"""
        stats_file = Path(__file__).parent / "agent_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        logger.debug("统计信息已保存")
    
    def process_command(self, command: str) -> str:
        """处理用户命令"""
        return self.approval_system.process_command(command)
    
    def get_status(self) -> str:
        """获取系统状态"""
        queue_status = self.queue_manager.get_queue_status()
        approval_pending = len(self.approval_system.get_pending())
        
        lines = [
            "📊【持续运行 Agent 状态】",
            f"⏰ 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"🔄 运行状态：{'运行中' if self.running else '已停止'}",
            "",
            "📦 队列信息:",
            f"   当前大小：{queue_status['total']}",
            f"   最大容量：{queue_status['max_size']}",
            f"   已满：{'是' if queue_status['full'] else '否'}",
            "",
            "📋 审批信息:",
            f"   待审批：{approval_pending}",
            "",
            "📈 统计信息:",
            f"   发现项目：{self.stats['projects_discovered']}",
            f"   分析项目：{self.stats['projects_analyzed']}",
            f"   已集成：{self.stats['projects_integrated']}",
            "",
            "=" * 60
        ]
        
        return '\n'.join(lines)
    
    def close(self):
        """清理资源"""
        logger.info("正在关闭 RunningAgent...")
        self.running = False
        self.discovery_engine.close()
        self.analyzer.close()
        self.approval_system.close()
        self.queue_manager.close()
        self.stats['end_time'] = datetime.now().isoformat()
        self._save_stats()
        logger.info("RunningAgent 已关闭")


def main():
    """主函数"""
    agent = RunningAgent()
    
    try:
        if len(sys.argv) > 1:
            command = ' '.join(sys.argv[1:])
            
            if command == 'status':
                print(agent.get_status())
            elif command == 'help':
                print("""
持续运行 Agent 命令:
  status     - 查看系统状态
  report     - 查看待审批报告
  approve    - 批准项目集成
  reject     - 拒绝项目集成
  list       - 列出待审批项目
  run        - 启动持续运行模式
  """)
            else:
                result = agent.process_command(command)
                print(result)
        else:
            agent.run()
            
    except KeyboardInterrupt:
        logger.info("收到中断信号")
        agent.close()
    except Exception as e:
        logger.error(f"运行错误：{e}", exc_info=True)
        agent.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
