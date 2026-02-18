import os
from glob import glob
from utils import convert_pdf_to_images, image_preprocesing



assets_dir = "/home/husammm/Desktop/courses/cs_courses/DL/projects/vlm_ocr_turkish/assets"
circulars_dir = os.path.join(assets_dir, "circulars")
decrees_dir = os.path.join(assets_dir, "decrees")

def pdf_to_images():
    pdf_images = os.path.join(assets_dir, "pdf_images")
    os.makedirs(pdf_images, exist_ok=True)

    circular_pdfs = glob(os.path.join(circulars_dir, "*.pdf"))
    circular_img_dir = os.path.join(pdf_images, "circular_images")
    os.makedirs(circular_img_dir, exist_ok=True)
    for circular_pdf in circular_pdfs:
        _ = convert_pdf_to_images(circular_pdf, circular_img_dir)
    
    decrees_pdfs = glob(os.path.join(decrees_dir, "*.pdf"))
    decrees_img_dir = os.path.join(pdf_images, "decrees_images")
    os.makedirs(decrees_img_dir, exist_ok=True)
    for decrees_pdf in decrees_pdfs:
        _ = convert_pdf_to_images(decrees_pdf, decrees_img_dir)
    
    



if __name__ == "__main__":
    # pdf_to_images()
    pass