import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from PIL import Image, ImageTk
import prompt_generator as pg
import item_generator as ig
import slicer_tool as st
import curation_tool as ct
import os
import threading

class PromptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spaceship Prompt Generator")
        self.root.geometry("1100x900")

        # --- Data Setup ---
        self.component_map = pg.get_component_map()
        self.tier_list = pg.get_tier_list()
        self.manufacturer_list = ["None / Generic"] + pg.get_manufacturer_names()
        
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
        self.notebook.add(self.tab_spaceship, text="Spaceship Components")

        # Tab 2: Item Icons
        self.tab_items = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_items, text="Item Icons")
        
        # Tab 3: Image Slicer
        self.tab_slicer = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_slicer, text="Image Slicer")

        # Tab 4: Asset Curation
        self.tab_curation = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_curation, text="Asset Curation")

        # --- Setup Tab 1: Spaceship Controls ---
        self.setup_spaceship_tab()

        # --- Setup Tab 2: Item Controls ---
        self.setup_item_tab()
        
        # --- Setup Tab 3: Slicer Controls ---
        self.setup_slicer_tab()

        # --- Setup Tab 4: Curation Controls ---
        self.curator = ct.AssetCurator()
        self.curation_queue = [] # List of filenames to process
        self.current_curation_index = 0
        self.setup_curation_tab()

        # --- Output Area (Right) ---
        self.lbl_output_header = ttk.Label(right_frame, text="Generated Output / Logs:", font=("Arial", 12, "bold"))
        self.lbl_output_header.pack(anchor="w")
        
        self.output_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Copy Button
        self.copy_btn = ttk.Button(right_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_btn.pack(anchor="e")
        
        # Status Bar (Bottom of Right Frame or Main Window)
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(right_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=(10,0))

    def setup_spaceship_tab(self):
        parent = self.tab_spaceship
        
        # Category
        ttk.Label(parent, text="Component Category:").pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(parent, textvariable=self.category_var, state="readonly")
        self.category_combo['values'] = list(self.component_map.keys())
        self.category_combo.pack(fill=tk.X, pady=(0, 10))
        self.category_combo.bind("<<ComboboxSelected>>", self.update_subcategories)
        self.category_combo.current(0) # Select first by default

        # Subcategory
        ttk.Label(parent, text="Subcategory:").pack(anchor="w")
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(parent, textvariable=self.subcategory_var, state="readonly")
        self.subcategory_combo.pack(fill=tk.X, pady=(0, 10))
        self.subcategory_combo.bind("<<ComboboxSelected>>", self.update_variants)

        # STRUCTURAL VARIANT
        ttk.Label(parent, text="Structural Variant (Form Factor):").pack(anchor="w")
        self.variant_var = tk.StringVar()
        self.variant_combo = ttk.Combobox(parent, textvariable=self.variant_var, state="readonly")
        self.variant_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Tier
        ttk.Label(parent, text="Tech Tier:").pack(anchor="w")
        self.tier_var = tk.StringVar()
        self.tier_combo = ttk.Combobox(parent, textvariable=self.tier_var, state="readonly")
        self.tier_combo['values'] = self.tier_list
        self.tier_combo.pack(fill=tk.X, pady=(0, 20))
        self.tier_combo.current(2) # Default to Tier 3

        # --- MANUFACTURER SECTION ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(parent, text="Manufacturer Preset", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,5))
        
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
        ttk.Label(parent, text="Color Override", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,10))
        
        self.use_custom_colors = tk.BooleanVar(value=False)
        self.chk_custom_color = ttk.Checkbutton(parent, text="Enable Custom Colors", variable=self.use_custom_colors, command=self.toggle_color_buttons)
        self.chk_custom_color.pack(anchor="w", pady=(0, 10))

        # Primary Color Button
        self.btn_primary_color = tk.Button(parent, text="Pick Main Color", command=lambda: self.pick_color('primary'), state=tk.DISABLED, bg="#dddddd")
        self.btn_primary_color.pack(fill=tk.X, pady=2)
        
        # Secondary Color Button
        self.btn_secondary_color = tk.Button(parent, text="Pick Energy/Glow Color", command=lambda: self.pick_color('secondary'), state=tk.DISABLED, bg="#dddddd")
        self.btn_secondary_color.pack(fill=tk.X, pady=2)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=20)

        # Generate Button for Tab 1
        self.gen_btn = ttk.Button(parent, text="GENERATE COMPONENT PROMPT", command=self.generate_spaceship_prompt)
        self.gen_btn.pack(fill=tk.X, pady=(10, 0), ipady=10)

        # Initialize subcategories
        self.update_subcategories()

    def setup_item_tab(self):
        parent = self.tab_items
        
        ttk.Label(parent, text="Item Icon Generation", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        explanation = ("Generates a prompt for a 8x8 sprite sheet (64 items) from the selected CSV.")
        ttk.Label(parent, text=explanation, wraplength=380).pack(anchor="w", pady=(0, 10))

        # CSV Selection for Item Prompt
        frame_csv_item = ttk.Frame(parent)
        frame_csv_item.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_select_item_csv = ttk.Button(frame_csv_item, text="Select CSV...", command=self.select_csv_for_item, width=15)
        self.btn_select_item_csv.pack(side=tk.LEFT)
        
        self.lbl_selected_item_csv = ttk.Label(frame_csv_item, text=os.path.basename(self.item_csv_path), foreground="blue")
        self.lbl_selected_item_csv.pack(side=tk.LEFT, padx=5)

        # Check for CSV existence
        if os.path.exists(ig.DEFAULT_CSV_PATH):
            status_text = f"CSV Detected: {ig.DEFAULT_CSV_PATH}"
            status_color = "green"
            state = tk.NORMAL
        else:
            status_text = f"Error: CSV not found at {ig.DEFAULT_CSV_PATH}"
            status_color = "red"
            state = tk.DISABLED

        self.lbl_csv_status = ttk.Label(parent, text=status_text, foreground=status_color, wraplength=380)
        self.lbl_csv_status.pack(anchor="w", pady=(0, 10))
        
        # Translation Checkbox
        self.var_translate_prompt = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Auto-Translate Content to English (Recommended)", variable=self.var_translate_prompt).pack(anchor="w", pady=(0, 5))
        
        # Cache Checkbox
        ttk.Checkbutton(parent, text="Write Translation Result into CSV (Cache)", variable=self.var_cache_translation).pack(anchor="w", pady=(0, 20))

        # Generate Button for Tab 2
        # Point to Threaded version
        self.btn_gen_items = ttk.Button(parent, text="GENERATE ICON GRID (8x8)", command=self.generate_item_prompt_threaded, state=state)
        self.btn_gen_items.pack(fill=tk.X, pady=(10, 0), ipady=10)
        
    def setup_slicer_tab(self):
        parent = self.tab_slicer
        
        ttk.Label(parent, text="Image Slicer (8x8 Grid)", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(parent, text="Splits an 8x8 grid image into 64 icons.", wraplength=380).pack(anchor="w", pady=(0, 10))
        
        # --- Image Selection ---
        ttk.Label(parent, text="1. Select Grid Image(s):", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Button(parent, text="Select Image File(s)...", command=self.select_images_for_slicer).pack(fill=tk.X, pady=(5, 5))
        self.lbl_selected_file = ttk.Label(parent, text="No file selected", foreground="gray", wraplength=400)
        self.lbl_selected_file.pack(anchor="w", pady=(0, 10))
        
        # --- Advanced Config ---
        frame_config = ttk.LabelFrame(parent, text="Advanced Configuration", padding=5)
        frame_config.pack(fill=tk.X, pady=5)
        
        # Grid Size
        ttk.Label(frame_config, text="Grid Size (Row x Col):").pack(side=tk.LEFT)
        self.var_grid_size = tk.StringVar(value="8")
        ttk.Entry(frame_config, textvariable=self.var_grid_size, width=5).pack(side=tk.LEFT, padx=5)
        
        # Scale Factor
        ttk.Label(frame_config, text="Norm Scale (0.1-1.0):").pack(side=tk.LEFT, padx=(10, 0))
        self.var_scale_factor = tk.DoubleVar(value=0.85)
        ttk.Entry(frame_config, textvariable=self.var_scale_factor, width=5).pack(side=tk.LEFT, padx=5)
        
        # --- Naming Options ---
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(parent, text="2. Smart Naming Options:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5,0))
        
        # Toggle Smart Naming
        self.var_use_csv_naming = tk.BooleanVar(value=True)
        cb_naming = ttk.Checkbutton(parent, text="Use CSV for Filenames (Smart Naming)", variable=self.var_use_csv_naming, command=self.toggle_smart_naming)
        cb_naming.pack(anchor="w")
        
        # Toggle Filename Translation
        self.var_translate_filename = tk.BooleanVar(value=True)
        self.cb_trans_file = ttk.Checkbutton(parent, text="Auto-Translate Filenames (ZH -> EN)", variable=self.var_translate_filename)
        self.cb_trans_file.pack(anchor="w", padx=(20, 0))
        
        # Cache Checkbox (Mirrored)
        self.cb_cache_file = ttk.Checkbutton(parent, text="Write Result into CSV (Cache)", variable=self.var_cache_translation)
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

        bg_text = "Remove Background"
        if not venv_exists:
            bg_text += " [Setup Required]"
            
        self.cb_remove_bg = ttk.Checkbutton(parent, text=bg_text, variable=self.var_remove_bg)
        self.cb_remove_bg.pack(anchor="w", pady=(5, 0))
        
        # Always enable
        self.cb_remove_bg.config(state=tk.NORMAL) 
        
        if not venv_exists:
             self.cb_remove_bg.config(state=tk.NORMAL) # Let user try it or see warning

        # Normalize Checkbox

        # Normalize Checkbox
        self.cb_normalize = ttk.Checkbutton(parent, text="Normalize Size & Position (Trim & Center 90%)", variable=self.var_normalize)
        self.cb_normalize.pack(anchor="w", pady=(2, 0))
        
        # CSV Selection
        frame_csv = ttk.Frame(parent)
        frame_csv.pack(fill=tk.X, pady=(5, 0))
        self.btn_select_csv = ttk.Button(frame_csv, text="Select CSV...", command=self.select_csv_for_slicer, width=15)
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
        self.btn_slice = ttk.Button(parent, text="SLICE INTO 64 ICONS", command=self.run_slicer_threaded, state=tk.DISABLED)
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
        ttk.Label(sidebar, text="Configuration", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Target Folder
        ttk.Label(sidebar, text="Target Folder (Output):").pack(anchor="w")
        self.curation_target_var = tk.StringVar()
        self.entry_curation_target = ttk.Entry(sidebar, textvariable=self.curation_target_var)
        self.entry_curation_target.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(sidebar, text="Browse Target...", command=self.browse_curation_target).pack(anchor="e")
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)
        
        # Source Folders
        ttk.Label(sidebar, text="Source Folders (Inputs):").pack(anchor="w")
        
        list_frame = ttk.Frame(sidebar)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.lst_sources = tk.Listbox(list_frame, height=8)
        self.lst_sources.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.lst_sources.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.lst_sources.config(yscrollcommand=sb.set)
        
        btn_frame = ttk.Frame(sidebar)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="+ Add Batch (Select Files)", command=self.add_source_folder_batch).pack(fill=tk.X, pady=(0, 2))
        
        btn_row2 = ttk.Frame(btn_frame)
        btn_row2.pack(fill=tk.X)
        ttk.Button(btn_row2, text="+ Add Folder", command=self.add_source_folder_single).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,1))
        ttk.Button(btn_row2, text="- Remove", command=self.remove_source_folder).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(1,0))
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)
        
        # Controls
        self.lbl_curation_status = ttk.Label(sidebar, text="Ready", wraplength=200)
        self.lbl_curation_status.pack(anchor="w", pady=(0, 10))
        
        self.btn_start_curation = ttk.Button(sidebar, text="START SESSION", command=self.start_curation_session, width=20)
        self.btn_start_curation.pack(fill=tk.X, ipady=5)
        
        # --- Main View (Comparison) ---
        self.frame_comparison = ttk.Frame(main_view)
        self.frame_comparison.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.lbl_compare_info = ttk.Label(self.frame_comparison, text="Waiting to start...", font=("Arial", 14))
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
        self.btn_curation_skip = ttk.Button(self.frame_comparison, text="Skip / Discard All", command=self.skip_curation_item, state=tk.DISABLED)
        self.btn_curation_skip.pack(pady=10)
        
        # Bind Keys
        self.root.bind("<Key>", self.handle_curation_keypress)

    def browse_curation_target(self):
        path = filedialog.askdirectory(title="Select Target Folder")
        if path:
            self.curation_target_var.set(path)

    def add_source_folder_batch(self):
        # Workaround for multi-folder select: Ask for files
        filepaths = filedialog.askopenfilenames(title="Select ANY file inside the source folder(s) - Ctrl+Click to select multiple folders")
        if filepaths:
            current_list = self.lst_sources.get(0, tk.END)
            for fp in filepaths:
                folder = os.path.dirname(fp)
                if folder not in current_list:
                    self.lst_sources.insert(tk.END, folder)
                    current_list = self.lst_sources.get(0, tk.END) # Update local ref
            self.lst_sources.see(tk.END)

    def add_source_folder_single(self):
        path = filedialog.askdirectory(title="Select Source Folder")
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
            messagebox.showerror("Error", "Please add at least one source folder.")
            return
        if not target:
            messagebox.showerror("Error", "Please select a target folder.")
            return
            
        # Configure Backend
        self.curator.set_config(list(sources), target)
        
        # Scan
        total, conflicts = self.curator.scan_files()
        
        # Auto-resolve uniques
        auto_count = self.curator.auto_resolve_uniques()
        
        msg = f"Scan Complete.\nTotal Files: {total}\nAuto-Resolved (Unique): {auto_count}\nConflicts to Review: {conflicts}"
        messagebox.showinfo("Session Started", msg)
        
        # Setup Queue
        self.curation_queue = self.curator.get_pending_conflicts()
        self.current_curation_index = 0
        
        self.load_next_curation_item()

    def load_next_curation_item(self):
        if self.current_curation_index >= len(self.curation_queue):
            # Done
            self.lbl_compare_info.config(text="Session Complete! All items resolved.")
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
                ttk.Label(frame_item, text="Error loading image").pack()
                
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
            messagebox.showerror("Error", "Failed to copy file.")

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
        filepaths = filedialog.askopenfilenames(title="Select Sprite Sheets", filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if filepaths:
            self.slicer_files = list(filepaths)
            count = len(self.slicer_files)
            if count == 1:
                display = os.path.basename(self.slicer_files[0])
            else:
                display = f"{count} files selected"
                
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
        filepath = filedialog.askopenfilename(title="Select Naming CSV", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.slicer_csv_path = filepath
            self.lbl_selected_csv.config(text=os.path.basename(filepath))

    def select_csv_for_item(self):
        filepath = filedialog.askopenfilename(title="Select Item CSV", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.item_csv_path = filepath
            self.lbl_selected_item_csv.config(text=os.path.basename(filepath))

    def toggle_smart_naming(self):
        if self.var_use_csv_naming.get():
            self.cb_trans_file.config(state=tk.NORMAL)
            self.cb_cache_file.config(state=tk.NORMAL)
            self.btn_select_csv.config(state=tk.NORMAL)
        else:
            self.cb_trans_file.config(state=tk.DISABLED)
            self.cb_cache_file.config(state=tk.DISABLED)
            self.btn_select_csv.config(state=tk.DISABLED)

    def set_ui_busy(self, busy=True, message="Processing..."):
        """Disable/Enable buttons and update status."""
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

    def generate_item_prompt_threaded(self):
        self.set_ui_busy(True, "Generating Prompt and Translating... (This may take a moment)")
        # Run in thread
        threading.Thread(target=self._generate_item_prompt_task, daemon=True).start()

    def _generate_item_prompt_task(self):
        items = ig.read_items_from_csv(self.item_csv_path)
        if not items:
            self.root.after(0, lambda: messagebox.showerror("Error", "Could not read items from CSV."))
            self.root.after(0, lambda: self.set_ui_busy(False, "Ready"))
            return
        
        do_translate = self.var_translate_prompt.get()
        do_cache = self.var_cache_translation.get()
        cache_path = self.item_csv_path if do_cache else None
        
        try:
            prompt = ig.generate_icon_grid_prompt(items, translate=do_translate, cache_path=cache_path)
            self.root.after(0, lambda: self.set_output(prompt))
            self.root.after(0, lambda: self.set_ui_busy(False, "Prompt Generated Successfully"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, "Error Occurred"))

    def run_slicer_threaded(self):
        # Ensure list exists
        if not hasattr(self, 'slicer_files') and hasattr(self, 'selected_image_path') and self.selected_image_path:
             self.slicer_files = [self.selected_image_path]
             
        if not hasattr(self, 'slicer_files') or not self.slicer_files:
            return
        
        self.set_ui_busy(True, "Slicing Images... (Batch Processing)")
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
            self.status_var.set(f"Processing ({i+1}/{total}): {os.path.basename(fp)}...")
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
                
        self.root.after(0, lambda: self.set_ui_busy(False, "Batch Complete"))
        
        summary = f"Processed {success_count}/{total} files successfully."
        if errors:
            summary += "\n\nErrors:\n" + "\n".join(errors)
            self.root.after(0, lambda: messagebox.showwarning("Batch Results", summary))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Batch Complete", summary))
            
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
            messagebox.showerror("Error", "Please select all options.")
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

    # Note: generate_item_prompt and run_slicer are now threaded versions above

    def set_output(self, text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def copy_to_clipboard(self):
        content = self.output_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Copied", "Prompt copied to clipboard!")

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

