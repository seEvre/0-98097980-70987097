import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np

def remove_black_and_make_transparent(img):
    """Remove black and make it transparent."""
    img_rgba = img.convert("RGBA")  # Convert image to RGBA for transparency support
    width, height = img.size
    pixels = img_rgba.load()
    
    # Iterate through all pixels
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            # Check if the pixel is black (or very close to black)
            if r < 30 and g < 30 and b < 30:  # You can adjust the threshold
                pixels[x, y] = (0, 0, 0, 0)  # Set pixel to fully transparent
    return img_rgba

def process_image(uploaded_image):
    # 1. Set canvas size
    canvas_size = (2000, 133)
    
    # 2. Open and resize image for efficiency
    img = Image.open(uploaded_image).convert("RGB")
    img = img.resize(canvas_size, Image.Resampling.LANCZOS)
    
    # 3. Convert to black and white
    img = img.convert("L").convert("RGB")
    
    # 4. Adjust brightness and contrast
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(0.9)
    
    # 5. Remove black and make transparent
    img = remove_black_and_make_transparent(img)
    
    # 6. Duplicate the image (top and bottom layers)
    top_layer = img.copy()
    bottom_layer = img.copy()
    
    # 7. Apply Gaussian Blur to top layer
    top_layer = top_layer.filter(ImageFilter.GaussianBlur(17))
    top_layer = top_layer.putalpha(122)  # Apply opacity (122 out of 255)
    
    # 8. Apply Sepia tone to bottom layer
    sepia = np.array(bottom_layer, dtype=np.float32)
    sepia[:, :, 0] *= 1.2  # Red channel
    sepia[:, :, 1] *= 1.0  # Green channel
    sepia[:, :, 2] *= 0.8  # Blue channel
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    bottom_layer = Image.fromarray(sepia)
    bottom_layer = bottom_layer.putalpha(204)  # Apply opacity (204 out of 255)
    
    # 9. Merge the top and bottom layers
    merged_image = Image.alpha_composite(bottom_layer, top_layer)
    
    # 10. Create a new text layer (below the image layers)
    text_layer = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    
    # Add text to be displayed
    ad_text = "FLUORINES COOL CLOTHING SHOP!!"
    
    # Attempt to load the DejaVuSans-Bold font; otherwise, fallback to default
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 95)  # Set font size to 95
    except:
        font = ImageFont.load_default()
    
    # 11. Get text dimensions and center it
    text_width, text_height = draw.textbbox((0, 0), ad_text, font=font)[2:]
    text_position = ((canvas_size[0] - text_width) // 2, (canvas_size[1] - text_height) // 2)
    
    # 12. Draw the text on the text layer
    draw.text(text_position, ad_text, fill=(0, 0, 0, 255), font=font)
    
    # 13. Composite the text layer over the image
    final_image = Image.alpha_composite(merged_image, text_layer)
    
    return final_image

def main():
    st.title("Fast Image Processor App")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        with st.spinner("Processing image..."):
            processed_image = process_image(uploaded_file)
            
            # Display the processed image
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
