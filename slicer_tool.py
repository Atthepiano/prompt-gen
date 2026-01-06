import os
import re
from PIL import Image
import item_generator as ig
import translation_service as ts

def sanitize_filename(name):
    """Remove invalid characters from filename."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_").lower()

def slice_image(image_path, grid_rows=8, grid_cols=8, output_dir=None, csv_path=None, translate_mode=False, remove_bg=False, cache_mode=True):
    """
    Slices an image into a grid of smaller images.
    param csv_path: Optional path to CSV to use for naming.
    param translate_mode: If True, translates item names from CSV to English.
    param remove_bg: If True, attempts to remove background from each slice using rembg.
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
        item_filenames = []
        if csv_path and os.path.exists(csv_path):
            try:
                items = ig.read_items_from_csv(csv_path)
                
                # Caching Logic for Filenames
                changed = False
                tm = None
                
                # Identify items needing translation (if translate_mode is on)
                if translate_mode:
                    indices_to_translate = []
                    names_to_translate = []
                    
                    for i, item in enumerate(items):
                        if not item.get('file_en'): # Check cache first
                             indices_to_translate.append(i)
                             names_to_translate.append(item['name'])
                    
                    if names_to_translate:
                        print(f"Translating {len(names_to_translate)} filenames...")
                        if not tm: tm = ts.TranslationManager()
                        translated = tm.translate_list(names_to_translate)
                        
                        for idx, t_name in zip(indices_to_translate, translated):
                            # Sanitize immediately for storage
                            sanitized = sanitize_filename(t_name)
                            items[idx]['file_en'] = sanitized
                            changed = True
                            
                    # Save back to CSV if we updated cache and it serves as our database
                    # NOTE: We only save if we actually translated something new AND cache is enabled
                    if changed and cache_mode:
                         ig.save_items_to_csv(csv_path, items)

                # Prepare final filename list
                for item in items:
                    # Use cached/translated filename if in translate mode OR if it exists
                    # (User said: "只要检测到csv中存在英文名，启用翻译的时候就不走接口了". 
                    # Implies if translate_mode is off, we use original name? 
                    # Usually filename needs to be English to avoid encoding issues, 
                    # but original logic allowed Chinese filenames if sanitize handle it.
                    # Let's assume: 
                    # If translate_mode=True: Use file_en (cached or new)
                    # If translate_mode=False: Use original name (sanitized)
                    
                    if translate_mode:
                        # We ensured file_en is populated above
                         item_filenames.append(item.get('file_en', ''))
                    else:
                         # Use cache if exists? User said "options default selected".
                         # If user unchecks translate, they probably want raw original name.
                         item_filenames.append(sanitize_filename(item['name']))
                         
            except Exception as e:
                print(f"Warning: Failed to read/process CSV: {e}")
                import traceback
                traceback.print_exc()
        
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
                
                # Remove Background if requested
                if remove_bg:
                    try:
                        # Define worker path and python path (relative to current script or cwd)
                        # We need to find the .venv_rembg/Scripts/python.exe
                        workspace_dir = os.getcwd() # Assumption: running from root
                        venv_python = os.path.join(workspace_dir, ".venv_rembg", "Scripts", "python.exe")
                        worker_script = os.path.join(workspace_dir, "worker_rembg.py")
                        
                        if not os.path.exists(venv_python):
                             print("Error: Venv python not found. Did you run setup_env.bat?")
                        elif not os.path.exists(worker_script):
                             print("Error: Worker script not found.")
                        else:
                            # Save temp file for processing
                            temp_input = os.path.join(output_dir, f"temp_{row}_{col}.png")
                            cell.save(temp_input)
                            
                            temp_output = os.path.join(output_dir, f"temp_{row}_{col}_out.png")
                            
                            # Call external worker
                            import subprocess
                            result = subprocess.run([venv_python, worker_script, temp_input, temp_output], capture_output=True, text=True)
                            
                            if result.returncode == 0 and os.path.exists(temp_output):
                                # Load back processing result
                                cell = Image.open(temp_output).convert("RGBA")
                                # Clean up
                                try:
                                    os.remove(temp_input)
                                    os.remove(temp_output)
                                except: pass
                            else:
                                print(f"Worker failed for {row},{col}: {result.stderr}")
                                if os.path.exists(temp_input): os.remove(temp_input)
                                
                    except Exception as e:
                        print(f"Failed to remove bg for cell {row},{col}: {e}")
                
                # Determine Filename
                idx = row * grid_cols + col
                if idx < len(item_filenames) and item_filenames[idx].strip():
                    # Filename is already sanitized if coming from file_en cache
                    # But safety check doesn't hurt, or if it's from original name
                    base_name = item_filenames[idx] # Already sanitized in logic above
                    
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
