"""QThread-based workers for all async tasks in PromptGen Tool.

Each worker:
  - receives its inputs at construction time
  - emits  `finished(result)`  on success
  - emits  `error(str)`        on failure
  - emits  `progress(str)`     for status updates

Callers connect to these signals, start the worker, then clean up after
`finished` or `error` fires.
"""

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from PySide6.QtCore import QThread, Signal


# ── Base ─────────────────────────────────────────────────────────────────────

class _BaseWorker(QThread):
    finished = Signal(object)   # emits result (type varies per subclass)
    error    = Signal(str)
    progress = Signal(str)

    def _emit_error(self, exc: Exception) -> None:
        self.error.emit(str(exc))


# ── Prompt generation ────────────────────────────────────────────────────────

class PromptWorker(_BaseWorker):
    """Calls an arbitrary prompt-building function and returns the string."""

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as exc:
            self._emit_error(exc)


# ── Single image generation ──────────────────────────────────────────────────

class ImageGenWorker(_BaseWorker):
    """Generates one image via the active provider.

    finished emits: bytes  (raw image data)
    """

    def __init__(self, generate_fn, prompt: str,
                 reference_images=None, text_last: bool = False):
        super().__init__()
        self._fn = generate_fn
        self._prompt = prompt
        self._refs = reference_images
        self._text_last = text_last

    def run(self):
        try:
            data = self._fn(self._prompt,
                            reference_images=self._refs,
                            text_last=self._text_last)
            self.finished.emit(data)
        except Exception as exc:
            self._emit_error(exc)


# ── Batch (concurrent) image generation ─────────────────────────────────────

class BatchImageGenWorker(_BaseWorker):
    """Generates *n* images concurrently.

    progress emits: "done_count/total" strings
    finished emits: list[bytes | Exception]  (one entry per image)
    """

    image_ready = Signal(int, bytes)   # (index, data) – fires as each image arrives

    def __init__(self, generate_fn, prompt: str, count: int,
                 reference_images=None, text_last: bool = False):
        super().__init__()
        self._fn = generate_fn
        self._prompt = prompt
        self._count = count
        self._refs = reference_images
        self._text_last = text_last

    def run(self):
        results: list[Any] = [None] * self._count
        done = 0

        def _task(idx):
            return idx, self._fn(self._prompt,
                                 reference_images=self._refs,
                                 text_last=self._text_last)

        with ThreadPoolExecutor(max_workers=self._count) as pool:
            futures = {pool.submit(_task, i): i for i in range(self._count)}
            for fut in as_completed(futures):
                try:
                    idx, data = fut.result()
                    results[idx] = data
                    self.image_ready.emit(idx, data)
                except Exception as exc:
                    idx = futures[fut]
                    results[idx] = exc
                finally:
                    done += 1
                    self.progress.emit(f"{done}/{self._count}")

        self.finished.emit(results)


# ── Image editing ────────────────────────────────────────────────────────────

class ImageEditWorker(_BaseWorker):
    """Edits an existing image via the active provider.

    finished emits: bytes
    """

    def __init__(self, edit_fn, prompt: str,
                 image_bytes: bytes, image_mime: str):
        super().__init__()
        self._fn = edit_fn
        self._prompt = prompt
        self._image_bytes = image_bytes
        self._image_mime = image_mime

    def run(self):
        try:
            data = self._fn(self._prompt, self._image_bytes, self._image_mime)
            self.finished.emit(data)
        except Exception as exc:
            self._emit_error(exc)


# ── Item prompt + translation ────────────────────────────────────────────────

class ItemPromptWorker(_BaseWorker):
    """Reads a CSV, builds a prompt, optionally translates.

    finished emits: str (the prompt)
    """

    def __init__(self, csv_path: str, translate: bool, cache: bool):
        super().__init__()
        self._csv = csv_path
        self._translate = translate
        self._cache = cache

    def run(self):
        import item_generator as ig
        try:
            items = ig.read_items_from_csv(self._csv)
            if not items:
                self.error.emit("Could not read items from CSV.")
                return
            cache_path = self._csv if self._cache else None
            prompt = ig.generate_icon_grid_prompt(
                items, translate=self._translate, cache_path=cache_path)
            self.finished.emit(prompt)
        except Exception as exc:
            self._emit_error(exc)


# ── Image slicer ─────────────────────────────────────────────────────────────

class SlicerWorker(_BaseWorker):
    """Slices one or more grid images.

    progress emits: human-readable status string
    finished emits: dict {"success": int, "errors": list[str]}
    """

    def __init__(self, files: list[str], rows: int, cols: int,
                 out_dir: str | None, csv_path: str | None,
                 translate: bool, remove_bg: bool, cache: bool,
                 normalize: bool, scale: float,
                 rename: str, auto_suffix: bool, smart_crop: bool):
        super().__init__()
        self.files = files
        self.rows = rows
        self.cols = cols
        self.out_dir = out_dir
        self.csv_path = csv_path
        self.translate = translate
        self.remove_bg = remove_bg
        self.cache = cache
        self.normalize = normalize
        self.scale = scale
        self.rename = rename
        self.auto_suffix = auto_suffix
        self.smart_crop = smart_crop

    def run(self):
        import slicer_tool as st
        import uuid as _uuid

        total = len(self.files)
        cells = self.rows * self.cols
        num_digits = max(2, len(str(cells)), len(str(total)))
        batch_id = _uuid.uuid4().hex if total > 1 else None

        success_count = 0
        errors = []
        current_index = 1

        for i, fp in enumerate(self.files):
            import os
            self.progress.emit(
                f"Processing ({i+1}/{total}): {os.path.basename(fp)}…")

            row_cuts = col_cuts = None
            if self.smart_crop:
                try:
                    self.progress.emit(
                        f"Detecting grid ({i+1}/{total}): {os.path.basename(fp)}…")
                    row_cuts, col_cuts = st.detect_grid(fp)
                except Exception as e:
                    pass  # fall back to manual grid

            try:
                success, msg, count = st.slice_image(
                    image_path=fp,
                    grid_rows=self.rows,
                    grid_cols=self.cols,
                    output_dir=self.out_dir,
                    csv_path=self.csv_path,
                    translate_mode=self.translate,
                    remove_bg=self.remove_bg,
                    cache_mode=self.cache,
                    normalize_mode=self.normalize,
                    scale_factor=self.scale,
                    rename_prefix=self.rename or None,
                    start_index=current_index,
                    num_digits=num_digits,
                    auto_suffix=self.auto_suffix,
                    batch_id=batch_id,
                    row_cuts=row_cuts,
                    col_cuts=col_cuts,
                )
                if success:
                    success_count += 1
                    current_index += count
                else:
                    errors.append(f"{os.path.basename(fp)}: {msg}")
            except Exception as exc:
                errors.append(f"{os.path.basename(fp)}: {exc}")

        self.finished.emit({"success": success_count, "errors": errors})


# ── Gemini image edit (library) ───────────────────────────────────────────────

class GeminiEditWorker(_BaseWorker):
    """Edit an image using Gemini and return bytes.

    finished emits: bytes
    """

    def __init__(self, prompt: str, image_path: str, api_key: str, model: str):
        super().__init__()
        self._prompt = prompt
        self._image_path = image_path
        self._api_key = api_key
        self._model = model

    def run(self):
        import gemini_service as gs
        import mimetypes
        try:
            mime = mimetypes.guess_type(self._image_path)[0] or "image/png"
            with open(self._image_path, "rb") as f:
                img_bytes = f.read()
            result = gs.edit_image_bytes(
                self._prompt, img_bytes, mime,
                api_key=self._api_key, model=self._model)
            self.finished.emit(result)
        except Exception as exc:
            self._emit_error(exc)
