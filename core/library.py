"""作品库：sqlite-backed 持久化层。

数据存于 %APPDATA%/PromptGen/library.db。本模块只关心存取，不耦合任何 UI。
图片本体仍写到原 outputs 目录，库里只记录路径 + 元数据。

Schema (assets 表):
    id              INTEGER PRIMARY KEY
    created_at      TEXT (ISO 8601 UTC, 排序键)
    generator_type  TEXT  ('spaceship'|'character'|'clothing'|'item'|'slicer'|'edit'|...)
    params_json     TEXT  (生成时所用参数的 JSON 序列化，便于"重抽")
    prompt          TEXT  (实际发给 Gemini 的 prompt 文本)
    image_path      TEXT  (绝对或相对路径；条目可指向已被删除的文件，library 不强制存在性)
    thumbnail_path  TEXT  (可空：未来缩略图缓存)
    rating          INTEGER (0-5，0 表示未评级)
    tags            TEXT  (逗号分隔)
    source_batch_id TEXT  (并发出图 / 切片产物的同批 UUID，可空)
    notes           TEXT  (用户备注)

设计要点：
- add_entry 是 fire-and-forget：插入失败只 log warning，不向上抛异常打断主流程
- list_entries 默认按 created_at DESC，支持 generator_type / rating>= / tag / 关键字过滤
- 模块级 _conn() 懒加载，多线程安全（sqlite3 默认 check_same_thread=True；这里用
  check_same_thread=False + 串行化的 _LOCK 保证写入安全）
"""
from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .logging_setup import get_logger

_log = get_logger(__name__)
_LOCK = threading.RLock()
_CONN: Optional[sqlite3.Connection] = None
_DB_PATH: Optional[str] = None


_SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL,
    generator_type  TEXT    NOT NULL,
    params_json     TEXT    NOT NULL DEFAULT '{}',
    prompt          TEXT    NOT NULL DEFAULT '',
    image_path      TEXT    NOT NULL DEFAULT '',
    thumbnail_path  TEXT,
    rating          INTEGER NOT NULL DEFAULT 0,
    tags            TEXT    NOT NULL DEFAULT '',
    source_batch_id TEXT,
    notes           TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_assets_created_at ON assets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assets_generator_type ON assets(generator_type);
CREATE INDEX IF NOT EXISTS idx_assets_rating ON assets(rating);
CREATE INDEX IF NOT EXISTS idx_assets_batch ON assets(source_batch_id);
"""


@dataclass
class AssetEntry:
    id: int
    created_at: str
    generator_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    prompt: str = ""
    image_path: str = ""
    thumbnail_path: Optional[str] = None
    rating: int = 0
    tags: List[str] = field(default_factory=list)
    source_batch_id: Optional[str] = None
    notes: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "AssetEntry":
        try:
            params = json.loads(row["params_json"]) if row["params_json"] else {}
        except (json.JSONDecodeError, TypeError):
            params = {}
        tags_raw = row["tags"] or ""
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        return cls(
            id=row["id"],
            created_at=row["created_at"],
            generator_type=row["generator_type"],
            params=params,
            prompt=row["prompt"] or "",
            image_path=row["image_path"] or "",
            thumbnail_path=row["thumbnail_path"],
            rating=row["rating"] or 0,
            tags=tags,
            source_batch_id=row["source_batch_id"],
            notes=row["notes"] or "",
        )


def _resolve_db_path() -> str:
    from paths import user_data_path
    return user_data_path("library.db")


def _open(db_path: Optional[str] = None) -> sqlite3.Connection:
    """初始化连接 + schema。db_path 显式传入会切换 / 重开。

    无参数调用 = 使用当前已配置的 path（测试通过 configure 切换后会保留），
    若从未配置则用 paths.user_data_path('library.db')。
    """
    global _CONN, _DB_PATH
    if db_path is None:
        if _CONN is not None and _DB_PATH is not None:
            return _CONN
        db_path = _resolve_db_path()
    if _CONN is not None and _DB_PATH == db_path:
        return _CONN
    if _CONN is not None:
        try:
            _CONN.close()
        except sqlite3.Error:
            pass
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    _CONN = conn
    _DB_PATH = db_path
    return conn


def configure(db_path: str) -> None:
    """切换到指定 db 路径（测试 / 自定义存储位置用）。

    会重开连接，丢弃任何缓存的 conn。"""
    with _LOCK:
        _open(db_path)


def reset_for_test() -> None:
    """测试 tearDown 调用，清掉模块级状态以避免连接泄漏到下个 case。"""
    global _CONN, _DB_PATH
    with _LOCK:
        if _CONN is not None:
            try:
                _CONN.close()
            except sqlite3.Error:
                pass
        _CONN = None
        _DB_PATH = None


def get_db_path() -> str:
    with _LOCK:
        _open()
        assert _DB_PATH is not None
        return _DB_PATH


def add_entry(
    *,
    generator_type: str,
    params: Optional[Dict[str, Any]] = None,
    prompt: str = "",
    image_path: str = "",
    thumbnail_path: Optional[str] = None,
    source_batch_id: Optional[str] = None,
    rating: int = 0,
    tags: Optional[List[str]] = None,
    notes: str = "",
) -> Optional[int]:
    """插入一条记录，返回 rowid。失败时返回 None 并记 warning（不抛）。"""
    try:
        with _LOCK:
            conn = _open()
            cur = conn.execute(
                """
                INSERT INTO assets (
                    created_at, generator_type, params_json, prompt,
                    image_path, thumbnail_path, rating, tags,
                    source_batch_id, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    generator_type,
                    json.dumps(params or {}, ensure_ascii=False),
                    prompt,
                    image_path,
                    thumbnail_path,
                    int(rating),
                    ",".join(tags or []),
                    source_batch_id,
                    notes,
                ),
            )
            conn.commit()
            return cur.lastrowid
    except sqlite3.Error as e:
        _log.warning("library.add_entry failed: %s", e)
        return None


def list_entries(
    *,
    generator_type: Optional[str] = None,
    min_rating: int = 0,
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> List[AssetEntry]:
    """按 created_at DESC 列出条目，应用过滤。"""
    sql = "SELECT * FROM assets WHERE 1=1"
    args: List[Any] = []
    if generator_type:
        sql += " AND generator_type = ?"
        args.append(generator_type)
    if min_rating > 0:
        sql += " AND rating >= ?"
        args.append(int(min_rating))
    if tag:
        # 简单 LIKE 匹配 tags 字段（逗号分隔），足够当前规模使用
        sql += " AND ',' || tags || ',' LIKE ?"
        args.append(f"%,{tag},%")
    if keyword:
        sql += " AND (prompt LIKE ? OR notes LIKE ? OR tags LIKE ?)"
        kw = f"%{keyword}%"
        args.extend([kw, kw, kw])
    sql += " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
    args.extend([int(limit), int(offset)])

    with _LOCK:
        conn = _open()
        try:
            rows = conn.execute(sql, args).fetchall()
        except sqlite3.Error as e:
            _log.warning("library.list_entries failed: %s", e)
            return []
    return [AssetEntry.from_row(r) for r in rows]


def get_entry(entry_id: int) -> Optional[AssetEntry]:
    with _LOCK:
        conn = _open()
        try:
            row = conn.execute("SELECT * FROM assets WHERE id = ?", (entry_id,)).fetchone()
        except sqlite3.Error as e:
            _log.warning("library.get_entry failed: %s", e)
            return None
    return AssetEntry.from_row(row) if row else None


def update_rating(entry_id: int, rating: int) -> bool:
    rating = max(0, min(5, int(rating)))
    return _update_field(entry_id, "rating", rating)


def update_tags(entry_id: int, tags: List[str]) -> bool:
    return _update_field(entry_id, "tags", ",".join(t.strip() for t in tags if t.strip()))


def update_notes(entry_id: int, notes: str) -> bool:
    return _update_field(entry_id, "notes", notes or "")


def _update_field(entry_id: int, column: str, value: Any) -> bool:
    try:
        with _LOCK:
            conn = _open()
            conn.execute(f"UPDATE assets SET {column} = ? WHERE id = ?", (value, entry_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        _log.warning("library update %s failed: %s", column, e)
        return False


def delete_entry(entry_id: int) -> bool:
    """只从库里删条目，不动磁盘上的图片文件。"""
    try:
        with _LOCK:
            conn = _open()
            conn.execute("DELETE FROM assets WHERE id = ?", (entry_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        _log.warning("library.delete_entry failed: %s", e)
        return False


def count(generator_type: Optional[str] = None) -> int:
    sql = "SELECT COUNT(*) FROM assets"
    args: List[Any] = []
    if generator_type:
        sql += " WHERE generator_type = ?"
        args.append(generator_type)
    with _LOCK:
        conn = _open()
        try:
            return int(conn.execute(sql, args).fetchone()[0])
        except sqlite3.Error:
            return 0


def all_tags() -> List[str]:
    """聚合所有出现过的 tag，用于 UI 自动补全。"""
    with _LOCK:
        conn = _open()
        try:
            rows = conn.execute("SELECT tags FROM assets WHERE tags <> ''").fetchall()
        except sqlite3.Error:
            return []
    seen = set()
    for r in rows:
        for t in (r["tags"] or "").split(","):
            t = t.strip()
            if t:
                seen.add(t)
    return sorted(seen)
