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
    try:
        img = Image.open(uploaded_image).convert("RGB")
        img = img.resize(canvas_size, Image.Resampling.LANCZOS)
    except Exception as e:
        raise ValueError(f"Error opening or resizing image: {e}")
    
    # 3. Convert to black and white
    img = img.convert("L").convert("RGB")
    
    # 4. Adjust brightness and contrast
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(0.9)
    
    # 5. Remove black and make transparent
    img = remove_black_and_make_transparent(img)
    
    # 6. Duplicate the image (top and bottom layers)
    try:
        top_layer = img.copy()
        bottom_layer = img.copy()
        if top_layer is None or bottom_layer is None:
            raise ValueError("Top or Bottom layers are None after copying.")
    except Exception as e:
        raise ValueError(f"Error during layer duplication: {e}")
    
    # Debugging: Check if top_layer and bottom_layer are created
    if top_layer is None or bottom_layer is None:
        raise ValueError("Layer duplication failed: one of the layers is None.")
    
    # 7. Apply Gaussian Blur to top layer
    try:
        top_layer = top_layer.filter(ImageFilter.GaussianBlur(17))
        top_layer = top_layer.putalpha(122)  # Apply opacity (122 out of 255)
    except Exception as e:
        raise ValueError(f"Error applying Gaussian blur to top layer: {e}")
    
    # 8. Apply Sepia tone to bottom layer
    try:
        sepia = np.array(bottom_layer, dtype=np.float32)
        sepia[:, :, 0] *= 1.2  # Red channel
        sepia[:, :, 1] *= 1.0  # Green channel
        sepia[:, :, 2] *= 0.8  # Blue channel
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        bottom_layer = Image.fromarray(sepia)
        bottom_layer = bottom_layer.putalpha(204)  # Apply opacity (204 out of 255)
    except Exception as e:
        raise ValueError(f"Error applying sepia tone to bottom layer: {e}")
    
    # 9. Ensure layers are in RGBA format
    try:
        top_layer = top_layer.convert("RGBA")
        bottom_layer = bottom_layer.convert("RGBA")
    except Exception as e:
        raise ValueError(f"Error converting layers to RGBA: {e}")
    
    # Debugging: Verify that layers have been converted correctly
    if top_layer.mode != 'RGBA' or bottom_layer.mode != 'RGBA':
        raise ValueError(f"Layer conversion failed: top_layer mode={top_layer.mode}, bottom_layer mode={bottom_layer.mode}")
    
    # Debugging: Check layer sizes and if they are created properly
    if top_layer.size != bottom_layer.size:
        raise ValueError(f"Top and Bottom layers have different sizes: {top_layer.size}, {bottom_layer.size}")
    
    # 10. Merge the top and bottom layers
    try:
        merged_image = Image.alpha_composite(bottom_layer, top_layer)
    except Exception as e:
        raise ValueError(f"Error during image compositing: {e}")
    
    # 11. Create a new text layer (below the image layers)
    text_layer = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    
    # Add text to be displayed
    ad_text = "FLUORINES COOL CLOTHING SHOP!!"
    
    # Attempt to load the DejaVuSans-Bold font; otherwise, fallback to default
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 95)  # Set font size to 95
    except Exception as e:
        font = ImageFont.load_default()
        st.warning(f"Font loading failed, using default. Error: {e}")
    
    # 12. Get text dimensions and center it
    text_bbox = draw.textbbox((0, 0), ad_text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_position = ((canvas_size[0] - text_width) // 2, (canvas_size[1] - text_height) // 2)
    
    # 13. Draw the text on the text layer
    text_fill = (0, 0, 0, 150)  # Adjust the alpha for opacity (150 means semi-transparent)
    draw.text(text_position, ad_text, fill=text_fill, font=font)
    
    # Debugging: Check if text layer is created properly
    if text_layer is None:
        raise ValueError("Text layer is not created properly.")
    
    # 14. Composite the text layer over the image
    try:
        final_image = Image.alpha_composite(merged_image, text_layer)
    except Exception as e:
        raise ValueError(f"Error during final compositing: {e}")
    
    return final_image

def main():
    st.title("Fast Image Processor App")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        with st.spinner("Processing image..."):
            try:
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
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    main()
