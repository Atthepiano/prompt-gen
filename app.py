import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor, as_completed
import prompt_generator as pg
import item_generator as ig
import character_generator as cg
import gemini_service as gs
import slicer_tool as st
import curation_tool as ct
import json
import os
import mimetypes
import threading
import io
import time

APP_CONFIG_PATH = "config.json"

UI_TEXTS_ZH = {
    "Spaceship Prompt Generator": "飞船提示词生成器",
    "Spaceship Components": "飞船组件",
    "Item Icons": "物品图标",
    "Character Prompts": "角色提示词",
    "Image Slicer": "图片切分",
    "Asset Curation": "资产整理",
    "Settings": "设置",
    "Generated Output / Logs:": "生成输出 / 日志：",
    "Copy to Clipboard": "复制到剪贴板",
    "Generate Image (Gemini)": "使用 Gemini 生成图片",
    "Image Preview": "图片预览",
    "No preview image": "暂无预览图片",
    "Save Image": "保存图片",
    "Discard Image": "丢弃图片",
    "Edit Image": "改图",
    "Concurrent Images:": "并发生成：",
    "Grid View": "网格视图",
    "Previous": "上一张",
    "Next": "下一张",
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
    "2. Smart Naming Options:": "2. 智能命名选项：",
    "Use CSV for Filenames (Smart Naming)": "使用 CSV 生成文件名（智能命名）",
    "Auto-Translate Filenames (ZH -> EN)": "自动翻译文件名（中 -> 英）",
    "Remove Background": "移除背景",
    "Normalize Size & Position (Trim & Center 90%)": "标准化尺寸与位置（裁切并居中 90%）",
    "SLICE INTO 64 ICONS": "切分为 64 个图标",
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
    "Gemini API Key:": "Gemini API Key：",
    "Gemini Model:": "Gemini 模型：",
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
    "No prompt content to send.": "没有可发送的提示词内容。",
    "Settings saved. Restart the app to apply language changes.": "设置已保存。请重启应用以应用语言变更。",
    "Settings saved.": "设置已保存。",
    "Please add at least one source folder.": "请至少添加一个源文件夹。",
    "Please select a target folder.": "请选择目标文件夹。",
    "Failed to copy file.": "复制文件失败。",
    "Could not read items from CSV.": "无法从 CSV 读取物品。",
    "{count} files selected": "已选择 {count} 个文件",
    "Failed to save settings.": "保存设置失败。",
    "Processed {success}/{total} files successfully.": "成功处理 {success}/{total} 个文件。",
    "Errors:": "错误：",
    "[Setup Required]": "【需要设置】",
    "CSV Detected: {path}": "检测到 CSV：{path}",
    "Error: CSV not found at {path}": "错误：未找到 CSV：{path}",
    "Error loading image": "加载图片出错",
}

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
        self.gemini_api_key = self.config.get("gemini_api_key", "")
        self.gemini_model = self.config.get("gemini_model", gs.DEFAULT_MODEL)
        self.image_save_dir = self.config.get("image_save_dir", "outputs")
        
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

        # Tab 2: Item Icons
        self.tab_items = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_items, text=self.t("Item Icons"))
        
        # Tab 3: Character Prompts
        self.tab_characters = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_characters, text=self.t("Character Prompts"))

        # Tab 4: Image Slicer
        self.tab_slicer = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_slicer, text=self.t("Image Slicer"))

        # Tab 5: Asset Curation
        self.tab_curation = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_curation, text=self.t("Asset Curation"))

        # Tab 6: Settings
        self.tab_settings = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_settings, text=self.t("Settings"))

        # --- Setup Tab 1: Spaceship Controls ---
        self.setup_spaceship_tab()

        # --- Setup Tab 2: Item Controls ---
        self.setup_item_tab()
        
        # --- Setup Tab 3: Character Controls ---
        self.setup_character_tab()
        
        # --- Setup Tab 4: Slicer Controls ---
        self.setup_slicer_tab()

        # --- Setup Tab 5: Curation Controls ---
        self.curator = ct.AssetCurator()
        self.curation_queue = [] # List of filenames to process
        self.current_curation_index = 0
        self.setup_curation_tab()
        
        # --- Setup Tab 6: Settings ---
        self.setup_settings_tab()

        # --- Output Area (Right) ---
        self.lbl_output_header = ttk.Label(right_frame, text=self.t("Generated Output / Logs:"), font=("Arial", 12, "bold"))
        self.lbl_output_header.pack(anchor="w")
        
        self.output_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

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
        self.btn_edit_image.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

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
        self.preview_photo = None
        self.pending_images = []
        self.preview_thumbnails = []
        self.active_preview_index = 0

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

    def setup_spaceship_tab(self):
        parent = self.tab_spaceship
        
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
        parent = self.tab_items
        
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
        parent = self.tab_characters
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text=self.t("Character Prompt Generation"), font=("Arial", 14, "bold")).pack(anchor="w")
        ttk.Label(header, text=self.t("Build a modular character prompt for retro sci-fi anime portraits."), wraplength=480).pack(anchor="w")

        main = ttk.Frame(parent)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
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
        self.age_scale = ttk.Scale(
            age_frame,
            from_=10,
            to=60,
            orient=tk.HORIZONTAL,
            command=lambda _=None: self._update_age_label(),
        )
        self.age_scale.set(self.age_var.get())
        self.age_scale.grid(row=0, column=0, sticky="ew")
        self.age_value_label = ttk.Label(age_frame, text="")
        self.age_value_label.grid(row=0, column=1, sticky="e", padx=(6, 0))
        self._update_age_label()

        ttk.Label(frame_base, text=self.t("Profession:")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        profession_options = cg.get_profession_options(self.ui_lang)
        self.profession_var = tk.StringVar(value=profession_options[0] if profession_options else "")
        self.profession_combo = ttk.Combobox(frame_base, textvariable=self.profession_var, state="readonly")
        self.profession_combo["values"] = profession_options
        self.profession_combo.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))
        self.profession_combo.bind("<<ComboboxSelected>>", self.update_outfit_options)

        ttk.Label(frame_base, text=self.t("Custom Profession:")).grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.custom_profession_var = tk.StringVar()
        ttk.Entry(frame_base, textvariable=self.custom_profession_var).grid(row=1, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Body Type:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        body_type_options = cg.get_body_type_options(self.ui_lang)
        self.body_type_var = tk.StringVar(value=body_type_options[0] if body_type_options else "")
        self.body_type_combo = ttk.Combobox(frame_base, textvariable=self.body_type_var, state="readonly")
        self.body_type_combo["values"] = body_type_options
        self.body_type_combo.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Skin Tone:")).grid(row=2, column=2, sticky="w", pady=(6, 0))
        skin_tone_options = cg.get_skin_tone_options(self.ui_lang)
        self.skin_tone_var = tk.StringVar(value=skin_tone_options[0] if skin_tone_options else "")
        self.skin_tone_combo = ttk.Combobox(frame_base, textvariable=self.skin_tone_var, state="readonly")
        self.skin_tone_combo["values"] = skin_tone_options
        self.skin_tone_combo.grid(row=2, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Framing:")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        framing_options = cg.get_framing_options(self.ui_lang)
        default_framing = ""
        if self.ui_lang == "zh":
            default_framing = next((f for f in framing_options if "胸像" in f), "")
        else:
            default_framing = next((f for f in framing_options if "bust portrait" in f), "")
        self.framing_var = tk.StringVar(value=default_framing or (framing_options[0] if framing_options else ""))
        self.framing_combo = ttk.Combobox(frame_base, textvariable=self.framing_var, state="readonly")
        self.framing_combo["values"] = framing_options
        self.framing_combo.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Aspect Ratio:")).grid(row=3, column=2, sticky="w", pady=(6, 0))
        aspect_ratio_options = cg.get_aspect_ratio_options(self.ui_lang)
        default_ratio = next((r for r in aspect_ratio_options if "1:1" in r), "")
        self.aspect_ratio_var = tk.StringVar(value=default_ratio or (aspect_ratio_options[0] if aspect_ratio_options else ""))
        self.aspect_ratio_combo = ttk.Combobox(frame_base, textvariable=self.aspect_ratio_var, state="readonly")
        self.aspect_ratio_combo["values"] = aspect_ratio_options
        self.aspect_ratio_combo.grid(row=3, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Expression:")).grid(row=4, column=0, sticky="w", pady=(6, 0))
        expression_options = cg.get_expression_options(self.ui_lang)
        self.expression_var = tk.StringVar(value=expression_options[0] if expression_options else "")
        self.expression_combo = ttk.Combobox(frame_base, textvariable=self.expression_var, state="readonly")
        self.expression_combo["values"] = expression_options
        self.expression_combo.grid(row=4, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_base, text=self.t("Gaze:")).grid(row=4, column=2, sticky="w", pady=(6, 0))
        gaze_options = cg.get_gaze_options(self.ui_lang)
        self.gaze_var = tk.StringVar(value=gaze_options[0] if gaze_options else "")
        self.gaze_combo = ttk.Combobox(frame_base, textvariable=self.gaze_var, state="readonly")
        self.gaze_combo["values"] = gaze_options
        self.gaze_combo.grid(row=4, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        frame_base.columnconfigure(1, weight=1)
        frame_base.columnconfigure(3, weight=1)

        # --- Hair ---
        frame_hair = ttk.LabelFrame(left_col, text=self.t("Hair"), padding=6)
        frame_hair.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame_hair, text=self.t("Hair Style:")).grid(row=0, column=0, sticky="w")
        hair_style_options = cg.get_hair_style_options(self.ui_lang)
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
        for i in range(self.artist_list.size()):
            self.artist_list.selection_set(i)

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

        # --- Outfit ---
        frame_outfit = ttk.LabelFrame(right_col, text=self.t("Outfit"), padding=6)
        frame_outfit.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        frame_outfit.columnconfigure(1, weight=1)
        frame_outfit.columnconfigure(3, weight=1)

        ttk.Label(frame_outfit, text=self.t("Outfit Type:")).grid(row=0, column=0, sticky="w")
        outfit_type_options = cg.get_outfit_type_options(lang=self.ui_lang)
        self.outfit_type_var = tk.StringVar(value=outfit_type_options[0] if outfit_type_options else "")
        self.outfit_type_combo = ttk.Combobox(frame_outfit, textvariable=self.outfit_type_var, state="readonly")
        self.outfit_type_combo["values"] = outfit_type_options
        self.outfit_type_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_outfit, text=self.t("Outfit Colors:")).grid(row=0, column=2, sticky="w")
        self.outfit_colors = []
        color_controls = ttk.Frame(frame_outfit)
        color_controls.grid(row=0, column=3, sticky="ew", padx=(5, 0))
        color_controls.columnconfigure(0, weight=1)
        self.btn_add_color = ttk.Button(color_controls, text=self.t("Add Color"), command=self.add_outfit_color, width=12)
        self.btn_add_color.grid(row=0, column=0, sticky="w")
        self.btn_clear_colors = ttk.Button(color_controls, text=self.t("Clear Colors"), command=self.clear_outfit_colors, width=12)
        self.btn_clear_colors.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.color_preview_frame = ttk.Frame(frame_outfit)
        self.color_preview_frame.grid(row=1, column=2, columnspan=2, sticky="ew", pady=(4, 0))
        self.color_preview_frame.columnconfigure(0, weight=1)

        ttk.Label(frame_outfit, text=self.t("Material Finish:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        material_options = cg.get_material_options(self.ui_lang)
        self.material_finish_var = tk.StringVar(value=material_options[0] if material_options else "")
        self.material_finish_combo = ttk.Combobox(frame_outfit, textvariable=self.material_finish_var, state="readonly")
        self.material_finish_combo["values"] = material_options
        self.material_finish_combo.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        apparel_frame = ttk.Frame(frame_outfit)
        apparel_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(6, 0), padx=(0, 6))
        ttk.Label(apparel_frame, text=self.t("Apparel Details")).grid(row=0, column=0, sticky="w")
        apparel_list_frame = ttk.Frame(apparel_frame)
        apparel_list_frame.grid(row=1, column=0, sticky="nsew")
        self.apparel_list = tk.Listbox(
            apparel_list_frame,
            selectmode=tk.MULTIPLE,
            height=6,
            exportselection=False,
        )
        for option in cg.get_apparel_detail_options(self.ui_lang):
            self.apparel_list.insert(tk.END, option)
        self.apparel_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_apparel = ttk.Scrollbar(apparel_list_frame, orient="vertical", command=self.apparel_list.yview)
        scroll_apparel.pack(side=tk.RIGHT, fill=tk.Y)
        self.apparel_list.config(yscrollcommand=scroll_apparel.set)
        apparel_frame.columnconfigure(0, weight=1)

        accessory_frame = ttk.Frame(frame_outfit)
        accessory_frame.grid(row=3, column=2, columnspan=2, sticky="nsew", pady=(6, 0), padx=(6, 0))
        ttk.Label(accessory_frame, text=self.t("Accessories")).grid(row=0, column=0, sticky="w")
        accessory_list_frame = ttk.Frame(accessory_frame)
        accessory_list_frame.grid(row=1, column=0, sticky="nsew")
        self.accessory_list = tk.Listbox(
            accessory_list_frame,
            selectmode=tk.MULTIPLE,
            height=6,
            exportselection=False,
        )
        for option in cg.get_accessory_options(self.ui_lang):
            self.accessory_list.insert(tk.END, option)
        self.accessory_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_acc = ttk.Scrollbar(accessory_list_frame, orient="vertical", command=self.accessory_list.yview)
        scroll_acc.pack(side=tk.RIGHT, fill=tk.Y)
        self.accessory_list.config(yscrollcommand=scroll_acc.set)
        accessory_frame.columnconfigure(0, weight=1)

        # --- Misc ---
        frame_misc = ttk.LabelFrame(right_col, text=self.t("Misc"), padding=6)
        frame_misc.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        frame_misc.columnconfigure(0, weight=1)

        ttk.Label(frame_misc, text=self.t("Misc Details")).grid(row=0, column=0, sticky="w")
        misc_list_frame = ttk.Frame(frame_misc)
        misc_list_frame.grid(row=1, column=0, sticky="nsew")
        self.misc_list = tk.Listbox(
            misc_list_frame,
            selectmode=tk.MULTIPLE,
            height=6,
            exportselection=False,
        )
        for option in cg.get_misc_options(self.ui_lang):
            self.misc_list.insert(tk.END, option)
        self.misc_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        misc_scroll = ttk.Scrollbar(misc_list_frame, orient="vertical", command=self.misc_list.yview)
        misc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.misc_list.config(yscrollcommand=misc_scroll.set)

        ttk.Label(frame_misc, text=self.t("Custom misc (comma separated):")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.custom_misc_var = tk.StringVar()
        ttk.Entry(frame_misc, textvariable=self.custom_misc_var).grid(row=3, column=0, sticky="ew", pady=(2, 0))

        # --- Extra Modifiers ---
        action_bar = ttk.Frame(parent)
        action_bar.pack(fill=tk.X, pady=(2, 0))
        action_bar.columnconfigure(1, weight=1)

        ttk.Label(action_bar, text=self.t("Extra modifiers (optional):")).grid(row=0, column=0, sticky="w")
        self.extra_modifiers_var = tk.StringVar()
        ttk.Entry(action_bar, textvariable=self.extra_modifiers_var).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.update_outfit_options()
        self._bind_character_auto_update()
        self.schedule_character_prompt_update()
        
    def setup_settings_tab(self):
        parent = self.tab_settings
        
        ttk.Label(parent, text=self.t("Settings Panel"), font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Gemini API
        frame_api = ttk.LabelFrame(parent, text="Gemini", padding=5)
        frame_api.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_api, text=self.t("Gemini API Key:")).grid(row=0, column=0, sticky="w")
        self.api_key_var = tk.StringVar(value=self.gemini_api_key)
        ttk.Entry(frame_api, textvariable=self.api_key_var).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        ttk.Label(frame_api, text=self.t("Gemini Model:")).grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.model_var = tk.StringVar(value=self.gemini_model)
        model_options = list(gs.IMAGE_MODELS)
        if self.gemini_model and self.gemini_model not in model_options and self.gemini_model.replace("models/", "") not in model_options:
            model_options.insert(0, self.gemini_model.replace("models/", ""))
        self.model_combo = ttk.Combobox(frame_api, textvariable=self.model_var, state="readonly")
        self.model_combo["values"] = model_options
        self.model_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
        
        frame_api.columnconfigure(1, weight=1)
        
        # Output directory
        frame_out = ttk.LabelFrame(parent, text=self.t("Image Save Directory:"), padding=5)
        frame_out.pack(fill=tk.X, pady=(0, 10))
        
        self.save_dir_var = tk.StringVar(value=self.image_save_dir)
        ttk.Entry(frame_out, textvariable=self.save_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(frame_out, text=self.t("Browse..."), command=self.select_save_dir).pack(side=tk.LEFT, padx=(5, 0))
        
        # Language
        frame_lang = ttk.LabelFrame(parent, text=self.t("UI Language:"), padding=5)
        frame_lang.pack(fill=tk.X, pady=(0, 10))
        
        self.lang_var = tk.StringVar(value=self.t("Chinese") if self.ui_lang == "zh" else self.t("English"))
        lang_combo = ttk.Combobox(frame_lang, textvariable=self.lang_var, state="readonly")
        lang_combo["values"] = [self.t("English"), self.t("Chinese")]
        lang_combo.pack(fill=tk.X)
        
        ttk.Button(parent, text=self.t("Save Settings"), command=self.save_settings).pack(fill=tk.X, pady=(10, 0), ipady=6)

    def setup_slicer_tab(self):
        parent = self.tab_slicer
        
        ttk.Label(parent, text=self.t("Image Slicer (8x8 Grid)"), font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(parent, text=self.t("Splits an 8x8 grid image into 64 icons."), wraplength=380).pack(anchor="w", pady=(0, 10))
        
        # --- Image Selection ---
        ttk.Label(parent, text=self.t("1. Select Grid Image(s):"), font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Button(parent, text=self.t("Select Image File(s)..."), command=self.select_images_for_slicer).pack(fill=tk.X, pady=(5, 5))
        self.lbl_selected_file = ttk.Label(parent, text=self.t("No file selected"), foreground="gray", wraplength=400)
        self.lbl_selected_file.pack(anchor="w", pady=(0, 10))
        
        # --- Advanced Config ---
        frame_config = ttk.LabelFrame(parent, text=self.t("Advanced Configuration"), padding=5)
        frame_config.pack(fill=tk.X, pady=5)
        
        # Grid Size
        ttk.Label(frame_config, text=self.t("Grid Size (Row x Col):")).pack(side=tk.LEFT)
        self.var_grid_size = tk.StringVar(value="8")
        ttk.Entry(frame_config, textvariable=self.var_grid_size, width=5).pack(side=tk.LEFT, padx=5)
        
        # Scale Factor
        ttk.Label(frame_config, text=self.t("Norm Scale (0.1-1.0):")).pack(side=tk.LEFT, padx=(10, 0))
        self.var_scale_factor = tk.DoubleVar(value=0.85)
        ttk.Entry(frame_config, textvariable=self.var_scale_factor, width=5).pack(side=tk.LEFT, padx=5)
        
        # --- Naming Options ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(parent, text=self.t("2. Smart Naming Options:"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(5,0))
        
        # Toggle Smart Naming
        self.var_use_csv_naming = tk.BooleanVar(value=True)
        cb_naming = ttk.Checkbutton(parent, text=self.t("Use CSV for Filenames (Smart Naming)"), variable=self.var_use_csv_naming, command=self.toggle_smart_naming)
        cb_naming.pack(anchor="w")
        
        # Toggle Filename Translation
        self.var_translate_filename = tk.BooleanVar(value=True)
        self.cb_trans_file = ttk.Checkbutton(parent, text=self.t("Auto-Translate Filenames (ZH -> EN)"), variable=self.var_translate_filename)
        self.cb_trans_file.pack(anchor="w", padx=(20, 0))
        
        # Cache Checkbox (Mirrored)
        self.cb_cache_file = ttk.Checkbutton(parent, text=self.t("Write Translation Result into CSV (Cache)"), variable=self.var_cache_translation)
        self.cb_cache_file.pack(anchor="w", padx=(20, 0), pady=(2,0))
        
        # Toggle Background Removal
        self.var_remove_bg = tk.BooleanVar(value=False)
        # Toggle Normalization
        self.var_normalize = tk.BooleanVar(value=False)
        
        # Check rembg availability
        venv_exists = False
        import sys
        if getattr(sys, 'frozen', False):
             # In frozen mode, assume valid if exe exists alongside
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
        self.cb_remove_bg.pack(anchor="w", pady=(5, 0))
        
        # Always enable
        self.cb_remove_bg.config(state=tk.NORMAL) 
        
        if not venv_exists:
             self.cb_remove_bg.config(state=tk.NORMAL) # Let user try it or see warning

        # Normalize Checkbox

        # Normalize Checkbox
        self.cb_normalize = ttk.Checkbutton(parent, text=self.t("Normalize Size & Position (Trim & Center 90%)"), variable=self.var_normalize)
        self.cb_normalize.pack(anchor="w", pady=(2, 0))
        
        # CSV Selection
        frame_csv = ttk.Frame(parent)
        frame_csv.pack(fill=tk.X, pady=(5, 0))
        self.btn_select_csv = ttk.Button(frame_csv, text=self.t("Select CSV..."), command=self.select_csv_for_slicer, width=15)
        self.btn_select_csv.pack(side=tk.LEFT)
        self.lbl_selected_csv = ttk.Label(frame_csv, text=os.path.basename(self.slicer_csv_path), foreground="blue")
        self.lbl_selected_csv.pack(side=tk.LEFT, padx=5)
        
        # --- Preview & Action ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        
        # Preview Area
        self.lbl_preview = ttk.Label(parent, text="[Preview]", background="#eeeeee", anchor="center")
        self.lbl_preview.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Slice Button
        # Point to Threaded version
        self.btn_slice = ttk.Button(parent, text=self.t("SLICE INTO 64 ICONS"), command=self.run_slicer_threaded, state=tk.DISABLED)
        self.btn_slice.pack(fill=tk.X, pady=(10, 0), ipady=10)

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

    def save_settings(self):
        previous_lang = self.ui_lang
        selected_lang = "zh" if self.lang_var.get() == self.t("Chinese") else "en"
        
        self.gemini_api_key = self.api_key_var.get().strip()
        self.gemini_model = self.model_var.get().strip() or gs.DEFAULT_MODEL
        self.image_save_dir = self.save_dir_var.get().strip() or "outputs"
        
        self.ui_lang = selected_lang
        
        data = {
            "gemini_api_key": self.gemini_api_key,
            "gemini_model": self.gemini_model,
            "image_save_dir": self.image_save_dir,
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
        
        # Get Config
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
            cols = 8 # Default
            
        try:
             scale = self.var_scale_factor.get()
        except:
             scale = 0.85
        
        success_count = 0
        errors = []
        
        total = len(self.slicer_files)
        
        for i, fp in enumerate(self.slicer_files):
            self.status_var.set(f"{self.t('Processing...')} ({i+1}/{total}): {os.path.basename(fp)}...")
            try:
                success, msg, count = st.slice_image(
                                                   image_path=fp, 
                                                   grid_rows=rows, 
                                                   grid_cols=cols,
                                                   csv_path=csv_to_use, 
                                                   translate_mode=do_translate,
                                                   remove_bg=self.var_remove_bg.get(),
                                                   cache_mode=self.var_cache_translation.get(),
                                                   normalize_mode=self.var_normalize.get(),
                                                   scale_factor=scale)
                if success:
                    success_count += 1
                else:
                    errors.append(f"{os.path.basename(fp)}: {msg}")
            except Exception as e:
                errors.append(f"{os.path.basename(fp)}: {str(e)}")
                
        self.root.after(0, lambda: self.set_ui_busy(False, self.t("Batch Complete")))
        
        summary = self.t("Processed {success}/{total} files successfully.").format(success=success_count, total=total)
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

    def add_outfit_color(self):
        if len(self.outfit_colors) >= 5:
            messagebox.showinfo(self.t("Outfit Colors:"), self.t("Max colors reached"))
            return
        color = colorchooser.askcolor(title=self.t("Outfit Colors:"))[1]
        if color:
            self.outfit_colors.append(color)
            self._refresh_outfit_colors()
            self.schedule_character_prompt_update()

    def clear_outfit_colors(self):
        if not self.outfit_colors:
            return
        self.outfit_colors = []
        self._refresh_outfit_colors()
        self.schedule_character_prompt_update()

    def _refresh_outfit_colors(self):
        for child in self.color_preview_frame.winfo_children():
            child.destroy()
        for idx, color in enumerate(self.outfit_colors):
            fg = "#000000"
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
                fg = "#000000" if luminance > 0.6 else "#ffffff"
            except Exception:
                fg = "#000000"
            chip = tk.Label(self.color_preview_frame, text=color.upper(), bg=color, fg=fg, padx=6, pady=2)
            chip.grid(row=0, column=idx, sticky="w", padx=(0, 4))

    def update_outfit_options(self, event=None):
        profession = self.profession_var.get()
        options = cg.get_outfit_type_options(profession, self.ui_lang)
        self.outfit_type_combo["values"] = options
        if self.outfit_type_var.get() not in options:
            self.outfit_type_var.set(options[0] if options else "")
        self.schedule_character_prompt_update()

    def _bind_character_auto_update(self):
        vars_to_watch = [
            self.gender_var,
            self.age_var,
            self.profession_var,
            self.custom_profession_var,
            self.body_type_var,
            self.skin_tone_var,
            self.framing_var,
            self.aspect_ratio_var,
            self.expression_var,
            self.gaze_var,
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
            self.outfit_type_var,
            self.material_finish_var,
            self.custom_misc_var,
            self.extra_modifiers_var,
        ]
        for var in vars_to_watch:
            var.trace_add("write", self.schedule_character_prompt_update)

        listboxes = [
            self.face_feature_list,
            self.apparel_list,
            self.accessory_list,
            self.misc_list,
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
            apparel_details=prompt_inputs["apparel_details"],
            accessories=prompt_inputs["accessories"],
            misc_details=prompt_inputs["misc_details"],
            artists=prompt_inputs["artists"],
            include_style=include_style,
            include_background=include_background,
            include_mood=include_mood,
            include_extra_modifiers=include_extra_modifiers,
        )
        self.set_output(prompt)

    def _collect_character_prompt_inputs(self):
        face_features = [self.face_feature_list.get(i) for i in self.face_feature_list.curselection()]
        apparel_details = [self.apparel_list.get(i) for i in self.apparel_list.curselection()]
        accessories = [self.accessory_list.get(i) for i in self.accessory_list.curselection()]
        misc_details = [self.misc_list.get(i) for i in self.misc_list.curselection()]
        artists = [self.artist_label_map.get(self.artist_list.get(i), self.artist_list.get(i)) for i in self.artist_list.curselection()]
        custom_misc = self.custom_misc_var.get().strip()
        if custom_misc:
            misc_details.extend([f.strip() for f in custom_misc.split(",") if f.strip()])
        return {
            "face_features": face_features,
            "apparel_details": apparel_details,
            "accessories": accessories,
            "misc_details": misc_details,
            "artists": artists,
        }

    def _build_character_prompt(
        self,
        face_features,
        apparel_details,
        accessories,
        misc_details,
        artists,
        include_style: bool,
        include_background: bool = True,
        include_mood: bool = True,
        include_extra_modifiers: bool = True,
    ):
        return cg.generate_character_prompt(
            gender=self.gender_var.get(),
            profession=self.profession_var.get(),
            age=self.age_var.get(),
            framing=self.framing_var.get(),
            aspect_ratio=self.aspect_ratio_var.get(),
            expression=self.expression_var.get(),
            gaze=self.gaze_var.get(),
            appearance_features=face_features,
            apparel_details=apparel_details,
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
            outfit_type=self.outfit_type_var.get(),
            material_finish=self.material_finish_var.get(),
            accessories=accessories,
            misc_details=misc_details,
            outfit_colors=self.outfit_colors,
            artists=artists,
            lang=self.ui_lang,
            custom_profession=self.custom_profession_var.get(),
            extra_modifiers=self.extra_modifiers_var.get(),
            include_style=include_style,
            include_background=include_background,
            include_mood=include_mood,
            include_extra_modifiers=include_extra_modifiers,
        )
    
    def generate_image_threaded(self):
        prompt = self.output_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror(self.t("Error"), self.t("No prompt content to send."))
            return
        
        api_key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
        if not api_key:
            messagebox.showerror(self.t("Error"), self.t("Gemini API key is missing."))
            return

        reference_images = self._get_style_reference_images()
        if (
            reference_images
            and self.notebook.select() == str(self.tab_characters)
            and self.style_ref_only_mode.get()
        ):
            prompt_inputs = self._collect_character_prompt_inputs()
            prompt = self._build_character_prompt(
                face_features=prompt_inputs["face_features"],
                apparel_details=prompt_inputs["apparel_details"],
                accessories=prompt_inputs["accessories"],
                misc_details=prompt_inputs["misc_details"],
                artists=prompt_inputs["artists"],
                include_style=False,
                include_background=True,
                include_mood=False,
                include_extra_modifiers=False,
            ).strip()
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

    def open_edit_dialog(self):
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
        api_key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
        model = self.model_var.get().strip() if hasattr(self, "model_var") else self.gemini_model
        
        try:
            image_bytes, mime_type = gs.generate_image_bytes(
                prompt,
                api_key=api_key,
                model=model,
                reference_images=reference_images,
            )
            self.pending_images = []
            self.pending_image_bytes = image_bytes
            self.pending_image_mime = mime_type
            self.pending_image_prefix = self.get_current_module_prefix()
            self.root.after(0, self.show_preview_image)
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
        api_key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
        if not api_key:
            messagebox.showerror(self.t("Error"), self.t("Gemini API key is missing."))
            return
        self.set_ui_busy(True, self.t("Editing Image..."))
        threading.Thread(target=self._edit_image_task, args=(edit_prompt,), daemon=True).start()

    def _edit_image_task(self, edit_prompt: str):
        api_key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
        model = self.model_var.get().strip() if hasattr(self, "model_var") else self.gemini_model
        image_bytes = self.pending_image_bytes
        image_mime = self.pending_image_mime

        try:
            edited_bytes, mime_type = gs.edit_image_bytes(
                edit_prompt,
                image_bytes=image_bytes,
                image_mime=image_mime,
                api_key=api_key,
                model=model,
            )
            self.pending_image_bytes = edited_bytes
            self.pending_image_mime = mime_type
            self.pending_image_prefix = f"{self.get_current_module_prefix()}_edit"
            self.root.after(0, self.show_preview_image)
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
            self.root.after(0, lambda: self.status_var.set(self.t("Image ready. Use Save/Discard.")))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))

    def _generate_images_task(self, prompt: str, reference_images, count: int):
        api_key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
        model = self.model_var.get().strip() if hasattr(self, "model_var") else self.gemini_model

        def worker():
            return gs.generate_image_bytes(prompt, api_key=api_key, model=model, reference_images=reference_images)

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

        self.pending_images = [{"bytes": b, "mime": m} for b, m in results]
        self.pending_image_bytes = None
        self.pending_image_mime = None
        self.active_preview_index = 0
        self.root.after(0, self.show_preview_images)
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
        dialog.geometry("720x720")
        dialog.transient(self.root)
        dialog.grab_set()

        img_label = ttk.Label(dialog, anchor="center")
        img_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        nav_frame = ttk.Frame(dialog)
        nav_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        def render():
            try:
                item = self.pending_images[self.active_preview_index]
                img = Image.open(io.BytesIO(item["bytes"]))
                img.thumbnail((680, 640))
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

        render()

    def save_preview_image(self):
        if not self.pending_image_bytes:
            return
        save_dir = self.save_dir_var.get().strip() if hasattr(self, "save_dir_var") else self.image_save_dir
        save_dir = save_dir or "outputs"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        ext = "png"
        filename = f"{self.pending_image_prefix}_{timestamp}.{ext}"
        output_path = os.path.join(save_dir, filename)
        try:
            with open(output_path, "wb") as f:
                f.write(self.pending_image_bytes)
            self.status_var.set(self.t("Image saved to {path}").format(path=output_path))
            self.discard_preview_image()
        except Exception as e:
            messagebox.showerror(self.t("Error"), str(e))

    def discard_preview_image(self):
        self.pending_image_bytes = None
        self.pending_image_mime = None
        self.pending_images = []
        self.preview_photo = None
        self.preview_label.config(text=self.t("No preview image"), image="")
        self.preview_label.pack(fill=tk.BOTH, expand=False, pady=(5, 10))
        self.preview_grid.pack_forget()
        self.btn_save_image.config(state=tk.DISABLED)
        self.btn_discard_image.config(state=tk.DISABLED)
        self.btn_edit_image.config(state=tk.DISABLED)
        self.status_var.set(self.t("Image discarded."))

    def get_current_module_prefix(self):
        current = self.notebook.select()
        if current == str(self.tab_spaceship):
            return "spaceship"
        if current == str(self.tab_items):
            return "items"
        if current == str(self.tab_characters):
            return "character"
        if current == str(self.tab_slicer):
            return "slicer"
        if current == str(self.tab_curation):
            return "curation"
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
    try:
        print("Starting Application...")
        root = tk.Tk()
        try:
            root.tk.call('source', 'azure.tcl')
        except:
            pass
            
        print("Initializing App Logic...")
        app = PromptApp(root)
        print("Entering Main Loop...")
        root.mainloop()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"CRITICAL ERROR: {err_msg}")
        with open("crash.log", "w") as f:
            f.write(err_msg)
        try:
            messagebox.showerror("Critical Error", f"Application Crashing:\n{e}\n\nSee crash.log for details.")
        except:
            pass

