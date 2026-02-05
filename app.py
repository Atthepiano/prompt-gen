import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from PIL import Image, ImageTk
import prompt_generator as pg
import item_generator as ig
import character_generator as cg
import gemini_service as gs
import slicer_tool as st
import curation_tool as ct
import json
import os
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
    "Core Descriptors": "核心描述",
    "Gender:": "性别：",
    "Age (Fuzzy):": "年龄（模糊）：",
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
    "Eye Color:": "眼睛颜色：",
    "Outfit Palette:": "服装配色：",
    "Material Finish:": "材质质感：",
    "Detail Builder": "细节拼装",
    "Face & Skin": "面部与肤质",
    "Apparel Details": "服装细节",
    "Accessories": "配饰",
    "Tech & Augments": "科技与义体",
    "Marks & Insignia": "标记与徽识",
    "Custom visual details (comma separated):": "自定义外观/服装/标记（逗号分隔）：",
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
        self.root.geometry("1100x900")

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
        
        main_pane.add(left_container, minsize=420)
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

        preview_btn_frame = ttk.Frame(right_frame)
        preview_btn_frame.pack(fill=tk.X, pady=(0, 10))
        self.btn_save_image = ttk.Button(preview_btn_frame, text=self.t("Save Image"), command=self.save_preview_image, state=tk.DISABLED)
        self.btn_save_image.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.btn_discard_image = ttk.Button(preview_btn_frame, text=self.t("Discard Image"), command=self.discard_preview_image, state=tk.DISABLED)
        self.btn_discard_image.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

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
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text=self.t("Character Prompt Generation"), font=("Arial", 14, "bold")).pack(anchor="w")
        ttk.Label(header, text=self.t("Build a modular character prompt for retro sci-fi anime portraits."), wraplength=520).pack(anchor="w")

        main = ttk.Frame(parent)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left_col = ttk.Frame(main)
        right_col = ttk.Frame(main)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # --- Core Descriptors ---
        frame_core = ttk.LabelFrame(left_col, text=self.t("Core Descriptors"), padding=6)
        frame_core.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame_core, text=self.t("Gender:")).grid(row=0, column=0, sticky="w")
        self.gender_var = tk.StringVar(value=cg.get_gender_options()[0])
        self.gender_combo = ttk.Combobox(frame_core, textvariable=self.gender_var, state="readonly")
        self.gender_combo["values"] = cg.get_gender_options()
        self.gender_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_core, text=self.t("Age (Fuzzy):")).grid(row=0, column=2, sticky="w")
        self.age_var = tk.StringVar(value="Adult")
        self.age_combo = ttk.Combobox(frame_core, textvariable=self.age_var, state="readonly")
        self.age_combo["values"] = cg.get_age_options()
        self.age_combo.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        ttk.Label(frame_core, text=self.t("Profession:")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.profession_var = tk.StringVar(value=cg.get_profession_options()[0])
        self.profession_combo = ttk.Combobox(frame_core, textvariable=self.profession_var, state="readonly")
        self.profession_combo["values"] = cg.get_profession_options()
        self.profession_combo.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_core, text=self.t("Custom Profession:")).grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.custom_profession_var = tk.StringVar()
        ttk.Entry(frame_core, textvariable=self.custom_profession_var).grid(row=1, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        frame_core.columnconfigure(1, weight=1)
        frame_core.columnconfigure(3, weight=1)

        # --- Composition ---
        frame_comp = ttk.LabelFrame(left_col, text=self.t("Composition"), padding=6)
        frame_comp.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame_comp, text=self.t("Framing:")).grid(row=0, column=0, sticky="w")
        self.framing_var = tk.StringVar(value="half body portrait")
        self.framing_combo = ttk.Combobox(frame_comp, textvariable=self.framing_var, state="readonly")
        self.framing_combo["values"] = cg.get_framing_options()
        self.framing_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_comp, text=self.t("Aspect Ratio:")).grid(row=0, column=2, sticky="w")
        self.aspect_ratio_var = tk.StringVar(value="2:3 portrait")
        self.aspect_ratio_combo = ttk.Combobox(frame_comp, textvariable=self.aspect_ratio_var, state="readonly")
        self.aspect_ratio_combo["values"] = cg.get_aspect_ratio_options()
        self.aspect_ratio_combo.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        frame_comp.columnconfigure(1, weight=1)
        frame_comp.columnconfigure(3, weight=1)

        # --- Expression ---
        frame_expr = ttk.LabelFrame(left_col, text=self.t("Expression & Gaze"), padding=6)
        frame_expr.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame_expr, text=self.t("Expression:")).grid(row=0, column=0, sticky="w")
        self.expression_var = tk.StringVar(value="serious expression")
        self.expression_combo = ttk.Combobox(frame_expr, textvariable=self.expression_var, state="readonly")
        self.expression_combo["values"] = cg.get_expression_options()
        self.expression_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_expr, text=self.t("Gaze:")).grid(row=0, column=2, sticky="w")
        self.gaze_var = tk.StringVar(value="looking at camera")
        self.gaze_combo = ttk.Combobox(frame_expr, textvariable=self.gaze_var, state="readonly")
        self.gaze_combo["values"] = cg.get_gaze_options()
        self.gaze_combo.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        frame_expr.columnconfigure(1, weight=1)
        frame_expr.columnconfigure(3, weight=1)

        # --- Base Visuals ---
        frame_visual = ttk.LabelFrame(right_col, text=self.t("Base Visuals"), padding=6)
        frame_visual.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame_visual, text=self.t("Body Type:")).grid(row=0, column=0, sticky="w")
        self.body_type_var = tk.StringVar(value=cg.get_body_type_options()[0])
        self.body_type_combo = ttk.Combobox(frame_visual, textvariable=self.body_type_var, state="readonly")
        self.body_type_combo["values"] = cg.get_body_type_options()
        self.body_type_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        ttk.Label(frame_visual, text=self.t("Skin Tone:")).grid(row=0, column=2, sticky="w")
        self.skin_tone_var = tk.StringVar(value=cg.get_skin_tone_options()[0])
        self.skin_tone_combo = ttk.Combobox(frame_visual, textvariable=self.skin_tone_var, state="readonly")
        self.skin_tone_combo["values"] = cg.get_skin_tone_options()
        self.skin_tone_combo.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        ttk.Label(frame_visual, text=self.t("Hair Style:")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.hair_style_var = tk.StringVar(value=cg.get_hair_style_options()[0])
        self.hair_style_combo = ttk.Combobox(frame_visual, textvariable=self.hair_style_var, state="readonly")
        self.hair_style_combo["values"] = cg.get_hair_style_options()
        self.hair_style_combo.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_visual, text=self.t("Hair Color:")).grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.hair_color_var = tk.StringVar(value=cg.get_hair_color_options()[0])
        self.hair_color_combo = ttk.Combobox(frame_visual, textvariable=self.hair_color_var, state="readonly")
        self.hair_color_combo["values"] = cg.get_hair_color_options()
        self.hair_color_combo.grid(row=1, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_visual, text=self.t("Eye Color:")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.eye_color_var = tk.StringVar(value=cg.get_eye_color_options()[0])
        self.eye_color_combo = ttk.Combobox(frame_visual, textvariable=self.eye_color_var, state="readonly")
        self.eye_color_combo["values"] = cg.get_eye_color_options()
        self.eye_color_combo.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        ttk.Label(frame_visual, text=self.t("Outfit Palette:")).grid(row=2, column=2, sticky="w", pady=(6, 0))
        self.outfit_palette_var = tk.StringVar(value=cg.get_outfit_palette_options()[0])
        self.outfit_palette_combo = ttk.Combobox(frame_visual, textvariable=self.outfit_palette_var, state="readonly")
        self.outfit_palette_combo["values"] = cg.get_outfit_palette_options()
        self.outfit_palette_combo.grid(row=2, column=3, sticky="ew", padx=(5, 0), pady=(6, 0))

        ttk.Label(frame_visual, text=self.t("Material Finish:")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.material_finish_var = tk.StringVar(value=cg.get_material_options()[0])
        self.material_finish_combo = ttk.Combobox(frame_visual, textvariable=self.material_finish_var, state="readonly")
        self.material_finish_combo["values"] = cg.get_material_options()
        self.material_finish_combo.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=(6, 0))

        frame_visual.columnconfigure(1, weight=1)
        frame_visual.columnconfigure(3, weight=1)

        # --- Detail Builder ---
        frame_detail = ttk.LabelFrame(right_col, text=self.t("Detail Builder"), padding=6)
        frame_detail.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        frame_detail.columnconfigure((0, 1, 2), weight=1)
        frame_detail.rowconfigure((0, 1), weight=1)

        appearance_frame = ttk.Frame(frame_detail)
        appearance_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        ttk.Label(appearance_frame, text=self.t("Face & Skin")).grid(row=0, column=0, sticky="w")
        appearance_list_frame = ttk.Frame(appearance_frame)
        appearance_list_frame.grid(row=1, column=0, sticky="nsew")
        self.appearance_list = tk.Listbox(appearance_list_frame, selectmode=tk.MULTIPLE, height=6)
        for option in cg.get_appearance_options():
            self.appearance_list.insert(tk.END, option)
        self.appearance_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(appearance_list_frame, orient="vertical", command=self.appearance_list.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.appearance_list.config(yscrollcommand=scroll.set)
        appearance_frame.columnconfigure(0, weight=1)
        appearance_frame.rowconfigure(1, weight=1)

        apparel_frame = ttk.Frame(frame_detail)
        apparel_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=(0, 6))
        ttk.Label(apparel_frame, text=self.t("Apparel Details")).grid(row=0, column=0, sticky="w")
        apparel_list_frame = ttk.Frame(apparel_frame)
        apparel_list_frame.grid(row=1, column=0, sticky="nsew")
        self.apparel_list = tk.Listbox(apparel_list_frame, selectmode=tk.MULTIPLE, height=6)
        for option in cg.get_apparel_detail_options():
            self.apparel_list.insert(tk.END, option)
        self.apparel_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_apparel = ttk.Scrollbar(apparel_list_frame, orient="vertical", command=self.apparel_list.yview)
        scroll_apparel.pack(side=tk.RIGHT, fill=tk.Y)
        self.apparel_list.config(yscrollcommand=scroll_apparel.set)
        apparel_frame.columnconfigure(0, weight=1)
        apparel_frame.rowconfigure(1, weight=1)

        accessory_frame = ttk.Frame(frame_detail)
        accessory_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=(0, 6))
        ttk.Label(accessory_frame, text=self.t("Accessories")).grid(row=0, column=0, sticky="w")
        accessory_list_frame = ttk.Frame(accessory_frame)
        accessory_list_frame.grid(row=1, column=0, sticky="nsew")
        self.accessory_list = tk.Listbox(accessory_list_frame, selectmode=tk.MULTIPLE, height=6)
        for option in cg.get_accessory_options():
            self.accessory_list.insert(tk.END, option)
        self.accessory_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_acc = ttk.Scrollbar(accessory_list_frame, orient="vertical", command=self.accessory_list.yview)
        scroll_acc.pack(side=tk.RIGHT, fill=tk.Y)
        self.accessory_list.config(yscrollcommand=scroll_acc.set)
        accessory_frame.columnconfigure(0, weight=1)
        accessory_frame.rowconfigure(1, weight=1)

        tech_frame = ttk.Frame(frame_detail)
        tech_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        ttk.Label(tech_frame, text=self.t("Tech & Augments")).grid(row=0, column=0, sticky="w")
        tech_list_frame = ttk.Frame(tech_frame)
        tech_list_frame.grid(row=1, column=0, sticky="nsew")
        self.tech_list = tk.Listbox(tech_list_frame, selectmode=tk.MULTIPLE, height=6)
        for option in cg.get_tech_detail_options():
            self.tech_list.insert(tk.END, option)
        self.tech_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_tech = ttk.Scrollbar(tech_list_frame, orient="vertical", command=self.tech_list.yview)
        scroll_tech.pack(side=tk.RIGHT, fill=tk.Y)
        self.tech_list.config(yscrollcommand=scroll_tech.set)
        tech_frame.columnconfigure(0, weight=1)
        tech_frame.rowconfigure(1, weight=1)

        mark_frame = ttk.Frame(frame_detail)
        mark_frame.grid(row=1, column=1, sticky="nsew", padx=6)
        ttk.Label(mark_frame, text=self.t("Marks & Insignia")).grid(row=0, column=0, sticky="w")
        mark_list_frame = ttk.Frame(mark_frame)
        mark_list_frame.grid(row=1, column=0, sticky="nsew")
        self.mark_list = tk.Listbox(mark_list_frame, selectmode=tk.MULTIPLE, height=6)
        for option in cg.get_marking_options():
            self.mark_list.insert(tk.END, option)
        self.mark_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_mark = ttk.Scrollbar(mark_list_frame, orient="vertical", command=self.mark_list.yview)
        scroll_mark.pack(side=tk.RIGHT, fill=tk.Y)
        self.mark_list.config(yscrollcommand=scroll_mark.set)
        mark_frame.columnconfigure(0, weight=1)
        mark_frame.rowconfigure(1, weight=1)

        # --- Custom Inputs & Actions ---
        bottom_bar = ttk.Frame(parent)
        bottom_bar.pack(fill=tk.X, pady=(0, 6))
        bottom_bar.columnconfigure(1, weight=1)
        bottom_bar.columnconfigure(3, weight=1)

        ttk.Label(bottom_bar, text=self.t("Custom visual details (comma separated):")).grid(row=0, column=0, sticky="w")
        self.custom_details_var = tk.StringVar()
        ttk.Entry(bottom_bar, textvariable=self.custom_details_var).grid(row=0, column=1, sticky="ew", padx=(6, 12))

        ttk.Label(bottom_bar, text=self.t("Custom gear/tech (comma separated):")).grid(row=0, column=2, sticky="w")
        self.custom_gear_var = tk.StringVar()
        ttk.Entry(bottom_bar, textvariable=self.custom_gear_var).grid(row=0, column=3, sticky="ew", padx=(6, 0))

        action_bar = ttk.Frame(parent)
        action_bar.pack(fill=tk.X, pady=(2, 0))
        action_bar.columnconfigure(1, weight=1)

        ttk.Label(action_bar, text=self.t("Extra modifiers (optional):")).grid(row=0, column=0, sticky="w")
        self.extra_modifiers_var = tk.StringVar()
        ttk.Entry(action_bar, textvariable=self.extra_modifiers_var).grid(row=0, column=1, sticky="ew", padx=(6, 12))

        self.btn_gen_character = ttk.Button(action_bar, text=self.t("GENERATE CHARACTER PROMPT"), command=self.generate_character_prompt)
        self.btn_gen_character.grid(row=0, column=2, sticky="e", ipadx=10, ipady=6)
        
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
    
    def generate_character_prompt(self):
        appearance = [self.appearance_list.get(i) for i in self.appearance_list.curselection()]
        apparel_details = [self.apparel_list.get(i) for i in self.apparel_list.curselection()]
        markings = [self.mark_list.get(i) for i in self.mark_list.curselection()]
        custom_details = self.custom_details_var.get().strip()
        if custom_details:
            appearance.extend([f.strip() for f in custom_details.split(",") if f.strip()])

        accessories = [self.accessory_list.get(i) for i in self.accessory_list.curselection()]
        tech_details = [self.tech_list.get(i) for i in self.tech_list.curselection()]
        custom_gear = self.custom_gear_var.get().strip()
        if custom_gear:
            accessories.extend([f.strip() for f in custom_gear.split(",") if f.strip()])
        
        prompt = cg.generate_character_prompt(
            gender=self.gender_var.get(),
            profession=self.profession_var.get(),
            age=self.age_var.get(),
            framing=self.framing_var.get(),
            aspect_ratio=self.aspect_ratio_var.get(),
            expression=self.expression_var.get(),
            gaze=self.gaze_var.get(),
            appearance_features=appearance,
            apparel_details=apparel_details,
            markings=markings,
            body_type=self.body_type_var.get(),
            skin_tone=self.skin_tone_var.get(),
            hair_style=self.hair_style_var.get(),
            hair_color=self.hair_color_var.get(),
            eye_color=self.eye_color_var.get(),
            outfit_palette=self.outfit_palette_var.get(),
            material_finish=self.material_finish_var.get(),
            accessories=accessories,
            tech_details=tech_details,
            custom_profession=self.custom_profession_var.get(),
            extra_modifiers=self.extra_modifiers_var.get(),
        )
        
        self.set_output(prompt)
    
    def generate_image_threaded(self):
        prompt = self.output_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror(self.t("Error"), self.t("No prompt content to send."))
            return
        
        api_key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
        if not api_key:
            messagebox.showerror(self.t("Error"), self.t("Gemini API key is missing."))
            return
        
        self.set_ui_busy(True, self.t("Generating Image..."))
        threading.Thread(target=self._generate_image_task, args=(prompt,), daemon=True).start()
    
    def _generate_image_task(self, prompt: str):
        api_key = self.api_key_var.get().strip() if hasattr(self, "api_key_var") else self.gemini_api_key
        model = self.model_var.get().strip() if hasattr(self, "model_var") else self.gemini_model
        
        try:
            image_bytes, mime_type = gs.generate_image_bytes(prompt, api_key=api_key, model=model)
            self.pending_image_bytes = image_bytes
            self.pending_image_mime = mime_type
            self.pending_image_prefix = self.get_current_module_prefix()
            self.root.after(0, self.show_preview_image)
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Ready")))
            self.root.after(0, lambda: self.status_var.set(self.t("Image ready. Use Save/Discard.")))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.t("Error"), str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, self.t("Error Occurred")))

    def show_preview_image(self):
        if not self.pending_image_bytes:
            return
        try:
            img = Image.open(io.BytesIO(self.pending_image_bytes))
            img.thumbnail((420, 420))
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_photo, text="")
            self.btn_save_image.config(state=tk.NORMAL)
            self.btn_discard_image.config(state=tk.NORMAL)
        except Exception:
            self.preview_label.config(text=self.t("Error loading image"), image="")
            self.preview_photo = None

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
        self.preview_photo = None
        self.preview_label.config(text=self.t("No preview image"), image="")
        self.btn_save_image.config(state=tk.DISABLED)
        self.btn_discard_image.config(state=tk.DISABLED)
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

