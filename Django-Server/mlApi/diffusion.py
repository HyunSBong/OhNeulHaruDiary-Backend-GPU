import os
import datetime

# ML
import torch
from diffusers import DiffusionPipeline

# S3
import boto3

## env
from django.conf import settings

def generate_one(prompt):
    pipe = DiffusionPipeline.from_pretrained(f"{os.getcwd()}/mlAPi/weights/stable-diffusion-v1-5", local_files_only=True)
    pipe = pipe.to("mps")
    pipe.enable_attention_slicing()
    _ = pipe(prompt, num_inference_steps=1)
    image = pipe(prompt).images[0]

    basename = "image"
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = "_".join([basename, suffix])
    image.save(f"{os.getcwd()}/mlAPi/temp/{filename}.png")

    return filename

def uploadS3(filename):
    AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'AWS_STORAGE_BUCKET_NAME')
    AWS_REGION = getattr(settings, 'AWS_REGION', 'AWS_REGION')
    
    client = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION)

    with open(f'{os.getcwd()}/mlAPi/temp/{filename}.png', 'rb') as data:
        client.upload_file(data.name, AWS_STORAGE_BUCKET_NAME, filename)
    
    url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{filename}"
    
    return url

    