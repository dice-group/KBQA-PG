# BERT-TRIPLEBERT-SPBERT
This model is derived from the base model 'bert_spbert_spbert'. This model consists of two encoders: one encoder [BERT](https://arxiv.org/abs/1810.04805) to prcocess natural language questions and another encoder 'tripleBERT' which is modified version of BERT base model and is fine-tuned with triples.

The output from both of these models is concatenated and feed into the decoder, which is a [SPBERT](https://arxiv.org/abs/2106.09997)  model.

## Installation

Install pytorch from `https://pytorch.org/`.

Install python packages with

```
pip install -r requirements.txt
```

## Preprocessing
The dataset needs to be preprocessed before it can be used for training or testing purposes. The data is stored in tne sub-directory ['/data/..']. The input data should be splited into three formats : .en for questions, .triple for triples and .sparql for files with sparql queries from the qtq files that have 'question-triple-queries' combined on a single file.
To preprocess the dataset, use `preprocess_qtq_file` in 
[`KBQA/appB/preprocessing/labeling_preprocessor/labeling_preprocessor.py`](../../preprocessing/labeling_preprocessor/labeling_preprocessor.py).

## Model Usage

### Training
To train the model, feed the preprocessed dataset into it. This is done with e.g. the commandline invocation in 
[`/example_commandline_invocations/train.txt`](example_commandline_invocations/train.txt). Explanations on the 
arguments are found within the code of [run.py](run.py) or the 
[Model Usage](../bert_spbert_spbert/README.md#model-usage) section of 
[bert-spbert-spbert](../bert_spbert_spbert/README.md).

The trained model will be stored as `/output/checkpoint-best-bleu/pytorch_model.bin` by default.

### Prediction
To predict with a trained model, feed the preprocessed dataset into it. This is done with e.g. the commandline 
invocation in 
[`/example_commandline_invocations/predict.txt`](example_commandline_invocations/predict.txt). Explanations on the 
arguments are found within the code of [run.py](run.py) or the 
[Model Usage](../bert_spbert_spbert/README.md#model-usage) section of 
[bert-spbert-spbert](../bert_spbert_spbert/README.md).

The default location of the prediction is `/output`. It can be changed with the 
`--output_dir` argument. The prediction file is `predict_0.output`.

## Postprocessing
The model predicts encoded SPARQLs. To decode a SPARQL, use the `decode_file` or `decode` function in 
[KBQA/appB/preprocessing/labeling_preprocessor/labeling_preprocessor.py](../../preprocessing/labeling_preprocessor/labeling_preprocessor.py).

## SPARQL Vocabulary
The training model can also be provided with special words or tokens used in SPARQL queries. The tokens are present in ['/sparql_vocabulary.txt'] and can be passed to the model as path with training argument '--sparql-vocab'.


