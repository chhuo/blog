import os
from pathlib import Path
import sys


def print_directory_structure(
        root_dir: str,
        ignore_dirs: list = None,
        max_depth: int = 5,
        ddd_core_dirs: list = None
):
    """
    打印目录结构，重点标注DDD核心目录

    Args:
        root_dir: 根目录路径
        ignore_dirs: 忽略的目录列表（如虚拟环境、缓存目录）
        max_depth: 最大递归深度（避免层级过深）
        ddd_core_dirs: DDD核心目录名称列表
    """
    # 初始化默认值
    if ignore_dirs is None:
        ignore_dirs = ['.git', '__pycache__', 'venv', 'env', '.env',
                       'node_modules', '.idea', 'vscode', '.cache','.venv']
    if ddd_core_dirs is None:
        # DDD经典目录结构（支持多种命名风格）
        ddd_core_dirs = [
            # 核心层
            'domain', 'domains', 'core',
            # 应用层
            'application', 'app', 'applications',
            # 基础设施层
            'infrastructure', 'infra',
            # 接口层
            'interfaces', 'api', 'interface',
            # 领域细分
            'entities', 'value_objects', 'aggregates', 'repositories',
            'services', 'events', 'specifications'
        ]

    # 验证根目录是否存在
    root_path = Path(root_dir).absolute()
    if not root_path.exists():
        print(f"错误：目录 {root_path} 不存在！")
        return

    print(f"\n=== 当前目录结构 (根目录: {root_path}) ===")
    print("=== DDD核心目录会标注【DDD】===\n")

    # 遍历目录
    for root, dirs, files in os.walk(root_path):
        # 计算当前深度
        rel_path = Path(root).relative_to(root_path)
        depth = len(rel_path.parts) if rel_path.parts else 0

        # 超过最大深度则停止递归
        if depth > max_depth:
            dirs[:] = []  # 清空dirs，停止向下遍历
            continue

        # 过滤忽略的目录
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        # 生成缩进
        indent = "    " * depth
        # 当前目录名称
        dir_name = os.path.basename(root) if depth > 0 else "."

        # 检查是否是DDD核心目录
        ddd_mark = " 【DDD】" if dir_name.lower() in [d.lower() for d in ddd_core_dirs] else ""

        # 打印目录
        print(f"{indent}├── {dir_name}/{ddd_mark}")

        # 打印文件（只显示.py文件，避免过多）
        for file in files:
            if file.endswith('.py'):
                file_indent = "    " * (depth + 1)
                print(f"{file_indent}├── {file}")


def main():
    # 获取当前执行目录（支持命令行参数指定目录）
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.getcwd()

    # 打印目录结构
    print_directory_structure(
        root_dir=target_dir,
        max_depth=60,  # 可根据需要调整深度
    )

    # 打印DDD架构参考说明
    print("\n=== DDD架构参考说明 ===")
    print("1. 核心层 (Domain): 包含实体、值对象、聚合根、领域服务、领域事件等")
    print("2. 应用层 (Application): 包含应用服务，协调领域层完成业务流程")
    print("3. 基础设施层 (Infrastructure): 提供技术支撑（数据库、缓存、第三方API等）")
    print("4. 接口层 (Interfaces): 对外提供接口（API、CLI、UI等）")
    print("\n如果你的目录包含以上核心目录，基本符合DDD架构规范！")


if __name__ == "__main__":
    main()