import csv
import os
from typing import List, Tuple

# --- Constants ---
GRID_SIZE = 8
TOTAL_ITEMS = GRID_SIZE * GRID_SIZE
DEFAULT_CSV_PATH = os.path.join("iconcsv", "item_test.csv")

def read_items_from_csv(filepath: str) -> List[Tuple[str, str]]:
    """
    Reads the first 64 valid items from a CSV file.
    Assumes format: Name, Description
    Skips empty lines.
    """
    items = []
    
    if not os.path.exists(filepath):
        return items

    try:
        # Try utf-8-sig first to handle BOM
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                return _parse_csv(reader)
        except UnicodeDecodeError:
            # Fallback to gbk
            with open(filepath, 'r', encoding='gbk') as f:
                reader = csv.reader(f)
                return _parse_csv(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def _parse_csv(reader) -> List[Tuple[str, str]]:
    items = []
    for row in reader:
        # Basic validation: must have at least 2 columns and name must not be empty
        if len(row) >= 2 and row[0].strip():
            name = row[0].strip()
            desc = row[1].strip()
            items.append((name, desc))
        
        if len(items) >= TOTAL_ITEMS:
            break
    return items

import translation_service as ts

def generate_icon_grid_prompt(items: List[Tuple[str, str]], translate: bool = False) -> str:
    """
    Generates a prompt for a 8x8 sprite sheet based on the provided items.
    param translate: If True, translates item names and descriptions to English.
    """
    
    if not items:
        return "Error: No valid items found in the CSV file."

    count = len(items)
    
    # Translation Logic
    process_items = items
    if translate:
        tm = ts.TranslationManager()
        
        # Unzip names and descriptions
        names = [item[0] for item in items]
        descs = [item[1] for item in items]
        
        # Batch translate concurrently
        print("Translating names...")
        t_names = tm.translate_list(names)
        print("Translating descriptions...")
        t_descs = tm.translate_list(descs)
        
        # Re-zip
        translated_items = list(zip(t_names, t_descs))
        process_items = translated_items
    
    # --- Prompt Construction ---
    
    header = f"""# 
`A strictly organized technical sprite sheet in a {GRID_SIZE}x{GRID_SIZE} grid layout containing {count} distinct RPG item icons.

**LAYOUT & FORMAT CRITERIA (CRITICAL):**
1. **ASPECT RATIO is strictly 1:1 (Square Canvas).**
2. The canvas must be a precise {GRID_SIZE}x{GRID_SIZE} grid.
3. Each cell in the grid must contain EXACTLY ONE item icon.
4. **PERSPECTIVE**: All icons must be presented in a **UNIFORM ISOMETRIC VIEW** (approx 45 degrees).
5. **BACKGROUND MUST BE PURE WHITE (#FFFFFF).**
6. Total items: {count}. If fewer than {TOTAL_ITEMS}, leave remaining cells empty.
7. **NEGATIVE CONSTRAINT**: **NO TEXT. NO LETTERS. NO NUMBERS. NO LABELS.** The icons must be purely visual.

**GRID CONTENTS:**
"""
    
    content = ""
    for i, (name, desc) in enumerate(process_items):
        row = (i // GRID_SIZE) + 1
        col = (i % GRID_SIZE) + 1
        content += f"Row {row}, Col {col}: **{name}** - {desc}\n"

    footer = """
**ART STYLE (90s Konami Tech-Noir Adventure):**
1. **Genre Core**: 90s Japanese PC adventure game art asset. Hard sci-fi anime blend with gritty graphic novel art.
2. **Texture & Technique**: Retro digital painting feel. Visible dithering patterns in shadows. Bitmapped graphics aesthetic, raster texture.
3. **Line Art & Shading**: Style influence of Yoji Shinkawa (early work). Heavy use of solid blacks for shadows. Hard, angular highlights on metallic surfaces.
4. **Color Palette**: Muted and Cold. Desaturated blues, grays, industrial tones. High contrast. (Adapted for white background).
`"""

    return header + content + footer
