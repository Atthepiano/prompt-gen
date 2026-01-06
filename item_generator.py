import csv
import os
from typing import List, Tuple, Dict
import translation_service as ts

# --- Constants ---
GRID_SIZE = 8
TOTAL_ITEMS = GRID_SIZE * GRID_SIZE
DEFAULT_CSV_PATH = os.path.join("iconcsv", "item_test.csv")

def read_items_from_csv(filepath: str) -> List[dict]:
    """
    Reads items from CSV. 
    Format: Name, Description, [Prompt_Name_EN], [Filename_EN]
    Returns list of dicts: {'name': str, 'desc': str, 'prompt_en': str, 'file_en': str}
    """
    items = []
    
    if not os.path.exists(filepath):
        return items

    try:
        # Try utf-8-sig first to handle BOM
        encoding = 'utf-8-sig'
        try:
             with open(filepath, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                return _parse_csv_to_dict(reader)
        except UnicodeDecodeError:
            encoding = 'gbk'
            with open(filepath, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                return _parse_csv_to_dict(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def _parse_csv_to_dict(reader) -> List[dict]:
    items = []
    for row in reader:
        if len(row) >= 2 and row[0].strip():
            item = {
                'name': row[0].strip(),
                'desc': row[1].strip(),
                'prompt_en': row[2].strip() if len(row) > 2 else "",
                'file_en': row[3].strip() if len(row) > 3 else ""
            }
            items.append(item)
        
        if len(items) >= TOTAL_ITEMS:
            break
    return items

def save_items_to_csv(filepath: str, items: List[dict]):
    """
    Writes items back to CSV, preserving 4 columns.
    """
    try:
        # Use utf-8-sig for Excel compatibility
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            for item in items:
                writer.writerow([
                    item.get('name', ''),
                    item.get('desc', ''),
                    item.get('prompt_en', ''),
                    item.get('file_en', '')
                ])
        print(f"Successfully saved cache to {filepath}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

def generate_icon_grid_prompt(items: List[dict], translate: bool = False, cache_path: str = None) -> str:
    """
    Generates a prompt for a 8x8 sprite sheet.
    param items: List of dicts (from read_items_from_csv)
    param translate: If True, ensures English names are available (uses cache or translates).
    param cache_path: If provided and translation happened, saves back to this path.
    """
    
    if not items:
        return "Error: No valid items found in the CSV file."

    count = len(items)
    
    # Process Translations
    if translate:
        tm = ts.TranslationManager()
        
        # Identify missing Prompt Names
        missing_indices = []
        texts_to_translate = []
        
        for i, item in enumerate(items):
            if not item.get('prompt_en'):
                # Combine name and desc for better context or just translate name? 
                # User said "prompts translated to normal English name"
                # Let's translate just the Name for the prompt list to keep it clean, 
                # or maybe Name + Desc if needed? The original code had separate lists.
                # Let's stick to translating Name and Description separately as before.
                missing_indices.append(i)
                texts_to_translate.append(item['name'])
        
        # Translate missing names
        if texts_to_translate:
            print(f"Translating {len(texts_to_translate)} missing names...")
            translated_names = tm.translate_list(texts_to_translate)
            
            # Apply back to items
            changed = False
            for idx, t_name in zip(missing_indices, translated_names):
                items[idx]['prompt_en'] = t_name
                changed = True
            
            # Save if cache enabled
            if changed and cache_path:
                save_items_to_csv(cache_path, items)
                
        # Access descriptions (we don't cache desc translation based on user request "Prompt Name" & "Filename")
        # But for Prompt Gen we need translated Descriptions too usually.
        # Let's just translate descriptions on the fly if not cached? 
        # The user specifically asked for "Translator result write into csv... prompt translated to normal english name... file name..."
        # They didn't explicitly say cache description, but it makes sense to.
        # However, to strictly follow "Col 3 = Prompt Name, Col 4 = Filename", we might not have space for Desc EN.
        # Let's just translate Desc on fly for now to abide by column structure provided.
        
        # Construct display list
        display_items = []
        descs_to_translate = [item['desc'] for item in items]
        print("Translating descriptions (not cached)...")
        translated_descs = tm.translate_list(descs_to_translate)
        
        for i, item in enumerate(items):
            d_name = item['prompt_en'] if item['prompt_en'] else item['name']
            d_desc = translated_descs[i]
            display_items.append((d_name, d_desc))
            
    else:
        # No translate, just use original
        display_items = [(item['name'], item['desc']) for item in items]
    
    # --- Prompt Construction ---
    
    header = f"""`A strictly organized technical sprite sheet in a {GRID_SIZE}x{GRID_SIZE} grid layout containing {count} distinct RPG item icons.

**LAYOUT & FORMAT CRITERIA (CRITICAL):**
1. **ASPECT RATIO is strictly 1:1 (Square Canvas).**
2. The canvas must be a precise {GRID_SIZE}x{GRID_SIZE} grid.
3. Each cell in the grid must contain EXACTLY ONE item icon.
4. **ALIGNMENT**: Each icon must be **PERFECTLY CENTERED** within its grid cell with generous, equal whitespace padding on all sides.
5. **SCALE**: All icons must share a **UNIFORM VISUAL SIZE** and weight. Do not allow some items to be significantly larger or smaller than others.
6. **PERSPECTIVE**: All icons must be presented in a **UNIFORM ISOMETRIC VIEW** (approx 45 degrees).
7. **BACKGROUND MUST BE PURE WHITE (#FFFFFF).**
8. Total items: {count}. If fewer than {TOTAL_ITEMS}, leave remaining cells empty.
9. **NEGATIVE CONSTRAINT**: **ABSOLUTELY NO TEXT. NO CHARACTERS. NO NUMBERS. NO LABELS. NO UI ELEMENTS.** The icons must be purely visual representation only.

**GRID CONTENTS:**
"""
    
    content = ""
    for i, (name, desc) in enumerate(display_items):
        row = (i // GRID_SIZE) + 1
        col = (i % GRID_SIZE) + 1
        content += f"Row {row}, Col {col}: **{name}** - {desc}\n"

    footer = """
**ART STYLE (90s Konami Tech-Noir Adventure):**
1. **Genre Core**: 90s Japanese PC adventure game art asset. Hard sci-fi anime blend with gritty graphic novel art.
2. **Texture & Technique**: Retro digital painting feel. Visible dithering patterns in shadows. Bitmapped graphics aesthetic, raster texture.
3. **Line Art & Shading**: Style influence of Yoji Shinkawa (early work). Heavy use of solid blacks for shadows. Hard, angular highlights on metallic surfaces.
4. **Color Palette**: Muted and Cold. Desaturated blues, grays, industrial tones. High contrast.
`"""

    return header + content + footer

