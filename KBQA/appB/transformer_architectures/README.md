# Transformer Architectures

This folder consists of all architectures off App B. Following we see a short overview of them.

### BERT-SPBERT

Located in `/bert_spbert`.

This model is equivalent to the original [SPBERT](https://arxiv.org/abs/2106.09997) model and used as baseline. It consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for
questions. The output tokens of the encoder are fed into the decoder. The decoder is an [SPBERT](https://arxiv.org/abs/2106.09997) instance.

### BERT-SPBERT-SPBERT

Located in `/bert_spbert_spbert`.

This model consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder [SPBERT](https://arxiv.org/abs/2106.09997) model for triples. The output tokens of
both models are concatenated and fed into the decoder. The decoder is another [SPBERT](https://arxiv.org/abs/2106.09997) instance.

### BERT-SPBERT2-SPBERT2

Located in `/bert_spbert2_spbert2`.

This model consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder SPBERT2 model for triples. The output tokens of
both models are concatenated and fed into the decoder. The decoder is another SPBERT2 instance.
SPBERT2 uses the preprocessor in `KBQA/AppB/preprocessing/basic_preprocessor` which is an overhauled version of the
[SPBERT](https://arxiv.org/abs/2106.09997) preprocessor with added vocabulary entries.

### BERT-SPBERT-LE-SPBERT-LE

Located in `/bert_spbert-le_spbert-le`.

This model consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder SPBERT-LE model for triples. The output tokens of
both models are concatenated and fed into the decoder. The decoder is another SPBERT-LE instance.
SPBERT-LE uses the preprocessor in `KBQA/AppB/preprocessing/labeling_preprocessor` which we call
label-encoder (LE).

### BERT-TRIPLE-BERT-SPBERT

Located in `/bert_triplebert_spbert`.

This model consists of an encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder TRIPLE-BERT model for triples. The output tokens
of both models are concatenated and fed into the decoder. The decoder is an [SPBERT](https://arxiv.org/abs/2106.09997) instance.
TRIPLE-BERT is pretrained on triples.

### KnowBERT-SPBERT-SPBERT

Located in `/kb`.

This model consists of an encoder [KnowBERT](https://arxiv.org/abs/1909.04164) model for natural language questions, an encoder [SPBERT](https://arxiv.org/abs/2106.09997) model for triples.
The output tokens of both models are concatenated and fed into the decoder. The decoder is another [SPBERT](https://arxiv.org/abs/2106.09997) instance.
The KnowBERT model used is the full KnowBERT-Wiki+Wordnet model.
