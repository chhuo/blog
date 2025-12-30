from app.infrastructure.http.server import start_flask_server

if __name__ == "__main__":
    print("博客项目启动中...")  # 此时已使用自定义print
    start_flask_server()

    # app.run(debug=True)
