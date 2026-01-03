import os
import re
from PIL import Image
import item_generator as ig
import translation_service as ts

def sanitize_filename(name):
    """Remove invalid characters from filename."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_").lower()

def slice_image(image_path, grid_rows=8, grid_cols=8, output_dir=None, csv_path=None, translate_mode=False):
    """
    Slices an image into a grid of smaller images.
    param csv_path: Optional path to CSV to use for naming.
    param translate_mode: If True, translates item names from CSV to English.
    Returns: (success: bool, message: str, count: int)
    """
    try:
        if not os.path.exists(image_path):
            return False, "Image file not found.", 0

        img = Image.open(image_path)
        width, height = img.size
        
        # Calculate cell size
        cell_width = width // grid_cols
        cell_height = height // grid_rows
        
        # Prepare content list if CSV provided
        item_names = []
        if csv_path and os.path.exists(csv_path):
            try:
                items = ig.read_items_from_csv(csv_path)
                # Helper to translate only names if needed
                if translate_mode:
                    tm = ts.TranslationManager()
                    # We only need the name (first elem)
                    raw_names = [item[0] for item in items]
                    item_names = tm.translate_list(raw_names)
                else:
                    item_names = [item[0] for item in items]
            except Exception as e:
                print(f"Warning: Failed to read/process CSV: {e}")
        
        # Prepare output directory
        if not output_dir:
            base_dir = os.path.dirname(image_path)
            name = os.path.splitext(os.path.basename(image_path))[0]
            output_dir = os.path.join(base_dir, f"{name}_slices")
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        count = 0
        for row in range(grid_rows):
            for col in range(grid_cols):
                left = col * cell_width
                upper = row * cell_height
                right = left + cell_width
                lower = upper + cell_height
                
                # Crop
                cell = img.crop((left, upper, right, lower))
                
                # Determine Filename
                idx = row * grid_cols + col
                if idx < len(item_names) and item_names[idx].strip():
                    base_name = sanitize_filename(item_names[idx])
                    if not base_name: # Handle case where sanitization leaves empty string
                        filename = f"icon_{row+1:02d}_{col+1:02d}.png"
                    else:
                        filename = f"{base_name}.png"
                        # Handle Duplicates
                        counter = 2
                        while os.path.exists(os.path.join(output_dir, filename)):
                            filename = f"{base_name}_{counter}.png"
                            counter += 1
                else:
                    filename = f"icon_{row+1:02d}_{col+1:02d}.png"
                
                save_path = os.path.join(output_dir, filename)
                cell.save(save_path)
                count += 1
                
        return True, f"Successfully sliced {count} icons to '{output_dir}'", count

    except Exception as e:
        return False, str(e), 0
