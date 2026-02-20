import json
import random

from utils import parse_json

def get_dataset(config, dataset_path, task_1_prompt, task_2_prompt):
    train_ds = []
    val_ds = []

    ## Rething about validation files
    val_files = config.data["val"]

    image_paths_set = set()
    for line in open(dataset_path):
        if line.strip() == "":
            continue

        record = json.loads(line.strip())
        llm_output = parse_json(record['output'])
        if not llm_output:
            continue

        ## Make sure not to use an image twice
        if record['image_path'] in image_paths_set:
            continue
        image_paths_set.add(record['image_path'])

        ## Split llm_output to match 2 tasks
        task_1_output = {
            "content": llm_output["content"],
            "structural_elements": llm_output.get("structural_elements", "")
        }
        del llm_output['content']
        if llm_output.get("structural_elements"):
            del llm_output["structural_elements"]

        task_2_output = llm_output

        task_1_message = {
            "conversations": [
                {
                    "from": "human",
                    "value": "<image>"+task_1_prompt
                },
                {
                    "from": "gpt",
                    "value": json.dumps(task_1_output,
                                        ensure_ascii=False, default=str)
                }
            ],
            "images": [
                record['image_path']
            ]
        }

        task_2_message = {
            "conversations": [
                {
                    "from": "human",
                    "value": "<image>"+task_2_prompt
                },
                {
                    "from": "gpt",
                    "value": json.dumps(task_2_output,
                                        ensure_ascii=False, default=str)
                }
            ],
            "images": [
                record['image_path']
            ]
        }

        if record['pdf_name'] in val_files[record['pdf_type']]:
            val_ds.append(task_1_message)
            val_ds.append(task_2_message)
        else:
            train_ds.append(task_1_message)
            train_ds.append(task_2_message)

    random.Random(31).shuffle(train_ds)
    random.Random(31).shuffle(val_ds)

    return train_ds, val_ds