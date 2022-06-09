# Basic Preprocessor
`basic_preprocessing.py` is an overhauled version of the SPARQL preprocessor.
This version reduces the number of tokens after tokenization.
It is neccessary to include the `sparql_vocabulary.txt` into the tokenizer to make use 
of it properly.

## Installation
Install python packages with:
```bash
pip install -r requirements.txt
```

To include new tokens within the vocabulary of e.g. BERT, you can use the `add_tokens` 
function documented in https://huggingface.co/docs/transformers/v4.18.0/en/internal/tokenization_utils#transformers.SpecialTokensMixin.add_tokens.
The code could look like this:
```python
with open("sparql_vocabulary.txt", "r", encoding="utf-8") as file:
    tokens = [line.strip() for line in file]
tokenizer.add_tokens(tokens)
```
Note that the vocabulary of this preprocessor is different from the labeling 
preprocessor.

## Usual Use Cases
- If you have a qtq-dataset, the function `preprocess_qtq_file` will do everything for you.
- If you have a file of SPARQLs where each line corresponds to one example, 
`preprocess_sparql_file` will preprocess it.
- Equivalently for a file consisting of a triple-set in each line and `preprocess_triples_file`.
- To decode an encoded SPARQL e.g. after prediction, use `decode`. To do this
for a file of encoded SPARQLs where each line corresponds to one SPARQL, use `decode_file`.
