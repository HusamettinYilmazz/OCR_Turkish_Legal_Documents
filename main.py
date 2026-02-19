import os
from glob import glob
from dotenv import load_dotenv
import requests

from transformers import Gemma3ForConditionalGeneration, AutoProcessor
import torch

from PIL import Image

from utils import convert_pdf_to_images, image_preprocesing


load_dotenv()
assets_dir = "/home/husammm/Desktop/courses/cs_courses/DL/projects/vlm_ocr_turkish/assets"
circulars_dir = os.path.join(assets_dir, "circulars")
decrees_dir = os.path.join(assets_dir, "decrees")
pdf_images = os.path.join(assets_dir, "pdf_images")
prompt_path = "/home/husammm/Desktop/courses/cs_courses/DL/projects/vlm_ocr_turkish/prompts/extraction_prompt.txt"

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
    
def load_prompt(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as prompt_file:
        return prompt_file.read()

def test_gemma3(hf_token, prompt, image):
    model_id = "google/gemma-3-4b-it"
      
    model = Gemma3ForConditionalGeneration.from_pretrained(
        model_id,
        dtype="auto",
        device_map="auto",
        token=hf_token
    ).eval()

    processor = AutoProcessor.from_pretrained(model_id)

    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}]
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)

    input_len = inputs["input_ids"].shape[-1]

    with torch.inference_mode():
        generation = model.generate(**inputs, max_new_tokens=1024, do_sample=False)
        generation = generation[0][input_len:]

    decoded = processor.decode(generation, skip_special_tokens=True)
    print(decoded)

if __name__ == "__main__":
    # pdf_to_images()

    hf_token = os.getenv("hf_token")
    prompt = load_prompt(prompt_path)
    sample_image = Image.open(f"{pdf_images}circular_images/01/002.jpg")

    # test_gemma3(hf_token, prompt, sample_image)
