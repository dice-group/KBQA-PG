# BERT-SPBERT-SPBERT
This model consists of an encoder BERT model for questions, an encoder SPBERT model for triples. The output tokens of 
both models are concatenated and fed into the decoder. The decoder is another SPBERT instance.

## Installation

Install pytorch from `https://pytorch.org/`.

Install python packages with
```
pip install -r requirements.txt
```

## Preprocessing
The preprocessor of the original SPBERT model is included. `preprocess_qtq.sh` provides a pipeline to preprocess 
datasets in qtq format.
