import torch
from transformers import PreTrainedTokenizerFast, BartModel
from transformers import BartForConditionalGeneration

# BART
bart_tokenizer = PreTrainedTokenizerFast.from_pretrained('.models/kobart-base-v2')
bart_model = BartModel.from_pretrained('.models/kobart-base-v2')

# BART + summarization
bart_summ_tokenizer = PreTrainedTokenizerFast.from_pretrained('.models/kobart-summarization')
bart_summ_model = BartForConditionalGeneration.from_pretrained('.models/kobart-summarization')

def tokenize(content):
    tokenized = kobart_tokenizer(content)
    tokenized_pt = kobart_tokenizer(content, return_tensors='pt')
    return tokenized

def summarize(content):
    content = content.replace('\n', ' ')
    raw_input_ids = bart_summ_tokenizer.encode(content)
    input_ids = [bart_summ_tokenizer.bos_token_id] + raw_input_ids + [bart_summ_tokenizer.eos_token_id]
    summary_ids = bart_summ_model.generate(torch.tensor([input_ids]),  num_beams=4,  max_length=512,  eos_token_id=1)
    return bart_summ_tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)