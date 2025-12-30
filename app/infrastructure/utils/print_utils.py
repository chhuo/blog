# app/infrastructure/utils/print_utils.py
import sys
import os
from datetime import datetime
from . import PROJECT_ROOT

# 保存原生print
native_print = print

# 2. 定义日志目录和文件路径/
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime("%Y-%m-%d")}.log")


def custom_print(*args, **kwargs):
    """自定义print：时间戳 + 控制台 + 日志文件"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    content = " ".join(map(str, args))
    output = f"{timestamp} {content}"

    # 控制台输出
    native_print(output, **kwargs)

    # 3. 确保logs目录存在（首次运行自动创建）
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # 日志文件输出（追加模式，utf-8编码）
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{output}\n")

