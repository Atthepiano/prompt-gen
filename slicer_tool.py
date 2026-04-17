import os
import re
import sys
from PIL import Image
import item_generator as ig
import translation_service as ts

def sanitize_filename(name):
    """Remove invalid characters from filename."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_").lower()

def normalize_image_content(img, threshold=30, scale_factor=0.85):
    """
    Trims, Denoises, and Centers the image content.
    """
    # 1. Denoise (Alpha Threshold)
    # Convert manually to avoid complex dependencies, or use point lookup
    # Load data to allow pixel access
    img = img.convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    # Simple thresholding
    for item in datas:
        # item is (r,g,b,a)
        if item[3] < threshold:
            new_data.append((0, 0, 0, 0)) # Fully transparent
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # 2. Trim (Get Bounding Box)
    bbox = img.getbbox()
    if not bbox:
        return img # Empty image
        
    content = img.crop(bbox)
    
    # 3. Scale and Center
    # Target size is original canvas size (assuming square input cells usually)
    target_w, target_h = img.size 
    
    # Max dimensions for content
    max_w = int(target_w * scale_factor)
    max_h = int(target_h * scale_factor)
    
    content_w, content_h = content.size
    
    # Calculate scale to fit
    ratio = min(max_w / content_w, max_h / content_h)
    new_w = int(content_w * ratio)
    new_h = int(content_h * ratio)
    
    # Resize content (LANCZOS for quality)
    content = content.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Paste into center of empty canvas
    new_img = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    offset_x = (target_w - new_w) // 2
    offset_y = (target_h - new_h) // 2
    
    new_img.paste(content, (offset_x, offset_y))
    return new_img

def detect_grid(image_path, max_divs=16, min_cell_ratio=0.08, bg_threshold=245):
    """
    Intelligently detects grid boundaries using content-block detection.

    Strategy: find WHERE CONTENT IS (not where background is), then cut
    in the gaps BETWEEN content blocks. This prevents:
      - False cuts inside cells (white margins within a cell won't be cut)
      - Missing cuts at explicit dividing lines (dark or colored lines are
        treated as content, so the cut lands in the white gap beside them)

    Also detects solid dark/colored dividing lines (rows/cols that are
    uniformly non-white but different from typical content) as separators.

    Performance: downsamples to ≤512px before scanning pixels.

    Returns: (row_cuts, col_cuts) — pixel boundary positions including
             0 at start and image dimension at end.
    """
    img = Image.open(image_path).convert("L")  # grayscale — single channel, faster
    w, h = img.size

    # --- Downsample for speed (max 512px on the longest side) ---
    proc = 512
    if max(w, h) > proc:
        sf = proc / max(w, h)
        sw, sh = max(1, int(w * sf)), max(1, int(h * sf))
        small = img.resize((sw, sh), Image.Resampling.BOX)
    else:
        small, sw, sh = img, w, h

    pix = small.load()

    # --- Build per-row and per-column content density in a single pass ---
    # "content pixel" = any pixel darker than bg_threshold (non-white)
    row_content = [0.0] * sh
    col_content = [0.0] * sw

    for y in range(sh):
        c = 0
        for x in range(sw):
            if pix[x, y] < bg_threshold:
                c += 1
        row_content[y] = c / sw

    for x in range(sw):
        c = 0
        for y in range(sh):
            if pix[x, y] < bg_threshold:
                c += 1
        col_content[x] = c / sh

    def profile_to_cuts(density, orig_dim, small_dim):
        n = len(density)
        if n == 0:
            return [0, orig_dim]

        peak = max(density)
        if peak < 0.005:          # Nearly blank image, nothing to detect
            return [0, orig_dim]

        # Adaptive thresholds based on actual image content level
        sep_th     = min(0.015, peak * 0.06)   # ≤ this → background/separator
        content_th = sep_th * 6                 # ≥ this → definite content

        # Minimum cell size in downsampled coords
        min_sz = max(3, int(n * min_cell_ratio))
        # Merge gap: white holes WITHIN a single view (e.g. gun barrel, hollow parts)
        # 2% of processed dimension → merges small holes without crossing cell gaps.
        merge_gap = max(1, int(n * 0.02))

        # --- Mark each position as "content" or not ---
        is_c = [density[i] > content_th for i in range(n)]

        # --- Find contiguous content bands ---
        bands = []
        in_b = False
        bs = 0
        for i, c in enumerate(is_c):
            if c and not in_b:
                bs = i
                in_b = True
            elif not c and in_b:
                bands.append([bs, i - 1])
                in_b = False
        if in_b:
            bands.append([bs, n - 1])

        # --- Merge bands separated by tiny gaps (white holes inside a view) ---
        merged = []
        for b in bands:
            if merged and (b[0] - merged[-1][1] - 1) <= merge_gap:
                merged[-1][1] = b[1]
            else:
                merged.append(b[:])

        # --- Drop noise bands that are too small to be a real cell ---
        min_band = max(1, min_sz // 4)
        merged = [b for b in merged if (b[1] - b[0] + 1) >= min_band]

        if len(merged) <= 1:
            return [0, orig_dim]

        # --- Place cuts at the midpoint of each gap between adjacent content bands ---
        scale = orig_dim / small_dim
        cuts = [0]
        for i in range(len(merged) - 1):
            gap_mid_s = (merged[i][1] + 1 + merged[i + 1][0]) // 2
            gap_mid_o = max(1, min(orig_dim - 1, round(gap_mid_s * scale)))

            # Enforce minimum cell size on both sides of the proposed cut
            if gap_mid_o - cuts[-1] < round(min_sz * scale):
                continue
            if orig_dim - gap_mid_o < round(min_sz * scale):
                continue

            cuts.append(gap_mid_o)

        cuts.append(orig_dim)
        return cuts if len(cuts) > 2 else [0, orig_dim]

    row_cuts = profile_to_cuts(row_content, h, sh)
    col_cuts = profile_to_cuts(col_content, w, sw)

    # --- Per-band refinement (Pass 2) ---
    # Problem: large views in one row/col band can fill the center of the opposite
    # dimension, hiding the separator in the global density profile.
    # Fix: scan each band independently; use whichever band yields more cuts.

    def band_density(axis, band_s, band_e):
        """Content density profile along `axis` ('col' or 'row') within a pixel band."""
        if axis == 'col':
            # band_s/band_e are row coordinates in downsampled space
            span = max(1, band_e - band_s)
            return [
                sum(1 for y in range(band_s, band_e) if pix[x, y] < bg_threshold) / span
                for x in range(sw)
            ]
        else:
            # band_s/band_e are col coordinates in downsampled space
            span = max(1, band_e - band_s)
            return [
                sum(1 for x in range(band_s, band_e) if pix[x, y] < bg_threshold) / span
                for y in range(sh)
            ]

    def refine_cuts(existing_cuts, orig_dim, small_dim, scan_axis, band_cuts_orig):
        """
        For each band defined by band_cuts_orig, compute a density profile
        along scan_axis, derive cuts, and return the best (most cuts found).
        """
        best = existing_cuts
        for i in range(len(band_cuts_orig) - 1):
            bs = max(0, round(band_cuts_orig[i] * small_dim / orig_dim))
            be = min(small_dim, round(band_cuts_orig[i + 1] * small_dim / orig_dim))
            if be - bs < 5:
                continue
            dens = band_density(scan_axis, bs, be)
            candidate = profile_to_cuts(dens, orig_dim, sw if scan_axis == 'col' else sh)
            if len(candidate) > len(best):
                best = candidate
        return best

    # Refine col_cuts using each row band
    if len(row_cuts) > 1:
        col_cuts = refine_cuts(col_cuts, w, sh, 'col', row_cuts)

    # Refine row_cuts using each col band
    if len(col_cuts) > 1:
        row_cuts = refine_cuts(row_cuts, h, sw, 'row', col_cuts)

    # Safety cap
    if len(row_cuts) - 1 > max_divs:
        n = max_divs
        row_cuts = [int(h * i / n) for i in range(n + 1)]
    if len(col_cuts) - 1 > max_divs:
        n = max_divs
        col_cuts = [int(w * i / n) for i in range(n + 1)]

    return row_cuts, col_cuts


def slice_image(image_path, grid_rows=8, grid_cols=8, output_dir=None, csv_path=None, translate_mode=False, remove_bg=False, cache_mode=True, normalize_mode=False, scale_factor=0.85, rename="", auto_suffix=False, image_seq=0, start_index=1, num_digits=2, row_cuts=None, col_cuts=None):
    """
    Slices an image into a grid of smaller images.
    param rename: If non-empty, all cells use this as base name.
    param auto_suffix: If True, adds image-level number prefix to cell numbers (for batch).
                       e.g. rename_01_01 (image 1 cell 1), rename_02_01 (image 2 cell 1).
                       If False, flat continuous numbering: rename_01, rename_02, ...
    param image_seq: This image's sequence number when auto_suffix is True.
    param start_index: Starting cell number for flat mode (batch continuity).
    param num_digits: Minimum zero-padding width (e.g. 2 -> _01, 3 -> _001).
    Returns: (success: bool, message: str, count: int)
    """
    try:
        if not os.path.exists(image_path):
            return False, "Image file not found.", 0
            


        img = Image.open(image_path)
        width, height = img.size

        # Use custom cuts if provided (smart crop), otherwise fall back to uniform grid
        if row_cuts and col_cuts:
            actual_rows = len(row_cuts) - 1
            actual_cols = len(col_cuts) - 1
        else:
            actual_rows = grid_rows
            actual_cols = grid_cols
            cell_width = width // grid_cols
            cell_height = height // grid_rows
            row_cuts = [i * cell_height for i in range(grid_rows + 1)]
            col_cuts = [i * cell_width for i in range(grid_cols + 1)]
        
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
                        if not ig.save_items_to_csv(csv_path, items):
                            csv_warning = "Warning: Could not save translations to CSV. Check if file is open."
                            print(csv_warning)

                # Prepare final filename list

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
                
        # Append warning if set
        # We need a way to pass this warnings to the return. 
        # But return is at the end of function.
        # Let's verify we actually catch the error inside read_items loop or if it's outside.
        # The entire CSV block is wrapped in try...except.
        
        if 'csv_warning' not in locals(): csv_warning = ""
        
        # Prepare output directory
        if not output_dir:
            base_dir = os.path.dirname(image_path)
            name = os.path.splitext(os.path.basename(image_path))[0]
            output_dir = os.path.join(base_dir, f"{name}_slices")
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        count = 0
        for row in range(actual_rows):
            for col in range(actual_cols):
                left = col_cuts[col]
                upper = row_cuts[row]
                right = col_cuts[col + 1]
                lower = row_cuts[row + 1]
                
                # Crop
                cell = img.crop((left, upper, right, lower))
                
                # Remove Background if requested
                if remove_bg:
                    try:
                        # Define worker command
                        worker_cmd = None
                        
                        # 1. Check for bundled/frozen worker EXE
                        if getattr(sys, 'frozen', False):
                            base_dir = os.path.dirname(sys.executable)
                            worker_exe = os.path.join(base_dir, "worker_rembg.exe")
                            if os.path.exists(worker_exe):
                                temp_input = os.path.join(output_dir, f"temp_{row}_{col}.png")
                                temp_output = os.path.join(output_dir, f"temp_{row}_{col}_out.png")
                                worker_cmd = [worker_exe, temp_input, temp_output]

                        # 2. Fallback to Dev Venv
                        if not worker_cmd:
                            workspace_dir = os.getcwd() 
                            venv_python = os.path.join(workspace_dir, ".venv_rembg", "Scripts", "python.exe")
                            worker_script = os.path.join(workspace_dir, "worker_rembg.py")
                            
                            if os.path.exists(venv_python) and os.path.exists(worker_script):
                                temp_input = os.path.join(output_dir, f"temp_{row}_{col}.png")
                                temp_output = os.path.join(output_dir, f"temp_{row}_{col}_out.png")
                                worker_cmd = [venv_python, worker_script, temp_input, temp_output]
                        
                        if worker_cmd:
                             # Save temp file
                             cell.save(temp_input)
                             
                             # Run
                             import subprocess
                             # Hide console window on Windows if frozen
                             startupinfo = None
                             if os.name == 'nt' and getattr(sys, 'frozen', False):
                                 startupinfo = subprocess.STARTUPINFO()
                                 startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                                 
                             result = subprocess.run(worker_cmd, capture_output=True, text=True, startupinfo=startupinfo)
                             
                             if result.returncode == 0 and os.path.exists(temp_output):
                                 cell = Image.open(temp_output).convert("RGBA")
                                 cell.load() # Force read
                                 try:
                                     os.remove(temp_input)
                                     os.remove(temp_output)
                                 except: pass
                             else:
                                 print(f"Worker failed for {row},{col}: {result.stderr}")
                                 try:
                                     if os.path.exists(temp_input):
                                         os.remove(temp_input)
                                 except: pass
                        else:
                             print("Rembg worker not found (venv missing and no frozen exe). Skipping bg removal.")
 
                    except Exception as e:
                        print(f"Failed to remove bg for cell {row},{col}: {e}")
                
                # Normalize Visual Size (Trim & Center)
                if normalize_mode:
                    try:
                        cell = normalize_image_content(cell, scale_factor=scale_factor)
                    except Exception as e:
                        print(f"Normalization failed for cell {row},{col}: {e}")
                
                # Determine Filename
                idx = row * actual_cols + col
                cell_num = count + 1
                
                if rename:
                    cell_str = str(cell_num).zfill(num_digits)
                    if auto_suffix and image_seq > 0:
                        img_str = str(image_seq).zfill(num_digits)
                        filename = f"{rename}_{img_str}_{cell_str}.png"
                    else:
                        seq = start_index + count
                        filename = f"{rename}_{str(seq).zfill(num_digits)}.png"
                else:
                    if idx < len(item_filenames) and item_filenames[idx].strip():
                        base_name = item_filenames[idx]
                        if not base_name:
                            base_name = f"icon_{row+1:02d}_{col+1:02d}"
                    else:
                        base_name = f"icon_{row+1:02d}_{col+1:02d}"
                    filename = f"{base_name}.png"
                    dup_counter = 2
                    while os.path.exists(os.path.join(output_dir, filename)):
                        filename = f"{base_name}_{dup_counter}.png"
                        dup_counter += 1
                
                save_path = os.path.join(output_dir, filename)
                cell.save(save_path)
                count += 1
                
        msg = f"Successfully sliced {count} icons to '{output_dir}'"
        if 'csv_warning' in locals() and csv_warning:
            msg += f"\n\n{csv_warning}"
            
        return True, msg, count

    except Exception as e:
        return False, str(e), 0
