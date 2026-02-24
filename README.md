<h1 align="center">Beyond OCR: Finetuning VLM for Turkish Legal Documents</h1>

<p align="center">
  Sometimes we resort to Vision-Language Models (VLMs) to perform OCR on documents. If we are already using a VLM, we can benefit from its capabilities to extract more than just plain text. Instead of limiting the output to OCR, the model can also extract structured information such as stamps, person names, and the structural elements of the page like tables and lists.
</p>

## Table of Contents
1. [Usage](#usage)
    - [Clone the Repository](#1-clone-the-repository)
    - [Install Dependencies](#2-install-the-required-dependencies)
    - [Download Model Checkpoint](#3-download-the-model-checkpoint)

3. [Example Outputs](#example-outputs)
4. [Dataset](#dataset)
5. [Training](#training)
6. [Evaluation](#evaluation) 
    - [Gemma3-4b-it Output](#gemma_output)
    - [LoRA Output](#lora_output)
