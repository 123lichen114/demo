import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys
def setup_logger():
    """配置应用日志系统"""
    # 创建日志目录
    log_dir = "error_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件名（包含日期）
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"app_errors_{current_date}.log")
    
    # 创建日志器
    logger = logging.getLogger("dashboard_app")
    logger.setLevel(logging.ERROR)  # 只记录错误级别及以上的日志
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 日志格式（包含时间、模块、函数、错误信息和堆栈）
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(module)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s'
    )
    
    # 文件处理器（限制单个文件大小为5MB，最多保留3个备份）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.ERROR)
    
    # 控制台处理器（开发时使用）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.ERROR)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


    