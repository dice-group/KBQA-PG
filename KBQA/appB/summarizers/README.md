# Summarizers

This directory contains all summarizers, which can be used to extract a subgraph from DBpedia based on a natural language question. All summarizers extend the class [BaseSummarizer](base_summarizer/base_summarizer.py). Therefore, they follow the same schema: First a summarizer is instantiated and all parameters are set in the constructor, then the function _summarize_ can be used to collect the triples representing the extracted subgraph. The triples are always returned in a list with the format "<subject> <predicate> <object>". All summarizers can be imported from this directory (KBQA/appB/summarizers). Note that the function _summarize_ requires a _Question_ object as parameter, which can be imported from **KBQA/appB/data_generator**. An overview of the summarizers is given below.

### BaseSummarizer

This summarizer provides the superclass for the summarizers. All summarizers extend from this class and override the _summarize_ method. For more information, see [./base_summarizer](base_summarizer/README.md).

### NES

This summarizer uses named entity recognition for extracting named entities from a given natural language question and returning a subgraph with all outgoing and ingoing edges for these entities. For more information, see [./nes_summarizer](nes_summarizer/README.md).

### FromAnswerSummarizer

This summarizer generates triples by extracting them from a SPARQL-query. For more information, see [./from_answer_summarizer](from_answer_summarizer/README.md).

### GoldSummarizer

This summarizer always returns the exact triples, which answers a natural language question. For more information, see [./gold_summarizer](gold_summarizer/README.md).

### LaurenSummarizer

This summarizer provides a wrapper for the state-of-the-art summarizer [LAUREN](https://ieeexplore.ieee.org/document/9364610) and returns the triples, which are also returned by the LAUREN-endpoint. For more information, see [./lauren_summarizer](lauren_summarizer/README.md).

### OneHopRankSummarizer

This summarizer combines two appraoches: In the first approach named entities and relations from a natural language question are linked using [FALCON 2.0](https://labs.tib.eu/falcon/falcon2/api-use) and all existing triples, which can be found with any combination, are returned. The second approach uses a supervised setting, where predicates are ranked based on a dataset and linked with DBpedia (see [here](/../../ranking/README.md). For more information, see [./one_hop_rank_summarizer](one_hop_rank_summarizer/README.md).
