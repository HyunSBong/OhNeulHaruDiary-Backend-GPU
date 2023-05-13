import torch
from diffusers import StableDiffusionPipeline

def generate_one(prompt):
    model_id = "./weights/prompthero-openjourney"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, local_files_only=True)
    pipe = pipe.to("cuda")
    image = pipe(prompt).images[0]
    
    return image