import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import prompt_generator as pg

class PromptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spaceship Prompt Generator")
        self.root.geometry("1100x850")

        # --- Data Setup ---
        self.component_map = pg.get_component_map()
        self.tier_list = pg.get_tier_list()
        self.manufacturer_list = ["None / Generic"] + pg.get_manufacturer_names()
        
        # Color variables
        self.primary_color = None
        self.secondary_color = None

        # --- Layout ---
        # Main Layout: Left (Controls), Right (Output)
        main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane, padding="10")
        right_frame = ttk.Frame(main_pane, padding="10")
        main_pane.add(left_frame, minsize=400)
        main_pane.add(right_frame)

        # --- Controls (Left) ---
        
        # Title Label
        ttk.Label(left_frame, text="Config", font=("Arial", 14, "bold")).pack(pady=(0, 20), anchor="w")

        # Category
        ttk.Label(left_frame, text="Component Category:").pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(left_frame, textvariable=self.category_var, state="readonly")
        self.category_combo['values'] = list(self.component_map.keys())
        self.category_combo.pack(fill=tk.X, pady=(0, 10))
        self.category_combo.bind("<<ComboboxSelected>>", self.update_subcategories)
        self.category_combo.current(0) # Select first by default

        # Subcategory
        ttk.Label(left_frame, text="Subcategory:").pack(anchor="w")
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(left_frame, textvariable=self.subcategory_var, state="readonly")
        self.subcategory_combo.pack(fill=tk.X, pady=(0, 10))
        self.subcategory_combo.bind("<<ComboboxSelected>>", self.update_variants)

        # STRUCTURAL VARIANT (New)
        ttk.Label(left_frame, text="Structural Variant (Form Factor):").pack(anchor="w")
        self.variant_var = tk.StringVar()
        self.variant_combo = ttk.Combobox(left_frame, textvariable=self.variant_var, state="readonly")
        self.variant_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Tier
        ttk.Label(left_frame, text="Tech Tier:").pack(anchor="w")
        self.tier_var = tk.StringVar()
        self.tier_combo = ttk.Combobox(left_frame, textvariable=self.tier_var, state="readonly")
        self.tier_combo['values'] = self.tier_list
        self.tier_combo.pack(fill=tk.X, pady=(0, 20))
        self.tier_combo.current(2) # Default to Tier 3

        # --- MANUFACTURER SECTION ---
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(left_frame, text="Manufacturer Preset", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,5))
        
        self.manufacturer_var = tk.StringVar()
        self.manufacturer_combo = ttk.Combobox(left_frame, textvariable=self.manufacturer_var, state="readonly")
        self.manufacturer_combo['values'] = self.manufacturer_list
        self.manufacturer_combo.pack(fill=tk.X, pady=(0, 5))
        self.manufacturer_combo.current(0)
        self.manufacturer_combo.bind("<<ComboboxSelected>>", self.on_manufacturer_change)

        # Manufacturer Description Label
        self.lbl_manufacturer_desc = ttk.Label(left_frame, text="", foreground="gray", wraplength=350)
        self.lbl_manufacturer_desc.pack(anchor="w", pady=(0, 10))

        # --- COLOR SECTION ---
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(left_frame, text="Color Override", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,10))
        
        self.use_custom_colors = tk.BooleanVar(value=False)
        self.chk_custom_color = ttk.Checkbutton(left_frame, text="Enable Custom Colors", variable=self.use_custom_colors, command=self.toggle_color_buttons)
        self.chk_custom_color.pack(anchor="w", pady=(0, 10))

        # Primary Color Button
        self.btn_primary_color = tk.Button(left_frame, text="Pick Main Color", command=lambda: self.pick_color('primary'), state=tk.DISABLED, bg="#dddddd")
        self.btn_primary_color.pack(fill=tk.X, pady=2)
        
        # Secondary Color Button
        self.btn_secondary_color = tk.Button(left_frame, text="Pick Energy/Glow Color", command=lambda: self.pick_color('secondary'), state=tk.DISABLED, bg="#dddddd")
        self.btn_secondary_color.pack(fill=tk.X, pady=2)

        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=20)

        # Generate Button
        self.gen_btn = ttk.Button(left_frame, text="GENERATE PROMPT", command=self.generate_prompt)
        self.gen_btn.pack(fill=tk.X, pady=(10, 0), ipady=10)

        # Initialize subcategories
        self.update_subcategories()

        # --- Output Area (Right) ---
        ttk.Label(right_frame, text="Generated Output:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.output_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Copy Button
        self.copy_btn = ttk.Button(right_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_btn.pack(anchor="e")

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

    def generate_prompt(self):
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
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", prompt)

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
