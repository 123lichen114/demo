import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys

_LOG_DIR = None

def setup_logger():
    global _LOG_DIR
    
    main_log_dir = "Logger"
    if not os.path.exists(main_log_dir):
        os.makedirs(main_log_dir)
    
    if _LOG_DIR is None:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        _LOG_DIR = os.path.join(main_log_dir, current_time)
        os.makedirs(_LOG_DIR, exist_ok=True)
    
    log_file = os.path.join(_LOG_DIR, "app.log")
    
    logger = logging.getLogger("dashboard_app")
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(module)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s'
    )
    
    # 仅保留文件处理器（移除控制台处理器）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.info(f"服务启动，日志存储目录：{_LOG_DIR}")
    return logger