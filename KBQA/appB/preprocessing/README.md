# Preprocessing Package
- `basic_preprocessing.py` includes an overhauled version of the SPARQL preprocessor.
This version tries to reduce the number of tokens after tokenization.
It is neccessary to include the `sparql_vocabulary.txt` into the tokenizer make use of it properly.
- `labeling_preprocessor.py` adds in addition to the functionality of `basic_preprocessing.py` an encoding of
prefixed URIs where it is encoded by the prefix and the label of the URI.
This should make the encoding more natural while it is not expected to increase the amount of tokens needed.

## Installation
Install python packages with
```
pip install -r requirements.txt
```
