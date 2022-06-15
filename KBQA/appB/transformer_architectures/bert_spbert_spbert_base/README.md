# BERT-SPBERT-SPBERT-Base
This model should be used ase initial point for other models. Copy it and feel free to do whatever you want with it. Do
not change this version.

This model consists of an encoder BERT model for questions, an encoder SPBERT model for triples. The output tokens of 
both models are concatenated and fed into the decoder. The decoder is another SPBERT instance.
## Installation

Install pytorch from `https://pytorch.org/`.

Install python packages with
```
pip install -r requirements.txt
```
