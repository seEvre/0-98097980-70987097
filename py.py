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
    
    # Apply Gaussian Blur efficiently to top layer
    top_layer = top_layer.filter(ImageFilter.GaussianBlur(10))
    top_layer = Image.blend(img, top_layer, 0.48)
    
    # Apply Sepia tone using NumPy to bottom layer
    sepia = np.array(bottom_layer, dtype=np.float32)
    sepia[:, :, 0] *= 1.2  # Red channel
    sepia[:, :, 1] *= 1.0  # Green channel
    sepia[:, :, 2] *= 0.8  # Blue channel
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    bottom_layer = Image.fromarray(sepia)
    
    # Merge layers
    merged_image = Image.blend(bottom_layer, top_layer, 1)
    
    # Create text pattern layer that covers the entire canvas
    text_layer = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw_text = ImageDraw.Draw(text_layer)
    ad_text = "Shop at Fluorine's Awesome Clothing Shop!!"
    
    # Choose a base font size; adjust as needed
    base_font_size = 50
    try:
        font = ImageFont.truetype("arial.ttf", base_font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text dimensions using a dummy image
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), ad_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Set spacing so that text repeats over entire canvas
    spacing_x = text_width + 20
    spacing_y = text_height + 20
    
    # Draw the text repeatedly over the canvas
    for y in range(0, canvas_size[1], spacing_y):
        for x in range(0, canvas_size[0], spacing_x):
            draw_text.text((x, y), ad_text, fill=(0, 0, 0, 255), font=font)
    
    # Convert merged_image to RGBA and reduce its opacity so the text shows through
    merged_image = merged_image.convert("RGBA")
    # Set opacity (alpha) to 200 out of 255
    merged_image.putalpha(200)
    
    # Composite the text layer under the processed image
    final_image = Image.alpha_composite(text_layer, merged_image)
    
    return final_image

def main():
    st.title("Fast Image Processor App")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        with st.spinner("Processing image..."):
            processed_image = process_image(uploaded_file)
            st.image(processed_image, caption="Processed Image", use_container_width=True)
            
            # Provide download option
            processed_image.save("output.png")
            with open("output.png", "rb") as file:
                st.download_button(label="Download Processed Image", data=file, file_name="processed_image.png", mime="image/png")

if __name__ == "__main__":
    main()
