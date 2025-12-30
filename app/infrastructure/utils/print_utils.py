# app/infrastructure/utils/print_utils.py
import sys
import os
from datetime import datetime

# 保存原生print
native_print = print
# 日志文件路径（基于项目根目录）
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app.log")


def custom_print(*args, **kwargs):
    """自定义print：时间戳 + 控制台 + 日志文件"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    content = " ".join(map(str, args))
    output = f"{timestamp} {content}"

    # 控制台输出
    native_print(output, **kwargs)
    # 日志文件输出（追加模式，utf-8编码）
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{output}\n")


# 替换全局print
sys.modules['builtins'].print = custom_print
