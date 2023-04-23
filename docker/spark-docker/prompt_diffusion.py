import torch
from diffusers import DiffusionPipeline
from transformers import AutoTokenizer, AutoModelForCausalLM

# Openjourney
pipeline = DiffusionPipeline.from_pretrained('.models/prompthero-openjourney', local_files_only=True)

# MS Promptist
prompter_model = AutoModelForCausalLM.from_pretrained(".models/ms-promptist")
prompter_tokenizer = AutoTokenizer.from_pretrained(".models/gpt2")
prompter_tokenizer.pad_token = prompter_tokenizer.eos_token
prompter_tokenizer.padding_side = "left"

device = 'cuda'
if torch.backends.mps.is_available():
	device = 'mps'

def generate_img(content):
    prompt = generate_prompt(content)
    pipeline = pipeline.to(device)
    image = pipeline(prompt, guidance_scale=9, num_inference_steps=25).images[0]
    return image

def generate_prompt(plain_text):
    prompter_tokenizer.to(device)
    prompter_model.to(device)
    
    input_ids = prompter_tokenizer(plain_text.strip()+" Rephrase:", return_tensors="pt").input_ids
    eos_id = prompter_tokenizer.eos_token_id
    outputs = prompter_model.generate(input_ids, do_sample=False, max_new_tokens=75, num_beams=8, num_return_sequences=8, eos_token_id=eos_id, pad_token_id=eos_id, length_penalty=-1.0)
    output_texts = prompter_tokenizer.batch_decode(outputs, skip_special_tokens=True)
    res = output_texts[0].replace(plain_text+" Rephrase:", "").strip()
    return res