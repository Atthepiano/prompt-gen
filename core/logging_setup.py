"""统一 logging 配置入口。

设计：
- 同一进程多次 init_app_logging() 是安全的（只配置一次根 logger）。
- 控制台输出 INFO+；文件输出 DEBUG+，写到 %APPDATA%/PromptGen/app.log（轮转）。
- core/ 内部模块用 get_logger(__name__) 即可，不需要自己 basicConfig。
- 不强制调用方使用 logger；现存 print 留给逐步迁移。
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys

_INITIALIZED = False
_LOG_FILE_PATH: str | None = None


def _resolve_log_path() -> str:
    try:
        from paths import user_data_path
        return user_data_path("app.log")
    except Exception:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app.log")


def init_app_logging(level: int = logging.INFO) -> str:
    """配置根 logger。返回日志文件实际路径，便于在 UI 中告知用户。"""
    global _INITIALIZED, _LOG_FILE_PATH
    if _INITIALIZED and _LOG_FILE_PATH:
        return _LOG_FILE_PATH

    log_path = _resolve_log_path()
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except OSError:
        pass

    _INITIALIZED = True
    _LOG_FILE_PATH = log_path
    return log_path


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
