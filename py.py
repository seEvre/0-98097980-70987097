import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np

def process_image(uploaded_image):
    # Create canvas
    canvas_size = (2000, 133)
    base_image = Image.new('RGB', canvas_size, (255, 255, 255))
    
    # Open and resize image
    img = Image.open(uploaded_image).convert("RGB")
    img = img.resize((2000, 133), Image.ANTIALIAS)
    
    # Convert to black and white
    img = img.convert("L").convert("RGB")
    
    # Adjust brightness and contrast
    enhancer_b = ImageEnhance.Brightness(img)
    img = enhancer_b.enhance(11/10)
    enhancer_c = ImageEnhance.Contrast(img)
    img = enhancer_c.enhance(0.9)
    
    # Duplicate the image
    top_layer = img.copy()
    bottom_layer = img.copy()
    
    # Apply Gaussian Blur to top layer
    top_layer = top_layer.filter(ImageFilter.GaussianBlur(17))
    top_layer = Image.blend(img, top_layer, 122/255)
    
    # Apply Sepia tone to bottom layer
    sepia = np.array(bottom_layer)
    sepia = sepia * [1.2, 1.0, 0.8]
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
    text_width, text_height = draw.textsize(text, font=font)
    text_position = ((2000 - text_width) // 2, (133 - text_height) // 2)
    draw.text(text_position, text, fill="black", font=font)
    
    return merged_image

def main():
    st.title("Image Processor App")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        processed_image = process_image(uploaded_file)
        st.image(processed_image, caption="Processed Image", use_column_width=True)
        
        # Provide download option
        processed_image.save("output.png")
        with open("output.png", "rb") as file:
            btn = st.download_button(label="Download Processed Image", data=file, file_name="processed_image.png", mime="image/png")

if __name__ == "__main__":
    main()
