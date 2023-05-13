import torch
from transformers import AutoTokenizer, AutoModel
from transformers import PreTrainedTokenizerFast, BartModel
from transformers import BartForConditionalGeneration

def inference_diary(text):
    # text = "오늘은 ~~~~~재밌는 하루였다"
    tokenizer = AutoTokenizer.from_pretrained("./weights/kobart-summ/", local_files_only=True)
    model = BartForConditionalGeneration.from_pretrained("./weights/kobart-summ/", local_files_only=True)

    text = text.replace('\n', ' ')
    raw_input_ids = tokenizer.encode(text)
    input_ids = [tokenizer.bos_token_id] + raw_input_ids + [tokenizer.eos_token_id]

    summary_ids = model.generate(torch.tensor([input_ids]),  num_beams=4,  max_length=512,  eos_token_id=1)
    result = tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

    return result

def inference_dialogue(dialogue):
    # dialogue = [
    #     "얌 너도 시간 되면 올래?", 
    #     "오 그래?? 좋지 좋지", 
    #     "되게 만들어야지", 
    # ]
    max_length = 64
    num_beams = 5
    length_penalty = 1.2

    tokenizer = AutoTokenizer.from_pretrained("../weights/alaggung-bart-r3f/")
    model = BartForConditionalGeneration.from_pretrained("../weights/alaggung-bart-r3f/")

    inputs = tokenizer("[BOS]" + "[SEP]".join(dialogue) + "[EOS]", return_tensors="pt")
    outputs = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask,
        num_beams=num_beams,
        length_penalty=length_penalty,
        max_length=max_length,
        use_cache=True,
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


