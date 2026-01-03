import slicer_tool as st
from PIL import Image, ImageDraw
import os

def test_slicer():
    print("Testing Slicer Tool...")
    
    # 1. Create a dummy image (800x800)
    img_path = "test_grid.png"
    img = Image.new('RGB', (800, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw grid lines for visibility
    for i in range(1, 8):
        y = i * 100
        draw.line([(0, y), (800, y)], fill='black', width=2)
        x = i * 100
        draw.line([(x, 0), (x, 800)], fill='black', width=2)
        
    img.save(img_path)
    print(f"Created dummy image: {img_path}")
    
    # 2. Slice it
    success, msg, count = st.slice_image(img_path)
    
    # 3. Verify output
    expected_dir = "test_grid_slices"
    if success and count == 64 and os.path.exists(expected_dir):
        files = os.listdir(expected_dir)
        if len(files) == 64:
            print("SUCCESS: Sliced 64 images correctly.")
        else:
            print(f"FAIL: File count mismatch. Expected 64, found {len(files)}")
    else:
        print(f"FAIL: Slicing reported failure. {msg}")
        
    # Cleanup (Optional)
    # os.remove(img_path)
    # import shutil
    # shutil.rmtree(expected_dir)

if __name__ == "__main__":
    test_slicer()
