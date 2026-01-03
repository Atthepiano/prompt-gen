import item_generator as ig
import slicer_tool as st
import translation_service as ts
import os
from PIL import Image

def test_translation_service():
    print("\n--- Testing Translation Service ---")
    tm = ts.TranslationManager()
    text = "测试"
    result = tm.translate_text(text)
    print(f"Original: {text}, Translated: {result}")
    if result.lower() in ["test", "testing", "trial"]:
        print("SUCCESS: Translation working.")
        return True
    else:
        print("WARNING: Translation result unexpected (check network/API).")
        return False

def test_item_prompt_translation():
    print("\n--- Testing Item Prompt Translation ---")
    items = [("药水", "恢复生命值")]
    prompt = ig.generate_icon_grid_prompt(items, translate=True)
    
    if "Potion" in prompt or "Medicine" in prompt or "Restore" in prompt:
        print("SUCCESS: Prompt translated.")
        # print("Preview:", prompt[:200])
    else:
        print("FAIL: Prompt translation not found.")

def test_slicer_smart_naming():
    print("\n--- Testing Slicer Smart Naming ---")
    
    # 1. Create Dummy Image
    img_path = "test_smart_grid.png"
    Image.new('RGB', (800, 800), color='white').save(img_path)
    
    # 2. Create Dummy CSV
    csv_path = "test_smart_names.csv"
    with open(csv_path, "w", encoding='utf-8-sig') as f:
        f.write("剑,描述\n盾,描述")
        
    # 3. Running Slicer with Translate = True
    output_dir = "test_smart_slices"
    st.slice_image(img_path, grid_rows=8, grid_cols=8, output_dir=output_dir, csv_path=csv_path, translate_mode=True)
    
    # 4. Check Files
    files = os.listdir(output_dir)
    found_sword = any("sword" in f.lower() or "jian" in f.lower() for f in files)
    found_shield = any("shield" in f.lower() or "dun" in f.lower() for f in files)
    
    if found_sword or found_shield:
         print(f"SUCCESS: Found translated filenames in {output_dir}")
         print(files[:5])
    else:
         print(f"FAIL: Translated filenames not found. Files: {files[:5]}")

    # Cleanup
    # os.remove(img_path)
    # os.remove(csv_path)

if __name__ == "__main__":
    if test_translation_service():
        test_item_prompt_translation()
        test_slicer_smart_naming()
