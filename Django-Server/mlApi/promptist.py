from django.conf import settings

import os
import sys
import json
import urllib.request

# google
import googletrans

# ML
from transformers import AutoModelForCausalLM, AutoTokenizer

NCP_CLIENT_ID = getattr(settings, 'NCP_CLIENT_ID', 'NCP_CLIENT_ID')
NCP_CLIENT_KEY = getattr(settings, 'NCP_CLIENT_KEY', 'NCP_CLIENT_KEY')

def translator(original):
    #### translate korean to english
    translator = googletrans.Translator()
    outStr = translator.translate(original, dest = 'en', src = 'auto')
    
    return outStr.text

def translator_naver(original):
    encText = urllib.parse.quote(original)
    data = "source=ko&target=en&text=" + encText
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", NCP_CLIENT_ID)
    request.add_header("X-NCP-APIGW-API-KEY", NCP_CLIENT_KEY)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        response_json = json.loads(response_body.decode('utf-8'))

        translatedText = response_json['message']['result']['translatedText']
        return translatedText
    else:
        print("Error Code:" + rescode)


def load_prompter():
    prompter_model = AutoModelForCausalLM.from_pretrained(f"{os.getcwd()}/mlAPi/weights/ms-promptist/", local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(f"{os.getcwd()}/mlAPi/weights/gpt2/", local_files_only=True)

    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    return prompter_model, tokenizer

def generate(plain_text, prompter_model, prompter_tokenizer):
    input_ids = prompter_tokenizer(plain_text.strip()+" Rephrase:", return_tensors="pt").input_ids
    eos_id = prompter_tokenizer.eos_token_id
    outputs = prompter_model.generate(input_ids, do_sample=False, max_new_tokens=75, num_beams=8, num_return_sequences=8, eos_token_id=eos_id, pad_token_id=eos_id, length_penalty=-1.0)
    output_texts = prompter_tokenizer.batch_decode(outputs, skip_special_tokens=True)
    res = output_texts[0].replace(plain_text+" Rephrase:", "").strip()

    return res

def promptist_manual(summarize_text): # 여기로 요약 데이터가 들어감.
    #translated = translator(summarize_text)
    translated = translator_naver(summarize_text)
    # prompt = translated + ", Pixar colored lineart in the style of WLOP and Atey Ghailan"
    prompt = translated + ", very realistic, highly detailed, digital painting, concept art, illustration, in (modern Disney style), 4k"

    return prompt

def promptist(summarize_text): # 여기로 요약 데이터가 들어감.
    prompter_model, prompter_tokenizer = load_prompter()
    prompt = generate(translator(summarize_text), prompter_model, prompter_tokenizer)

    return prompt
