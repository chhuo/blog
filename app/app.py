# app/app.py（必须放在根目录的app文件夹下）
import os

from flask import Flask, send_file


def create_app():
    """Flask应用工厂函数（必须有这个函数，且返回Flask实例）"""
    app = Flask(__name__)

    # 测试路由（验证应用是否正常）
    @app.route("/")
    def index():
        return {
            "code": 200,
            "msg": "Flask服务启动成功（Windows+Waitress）",
            "path": "app/app.py"
        }

    @app.route('/cs', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_vue(path):
        FRONTEND_DIR = r"D:\project\blog\blog-frontend"
        # 1. 如果是静态文件（js/css/img），直接返回
        static_file = os.path.join(FRONTEND_DIR,"pages","front", path)
        print(static_file)
        if os.path.exists(static_file) and os.path.isfile(static_file):

            return send_file(static_file)
        # 2. 非静态文件/非API，返回index.html
        print(1)
        return send_file(os.path.join(FRONTEND_DIR, "pages", "front", "index.html"))

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


# D:\\project\\blog\\blog-frontend\\front\\index.html
# D:\\project\\blog\\blog-frontend\\pages\\front\\index.html
# 生产环境无需调用app.run()，交给Waitress启动
if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000, debug=True)
