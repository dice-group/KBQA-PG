# BERT-SPBERT-SPBERT
This model consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder [SPBERT](https://arxiv.org/abs/2106.09997) model for triples. The output tokens of 
both models are concatenated and fed into the decoder. The decoder is another [SPBERT](https://arxiv.org/abs/2106.09997) instance.

## Installation

Install pytorch from `https://pytorch.org/`.

Install python packages with
```
pip install -r requirements.txt
```

## Preprocessing
`preprocess_qtq.sh` provides a pipeline to preprocess datasets in qtq format. This is the original preprocessing of the 
[SPBERT](https://arxiv.org/abs/2106.09997) paper.


```
bash preprocess_qtq.sh <qtq-dataset-name>.json
```
with the qtq-dataset located in `./data/input/` as `<qtq-dataset-name>.json`
preprocesses the dataset.

The preprocessed data is located in `./data/output` as `<qtq-dataset-name>.en`, `<qtq-dataset-name>.triple`, 
`<qtq-dataset-name>.sparql`. The path `/data/output/<qtq-dataset-name>` without the suffix will be used for model 
usage.

## Model Usage
Within `/example_commandline_invocations` you see examples on how to train, test and predict with the model. For further
information on the arguments we reffer the the code in `/run.py`. We will explain the training example here. Hints on
the prediction example are following afterwards.

#### Training

Given the following example commandline invocation.
```
python run.py 
--do_train 
--do_eval 
--model_type bert 
--encoder_model_name_or_path bert-base-cased 
--decoder_model_name_or_path "razent/spbert-mlm-wso-base" 
--train_filename ./data/qald-8/preprocessed/train/qtq-qald-8-train 
--dev_filename ./data/qald-8/preprocessed/val/qtq-qald-8-val 
--max_source_length 32  
--max_triples_length 512 
--max_target_length 192 
--train_batch_size 22 
--eval_batch_size 22 
--num_train_epochs 200 
--learning_rate 5e-5 
--weight_decay 0.01 
--beam_size 10 
--save_inverval 1  
--load_bleu_file No 
--load_model_checkpoint No 
--warmup_epochs 10
```
`--do_train` indicates that we want to train.

`--do_eval` indicates that we also want to evaluate BLEU scores in between training.

`--model_type bert` indicates that we work on bert models. There is the option to use roberta models, but this was not
tested yet.

`--encoder_model_name_or_path bert_base-cased` defines the model which is loaded as encoder. It is taken from 
Huggingface. You can use local paths also.

`--decoder_model_name_or_path "razent/spbert-mlm-wso-base" ` defines the model which is loaded for decoding AND in our
model for encoding triples. It is loaded from Huggingface. `razent/spbert-mlm-wso-base` is the pretrained [SPBERT](https://arxiv.org/abs/2106.09997) model.
You can use local paths also.

`--train_filename ./data/qald-8/preprocessed/train/qtq-qald-8-train ` defines the location of the training data. Only 
the name without suffix is taken. The suffixes `.en`, `.triple`, `.sparql` are appended implicitly.

`--dev_filename ./data/qald-8/preprocessed/val/qtq-qald-8-val` defines the location of the validation data to calculate
the intermediate BLEU scores. Only the name without suffix is taken. The suffixes `.en`, `.triple`, `.sparql` are 
appended implicitly.

`--max_source_length 32` defines the number of tokens put into the encoder. 32 was sufficient for basic qald-dataset 
questions.

`--max_triples_length 512 ` defines the number of triple-encoder tokens. 512 is the maximum length of our loaded [BERT](https://arxiv.org/abs/1810.04805) 
model.

`--max_target_length 192 ` defines the number of tokens output from the decoder. 192 is sufficient for qald-dataset 
sparql lengths.

`--train_batch_size 22` defines the batch size. 22 is the maximum for 2 x 25 GB GPUs. Note, that training is distributed on 
all available GPUs automatically if not specified otherwise.

`--eval_batch_size 22` the batch size of validation for the BLEU score.

`--num_train_epochs 200` the number of training epochs on the same dataset. BLEU scores have shown, that we not see any
better BLEU scores with more than 200 epochs. The model is taking the best BLEU score epoch automatically.

`--learning_rate 5e-5` 
`--weight_decay 0.01` are self-explanatory.

`--beam_size 10` for evaluation, a BEAM search is used. This is the size of it.

`--save_inverval 1` defines after how many training epochs the model is stored.

`--load_bleu_file No` Yes, if you are resuming a previous run and want the BLEU scores to be appended in the BLEU score
file.

`--load_model_checkpoint No ` Yes, if you are resuming a previous run and want an old model to be loaded.

`--warmup_epochs 10` defines the number of initial epochs before validation of the model is used also.

The model will default to your GPU if you have one. To disable this, you can use `--no_cuda` additionally.

The trained model will be stored as `/output/checkpoint-best-bleu/pytorch_model.bin` by default. To specify another 
output location, add `--output_dir` to the argument list with some path.

#### Prediction

Prediction does not vary much. In the example, you see the following additional arguments:

`--do_predict` which enables prediction.

`--load_model_checkpoint Yes` enables loading of a trained model.

`--load_model_path ./output/checkpoint-best-bleu/pytorch_model.bin` defines the location of the trained model.

`--predict_filename` defines a path to the dataset which predictions should be made on.

The default location of the prediction is `/output`. It can be changed with the 
`--output_dir` argument. The prediction file is `predict_0.output`.

## Postprocessing
The model predicts encoded SPARQLs. To decode a SPARQL, use the `decode` function in 
`generator_utils.py`.

## Note
This model and code is a changed version of the original [SPBERT](https://arxiv.org/abs/2106.09997) model and code.
