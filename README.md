<h1 align="center">Beyond OCR: Finetuning VLM for Turkish Legal Documents</h1>

<p align="center">
  Sometimes we resort to Vision-Language Models (VLMs) to perform OCR on documents. If we are already using a VLM, we can benefit from its capabilities to extract more than just plain text. Instead of limiting the output to OCR, the model can also extract structured information such as stamps, person names, and the structural elements of the page like tables and lists.
</p>



## Table of Contents
1. [Usage](#usage)
    - [Clone the Repository](#1-clone-the-repository)
    - [Create conda environment](#2-create-conda-environment)
    - [Install Dependencies](#3-install-the-required-dependencies)
    - [Download Model Checkpoint](#4-download-the-model-checkpoint)

2. [Example Outputs](#example-outputs)
3. [Dataset](#dataset)
4. [Training](#training)
5. [Evaluation](#evaluation) 
    - [Gemma3-4b-it Output](#gemma_output)
    - [LoRA Output](#lora_output)


## Usage

---


### 1. Clone the repository
```bash
git clone https://github.com/HusamettinYilmazz/OCR_Turkish_Legal_Documents.git
```

### 2. Create conda environment
```bash
conda create -n ocr_vlm python=3.11; 
conda activate ocr_vlm
```

### 3. Install the required dependencies
```bash
pip install -r requirements.txt
```

### 4.Download the model checkpoint
#### Install huggingface_hub
```bash
pip install huggingface_hub
```
#### Download from huggingface
```python
from huggingface_hub import snapshot_download

checkpoint_hash = "918bf033daf5fc32bafa707a168d05b84daf3922"

path = snapshot_download(
        repo_id="husammm/V3",
        revision=checkpoint_hash,
        allow_patterns="last-checkpoint/*",
        local_dir=f"./loaded_checkpoints/{checkpoint_num}",
        local_dir_use_symlinks=False
        )
print(f"Local repo path: {path}")
```

## Example Outputs