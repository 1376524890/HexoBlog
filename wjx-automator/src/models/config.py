"""
配置数据模型
Configuration data models
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class BrowserConfig:
    """浏览器配置"""
    driver_path: Optional[str] = None
    headless: bool = True
    window_size: tuple = (1920, 1080)
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    wait_timeout: int = 30
    explicit_wait: int = 10


@dataclass
class ExecutionConfig:
    """执行配置"""
    workers: int = 5
    max_retries: int = 3
    retry_delay: int = 2
    request_timeout: int = 60
    delay_between_submissions: int = 5


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    output_dir: str = "logs"
    file_name: str = "wjx_automator"
    max_size_mb: int = 10
    backup_count: int = 5


@dataclass
class QuestionnaireConfig:
    """问卷配置"""
    url: str = "https://v.wjx.cn/vm/PhfZxRV.aspx"
    total_questions: int = 28
    
    # 问题类型分类
    question_types: dict = field(default_factory=lambda: {
        "single_choice": [1, 5, 6, 14],
        "multiple_choice": [2, 3, 4, 11, 13],
        "scale": [7, 8, 9, 10, 12, 15, 16, 17, 18, 24],
        "short_answer": [25, 26, 27, 28]
    })


@dataclass
class AdvancedConfig:
    """高级配置"""
    save_screenshots: bool = False
    save_html: bool = False
    proxy: Optional[str] = None
    cookies_file: Optional[str] = None


@dataclass
class Config:
    """主配置类"""
    questionnaire: QuestionnaireConfig = field(default_factory=QuestionnaireConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    data: dict = field(default_factory=lambda: {
        "stats_file": "data/q28_response.csv",
        "xpath_file": "xpath_config.json"
    })
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)
    
    @classmethod
    def from_json(cls, filepath: str) -> "Config":
        """从 JSON 文件加载配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 递归转换为 Config 对象
        return cls._from_dict(data)
    
    @classmethod
    def _from_dict(cls, data: dict) -> "Config":
        """从字典转换为 Config 对象"""
        config = {}
        
        if 'questionnaire' in data:
            config['questionnaire'] = QuestionnaireConfig(**data['questionnaire'])
        if 'browser' in data:
            config['browser'] = BrowserConfig(**data['browser'])
        if 'execution' in data:
            config['execution'] = ExecutionConfig(**data['execution'])
        if 'logging' in data:
            config['logging'] = LoggingConfig(**data['logging'])
        if 'data' in data:
            config['data'] = data['data']
        if 'advanced' in data:
            config['advanced'] = AdvancedConfig(**data['advanced'])
        
        return cls(**config)
    
    def to_json(self, filepath: str) -> None:
        """保存到 JSON 文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"Config(questionnaire_url='{self.questionnaire.url}')"
