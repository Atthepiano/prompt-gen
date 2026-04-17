"""向后兼容 shim：真实实现已搬到 core.item_generator。"""
from core.item_generator import *  # noqa: F401,F403
from core.item_generator import (  # noqa: F401
    DEFAULT_CSV_PATH,
    GRID_SIZE,
    TOTAL_ITEMS,
    read_items_from_csv,
)
