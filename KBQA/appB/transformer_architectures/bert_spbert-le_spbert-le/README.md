# BERT-SPBERT-LE-SPBERT-LE
This model consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder SPBERT-LE model for triples. The output tokens of 
both models are concatenated and fed into the decoder. The decoder is another SPBERT-LE instance.
SPBERT-LE uses the preprocessor in `KBQA/AppB/preprocessing/labeling_preprocessor` which we call
label-encoder (LE).

## Installation

Install pytorch from `https://pytorch.org/`.

Install python packages with
```
pip install -r requirements.txt
```

## How To Do Predictions
Given a question and corresponding triples, use 
`KBQA/AppB/preprocessing/labeling_preprocessor/labeling_preprocessor/preprocess_natural_language_sentence` to
preprocess the question and
`KBQA/AppB/preprocessing/labeling_preprocessor/labeling_preprocessor/preprocess_triples` to preprocess the triples.

These are fed into BERT-SPBERT-LE-SPBERT-LE with the predict commandline
invocation of your choice (e.g. the one in `example_commandline_invocations/predict.txt`).

After the prediction is made, decode the file which holds the prediction with
`KBQA/AppB/preprocessing/labeling_preprocessor/labeling_preprocessor/decode_file` or the prediction string with
`KBQA/AppB/preprocessing/labeling_preprocessor/labeling_preprocessor/decode`.

## Note
This model is a changed version of the original [SPBERT](https://arxiv.org/abs/2106.09997) model.


