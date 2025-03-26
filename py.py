import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np

def process_image(uploaded_image):
    # Set canvas size
    canvas_size = (2000, 133)
    
    # Open and resize image early for efficiency
    img = Image.open(uploaded_image).convert("RGB")
    img = img.resize(canvas_size, Image.Resampling.LANCZOS)
    
    # Convert to black and white
    img = img.convert("L").convert("RGB")
    
    # Adjust brightness and contrast
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(0.9)
    
    # Duplicate the image
    top_layer = img.copy()
    bottom_layer = img.copy()
    
    # Apply Gaussian Blur efficiently
    top_layer = top_layer.filter(ImageFilter.GaussianBlur(10))
    top_layer = Image.blend(img, top_layer, 0.48)
    
    # Apply Sepia tone using NumPy
    sepia = np.array(bottom_layer, dtype=np.float32)
    sepia[:, :, 0] *= 1.2  # Red channel
    sepia[:, :, 1] *= 1.0  # Green channel
    sepia[:, :, 2] *= 0.8  # Blue channel
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    bottom_layer = Image.fromarray(sepia)
    
    # Merge layers
    merged_image = Image.blend(bottom_layer, top_layer, 1)
    
    # Add text overlay
    draw = ImageDraw.Draw(merged_image)
    font_size = 50
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    text = "YOUR AD HERE"
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    text_position = ((canvas_size[0] - text_width) // 2, (canvas_size[1] - text_height) // 2)
    draw.text(text_position, text, fill="black", font=font)
    
    return merged_image

def main():
    st.title("Fast Image Processor App")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        with st.spinner("Processing image..."):
            processed_image = process_image(uploaded_file)
            st.image(processed_image, caption="Processed Image", use_column_width=True)
            
            # Provide download option
            processed_image.save("output.png")
            with open("output.png", "rb") as file:
                st.download_button(label="Download Processed Image", data=file, file_name="processed_image.png", mime="image/png")

if __name__ == "__main__":
    main()
