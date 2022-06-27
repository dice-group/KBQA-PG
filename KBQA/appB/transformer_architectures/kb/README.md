# KnowBERT-SPBERT-SPBERT
This model consists of an encoder [KnowBERT](https://arxiv.org/abs/1909.04164) model for natural language questions, an encoder [SPBERT](https://arxiv.org/abs/2106.09997) model for triples. 
The output tokens of both models are concatenated and fed into the decoder. The decoder is another [SPBERT](https://arxiv.org/abs/2106.09997) instance.
The KnowBERT model used is the full KnowBERT-Wiki+Wordnet model.

## Installation

Install python packages with
```
pip install -r requirements.txt
```
Then install NLTK data and spacy models with the following python invocations
```
python -c "import nltk; nltk.download('wordnet')"
python -m spacy download en_core_web_sm
```
Lastly install the KBQA package by executing the following command in the root directory of the KBQA-PG repository
```
pip install -e .
```

## Instantiation

The `Knowbert` model can be instantiated with the class method `.from_pretrained()`. Additionally the KnowbertBatchifier is needed for turning an input
NL-sentence into the model input dictionary.
```
from KBQA.appB.transformer_architectures.kb.knowbert import KnowBert
from KBQA.appB.transformer_architectures.kb.knowbert_utils import KnowBertBatchifier

knowbert_model_path = "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/models/knowbert_wiki_wordnet_model.tar.gz"

encoder = KnowBert.load_pretrained_model()
batcher = KnowBertBatchifier(knowbert_model_path)
```

For instantiating the full sequence-to-sequence model use the `init` function from `run.py`. The `args` are defined in `namespace.py` and for instantiation
the following arguments may be changed:
```
"load_model_checkpoint": "Yes"/"No"
"load_model_path": "/path/to/checkpoint/pytorch_model.bin"
"max_source_length": [1-512], 32 recommended
"max_triples_length": [1-512], 512 recommended
"max_target_length": [1-512], 192 recommended
"no_cuda": True/False # Enable/Disable GPU
"beam_size": [1-10], 10 for training, 2 for prediction
"seed": 42 # random seed
```
Then, get the model, batchifier, sparql tokenizer and the selected device by
```
from KBQA.appB.transformer_architectures.kb.namespace import KNOWBERT_SPBERT_SPBERT
from KBQA.appB.transformer_architectures.kb.run import init

model, batcher, tokenizer, device = init(KNOWBERT_SPBERT_SPBERT)
```

## Training
For training the preprocessing of the NL-question, the triples and the SPARQL-query is the same as for [bert-spbert-spbert](https://github.com/dice-group/KBQA-PG/tree/feature/knowbert-clean/KBQA/appB/transformer_architectures/bert_spbert_spbert).
Additionally, the following arguments may be changed for training:
```
"output_dir": "/path/to/output/location"
"train_filename": "/path/to/preprocessed/traindata/folder"
"dev_filename": "/path/to/preprocessed/validation/folder"
"do_eval": True/False # Enable/Disable validation step inbetween training
"train_batch_size": 4 # Depends on available GPU memory
"eval_batch_size": 4
"num_train_epochs": 200
"save_interval": 1 # Only do evaluation step and checkpointing every save_interval steps
```
Then, train the model using the `run` function from `run.py`.
```
from KBQA.appB.transformer_architectures.kb.namespace import KNOWBERT_SPBERT_SPBERT
from KBQA.appB.transformer_architectures.kb.run import train

train(model, batcher, tokenizer, device, BERT_SPBERT_SPBERT)
```

## Prediction
Use the same parameters as for training. The input NL-Question and triples need to be preprocessed beforehand. Set the `"predict_file_name"` accordingly and use
```
from KBQA.appB.transformer_architectures.kb.namespace import KNOWBERT_SPBERT_SPBERT
from KBQA.appB.transformer_architectures.kb.run import predict

predict(model, batcher, tokenizer, device, BERT_SPBERT_SPBERT)
```
The output prediction is then also stored in the `"predict_file_name"` folder.
