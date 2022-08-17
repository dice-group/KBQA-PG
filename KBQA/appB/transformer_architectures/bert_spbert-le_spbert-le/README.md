# BERT-SPBERT-LE-SPBERT-LE
This model consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder SPBERT-LE model for triples. The output tokens of 
both models are concatenated and fed into the decoder. The decoder is another SPBERT-LE instance.
SPBERT-LE uses the [labeling-preprocessor](../../preprocessing/labeling_preprocessor/README.md) in [`KBQA/appB/preprocessing/labeling_preprocessor`](../../preprocessing/labeling_preprocessor) which we call
label-encoder (LE).

## Installation

Install pytorch from `https://pytorch.org/`.

Install python packages with
```
pip install -r requirements.txt
```

## Preprocessing
Given a qtq-dataset (question-triple-query-dataset) we want to preprocess it. Note that the query part can be empty if 
the intention is to predict. To preprocess the dataset, use `preprocess_qtq_file` in 
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

## Note
This model and code is a changed version of the original [SPBERT](https://arxiv.org/abs/2106.09997) model and code.


