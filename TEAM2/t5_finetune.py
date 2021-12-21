#import necessary modules and libraries
from tqdm import tqdm
import numpy as np
from transformers import AutoTokenizer
from bert_score import BERTScorer
from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_dataset, load_metric
from transformers import pipeline




def preprocess_function(examples):
    '''
    Preprocesses the input data for Transformer model
    
    Input : raw input text
    Output : tokenized data for model

    '''
    inputs = []
    targets = []
    for srcs  in examples[source_lang]:
        inputs.append(srcs)
    for trgs in examples[target_lang]:
        targets.append(trgs)
    model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True)

    # Setup the tokenizer for targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=max_target_length, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def postprocess_text(preds, labels):
    '''
    post processing of predictions and labels for evaluation and compute metrics
    '''
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]
    return preds, labels



def compute_metrics(eval_preds):
    '''
    computes evaluation metrics for predictions of Model based on BERTScorer model
    '''
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Some simple post-processing
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

    P, R, F1 = scorer.score(decoded_preds, decoded_labels)
    result = metric.compute(predictions=decoded_preds, references=decoded_labels)
    
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    gen_len = np.mean(prediction_lens)
    
    return {"gen_len":gen_len, 'BERTScorer-P':P.mean(), 'BERTScorer-R':R.mean(), 'BERTScorer-F1':F1.mean(), "sacrebleu-score": result["score"]} 




model_checkpoint = 't5-base'
data_files = {'train':'train_data.csv', 'test':'test_data.csv'}
fp16 = True
model_name = f't5-base-2'
model_path = 'models/'+ model_name
max_input_length = 0 
max_target_length = 0
batch_size = 8

#initialize tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint).to("cuda")

#source and target formats for model
source_lang = 'question'
target_lang = 'query'

#preparation of data
dataset = load_dataset('csv', data_files = data_files )
tokenized_datasets = dataset.map(preprocess_function, batched=True)
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

#setup evaluation metrics based on BERTScorer
scorer = BERTScorer(lang="en", rescale_with_baseline=True)
metric = load_metric("sacrebleu")


#determine max input and target length 
for d in tqdm(dataset['train']):
    len_en = len(d['question'])
    len_qry = len(d['query'])
    if len_en > max_input_length: max_input_length=len_en
    if len_qry > max_target_length: max_target_length=len_qry

#hyperparameters arguments for model trainer
args = Seq2SeqTrainingArguments(
    model_name,
    evaluation_strategy = "epoch",
    learning_rate=3e-4,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=1,
    predict_with_generate=True,
    fp16=fp16
)

#initialize trainer for model to train
trainer = Seq2SeqTrainer(
    model,
    args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

#start training
trainer.train()

#save trained model on desired path
trainer.save_model(model_path)

#translation pipeline for prediction of fine tuned model
translator = pipeline(
    "translation_xx_to_yy",
    model=model,
    tokenizer=tokenizer,
    device=0 #0 for cuda, -1 for cpu
)


#text to sparql traanslation example
translate= lambda q: (translator(q, max_length=100)[0]['translation_text'])
translate('Who wrote the alchemist')