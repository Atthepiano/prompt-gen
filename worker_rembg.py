import argparse
import sys
import os
from PIL import Image

# Ensure dependencies are available
try:
    from rembg import remove, new_session
except ImportError:
    print("ERROR: rembg not installed in this environment.")
    sys.exit(1)

def process_image(input_path, output_path):
    try:
        if not os.path.exists(input_path):
            print(f"Error: Input file not found: {input_path}")
            sys.exit(1)

        print(f"Processing: {input_path}")
        
        # Open image
        with open(input_path, 'rb') as i:
            input_data = i.read()
            
            # Create session with explicit CPU provider to avoid detection errors
            # u2net is the default model
            try:
                session = new_session("u2net", providers=['CPUExecutionProvider'])
                output_data = remove(input_data, session=session)
            except Exception as e:
                # Fallback: try without specifying providers (let rembg decide) if CPU fails
                print(f"Warning: Explicit CPU session failed ({e}), retrying default...")
                output_data = remove(input_data)

            with open(output_path, 'wb') as o:
                o.write(output_data)
                
        print(f"Success: {output_path}")

    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remove background from image using rembg.')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', help='Output image path')
    
    args = parser.parse_args()
    process_image(args.input, args.output)
