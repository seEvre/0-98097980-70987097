import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np
from io import BytesIO

def remove_black_and_make_transparent(img):
    """Remove black pixels and make them transparent."""
    img_rgba = img.convert("RGBA")
    width, height = img.size
    pixels = img_rgba.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r < 30 and g < 30 and b < 30:  # Adjust threshold as needed
                pixels[x, y] = (0, 0, 0, 0)  # Fully transparent
    return img_rgba

def process_image(uploaded_image):
    # Set canvas size
    canvas_size = (2000, 133)
    
    # Open and resize image
    try:
        img = Image.open(BytesIO(uploaded_image.read())).convert("RGB")
        img = img.resize(canvas_size, Image.Resampling.LANCZOS)
    except Exception as e:
        raise ValueError(f"Error opening or resizing image: {e}")
    
    # Convert to black and white
    img = img.convert("L").convert("RGB")
    
    # Adjust brightness and contrast
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(0.9)
    
    # Remove black pixels and make them transparent
    img = remove_black_and_make_transparent(img)
    
    # Duplicate the image for top and bottom layers
    top_layer = img.copy()
    bottom_layer = img.copy()
    
    # Apply Gaussian Blur to top layer
    top_layer = top_layer.filter(ImageFilter.GaussianBlur(17))
    top_layer.putalpha(122)  # Set opacity
    
    # Apply Sepia tone to bottom layer
    sepia = np.array(bottom_layer, dtype=np.float32)
    sepia[:, :, 0] *= 1.2  # Red channel
    sepia[:, :, 1] *= 1.0  # Green channel
    sepia[:, :, 2] *= 0.8  # Blue channel
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    bottom_layer = Image.fromarray(sepia)
    bottom_layer.putalpha(204)  # Set opacity
    
    # Ensure layers are in RGBA format
    top_layer = top_layer.convert("RGBA") if top_layer else None
    bottom_layer = bottom_layer.convert("RGBA") if bottom_layer else None
    if not top_layer or not bottom_layer:
        raise ValueError("Failed to convert layers to RGBA.")
    
    # Merge the top and bottom layers
    merged_image = Image.alpha_composite(bottom_layer, top_layer)
    
    # Create a text layer
    text_layer = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    ad_text = "FLUORINES COOL CLOTHING SHOP!!"
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 95)
    except IOError:
        font = ImageFont.load_default()
        st.warning("Custom font not found, using default.")
    text_bbox = draw.textbbox((0, 0), ad_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((canvas_size[0] - text_width) // 2, (canvas_size[1] - text_height) // 2)
    draw.text(text_position, ad_text, fill=(0, 0, 0, 150), font=font)
    
    # Composite the text layer over the image
    final_image = Image.alpha_composite(merged_image, text_layer)
    return final_image

def main():
    st.title("Fast Image Processor App")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        with st.spinner("Processing image..."):
            try:
                processed_image = process_image(uploaded_file)
                st.image(processed_image, caption="Processed Image", use_container_width=True)
                processed_image.save("output.png")
                with open("output.png", "rb") as file:
                    st.download_button(
                        label="Download Processed Image",
                        data=file,
                        file_name="processed_image.png",
                        mime="image/png"
                    )
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
    else:
        st.info("Please upload an image to begin.")

if __name__ == "__main__":
    main()
