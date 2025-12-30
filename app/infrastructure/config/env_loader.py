from dotenv import load_dotenv
from pathlib import Path
import os
from dataclasses import dataclass  # 用dataclass简化配置类定义
from . import PROJECT_ROOT


# 第一步：加载.env文件（仅执行一次）
def _load_env():
    """内部函数：加载.env，仅初始化时执行"""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 加载.env配置：{env_file}")


# 第二步：封装所有配置为数据类（结构化、易提示、可校验）
@dataclass(frozen=True)  # frozen=True 确保配置只读，避免被修改
class AppConfig:
    # Flask基础配置
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    FLASK_HOST: str = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", 5000))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_123456")

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

    # 可扩展：新增配置直接加字段即可
    # LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# 第三步：初始化配置（加载.env + 创建配置对象，全局唯一）
_load_env()
CONFIG = AppConfig()  # 全局配置对象，后续所有模块直接导入这个对象
