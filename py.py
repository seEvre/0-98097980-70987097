import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np

def process_image(uploaded_image):
    # Set canvas size
    canvas_size = (2000, 133)
    
    # 1. Open and resize image early for efficiency
    img = Image.open(uploaded_image).convert("RGB")
    img = img.resize(canvas_size, Image.Resampling.LANCZOS)
    
    # 2. Convert to black and white
    img = img.convert("L").convert("RGB")
    
    # 3. Adjust brightness and contrast
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(0.9)
    
    # 4. Duplicate the image
    top_layer = img.copy()
    bottom_layer = img.copy()
    
    # 5. Apply Gaussian Blur to top layer
    top_layer = top_layer.filter(ImageFilter.GaussianBlur(10))
    top_layer = Image.blend(img, top_layer, 0.48)
    
    # 6. Apply Sepia tone using NumPy to bottom layer
    sepia = np.array(bottom_layer, dtype=np.float32)
    sepia[:, :, 0] *= 1.2  # Red channel
    sepia[:, :, 1] *= 1.0  # Green channel
    sepia[:, :, 2] *= 0.8  # Blue channel
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    bottom_layer = Image.fromarray(sepia)
    
    # 7. Merge layers
    merged_image = Image.blend(bottom_layer, top_layer, 1)
    merged_image = merged_image.convert("RGBA")  # Convert to RGBA
    
    # 8. Create text layer
    text_layer = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    
    ad_text = "FLUORINES COOL CLOTHING SHOP!!"
    
    # Attempt to load a TTF font; otherwise, fallback
    try:
        font_path = "arial.ttf"
        font_size = 10  # Start small
        font = ImageFont.truetype(font_path, font_size)
        
        # Dynamically find the max font size that fits the width & height
        while True:
            text_width, text_height = draw.textbbox((0, 0), ad_text, font=font)[2:]
            if text_width >= canvas_size[0] * 0.98 or text_height >= canvas_size[1] * 0.98:
                break  # Stop when it's just below the max size
            font_size += 2
            font = ImageFont.truetype(font_path, font_size)

    except:
        font = ImageFont.load_default()
    
    # 9. Center text
    text_width, text_height = draw.textbbox((0, 0), ad_text, font=font)[2:]
    text_position = ((canvas_size[0] - text_width) // 2, (canvas_size[1] - text_height) // 2)
    
    # 10. Draw the text
    draw.text(text_position, ad_text, fill=(0, 0, 0, 255), font=font)
    
    # 11. Composite text over image
    final_image = Image.alpha_composite(merged_image, text_layer)
    
    return final_image

def main():
    st.title("Fast Image Processor App")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        with st.spinner("Processing image..."):
            processed_image = process_image(uploaded_file)
            
            # Use the newer parameter
            st.image(processed_image, caption="Processed Image", use_container_width=True)
            
            # Provide download option
            processed_image.save("output.png")
            with open("output.png", "rb") as file:
                st.download_button(
                    label="Download Processed Image",
                    data=file,
                    file_name="processed_image.png",
                    mime="image/png"
                )

if __name__ == "__main__":
    main()
