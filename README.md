# Knowledge Base Question Answering

[develop](../../tree/develop) branch:&nbsp;
![Deployment develop](https://github.com/dice-group/KBQA-PG/actions/workflows/deploy.yml/badge.svg?branch=develop)
![Testing develop](https://github.com/dice-group/KBQA-PG/actions/workflows/lint.yml/badge.svg?branch=develop)
![Gerbil develop](<https://img.shields.io/badge/dynamic/xml?color=informational&label=Gerbil%20F1&query=(//tr[1]/td[13]/text()[1])[1]&suffix=%&url=http://kbqa-pg.cs.upb.de/dev/gerbil/&link=http://kbqa-pg.cs.upb.de/dev/gerbil/>)

[master](../../tree/master) branch:&nbsp;
![Deployment master](https://github.com/dice-group/KBQA-PG/actions/workflows/deploy.yml/badge.svg?branch=master)
![Testing master](https://github.com/dice-group/KBQA-PG/actions/workflows/lint.yml/badge.svg?branch=master)
![Gerbil master](<https://img.shields.io/badge/dynamic/xml?color=informational&label=Gerbil%20F1&query=(//tr[1]/td[13]/text()[1])[1]&suffix=%&url=http://kbqa-pg.cs.upb.de/gerbil/&link=http://kbqa-pg.cs.upb.de/gerbil/>)

<!-- [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/dice-group/KBQA-PG/develop.svg)](https://results.pre-commit.ci/latest/github/dice-group/KBQA-PG/develop) -->

Explore our QA system: [kbqa-pg.cs.upb.de](http://kbqa-pg.cs.upb.de/)

# KBQA Library

Within [`./KBQA`](KBQA) you find the library of this project. It is filled with READMEs to guide you through the library and
modules are thooroughly documented. We worked on two different approaches, called App A and [App B](KBQA/appB/README.md).

[App B](KBQA/appB/README.md) enhances [SPBERT](https://arxiv.org/abs/2106.09997) by adding
triples as additional knowledge. The major parts it consists of are the [summarizers](KBQA/appB/summarizers/README.md)
and the [transformer architectures](KBQA/appB/transformer_architectures/README.md). For more information on
[App B](KBQA/appB/README.md), visit [`/KBQA/appB`](KBQA/appB).

To use most of our modules, install the library with e.g.

`pip install -e <path to cloned library>/KBQA-PG`.

Following we will provide examples on how to use our library.

## Examples

### App B: bert-spbert-spbert

This example goes through the steps to use our
[bert-spbert-spbert](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md) model. This model consists of an
encoder [BERT](https://arxiv.org/abs/1810.04805) model for questions, an encoder
[SPBERT](https://arxiv.org/abs/2106.09997) model for triples. The output tokens of
both models are concatenated and fed into the decoder. The decoder is another
[SPBERT](https://arxiv.org/abs/2106.09997) instance.

#### Training

Training this model corresponds to the following steps:

1. qtq-Dataset Generation
2. qtq-Dataset Preprocessing
3. Training the Model

We will go through them in detail next.

#### 1. qtq-Dataset Generation

The preprocessors are designed to parse a qtq-dataset (question-triple-query-dataset). Therefore, the first step is the generation of such a dataset by the [data_generator](KBQA/appB/data_generator/README.md). In the following the steps are shown to generate the qtq-dataset from the dataset [qald-9-train-multilingual](KBQA/datasets/qald-9/updated/) using the [LaurenSummarizer](KBQA/appB/summarizers/lauren_summarizer/README.md):

1. Navigate to the data_generator directory: `cd KBQA/appB/data_generator`
2. Run the command `python generator -d qald-9/updated/updated-qald-9-train-multilingual.json -s LaurenSummarizer --output qtq-updated-qald-9-train-multilingual.json`

The generator will then generate the qtq-dataset and save it to the [datasets](KBQA/datasets/) directory. Note that for `qald-8`, `qald-9` and `lc-quad` all qtq-datasets were already generated and can be found in [this](KBQA/datasets/qtq/) directory.

#### 2. qtq-Dataset Preprocessing

Every model has specific preprocessors for the input data. You find the preprocessor corresponding to each model in the
READMEs of the model you want to use. The input data must have qtq-format.

We want to use
[bert-spbert-spbert](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md) which is located in
[`KBQA/appB/transformer_architectures/bert_spbert_spbert`](KBQA/appB/transformer_architectures/bert_spbert_spbert).
The [README](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md) there explains how to preprocess. First
you have to follow the [installation](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md#installation)
instructions. Then the [preprocessing](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md#preprocessing)
instructions.

#### 3. Training the Model

This step also is explained at the model [README](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md).
Follow the example in the [Model Usage](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md#model-usage)
section. The trained model will be stored as `/output/checkpoint-best-bleu/pytorch_model.bin` by default. This binary
can be given as argument to the prediction phase.

#### Prediction

Prediction with the trained model consists of the following steps:

1. qtq-Dataset Generation
2. qtq-Dataset Preprocessing
3. Prediction with Trained Model
4. Decode Prediction

Step 1 and 2 are the same as in the training example, except you will not see any queries in the qtq-dataset.

Step 3 is explained on the [README](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md) within
[Model Usage](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md#model-usage) again.

For step 4, follow the [Postprocessing](KBQA/appB/transformer_architectures/bert_spbert_spbert/README.md#postprocessing)
part.

### App B: Other Models

All the models in [`KBQA/appB/transformer_architectures`](KBQA/appB/transformer_architectures/README.md) follow similar
schemes as in the [App B: bert-spbert-spbert](#app-b-bert-spbert-spbert) example. The corresponding READMEs should provide you with the information to use the corresponding model.

# Contributing

## Workflow

We use the workflow as described by [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow).

Follow the guidelines for [commit messages](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53).

A properly formed git commit subject line should always be able to complete the following sentence

> If applied, this commit will _\<your subject line here\>_

### Branches

We have two main branches `master` for releases and `develop` for development builds. These branches always contain completed changes and executable, formated code and will be deployed to our server. Therefore, these branches are protected and only reviewed pull requests (PR) can be merged. For every feature/topic a new branch based on develop has to be created. A PR should only contain one topic and can also be opened as a draft to get early feedback. When merging a PR, individual commits can be combined (rebased) if they describe a related change.

<table>
  <thead>
    <tr>
      <th>Instance</th>
      <th>Branch</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Release</td>
      <td>master</td>
      <td>Accepts merges from Develop</td>
    </tr>
    <tr>
      <td>Working</td>
      <td>develop</td>
      <td>Accepts merges from Features/Issues and Hotfixes</td>
    </tr>
    <tr>
      <td>Features/Issues</td>
      <td>feature/*</td>
      <td>A branch for each Feature/Issue</td>
    </tr>
    <tr>
      <td>Hotfix</td>
      <td>hotfix/*</td>
      <td>Always branch off Develop</td>
    </tr>
  </tbody>
</table>

### Folder structure

The top directory contains only configuration files that refer to this repository. Everything else is in the [KBQA](/KBQA) folder:

The end-to-end system that is automatically deployed on the VM is located in the folder [kbqa](/KBQA/kbqa).
Other topics that are not (yet) included in the end-to-end system should have their own folder.

## Code Style

We use the standard style guides.

### Python conventions

For python, this is the [PEP 8](https://www.python.org/dev/peps/pep-0008/).

Type hints ([PEP 484](https://www.python.org/dev/peps/pep-0484/)) should be used whenever possible. Static analysis can then ensure that variables and functions are used correctly.

For documenting the code we use docstrings ([PEP 257](https://www.python.org/dev/peps/pep-0257/)). Every method and class has a docstring describing its function and arguments. We follow the [numpy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html). Using consistent docstrings in the project, we automatically create a code documentation website.

## Setup

### Installation

In order to include modules from different directories, you can install the project as a package. This way the project can be splitted into different subdirectories/subprojects, which can be imported by each other. The installation can be done by running the following command in this directory:

```
pip install -e .
```

After that, you can import all source files starting with the root directory `KBQA`.

### Linters

We use the different linters to apply style rules and point out issues in code. This greatly simplifies code reviews and helps to detect errors early on.

To automatically run the linters on every commit, we use [pre-commit](https://pre-commit.com/). To setup pre-commit once run the following commands:

```
pip install pre-commit
pre-commit install
```

Now on every commit the linters defined in [pre-commit config](.pre-commit-config.yaml) will run automatically.

If you are in a hurry, you can skip the linting with `git commit --no-verify`.
But to merge into the develop branch the pipeline has to pass.

### Exclude external code files

The linters should not be applied to external code files (libraries), configs, and non-code folders as they do not have to meet our coding conventions. Therefore, these files or folders have to be excluded from the linting process. This can be done in the [pre-commit config](.pre-commit-config.yaml) by adding the files or folders to the exclude option, which is a regular expression.
Example: `exclude: ^documentation/`

### Recommended VS Code Extensions

#### Python Docstring Generator

Quickly generate docstrings for python functions in the right format by typing triple quotes.
