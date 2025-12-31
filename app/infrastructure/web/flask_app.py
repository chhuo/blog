# 负责创建Flask实例、绑定配置（框架底层，无业务逻辑）
from flask import Flask
from app.infrastructure.config import CONFIG


def create_flask_app() -> Flask:
    """创建并配置Flask实例（核心框架初始化）"""
    # 1. 初始化Flask
    app = Flask(__name__)

    # 2. 从配置中读取参数（依赖基础设施层的配置工具）
    app.config["SECRET_KEY"] = CONFIG.SECRET_KEY
    app.config["DEBUG"] = CONFIG.FLASK_DEBUG
    # app.config["DATABASE_URL"] = CONFIG.DATABASE_URL

    # 3. 可扩展：注册全局中间件、异常处理器等（框架级逻辑）
    # app.before_request(xxx)

    return app
