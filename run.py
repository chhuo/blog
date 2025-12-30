# run.py
# from app import create_app

# 第一步：加载并替换print（必须在应用初始化前执行）
from app.infrastructure.utils.print_utils import custom_print

# app = create_app()

if __name__ == "__main__":
    print("博客项目启动中...")  # 此时已使用自定义print
    # app.run(debug=True)
