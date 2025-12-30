# 负责启动HTTP服务、注册路由（对外暴露接口，仅接口层有Flask路由依赖）
from app.infrastructure.web.flask_app import create_flask_app
from app.infrastructure.config import CONFIG


def start_flask_server():
    """启动Flask HTTP服务（仅做服务启动，无核心业务）"""
    # 1. 创建Flask实例
    app = create_flask_app()

    # 2. 注册路由（示例：接口层的路由，业务逻辑调用应用层）
    @app.route("/health")
    def health_check():
        return {"status": "ok"}, 200

    app.run(
        host=CONFIG.FLASK_HOST,
        port=CONFIG.FLASK_PORT,
        debug=CONFIG.FLASK_DEBUG
    )
