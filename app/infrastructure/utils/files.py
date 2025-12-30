import pathlib
from pathlib import Path
from typing import Union, Optional

# 全局缓存：项目根目录Path对象（仅初始化一次）
_PROJECT_ROOT: Optional[pathlib.Path] = None


def get_project_abs_root_path_by_env() -> pathlib.Path:
    """
    获取项目根目录的绝对路径（返回Path对象，全局缓存，仅首次调用回溯目录）
    核心逻辑：从当前文件所在目录向上回溯，找到包含.env文件的目录作为根目录
    :return: 项目根目录的绝对Path对象
    :raise FileNotFoundError: 未找到.env文件（无有效项目根目录）
    :raise PermissionError: 目录访问权限不足
    """
    global _PROJECT_ROOT

    # 缓存命中：直接返回已初始化的根目录
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    # 缓存未命中：向上回溯查找.env文件
    # 起始目录：当前函数所在文件（utils/files.py）的父目录
    start_dir = pathlib.Path(__file__).parent.absolute()
    current_dir = start_dir

    while True:
        # 检查当前目录是否包含.env文件
        env_file = current_dir / ".env"
        if env_file.exists() and env_file.is_file():
            _PROJECT_ROOT = current_dir.absolute()
            return _PROJECT_ROOT

        # 向上回溯一级目录
        parent_dir = current_dir.parent
        # 终止条件：到达系统根目录仍未找到
        if parent_dir == current_dir:
            raise FileNotFoundError(
                f"未找到项目根目录！从{start_dir}向上回溯至系统根目录，均未发现.env文件。\n"
                "请确认.env文件放在项目根目录下，或检查目录访问权限。"
            )

        current_dir = parent_dir


def ensure_file(
        file: Union[str, Path],
        the_way: int = 1
) -> None:
    """
    检测文件是否存在，并按指定方式处理
    :param file: 需要检测的文件路径（支持字符串/Path对象，自动转为绝对路径）
    :param the_way: 处理方式：
        1：文件不存在 → 抛出FileNotFoundError；文件存在 → 无操作
        2：文件不存在 → 创建空文件；文件存在 → 无操作（修正原逻辑：原逻辑错误删除文件）
        3：文件存在 → 删除后重建空文件；文件不存在 → 创建空文件（扩展实用场景）
    :return: None
    :raise FileNotFoundError: 方式1且文件不存在时抛出
    :raise PermissionError: 无文件/目录操作权限时抛出
    :raise IsADirectoryError: 传入路径是目录而非文件时抛出
    """
    # 统一转换为Path对象，确保绝对路径，兼容字符串输入
    file_path = Path(file).absolute()

    # 先判断路径是否是目录（避免把目录当成文件处理）
    if file_path.is_dir():
        raise IsADirectoryError(f"指定路径是目录，并非文件：{file_path}")

    # 判断文件是否存在
    file_exists = file_path.exists() and file_path.is_file()

    # 按处理方式执行逻辑
    if the_way == 1:
        # 方式1：不存在则抛错，存在则无操作
        if not file_exists:
            raise FileNotFoundError(f"文件不存在：{file_path}")

    elif the_way == 2:
        # 方式2：不存在则创建，存在则无操作（修正原逻辑的错误删除）
        if not file_exists:
            # 先确保父目录存在（避免创建文件时因目录不存在报错）
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # 创建空文件（touch兼容所有系统）
            file_path.touch(exist_ok=True)

    elif the_way == 3:
        # 扩展方式3：强制重建（存在则删除，再创建）
        if file_exists:
            file_path.unlink()  # 删除已有文件
        # 确保父目录+创建空文件
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

    else:
        raise ValueError(f"不支持的处理方式：{the_way}，仅支持1/2/3")
