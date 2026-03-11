"""
问卷星自动填写系统主入口
Automated WJX Questionnaire Filler
"""

import argparse
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from src.core.questionnaire import QuestionnaireAutoFiller
from src.utils.logger import setup_logger
from src.utils.stats import load_question_stats
from src.models.config import Config

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="问卷星自动填写系统 - 基于统计分布批量填写问卷",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用配置文件
  python main.py --config config.json
  
  # 指定数据文件
  python main.py --data data/q28_response.csv
  
  # 使用自定义线程数
  python main.py --workers 10
  
  # 仅生成填充数据不提交
  python main.py --dry-run
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.json",
        help="配置文件路径 (默认：config.json)"
    )
    
    parser.add_argument(
        "--data", "-d",
        type=str,
        default="data/q28_response.csv",
        help="问卷数据统计文件路径 (默认：data/q28_response.csv)"
    )
    
    parser.add_argument(
        "--xpath", "-x",
        type=str,
        default="xpath_config.json",
        help="XPath 配置路径 (默认：xpath_config.json)"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=5,
        help="并发线程数 (默认：5)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅生成填充数据，不实际提交"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="logs",
        help="日志输出目录 (默认：logs)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger(
        level=logging.DEBUG if args.verbose else logging.INFO,
        output_dir=args.output_dir
    )
    
    logger.info("=" * 80)
    logger.info("问卷星自动填写系统启动")
    logger.info("=" * 80)
    
    try:
        # 加载配置
        logger.info(f"加载配置文件：{args.config}")
        config = Config.from_json(args.config)
        
        # 加载问题统计
        logger.info(f"加载问题统计：{args.data}")
        question_stats = load_question_stats(args.data)
        
        # 创建自动填写器
        filler = QuestionnaireAutoFiller(
            config=config,
            question_stats=question_stats,
            xpath_config=args.xpath,
            logger=logger
        )
        
        if args.dry_run:
            logger.info("干燥模式：仅生成填充数据，不实际提交")
            # 生成示例填充数据
            examples = filler.generate_fill_examples(count=10)
            logger.info(f"生成了 {len(examples)} 个填充示例")
            for i, example in enumerate(examples[:3], 1):  # 只显示前 3 个
                logger.info(f"\n示例 {i}:")
                for qid, answer in example.items():
                    logger.info(f"  Q{qid}: {answer}")
        else:
            # 执行批量填写
            results = filler.batch_fill(
                total_records=210,
                workers=args.workers
            )
            
            # 输出统计
            logger.info("\n" + "=" * 80)
            logger.info("填写完成统计")
            logger.info("=" * 80)
            logger.info(f"成功：{results['success']}")
            logger.info(f"失败：{results['failed']}")
            logger.info(f"成功率：{results['success_rate']:.2f}%")
            
        return 0
        
    except Exception as e:
        logger.error(f"程序执行失败：{e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
