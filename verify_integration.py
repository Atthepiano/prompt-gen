import item_generator as ig
import os

def test_verification():
    print("Testing Item Generator...")
    
    # 1. Test CSV Path
    csv_path = ig.DEFAULT_CSV_PATH
    print(f"Checking CSV path: {csv_path} -> {os.path.exists(csv_path)}")
    
    # 2. Test Reading Items
    items = ig.read_items_from_csv(csv_path)
    print(f"Items found: {len(items)}")
    
    if len(items) == 0:
        print("FAIL: No items read.")
        return
        
    print("First item:", items[0])
    
    # 3. Test Generation
    prompt = ig.generate_icon_grid_prompt(items)
    
    if "8x8" in prompt and "Konami" in prompt and "WHITE" in prompt and "NO TEXT" in prompt:
        print("SUCCESS: Prompt generated successfully containing target style (Konami + White BG + No Text).")
        # print("--- Preview ---\n" + prompt[:500] + "...")
    else:
        print("FAIL: Generated prompt missing expected keywords or data.")

if __name__ == "__main__":
    test_verification()
