"""Generator 公共工具：option pair 处理、标签映射、本地化文本、配置读取。

character_generator 和 clothing_generator 历史上各自实现了一份完全相同的辅助函数；
此模块为唯一来源。两个 generator 应 `from . import _options_shared as _shared` 使用。

行为约束：所有函数必须与原 character_generator 中的同名函数 byte-for-byte 等价。
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple


def make_options(pairs: List[tuple], lang: str) -> List[str]:
    """根据 lang 返回展示给用户的标签列表（en 或 zh）。"""
    use_zh = lang == "zh"
    return [zh if use_zh else en for en, zh in pairs]


def make_option_map(pairs: List[tuple], lang: str) -> Dict[str, str]:
    """label -> 英文 value（用于把 UI 选中项还原为 prompt 用的英文值）。"""
    use_zh = lang == "zh"
    return {(zh if use_zh else en): en for en, zh in pairs}


def make_label_map(pairs: List[tuple], lang: str) -> Dict[str, str]:
    """英文 value -> 当前语言下的 label。"""
    use_zh = lang == "zh"
    return {en: (zh if use_zh else en) for en, zh in pairs}


def label_to_value(label: str, mapping: Dict[str, str]) -> str:
    return mapping.get(label, label)


def labels_to_values(labels: List[str], mapping: Dict[str, str]) -> List[str]:
    return [mapping.get(label, label) for label in labels]


def localize_text(value, lang: str) -> str:
    """value 可能是 str，也可能是 {"en": ..., "zh": ...}。"""
    if isinstance(value, dict):
        primary = value.get(lang)
        fallback = value.get("zh") if lang == "en" else value.get("en")
        return str(primary or fallback or "").strip()
    return str(value).strip()


def load_options_config(path: str) -> Dict[str, List]:
    """读取 *_options.json，失败时返回空 dict（让调用方走默认 pairs）。"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def get_option_pairs(
    config: Dict[str, List], key: str, default_pairs: List[tuple]
) -> List[tuple]:
    """从 options.json 配置里取出 [(en, zh), ...] 列表；条目缺失则用 default_pairs。"""
    raw_items = config.get(key)
    if not isinstance(raw_items, list):
        return default_pairs
    pairs: List[Tuple[str, str]] = []
    for item in raw_items:
        en = zh = None
        if isinstance(item, (list, tuple)) and len(item) == 2:
            en, zh = item
        elif isinstance(item, dict):
            en = item.get("en")
            zh = item.get("zh")
        if en is None or zh is None:
            continue
        en = str(en).strip()
        zh = str(zh).strip()
        if en and zh:
            pairs.append((en, zh))
    return pairs if pairs else default_pairs
