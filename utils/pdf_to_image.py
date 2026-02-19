import os

from pdf2image import convert_from_path
from PIL import Image, ImageEnhance

import base64

def image_preprocesing(image: Image, max_width: int =600) -> Image:
    """
    Args:
        image: PIL image object
        max_width: Maximum width in pixels(height auto-scaled to maintain ratio)

    Steps:
        1. Convert to grayscale (reduces size and improves OCR)
        2. Resize to reasonable scale (width, height)
        3. Increase contrast

    Return:
        enhanced_image: Contrast enhanced gray scale Image object
    """

    # Convert to grayscale
    gray_image = image.convert('L')

    # Resize if exceeding max_width
    if gray_image.width > max_width:
        ratio = gray_image.height / gray_image.width
        new_height = int(max_width * ratio)

        gray_image = gray_image.resize((max_width, new_height), Image.LANCZOS)

    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(1.5)

    return enhanced_image

def convert_pdf_to_images(pdf_path, images_base_dir, max_width=600):
    """
    Args:
        pdf_path: Path to the pdf file
        output_images_dir: Base directory to save images
        max_width: Maximum width in pixels(height auto-scaled to maintain ratio)

    Steps:
        1. Extract images from pdf
        2. write all images to a pdf's specificed dir
    Return:
        a set of image pathes
    """
    # Pdf name
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0][:2]

    # Create pdf's images output dir
    output_dir = os.path.join(images_base_dir, pdf_name)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Converting {pdf_name}document.pdf")
    images = convert_from_path(pdf_path, dpi=200)
    generated_paths = []

    # Process and save each page as jpeg image
    for image_num, image in enumerate(images, start=1):

        # Preprocess image
        preprocessed_image = image_preprocesing(image, max_width)

        # Save image
        image_output_path = os.path.join(output_dir, f"{image_num:03d}.jpg")
        preprocessed_image.save(image_output_path, format="JPEG", quality=100, optimize=True)
        print(f"Page num: {image_num} saved to {image_output_path}")

        generated_paths.append(image_output_path)

    return generated_paths

def image_to_base64_data_uri(image_path):
    """Convert image to base64 data URI for APIs"""
    with open(image_path, 'rb') as image_file:
        img_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # Determine image type from extension
    ext = image_path.lower().split('.')[-1]
    mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"

    return f"data:{mime_type};base64,{img_base64}"