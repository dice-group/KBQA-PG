from transformers import AutoTokenizer, pipeline
from transformers import AutoModelForSeq2SeqLM
from app.t5.generator_utils import decode
import torch
import os

#set device and model name
device = torch.device("cuda" if torch.cuda.is_available() else "cpu" )
model_name = 't5-base-en'
model_checkpoint = 'models/'+ model_name

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint).to(device)

def process_question(question):
    translator = pipeline(
        "translation_xx_to_yy",
        model=model,
        tokenizer=tokenizer,
        device= device#0 for cuda, -1 for cpu
    )
    translate= lambda q: (translator(q, max_length=100)[0]['translation_text'])
    sparql = translate(question)
    decoded_sparql = decode(sparql)
    
    return decoded_sparql
