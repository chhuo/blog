from app.infrastructure.utils import get_project_abs_root_path_by_env

PROJECT_ROOT = get_project_abs_root_path_by_env()
print(f"找到当前项目绝对根目录地址：{PROJECT_ROOT}")
from .env_loader import CONFIG
