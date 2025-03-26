from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np
import streamlit as st

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
    
    # 7. Create text layer (this layer will be the bottom one, so we composite it last)
    text_layer = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    
    ad_text = "FLUORINES COOL CLOTHING SHOP!!"
    
    # 8. Use DejaVuSans-Bold font available by default in Streamlit Cloud with size 95
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 95)  # Set font size to 95
    except:
        font = ImageFont.load_default()  # Fallback to default font if DejaVuSans-Bold is unavailable
    
    # 9. Get text dimensions and center it using textbbox
    text_bbox = draw.textbbox((0, 0), ad_text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]  # Calculate width and height
    text_position = ((canvas_size[0] - text_width) // 2, (canvas_size[1] - text_height) // 2)
    
    # 10. Draw the text on the text layer
    draw.text(text_position, ad_text, fill=(0, 0, 0, 255), font=font)
    
    # 11. Merge the image layers on top of the text (so text is at the bottom)
    final_image = Image.alpha_composite(text_layer, bottom_layer)  # Composite the text as bottom layer first
    final_image = Image.alpha_composite(final_image, top_layer)  # Composite the other image layers on top
    
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
