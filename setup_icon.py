from PIL import Image
import shutil
import os

# Source path from the generate_image tool output
src = r"C:/Users/shiva/.gemini/antigravity/brain/7f495f81-aa80-4d87-8fd1-70ff8e1ec25f/app_icon_1769779259630.png"
dst_dir = r"C:/Users/shiva/.gemini/antigravity/scratch/billing_app/assets"

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

dst_png = os.path.join(dst_dir, "icon.png")
dst_ico = os.path.join(dst_dir, "icon.ico")

# Copy
shutil.copy(src, dst_png)
print(f"Copied icon to {dst_png}")

# Convert to ICO
try:
    img = Image.open(dst_png)
    # Save as ICO with optimal sizes for Windows
    img.save(dst_ico, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]) 
    print(f"Converted icon to {dst_ico}")
except Exception as e:
    print(f"Error converting icon: {e}")
