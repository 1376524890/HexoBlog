#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问卷星自动化工具 - 主入口
作者：御坂美琴一号
版本：1.0.0
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.questionnaire import QuestionnaireFiller
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger
from src.utils.answer_strategy import AnswerStrategy


def main():
    """主函数"""
    # 加载配置
    config = ConfigLoader.load('config/config.json')
    
    # 初始化日志
    logger = setup_logger(config.get('logging'))
    
    # 初始化答案策略
    answer_strategy = AnswerStrategy.from_config(config.get('answers'))
    
    # 创建问卷填充器
    filler = QuestionnaireFiller(config, answer_strategy, logger)
    
    # 开始填写
    try:
        filler.start()
        logger.info("问卷填写完成！")
    except Exception as e:
        logger.error(f"填写过程中出错：{e}")
        raise


if __name__ == '__main__':
    main()
