import json

with open("./llamafactory_ocr_finetune_data/train.json") as train_src:
    train_ds = json.loads(train_src.read())


with open("./llamafactory_ocr_finetune_data/val.json") as val_src:
    val_ds = json.loads(val_src.read())




for idx in range(len(train_ds)):
    train_ds[idx]["images"][0] = train_ds[idx]["images"][0].replace(
        "/home/husammm/Desktop/courses/cs_courses/DL/projects/vlm_ocr_turkish/assets/pdf_images",
        "/workspace/pdf_images"
    )

for idx in range(len(val_ds)):
    val_ds[idx]["images"][0] = val_ds[idx]["images"][0].replace(
        "/home/husammm/Desktop/courses/cs_courses/DL/projects/vlm_ocr_turkish/assets/pdf_images",
        "/workspace/pdf_images"
    )







import os

dataset_dir = "./llamafactory_ocr_finetune_data"

with open(os.path.join(dataset_dir, "train_edited.json"), "w") as dest:
    json.dump(train_ds, dest, ensure_ascii=False, default=str)

with open(os.path.join(dataset_dir, "val_edited.json"), "w") as dest:
    json.dump(val_ds, dest, ensure_ascii=False, default=str)
