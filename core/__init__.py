"""Pure-logic core for the Prompt Generator app.

UI 层（Tkinter / 未来的 Web）不应依赖 Tkinter 之外的任何东西就能用 core/。
core/ 内部只允许依赖：标准库、Pillow（图像处理）、requests、deep_translator。
不允许 import tkinter。
"""
