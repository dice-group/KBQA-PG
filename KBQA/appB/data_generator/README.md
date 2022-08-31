# Data Generator

The data generator can be used to generate QTQ-datasets from qald and lc-quad datasets. The generator implements a mechanism to save the progress, when the process is interrupted. This gives the opportunity to generate a dataset in multiple chunks. This makes the generation easier, especially, if the dataset is large or the summarizer takes some time to find the triples.

## Usage

The generator can be as a command line tool with the following arguments:

- `-d, --dataset`: This argument specifies the name of the qald or lc-quad dataset, from which the QTQ-dataset should be generated.
- `-s, --summarizer`: This argument specifies the name of the summarizer, which is used to generate the triples for the QTQ-datasets. The supported summarizers are `[FromAnswerSummarizer, GoldSummarizer, LaurenSummarizer, NES, OneHopRankSummarizer]`
- `-o, --output`: This argument specifies the name of the output file (i.e. the QTQ-dataset).

The generated QTQ-dataset will be stored in `KBQA/datasets/<output>`.
