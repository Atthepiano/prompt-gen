import os
import shutil
from collections import defaultdict
from typing import List, Dict, Tuple

class AssetCurator:
    def __init__(self):
        self.sources = []
        self.target_dir = ""
        self.conflict_map = defaultdict(list)
        self.total_files = 0
        self.resolved_count = 0
        self.current_conflicts = [] # List of filenames that need resolution
        
    def set_config(self, source_dirs: List[str], target_dir: str):
        self.sources = source_dirs
        self.target_dir = target_dir
        
    def scan_files(self) -> Tuple[int, int]:
        """
        Scans source directories and groups files by name.
        Returns: (total_unique_filenames, conflict_count)
        """
        self.conflict_map.clear()
        self.current_conflicts.clear()
        self.resolved_count = 0
        
        valid_exts = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        
        for src in self.sources:
            if not os.path.exists(src):
                continue
                
            for root, dirs, files in os.walk(src):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in valid_exts:
                        full_path = os.path.join(root, f)
                        # We use simple filename as key. 
                        # If user has nested folders matching exactly, this might flatten them.
                        # For generated assets, flattening is usually desired or acceptable.
                        self.conflict_map[f].append(full_path)
        
        self.total_files = len(self.conflict_map)
        
        # Prepare conflict list
        for fname, paths in self.conflict_map.items():
            if len(paths) > 1:
                self.current_conflicts.append(fname)
                
        conflict_count = len(self.current_conflicts)
        return self.total_files, conflict_count

    def auto_resolve_uniques(self) -> int:
        """
        Moves files that have no conflicts (only exist in one source).
        Returns count of moved files.
        """
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
            
        count = 0
        # Iterate over a copy of keys since we might assume they are 'resolved'
        # But actually, we just perform the copy.
        
        for fname, paths in self.conflict_map.items():
            if len(paths) == 1:
                src_path = paths[0]
                dst_path = os.path.join(self.target_dir, fname)
                
                # Check if already exists in target (optional safety)
                if not os.path.exists(dst_path):
                    try:
                        shutil.copy2(src_path, dst_path)
                        count += 1
                        self.resolved_count += 1
                    except Exception as e:
                        print(f"Error copying {src_path}: {e}")
        
        return count

    def get_pending_conflicts(self) -> List[str]:
        """Returns list of filenames that still need resolution."""
        # Filter conflict_map for items that are strictly conflicts and NOT yet resolved?
        # Actually simplest to just stick to the pre-calculated list.
        return self.current_conflicts

    def get_variants(self, filename: str) -> List[str]:
        """Returns list of full paths for a given filename."""
        return self.conflict_map.get(filename, [])

    def commit_selection(self, filename: str, selected_path: str):
        """
        Copies the selected variant to target.
        """
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
            
        dst_path = os.path.join(self.target_dir, filename)
        try:
            shutil.copy2(selected_path, dst_path)
            self.resolved_count += 1
            return True
        except Exception as e:
            print(f"Error copying {selected_path}: {e}")
            return False

    def skip_file(self, filename: str):
        """Explicitly skip a file (count as resolved but don't copy)."""
        self.resolved_count += 1
