# App B

This folder comprises the major part of App B. App B enhances [SPBERT](https://arxiv.org/abs/2106.09997) by adding
triples as additional knowledge. An overview of the different approaches is found within
[./transformer_architectures](transformer_architectures/README.md).

## Content of this Package

### ./data_generator

Given a summarizer, this package provides utils to generate so called qtq-files (question-triple-query-files). These
are used as input for all the models. For more information, see [./data_generator](data_generator/README.md).

### ./preprocessing

The transformer-architectures SPBERT2 and SPBERT-LE are based on newly written preprocessors. For more information, see
[./preprocessing](preprocessing/README.md).

### ./summarizers

Given a question, summarizers generate triples from a knowledge base. We developed some of such summarizers.
For more information, see [./summarizers](summarizers/README.md).

### ./transformer_architectures

We developed differen models for App B. For more information, see
[./transformer_architectures](transformer_architectures/README.md).
