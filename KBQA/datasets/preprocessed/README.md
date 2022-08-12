# Preprocessed Datasets

Here we store the preprocessed datasets. We use different preprocessors which are distinguished through different
folders explained in [Content](#content).

## Content

### basic_preprocessor

qtq-datasets preprocessed with the [basic_preprocessor](../../appB/preprocessing/basic_preprocessor/README.md) which is
used for [SPBERT2](../../appB/transformer_architectures/bert_spbert2_spbert2/README.md).

### labeling_preprocessor

qtq-datasets preprocessed with the [labeling_preprocessor](../../appB/preprocessing/labeling_preprocessor/README.md)
which is used for [SPBERT-LE](../../appB/transformer_architectures/bert_spbert-le_spbert-le/README.md).

### spbert_preprocessor

qtq-datasets preprocessed with the preprocessor included in the original [SPBERT](https://arxiv.org/abs/2106.09997)
library.

This preprocessor can be found in
[KBQA-PG/KBQA/appB/transformer_architectures/bert_spbert](../../appB/transformer_architectures/bert_spbert) and in
[KBQA-PG/KBQA/appB/transformer_architectures/bert_spbert](../../appB/transformer_architectures/bert_spbert_spbert).

Respectively, how to use them is explained
[here](../../appB/transformer_architectures/bert_spbert/README.md#preprocessing)
and
[here](../../appB/transformer_architectures/bert_spbert_spbert/README.md#preprocessing).
