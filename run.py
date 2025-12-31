# 第一步 获取当前主地址
from utils.logger import *
import os
from pathlib import Path
import click
import yaml


def deep_merge(default: dict, custom: dict) -> dict:
    """
    深度合并两个字典：
    - 自定义配置（custom）覆盖默认配置（default）的同名键；
    - 嵌套字典逐层合并，而非整体替换；
    - 非字典类型直接覆盖，字典类型递归合并。
    """
    merged = default.copy()  # 先复制默认配置（避免修改原字典）
    for key, value in custom.items():
        # 如果自定义值是字典，且默认配置中该键也是字典 → 递归合并
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = deep_merge(merged[key], value)
        # 否则直接覆盖（非字典类型/默认配置无此键）
        else:
            merged[key] = value
    return merged


# 加载启动配置
def init_config_logger(workspace: str = ".") -> dict:
    workspace_path = Path(workspace).absolute()  # 工作目录（文件夹）
    config_path = workspace_path / "launch.yaml"  # 配置文件（文件）
    default_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 8000,
            "reload": True,
            "workers": 1
        },
        "log": {
            # 日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL
            "level": "DEBUG",
            "path": str(workspace_path / "logs"),  # 日志文件存工作目录下的 logs 子目录
            "use_json": False,
            "backup_count": 15,
            "max_bytes": 20 * 1024 * 1024,
        },
        "dependencies": {
            "check_db": True
        },
        "waitress": {
            "host": "0.0.0.0",
            "port": 8000,
            "threads": 8,
            "connection_limit": 1000,
            "access_log_path": f"{workspace}/waitress/waitress_access.log",
            "error_log_path": f"{workspace}/waitress/waitress_error.log",
        },
        "process_pool": {
            "wsgi_process_num": 1,
            "check_interval": 5,
            "resource_warning_cpu": 80,  # CPU告警阈值
            "resource_warning_mem": 90,  # 内存告警阈值
        }
    }

    def load_logger(init_logger, log_config):
        init_logger(
            level=log_config.get("level", "DEBUG"),
            log_dir=log_config.get("path", str(workspace_path / "logs")),
            use_json=log_config.get("use_json", False),
            backup_count=log_config.get("backup_count", 15),
            max_bytes=log_config.get("max_bytes", 20 * 1024 * 1024)
        )
        logInfo(f"初始化日志，级别：{log_config.get("level")}，路径：{log_config.get("path")}")
        logInfo("✅ 成功加载日志功能")

    try:
        # 3. 配置文件存在 → 读取配置
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}  # 空文件返回空字典，避免 None
            # 合并默认配置（防止配置文件缺失关键字段）
            config = deep_merge(default_config, config)
            load_logger(init_logger, config.get("log", {}))
            logInfo(f"✅ 成功加载配置文件：{config_path}")

        # 4. 配置文件不存在 → 创建目录 + 生成默认配置
        else:
            # 先创建工作目录（含父目录，已存在不报错）
            workspace_path.mkdir(parents=True, exist_ok=True)
            # 写入默认配置文件（UTF-8 编码，缩进4格，支持中文）
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    default_config,
                    f,
                    indent=4,
                    allow_unicode=True,
                    sort_keys=False  # 保持配置顺序，更易读
                )
            config = default_config
            load_logger(init_logger, config.get("log", {}))
            logInfo(f"⚠️  配置文件不存在，已创建默认配置：{config_path}")

        return config

    # 5. 异常处理：覆盖文件读取/解析错误
    except yaml.YAMLError as e:
        raise ValueError(f"配置文件格式错误（YAML 解析失败）：{config_path} → {str(e)}")
    except PermissionError:
        raise PermissionError(f"无权限访问配置文件/目录：{config_path}（检查读写权限）")
    except Exception as e:
        print(f"❌ 加载配置/初始化日志失败：{str(e)}")
        raise RuntimeError(f"加载配置失败：{str(e)}")


@click.command()
@click.option(
    "--workspace",
    default=".",
    help="指定工作目录（存放配置文件和程序生成文件），默认：当前文件夹"
)
def start(workspace: str):
    # 加载启动配置
    CONFIG = init_config_logger(workspace)
    logInfo(f"🚀 启动配置加载完成，工作目录：{Path(workspace).absolute()}")
    logInfo(f"📌 服务配置 - host: {CONFIG['server']['host']}, port: {CONFIG['server']['port']}")
    logInfo("开始启动后端主进程")

    # Windows必须用spawn启动方式
    multiprocessing.set_start_method("spawn", force=True)

    # 初始化管理器（传递配置）
    manager = WSGIProcessManager(CONFIG)
    # 注册退出信号
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)

    # 启动服务
    try:
        manager.start_pool()
    except Exception as e:
        logError(f"❌ 服务启动失败：{e}")
        manager.stop_all()
        sys.exit(1)
    while 1:
        time.sleep(1)


import os
import sys
import signal
import time
import multiprocessing
import psutil
from typing import List

# 强制将项目根目录加入Python路径（优先级最高）
sys.path.insert(0, os.path.abspath(os.getcwd()))


def run_waitress(config: dict):
    try:
        # 修正导入：只导入需要的函数，去掉无用的get_logger（如果没用到）
        from utils.logger import init_logger, logInfo, logError

        # 子进程重新初始化日志
        init_logger(
            level=config["log"]["level"],
            log_dir=config["log"]["path"],
            use_json=config["log"]["use_json"],
            backup_count=config["log"]["backup_count"],
            max_bytes=config["log"]["max_bytes"]
        )

        waitress_config = config["waitress"]
        from app.app import create_app
        app = create_app()
        logInfo(f"✅ 成功导入Flask应用：{app}")

        # 若需要waitress专属logger，用get_logger（现在已补全）
        access_logger = get_logger('waitress.access')
        error_logger = get_logger('waitress')

        from waitress import serve
        logInfo(f"🚀 启动Waitress服务：http://{waitress_config['host']}:{waitress_config['port']}")
        serve(
            app,
            host=waitress_config["host"],
            port=waitress_config["port"],
            threads=waitress_config["threads"],
            connection_limit=waitress_config["connection_limit"],
            log_socket_errors=True
        )
    except Exception as e:
        logError(f"❌ Waitress启动失败：{e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
# ===================== 进程管理器 =====================
class WSGIProcessManager:
    def __init__(self, config: dict):
        self.config = config  # 保存配置
        self.wsgi_processes: List[multiprocessing.Process] = []
        self.is_running = False
        # 提取进程池配置（避免硬编码）
        self.process_pool_config = config["process_pool"]
        self.waitress_config = config["waitress"]

    def start_waitress_process(self) -> multiprocessing.Process:
        """启动Waitress子进程（传递配置参数）"""
        process = multiprocessing.Process(
            name="Waitress-Server",
            target=run_waitress,
            args=(self.config,),  # 将配置作为参数传递给子进程
            daemon=False
        )
        process.start()
        logInfo(f"✅ Waitress进程启动成功，PID: {process.pid}")
        return process

    def start_pool(self):
        self.is_running = True
        # 启动Waitress进程
        for _ in range(self.process_pool_config["wsgi_process_num"]):
            process = self.start_waitress_process()
            self.wsgi_processes.append(process)
        # 启动监控
        self._monitor_processes()

    def _monitor_processes(self):
        logInfo(f"🔍 启动进程监控，检查间隔：{self.process_pool_config['check_interval']}秒")
        while self.is_running:
            for i, process in enumerate(self.wsgi_processes):
                if not process.is_alive():
                    exitcode = process.exitcode
                    logInfo(f"⚠️ Waitress进程（PID:{process.pid}）退出，退出码：{exitcode}")
                    process.join()
                    time.sleep(2)
                    new_process = self.start_waitress_process()
                    self.wsgi_processes[i] = new_process
                else:
                    # 监控资源占用
                    try:
                        p = psutil.Process(process.pid)
                        cpu = p.cpu_percent(interval=0.1)
                        mem = p.memory_percent()
                        if cpu > self.config["process_pool"]["resource_warning_cpu"] or mem > self.config["process_pool"]["resource_warning_mem"]:
                            logDebug(f"⚠️ Waitress进程（PID:{process.pid}）资源过高：CPU {cpu}%，内存 {mem}%")
                    except psutil.NoSuchProcess:
                        pass
            time.sleep(self.process_pool_config["check_interval"])

    def stop_all(self):
        self.is_running = False
        logInfo("\n🛑 开始停止所有Waitress进程...")
        for process in self.wsgi_processes:
            if process.is_alive():
                try:
                    process.terminate()
                    process.join(timeout=5)
                    if process.is_alive():
                        process.kill()
                    logDebug(f"✅ Waitress进程（PID:{process.pid}）已停止")
                except Exception as e:
                    logDebug(f"❌ 停止进程失败：{e}")
        self.wsgi_processes.clear()
        logInfo("✅ 所有进程已停止")
        print("bye")

    def signal_handler(self, sig, frame):
        logDebug(f"\n📢 捕获退出信号：{sig}")
        self.stop_all()
        sys.exit(0)


if __name__ == "__main__":
    start()
