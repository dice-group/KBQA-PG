# tripleBERT
TripleBERT is a modifed version of [BERT](https://arxiv.org/abs/1810.04805). This model is fine tuned with triples,which are summarized DBPedia subgraph for different entities, using MLM (Masked Language Modelling) technique.
TripleBERT acts as triple encoder in 'bert_triplebert_spbert' architecture.

In `bert_LM.py`, the BERT (base) language model is defined, which is adapted from huggingface library
('https://huggingface.co/docs/transformers/model_doc/bert') and the tripleBERT model is defined in `tripleBERT.py`.


## Preprocessing
The model is trained using pre-processed data. To preprocess the dataset, use `preprocess_qtq_file` in 
[`KBQA/appB/preprocessing/labeling_preprocessor/labeling_preprocessor.py`](../../preprocessing/labeling_preprocessor/labeling_preprocessor.py). The .triple file is enough for this implementation.

The preprocessed files should be kept in ['/preprocessed_data_files'] directory.

## Training
To pre-train the model, run 
```
python tripleBERT_MLM_pretrain.py
```
The pre-trained language model will be saved in `/out/` directory.

## SPARQL Vocabulary
The training model can also be provided with special words or tokens used in SPARQL queries. The tokens are present in ['/sparql_vocabulary.txt'] and can be added by setting sparql_vocab = True in the tripleBERT_MLM_pretrain.py file.