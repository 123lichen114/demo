import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys

# 模块级变量：存储首次创建的日志目录，确保进程内唯一
_LOG_DIR = None

def setup_logger():
    """配置应用日志系统：仅在服务启动时创建一次日志文件夹"""
    global _LOG_DIR  # 使用全局变量记录日志目录
    
    # 主日志文件夹
    main_log_dir = "Logger"
    if not os.path.exists(main_log_dir):
        os.makedirs(main_log_dir)
    
    # 仅在首次调用时创建时间戳子文件夹
    if _LOG_DIR is None:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # 精确到秒的启动时间
        _LOG_DIR = os.path.join(main_log_dir, current_time)
        os.makedirs(_LOG_DIR, exist_ok=True)  # 确保文件夹创建成功
    
    # 日志文件路径（固定在首次创建的文件夹内）
    log_file = os.path.join(_LOG_DIR, "app.log")
    
    # 创建日志器
    logger = logging.getLogger("dashboard_app")
    logger.setLevel(logging.INFO)  # 记录INFO及以上级别（包含更多信息）
    
    # 避免重复添加处理器（关键：确保处理器只初始化一次）
    if logger.handlers:
        return logger
    
    # 日志格式（包含详细上下文）
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
    file_handler.setLevel(logging.INFO)  # 文件记录INFO及以上
    
    # 控制台处理器（开发调试用）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # 控制台显示INFO及以上
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 记录启动日志（仅首次初始化时输出）
    logger.info(f"服务启动，日志存储目录：{_LOG_DIR}")
    return logger

# 使用示例