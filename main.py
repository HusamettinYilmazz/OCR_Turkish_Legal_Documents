import os
from glob import glob
from dotenv import load_dotenv
import requests
from tqdm import tqdm
import json

from transformers import Gemma3ForConditionalGeneration, AutoProcessor
import torch

from PIL import Image

import litellm
from litellm import completion

from utils import convert_pdf_to_images, image_preprocesing
from utils import image_to_base64_data_uri
from utils import Logger, load_config, get_last_row

from src import get_dataset

load_dotenv()
ROOT = "/home/husammm/Desktop/courses/cs_courses/DL/projects/vlm_ocr_turkish/"

def pdf_to_images(assets_dir):
    circulars_dir = os.path.join(assets_dir, "circulars")
    decrees_dir = os.path.join(assets_dir, "decrees")

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

def generate_output_gemini3(model_id, prompt, image_path):
    
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_to_base64_data_uri(image_path)
                    }
                }

            ]
        }
    ]

    response = completion(
        model=model_id,
        messages=messages,
        max_tokens=4096
    )

    return response

def pdf_its_images(pdf_images_path):
    ## build a dictinory of {"pdf_type": {"pdf_num": pdf_images_paths}}
    pdf_types = glob(os.path.join(pdf_images_path, "*"))
    pdf_images_dict = {}
    for pdf_type in pdf_types:
        pdf_files = glob(os.path.join(pdf_type, "*"))
        pdf_type = os.path.basename(pdf_type).replace("_images", "")

        pdf_images_dict[pdf_type] = {}
        for idx, pdf_name in enumerate(pdf_files):
            pdf_num = os.path.splitext(os.path.basename(pdf_name))[0][:2]
            
            pdf_images_dict[pdf_type][pdf_num] = glob(os.path.join(pdf_files[idx], "*.jpg"))

    return pdf_images_dict

def knowladge_distilation(save_dir, pdf_images_dict, prompt):
    model_id = "openai/google/gemini-3-flash-preview"
    logger = Logger(save_dir)
    target_dir = os.path.join(save_dir, "llm_response")
    os.makedirs(target_dir, exist_ok=True)
    generated_target_file = os.path.join(target_dir, "image_ocr.jsonl")
    
    ## current price at openrouter
    price_1m_input_tokens = 0.5
    price_1m_output_tokens = 0.3

    prompt_tokens = 0
    completion_tokens = 0

    img_idx = 0
    completed_idx = get_last_row(generated_target_file)["id"]
    for pdf_type, pdf_images in pdf_images_dict.items():
        # pdf_images = pdf_images_dict[pdf_type]
        for pdf_num, image_paths in pdf_images.items():

            # print(f"file_{pdf_num}")
            for image_path in tqdm(image_paths, desc=f"{pdf_type}: file_{pdf_num}"):
                img_idx += 1
                if img_idx <= completed_idx:
                    continue
                response = generate_output_gemini3(model_id, prompt, image_path)

                ## Check if response has an issue
                if response:
                    if response.choices[0].finish_reason != 'stop':
                        logger.info(f"Error stop: pdf type: {pdf_type} pdf number: {pdf_num} at image number (global): {img_idx}, {response.choices[0].finish_reason}")
                        continue
                    llm_response = response.choices[0].message.content
                
                logger.info(response)
                ## Write the content of response to json file
                with open(generated_target_file, "a", encoding="utf8") as dest:
                    dest.write(json.dumps(
                        {
                            "id": img_idx,
                            "pdf_type": pdf_type,
                            "pdf_name": pdf_num,
                            "image_path": image_path,
                            "model_id": model_id,
                            "output": llm_response
                        },
                        default=str, ensure_ascii=False,
                    ) + "\n")

                prompt_tokens += response.usage['prompt_tokens']
                completion_tokens += response.usage['completion_tokens']

                ## Calculate total cost each 10 images
                if img_idx % 10 == 0:
                    input_cost = (prompt_tokens / 1_000_000) * price_1m_input_tokens
                    output_cost = (completion_tokens / 1_000_000) * price_1m_output_tokens
                    total_cost = input_cost + output_cost
                    logger.info(f"Input tokens cost: {input_cost}")
                    logger.info(f"Output tokens cost: {output_cost}")
                    logger.info(f"Total cost: {total_cost:.3f} for {img_idx} images")
    
    logger.info(f"Total number of images: {img_idx}")
    return input_cost, output_cost

def build_dataset(config):
    llm_response_path = os.path.join(ROOT, "outputs/llm_response/image_ocr.jsonl")
    task_1_prompt = load_prompt(os.path.join(ROOT, "prompts/task1.txt"))
    task_2_prompt = load_prompt(os.path.join(ROOT, "prompts/task2.txt"))
    train_ds, val_ds = get_dataset(config, llm_response_path, task_1_prompt, task_2_prompt)
    
    dataset_dir = os.path.join(ROOT, "assets", "llamafactory_ocr_finetune_data")
    os.makedirs(dataset_dir, exist_ok=True)

    with open(os.path.join(dataset_dir, "train.json"), "w") as dest:
        json.dump(train_ds, dest, ensure_ascii=False, default=str)

    with open(os.path.join(dataset_dir, "val.json"), "w") as dest:
        json.dump(val_ds, dest, ensure_ascii=False, default=str)



def main():
    config_path = os.path.join(ROOT, "configs/config.yaml")
    config = load_config(config_path)
    
    assets_dir = os.path.join(ROOT, config.data["dataset_path"])
    pdf_images = os.path.join(assets_dir, "pdf_images")
    prompt_path = os.path.join(ROOT, config.data["prompt_path"])
    save_dir = os.path.join(ROOT, config.data["output_path"])
    
    hf_token = os.getenv("hf_token")
    open_router_key = os.getenv("open_router_key")
    os.environ["OPENAI_API_KEY"] = open_router_key
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
    
    # pdf_images_dict = pdf_its_images(pdf_images)
    # prompt = load_prompt(prompt_path)
    
    # test_gemma3(hf_token, prompt, sample_image)
    # input_cost, output_cost = knowladge_distilation(save_dir, pdf_images_dict, prompt)

    build_dataset(config)

if __name__ == "__main__":
    main()