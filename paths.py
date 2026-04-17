"""统一资源 / 用户数据路径解析。

- resource_path(name): 只读资源（随程序分发的 JSON / CSV / 图片）。
  开发态读源码目录；PyInstaller 打包后读 sys._MEIPASS（--onedir 下与 exe 同级）。
- user_data_path(name): 可写用户数据（config、preview 配置、日志）。
  优先 %APPDATA%/PromptGen（Windows）或 ~/.promptgen，回退到资源目录（兼容旧版本）。
"""
import os
import sys


def _resource_root() -> str:
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(*parts: str) -> str:
    return os.path.join(_resource_root(), *parts)


def _user_data_root() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    root = os.path.join(base, "PromptGen") if base else os.path.join(os.path.expanduser("~"), ".promptgen")
    try:
        os.makedirs(root, exist_ok=True)
        return root
    except OSError:
        return _resource_root()


def user_data_path(*parts: str) -> str:
    return os.path.join(_user_data_root(), *parts)


def migrate_legacy_file(filename: str) -> str:
    """如果用户数据目录里没有该文件，但旧版本在资源目录留有副本，则迁移过去。
    返回最终应使用的绝对路径（始终指向用户数据目录）。"""
    target = user_data_path(filename)
    if os.path.exists(target):
        return target
    legacy = resource_path(filename)
    if os.path.exists(legacy):
        try:
            with open(legacy, "rb") as src, open(target, "wb") as dst:
                dst.write(src.read())
        except OSError:
            return legacy
    return target
