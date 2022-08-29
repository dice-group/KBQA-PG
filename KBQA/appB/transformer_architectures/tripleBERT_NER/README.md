# BERTforEntityConcat
This module modfies the standard BERT model (bert-base-uncased) and concats the entity embeddings of known entity present in the question with the BERT model for the prediction of SPARQL queries based on input question and known *named-entity* in the question.
This module is based on *Enriching BERT with Knowledge Graph Embedding for Document Classification* (https://arxiv.org/abs/1909.08402). 

## Entity Annotations  and Embeddings
The entity present in the natural language questions are annotated with DBpedia Spotlight. The embeddings for the identifed entites are then retrived from embedding server hosted on the Project Group VM.
The embeddings along with entites are stored in `entity2vec` file.

## Models
The BERTforEntityConcat model is defined with two different frameworks. One is based on the HuggingFace (https://huggingface.co/) implementation of BERT and another is a basic implementation of BERT model in pytorch.

## Training 
The script for training is in `train.py` file. To start the training, just run : 
```
python train.py
```

### The module is not complete. 