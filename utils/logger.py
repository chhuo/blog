import logging
import logging.handlers
import os
import json
import inspect
from logging import Logger, LogRecord
from typing import Optional, Tuple

# ==================== 全局单例控制（极简版） ====================
def init_logger(
        log_dir: str = "logs",
        level: str = "INFO",
        use_json: bool = False,
        max_bytes: int = 50 * 1024 * 1024,
        backup_count: int = 30,
) -> None:
    """初始化全局日志（仅调用一次）"""
    if logging.getLogger().handlers:  # 避免重复初始化
        return

    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    # 日志文件名
    from datetime import datetime
    log_file = os.path.join(log_dir, f"app.{datetime.now().strftime('%Y-%m-%d')}.log")

    # 格式器
    if use_json:
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                return json.dumps({
                    "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "process": record.process,
                    "level": record.levelname,
                    "name": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "funcName": record.funcName,
                    "lineno": record.lineno,
                    "exc_info": self.formatException(record.exc_info) if record.exc_info else None
                }, ensure_ascii=False)
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(process)-8d | %(levelname)-8s | %(name)-15s | %(module)s.%(funcName)s():%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # 文件Handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    # 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 配置root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

# ==================== 核心：硬编码栈帧索引（根据调试结果修改） ====================
def logInfo(msg: str, *args, **kwargs):
    """全局INFO日志（硬编码栈帧索引，确保定位到父函数）"""
    logger = logging.getLogger()
    # 硬编码跳过3帧（根据调试结果调整，比如3）
    stack = inspect.stack()
    if len(stack) >= 4:  # 栈帧3是父函数
        frame_info = stack[3]
        # 手动构造LogRecord
        record = LogRecord(
            name=logger.name,
            level=logging.INFO,
            pathname=frame_info.filename,
            lineno=frame_info.lineno,
            msg=msg,
            args=args,
            exc_info=kwargs.get("exc_info"),
            func=frame_info.function,
        )
        # 提取模块名（去掉路径和.py后缀）
        record.module = os.path.basename(frame_info.filename).replace(".py", "")
        record.process = os.getpid()
        # 直接处理记录
        logger.handle(record)
    else:
        # 兜底
        logger.info(msg, *args, **kwargs)

# 其他日志级别同理（复制logInfo，改级别）
def logDebug(msg: str, *args, **kwargs):
    logger = logging.getLogger()
    stack = inspect.stack()
    if len(stack) >= 4:
        frame_info = stack[3]
        record = LogRecord(
            name=logger.name,
            level=logging.DEBUG,
            pathname=frame_info.filename,
            lineno=frame_info.lineno,
            msg=msg,
            args=args,
            exc_info=kwargs.get("exc_info"),
            func=frame_info.function,
        )
        record.module = os.path.basename(frame_info.filename).replace(".py", "")
        record.process = os.getpid()
        logger.handle(record)
    else:
        logger.debug(msg, *args, **kwargs)

def logError(msg: str, *args, **kwargs):
    logger = logging.getLogger()
    stack = inspect.stack()
    if len(stack) >= 4:
        frame_info = stack[3]
        record = LogRecord(
            name=logger.name,
            level=logging.ERROR,
            pathname=frame_info.filename,
            lineno=frame_info.lineno,
            msg=msg,
            args=args,
            exc_info=kwargs.get("exc_info"),
            func=frame_info.function,
        )
        record.module = os.path.basename(frame_info.filename).replace(".py", "")
        record.process = os.getpid()
        logger.handle(record)
    else:
        logger.error(msg, *args, **kwargs)

def logException(msg: str, *args, **kwargs):
    logError(msg, *args, exc_info=True, **kwargs)

# ==================== 补全缺失的get_logger函数 ====================
def get_logger(name: str = "app") -> Logger:
    """获取已配置的logger（兼容原有代码）"""
    init_logger()  # 确保日志已初始化
    return logging.getLogger(name)