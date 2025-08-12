import logging
import os
from datetime import datetime

def setup_logging():
    """配置日志系统并返回一个日志器实例"""
    # 确保日志目录存在
    log_dir = "error_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件名包含日期
    log_filename = f"{log_dir}/app_errors_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 创建日志器
    logger = logging.getLogger('user_behavior_analysis')
    logger.setLevel(logging.ERROR)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建文件处理器
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.ERROR)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志器
        logger.addHandler(file_handler)
    
    return logger

# 创建一个全局日志器实例，供其他模块直接导入使用
logger = setup_logging()
    