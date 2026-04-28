import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor, as_completed
import prompt_generator as pg
import item_generator as ig
import character_generator as cg
import clothing_generator as clg
import mecha_generator as mg
import mecha_part_generator as mpg
import ship_generator as sg
import gemini_service as gs
import core.openai_service as oi
import slicer_tool as st
import curation_tool as ct
import json
import os
import mimetypes
import threading
import io
import time
from typing import List
from paths import migrate_legacy_file

APP_CONFIG_PATH = migrate_legacy_file("config.json")
HAIR_PREVIEW_CONFIG_PATH = migrate_legacy_file("hair_previews.json")

UI_TEXTS_ZH = {
    "Spaceship Prompt Generator": "飞船提示词生成器",
    "Spaceship Components": "飞船组件",
    "Mecha": "机甲",
    "Mecha Components": "机甲组件",
    "Spaceship": "飞船",
    "Item Icons": "物品图标",
    "Character Prompts": "角色提示词",
    "Clothing Presets": "服装预设",
    "Image Slicer": "图片切分",
    "Asset Curation": "资产整理",
    "Asset Library": "作品库",
    "Type:": "类型：",
    "Min ★:": "最低评级：",
    "Search:": "搜索：",
    "Refresh": "刷新",
    "Time": "时间",
    "Type": "类型",
    "Prompt / Notes": "Prompt / 备注",
    "Details": "详细信息",
    "Tags:": "标签：",
    "Copy Prompt": "复制 Prompt",
    "Open Folder": "打开所在目录",
    "Edit with Gemini": "用 Gemini 改图",
    "Delete Entry": "删除记录",
    "{n} entries": "共 {n} 条",
    "File no longer exists.": "文件已不存在。",
    "Confirm": "确认",
    "Delete this library entry? (image file is kept on disk)": "删除此条记录？（磁盘上的图片文件保留）",
    "Info": "提示",
    "Settings": "设置",
    "Generated Output / Logs:": "生成输出 / 日志：",
    "Copy to Clipboard": "复制到剪贴板",
    "Generate Image (Gemini)": "使用 Gemini 生成图片",
    "Image Preview": "图片预览",
    "No preview image": "暂无预览图片",
    "Save Image": "保存图片",
    "Discard Image": "丢弃图片",
    "Edit Image": "改图",
    "Undo Edit": "撤销改图",
    "Reverted to previous version. {n} more undo(s) available.": "已回退到上一版本。还可撤销 {n} 次。",
    "Reverted to original image.": "已恢复为原始图片。",
    "Concurrent Images:": "并发生成：",
    "Grid View": "网格视图",
    "Previous": "上一张",
    "Next": "下一张",
    "Save Selected": "保存当前",
    "Discard Selected": "丢弃当前",
    "Edit Prompt:": "修改提示：",
    "Apply Edit": "执行改图",
    "Cancel": "取消",
    "Ready": "就绪",
    "Component Category:": "组件类别：",
    "Subcategory:": "子类别：",
    "Structural Variant (Form Factor):": "结构变体（形态）：",
    "Tech Tier:": "科技等级：",
    "Manufacturer Preset": "制造商预设",
    "Color Override": "颜色覆盖",
    "Enable Custom Colors": "启用自定义颜色",
    "Pick Main Color": "选择主色",
    "Pick Energy/Glow Color": "选择能量/发光颜色",
    "GENERATE COMPONENT PROMPT": "生成组件提示词",
    "Mecha Prompt Generation": "机甲提示词生成",
    "Generate a 4-view bare-frame mecha reference sheet (90s OVA real-robot style).": "生成 4 视图裸机机甲参考图（90s OVA 真实系机器人风格）。",
    "Mecha Class:": "机甲机种：",
    "Mecha Variant:": "机甲变体：",
    "Mecha Designer (multi-select)": "机设师（可多选）",
    "GENERATE MECHA PROMPT": "生成机甲提示词",
    "Mecha Component Prompt Generation": "机甲组件提示词生成",
    "Generate a 4-view reference sheet for an individual piece of mecha equipment (hand weapon, shield, shoulder pod).": "生成 4 视图机甲单件装备参考图（手持武器 / 盾 / 肩部模块）。",
    "GENERATE MECHA COMPONENT PROMPT": "生成机甲组件提示词",
    "Design Controls (Auto = random / by designer)": "设计控制（自动 = 随机 / 由设计师决定）",
    "Sensor Module:": "传感器模组：",
    "Surface Treatment:": "表面处理：",
    "Shoulder Form:": "肩甲形态：",
    "Propulsion Style:": "推进系统：",
    "Paint Scheme:": "涂装格式：",
    "Spaceship Prompt Generation": "飞船提示词生成",
    "Generate a 4-view full-vessel spaceship reference sheet (90s OVA capital ship style).": "生成 4 视图整船飞船参考图（90s OVA 舰艇风格）。",
    "Ship Archetype:": "船型：",
    "Ship Variant:": "飞船变体：",
    "Ship Designer (multi-select)": "机设师 / 舰设师（可多选）",
    "GENERATE SHIP PROMPT": "生成飞船提示词",
    "Clear Selection": "清除选择",
    "Item Icon Generation": "物品图标生成",
    "Generates a prompt for a 8x8 sprite sheet (64 items) from the selected CSV.": "根据所选 CSV 生成 8x8 精灵表（64 个物品）的提示词。",
    "Select CSV...": "选择 CSV...",
    "Auto-Translate Content to English (Recommended)": "自动翻译内容到英文（推荐）",
    "Write Translation Result into CSV (Cache)": "将翻译结果写回 CSV（缓存）",
    "GENERATE ICON GRID (8x8)": "生成图标网格（8x8）",
    "Image Slicer (8x8 Grid)": "图片切分（8x8 网格）",
    "Splits an 8x8 grid image into 64 icons.": "将 8x8 网格图像切分为 64 个图标。",
    "1. Select Grid Image(s):": "1. 选择网格图像：",
    "Select Image File(s)...": "选择图像文件...",
    "No file selected": "未选择文件",
    "Advanced Configuration": "高级配置",
    "Grid Size (Row x Col):": "网格尺寸（行 x 列）：",
    "Norm Scale (0.1-1.0):": "标准化比例（0.1-1.0）：",
    "Smart Crop (auto-detect grid)": "智能裁剪（自动检测网格）",
    "(overrides row/col input)": "（覆盖行列数设置）",
    "Detecting grid...": "正在检测网格...",
    "2. Smart Naming Options:": "2. 智能命名选项：",
    "Use CSV for Filenames (Smart Naming)": "使用 CSV 生成文件名（智能命名）",
    "Auto-Translate Filenames (ZH -> EN)": "自动翻译文件名（中 -> 英）",
    "Remove Background": "移除背景",
    "Normalize Size & Position (Trim & Center 90%)": "标准化尺寸与位置（裁切并居中 90%）",
    "SLICE INTO 64 ICONS": "切分为 64 个图标",
    "2. Output Directory:": "2. 输出目录：",
    "(Leave empty: each image creates its own subfolder)": "（留空：每张图自动创建子目录）",
    "3. Naming Options:": "3. 命名选项：",
    "Rename:": "重命名：",
    "(overrides CSV naming if filled)": "（填写后覆盖 CSV 命名）",
    "Batch auto suffix (e.g. weapon_01_01, weapon_02_01)": "批处理自动后缀（如 weapon_01_01、weapon_02_01）",
    "4. Processing Options:": "4. 处理选项：",
    "Select Folder (Batch)...": "选择文件夹（批处理）...",
    "No image files found in the selected folder.": "所选文件夹中未找到图片文件。",
    "Image Slicer": "图片切分",
    "Asset Curation": "资产整理",
    "Configuration": "配置",
    "Target Folder (Output):": "目标文件夹（输出）：",
    "Browse Target...": "浏览目标...",
    "Source Folders (Inputs):": "源文件夹（输入）：",
    "+ Add Batch (Select Files)": "+ 批量添加（选文件）",
    "+ Add Folder": "+ 添加文件夹",
    "- Remove": "- 移除",
    "START SESSION": "开始整理",
    "Waiting to start...": "等待开始...",
    "Skip / Discard All": "跳过 / 全部丢弃",
    "Character Prompt Generation": "角色提示词生成",
    "Build a modular character prompt for retro sci-fi anime portraits.": "构建复古科幻动漫人像的模块化提示词。",
    "Clothing Preset Generation": "服装预设生成",
    "Build a modular clothing preset prompt for retro sci-fi outfit sheets.": "构建复古科幻服装预设图的模块化提示词。",
    "Faction & Role": "势力与角色",
    "Gender:": "男/女装：",
    "Outfit Gender:": "服装性别：",
    "Faction:": "势力：",
    "Role Archetype:": "角色类型：",
    "No faction description": "暂无势力描述",
    "Presentation & Layout": "呈现与构图",
    "View Mode:": "视图模式：",
    "Pose:": "姿势：",
    "Presentation:": "呈现方式：",
    "Swap-ready mannequin spec (future workflow)": "换装兼容人台规范（后续流程）",
    "Outfit Build": "服装构成",
    "Outfit Category:": "服装类别：",
    "Show all outfit categories": "显示全部服装类别（忽略角色限制）",
    "Silhouette:": "轮廓：",
    "Layering:": "层次结构：",
    "Material:": "材质：",
    "Palette:": "配色：",
    "Wear State:": "使用磨损：",
    "Detail Accents": "服装细节",
    "Insignia & Markings": "标识与徽记",
    "Custom notes (comma separated):": "自定义备注（逗号分隔）：",
    "Outfit Swap (Preview)": "换装预览（占位）",
    "Character Image:": "角色图：",
    "Clothing Preset Image:": "服装预设图：",
    "Select Character Image...": "选择角色图...",
    "Select Clothing Image...": "选择服装图...",
    "No image selected": "未选择图片",
    "Output Name:": "输出名称：",
    "Run Outfit Swap (Gemini)": "执行换装（Gemini）",
    "Select character and clothing images first.": "请先选择角色图与服装图。",
    "Core Descriptors": "基础",
    "Gender:": "性别：",
    "Age:": "年龄：",
    "Profession:": "职业：",
    "Custom Profession:": "自定义职业：",
    "Composition": "构图",
    "Framing:": "画幅范围：",
    "Aspect Ratio:": "画幅比例：",
    "Expression & Gaze": "表情与视线",
    "Expression:": "表情：",
    "Gaze:": "视线：",
    "Base Visuals": "基础视觉",
    "Body Type:": "体型：",
    "Skin Tone:": "肤色：",
    "Hair Style:": "发型：",
    "Hair Color:": "发色：",
    "Hair Color Advanced Mode": "发色高级模式",
    "Hair Colors:": "发色配色：",
    "Add Hair Color": "添加发色",
    "Clear Hair Colors": "清空发色",
    "Bangs Presence:": "刘海：",
    "Bangs Style:": "刘海类型：",
    "Hair Style Preview:": "发型预览：",
    "Set Preview Image": "设置预览图",
    "Clear Preview": "清除预览",
    "Only show hair styles for current gender": "仅显示当前性别发型",
    "Hair Preview Settings": "发型预览设置",
    "Select Hair Style:": "选择发型：",
    "Face Shape:": "脸型：",
    "Eye Size:": "眼睛大小：",
    "Nose Size:": "鼻型/大小：",
    "Mouth Shape:": "嘴型：",
    "Cheek Fullness:": "颧/脸颊：",
    "Jaw Width:": "下颌宽度：",
    "Eye Color:": "眼睛颜色：",
    "Outfit Palette:": "服装配色：",
    "Material Finish:": "材质质感：",
    "Hair": "发型",
    "Face": "面部",
    "Outfit": "服装",
    "Misc": "杂项",
    "Outfit Type:": "服装类型：",
    "Outfit Colors:": "服装配色：",
    "Add Color": "添加颜色",
    "Clear Colors": "清空配色",
    "Max hair colors reached": "已达到最多 3 个发色",
    "Max colors reached": "已达到最多 5 个颜色",
    "Face Features": "面部特征",
    "Apparel Details": "服装细节",
    "Accessories": "配饰",
    "Misc Details": "杂项细节",
    "Artist Styles": "艺术家风格",
    "Style Reference (Optional)": "画风参考（可选）",
    "Style Reference Only Mode": "仅参考图风格模式",
    "Use style reference only (remove style text from prompt)": "仅参考图风格（从提示词移除画风相关内容）",
    "Select Style Image...": "选择画风参考图...",
    "Clear Style Image": "清除画风参考图",
    "No style image selected": "未选择画风参考图",
    "Style image selected: {name}": "已选择画风参考图：{name}",
    "Style images selected: {count}": "已选择画风参考图：{count} 张",
    "Failed to read style image.": "读取画风参考图失败。",
    "Custom misc (comma separated):": "自定义杂项（逗号分隔）：",
    "Custom gear/tech (comma separated):": "自定义配饰/科技（逗号分隔）：",
    "Extra modifiers (optional):": "额外修饰（可选）：",
    "GENERATE CHARACTER PROMPT": "生成角色提示词",
    "Settings Panel": "设置面板",
    "API Provider:": "API 提供商：",
    "Gemini": "Gemini",
    "OpenAI": "OpenAI",
    "Gemini API Key:": "Gemini API Key：",
    "Gemini Model:": "Gemini 模型：",
    "OpenAI API Key:": "OpenAI API Key：",
    "OpenAI Base URL:": "OpenAI 接口地址（Base URL）：",
    "OpenAI Model:": "OpenAI 模型：",
    "Image Size:": "图像尺寸：",
    "Image Quality:": "图像质量：",
    "Image Save Directory:": "图片保存目录：",
    "Browse...": "浏览...",
    "UI Language:": "界面语言：",
    "Save Settings": "保存设置",
    "English": "English",
    "Chinese": "中文",
    "Copied": "已复制",
    "Prompt copied to clipboard!": "提示词已复制到剪贴板！",
    "Error": "错误",
    "Please select all options.": "请先选择所有选项。",
    "Generating Prompt and Translating... (This may take a moment)": "正在生成提示词并翻译...（请稍候）",
    "Prompt Generated Successfully": "提示词生成成功",
    "Error Occurred": "发生错误",
    "Slicing Images... (Batch Processing)": "正在切分图片...（批处理）",
    "Batch Complete": "批处理完成",
    "Batch Results": "批处理结果",
    "Session Started": "会话已开始",
    "Scan Complete.\nTotal Files: {total}\nAuto-Resolved (Unique): {auto}\nConflicts to Review: {conflicts}": "扫描完成。\n文件总数：{total}\n自动处理（唯一）：{auto}\n待处理冲突：{conflicts}",
    "Session Complete! All items resolved.": "会话完成！已解决所有条目。",
    "Select Target Folder": "选择目标文件夹",
    "Select Source Folder": "选择源文件夹",
    "Select ANY file inside the source folder(s) - Ctrl+Click to select multiple folders": "选择任意源文件夹内的文件（可按 Ctrl 多选文件夹）",
    "Select Sprite Sheets": "选择精灵表",
    "Select Naming CSV": "选择命名 CSV",
    "Select Item CSV": "选择物品 CSV",
    "Copied": "已复制",
    "Processing...": "处理中...",
    "Generating Image...": "正在生成图片...",
    "Image saved: {path}": "图片已保存：{path}",
    "Image ready. Use Save/Discard.": "图片已生成，请选择保存或丢弃。",
    "Editing Image...": "正在改图...",
    "No image to edit.": "没有可改的图片。",
    "Image discarded.": "图片已丢弃。",
    "Image saved to {path}": "图片已保存到：{path}",
    "Gemini API key is missing.": "缺少 Gemini API Key。",
    "API key is missing. Please add your key in Settings.": "缺少 API Key，请在设置中填写。",
    "No prompt content to send.": "没有可发送的提示词内容。",
    "Settings saved. Restart the app to apply language changes.": "设置已保存。请重启应用以应用语言变更。",
    "Settings saved.": "设置已保存。",
    "Please add at least one source folder.": "请至少添加一个源文件夹。",
    "Please select a target folder.": "请选择目标文件夹。",
    "Failed to copy file.": "复制文件失败。",
    "Could not read items from CSV.": "无法从 CSV 读取物品。",
    "{count} files selected": "已选择 {count} 个文件",
    "Failed to save settings.": "保存设置失败。",
    "Per-Tab Output Directories": "按页签设置输出目录",
    "Spaceship Dir:": "飞船组件目录：",
    "Item Icons Dir:": "物品图标目录：",
    "Character Dir:": "角色目录：",
    "Clothing Dir:": "服装目录：",
    "Default (use global dir)": "默认（使用全局目录）",
    "Processed {success}/{total} files successfully.": "成功处理 {success}/{total} 个文件。",
    "Errors:": "错误：",
    "[Setup Required]": "【需要设置】",
    "CSV Detected: {path}": "检测到 CSV：{path}",
    "Error: CSV not found at {path}": "错误：未找到 CSV：{path}",
    "Error loading image": "加载图片出错",
}

class _ComboboxTooltip:
    """Lightweight tooltip that shows a hint string for the currently-selected
    item of a Combobox. Hovering over the combobox for ~500ms pops the tooltip;
    leaving the widget or changing selection hides it.

    Usage:
        tip = _ComboboxTooltip(combobox, hint_lookup)
        # hint_lookup: callable(label_str) -> hint_str
        # When the user changes selection or hovers, the tooltip text is the
        # result of calling hint_lookup(combobox.get()).
    """
    DELAY_MS = 500
    OFFSET_X = 14
    OFFSET_Y = 18
    MAX_WIDTH = 380

    def __init__(self, widget, hint_lookup):
        self.widget = widget
        self.hint_lookup = hint_lookup
        self._after_id = None
        self._tipwin = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")
        widget.bind("<<ComboboxSelected>>", self._on_select, add="+")

    def _on_select(self, _e=None):
        # Briefly hide on selection change so the new value's tooltip can be
        # picked up next hover.
        self._hide()

    def _schedule(self, _e=None):
        self._cancel()
        self._after_id = self.widget.after(self.DELAY_MS, self._show)

    def _cancel(self):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        self._after_id = None
        try:
            label = self.widget.get()
        except Exception:
            return
        text = ""
        try:
            text = self.hint_lookup(label) or ""
        except Exception:
            text = ""
        if not text:
            return
        if self._tipwin:
            return
        # Position near the cursor
        x = self.widget.winfo_pointerx() + self.OFFSET_X
        y = self.widget.winfo_pointery() + self.OFFSET_Y
        # Keep within screen bounds
        try:
            sw = self.widget.winfo_screenwidth()
            sh = self.widget.winfo_screenheight()
            if x + self.MAX_WIDTH + 20 > sw:
                x = max(0, sw - self.MAX_WIDTH - 20)
            if y + 80 > sh:
                y = max(0, sh - 100)
        except Exception:
            pass
        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        try:
            tw.attributes("-topmost", True)
        except Exception:
            pass
        tw.wm_geometry(f"+{int(x)}+{int(y)}")
        frame = tk.Frame(tw, background="#fffbe6", borderwidth=1, relief="solid")
        frame.pack(fill="both", expand=True)
        lbl = tk.Label(
            frame,
            text=text,
            justify="left",
            background="#fffbe6",
            foreground="#222",
            font=("Microsoft YaHei", 9) if tk.TkVersion else None,
            wraplength=self.MAX_WIDTH,
            padx=8,
            pady=6,
        )
        lbl.pack()
        self._tipwin = tw

    def _hide(self, _e=None):
        self._cancel()
        if self._tipwin is not None:
            try:
                self._tipwin.destroy()
            except Exception:
                pass
            self._tipwin = None


class PromptApp:
    def __init__(self, root):
        self.root = root
        self.config = self.load_config()
        self.ui_lang = self.config.get("language", "en")
        self.root.title(self.t("Spaceship Prompt Generator"))
        self.root.geometry("980x820")

        # --- Data Setup ---
        self.component_map = pg.get_component_map()
        self.tier_list = pg.get_tier_list()
        self.manufacturer_list = ["None / Generic"] + pg.get_manufacturer_names()
        
        # --- Settings ---
        self.api_provider = self.config.get("api_provider", "Gemini")  # "Gemini" or "OpenAI"
        self.gemini_api_key = self.config.get("gemini_api_key", "")
        self.gemini_model = self.config.get("gemini_model", gs.DEFAULT_MODEL)
        self.openai_api_key = self.config.get("openai_api_key", "")
        self.openai_base_url = self.config.get("openai_base_url", oi.DEFAULT_BASE_URL)
        self.openai_model = self.config.get("openai_model", oi.DEFAULT_MODEL)
        self.openai_image_size = self.config.get("openai_image_size", "1024x1024")
        self.openai_image_quality = self.config.get("openai_image_quality", "auto")
        self.image_save_dir = self.config.get("image_save_dir", "outputs")
        self.spaceship_save_dir = self.config.get("spaceship_save_dir", "")
        self.items_save_dir = self.config.get("items_save_dir", "")
        self.character_save_dir = self.config.get("character_save_dir", "")
        self.clothing_save_dir = self.config.get("clothing_save_dir", "")
        
        # Color variables
        self.primary_color = None
        self.secondary_color = None
        
        # Slicer variables
        self.selected_image_path = None
        self.preview_image = None # Keep reference
        
        # Slicer variables
        self.selected_image_path = None
        self.preview_image = None # Keep reference

        # Style reference image (Character tab)
        self.style_ref_paths = []
        self.style_ref_blobs = []
        self.style_ref_only_mode = tk.BooleanVar(value=False)

        # Hair/Bangs preview config
        self.hair_preview_config = self.load_hair_preview_config()
        self.hair_style_previews = dict(self.hair_preview_config.get("hair_style", {}))
        self.hair_style_preview_image = None
        
        # Slicer Smart Naming
        self.slicer_csv_path = ig.DEFAULT_CSV_PATH # Default to item_test.csv
        
        # Item Prompt Variables
        self.item_csv_path = ig.DEFAULT_CSV_PATH
        self.var_cache_translation = tk.BooleanVar(value=True)
        self.var_normalize = tk.BooleanVar(value=True) # Default True for normalization logic # Unified cache option

        # --- Layout ---
        # Main Layout: Left (Controls), Right (Output)
        main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Side Container (will hold the Notebook)
        left_container = ttk.Frame(main_pane) 
        right_frame = ttk.Frame(main_pane, padding="10")
        
        main_pane.add(left_container, minsize=380)
        main_pane.add(right_frame)

        # --- Notebook (Tabs) ---
        self.notebook = ttk.Notebook(left_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Spaceship Components
        self.tab_spaceship = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_spaceship, text=self.t("Spaceship Components"))

        # Tab 1b: Mecha
        self.tab_mecha = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_mecha, text=self.t("Mecha"))

        # Tab 1b': Mecha Components (hand weapons, shields, shoulder pods)
        self.tab_mecha_part = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_mecha_part, text=self.t("Mecha Components"))

        # Tab 1c: Spaceship (full vessel)
        self.tab_ship = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_ship, text=self.t("Spaceship"))

        # Tab 2: Item Icons
        self.tab_items = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_items, text=self.t("Item Icons"))
        
        # Tab 3: Character Prompts
        self.tab_characters = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_characters, text=self.t("Character Prompts"))

        # Tab 4: Clothing Presets
        self.tab_clothing = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_clothing, text=self.t("Clothing Presets"))

        # Tab 5: Image Slicer
        self.tab_slicer = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_slicer, text=self.t("Image Slicer"))

        # Tab 6: Asset Curation
        self.tab_curation = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_curation, text=self.t("Asset Curation"))

        # Tab 7: Asset Library
        self.tab_library = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_library, text=self.t("Asset Library"))

        # Tab 8: Settings
        self.tab_settings = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_settings, text=self.t("Settings"))

        # --- Setup Tab 1: Spaceship Controls ---
        self.setup_spaceship_tab()

        # --- Setup Tab 1b: Mecha Controls ---
        self.setup_mecha_tab()

        # --- Setup Tab 1b': Mecha Components Controls ---
        self.setup_mecha_part_tab()

        # --- Setup Tab 1c: Ship Controls ---
        self.setup_ship_tab()

        # --- Setup Tab 2: Item Controls ---
        self.setup_item_tab()
        
        # --- Setup Tab 3: Character Controls ---
        self.setup_character_tab()

        # --- Setup Tab 4: Clothing Controls ---
        self.setup_clothing_tab()
        
        # --- Setup Tab 5: Slicer Controls ---
        self.setup_slicer_tab()

        # --- Setup Tab 6: Curation Controls ---
        self.curator = ct.AssetCurator()
        self.curation_queue = [] # List of filenames to process
        self.current_curation_index = 0
        self.setup_curation_tab()
        
        # --- Setup Tab 7: Asset Library ---
        self.setup_library_tab()

        # --- Setup Tab 8: Settings ---
        self.setup_settings_tab()

        # --- Output Area (Right) ---
        self.lbl_output_header = ttk.Label(right_frame, text=self.t("Generated Output / Logs:"), font=("Arial", 12, "bold"))
        self.lbl_output_header.pack(anchor="w")
        
        self.output_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10), height=7)
        self.output_text.pack(fill=tk.X, expand=False, pady=(5, 10))

        # --- Image Preview Area ---
        self.preview_header = ttk.Label(right_frame, text=self.t("Image Preview"), font=("Arial", 12, "bold"))
        self.preview_header.pack(anchor="w")

        self.preview_label = ttk.Label(right_frame, text=self.t("No preview image"), background="#eeeeee", anchor="center")
        self.preview_label.pack(fill=tk.BOTH, expand=False, pady=(5, 10))

        self.preview_grid = ttk.Frame(right_frame)
        self.preview_grid.pack(fill=tk.BOTH, expand=False, pady=(5, 10))
        self.preview_grid.pack_forget()

        preview_btn_frame = ttk.Frame(right_frame)
        preview_btn_frame.pack(fill=tk.X, pady=(0, 10))
        self.btn_save_image = ttk.Button(preview_btn_frame, text=self.t("Save Image"), command=self.save_preview_image, state=tk.DISABLED)
        self.btn_save_image.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.btn_discard_image = ttk.Button(preview_btn_frame, text=self.t("Discard Image"), command=self.discard_preview_image, state=tk.DISABLED)
        self.btn_discard_image.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        self.btn_edit_image = ttk.Button(preview_btn_frame, text=self.t("Edit Image"), command=self.open_edit_dialog, state=tk.DISABLED)
        self.btn_edit_image.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 5))
        self.btn_undo_edit = ttk.Button(preview_btn_frame, text=self.t("Undo Edit"), command=self.undo_edit_image, state=tk.DISABLED)
        self.btn_undo_edit.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 0))

        # Concurrency controls
        concurrency_frame = ttk.Frame(right_frame)
        concurrency_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(concurrency_frame, text=self.t("Concurrent Images:")).pack(side=tk.LEFT)
        self.concurrent_var = tk.StringVar(value="1")
        self.concurrent_combo = ttk.Combobox(concurrency_frame, textvariable=self.concurrent_var, state="readonly", width=5)
        self.concurrent_combo["values"] = ["1", "2", "4", "6", "8"]
        self.concurrent_combo.pack(side=tk.LEFT, padx=(6, 0))

        # Copy Button
        self.copy_btn = ttk.Button(right_frame, text=self.t("Copy to Clipboard"), command=self.copy_to_clipboard)
        self.copy_btn.pack(anchor="e")
        
        self.gen_image_btn = ttk.Button(right_frame, text=self.t("Generate Image (Gemini)"), command=self.generate_image_threaded)
        self.gen_image_btn.pack(anchor="e", pady=(5, 0))
        
        # Status Bar (Bottom of Right Frame or Main Window)
        self.status_var = tk.StringVar(value=self.t("Ready"))
        self.status_label = ttk.Label(right_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=(10,0))

        # Preview image state
        self.pending_image_bytes = None
        self.pending_image_mime = None
        self.pending_image_prefix = "gemini"
        self.pending_batch_id = None
        self.preview_photo = None
        self.pending_images = []
        self.preview_thumbnails = []
        self.active_preview_index = 0
        self.edit_undo_stack = []

    def t(self, text: str) -> str:
        if self.ui_lang == "zh":
            return UI_TEXTS_ZH.get(text, text)
        return text

    def load_config(self) -> dict:
        if os.path.exists(APP_CONFIG_PATH):
            try:
                with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(self, data: dict) -> bool:
        try:
            with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load_hair_preview_config(self) -> dict:
        if os.path.exists(HAIR_PREVIEW_CONFIG_PATH):
            try:
                with open(HAIR_PREVIEW_CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    if "hair_style" not in data:
                        data["hair_style"] = {}
                    return data
            except Exception:
                return {"hair_style": {}}
        return {"hair_style": {}}

    def save_hair_preview_config(self) -> bool:
        try:
            payload = {
                "hair_style": self.hair_style_previews,
            }
            with open(HAIR_PREVIEW_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def _make_scrollable(self, tab_frame: ttk.Frame) -> ttk.Frame:
        """Wrap *tab_frame* in a Canvas+Scrollbar so its content can scroll
        vertically when the window is too short to show everything.

        Returns the inner body frame that callers should use as *parent*
        when building tab content.
        """
        canvas = tk.Canvas(tab_frame, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
        body = ttk.Frame(canvas)

        # Keep scrollregion in sync with body size
        body.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")

        # Stretch body horizontally to match canvas width so fill=tk.X children work
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width),
        )

        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mousewheel only while the pointer is inside this canvas
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        return body

    def setup_spaceship_tab(self):
        parent = self._make_scrollable(self.tab_spaceship)
        
        # Category
        ttk.Label(parent, text=self.t("Component Category:")).pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(parent, textvariable=self.category_var, state="readonly")
        self.category_combo['values'] = list(self.component_map.keys())
        self.category_combo.pack(fill=tk.X, pady=(0, 10))
        self.category_combo.bind("<<ComboboxSelected>>", self.update_subcategories)
        self.category_combo.current(0) # Select first by default

        # Subcategory
        ttk.Label(parent, text=self.t("Subcategory:")).pack(anchor="w")
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(parent, textvariable=self.subcategory_var, state="readonly")
        self.subcategory_combo.pack(fill=tk.X, pady=(0, 10))
        self.subcategory_combo.bind("<<ComboboxSelected>>", self.update_variants)

        # STRUCTURAL VARIANT
        ttk.Label(parent, text=self.t("Structural Variant (Form Factor):")).pack(anchor="w")
        self.variant_var = tk.StringVar()
        self.variant_combo = ttk.Combobox(parent, textvariable=self.variant_var, state="readonly")
        self.variant_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Tier
        ttk.Label(parent, text=self.t("Tech Tier:")).pack(anchor="w")
        self.tier_var = tk.StringVar()
        self.tier_combo = ttk.Combobox(parent, textvariable=self.tier_var, state="readonly")
        self.tier_combo['values'] = self.tier_list
        self.tier_combo.pack(fill=tk.X, pady=(0, 20))
        self.tier_combo.current(2) # Default to Tier 3

        # --- MANUFACTURER SECTION ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(parent, text=self.t("Manufacturer Preset"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,5))
        
        self.manufacturer_var = tk.StringVar()
        self.manufacturer_combo = ttk.Combobox(parent, textvariable=self.manufacturer_var, state="readonly")
        self.manufacturer_combo['values'] = self.manufacturer_list
        self.manufacturer_combo.pack(fill=tk.X, pady=(0, 5))
        self.manufacturer_combo.current(0)
        self.manufacturer_combo.bind("<<ComboboxSelected>>", self.on_manufacturer_change)

        # Manufacturer Description Label
        self.lbl_manufacturer_desc = ttk.Label(parent, text="", foreground="gray", wraplength=350)
        self.lbl_manufacturer_desc.pack(anchor="w", pady=(0, 10))

        # --- COLOR SECTION ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(parent, text=self.t("Color Override"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,10))
        
        self.use_custom_colors = tk.BooleanVar(value=False)
        self.chk_custom_color = ttk.Checkbutton(parent, text=self.t("Enable Custom Colors"), variable=self.use_custom_colors, command=self.toggle_color_buttons)
        self.chk_custom_color.pack(anchor="w", pady=(0, 10))

        # Primary Color Button
        self.btn_primary_color = tk.Button(parent, text=self.t("Pick Main Color"), command=lambda: self.pick_color('primary'), state=tk.DISABLED, bg="#dddddd")
        self.btn_primary_color.pack(fill=tk.X, pady=2)
        
        # Secondary Color Button
        self.btn_secondary_color = tk.Button(parent, text=self.t("Pick Energy/Glow Color"), command=lambda: self.pick_color('secondary'), state=tk.DISABLED, bg="#dddddd")
        self.btn_secondary_color.pack(fill=tk.X, pady=2)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=20)

        # Generate Button for Tab 1
        self.gen_btn = ttk.Button(parent, text=self.t("GENERATE COMPONENT PROMPT"), command=self.generate_spaceship_prompt)
        self.gen_btn.pack(fill=tk.X, pady=(10, 0), ipady=10)

        # Initialize subcategories
        self.update_subcategories()

    def setup_item_tab(self):
        parent = self._make_scrollable(self.tab_items)
        
        ttk.Label(parent, text=self.t("Item Icon Generation"), font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        explanation = self.t("Generates a prompt for a 8x8 sprite sheet (64 items) from the selected CSV.")
        ttk.Label(parent, text=explanation, wraplength=380).pack(anchor="w", pady=(0, 10))

        # CSV Selection for Item Prompt
        frame_csv_item = ttk.Frame(parent)
        frame_csv_item.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_select_item_csv = ttk.Button(frame_csv_item, text=self.t("Select CSV..."), command=self.select_csv_for_item, width=15)
        self.btn_select_item_csv.pack(side=tk.LEFT)
        
        self.lbl_selected_item_csv = ttk.Label(frame_csv_item, text=os.path.basename(self.item_csv_path), foreground="blue")
        self.lbl_selected_item_csv.pack(side=tk.LEFT, padx=5)

        # Check for CSV existence
        if os.path.exists(ig.DEFAULT_CSV_PATH):
            status_text = self.t("CSV Detected: {path}").format(path=ig.DEFAULT_CSV_PATH)
            status_color = "green"
            state = tk.NORMAL
        else:
            status_text = self.t("Error: CSV not found at {path}").format(path=ig.DEFAULT_CSV_PATH)
            status_color = "red"
            state = tk.DISABLED

        self.lbl_csv_status = ttk.Label(parent, text=status_text, foreground=status_color, wraplength=380)
        self.lbl_csv_status.pack(anchor="w", pady=(0, 10))
        
        # Translation Checkbox
        self.var_translate_prompt = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text=self.t("Auto-Translate Content to English (Recommended)"), variable=self.var_translate_prompt).pack(anchor="w", pady=(0, 5))
        
        # Cache Checkbox
        ttk.Checkbutton(parent, text=self.t("Write Translation Result into CSV (Cache)"), variable=self.var_cache_translation).pack(anchor="w", pady=(0, 20))

        # Generate Button for Tab 2
        # Point to Threaded version
        self.btn_gen_items = ttk.Button(parent, text=self.t("GENERATE ICON GRID (8x8)"), command=self.generate_item_prompt_threaded, state=state)
        self.btn_gen_items.pack(fill=tk.X, pady=(10, 0), ipady=10)
        
    def setup_character_tab(self):
        parent = self._make_scrollable(self.tab_characters)
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text=self.t("Character Prompt Generation"), font=("Arial", 14, "bold")).pack(anchor="w")
        ttk.Label(header, text=self.t("Build a modular character prompt for retro sci-fi anime portraits."), wraplength=480).pack(anchor="w")

        main = ttk.Frame(parent)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        left_col = ttk.Frame(main)
        right_col = ttk.Frame(main)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # --- Base ---
        frame_base = ttk.LabelFrame(left_col, text=self.t("Core Descriptors"), padding=6)
        frame_base.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame_base, text=self.t("Gender:")).grid(row=0, column=0, sticky="w")
        gender_options = cg.get_gender_options(self.ui_lang)
        default_gender = ""
        if self.ui_lang == "zh":
            default_gender = next((g for g in gender_options if "女性" in g), "")
        else:
            default_gender = next((g for g in gender_options if "Female" in g), "")
        self.gender_var = tk.StringVar(value=default_gender or (gender_options[0] if gender_options else ""))
        self.gender_combo = ttk.Combobox(frame_base, textvariable=self.gender_var, state="readonly")
        self.gender_combo["values"] = gender_options
        self.gender_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_base, text=self.t("Age:")).grid(row=0, column=2, sticky="w")
        self.age_var = tk.IntVar(value=17)
        age_frame = ttk.Frame(frame_base)
        age_frame.grid(row=0, column=3, sticky="ew", padx=(5, 0))
        age_frame.columnconfigure(0, weight=1)
        # NOTE: ttk.Scale.set() triggers the `command` callback synchronously,
        # which calls _update_age_label() — so age_value_label MUST exist
        # before we call age_scale.set(). Create the label first.
        self.age_value_label = ttk.Label(age_frame, text="")
        self.age_scale = ttk.Scale(
            age_frame,
            from_=10,
            to=60,
            orient=tk.HORIZONTAL,
            command=lambda _=None: self._update_age_label(),
        )
        self.age_scale.set(self.age_var.get())
        self.age_scale.grid(row=0, column=0, sticky="ew")
        self.age_value_label.grid(row=0, column=1, sticky="e", padx=(6, 0))
        self._update_age_label()

        ttk.Label(frame_base, text=self.t("Body Type:")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        body_type_options = cg.get_body_type_options(self.ui_lang)
        self.body_type_var = tk.StringVar(value=body_type_options[0] if body_type_options else "")
        self.body_type_combo = ttk.Combobox(frame_base, textvariable=self.body_type_var, state="readonly")
        self.body_type_combo["values"] = body_type_options
        self.body_type_combo.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Skin Tone:")).grid(row=1, column=2, sticky="w", pady=(6, 0))
        skin_tone_options = cg.get_skin_tone_options(self.ui_lang)
        self.skin_tone_var = tk.StringVar(value=skin_tone_options[0] if skin_tone_options else "")
        self.skin_tone_combo = ttk.Combobox(frame_base, textvariable=self.skin_tone_var, state="readonly")
        self.skin_tone_combo["values"] = skin_tone_options
        self.skin_tone_combo.grid(row=1, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Framing:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        framing_options = cg.get_framing_options(self.ui_lang)
        default_framing = ""
        if self.ui_lang == "zh":
            default_framing = next((f for f in framing_options if "胸像" in f), "")
        else:
            default_framing = next((f for f in framing_options if "bust portrait" in f), "")
        self.framing_var = tk.StringVar(value=default_framing or (framing_options[0] if framing_options else ""))
        self.framing_combo = ttk.Combobox(frame_base, textvariable=self.framing_var, state="readonly")
        self.framing_combo["values"] = framing_options
        self.framing_combo.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Aspect Ratio:")).grid(row=2, column=2, sticky="w", pady=(6, 0))
        aspect_ratio_options = cg.get_aspect_ratio_options(self.ui_lang)
        default_ratio = next((r for r in aspect_ratio_options if "1:1" in r), "")
        self.aspect_ratio_var = tk.StringVar(value=default_ratio or (aspect_ratio_options[0] if aspect_ratio_options else ""))
        self.aspect_ratio_combo = ttk.Combobox(frame_base, textvariable=self.aspect_ratio_var, state="readonly")
        self.aspect_ratio_combo["values"] = aspect_ratio_options
        self.aspect_ratio_combo.grid(row=2, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Expression:")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        expression_options = cg.get_expression_options(self.ui_lang)
        self.expression_var = tk.StringVar(value=expression_options[0] if expression_options else "")
        self.expression_combo = ttk.Combobox(frame_base, textvariable=self.expression_var, state="readonly")
        self.expression_combo["values"] = expression_options
        self.expression_combo.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Gaze:")).grid(row=3, column=2, sticky="w", pady=(6, 0))
        gaze_options = cg.get_gaze_options(self.ui_lang)
        self.gaze_var = tk.StringVar(value=gaze_options[0] if gaze_options else "")
        self.gaze_combo = ttk.Combobox(frame_base, textvariable=self.gaze_var, state="readonly")
        self.gaze_combo["values"] = gaze_options
        self.gaze_combo.grid(row=3, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Clothing Hint:")).grid(row=4, column=0, sticky="w", pady=(6, 0))
        clothing_hint_options = cg.get_clothing_hint_options(self.ui_lang)
        self.clothing_hint_var = tk.StringVar(value=clothing_hint_options[0] if clothing_hint_options else "")
        self.clothing_hint_combo = ttk.Combobox(frame_base, textvariable=self.clothing_hint_var, state="readonly")
        self.clothing_hint_combo["values"] = clothing_hint_options
        self.clothing_hint_combo.grid(row=4, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        frame_base.columnconfigure(1, weight=1)
        frame_base.columnconfigure(3, weight=1)

        # --- Hair ---
        frame_hair = ttk.LabelFrame(left_col, text=self.t("Hair"), padding=6)
        frame_hair.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame_hair, text=self.t("Hair Style:")).grid(row=0, column=0, sticky="w")
        self.hair_style_options_by_gender = cg.get_hair_style_options_by_gender(self.ui_lang)
        self.hair_style_all_options = cg.get_hair_style_options(self.ui_lang)
        self.filter_hair_by_gender = tk.BooleanVar(value=True)
        hair_style_options = self._get_filtered_hair_style_options()
        self.hair_style_var = tk.StringVar(value=hair_style_options[0] if hair_style_options else "")
        self.hair_style_combo = ttk.Combobox(frame_hair, textvariable=self.hair_style_var, state="readonly")
        self.hair_style_combo["values"] = hair_style_options
        self.hair_style_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_hair, text=self.t("Hair Color:")).grid(row=0, column=2, sticky="w")
        hair_color_options = cg.get_hair_color_options(self.ui_lang)
        self.hair_color_var = tk.StringVar(value=hair_color_options[0] if hair_color_options else "")
        self.hair_color_combo = ttk.Combobox(frame_hair, textvariable=self.hair_color_var, state="readonly")
        self.hair_color_combo["values"] = hair_color_options
        self.hair_color_combo.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        self.hair_color_advanced = tk.BooleanVar(value=False)
        self.chk_hair_color_advanced = ttk.Checkbutton(
            frame_hair,
            text=self.t("Hair Color Advanced Mode"),
            variable=self.hair_color_advanced,
            command=self.toggle_hair_color_mode,
        )
        self.chk_hair_color_advanced.grid(row=1, column=0, sticky="w", pady=(6, 0), columnspan=2)

        hair_color_controls = ttk.Frame(frame_hair)
        hair_color_controls.grid(row=1, column=2, columnspan=2, sticky="ew", pady=(6, 0))
        hair_color_controls.columnconfigure(0, weight=1)
        self.hair_colors = []
        self.btn_add_hair_color = ttk.Button(
            hair_color_controls,
            text=self.t("Add Hair Color"),
            command=self.add_hair_color,
            width=12,
            state=tk.DISABLED,
        )
        self.btn_add_hair_color.grid(row=0, column=0, sticky="w")
        self.btn_clear_hair_colors = ttk.Button(
            hair_color_controls,
            text=self.t("Clear Hair Colors"),
            command=self.clear_hair_colors,
            width=12,
            state=tk.DISABLED,
        )
        self.btn_clear_hair_colors.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.hair_color_preview = ttk.Frame(frame_hair)
        self.hair_color_preview.grid(row=2, column=2, columnspan=2, sticky="ew", pady=(4, 0))
        self.hair_color_preview.columnconfigure(0, weight=1)

        self.chk_filter_hair_by_gender = ttk.Checkbutton(
            frame_hair,
            text=self.t("Only show hair styles for current gender"),
            variable=self.filter_hair_by_gender,
            command=self.refresh_hair_style_options,
        )
        self.chk_filter_hair_by_gender.grid(row=2, column=0, sticky="w", pady=(4, 0), columnspan=2)

        ttk.Label(frame_hair, text=self.t("Bangs Presence:")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        bangs_presence_options = cg.get_bangs_presence_options(self.ui_lang)
        self.bangs_presence_var = tk.StringVar(value=bangs_presence_options[0] if bangs_presence_options else "")
        self.bangs_presence_combo = ttk.Combobox(frame_hair, textvariable=self.bangs_presence_var, state="readonly")
        self.bangs_presence_combo["values"] = bangs_presence_options
        self.bangs_presence_combo.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_hair, text=self.t("Bangs Style:")).grid(row=3, column=2, sticky="w", pady=(6, 0))
        bangs_style_options = cg.get_bangs_style_options(self.ui_lang)
        self.bangs_style_var = tk.StringVar(value=bangs_style_options[0] if bangs_style_options else "")
        self.bangs_style_combo = ttk.Combobox(frame_hair, textvariable=self.bangs_style_var, state="readonly")
        self.bangs_style_combo["values"] = bangs_style_options
        self.bangs_style_combo.grid(row=3, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        frame_hair.columnconfigure(1, weight=1)
        frame_hair.columnconfigure(3, weight=1)

        self.gender_var.trace_add("write", self.refresh_hair_style_options)
        self.refresh_hair_style_options()

        # --- Face ---
        frame_face = ttk.LabelFrame(left_col, text=self.t("Face"), padding=6)
        frame_face.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        frame_face.columnconfigure(1, weight=1)
        frame_face.columnconfigure(3, weight=1)

        ttk.Label(frame_face, text=self.t("Face Shape:")).grid(row=0, column=0, sticky="w")
        face_shape_options = cg.get_face_shape_options(self.ui_lang)
        self.face_shape_var = tk.StringVar(value=face_shape_options[0] if face_shape_options else "")
        self.face_shape_combo = ttk.Combobox(frame_face, textvariable=self.face_shape_var, state="readonly")
        self.face_shape_combo["values"] = face_shape_options
        self.face_shape_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_face, text=self.t("Eye Size:")).grid(row=0, column=2, sticky="w")
        eye_size_options = cg.get_eye_size_options(self.ui_lang)
        self.eye_size_var = tk.StringVar(value=eye_size_options[0] if eye_size_options else "")
        self.eye_size_combo = ttk.Combobox(frame_face, textvariable=self.eye_size_var, state="readonly")
        self.eye_size_combo["values"] = eye_size_options
        self.eye_size_combo.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        ttk.Label(frame_face, text=self.t("Nose Size:")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        nose_size_options = cg.get_nose_size_options(self.ui_lang)
        self.nose_size_var = tk.StringVar(value=nose_size_options[0] if nose_size_options else "")
        self.nose_size_combo = ttk.Combobox(frame_face, textvariable=self.nose_size_var, state="readonly")
        self.nose_size_combo["values"] = nose_size_options
        self.nose_size_combo.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_face, text=self.t("Mouth Shape:")).grid(row=1, column=2, sticky="w", pady=(6, 0))
        mouth_shape_options = cg.get_mouth_shape_options(self.ui_lang)
        self.mouth_shape_var = tk.StringVar(value=mouth_shape_options[0] if mouth_shape_options else "")
        self.mouth_shape_combo = ttk.Combobox(frame_face, textvariable=self.mouth_shape_var, state="readonly")
        self.mouth_shape_combo["values"] = mouth_shape_options
        self.mouth_shape_combo.grid(row=1, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_face, text=self.t("Cheek Fullness:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        cheek_fullness_options = cg.get_cheek_fullness_options(self.ui_lang)
        self.cheek_fullness_var = tk.StringVar(value=cheek_fullness_options[0] if cheek_fullness_options else "")
        self.cheek_fullness_combo = ttk.Combobox(frame_face, textvariable=self.cheek_fullness_var, state="readonly")
        self.cheek_fullness_combo["values"] = cheek_fullness_options
        self.cheek_fullness_combo.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_face, text=self.t("Jaw Width:")).grid(row=2, column=2, sticky="w", pady=(6, 0))
        jaw_width_options = cg.get_jaw_width_options(self.ui_lang)
        self.jaw_width_var = tk.StringVar(value=jaw_width_options[0] if jaw_width_options else "")
        self.jaw_width_combo = ttk.Combobox(frame_face, textvariable=self.jaw_width_var, state="readonly")
        self.jaw_width_combo["values"] = jaw_width_options
        self.jaw_width_combo.grid(row=2, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_face, text=self.t("Eye Color:")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        eye_color_options = cg.get_eye_color_options(self.ui_lang)
        self.eye_color_var = tk.StringVar(value=eye_color_options[0] if eye_color_options else "")
        self.eye_color_combo = ttk.Combobox(frame_face, textvariable=self.eye_color_var, state="readonly")
        self.eye_color_combo["values"] = eye_color_options
        self.eye_color_combo.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        face_list_frame = ttk.Frame(frame_face)
        face_list_frame.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=(6, 0))
        ttk.Label(face_list_frame, text=self.t("Face Features")).grid(row=0, column=0, sticky="w")
        face_list_container = ttk.Frame(face_list_frame)
        face_list_container.grid(row=1, column=0, sticky="nsew")
        self.face_feature_list = tk.Listbox(
            face_list_container,
            selectmode=tk.MULTIPLE,
            height=6,
            exportselection=False,
        )
        for option in cg.get_appearance_options(self.ui_lang):
            self.face_feature_list.insert(tk.END, option)
        self.face_feature_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        face_scroll = ttk.Scrollbar(face_list_container, orient="vertical", command=self.face_feature_list.yview)
        face_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.face_feature_list.config(yscrollcommand=face_scroll.set)
        face_list_frame.columnconfigure(0, weight=1)

        # --- Artist Styles ---
        frame_artists = ttk.LabelFrame(left_col, text=self.t("Artist Styles"), padding=6)
        frame_artists.grid(row=3, column=0, sticky="nsew", pady=(0, 8))
        frame_artists.columnconfigure(0, weight=1)
        artist_list_frame = ttk.Frame(frame_artists)
        artist_list_frame.grid(row=0, column=0, sticky="nsew")
        self.artist_list = tk.Listbox(
            artist_list_frame,
            selectmode=tk.MULTIPLE,
            height=5,
            exportselection=False,
        )
        self.artist_label_map = cg.get_artist_label_map(self.ui_lang)
        for option in cg.get_artist_options(self.ui_lang):
            self.artist_list.insert(tk.END, option)
        self.artist_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        artist_scroll = ttk.Scrollbar(artist_list_frame, orient="vertical", command=self.artist_list.yview)
        artist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.artist_list.config(yscrollcommand=artist_scroll.set)

        # --- Style Reference ---
        frame_style_ref = ttk.LabelFrame(left_col, text=self.t("Style Reference (Optional)"), padding=6)
        frame_style_ref.grid(row=4, column=0, sticky="nsew", pady=(0, 8))
        ttk.Button(frame_style_ref, text=self.t("Select Style Image..."), command=self.select_style_reference_image).pack(fill=tk.X)
        self.lbl_style_ref = ttk.Label(frame_style_ref, text=self.t("No style image selected"), foreground="gray", wraplength=320)
        self.lbl_style_ref.pack(anchor="w", pady=(4, 6))
        ttk.Button(frame_style_ref, text=self.t("Clear Style Image"), command=self.clear_style_reference_image).pack(fill=tk.X)
        self.chk_style_ref_only = ttk.Checkbutton(
            frame_style_ref,
            text=self.t("Use style reference only (remove style text from prompt)"),
            variable=self.style_ref_only_mode,
            command=self.schedule_character_prompt_update,
        )
        self.chk_style_ref_only.pack(anchor="w", pady=(6, 0))
        self.chk_style_ref_only.config(state=tk.DISABLED)


        # --- Extra Modifiers ---
        action_bar = ttk.Frame(parent)
        action_bar.pack(fill=tk.X, pady=(2, 0))
        action_bar.columnconfigure(1, weight=1)

        ttk.Label(action_bar, text=self.t("Extra modifiers (optional):")).grid(row=0, column=0, sticky="w")
        self.extra_modifiers_var = tk.StringVar()
        ttk.Entry(action_bar, textvariable=self.extra_modifiers_var).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._bind_character_auto_update()
        self.schedule_character_prompt_update()

    def setup_clothing_tab(self):
        parent = self._make_scrollable(self.tab_clothing)
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text=self.t("Clothing Preset Generation"), font=("Arial", 14, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text=self.t("Build a modular clothing preset prompt for retro sci-fi outfit sheets."),
            wraplength=480,
        ).pack(anchor="w")

        main = ttk.Frame(parent)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        left_col = ttk.Frame(main)
        right_col = ttk.Frame(main)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # --- Faction & Role ---
        frame_faction = ttk.LabelFrame(left_col, text=self.t("Faction & Role"), padding=6)
        frame_faction.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        frame_faction.columnconfigure(1, weight=1)

        ttk.Label(frame_faction, text=self.t("Faction:")).grid(row=0, column=0, sticky="w")
        faction_options = clg.get_faction_options(self.ui_lang)
        self.faction_var = tk.StringVar(value=faction_options[0] if faction_options else "")
        self.faction_combo = ttk.Combobox(frame_faction, textvariable=self.faction_var, state="readonly")
        self.faction_combo["values"] = faction_options
        self.faction_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.faction_combo.bind("<<ComboboxSelected>>", self.update_clothing_faction_desc)

        ttk.Label(frame_faction, text=self.t("Outfit Gender:")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        gender_options = clg.get_gender_options(self.ui_lang)
        self.clothing_gender_var = tk.StringVar(value=gender_options[0] if gender_options else "")
        self.clothing_gender_combo = ttk.Combobox(frame_faction, textvariable=self.clothing_gender_var, state="readonly")
        self.clothing_gender_combo["values"] = gender_options
        self.clothing_gender_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_faction, text=self.t("Role Archetype:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        role_options = clg.get_role_options(self.ui_lang)
        self.role_var = tk.StringVar(value=role_options[0] if role_options else "")
        self.role_combo = ttk.Combobox(frame_faction, textvariable=self.role_var, state="readonly")
        self.role_combo["values"] = role_options
        self.role_combo.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        self.faction_desc_map = clg.get_faction_description_map(self.ui_lang)
        self.lbl_faction_desc = ttk.Label(frame_faction, text="", foreground="gray", wraplength=340)
        self.lbl_faction_desc.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.update_clothing_faction_desc()

        # --- Presentation & Layout ---
        frame_layout = ttk.LabelFrame(left_col, text=self.t("Presentation & Layout"), padding=6)
        frame_layout.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        frame_layout.columnconfigure(1, weight=1)

        ttk.Label(frame_layout, text=self.t("View Mode:")).grid(row=0, column=0, sticky="w")
        view_mode_options = clg.get_view_mode_options(self.ui_lang)
        view_mode_default = next(
            (opt for opt in view_mode_options if ("单一正面全身" in opt or "single full-body front" in opt)),
            view_mode_options[0] if view_mode_options else "",
        )
        self.view_mode_var = tk.StringVar(value=view_mode_default)
        self.view_mode_combo = ttk.Combobox(frame_layout, textvariable=self.view_mode_var, state="readonly")
        self.view_mode_combo["values"] = view_mode_options
        self.view_mode_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        ttk.Label(frame_layout, text=self.t("Aspect Ratio:")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        aspect_ratio_options = clg.get_aspect_ratio_options(self.ui_lang)
        aspect_ratio_default = next(
            (opt for opt in aspect_ratio_options if "1:1" in opt),
            aspect_ratio_options[0] if aspect_ratio_options else "",
        )
        self.clothing_aspect_ratio_var = tk.StringVar(value=aspect_ratio_default)
        self.clothing_aspect_ratio_combo = ttk.Combobox(
            frame_layout, textvariable=self.clothing_aspect_ratio_var, state="readonly"
        )
        self.clothing_aspect_ratio_combo["values"] = aspect_ratio_options
        self.clothing_aspect_ratio_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_layout, text=self.t("Pose:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        pose_options = clg.get_pose_options(self.ui_lang)
        pose_default = next(
            (opt for opt in pose_options if ("中性 A 字站姿人台" in opt or "neutral A-pose mannequin" in opt)),
            pose_options[0] if pose_options else "",
        )
        self.pose_var = tk.StringVar(value=pose_default)
        self.pose_combo = ttk.Combobox(frame_layout, textvariable=self.pose_var, state="readonly")
        self.pose_combo["values"] = pose_options
        self.pose_combo.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_layout, text=self.t("Presentation:")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        presentation_options = clg.get_presentation_options(self.ui_lang)
        presentation_default = next(
            (opt for opt in presentation_options if ("平铺展示" in opt or "flat lay garment layout" in opt)),
            presentation_options[0] if presentation_options else "",
        )
        self.presentation_var = tk.StringVar(value=presentation_default)
        self.presentation_combo = ttk.Combobox(frame_layout, textvariable=self.presentation_var, state="readonly")
        self.presentation_combo["values"] = presentation_options
        self.presentation_combo.grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        # --- Outfit Build ---
        frame_outfit = ttk.LabelFrame(right_col, text=self.t("Outfit Build"), padding=6)
        frame_outfit.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        frame_outfit.columnconfigure(1, weight=1)

        ttk.Label(frame_outfit, text=self.t("Outfit Category:")).grid(row=0, column=0, sticky="w")
        outfit_options = clg.get_outfit_category_options(self.ui_lang)
        self.outfit_category_var = tk.StringVar(value=outfit_options[0] if outfit_options else "")
        self.outfit_category_combo = ttk.Combobox(
            frame_outfit, textvariable=self.outfit_category_var, state="readonly"
        )
        self.outfit_category_combo["values"] = outfit_options
        self.outfit_category_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.show_all_outfits_var = tk.BooleanVar(value=False)
        self.chk_show_all_outfits = ttk.Checkbutton(
            frame_outfit,
            text=self.t("Show all outfit categories"),
            variable=self.show_all_outfits_var,
            command=self.refresh_outfit_category_options,
        )
        self.chk_show_all_outfits.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        ttk.Label(frame_outfit, text=self.t("Silhouette:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        silhouette_options = clg.get_silhouette_options(self.ui_lang)
        self.silhouette_var = tk.StringVar(value=silhouette_options[0] if silhouette_options else "")
        self.silhouette_combo = ttk.Combobox(frame_outfit, textvariable=self.silhouette_var, state="readonly")
        self.silhouette_combo["values"] = silhouette_options
        self.silhouette_combo.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_outfit, text=self.t("Layering:")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        layering_options = clg.get_layering_options(self.ui_lang)
        self.layering_var = tk.StringVar(value=layering_options[0] if layering_options else "")
        self.layering_combo = ttk.Combobox(frame_outfit, textvariable=self.layering_var, state="readonly")
        self.layering_combo["values"] = layering_options
        self.layering_combo.grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_outfit, text=self.t("Material:")).grid(row=4, column=0, sticky="w", pady=(6, 0))
        material_options = clg.get_material_options(self.ui_lang)
        self.clothing_material_var = tk.StringVar(value=material_options[0] if material_options else "")
        self.clothing_material_combo = ttk.Combobox(
            frame_outfit, textvariable=self.clothing_material_var, state="readonly"
        )
        self.clothing_material_combo["values"] = material_options
        self.clothing_material_combo.grid(row=4, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_outfit, text=self.t("Palette:")).grid(row=5, column=0, sticky="w", pady=(6, 0))
        palette_options = clg.get_palette_options(self.ui_lang)
        self.palette_var = tk.StringVar(value=palette_options[0] if palette_options else "")
        self.palette_combo = ttk.Combobox(frame_outfit, textvariable=self.palette_var, state="readonly")
        self.palette_combo["values"] = palette_options
        self.palette_combo.grid(row=5, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_outfit, text=self.t("Wear State:")).grid(row=6, column=0, sticky="w", pady=(6, 0))
        wear_state_options = clg.get_wear_state_options(self.ui_lang)
        self.wear_state_var = tk.StringVar(value=wear_state_options[0] if wear_state_options else "")
        self.wear_state_combo = ttk.Combobox(frame_outfit, textvariable=self.wear_state_var, state="readonly")
        self.wear_state_combo["values"] = wear_state_options
        self.wear_state_combo.grid(row=6, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        self.role_var.trace_add("write", self.refresh_outfit_category_options)
        self.clothing_gender_var.trace_add("write", self.refresh_outfit_category_options)
        self.refresh_outfit_category_options()

        # --- Detail Accents ---
        frame_details = ttk.LabelFrame(right_col, text=self.t("Detail Accents"), padding=6)
        frame_details.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        detail_list_frame = ttk.Frame(frame_details)
        detail_list_frame.pack(fill=tk.BOTH, expand=True)
        self.detail_accent_list = tk.Listbox(
            detail_list_frame,
            selectmode=tk.MULTIPLE,
            height=5,
            exportselection=False,
        )
        for option in clg.get_detail_accent_options(self.ui_lang):
            self.detail_accent_list.insert(tk.END, option)
        self.detail_accent_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll = ttk.Scrollbar(detail_list_frame, orient="vertical", command=self.detail_accent_list.yview)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_accent_list.config(yscrollcommand=detail_scroll.set)

        # --- Accessories ---
        frame_accessories = ttk.LabelFrame(right_col, text=self.t("Accessories"), padding=6)
        frame_accessories.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        accessory_list_frame = ttk.Frame(frame_accessories)
        accessory_list_frame.pack(fill=tk.BOTH, expand=True)
        self.clothing_accessory_list = tk.Listbox(
            accessory_list_frame,
            selectmode=tk.MULTIPLE,
            height=5,
            exportselection=False,
        )
        for option in clg.get_accessory_options(self.ui_lang):
            self.clothing_accessory_list.insert(tk.END, option)
        self.clothing_accessory_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        accessory_scroll = ttk.Scrollbar(accessory_list_frame, orient="vertical", command=self.clothing_accessory_list.yview)
        accessory_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.clothing_accessory_list.config(yscrollcommand=accessory_scroll.set)

        # --- Insignia ---
        frame_insignia = ttk.LabelFrame(right_col, text=self.t("Insignia & Markings"), padding=6)
        frame_insignia.grid(row=3, column=0, sticky="nsew", pady=(0, 8))
        insignia_list_frame = ttk.Frame(frame_insignia)
        insignia_list_frame.pack(fill=tk.BOTH, expand=True)
        self.clothing_insignia_list = tk.Listbox(
            insignia_list_frame,
            selectmode=tk.MULTIPLE,
            height=4,
            exportselection=False,
        )
        for option in clg.get_insignia_options(self.ui_lang):
            self.clothing_insignia_list.insert(tk.END, option)
        self.clothing_insignia_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        insignia_scroll = ttk.Scrollbar(insignia_list_frame, orient="vertical", command=self.clothing_insignia_list.yview)
        insignia_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.clothing_insignia_list.config(yscrollcommand=insignia_scroll.set)

        # --- Misc ---
        frame_misc = ttk.LabelFrame(right_col, text=self.t("Misc"), padding=6)
        frame_misc.grid(row=4, column=0, sticky="ew")
        frame_misc.columnconfigure(0, weight=1)
        ttk.Label(frame_misc, text=self.t("Custom notes (comma separated):")).grid(row=0, column=0, sticky="w")
        self.clothing_custom_notes_var = tk.StringVar()
        ttk.Entry(frame_misc, textvariable=self.clothing_custom_notes_var).grid(row=1, column=0, sticky="ew", pady=(4, 0))

        # --- Outfit Swap Preview (Gemini) ---
        frame_swap = ttk.LabelFrame(right_col, text=self.t("Outfit Swap (Preview)"), padding=6)
        frame_swap.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        frame_swap.columnconfigure(1, weight=1)

        ttk.Label(frame_swap, text=self.t("Character Image:")).grid(row=0, column=0, sticky="w")
        self.swap_character_path_var = tk.StringVar(value=self.t("No image selected"))
        self.lbl_swap_character = ttk.Label(frame_swap, textvariable=self.swap_character_path_var, foreground="gray", wraplength=280)
        self.lbl_swap_character.grid(row=0, column=1, sticky="w", padx=(5, 0))
        ttk.Button(frame_swap, text=self.t("Select Character Image..."), command=self.select_swap_character_image).grid(
            row=1, column=1, sticky="ew", padx=(5, 0), pady=(4, 0)
        )

        ttk.Label(frame_swap, text=self.t("Clothing Preset Image:")).grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.swap_clothing_path_var = tk.StringVar(value=self.t("No image selected"))
        self.lbl_swap_clothing = ttk.Label(frame_swap, textvariable=self.swap_clothing_path_var, foreground="gray", wraplength=280)
        self.lbl_swap_clothing.grid(row=2, column=1, sticky="w", padx=(5, 0), pady=(8, 0))
        ttk.Button(frame_swap, text=self.t("Select Clothing Image..."), command=self.select_swap_clothing_image).grid(
            row=3, column=1, sticky="ew", padx=(5, 0), pady=(4, 0)
        )

        ttk.Label(frame_swap, text=self.t("Output Name:")).grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.swap_output_name_var = tk.StringVar(value="swap_preview")
        ttk.Entry(frame_swap, textvariable=self.swap_output_name_var).grid(row=4, column=1, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Button(frame_swap, text=self.t("Run Outfit Swap (Gemini)"), command=self.run_outfit_swap_threaded).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        # --- Extra Modifiers ---
        action_bar = ttk.Frame(parent)
        action_bar.pack(fill=tk.X, pady=(2, 0))
        action_bar.columnconfigure(1, weight=1)
        ttk.Label(action_bar, text=self.t("Extra modifiers (optional):")).grid(row=0, column=0, sticky="w")
        self.clothing_extra_modifiers_var = tk.StringVar()
        ttk.Entry(action_bar, textvariable=self.clothing_extra_modifiers_var).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._bind_clothing_auto_update()
        self.schedule_clothing_prompt_update()

    def update_clothing_faction_desc(self, *_):
        desc = self.faction_desc_map.get(self.faction_var.get(), "")
        if not desc:
            desc = self.t("No faction description")
        self.lbl_faction_desc.config(text=desc)
        self.schedule_clothing_prompt_update()

    def refresh_outfit_category_options(self, *_):
        allow_all = bool(self.show_all_outfits_var.get())
        options = clg.get_outfit_category_options_for_role(self.ui_lang, self.role_var.get(), allow_all)
        if not options:
            options = clg.get_outfit_category_options(self.ui_lang)
        current = self.outfit_category_var.get()
        self.outfit_category_combo["values"] = options
        if current in options:
            self.outfit_category_var.set(current)
        else:
            self.outfit_category_var.set(options[0] if options else "")
        self.schedule_clothing_prompt_update()

    def _select_image_path(self) -> str:
        return filedialog.askopenfilename(
            title=self.t("Select Image File(s)..."),
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.gif")],
        )

    def select_swap_character_image(self):
        path = self._select_image_path()
        if not path:
            return
        self.swap_character_path_var.set(path)
        self.lbl_swap_character.config(foreground="black")

    def select_swap_clothing_image(self):
        path = self._select_image_path()
        if not path:
            return
        self.swap_clothing_path_var.set(path)
        self.lbl_swap_clothing.config(foreground="black")

    def _load_image_blob(self, path: str):
        with open(path, "rb") as fh:
            image_bytes = fh.read()
        mime_type = mimetypes.guess_type(path)[0] or "image/png"
        return image_bytes, mime_type

    def _build_outfit_swap_prompt(self) -> str:
        guidance = [
            "You are given two images.",
            "First image: the character to keep (face, body proportions, pose, lighting).",
            "Second image: the clothing preset to apply.",
            "Replace only the outfit on the character with the clothing from the second image.",
            "Keep identity, face, hair, skin, and pose unchanged.",
            "Do NOT change the framing, camera angle, crop, or composition of Image 1.",
            "The output must keep Image 1's exact framing and silhouette scale.",
            "Adapt the clothing to the character, not the character to the clothing.",
            "This is an outfit swap, NOT a head swap. Do not move or replace the head.",
            "Match the retro 90s Japanese realistic sci-fi anime cel-shaded look.",
            "Keep the background clean and simple.",
        ]
        extra = self.clothing_extra_modifiers_var.get().strip()
        if extra:
            guidance.append(f"Extra notes: {extra}.")
        return "\n".join(guidance).strip()

    def run_outfit_swap_threaded(self):
        character_path = self.swap_character_path_var.get()
        clothing_path = self.swap_clothing_path_var.get()
        if (
            self.t("No image selected") in (character_path, clothing_path)
            or not os.path.exists(character_path)
            or not os.path.exists(clothing_path)
        ):
            messagebox.showerror(self.t("Error"), self.t("Select character and clothing images first."))
            return
        _, api_key, _, _ = self._get_active_api_credentials()
        if not api_key:
            messagebox.showerror(self.t("Error"), self.t("API key is missing. Please add your key in Settings."))
            return
        output_name = self.swap_output_name_var.get().strip() or "swap_preview"
        prompt = self._build_outfit_swap_prompt()
        log_lines = [
            "# Outfit Swap Prompt",
            f"Character: {character_path}",
            f"Clothing: {clothing_path}",
            f"Output: {output_name}",
            "",
            prompt,
        ]
        self.set_output("\n".join(log_lines))
        self.set_ui_busy(True, self.t("Generating Image..."))
        threading.Thread(
            target=self._run_outfit_swap_task,
            args=(prompt, character_path, clothing_path),
            daemon=True,
        ).start()

    def _run_outfit_swap_task(self, prompt: str, character_path: str, clothing_path: str):
        try:
            character_blob = self._load_image_blob(character_path)
            clothing_blob = self._load_image_blob(clothing_path)
            image_bytes, mime_type = self._generate_image_with_active_provider(
                prompt,
                reference_images=[character_blob, clothing_blob],
                text_last=True,
            )
            self.pending_images = []
            self.edit_undo_stack.clear()
            self.pending_image_bytes = image_bytes
            self.pending_image_mime = mime_type
            self.pending_image_prefix = "clothing_swap"
            self.root.after(0, self.show_preview_image)
            self.root.after(0, self._refresh_undo_button)
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
            self.root.after(0, lambda: self.status_var.set(self.t("Image ready. Use Save/Discard.")))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))
        
    # ------------------------------------------------------------------
    # Asset Library Tab
    # ------------------------------------------------------------------
    def setup_library_tab(self):
        from core import library as _lib

        parent = self.tab_library
        self._library_module = _lib
        self._library_selected_id = None
        self._library_preview_photo = None  # 防止 PhotoImage 被 GC

        # ---- 顶部过滤工具条 ----
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(toolbar, text=self.t("Type:")).pack(side=tk.LEFT)
        self.lib_type_var = tk.StringVar(value="(all)")
        type_options = ["(all)", "spaceship", "mecha", "mecha_part", "ship", "items", "character", "clothing", "slicer", "curation", "gemini", "clothing_swap"]
        ttk.Combobox(toolbar, textvariable=self.lib_type_var, values=type_options,
                     state="readonly", width=14).pack(side=tk.LEFT, padx=(4, 12))

        ttk.Label(toolbar, text=self.t("Min ★:")).pack(side=tk.LEFT)
        self.lib_min_rating_var = tk.IntVar(value=0)
        ttk.Spinbox(toolbar, from_=0, to=5, textvariable=self.lib_min_rating_var,
                    width=4).pack(side=tk.LEFT, padx=(4, 12))

        ttk.Label(toolbar, text=self.t("Search:")).pack(side=tk.LEFT)
        self.lib_keyword_var = tk.StringVar()
        kw_entry = ttk.Entry(toolbar, textvariable=self.lib_keyword_var, width=24)
        kw_entry.pack(side=tk.LEFT, padx=(4, 8))
        kw_entry.bind("<Return>", lambda e: self._library_refresh())

        ttk.Button(toolbar, text=self.t("Refresh"),
                   command=self._library_refresh).pack(side=tk.LEFT, padx=(0, 4))
        self.lib_count_label = ttk.Label(toolbar, text="")
        self.lib_count_label.pack(side=tk.LEFT, padx=(8, 0))

        # ---- 主体：左侧列表，右侧详情 ----
        body = ttk.Frame(parent)
        body.pack(fill=tk.BOTH, expand=True)

        # 左侧：Treeview
        list_frame = ttk.Frame(body)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        cols = ("id", "time", "type", "rating", "prompt")
        self.lib_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=20)
        self.lib_tree.heading("id", text="ID")
        self.lib_tree.heading("time", text=self.t("Time"))
        self.lib_tree.heading("type", text=self.t("Type"))
        self.lib_tree.heading("rating", text="★")
        self.lib_tree.heading("prompt", text=self.t("Prompt / Notes"))
        self.lib_tree.column("id", width=50, anchor=tk.E)
        self.lib_tree.column("time", width=140)
        self.lib_tree.column("type", width=90)
        self.lib_tree.column("rating", width=40, anchor=tk.CENTER)
        self.lib_tree.column("prompt", width=320)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.lib_tree.yview)
        self.lib_tree.configure(yscrollcommand=vsb.set)
        self.lib_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.LEFT, fill=tk.Y)
        self.lib_tree.bind("<<TreeviewSelect>>", self._library_on_select)

        # 右侧：详情面板
        detail = ttk.Frame(body, width=400)
        detail.pack(side=tk.LEFT, fill=tk.BOTH)
        detail.pack_propagate(False)

        self.lib_preview_label = ttk.Label(detail, text=self.t("No preview image"),
                                           anchor="center", relief="sunken")
        self.lib_preview_label.pack(fill=tk.BOTH, expand=False, ipady=80)

        info_frame = ttk.LabelFrame(detail, text=self.t("Details"), padding=6)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        # 评级 + 标签
        edit_frame = ttk.Frame(info_frame)
        edit_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(edit_frame, text="★").pack(side=tk.LEFT)
        self.lib_rating_var = tk.IntVar(value=0)
        ttk.Spinbox(edit_frame, from_=0, to=5, textvariable=self.lib_rating_var,
                    width=4, command=self._library_save_rating).pack(side=tk.LEFT, padx=(4, 12))
        ttk.Label(edit_frame, text=self.t("Tags:")).pack(side=tk.LEFT)
        self.lib_tags_var = tk.StringVar()
        tags_entry = ttk.Entry(edit_frame, textvariable=self.lib_tags_var)
        tags_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        tags_entry.bind("<FocusOut>", lambda e: self._library_save_tags())
        tags_entry.bind("<Return>", lambda e: self._library_save_tags())

        # prompt / params
        self.lib_detail_text = tk.Text(info_frame, height=10, wrap="word")
        self.lib_detail_text.pack(fill=tk.BOTH, expand=True)
        self.lib_detail_text.config(state=tk.DISABLED)

        # 操作按钮
        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(btn_frame, text=self.t("Copy Prompt"),
                   command=self._library_copy_prompt).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text=self.t("Open Folder"),
                   command=self._library_open_folder).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text=self.t("Edit with Gemini"),
                   command=self._library_edit_with_gemini).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text=self.t("Delete Entry"),
                   command=self._library_delete).pack(side=tk.RIGHT)

        # 切到 tab 时自动刷新
        self.notebook.bind("<<NotebookTabChanged>>", self._library_on_tab_change, add="+")
        self._library_refresh()

    def _library_on_tab_change(self, _event=None):
        try:
            if self.notebook.select() == str(self.tab_library):
                self._library_refresh()
        except Exception:
            pass

    def _library_refresh(self):
        gtype = self.lib_type_var.get()
        if gtype == "(all)":
            gtype = None
        kw = self.lib_keyword_var.get().strip() or None
        min_rating = max(0, int(self.lib_min_rating_var.get() or 0))
        entries = self._library_module.list_entries(
            generator_type=gtype,
            min_rating=min_rating,
            keyword=kw,
            limit=500,
        )
        self.lib_tree.delete(*self.lib_tree.get_children())
        for e in entries:
            time_str = e.created_at.replace("T", " ").rsplit("+", 1)[0]
            stars = "★" * e.rating + "·" * (5 - e.rating)
            preview = (e.prompt or e.notes or "").replace("\n", " ")
            if len(preview) > 80:
                preview = preview[:80] + "…"
            self.lib_tree.insert("", "end", iid=str(e.id),
                                 values=(e.id, time_str, e.generator_type, stars, preview))
        self.lib_count_label.config(
            text=self.t("{n} entries").format(n=len(entries))
        )

    def _library_on_select(self, _event=None):
        sel = self.lib_tree.selection()
        if not sel:
            return
        try:
            entry_id = int(sel[0])
        except (ValueError, IndexError):
            return
        entry = self._library_module.get_entry(entry_id)
        if not entry:
            return
        self._library_selected_id = entry_id

        # 评级 / 标签
        self.lib_rating_var.set(entry.rating)
        self.lib_tags_var.set(", ".join(entry.tags))

        # 详情文本
        import json as _json
        params_str = _json.dumps(entry.params, ensure_ascii=False, indent=2) if entry.params else "(none)"
        body = (
            f"# Image\n{entry.image_path}\n\n"
            f"# Created\n{entry.created_at}\n\n"
            f"# Generator\n{entry.generator_type}\n\n"
            f"# Batch\n{entry.source_batch_id or '-'}\n\n"
            f"# Notes\n{entry.notes or '-'}\n\n"
            f"# Params\n{params_str}\n\n"
            f"# Prompt\n{entry.prompt}\n"
        )
        self.lib_detail_text.config(state=tk.NORMAL)
        self.lib_detail_text.delete("1.0", tk.END)
        self.lib_detail_text.insert("1.0", body)
        self.lib_detail_text.config(state=tk.DISABLED)

        # 图片预览
        self._library_preview_photo = None
        self.lib_preview_label.config(image="", text=self.t("No preview image"))
        if entry.image_path and os.path.exists(entry.image_path):
            try:
                img = Image.open(entry.image_path)
                img.thumbnail((380, 380))
                self._library_preview_photo = ImageTk.PhotoImage(img)
                self.lib_preview_label.config(image=self._library_preview_photo, text="")
            except Exception as e:
                self.lib_preview_label.config(text=f"(preview failed: {e})")

    def _library_save_rating(self):
        if self._library_selected_id is None:
            return
        self._library_module.update_rating(self._library_selected_id, int(self.lib_rating_var.get()))
        # 仅刷新当前行的星级显示
        iid = str(self._library_selected_id)
        if self.lib_tree.exists(iid):
            vals = list(self.lib_tree.item(iid, "values"))
            r = int(self.lib_rating_var.get())
            vals[3] = "★" * r + "·" * (5 - r)
            self.lib_tree.item(iid, values=vals)

    def _library_save_tags(self):
        if self._library_selected_id is None:
            return
        raw = self.lib_tags_var.get()
        tags = [t.strip() for t in raw.replace("，", ",").split(",") if t.strip()]
        self._library_module.update_tags(self._library_selected_id, tags)

    def _library_copy_prompt(self):
        if self._library_selected_id is None:
            return
        entry = self._library_module.get_entry(self._library_selected_id)
        if not entry or not entry.prompt:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(entry.prompt)
        self.status_var.set(self.t("Prompt copied to clipboard!"))

    def _library_open_folder(self):
        if self._library_selected_id is None:
            return
        entry = self._library_module.get_entry(self._library_selected_id)
        if not entry or not entry.image_path:
            return
        target = entry.image_path
        if not os.path.exists(target):
            messagebox.showinfo(self.t("Info"), self.t("File no longer exists."))
            return
        # Windows: explorer /select,<path>
        try:
            import subprocess
            if os.name == "nt":
                subprocess.Popen(["explorer", "/select,", os.path.normpath(target)])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(target)])
        except Exception as e:
            messagebox.showerror(self.t("Error"), str(e))

    def _library_edit_with_gemini(self):
        """从作品库选中条目加载图片到主预览区，并打开改图对话框。
        编辑结果走原有保存流程，会作为新条目入库，batch_id='edit:<原id>' 留作演变链索引。"""
        if self._library_selected_id is None:
            return
        entry = self._library_module.get_entry(self._library_selected_id)
        if not entry:
            return
        if not entry.image_path or not os.path.exists(entry.image_path):
            messagebox.showerror(self.t("Error"), self.t("File no longer exists."))
            return
        _, api_key, _, _ = self._get_active_api_credentials()
        if not api_key:
            messagebox.showerror(self.t("Error"), self.t("API key is missing. Please add your key in Settings."))
            return

        # 读图片字节，写入主预览状态（复用 open_edit_dialog 的现有路径）
        try:
            with open(entry.image_path, "rb") as f:
                image_bytes = f.read()
        except Exception as e:
            messagebox.showerror(self.t("Error"), str(e))
            return
        mime = mimetypes.guess_type(entry.image_path)[0] or "image/png"

        self.pending_image_bytes = image_bytes
        self.pending_image_mime = mime
        self.pending_images = []
        self.edit_undo_stack.clear()
        # 编辑产物的 prefix 与父条目同类型，便于库里筛选
        self.pending_image_prefix = f"{entry.generator_type}_edit"
        # batch_id 编码父条目 id，将来可用此聚合演变链
        self.pending_batch_id = f"edit:{entry.id}"
        # 让主预览也显示一下这张图
        try:
            self.show_preview_image()
        except Exception:
            pass

        # 打开改图对话框，预填该条目的 prompt 作为初稿
        self.open_edit_dialog(initial_prompt=entry.prompt or "")

    def _library_delete(self):
        if self._library_selected_id is None:
            return
        if not messagebox.askyesno(self.t("Confirm"),
                                   self.t("Delete this library entry? (image file is kept on disk)")):
            return
        self._library_module.delete_entry(self._library_selected_id)
        self._library_selected_id = None
        self._library_refresh()
        self.lib_detail_text.config(state=tk.NORMAL)
        self.lib_detail_text.delete("1.0", tk.END)
        self.lib_detail_text.config(state=tk.DISABLED)
        self.lib_preview_label.config(image="", text=self.t("No preview image"))
        self._library_preview_photo = None

    def setup_settings_tab(self):
        parent = self._make_scrollable(self.tab_settings)

        ttk.Label(parent, text=self.t("Settings Panel"), font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # ── API Provider selector ──────────────────────────────────────────
        self.frame_provider = ttk.LabelFrame(parent, text=self.t("API Provider:"), padding=5)
        self.frame_provider.pack(fill=tk.X, pady=(0, 6))

        self.provider_var = tk.StringVar(value=self.api_provider)
        for prov in ("Gemini", "OpenAI"):
            ttk.Radiobutton(
                self.frame_provider, text=self.t(prov), variable=self.provider_var,
                value=prov, command=self._on_provider_changed,
            ).pack(side=tk.LEFT, padx=8)

        # ── Gemini section ────────────────────────────────────────────────
        self.frame_gemini = ttk.LabelFrame(parent, text="Gemini", padding=5)
        self.frame_gemini.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(self.frame_gemini, text=self.t("Gemini API Key:")).grid(row=0, column=0, sticky="w")
        self.api_key_var = tk.StringVar(value=self.gemini_api_key)
        ttk.Entry(self.frame_gemini, textvariable=self.api_key_var, show="").grid(
            row=0, column=1, sticky="ew", padx=(5, 0))

        ttk.Label(self.frame_gemini, text=self.t("Gemini Model:")).grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.model_var = tk.StringVar(value=self.gemini_model)
        gemini_model_options = list(gs.IMAGE_MODELS)
        cur_gm = self.gemini_model.replace("models/", "")
        if cur_gm and cur_gm not in gemini_model_options:
            gemini_model_options.insert(0, cur_gm)
        self.model_combo = ttk.Combobox(
            self.frame_gemini, textvariable=self.model_var,
            values=gemini_model_options, state="readonly")
        self.model_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))

        self.frame_gemini.columnconfigure(1, weight=1)

        # ── OpenAI section ────────────────────────────────────────────────
        self.frame_openai = ttk.LabelFrame(parent, text="OpenAI", padding=5)
        self.frame_openai.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(self.frame_openai, text=self.t("OpenAI API Key:")).grid(row=0, column=0, sticky="w")
        self.openai_key_var = tk.StringVar(value=self.openai_api_key)
        ttk.Entry(self.frame_openai, textvariable=self.openai_key_var, show="").grid(
            row=0, column=1, sticky="ew", padx=(5, 0))

        ttk.Label(self.frame_openai, text=self.t("OpenAI Base URL:")).grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.openai_url_var = tk.StringVar(value=self.openai_base_url)
        ttk.Entry(self.frame_openai, textvariable=self.openai_url_var).grid(
            row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))

        ttk.Label(self.frame_openai, text=self.t("OpenAI Model:")).grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.openai_model_var = tk.StringVar(value=self.openai_model)
        openai_model_options = list(oi.ALL_MODELS)
        cur_om = self.openai_model
        if cur_om and cur_om not in openai_model_options:
            openai_model_options.insert(0, cur_om)
        self.openai_model_combo = ttk.Combobox(
            self.frame_openai, textvariable=self.openai_model_var,
            values=openai_model_options, state="readonly")
        self.openai_model_combo.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))

        ttk.Label(self.frame_openai, text=self.t("Image Size:")).grid(row=3, column=0, sticky="w", pady=(5, 0))
        self.openai_size_var = tk.StringVar(value=self.openai_image_size)
        self.openai_size_combo = ttk.Combobox(
            self.frame_openai, textvariable=self.openai_size_var,
            values=oi.SIZES_GPT_IMAGE, state="readonly")
        self.openai_size_combo.grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))

        ttk.Label(self.frame_openai, text=self.t("Image Quality:")).grid(row=4, column=0, sticky="w", pady=(5, 0))
        self.openai_quality_var = tk.StringVar(value=self.openai_image_quality)
        self.openai_quality_combo = ttk.Combobox(
            self.frame_openai, textvariable=self.openai_quality_var,
            values=oi.QUALITY_OPTIONS, state="readonly")
        self.openai_quality_combo.grid(row=4, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))

        self.frame_openai.columnconfigure(1, weight=1)

        # Apply initial visibility
        self._on_provider_changed()
        
        # Output directory (global default)
        frame_out = ttk.LabelFrame(parent, text=self.t("Image Save Directory:"), padding=5)
        frame_out.pack(fill=tk.X, pady=(0, 10))
        
        self.save_dir_var = tk.StringVar(value=self.image_save_dir)
        ttk.Entry(frame_out, textvariable=self.save_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(frame_out, text=self.t("Browse..."), command=self.select_save_dir).pack(side=tk.LEFT, padx=(5, 0))

        # Per-tab output directories
        frame_tab_dirs = ttk.LabelFrame(parent, text=self.t("Per-Tab Output Directories"), padding=5)
        frame_tab_dirs.pack(fill=tk.X, pady=(0, 10))
        frame_tab_dirs.columnconfigure(1, weight=1)

        tab_dir_defs = [
            ("Spaceship Dir:", "spaceship_save_dir_var", self.spaceship_save_dir, self._select_spaceship_dir),
            ("Item Icons Dir:", "items_save_dir_var", self.items_save_dir, self._select_items_dir),
            ("Character Dir:", "character_save_dir_var", self.character_save_dir, self._select_character_dir),
            ("Clothing Dir:", "clothing_save_dir_var", self.clothing_save_dir, self._select_clothing_dir),
        ]
        for row_idx, (label_key, var_attr, default_val, browse_cmd) in enumerate(tab_dir_defs):
            ttk.Label(frame_tab_dirs, text=self.t(label_key)).grid(row=row_idx, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=default_val)
            setattr(self, var_attr, var)
            ttk.Entry(frame_tab_dirs, textvariable=var).grid(row=row_idx, column=1, sticky="ew", padx=(5, 5), pady=2)
            ttk.Button(frame_tab_dirs, text=self.t("Browse..."), command=browse_cmd).grid(row=row_idx, column=2, pady=2)
        
        # Language
        frame_lang = ttk.LabelFrame(parent, text=self.t("UI Language:"), padding=5)
        frame_lang.pack(fill=tk.X, pady=(0, 10))
        
        self.lang_var = tk.StringVar(value=self.t("Chinese") if self.ui_lang == "zh" else self.t("English"))
        lang_combo = ttk.Combobox(frame_lang, textvariable=self.lang_var, state="readonly")
        lang_combo["values"] = [self.t("English"), self.t("Chinese")]
        lang_combo.pack(fill=tk.X)

        frame_hair_preview = ttk.LabelFrame(parent, text=self.t("Hair Preview Settings"), padding=5)
        frame_hair_preview.pack(fill=tk.X, pady=(0, 10))
        frame_hair_preview.columnconfigure(1, weight=1)

        ttk.Label(frame_hair_preview, text=self.t("Select Hair Style:")).grid(row=0, column=0, sticky="w")
        self.hair_preview_style_var = tk.StringVar()
        hair_preview_options = cg.get_hair_style_options(self.ui_lang)
        if hair_preview_options:
            self.hair_preview_style_var.set(hair_preview_options[0])
        self.hair_preview_style_combo = ttk.Combobox(
            frame_hair_preview,
            textvariable=self.hair_preview_style_var,
            state="readonly",
        )
        self.hair_preview_style_combo["values"] = hair_preview_options
        self.hair_preview_style_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.hair_style_preview_canvas = tk.Canvas(
            frame_hair_preview,
            background="#eeeeee",
            highlightthickness=0,
            width=240,
            height=200,
        )
        self.hair_style_preview_canvas.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 4))

        hair_preview_btns = ttk.Frame(frame_hair_preview)
        hair_preview_btns.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(hair_preview_btns, text=self.t("Set Preview Image"), command=self.set_hair_style_preview).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4)
        )
        ttk.Button(hair_preview_btns, text=self.t("Clear Preview"), command=self.clear_hair_style_preview).pack(
            side=tk.LEFT, expand=True, fill=tk.X
        )

        self.hair_preview_style_var.trace_add("write", lambda *_: self.update_hair_style_preview())
        self.update_hair_style_preview()
        
        ttk.Button(parent, text=self.t("Save Settings"), command=self.save_settings).pack(fill=tk.X, pady=(10, 0), ipady=6)

    def setup_slicer_tab(self):
        parent = self._make_scrollable(self.tab_slicer)
        
        ttk.Label(parent, text=self.t("Image Slicer (8x8 Grid)"), font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 5))
        
        # ===== Section 1: Input =====
        ttk.Label(parent, text=self.t("1. Select Grid Image(s):"), font=("Arial", 10, "bold")).pack(anchor="w")
        frame_img_btns = ttk.Frame(parent)
        frame_img_btns.pack(fill=tk.X, pady=(3, 3))
        ttk.Button(frame_img_btns, text=self.t("Select Image File(s)..."), command=self.select_images_for_slicer).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        ttk.Button(frame_img_btns, text=self.t("Select Folder (Batch)..."), command=self.select_folder_for_slicer).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))
        self.lbl_selected_file = ttk.Label(parent, text=self.t("No file selected"), foreground="gray", wraplength=400)
        self.lbl_selected_file.pack(anchor="w", pady=(0, 5))
        
        # ===== Section 2: Output Directory =====
        ttk.Label(parent, text=self.t("2. Output Directory:"), font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(parent, text=self.t("(Leave empty: each image creates its own subfolder)"), foreground="gray").pack(anchor="w")
        frame_outdir = ttk.Frame(parent)
        frame_outdir.pack(fill=tk.X, pady=(3, 5))
        self.var_slicer_outdir = tk.StringVar(value="")
        ttk.Entry(frame_outdir, textvariable=self.var_slicer_outdir).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(frame_outdir, text=self.t("Browse..."), command=self.browse_slicer_outdir, width=8).pack(side=tk.LEFT)
        
        # ===== Section 3: Grid Config =====
        frame_config = ttk.LabelFrame(parent, text=self.t("Advanced Configuration"), padding=5)
        frame_config.pack(fill=tk.X, pady=3)

        # Row 1: Grid size + norm scale
        frame_config_row1 = ttk.Frame(frame_config)
        frame_config_row1.pack(fill=tk.X)
        self.lbl_grid_size = ttk.Label(frame_config_row1, text=self.t("Grid Size (Row x Col):"))
        self.lbl_grid_size.pack(side=tk.LEFT)
        self.var_grid_size = tk.StringVar(value="8")
        self.entry_grid_size = ttk.Entry(frame_config_row1, textvariable=self.var_grid_size, width=5)
        self.entry_grid_size.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_config_row1, text=self.t("Norm Scale (0.1-1.0):")).pack(side=tk.LEFT, padx=(10, 0))
        self.var_scale_factor = tk.DoubleVar(value=0.85)
        ttk.Entry(frame_config_row1, textvariable=self.var_scale_factor, width=5).pack(side=tk.LEFT, padx=5)

        # Row 2: Smart crop toggle
        frame_config_row2 = ttk.Frame(frame_config)
        frame_config_row2.pack(fill=tk.X, pady=(4, 0))
        self.var_smart_crop = tk.BooleanVar(value=False)
        self.cb_smart_crop = ttk.Checkbutton(
            frame_config_row2,
            text=self.t("Smart Crop (auto-detect grid)") + "  " + self.t("(overrides row/col input)"),
            variable=self.var_smart_crop,
            command=self._toggle_smart_crop
        )
        self.cb_smart_crop.pack(side=tk.LEFT)
        
        # ===== Section 4: Naming =====
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=3)
        ttk.Label(parent, text=self.t("3. Naming Options:"), font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Rename (top priority)
        frame_rename = ttk.Frame(parent)
        frame_rename.pack(fill=tk.X, pady=(3, 0))
        ttk.Label(frame_rename, text=self.t("Rename:")).pack(side=tk.LEFT)
        self.var_rename = tk.StringVar(value="")
        ttk.Entry(frame_rename, textvariable=self.var_rename, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_rename, text=self.t("(overrides CSV naming if filled)"), foreground="gray").pack(side=tk.LEFT)
        
        # Auto suffix checkbox (for batch: adds image-level number)
        self.var_auto_suffix = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text=self.t("Batch auto suffix (e.g. weapon_01_01, weapon_02_01)"), variable=self.var_auto_suffix).pack(anchor="w", padx=(20, 0), pady=(1, 0))
        
        # CSV Smart Naming (lower priority)
        self.var_use_csv_naming = tk.BooleanVar(value=True)
        cb_naming = ttk.Checkbutton(parent, text=self.t("Use CSV for Filenames (Smart Naming)"), variable=self.var_use_csv_naming, command=self.toggle_smart_naming)
        cb_naming.pack(anchor="w", pady=(3, 0))
        
        self.var_translate_filename = tk.BooleanVar(value=True)
        self.cb_trans_file = ttk.Checkbutton(parent, text=self.t("Auto-Translate Filenames (ZH -> EN)"), variable=self.var_translate_filename)
        self.cb_trans_file.pack(anchor="w", padx=(20, 0))
        
        self.cb_cache_file = ttk.Checkbutton(parent, text=self.t("Write Translation Result into CSV (Cache)"), variable=self.var_cache_translation)
        self.cb_cache_file.pack(anchor="w", padx=(20, 0), pady=(1,0))
        
        frame_csv = ttk.Frame(parent)
        frame_csv.pack(fill=tk.X, pady=(3, 0))
        self.btn_select_csv = ttk.Button(frame_csv, text=self.t("Select CSV..."), command=self.select_csv_for_slicer, width=15)
        self.btn_select_csv.pack(side=tk.LEFT)
        self.lbl_selected_csv = ttk.Label(frame_csv, text=os.path.basename(self.slicer_csv_path), foreground="blue")
        self.lbl_selected_csv.pack(side=tk.LEFT, padx=5)
        
        # ===== Section 5: Processing Options =====
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=3)
        ttk.Label(parent, text=self.t("4. Processing Options:"), font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.var_remove_bg = tk.BooleanVar(value=False)
        self.var_normalize = tk.BooleanVar(value=False)
        
        venv_exists = False
        import sys
        if getattr(sys, 'frozen', False):
             base_dir = os.path.dirname(sys.executable)
             if os.path.exists(os.path.join(base_dir, "worker_rembg.exe")):
                 venv_exists = True
        if not venv_exists:
            try:
                workspace_dir = os.getcwd()
                venv_python = os.path.join(workspace_dir, ".venv_rembg", "Scripts", "python.exe")
                if os.path.exists(venv_python):
                    venv_exists = True
            except:
                pass

        bg_text = self.t("Remove Background")
        if not venv_exists:
            bg_text += " " + self.t("[Setup Required]")
        self.cb_remove_bg = ttk.Checkbutton(parent, text=bg_text, variable=self.var_remove_bg)
        self.cb_remove_bg.pack(anchor="w", pady=(3, 0))
        self.cb_remove_bg.config(state=tk.NORMAL)

        self.cb_normalize = ttk.Checkbutton(parent, text=self.t("Normalize Size & Position (Trim & Center 90%)"), variable=self.var_normalize)
        self.cb_normalize.pack(anchor="w", pady=(1, 0))
        
        # ===== Preview & Action =====
        self.lbl_preview = ttk.Label(parent, text="[Preview]", background="#eeeeee", anchor="center")
        self.lbl_preview.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.btn_slice = ttk.Button(parent, text=self.t("SLICE INTO 64 ICONS"), command=self.run_slicer_threaded, state=tk.DISABLED)
        self.btn_slice.pack(fill=tk.X, pady=(5, 0), ipady=10)

    def _toggle_smart_crop(self):
        """Enable/disable the manual grid size entry based on smart crop checkbox."""
        if self.var_smart_crop.get():
            self.entry_grid_size.config(state=tk.DISABLED)
            self.lbl_grid_size.config(foreground="gray")
        else:
            self.entry_grid_size.config(state=tk.NORMAL)
            self.lbl_grid_size.config(foreground="")

    def setup_curation_tab(self):
        parent = self.tab_curation
        
        # Main Layout: Sidebar (Config) | Main (View)
        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        sidebar = ttk.Frame(paned, padding=(0, 0, 10, 0))
        main_view = ttk.Frame(paned)
        
        paned.add(sidebar, minsize=250)
        paned.add(main_view)
        
        # --- Sidebar ---
        ttk.Label(sidebar, text=self.t("Configuration"), font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Target Folder
        ttk.Label(sidebar, text=self.t("Target Folder (Output):")).pack(anchor="w")
        self.curation_target_var = tk.StringVar()
        self.entry_curation_target = ttk.Entry(sidebar, textvariable=self.curation_target_var)
        self.entry_curation_target.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(sidebar, text=self.t("Browse Target..."), command=self.browse_curation_target).pack(anchor="e")
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)
        
        # Source Folders
        ttk.Label(sidebar, text=self.t("Source Folders (Inputs):")).pack(anchor="w")
        
        list_frame = ttk.Frame(sidebar)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.lst_sources = tk.Listbox(list_frame, height=8)
        self.lst_sources.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.lst_sources.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.lst_sources.config(yscrollcommand=sb.set)
        
        btn_frame = ttk.Frame(sidebar)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text=self.t("+ Add Batch (Select Files)"), command=self.add_source_folder_batch).pack(fill=tk.X, pady=(0, 2))
        
        btn_row2 = ttk.Frame(btn_frame)
        btn_row2.pack(fill=tk.X)
        ttk.Button(btn_row2, text=self.t("+ Add Folder"), command=self.add_source_folder_single).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,1))
        ttk.Button(btn_row2, text=self.t("- Remove"), command=self.remove_source_folder).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(1,0))
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)
        
        # Controls
        self.lbl_curation_status = ttk.Label(sidebar, text=self.t("Ready"), wraplength=200)
        self.lbl_curation_status.pack(anchor="w", pady=(0, 10))
        
        self.btn_start_curation = ttk.Button(sidebar, text=self.t("START SESSION"), command=self.start_curation_session, width=20)
        self.btn_start_curation.pack(fill=tk.X, ipady=5)
        
        # --- Main View (Comparison) ---
        self.frame_comparison = ttk.Frame(main_view)
        self.frame_comparison.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.lbl_compare_info = ttk.Label(self.frame_comparison, text=self.t("Waiting to start..."), font=("Arial", 14))
        self.lbl_compare_info.pack(pady=10)
        
        # Image Grid Container (Scrollable)
        canvas_container = ttk.Frame(self.frame_comparison)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_comp = tk.Canvas(canvas_container)
        self.scroll_comp = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas_comp.yview)
        self.frame_comp_inner = ttk.Frame(self.canvas_comp)
        
        self.frame_comp_inner.bind(
            "<Configure>",
            lambda e: self.canvas_comp.configure(scrollregion=self.canvas_comp.bbox("all"))
        )
        
        self.canvas_comp.create_window((0, 0), window=self.frame_comp_inner, anchor="nw")
        self.canvas_comp.configure(yscrollcommand=self.scroll_comp.set)
        
        self.canvas_comp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll_comp.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom Controls
        self.btn_curation_skip = ttk.Button(self.frame_comparison, text=self.t("Skip / Discard All"), command=self.skip_curation_item, state=tk.DISABLED)
        self.btn_curation_skip.pack(pady=10)
        
        # Bind Keys
        self.root.bind("<Key>", self.handle_curation_keypress)

    def browse_curation_target(self):
        path = filedialog.askdirectory(title=self.t("Select Target Folder"))
        if path:
            self.curation_target_var.set(path)

    def add_source_folder_batch(self):
        # Workaround for multi-folder select: Ask for files
        filepaths = filedialog.askopenfilenames(title=self.t("Select ANY file inside the source folder(s) - Ctrl+Click to select multiple folders"))
        if filepaths:
            current_list = self.lst_sources.get(0, tk.END)
            for fp in filepaths:
                folder = os.path.dirname(fp)
                if folder not in current_list:
                    self.lst_sources.insert(tk.END, folder)
                    current_list = self.lst_sources.get(0, tk.END) # Update local ref
            self.lst_sources.see(tk.END)

    def add_source_folder_single(self):
        path = filedialog.askdirectory(title=self.t("Select Source Folder"))
        if path:
            if path not in self.lst_sources.get(0, tk.END):
                self.lst_sources.insert(tk.END, path)
                self.lst_sources.see(tk.END)

    def remove_source_folder(self):
        selection = self.lst_sources.curselection()
        if selection:
            self.lst_sources.delete(selection[0])

    def start_curation_session(self):
        sources = self.lst_sources.get(0, tk.END)
        target = self.curation_target_var.get()
        
        if not sources:
            messagebox.showerror(self.t("Error"), self.t("Please add at least one source folder."))
            return
        if not target:
            messagebox.showerror(self.t("Error"), self.t("Please select a target folder."))
            return
            
        # Configure Backend
        self.curator.set_config(list(sources), target)
        
        # Scan
        total, conflicts = self.curator.scan_files()
        
        # Auto-resolve uniques
        auto_count = self.curator.auto_resolve_uniques()
        
        msg = self.t("Scan Complete.\nTotal Files: {total}\nAuto-Resolved (Unique): {auto}\nConflicts to Review: {conflicts}").format(
            total=total, auto=auto_count, conflicts=conflicts
        )
        messagebox.showinfo(self.t("Session Started"), msg)
        
        # Setup Queue
        self.curation_queue = self.curator.get_pending_conflicts()
        self.current_curation_index = 0
        
        self.load_next_curation_item()

    def load_next_curation_item(self):
        if self.current_curation_index >= len(self.curation_queue):
            # Done
            self.lbl_compare_info.config(text=self.t("Session Complete! All items resolved."))
            for widget in self.frame_comp_inner.winfo_children(): widget.destroy()
            self.btn_curation_skip.config(state=tk.DISABLED)
            return
            
        filename = self.curation_queue[self.current_curation_index]
        variants = self.curator.get_variants(filename)
        
        # Update Header
        progress = f"({self.current_curation_index + 1}/{len(self.curation_queue)})"
        self.lbl_compare_info.config(text=f"{progress} Comparing: {filename}")
        self.btn_curation_skip.config(state=tk.NORMAL)
        
        # Clear Display
        for widget in self.frame_comp_inner.winfo_children(): widget.destroy()
        
        # Display Grid logic
        # Max columns = 3 (Fits nicely in 850px width: 3 * (180+20) = 600px, leaving room)
        COL_LIMIT = 3
        
        # Keep references to images so garbage collector doesn't eat them
        self.curation_images = []
        
        for i, path in enumerate(variants):
            row = i // COL_LIMIT
            col = i % COL_LIMIT
            
            frame_item = ttk.Frame(self.frame_comp_inner, borderwidth=2, relief="groove", padding=5)
            frame_item.grid(row=row, column=col, padx=10, pady=10)
            
            try:
                img = Image.open(path)
                # Resize to fit nicely (180x180 max)
                img.thumbnail((180, 180)) 
                photo = ImageTk.PhotoImage(img)
                self.curation_images.append(photo)
                
                # Image Button
                btn_img = tk.Button(frame_item, image=photo, command=lambda p=path: self.select_curation_item(filename, p))
                btn_img.pack()
                
                # Label
                hotkey = str(i + 1)
                lbl = ttk.Label(frame_item, text=f"[{hotkey}] Source {i+1}", font=("Arial", 10, "bold"))
                lbl.pack(pady=(5,0))
                
                # Source path tooltip/label (truncated)
                src_folder = os.path.basename(os.path.dirname(path))
                ttk.Label(frame_item, text=src_folder, foreground="gray").pack()
                
            except Exception as e:
                ttk.Label(frame_item, text=self.t("Error loading image")).pack()
                
        # Update layout
        self.frame_comp_inner.update_idletasks()
        self.canvas_comp.configure(scrollregion=self.canvas_comp.bbox("all"))

    def select_curation_item(self, filename, path):
        # Commit to backend
        success = self.curator.commit_selection(filename, path)
        if success:
            self.current_curation_index += 1
            self.load_next_curation_item()
        else:
            messagebox.showerror(self.t("Error"), self.t("Failed to copy file."))

    def skip_curation_item(self):
        filename = self.curation_queue[self.current_curation_index]
        self.curator.skip_file(filename)
        self.current_curation_index += 1
        self.load_next_curation_item()
        
    def handle_curation_keypress(self, event):
        # Only active if Curation tab is selected
        if self.notebook.select() != str(self.tab_curation):
            return
            
        if not self.curation_queue or self.current_curation_index >= len(self.curation_queue):
            return
            
        key = event.char
        if key in "123456789":
            idx = int(key) - 1
            filename = self.curation_queue[self.current_curation_index]
            variants = self.curator.get_variants(filename)
            
            if 0 <= idx < len(variants):
                self.select_curation_item(filename, variants[idx])

    def select_style_reference_image(self):
        filepaths = filedialog.askopenfilenames(
            title=self.t("Select Style Image..."),
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")],
        )
        if not filepaths:
            return
        paths = list(filepaths)
        blobs = []
        try:
            for filepath in paths:
                with open(filepath, "rb") as f:
                    image_bytes = f.read()
                mime_type = mimetypes.guess_type(filepath)[0] or "image/png"
                blobs.append((image_bytes, mime_type))
        except Exception:
            messagebox.showerror(self.t("Error"), self.t("Failed to read style image."))
            return
        self.style_ref_paths = paths
        self.style_ref_blobs = blobs
        if len(paths) == 1:
            display_name = os.path.basename(paths[0])
            label_text = self.t("Style image selected: {name}").format(name=display_name)
        else:
            label_text = self.t("Style images selected: {count}").format(count=len(paths))
        self.lbl_style_ref.config(text=label_text, foreground="black")
        self.chk_style_ref_only.config(state=tk.NORMAL)
        self.schedule_character_prompt_update()

    def clear_style_reference_image(self):
        self.style_ref_paths = []
        self.style_ref_blobs = []
        self.lbl_style_ref.config(text=self.t("No style image selected"), foreground="gray")
        self.style_ref_only_mode.set(False)
        self.chk_style_ref_only.config(state=tk.DISABLED)
        self.schedule_character_prompt_update()
                
    def select_images_for_slicer(self):
        filepaths = filedialog.askopenfilenames(title=self.t("Select Sprite Sheets"), filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if filepaths:
            self.slicer_files = list(filepaths)
            count = len(self.slicer_files)
            if count == 1:
                display = os.path.basename(self.slicer_files[0])
            else:
                display = self.t("{count} files selected").format(count=count)
                
            self.selected_image_path = self.slicer_files[0] # Compat
            self.lbl_selected_file.config(text=display, foreground="black")
            self.btn_slice.config(state=tk.NORMAL)
            
            # Show Preview
            try:
                img = Image.open(filepath)
                # Resize for preview (keep aspect ratio)
                img.thumbnail((300, 300))
                self.preview_image = ImageTk.PhotoImage(img) # Keep ref
                self.lbl_preview.config(image=self.preview_image, text="")
            except Exception as e:
                self.lbl_preview.config(text=f"Error loading preview: {e}", image="")
    
    def browse_slicer_outdir(self):
        path = filedialog.askdirectory(title=self.t("Output Directory:"))
        if path:
            self.var_slicer_outdir.set(path)

    def select_folder_for_slicer(self):
        folder = filedialog.askdirectory(title=self.t("Select Folder (Batch)..."))
        if folder:
            valid_ext = ('.png', '.jpg', '.jpeg', '.webp')
            files = sorted([
                os.path.join(folder, f) for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(valid_ext)
            ])
            if not files:
                messagebox.showwarning(self.t("Error"), self.t("No image files found in the selected folder."))
                return
            self.slicer_files = files
            count = len(files)
            display = self.t("{count} files selected").format(count=count)
            self.selected_image_path = files[0]
            self.lbl_selected_file.config(text=display, foreground="black")
            self.btn_slice.config(state=tk.NORMAL)
            try:
                img = Image.open(files[0])
                img.thumbnail((300, 300))
                self.preview_image = ImageTk.PhotoImage(img)
                self.lbl_preview.config(image=self.preview_image, text="")
            except Exception as e:
                self.lbl_preview.config(text=f"Error loading preview: {e}", image="")

    def select_csv_for_slicer(self):
        filepath = filedialog.askopenfilename(title=self.t("Select Naming CSV"), filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.slicer_csv_path = filepath
            self.lbl_selected_csv.config(text=os.path.basename(filepath))

    def select_csv_for_item(self):
        filepath = filedialog.askopenfilename(title=self.t("Select Item CSV"), filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.item_csv_path = filepath
            self.lbl_selected_item_csv.config(text=os.path.basename(filepath))

    def select_save_dir(self):
        path = filedialog.askdirectory(title=self.t("Image Save Directory:"))
        if path:
            self.save_dir_var.set(path)

    def _select_spaceship_dir(self):
        path = filedialog.askdirectory(title=self.t("Spaceship Dir:"))
        if path:
            self.spaceship_save_dir_var.set(path)

    def _select_items_dir(self):
        path = filedialog.askdirectory(title=self.t("Item Icons Dir:"))
        if path:
            self.items_save_dir_var.set(path)

    def _select_character_dir(self):
        path = filedialog.askdirectory(title=self.t("Character Dir:"))
        if path:
            self.character_save_dir_var.set(path)

    def _select_clothing_dir(self):
        path = filedialog.askdirectory(title=self.t("Clothing Dir:"))
        if path:
            self.clothing_save_dir_var.set(path)

    def _get_current_save_dir(self) -> str:
        """Return the save directory for the current active tab, falling back to global dir.
        For spaceship tab, appends a subfolder named after the component category."""
        global_dir = (self.save_dir_var.get().strip() if hasattr(self, "save_dir_var") else self.image_save_dir) or "outputs"
        current = self.notebook.select()

        if current == str(self.tab_spaceship):
            tab_dir = (self.spaceship_save_dir_var.get().strip() if hasattr(self, "spaceship_save_dir_var") else self.spaceship_save_dir)
            base = tab_dir or global_dir
            cat = self.category_var.get().strip().lower() if hasattr(self, "category_var") else ""
            if cat:
                return os.path.join(base, cat)
            return base
        elif current == str(self.tab_items):
            tab_dir = (self.items_save_dir_var.get().strip() if hasattr(self, "items_save_dir_var") else self.items_save_dir)
            return tab_dir or global_dir
        elif current == str(self.tab_characters):
            tab_dir = (self.character_save_dir_var.get().strip() if hasattr(self, "character_save_dir_var") else self.character_save_dir)
            return tab_dir or global_dir
        elif current == str(self.tab_clothing):
            tab_dir = (self.clothing_save_dir_var.get().strip() if hasattr(self, "clothing_save_dir_var") else self.clothing_save_dir)
            return tab_dir or global_dir
        return global_dir

    def _on_provider_changed(self):
        """Show/hide Gemini / OpenAI config sections based on selected provider."""
        provider = self.provider_var.get() if hasattr(self, "provider_var") else self.api_provider
        if provider == "OpenAI":
            self.frame_gemini.pack_forget()
            self.frame_openai.pack(fill=tk.X, pady=(0, 6))
        else:
            self.frame_openai.pack_forget()
            self.frame_gemini.pack(fill=tk.X, pady=(0, 6))

    def _get_active_api_credentials(self):
        """Return (provider, key, model, extra_kwargs) for the active API provider."""
        provider = self.provider_var.get() if hasattr(self, "provider_var") else self.api_provider
        if provider == "OpenAI":
            key = self.openai_key_var.get().strip() if hasattr(self, "openai_key_var") else self.openai_api_key
            model = self.openai_model_var.get().strip() if hasattr(self, "openai_model_var") else self.openai_model
            base_url = self.openai_url_var.get().strip() if hasattr(self, "openai_url_var") else self.openai_base_url
            size = self.openai_size_var.get() if hasattr(self, "openai_size_var") else self.openai_image_size
            quality = self.openai_quality_var.get() if hasattr(self, "openai_quality_var") else self.openai_image_quality
            return "OpenAI", key, model, {"base_url": base_url or oi.DEFAULT_BASE_URL, "size": size, "quality": quality}
        else:
            key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
            model = self.model_var.get().strip() if hasattr(self, "model_var") else self.gemini_model
            return "Gemini", key, model, {}

    def _generate_image_with_active_provider(self, prompt, reference_images=None, text_last=False):
        """Route image generation to Gemini or OpenAI based on current settings."""
        provider, key, model, extra = self._get_active_api_credentials()
        if not key:
            raise ValueError("API key is missing.")
        if provider == "OpenAI":
            return oi.generate_image_bytes(
                prompt, api_key=key, model=model,
                reference_images=reference_images or [], **extra,
            )
        else:
            return gs.generate_image_bytes(
                prompt, api_key=key, model=model,
                reference_images=reference_images if reference_images else None,
                text_last=text_last,
            )

    def _edit_image_with_active_provider(self, prompt, image_bytes, image_mime):
        """Route image editing to Gemini or OpenAI based on current settings."""
        provider, key, model, extra = self._get_active_api_credentials()
        if not key:
            raise ValueError("API key is missing.")
        if provider == "OpenAI":
            return oi.edit_image_bytes(prompt, image_bytes, image_mime, api_key=key, model=model, **extra)
        else:
            return gs.edit_image_bytes(prompt, image_bytes, image_mime, api_key=key, model=model)

    def save_settings(self):
        previous_lang = self.ui_lang
        selected_lang = "zh" if self.lang_var.get() == self.t("Chinese") else "en"

        self.api_provider = self.provider_var.get() if hasattr(self, "provider_var") else self.api_provider
        self.gemini_api_key = self.api_key_var.get().strip()
        self.gemini_model = self.model_var.get().strip() or gs.DEFAULT_MODEL
        self.openai_api_key = self.openai_key_var.get().strip() if hasattr(self, "openai_key_var") else self.openai_api_key
        self.openai_base_url = self.openai_url_var.get().strip() if hasattr(self, "openai_url_var") else self.openai_base_url
        self.openai_model = self.openai_model_var.get().strip() if hasattr(self, "openai_model_var") else self.openai_model
        self.openai_image_size = self.openai_size_var.get() if hasattr(self, "openai_size_var") else self.openai_image_size
        self.openai_image_quality = self.openai_quality_var.get() if hasattr(self, "openai_quality_var") else self.openai_image_quality
        self.image_save_dir = self.save_dir_var.get().strip() or "outputs"
        self.spaceship_save_dir = self.spaceship_save_dir_var.get().strip()
        self.items_save_dir = self.items_save_dir_var.get().strip()
        self.character_save_dir = self.character_save_dir_var.get().strip()
        self.clothing_save_dir = self.clothing_save_dir_var.get().strip()

        self.ui_lang = selected_lang

        data = {
            "api_provider": self.api_provider,
            "gemini_api_key": self.gemini_api_key,
            "gemini_model": self.gemini_model,
            "openai_api_key": self.openai_api_key,
            "openai_base_url": self.openai_base_url,
            "openai_model": self.openai_model,
            "openai_image_size": self.openai_image_size,
            "openai_image_quality": self.openai_image_quality,
            "image_save_dir": self.image_save_dir,
            "spaceship_save_dir": self.spaceship_save_dir,
            "items_save_dir": self.items_save_dir,
            "character_save_dir": self.character_save_dir,
            "clothing_save_dir": self.clothing_save_dir,
            "language": selected_lang,
        }

        if self.save_config(data):
            if previous_lang != selected_lang:
                messagebox.showinfo(self.t("Settings"), self.t("Settings saved. Restart the app to apply language changes."))
            else:
                messagebox.showinfo(self.t("Settings"), self.t("Settings saved."))
        else:
            messagebox.showerror(self.t("Error"), self.t("Failed to save settings."))

    def toggle_smart_naming(self):
        if self.var_use_csv_naming.get():
            self.cb_trans_file.config(state=tk.NORMAL)
            self.cb_cache_file.config(state=tk.NORMAL)
            self.btn_select_csv.config(state=tk.NORMAL)
        else:
            self.cb_trans_file.config(state=tk.DISABLED)
            self.cb_cache_file.config(state=tk.DISABLED)
            self.btn_select_csv.config(state=tk.DISABLED)

    def set_ui_busy(self, busy=True, message=None):
        """Disable/Enable buttons and update status."""
        if message is None:
            message = self.t("Processing...")
        state = tk.DISABLED if busy else tk.NORMAL
        
        # Update Status
        self.status_var.set(message)
        self.root.update_idletasks() # Force update
        
        # Disable buttons
        self.btn_gen_items.config(state=state)
        # Slicer button only re-enables if image is selected, handle carefully
        if busy:
             self.btn_slice.config(state=tk.DISABLED)
        elif self.selected_image_path:
             self.btn_slice.config(state=tk.NORMAL)
        
        self.gen_btn.config(state=state)
        self.gen_image_btn.config(state=state)
        if busy:
            self.btn_edit_image.config(state=tk.DISABLED)
        elif self.pending_image_bytes:
            self.btn_edit_image.config(state=tk.NORMAL)

    def generate_item_prompt_threaded(self):
        self.set_ui_busy(True, self.t("Generating Prompt and Translating... (This may take a moment)"))
        # Run in thread
        threading.Thread(target=self._generate_item_prompt_task, daemon=True).start()

    def _generate_item_prompt_task(self):
        items = ig.read_items_from_csv(self.item_csv_path)
        if not items:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), self.t("Could not read items from CSV.")))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
            return
        
        do_translate = self.var_translate_prompt.get()
        do_cache = self.var_cache_translation.get()
        cache_path = self.item_csv_path if do_cache else None
        
        try:
            prompt = ig.generate_icon_grid_prompt(items, translate=do_translate, cache_path=cache_path)
            self.root.after(0, lambda: self.set_output(prompt))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Prompt Generated Successfully")))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))

    def run_slicer_threaded(self):
        # Ensure list exists
        if not hasattr(self, 'slicer_files') and hasattr(self, 'selected_image_path') and self.selected_image_path:
             self.slicer_files = [self.selected_image_path]
             
        if not hasattr(self, 'slicer_files') or not self.slicer_files:
            return
        
        self.set_ui_busy(True, self.t("Slicing Images... (Batch Processing)"))
        threading.Thread(target=self._run_slicer_task, daemon=True).start()

    def _run_slicer_task(self):
        csv_to_use = self.slicer_csv_path if self.var_use_csv_naming.get() else None
        do_translate = self.var_translate_filename.get()
        
        try:
            grid_size_str = self.var_grid_size.get()
            if 'x' in grid_size_str:
                parts = grid_size_str.split('x')
                rows = int(parts[0])
                cols = int(parts[1])
            else:
                rows = int(grid_size_str)
                cols = rows
        except:
            rows = 8
            cols = 8
            
        try:
             scale = self.var_scale_factor.get()
        except:
             scale = 0.85
        
        rename_str = self.var_rename.get().strip()
        auto_suffix = self.var_auto_suffix.get()
        out_dir = self.var_slicer_outdir.get().strip() or None
        
        total_files = len(self.slicer_files)
        use_smart_crop = self.var_smart_crop.get()
        cells_per_image = rows * cols

        if auto_suffix:
            num_digits = max(2, len(str(cells_per_image)), len(str(total_files)))
        else:
            num_digits = max(2, len(str(cells_per_image * total_files)))

        import uuid as _uuid
        batch_id = _uuid.uuid4().hex if total_files > 1 else None
        success_count = 0
        errors = []
        current_index = 1

        for i, fp in enumerate(self.slicer_files):
            self.status_var.set(f"{self.t('Processing...')} ({i+1}/{total_files}): {os.path.basename(fp)}...")

            # Smart crop: detect grid boundaries automatically
            img_row_cuts = None
            img_col_cuts = None
            if use_smart_crop:
                try:
                    self.status_var.set(f"{self.t('Detecting grid...')} ({i+1}/{total_files}): {os.path.basename(fp)}...")
                    img_row_cuts, img_col_cuts = st.detect_grid(fp)
                except Exception as e:
                    print(f"Smart crop detection failed for {os.path.basename(fp)}: {e}, falling back to manual grid")

            try:
                success, msg, count = st.slice_image(
                                                   image_path=fp,
                                                   grid_rows=rows,
                                                   grid_cols=cols,
                                                   output_dir=out_dir,
                                                   csv_path=csv_to_use,
                                                   translate_mode=do_translate,
                                                   remove_bg=self.var_remove_bg.get(),
                                                   cache_mode=self.var_cache_translation.get(),
                                                   normalize_mode=self.var_normalize.get(),
                                                   scale_factor=scale,
                                                   rename=rename_str,
                                                   auto_suffix=auto_suffix,
                                                   image_seq=i + 1,
                                                   start_index=current_index,
                                                   num_digits=num_digits,
                                                   row_cuts=img_row_cuts,
                                                   col_cuts=img_col_cuts)
                if not auto_suffix:
                    current_index += count
                if success:
                    success_count += 1
                    try:
                        from core import library
                        library.add_entry(
                            generator_type="slicer",
                            params={
                                "source_image": fp,
                                "output_dir": out_dir or "",
                                "grid_rows": rows,
                                "grid_cols": cols,
                                "cell_count": count,
                                "remove_bg": self.var_remove_bg.get(),
                                "translate": do_translate,
                                "csv": csv_to_use or "",
                            },
                            prompt="",
                            image_path=fp,
                            source_batch_id=batch_id,
                            notes=f"Sliced into {count} cells",
                        )
                    except Exception as e:
                        from core.logging_setup import get_logger
                        get_logger("app").warning("library.add_entry (slicer) failed: %s", e)
                else:
                    errors.append(f"{os.path.basename(fp)}: {msg}")
            except Exception as e:
                errors.append(f"{os.path.basename(fp)}: {str(e)}")
                
        self.root.after(0, lambda: self.set_ui_busy(False, self.t("Batch Complete")))
        
        summary = self.t("Processed {success}/{total} files successfully.").format(success=success_count, total=total_files)
        if errors:
            summary += "\n\n" + self.t("Errors:") + "\n" + "\n".join(errors)
            self.root.after(0, lambda: messagebox.showwarning(self.t("Batch Results"), summary))
        else:
            self.root.after(0, lambda: messagebox.showinfo(self.t("Batch Complete"), summary))
            
        self.root.after(0, lambda: self.set_output(summary))
                


    # --- Event Handlers (Spaceship) ---
    def update_subcategories(self, event=None):
        cat = self.category_var.get()
        if cat in self.component_map:
            subs = self.component_map[cat]
            self.subcategory_combo['values'] = subs
            if subs:
                self.subcategory_combo.current(0)
            else:
                self.subcategory_combo.set("")
        self.update_variants()

    def update_variants(self, event=None):
        cat = self.category_var.get()
        sub = self.subcategory_var.get()
        
        variants = pg.get_variants_for_subcategory(cat, sub)
        self.variant_combo['values'] = variants
        if variants:
            self.variant_combo.current(0)
        else:
            self.variant_combo.set("Standard")

    def on_manufacturer_change(self, event=None):
        name = self.manufacturer_var.get()
        if name and name != "None / Generic":
            # Find data
            data = pg.get_manufacturer_by_name(name)
            if data:
                self.lbl_manufacturer_desc.config(text=data.get("description", ""))
            
            # Disable Custom Colors
            self.use_custom_colors.set(False)
            self.chk_custom_color.configure(state=tk.DISABLED)
            self.toggle_color_buttons() # Ensure buttons update
        else:
            self.lbl_manufacturer_desc.config(text="")
            # Enable Custom Colors
            self.chk_custom_color.configure(state=tk.NORMAL)
            self.toggle_color_buttons()

    def toggle_color_buttons(self):
        state = tk.NORMAL if self.use_custom_colors.get() else tk.DISABLED
        self.btn_primary_color.config(state=state)
        self.btn_secondary_color.config(state=state)

    def pick_color(self, color_type):
        color = colorchooser.askcolor(title=f"Choose {color_type} color")[1]
        if color:
            if color_type == 'primary':
                self.primary_color = color
                self.btn_primary_color.config(bg=color, text=f"Main: {color}")
            else:
                self.secondary_color = color
                self.btn_secondary_color.config(bg=color, text=f"Glow: {color}")

    # --- Generation Logic ---

    def generate_spaceship_prompt(self):
        tier = self.tier_var.get()
        cat = self.category_var.get()
        sub = self.subcategory_var.get()
        manu = self.manufacturer_var.get()
        var = self.variant_var.get()

        if not tier or not cat or not sub:
            messagebox.showerror(self.t("Error"), self.t("Please select all options."))
            return

        p_col = self.primary_color if self.use_custom_colors.get() else None
        s_col = self.secondary_color if self.use_custom_colors.get() else None
        
        # Pass "None" string as None value
        if manu == "None / Generic":
            manu = None

        prompt = pg.generate_prompt_by_strings(tier, cat, sub,
                                             primary_color=p_col,
                                             secondary_color=s_col,
                                             manufacturer_name=manu,
                                             variation_name=var)

        self.set_output(prompt)

    # =========================================================================
    # Mecha tab
    # =========================================================================

    def setup_mecha_tab(self):
        parent = self.tab_mecha
        lang = self.ui_lang

        # Mecha tab has many controls — use a scrollable canvas
        body = self._make_scrollable(parent)

        ttk.Label(body, text=self.t("Mecha Prompt Generation"), font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Label(body, text=self.t("Generate a 4-view bare-frame mecha reference sheet (90s OVA real-robot style)."),
                  foreground="gray", wraplength=360).pack(anchor="w", pady=(0, 10))

        # --- Class / Variant / Tier (bilingual labels) ---
        self._mecha_subcat_label_map = mg.get_subcategory_label_map(lang)
        ttk.Label(body, text=self.t("Mecha Class:")).pack(anchor="w")
        self.mecha_subcat_var = tk.StringVar()
        self.mecha_subcat_combo = ttk.Combobox(body, textvariable=self.mecha_subcat_var, state="readonly")
        self.mecha_subcat_combo['values'] = list(self._mecha_subcat_label_map.keys())
        self.mecha_subcat_combo.current(0)
        self.mecha_subcat_combo.pack(fill=tk.X, pady=(0, 10))

        self._mecha_variant_label_map = mg.get_variant_label_map(lang)
        ttk.Label(body, text=self.t("Mecha Variant:")).pack(anchor="w")
        self.mecha_variant_var = tk.StringVar()
        self.mecha_variant_combo = ttk.Combobox(body, textvariable=self.mecha_variant_var, state="readonly")
        self.mecha_variant_combo['values'] = list(self._mecha_variant_label_map.keys())
        self.mecha_variant_combo.current(0)
        self.mecha_variant_combo.pack(fill=tk.X, pady=(0, 10))

        self._mecha_tier_label_map = mg.get_tier_label_map(lang)
        ttk.Label(body, text=self.t("Tech Tier:")).pack(anchor="w")
        self.mecha_tier_var = tk.StringVar()
        self.mecha_tier_combo = ttk.Combobox(body, textvariable=self.mecha_tier_var, state="readonly")
        self.mecha_tier_combo['values'] = list(self._mecha_tier_label_map.keys())
        self.mecha_tier_combo.current(2)
        self.mecha_tier_combo.pack(fill=tk.X, pady=(0, 10))

        # --- Manufacturer ---
        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(body, text=self.t("Manufacturer Preset"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.mecha_manufacturer_var = tk.StringVar()
        self.mecha_manufacturer_combo = ttk.Combobox(body, textvariable=self.mecha_manufacturer_var, state="readonly")
        self.mecha_manufacturer_combo['values'] = self.manufacturer_list
        self.mecha_manufacturer_combo.current(0)
        self.mecha_manufacturer_combo.pack(fill=tk.X, pady=(0, 10))

        # --- Five Design Control axes ---
        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(body, text=self.t("Design Controls (Auto = random / by designer)"),
                  font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))

        # Helper to build a bilingual axis dropdown with hover-tooltip
        def _build_axis(label_key, options_fn, label_map_fn, hints_fn, default_index=0):
            ttk.Label(body, text=self.t(label_key)).pack(anchor="w")
            var = tk.StringVar()
            combo = ttk.Combobox(body, textvariable=var, state="readonly")
            options = options_fn(lang)
            combo['values'] = options
            combo.current(default_index)
            combo.pack(fill=tk.X, pady=(0, 8))
            hints = hints_fn(lang)
            _ComboboxTooltip(combo, lambda lbl, h=hints: h.get(lbl, ""))
            return var, combo, label_map_fn(lang), hints

        (self.mecha_sensor_var, self.mecha_sensor_combo, self._mecha_sensor_map, self._mecha_sensor_hints) = \
            _build_axis("Sensor Module:", mg.get_sensor_module_options,
                        mg.get_sensor_module_label_map, mg.get_sensor_module_hints)
        (self.mecha_surface_var, self.mecha_surface_combo, self._mecha_surface_map, self._mecha_surface_hints) = \
            _build_axis("Surface Treatment:", mg.get_surface_treatment_options,
                        mg.get_surface_treatment_label_map, mg.get_surface_treatment_hints)
        (self.mecha_shoulder_var, self.mecha_shoulder_combo, self._mecha_shoulder_map, self._mecha_shoulder_hints) = \
            _build_axis("Shoulder Form:", mg.get_shoulder_form_options,
                        mg.get_shoulder_form_label_map, mg.get_shoulder_form_hints)
        (self.mecha_propulsion_var, self.mecha_propulsion_combo, self._mecha_propulsion_map, self._mecha_propulsion_hints) = \
            _build_axis("Propulsion Style:", mg.get_propulsion_style_options,
                        mg.get_propulsion_style_label_map, mg.get_propulsion_style_hints)
        (self.mecha_paint_var, self.mecha_paint_combo, self._mecha_paint_map, self._mecha_paint_hints) = \
            _build_axis("Paint Scheme:", mg.get_paint_scheme_options,
                        mg.get_paint_scheme_label_map, mg.get_paint_scheme_hints)

        # --- Designer (multi-select via Listbox) ---
        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(body, text=self.t("Mecha Designer (multi-select)"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))

        designer_options = mg.get_designer_options(lang)
        self._mecha_designer_label_map = mg.get_designer_label_map(lang)

        designer_frame = ttk.Frame(body)
        designer_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 5))
        self.mecha_designer_listbox = tk.Listbox(designer_frame, selectmode=tk.MULTIPLE, height=6, exportselection=False)
        for label in designer_options:
            self.mecha_designer_listbox.insert(tk.END, label)
        designer_scroll = ttk.Scrollbar(designer_frame, orient=tk.VERTICAL, command=self.mecha_designer_listbox.yview)
        self.mecha_designer_listbox.configure(yscrollcommand=designer_scroll.set)
        self.mecha_designer_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        designer_scroll.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Button(body, text=self.t("Clear Selection"),
                   command=lambda: self.mecha_designer_listbox.selection_clear(0, tk.END)).pack(anchor="e", pady=(0, 10))

        ttk.Separator(body, orient='horizontal').pack(fill='x', pady=10)

        # Generate
        ttk.Button(body, text=self.t("GENERATE MECHA PROMPT"),
                   command=self.generate_mecha_prompt).pack(fill=tk.X, pady=(10, 0), ipady=10)

    def generate_mecha_prompt(self):
        tier_label = self.mecha_tier_var.get()
        sub_label = self.mecha_subcat_var.get()
        var_label = self.mecha_variant_var.get()
        manu = self.mecha_manufacturer_var.get()

        # Resolve bilingual labels back to canonical keys
        tier = self._mecha_tier_label_map.get(tier_label, tier_label)
        sub = self._mecha_subcat_label_map.get(sub_label, sub_label)
        var = self._mecha_variant_label_map.get(var_label, var_label)

        if not tier or not sub:
            messagebox.showerror(self.t("Error"), self.t("Please select all options."))
            return

        if manu == "None / Generic":
            manu = None

        # Five design control axes — resolve label -> key (None for Auto)
        sensor_key = self._mecha_sensor_map.get(self.mecha_sensor_var.get())
        surface_key = self._mecha_surface_map.get(self.mecha_surface_var.get())
        shoulder_key = self._mecha_shoulder_map.get(self.mecha_shoulder_var.get())
        propulsion_key = self._mecha_propulsion_map.get(self.mecha_propulsion_var.get())
        paint_key = self._mecha_paint_map.get(self.mecha_paint_var.get())

        selected_labels = [self.mecha_designer_listbox.get(i) for i in self.mecha_designer_listbox.curselection()]
        designer_names = [self._mecha_designer_label_map.get(lbl, lbl) for lbl in selected_labels]

        prompt = mg.generate_mecha_prompt_by_strings(
            tier_name=tier,
            subcategory=sub,
            manufacturer_name=manu,
            variation_name=var,
            designer_names=designer_names,
            sensor_module_key=sensor_key,
            surface_treatment_key=surface_key,
            shoulder_form_key=shoulder_key,
            propulsion_style_key=propulsion_key,
            paint_scheme_key=paint_key,
        )
        self.set_output(prompt)

    # =========================================================================
    # Mecha Components tab (hand weapons, shields, shoulder pods)
    # =========================================================================

    def setup_mecha_part_tab(self):
        parent = self._make_scrollable(self.tab_mecha_part)
        lang = self.ui_lang

        ttk.Label(parent, text=self.t("Mecha Component Prompt Generation"),
                  font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Label(parent,
                  text=self.t("Generate a 4-view reference sheet for an individual piece of mecha equipment (hand weapon, shield, shoulder pod)."),
                  foreground="gray", wraplength=360).pack(anchor="w", pady=(0, 10))

        # Subcategory (mount type)
        self._mecha_part_subcat_label_map = mpg.get_subcategory_label_map(lang)
        ttk.Label(parent, text=self.t("Component Category:")).pack(anchor="w")
        self.mecha_part_subcat_var = tk.StringVar()
        self.mecha_part_subcat_combo = ttk.Combobox(parent, textvariable=self.mecha_part_subcat_var, state="readonly")
        self.mecha_part_subcat_combo['values'] = list(self._mecha_part_subcat_label_map.keys())
        self.mecha_part_subcat_combo.current(0)
        self.mecha_part_subcat_combo.pack(fill=tk.X, pady=(0, 10))
        self.mecha_part_subcat_combo.bind("<<ComboboxSelected>>", self._update_mecha_part_variants)

        # Structural Variant
        ttk.Label(parent, text=self.t("Structural Variant (Form Factor):")).pack(anchor="w")
        self.mecha_part_variant_var = tk.StringVar()
        self.mecha_part_variant_combo = ttk.Combobox(parent, textvariable=self.mecha_part_variant_var, state="readonly")
        self.mecha_part_variant_combo.pack(fill=tk.X, pady=(0, 10))

        # Tier
        self._mecha_part_tier_label_map = mpg.get_tier_label_map(lang)
        ttk.Label(parent, text=self.t("Tech Tier:")).pack(anchor="w")
        self.mecha_part_tier_var = tk.StringVar()
        self.mecha_part_tier_combo = ttk.Combobox(parent, textvariable=self.mecha_part_tier_var, state="readonly")
        self.mecha_part_tier_combo['values'] = list(self._mecha_part_tier_label_map.keys())
        self.mecha_part_tier_combo.current(2)
        self.mecha_part_tier_combo.pack(fill=tk.X, pady=(0, 20))

        # --- Manufacturer ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(parent, text=self.t("Manufacturer Preset"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.mecha_part_manufacturer_var = tk.StringVar()
        self.mecha_part_manufacturer_combo = ttk.Combobox(parent, textvariable=self.mecha_part_manufacturer_var, state="readonly")
        self.mecha_part_manufacturer_combo['values'] = self.manufacturer_list
        self.mecha_part_manufacturer_combo.current(0)
        self.mecha_part_manufacturer_combo.pack(fill=tk.X, pady=(0, 10))
        self.mecha_part_manufacturer_combo.bind("<<ComboboxSelected>>", self._on_mecha_part_manufacturer_change)

        self.lbl_mecha_part_manufacturer_desc = ttk.Label(parent, text="", foreground="gray", wraplength=350)
        self.lbl_mecha_part_manufacturer_desc.pack(anchor="w", pady=(0, 10))

        # --- Color Override ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(parent, text=self.t("Color Override"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))
        self.mecha_part_use_custom_colors = tk.BooleanVar(value=False)
        self.chk_mecha_part_custom_color = ttk.Checkbutton(
            parent, text=self.t("Enable Custom Colors"),
            variable=self.mecha_part_use_custom_colors,
            command=self._toggle_mecha_part_color_buttons,
        )
        self.chk_mecha_part_custom_color.pack(anchor="w", pady=(0, 10))

        self.mecha_part_primary_color = "#444444"
        self.mecha_part_secondary_color = "#00FFFF"
        self.btn_mecha_part_primary_color = tk.Button(
            parent, text=self.t("Pick Main Color"),
            command=lambda: self._pick_mecha_part_color('primary'),
            state=tk.DISABLED, bg="#dddddd",
        )
        self.btn_mecha_part_primary_color.pack(fill=tk.X, pady=2)
        self.btn_mecha_part_secondary_color = tk.Button(
            parent, text=self.t("Pick Energy/Glow Color"),
            command=lambda: self._pick_mecha_part_color('secondary'),
            state=tk.DISABLED, bg="#dddddd",
        )
        self.btn_mecha_part_secondary_color.pack(fill=tk.X, pady=2)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=20)

        ttk.Button(parent, text=self.t("GENERATE MECHA COMPONENT PROMPT"),
                   command=self.generate_mecha_part_prompt).pack(fill=tk.X, pady=(10, 0), ipady=10)

        # Initial variant fill
        self._update_mecha_part_variants()

    def _update_mecha_part_variants(self, _e=None):
        lang = self.ui_lang
        sub_label = self.mecha_part_subcat_var.get()
        sub_key = self._mecha_part_subcat_label_map.get(sub_label, sub_label)
        self._mecha_part_variant_label_map = mpg.get_variant_label_map(sub_key, lang)
        opts = list(self._mecha_part_variant_label_map.keys())
        self.mecha_part_variant_combo['values'] = opts
        if opts:
            self.mecha_part_variant_combo.current(0)
        else:
            self.mecha_part_variant_var.set("")

    def _on_mecha_part_manufacturer_change(self, _e=None):
        name = self.mecha_part_manufacturer_var.get()
        if not name or name == "None / Generic":
            self.lbl_mecha_part_manufacturer_desc.config(text="")
            return
        m = pg.get_manufacturer_by_name(name)
        if m:
            desc = f"{m.get('design_language', '')}  |  {m.get('color_palette', '')}"
            self.lbl_mecha_part_manufacturer_desc.config(text=desc)
        else:
            self.lbl_mecha_part_manufacturer_desc.config(text="")

    def _toggle_mecha_part_color_buttons(self):
        state = tk.NORMAL if self.mecha_part_use_custom_colors.get() else tk.DISABLED
        self.btn_mecha_part_primary_color.config(state=state)
        self.btn_mecha_part_secondary_color.config(state=state)

    def _pick_mecha_part_color(self, slot):
        color = colorchooser.askcolor(title=self.t("Pick a Color"))
        if color and color[1]:
            hex_code = color[1]
            if slot == 'primary':
                self.mecha_part_primary_color = hex_code
                self.btn_mecha_part_primary_color.config(bg=hex_code, text=hex_code)
            else:
                self.mecha_part_secondary_color = hex_code
                self.btn_mecha_part_secondary_color.config(bg=hex_code, text=hex_code)

    def generate_mecha_part_prompt(self):
        sub_label = self.mecha_part_subcat_var.get()
        var_label = self.mecha_part_variant_var.get()
        tier_label = self.mecha_part_tier_var.get()
        manu = self.mecha_part_manufacturer_var.get()

        sub_key = self._mecha_part_subcat_label_map.get(sub_label, sub_label)
        var_key = getattr(self, "_mecha_part_variant_label_map", {}).get(var_label, var_label)
        tier_key = self._mecha_part_tier_label_map.get(tier_label, tier_label)

        if not sub_key or not tier_key:
            messagebox.showerror(self.t("Error"), self.t("Please select all options."))
            return

        if manu == "None / Generic":
            manu = None

        p_col = self.mecha_part_primary_color if self.mecha_part_use_custom_colors.get() else None
        s_col = self.mecha_part_secondary_color if self.mecha_part_use_custom_colors.get() else None

        prompt = mpg.generate_mecha_part_prompt_by_strings(
            tier_name=tier_key,
            subcategory_key=sub_key,
            primary_color=p_col,
            secondary_color=s_col,
            manufacturer_name=manu,
            variation_key=var_key,
        )
        self.set_output(prompt)

    # =========================================================================
    # Spaceship (full vessel) tab
    # =========================================================================

    def setup_ship_tab(self):
        parent = self._make_scrollable(self.tab_ship)
        lang = self.ui_lang

        ttk.Label(parent, text=self.t("Spaceship Prompt Generation"), font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Label(parent, text=self.t("Generate a 4-view full-vessel spaceship reference sheet (90s OVA capital ship style)."),
                  foreground="gray", wraplength=360).pack(anchor="w", pady=(0, 10))

        # Archetype (labels follow UI language; map back to canonical name on submit)
        ttk.Label(parent, text=self.t("Ship Archetype:")).pack(anchor="w")
        self.ship_archetype_var = tk.StringVar()
        self.ship_archetype_combo = ttk.Combobox(parent, textvariable=self.ship_archetype_var, state="readonly")
        _archetype_vals = sg.get_archetype_list(lang)
        self.ship_archetype_combo['values'] = _archetype_vals
        self._ship_archetype_label_map = sg.get_archetype_label_map(lang)
        if _archetype_vals: self.ship_archetype_combo.set(_archetype_vals[0])
        self.ship_archetype_combo.pack(fill=tk.X, pady=(0, 10))

        # Variant (labels follow UI language; map back to canonical id on submit)
        ttk.Label(parent, text=self.t("Ship Variant:")).pack(anchor="w")
        self.ship_variant_var = tk.StringVar()
        self.ship_variant_combo = ttk.Combobox(parent, textvariable=self.ship_variant_var, state="readonly")
        _variant_vals = sg.get_variant_list(lang)
        self.ship_variant_combo['values'] = _variant_vals
        self._ship_variant_label_map = sg.get_variant_label_map(lang)
        if _variant_vals: self.ship_variant_combo.set(_variant_vals[0])
        self.ship_variant_combo.pack(fill=tk.X, pady=(0, 10))

        # Tier
        ttk.Label(parent, text=self.t("Tech Tier:")).pack(anchor="w")
        self.ship_tier_var = tk.StringVar()
        self.ship_tier_combo = ttk.Combobox(parent, textvariable=self.ship_tier_var, state="readonly")
        self.ship_tier_combo['values'] = self.tier_list
        self.ship_tier_combo.current(2)
        self.ship_tier_combo.pack(fill=tk.X, pady=(0, 10))

        # Manufacturer
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(parent, text=self.t("Manufacturer Preset"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.ship_manufacturer_var = tk.StringVar()
        self.ship_manufacturer_combo = ttk.Combobox(parent, textvariable=self.ship_manufacturer_var, state="readonly")
        self.ship_manufacturer_combo['values'] = self.manufacturer_list
        if self.manufacturer_list: self.ship_manufacturer_combo.set(self.manufacturer_list[0])
        self.ship_manufacturer_combo.pack(fill=tk.X, pady=(0, 10))

        # Designer (shared mecha designer pool)
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(parent, text=self.t("Ship Designer (multi-select)"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))

        designer_options = sg.get_designer_options(lang)
        self._ship_designer_label_map = sg.get_designer_label_map(lang)

        designer_frame = ttk.Frame(parent)
        designer_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 5))
        self.ship_designer_listbox = tk.Listbox(designer_frame, selectmode=tk.MULTIPLE, height=6, exportselection=False)
        for label in designer_options:
            self.ship_designer_listbox.insert(tk.END, label)
        designer_scroll = ttk.Scrollbar(designer_frame, orient=tk.VERTICAL, command=self.ship_designer_listbox.yview)
        self.ship_designer_listbox.configure(yscrollcommand=designer_scroll.set)
        self.ship_designer_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        designer_scroll.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Button(parent, text=self.t("Clear Selection"),
                   command=lambda: self.ship_designer_listbox.selection_clear(0, tk.END)).pack(anchor="e", pady=(0, 10))

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(parent, text=self.t("GENERATE SHIP PROMPT"),
                   command=self.generate_ship_prompt).pack(fill=tk.X, pady=(10, 0), ipady=10)

    def generate_ship_prompt(self):
        tier = self.ship_tier_var.get()
        archetype_label = self.ship_archetype_var.get()
        variant_label = self.ship_variant_var.get()
        manu = self.ship_manufacturer_var.get()

        if not tier or not archetype_label:
            messagebox.showerror(self.t("Error"), self.t("Please select all options."))
            return

        # Resolve localized UI labels back to the canonical English ids that
        # the generator core understands.
        archetype = self._ship_archetype_label_map.get(archetype_label, archetype_label)
        var = self._ship_variant_label_map.get(variant_label, variant_label)

        if manu == "None / Generic":
            manu = None

        selected_labels = [self.ship_designer_listbox.get(i) for i in self.ship_designer_listbox.curselection()]
        designer_names = [self._ship_designer_label_map.get(lbl, lbl) for lbl in selected_labels]

        prompt = sg.generate_ship_prompt_by_strings(
            tier_name=tier,
            archetype_name=archetype,
            manufacturer_name=manu,
            variation_name=var,
            designer_names=designer_names,
        )
        self.set_output(prompt)

    def _update_age_label(self):
        value = int(float(self.age_scale.get()))
        self.age_var.set(value)
        descriptor = cg.get_age_descriptor(value) or ""
        zh_map = {
            "child": "儿童",
            "teenager": "青少年",
            "young adult": "青年",
            "adult": "成年人",
            "middle-aged adult": "中年",
            "mature adult": "成熟成年人",
        }
        zh_desc = zh_map.get(descriptor, "")
        if zh_desc:
            label_text = f"{value} / {zh_desc}"
        else:
            label_text = f"{value}"
        self.age_value_label.config(text=label_text)
        self.schedule_character_prompt_update()

    def toggle_hair_color_mode(self):
        advanced = self.hair_color_advanced.get()
        if advanced:
            self.hair_color_combo.config(state=tk.DISABLED)
            self.btn_add_hair_color.config(state=tk.NORMAL)
            self.btn_clear_hair_colors.config(state=tk.NORMAL)
        else:
            self.hair_color_combo.config(state="readonly")
            self.btn_add_hair_color.config(state=tk.DISABLED)
            self.btn_clear_hair_colors.config(state=tk.DISABLED)
            self.clear_hair_colors()
        self.schedule_character_prompt_update()

    def add_hair_color(self):
        if len(self.hair_colors) >= 3:
            messagebox.showinfo(self.t("Hair Colors:"), self.t("Max hair colors reached"))
            return
        color = colorchooser.askcolor(title=self.t("Hair Colors:"))[1]
        if color:
            self.hair_colors.append(color)
            self._refresh_hair_colors()
            self.schedule_character_prompt_update()

    def clear_hair_colors(self):
        if not self.hair_colors:
            return
        self.hair_colors = []
        self._refresh_hair_colors()
        self.schedule_character_prompt_update()

    def _refresh_hair_colors(self):
        for child in self.hair_color_preview.winfo_children():
            child.destroy()
        for idx, color in enumerate(self.hair_colors):
            fg = "#000000"
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
                fg = "#000000" if luminance > 0.6 else "#ffffff"
            except Exception:
                fg = "#000000"
            chip = tk.Label(self.hair_color_preview, text=color.upper(), bg=color, fg=fg, padx=6, pady=2)
            chip.grid(row=0, column=idx, sticky="w", padx=(0, 4))

    def _get_gender_value(self) -> str:
        mapping = cg.get_gender_label_map(self.ui_lang)
        return mapping.get(self.gender_var.get(), self.gender_var.get())

    def _get_hair_style_key(self) -> str:
        label = self._get_current_hair_preview_label()
        return self._get_hair_style_key_from_label(label)

    def _get_hair_style_key_from_label(self, label: str) -> str:
        mapping = cg.get_hair_style_label_map(self.ui_lang)
        normalized = (label or "").strip()
        return mapping.get(normalized, normalized)

    def _get_current_hair_preview_label(self) -> str:
        if hasattr(self, "hair_preview_style_var"):
            return self.hair_preview_style_var.get().strip()
        return self.hair_style_var.get().strip()

    def _get_filtered_hair_style_options(self) -> List[str]:
        options_all = self.hair_style_all_options or cg.get_hair_style_options(self.ui_lang)
        if not self.filter_hair_by_gender.get():
            return options_all
        gender_value = self._get_gender_value().lower()
        if gender_value in ("male", "female"):
            options_by_gender = self.hair_style_options_by_gender or cg.get_hair_style_options_by_gender(self.ui_lang)
            neutral = options_by_gender.get("neutral", [])
            return options_by_gender.get(gender_value, options_all) + [o for o in neutral if o not in options_by_gender.get(gender_value, options_all)]
        options_by_gender = self.hair_style_options_by_gender or cg.get_hair_style_options_by_gender(self.ui_lang)
        neutral = options_by_gender.get("neutral", [])
        return neutral or options_all

    def refresh_hair_style_options(self, *_):
        options = self._get_filtered_hair_style_options()
        self.hair_style_combo["values"] = options
        current = self.hair_style_var.get()
        if not options:
            if current:
                self.hair_style_var.set("")
            self.update_hair_style_preview()
            return
        if current not in options:
            self.hair_style_var.set(options[0])
        self.update_hair_style_preview()

    def _set_preview_canvas_image(self, canvas: tk.Canvas, path: str, size: tuple, attr_name: str):
        photo = None
        canvas.delete("all")
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.convert("RGBA")
                img.thumbnail(size, Image.LANCZOS)
                bg = Image.new("RGBA", size, (238, 238, 238, 255))
                offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
                bg.paste(img, offset)
                photo = ImageTk.PhotoImage(bg)
            except Exception:
                photo = None
        if photo:
            canvas.create_image(size[0] // 2, size[1] // 2, image=photo)
        else:
            canvas.create_text(size[0] // 2, size[1] // 2, text=self.t("No preview image"))
        setattr(self, attr_name, photo)

    def update_hair_style_preview(self):
        if not hasattr(self, "hair_style_preview_canvas"):
            return
        key = self._get_hair_style_key()
        path = self.hair_style_previews.get(key, "")
        self._set_preview_canvas_image(self.hair_style_preview_canvas, path, (200, 200), "hair_style_preview_image")

    def set_hair_style_preview(self):
        key = self._get_hair_style_key()
        if not key:
            return
        path = filedialog.askopenfilename(
            title=self.t("Set Preview Image"),
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp;*.gif;*.bmp")],
        )
        if not path:
            return
        self.hair_style_previews[key] = path
        self.save_hair_preview_config()
        self.update_hair_style_preview()

    def clear_hair_style_preview(self):
        key = self._get_hair_style_key()
        if not key:
            return
        if key in self.hair_style_previews:
            self.hair_style_previews.pop(key, None)
            self.save_hair_preview_config()
        self.update_hair_style_preview()

    def _bind_character_auto_update(self):
        vars_to_watch = [
            self.gender_var,
            self.age_var,
            self.body_type_var,
            self.skin_tone_var,
            self.framing_var,
            self.aspect_ratio_var,
            self.expression_var,
            self.gaze_var,
            self.clothing_hint_var,
            self.hair_style_var,
            self.hair_color_var,
            self.hair_color_advanced,
            self.bangs_presence_var,
            self.bangs_style_var,
            self.face_shape_var,
            self.eye_size_var,
            self.nose_size_var,
            self.mouth_shape_var,
            self.cheek_fullness_var,
            self.jaw_width_var,
            self.eye_color_var,
            self.extra_modifiers_var,
        ]
        for var in vars_to_watch:
            var.trace_add("write", self.schedule_character_prompt_update)

        listboxes = [
            self.face_feature_list,
            self.artist_list,
        ]
        for lb in listboxes:
            lb.bind("<<ListboxSelect>>", self.schedule_character_prompt_update)

    def schedule_character_prompt_update(self, *_):
        if getattr(self, "_character_update_pending", False):
            return
        self._character_update_pending = True
        self.root.after(50, self._run_character_prompt_update)

    def _run_character_prompt_update(self):
        self._character_update_pending = False
        try:
            self.generate_character_prompt()
        except Exception:
            pass

    def generate_character_prompt(self):
        prompt_inputs = self._collect_character_prompt_inputs()
        include_style = True
        include_background = True
        include_mood = True
        include_extra_modifiers = True
        if self.style_ref_blobs and self.style_ref_only_mode.get():
            include_style = False
            include_mood = False
            include_extra_modifiers = False
        prompt = self._build_character_prompt(
            face_features=prompt_inputs["face_features"],
            artists=prompt_inputs["artists"],
            include_style=include_style,
            include_background=include_background,
            include_mood=include_mood,
            include_extra_modifiers=include_extra_modifiers,
        )
        self.set_output(prompt)

    def _collect_character_prompt_inputs(self):
        face_features = [self.face_feature_list.get(i) for i in self.face_feature_list.curselection()]
        artists = [self.artist_label_map.get(self.artist_list.get(i), self.artist_list.get(i)) for i in self.artist_list.curselection()]
        return {
            "face_features": face_features,
            "artists": artists,
        }

    def _build_character_prompt(
        self,
        face_features,
        artists,
        include_style: bool,
        include_background: bool = True,
        include_mood: bool = True,
        include_extra_modifiers: bool = True,
    ):
        return cg.generate_character_prompt(
            gender=self.gender_var.get(),
            age=self.age_var.get(),
            framing=self.framing_var.get(),
            aspect_ratio=self.aspect_ratio_var.get(),
            expression=self.expression_var.get(),
            gaze=self.gaze_var.get(),
            appearance_features=face_features,
            body_type=self.body_type_var.get(),
            skin_tone=self.skin_tone_var.get(),
            hair_style=self.hair_style_var.get(),
            hair_color=self.hair_color_var.get(),
            hair_colors=self.hair_colors if self.hair_color_advanced.get() else [],
            hair_bangs_presence=self.bangs_presence_var.get(),
            hair_bangs_style=self.bangs_style_var.get(),
            face_shape=self.face_shape_var.get(),
            eye_size=self.eye_size_var.get(),
            nose_size=self.nose_size_var.get(),
            mouth_shape=self.mouth_shape_var.get(),
            cheek_fullness=self.cheek_fullness_var.get(),
            jaw_width=self.jaw_width_var.get(),
            eye_color=self.eye_color_var.get(),
            clothing_hint=self.clothing_hint_var.get(),
            artists=artists,
            lang=self.ui_lang,
            extra_modifiers=self.extra_modifiers_var.get(),
            include_style=include_style,
            include_background=include_background,
            include_mood=include_mood,
            include_extra_modifiers=include_extra_modifiers,
        )

    def _bind_clothing_auto_update(self):
        vars_to_watch = [
            self.faction_var,
            self.clothing_gender_var,
            self.role_var,
            self.view_mode_var,
            self.clothing_aspect_ratio_var,
            self.pose_var,
            self.presentation_var,
            self.outfit_category_var,
            self.silhouette_var,
            self.layering_var,
            self.clothing_material_var,
            self.palette_var,
            self.wear_state_var,
            self.clothing_custom_notes_var,
            self.clothing_extra_modifiers_var,
        ]
        for var in vars_to_watch:
            var.trace_add("write", self.schedule_clothing_prompt_update)

        listboxes = [
            self.detail_accent_list,
            self.clothing_accessory_list,
            self.clothing_insignia_list,
        ]
        for lb in listboxes:
            lb.bind("<<ListboxSelect>>", self.schedule_clothing_prompt_update)

    def schedule_clothing_prompt_update(self, *_):
        if getattr(self, "_clothing_update_pending", False):
            return
        self._clothing_update_pending = True
        self.root.after(50, self._run_clothing_prompt_update)

    def _run_clothing_prompt_update(self):
        self._clothing_update_pending = False
        try:
            self.generate_clothing_prompt()
        except Exception:
            pass

    def generate_clothing_prompt(self):
        prompt_inputs = self._collect_clothing_prompt_inputs()
        prompt = self._build_clothing_prompt(
            detail_accents=prompt_inputs["detail_accents"],
            accessories=prompt_inputs["accessories"],
            insignia=prompt_inputs["insignia"],
            extra_notes=prompt_inputs["extra_notes"],
        )
        self.set_output(prompt)

    def _collect_clothing_prompt_inputs(self):
        detail_accents = [self.detail_accent_list.get(i) for i in self.detail_accent_list.curselection()]
        accessories = [self.clothing_accessory_list.get(i) for i in self.clothing_accessory_list.curselection()]
        insignia = [self.clothing_insignia_list.get(i) for i in self.clothing_insignia_list.curselection()]
        extra_notes = self.clothing_custom_notes_var.get().strip()
        if extra_notes:
            detail_accents.extend([n.strip() for n in extra_notes.split(",") if n.strip()])
        return {
            "detail_accents": detail_accents,
            "accessories": accessories,
            "insignia": insignia,
            "extra_notes": self.clothing_extra_modifiers_var.get().strip(),
        }

    def _build_clothing_prompt(
        self,
        detail_accents,
        accessories,
        insignia,
        extra_notes,
    ):
        return clg.generate_clothing_preset_prompt(
            faction=self.faction_var.get(),
            gender=self.clothing_gender_var.get(),
            role=self.role_var.get(),
            outfit_category=self.outfit_category_var.get(),
            silhouette=self.silhouette_var.get(),
            layering=self.layering_var.get(),
            material=self.clothing_material_var.get(),
            palette=self.palette_var.get(),
            wear_state=self.wear_state_var.get(),
            presentation=self.presentation_var.get(),
            pose=self.pose_var.get(),
            view_mode=self.view_mode_var.get(),
            aspect_ratio=self.clothing_aspect_ratio_var.get(),
            detail_accents=detail_accents,
            accessories=accessories,
            insignia=insignia,
            extra_notes=extra_notes,
            include_style=True,
            include_background=True,
            include_mood=True,
            swap_ready=True,
            lang=self.ui_lang,
        )
    
    def _show_openai_prompt_preview(self, prompt: str) -> bool:
        """Show a modal dialog with the prompt that will actually be sent to OpenAI.

        Shows both the original and sanitized prompts so the user can verify
        what changed. Returns True to proceed with generation, False to cancel.
        """
        from core.prompt_sanitizer import sanitize_for_openai
        from tkinter.scrolledtext import ScrolledText

        sanitized = sanitize_for_openai(prompt)
        changed = sanitized != prompt
        is_zh = self.ui_lang == "zh"

        result = {"proceed": False}

        dlg = tk.Toplevel(self.root)
        dlg.title("发送给 OpenAI 的提示词" if is_zh else "Prompt sent to OpenAI")
        dlg.resizable(True, True)
        dlg.grab_set()

        # ── Status banner ────────────────────────────────────────────────────
        if changed:
            banner_text = "✓ 已移除画师名称引用，以下为实际发送内容：" if is_zh else "✓ Artist references removed. Text below is what will be sent:"
            banner_fg = "#1a7f37"
        else:
            banner_text = "提示词未做修改（未检测到画师名称）：" if is_zh else "No changes made (no artist references detected):"
            banner_fg = "#555555"

        banner = tk.Label(dlg, text=banner_text, fg=banner_fg, font=("Arial", 9, "bold"), anchor="w")
        banner.pack(fill=tk.X, padx=10, pady=(10, 2))

        # ── Sanitized prompt (what OpenAI actually receives) ─────────────────
        txt = ScrolledText(dlg, wrap=tk.WORD, width=72, height=10, font=("Arial", 9))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        txt.insert("1.0", sanitized)
        txt.config(state=tk.DISABLED)  # read-only so copy button is the authoritative source

        # ── Original (collapsed, only shown when something changed) ──────────
        if changed:
            orig_lbl = "原始提示词（含画师名，供参考）：" if is_zh else "Original prompt (with artist names, for reference):"
            ttk.Label(dlg, text=orig_lbl, foreground="#888888", font=("Arial", 8)).pack(anchor="w", padx=10, pady=(0, 1))
            orig_txt = ScrolledText(dlg, wrap=tk.WORD, width=72, height=5,
                                    font=("Arial", 8), foreground="#888888", background="#f5f5f5")
            orig_txt.pack(fill=tk.X, padx=10, pady=(0, 6))
            orig_txt.insert("1.0", prompt)
            orig_txt.config(state=tk.DISABLED)

        # ── Buttons ──────────────────────────────────────────────────────────
        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        def copy_sanitized():
            content = sanitized  # always copy the sanitized version, not widget text
            dlg.clipboard_clear()
            dlg.clipboard_append(content)
            copy_btn.config(text="✓ " + ("已复制！" if is_zh else "Copied!"))
            dlg.after(1500, lambda: copy_btn.config(text=copy_lbl))

        def on_generate():
            result["proceed"] = True
            dlg.destroy()

        def on_cancel():
            dlg.destroy()

        copy_lbl = "复制已过滤内容" if is_zh else "Copy (filtered)"
        gen_lbl  = "生成" if is_zh else "Generate"
        cxl_lbl  = "取消" if is_zh else "Cancel"

        copy_btn = ttk.Button(btn_frame, text=copy_lbl, command=copy_sanitized)
        copy_btn.pack(side=tk.LEFT)
        ttk.Button(btn_frame, text=cxl_lbl,  command=on_cancel).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(btn_frame, text=gen_lbl,  command=on_generate).pack(side=tk.RIGHT)

        # Centre on parent window
        dlg.update_idletasks()
        pw, ph = self.root.winfo_width(), self.root.winfo_height()
        px, py = self.root.winfo_x(), self.root.winfo_y()
        dw, dh = dlg.winfo_width(), dlg.winfo_height()
        dlg.geometry(f"+{px + (pw - dw) // 2}+{py + (ph - dh) // 2}")

        self.root.wait_window(dlg)
        return result["proceed"]

    def generate_image_threaded(self):
        current_tab = self.notebook.select()

        # Auto-regenerate prompt for the active tab before reading
        if current_tab == str(self.tab_spaceship):
            self.generate_spaceship_prompt()
        elif current_tab == str(self.tab_mecha):
            self.generate_mecha_prompt()
        elif current_tab == str(self.tab_mecha_part):
            self.generate_mecha_part_prompt()
        elif current_tab == str(self.tab_ship):
            self.generate_ship_prompt()
        elif current_tab == str(self.tab_characters):
            self.generate_character_prompt()
        elif current_tab == str(self.tab_clothing):
            self.generate_clothing_prompt()

        provider, api_key, _, _ = self._get_active_api_credentials()
        if not api_key:
            messagebox.showerror(self.t("Error"), self.t("API key is missing. Please add your key in Settings."))
            return

        reference_images = self._get_style_reference_images()

        # Item icons tab: run prompt generation + image generation together in background
        if current_tab == str(self.tab_items):
            self.set_ui_busy(True, self.t("Generating Image..."))
            threading.Thread(target=self._generate_item_then_image_task, args=(reference_images,), daemon=True).start()
            return

        if (
            reference_images
            and current_tab == str(self.tab_characters)
            and self.style_ref_only_mode.get()
        ):
            prompt_inputs = self._collect_character_prompt_inputs()
            prompt = self._build_character_prompt(
                face_features=prompt_inputs["face_features"],
                artists=prompt_inputs["artists"],
                include_style=False,
                include_background=True,
                include_mood=False,
                include_extra_modifiers=False,
            ).strip()
        else:
            prompt = self.output_text.get("1.0", tk.END).strip()

        if not prompt:
            messagebox.showerror(self.t("Error"), self.t("No prompt content to send."))
            return

        # When using OpenAI, show the sanitized prompt before sending so the
        # user can inspect and copy it for verification on the official site.
        if provider == "OpenAI":
            if not self._show_openai_prompt_preview(prompt):
                return

        try:
            count = int(self.concurrent_var.get() or "1")
        except ValueError:
            count = 1
        count = max(1, min(8, count))
        self.set_ui_busy(True, self.t("Generating Image..."))
        if count == 1:
            threading.Thread(target=self._generate_image_task, args=(prompt, reference_images), daemon=True).start()
        else:
            threading.Thread(target=self._generate_images_task, args=(prompt, reference_images, count), daemon=True).start()

    def _generate_item_then_image_task(self, reference_images):
        """Background task: generate item icon prompt first, then generate image."""
        items = ig.read_items_from_csv(self.item_csv_path)
        if not items:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), self.t("Could not read items from CSV.")))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
            return

        do_translate = self.var_translate_prompt.get()
        do_cache = self.var_cache_translation.get()
        cache_path = self.item_csv_path if do_cache else None

        try:
            prompt = ig.generate_icon_grid_prompt(items, translate=do_translate, cache_path=cache_path)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))
            return

        self.root.after(0, lambda: self.set_output(prompt))
        self._generate_image_task(prompt, reference_images)

    def open_edit_dialog(self, initial_prompt: str = ""):
        if not self.pending_image_bytes:
            messagebox.showerror(self.t("Error"), self.t("No image to edit."))
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(self.t("Edit Image"))
        dialog.geometry("520x360")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text=self.t("Edit Prompt:"), font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        prompt_box = tk.Text(dialog, height=10, wrap=tk.WORD)
        prompt_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        if initial_prompt:
            prompt_box.insert("1.0", initial_prompt)

        btn_row = ttk.Frame(dialog)
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        def submit():
            edit_prompt = prompt_box.get("1.0", tk.END).strip()
            if not edit_prompt:
                messagebox.showerror(self.t("Error"), self.t("No prompt content to send."))
                return
            dialog.destroy()
            self.edit_image_threaded(edit_prompt)

        ttk.Button(btn_row, text=self.t("Apply Edit"), command=submit).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(btn_row, text=self.t("Cancel"), command=dialog.destroy).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
    
    def _generate_image_task(self, prompt: str, reference_images=None):
        try:
            image_bytes, mime_type = self._generate_image_with_active_provider(
                prompt,
                reference_images=reference_images,
            )
            self.pending_images = []
            self.edit_undo_stack.clear()
            self.pending_image_bytes = image_bytes
            self.pending_image_mime = mime_type
            self.pending_image_prefix = self.get_current_module_prefix()
            self.root.after(0, self.show_preview_image)
            self.root.after(0, self._refresh_undo_button)
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
            self.root.after(0, lambda: self.status_var.set(self.t("Image ready. Use Save/Discard.")))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))

    def _get_style_reference_images(self):
        if self.notebook.select() != str(self.tab_characters):
            return None
        if not self.style_ref_blobs:
            return None
        return list(self.style_ref_blobs)

    def edit_image_threaded(self, edit_prompt: str):
        if not self.pending_image_bytes:
            messagebox.showerror(self.t("Error"), self.t("No image to edit."))
            return
        _, api_key, _, _ = self._get_active_api_credentials()
        if not api_key:
            messagebox.showerror(self.t("Error"), self.t("API key is missing. Please add your key in Settings."))
            return
        self.set_ui_busy(True, self.t("Editing Image..."))
        threading.Thread(target=self._edit_image_task, args=(edit_prompt,), daemon=True).start()

    def _edit_image_task(self, edit_prompt: str):
        image_bytes = self.pending_image_bytes
        image_mime = self.pending_image_mime

        try:
            edited_bytes, mime_type = self._edit_image_with_active_provider(
                edit_prompt,
                image_bytes=image_bytes,
                image_mime=image_mime,
            )
            self.edit_undo_stack.append({"bytes": image_bytes, "mime": image_mime})
            self.pending_image_bytes = edited_bytes
            self.pending_image_mime = mime_type
            self.pending_image_prefix = f"{self.get_current_module_prefix()}_edit"
            self.root.after(0, self.show_preview_image)
            self.root.after(0, self._refresh_undo_button)
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
            self.root.after(0, lambda: self.status_var.set(self.t("Image ready. Use Save/Discard.")))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))

    def _generate_images_task(self, prompt: str, reference_images, count: int):
        def worker():
            return self._generate_image_with_active_provider(prompt, reference_images=reference_images)

        results = []
        try:
            with ThreadPoolExecutor(max_workers=count) as executor:
                futures = [executor.submit(worker) for _ in range(count)]
                for future in as_completed(futures):
                    results.append(future.result())
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))
            return

        import uuid as _uuid
        self.pending_images = [{"bytes": b, "mime": m} for b, m in results]
        self.pending_image_bytes = None
        self.pending_image_mime = None
        self.edit_undo_stack.clear()
        self.pending_image_prefix = self.get_current_module_prefix()
        self.pending_batch_id = _uuid.uuid4().hex if len(self.pending_images) > 1 else None
        self.active_preview_index = 0
        self.root.after(0, self.show_preview_images)
        self.root.after(0, self._refresh_undo_button)
        self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
        self.root.after(0, lambda: self.status_var.set(self.t("Image ready. Use Save/Discard.")))

    def show_preview_image(self):
        if not self.pending_image_bytes:
            return
        try:
            img = Image.open(io.BytesIO(self.pending_image_bytes))
            img.thumbnail((420, 420))
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_photo, text="")
            self.preview_label.pack(fill=tk.BOTH, expand=False, pady=(5, 10))
            self.preview_grid.pack_forget()
            self.btn_save_image.config(state=tk.NORMAL)
            self.btn_discard_image.config(state=tk.NORMAL)
            self.btn_edit_image.config(state=tk.NORMAL)
        except Exception:
            self.preview_label.config(text=self.t("Error loading image"), image="")
            self.preview_photo = None

    def show_preview_images(self):
        if not self.pending_images:
            return
        self.preview_label.pack_forget()
        self.preview_grid.pack(fill=tk.BOTH, expand=False, pady=(5, 10))
        self._render_image_grid()
        self.btn_save_image.config(state=tk.DISABLED)
        self.btn_discard_image.config(state=tk.DISABLED)
        self.btn_edit_image.config(state=tk.DISABLED)

    def _render_image_grid(self):
        for child in self.preview_grid.winfo_children():
            child.destroy()
        self.preview_thumbnails = []
        columns = 4
        for idx, item in enumerate(self.pending_images):
            try:
                img = Image.open(io.BytesIO(item["bytes"]))
                img.thumbnail((140, 140))
                thumb = ImageTk.PhotoImage(img)
                self.preview_thumbnails.append(thumb)
                btn = tk.Button(self.preview_grid, image=thumb, command=lambda i=idx: self.open_image_viewer(i))
                row = idx // columns
                col = idx % columns
                btn.grid(row=row, column=col, padx=6, pady=6)
            except Exception:
                lbl = ttk.Label(self.preview_grid, text=self.t("Error loading image"))
                row = idx // columns
                col = idx % columns
                lbl.grid(row=row, column=col, padx=6, pady=6)

    def open_image_viewer(self, index: int):
        if not self.pending_images:
            return
        self.active_preview_index = index
        dialog = tk.Toplevel(self.root)
        dialog.title(self.t("Image Preview"))
        dialog.geometry("720x860")
        dialog.transient(self.root)
        dialog.grab_set()

        img_label = ttk.Label(dialog, anchor="center")
        img_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        nav_frame = ttk.Frame(dialog)
        nav_frame.pack(fill=tk.X, padx=10, pady=(0, 6))

        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        def render():
            try:
                item = self.pending_images[self.active_preview_index]
                img = Image.open(io.BytesIO(item["bytes"]))
                img.thumbnail((680, 680))
                photo = ImageTk.PhotoImage(img)
                img_label.image = photo
                img_label.config(image=photo, text="")
            except Exception:
                img_label.config(text=self.t("Error loading image"), image="")

        def go_prev():
            if not self.pending_images:
                return
            self.active_preview_index = (self.active_preview_index - 1) % len(self.pending_images)
            render()

        def go_next():
            if not self.pending_images:
                return
            self.active_preview_index = (self.active_preview_index + 1) % len(self.pending_images)
            render()

        ttk.Button(nav_frame, text=self.t("Previous"), command=go_prev).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(nav_frame, text=self.t("Next"), command=go_next).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 5))
        ttk.Button(nav_frame, text=self.t("Grid View"), command=dialog.destroy).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        def save_selected():
            if not self.pending_images:
                return
            item = self.pending_images[self.active_preview_index]
            batch_id = getattr(self, "pending_batch_id", None)
            output_path = self._save_image_bytes_to_disk(item["bytes"], self.pending_image_prefix, batch_id=batch_id)
            if output_path:
                self.status_var.set(self.t("Image saved to {path}").format(path=output_path))
                self._discard_active_pending_image(dialog)

        def discard_selected():
            if not self.pending_images:
                return
            self._discard_active_pending_image(dialog)

        def edit_selected():
            if not self.pending_images:
                return
            item = self.pending_images[self.active_preview_index]
            self.pending_image_bytes = item["bytes"]
            self.pending_image_mime = item["mime"]
            dialog.destroy()
            self.open_edit_dialog()

        ttk.Button(action_frame, text=self.t("Save Selected"), command=save_selected).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5)
        )
        ttk.Button(action_frame, text=self.t("Discard Selected"), command=discard_selected).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 5)
        )
        ttk.Button(action_frame, text=self.t("Edit Image"), command=edit_selected).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0)
        )

        render()

    def _discard_active_pending_image(self, dialog=None):
        if not self.pending_images:
            return
        if 0 <= self.active_preview_index < len(self.pending_images):
            self.pending_images.pop(self.active_preview_index)
        if not self.pending_images:
            self.active_preview_index = 0
            self.preview_grid.pack_forget()
            self.preview_label.config(text=self.t("No preview image"), image="")
            self.btn_save_image.config(state=tk.DISABLED)
            self.btn_discard_image.config(state=tk.DISABLED)
            self.btn_edit_image.config(state=tk.DISABLED)
            if dialog:
                dialog.destroy()
            return
        self.active_preview_index %= len(self.pending_images)
        self._render_image_grid()
        if dialog:
            dialog.destroy()
            self.open_image_viewer(self.active_preview_index)

    def _save_image_bytes_to_disk(self, image_bytes: bytes, prefix: str, batch_id: str = None):
        if not image_bytes:
            return None
        save_dir = self._get_current_save_dir()
        os.makedirs(save_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        ext = "png"
        filename = f"{prefix}_{timestamp}.{ext}"
        output_path = os.path.join(save_dir, filename)
        try:
            with open(output_path, "wb") as f:
                f.write(image_bytes)
        except Exception as e:
            messagebox.showerror(self.t("Error"), str(e))
            return None
        # 入库：失败不打断主流程
        try:
            from core import library
            current_prompt = self.output_text.get("1.0", tk.END).strip() if hasattr(self, "output_text") else ""
            library.add_entry(
                generator_type=prefix,
                prompt=current_prompt,
                image_path=output_path,
                source_batch_id=batch_id,
            )
        except Exception as e:
            from core.logging_setup import get_logger
            get_logger("app").warning("library.add_entry failed: %s", e)
        return output_path

    def save_preview_image(self):
        if not self.pending_image_bytes:
            return
        output_path = self._save_image_bytes_to_disk(self.pending_image_bytes, self.pending_image_prefix)
        if output_path:
            self.status_var.set(self.t("Image saved to {path}").format(path=output_path))
            self.discard_preview_image()

    def discard_preview_image(self):
        self.pending_image_bytes = None
        self.pending_image_mime = None
        self.pending_images = []
        self.preview_photo = None
        self.edit_undo_stack.clear()
        self.preview_label.config(text=self.t("No preview image"), image="")
        self.preview_label.pack(fill=tk.BOTH, expand=False, pady=(5, 10))
        self.preview_grid.pack_forget()
        self.btn_save_image.config(state=tk.DISABLED)
        self.btn_discard_image.config(state=tk.DISABLED)
        self.btn_edit_image.config(state=tk.DISABLED)
        self.btn_undo_edit.config(state=tk.DISABLED)
        self.status_var.set(self.t("Image discarded."))

    def undo_edit_image(self):
        if not self.edit_undo_stack:
            return
        prev = self.edit_undo_stack.pop()
        self.pending_image_bytes = prev["bytes"]
        self.pending_image_mime = prev["mime"]
        self.pending_image_prefix = self.get_current_module_prefix()
        self.show_preview_image()
        self._refresh_undo_button()
        depth = len(self.edit_undo_stack)
        if depth > 0:
            self.status_var.set(self.t("Reverted to previous version. {n} more undo(s) available.").format(n=depth))
        else:
            self.status_var.set(self.t("Reverted to original image."))

    def _refresh_undo_button(self):
        if self.edit_undo_stack:
            self.btn_undo_edit.config(state=tk.NORMAL)
        else:
            self.btn_undo_edit.config(state=tk.DISABLED)

    def get_current_module_prefix(self):
        current = self.notebook.select()
        if current == str(self.tab_spaceship):
            return "spaceship"
        if hasattr(self, "tab_mecha") and current == str(self.tab_mecha):
            return "mecha"
        if hasattr(self, "tab_mecha_part") and current == str(self.tab_mecha_part):
            return "mecha_part"
        if hasattr(self, "tab_ship") and current == str(self.tab_ship):
            return "ship"
        if current == str(self.tab_items):
            return "items"
        if current == str(self.tab_characters):
            return "character"
        if current == str(self.tab_clothing):
            return "clothing"
        if current == str(self.tab_slicer):
            return "slicer"
        if current == str(self.tab_curation):
            return "curation"
        if hasattr(self, "tab_library") and current == str(self.tab_library):
            return "library"
        return "gemini"

    # Note: generate_item_prompt and run_slicer are now threaded versions above

    def set_output(self, text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def copy_to_clipboard(self):
        content = self.output_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo(self.t("Copied"), self.t("Prompt copied to clipboard!"))

if __name__ == "__main__":
    from core.logging_setup import init_app_logging, get_logger
    log_path = init_app_logging()
    log = get_logger("app")
    log.info("Starting Application... log file: %s", log_path)
    try:
        root = tk.Tk()
        try:
            root.tk.call('source', 'azure.tcl')
        except Exception:
            pass

        log.info("Initializing App Logic")
        app = PromptApp(root)
        log.info("Entering Main Loop")
        root.mainloop()
    except Exception as e:
        log.exception("CRITICAL ERROR during startup or main loop")
        from paths import user_data_path
        import traceback
        err_msg = traceback.format_exc()
        with open(user_data_path("crash.log"), "w") as f:
            f.write(err_msg)
        try:
            messagebox.showerror("Critical Error", f"Application Crashing:\n{e}\n\nSee crash.log for details.")
        except Exception:
            pass
