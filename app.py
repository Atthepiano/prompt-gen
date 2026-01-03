import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from PIL import Image, ImageTk
import prompt_generator as pg
import item_generator as ig
import slicer_tool as st
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
        
        # Slicer Smart Naming
        self.slicer_csv_path = ig.DEFAULT_CSV_PATH # Default to item_test.csv

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

        # --- Setup Tab 1: Spaceship Controls ---
        self.setup_spaceship_tab()

        # --- Setup Tab 2: Item Controls ---
        self.setup_item_tab()
        
        # --- Setup Tab 3: Slicer Controls ---
        self.setup_slicer_tab()

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
        
        explanation = ("Generates a prompt for a 8x8 sprite sheet (64 items) from 'iconcsv/item_test.csv'.")
        ttk.Label(parent, text=explanation, wraplength=380).pack(anchor="w", pady=(0, 10))

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
        ttk.Checkbutton(parent, text="Auto-Translate Content to English (Recommended)", variable=self.var_translate_prompt).pack(anchor="w", pady=(0, 20))

        # Generate Button for Tab 2
        # Point to Threaded version
        self.btn_gen_items = ttk.Button(parent, text="GENERATE ICON GRID (8x8)", command=self.generate_item_prompt_threaded, state=state)
        self.btn_gen_items.pack(fill=tk.X, pady=(10, 0), ipady=10)
        
    def setup_slicer_tab(self):
        parent = self.tab_slicer
        
        ttk.Label(parent, text="Image Slicer (8x8 Grid)", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(parent, text="Splits an 8x8 grid image into 64 icons.", wraplength=380).pack(anchor="w", pady=(0, 10))
        
        # --- Image Selection ---
        ttk.Label(parent, text="1. Select Grid Image:", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Button(parent, text="Select Image File...", command=self.select_image_for_slicer).pack(fill=tk.X, pady=(5, 5))
        self.lbl_selected_file = ttk.Label(parent, text="No file selected", foreground="gray")
        self.lbl_selected_file.pack(anchor="w", pady=(0, 10))
        
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
        
    def select_image_for_slicer(self):
        filepath = filedialog.askopenfilename(title="Select Sprite Sheet", filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if filepath:
            self.selected_image_path = filepath
            self.lbl_selected_file.config(text=f"...{os.path.basename(filepath)}")
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

    def toggle_smart_naming(self):
        if self.var_use_csv_naming.get():
            self.cb_trans_file.config(state=tk.NORMAL)
            self.btn_select_csv.config(state=tk.NORMAL)
        else:
            self.cb_trans_file.config(state=tk.DISABLED)
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
        items = ig.read_items_from_csv(ig.DEFAULT_CSV_PATH)
        if not items:
            self.root.after(0, lambda: messagebox.showerror("Error", "Could not read items from CSV."))
            self.root.after(0, lambda: self.set_ui_busy(False, "Ready"))
            return
        
        do_translate = self.var_translate_prompt.get()
        try:
            prompt = ig.generate_icon_grid_prompt(items, translate=do_translate)
            self.root.after(0, lambda: self.set_output(prompt))
            self.root.after(0, lambda: self.set_ui_busy(False, "Prompt Generated Successfully"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, "Error Occurred"))

    def run_slicer_threaded(self):
        if not self.selected_image_path:
            return
        
        self.set_ui_busy(True, "Slicing Image and Translating Names... (Please wait)")
        threading.Thread(target=self._run_slicer_task, daemon=True).start()

    def _run_slicer_task(self):
        csv_to_use = self.slicer_csv_path if self.var_use_csv_naming.get() else None
        do_translate = self.var_translate_filename.get()
            
        try:
            success, msg, count = st.slice_image(self.selected_image_path, 
                                               csv_path=csv_to_use, 
                                               translate_mode=do_translate)
            
            if success:
                final_msg = f"{msg}\n\nGenerated {count} icons.\nCSV Used: {csv_to_use}\nTranslation: {do_translate}"
                self.root.after(0, lambda: messagebox.showinfo("Success", msg))
                self.root.after(0, lambda: self.set_output(final_msg))
                self.root.after(0, lambda: self.set_ui_busy(False, "Slicing Complete"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", msg))
                self.root.after(0, lambda: self.set_ui_busy(False, "Slicing Failed"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Critical Error", str(e)))
            self.root.after(0, lambda: self.set_ui_busy(False, "Error"))

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
    root = tk.Tk()
    try:
        root.tk.call('source', 'azure.tcl')
    except:
        pass
        
    app = PromptApp(root)
    root.mainloop()
