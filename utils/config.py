from dotenv import load_dotenv
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:

    # Flask配置
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    FLASK_HOST: str = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", 5000))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_888888")


def load_config(PROJECT_ROOT: str) -> AppConfig:
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logInfo(f"✅ 加载.env配置：{env_file}")
    else:
        logInfo(f"⚠️ 未找到.env，使用默认配置")

    logInfo(f"📝 日志配置完成 - 级别：{config.LOG_LEVEL} | 目录：{config.LOG_DIR}")

