# LaurenSummarizer

The LaurenSummarizer provides a wrapper for the summarizer introduced in the paper "LAUREN - Knowledge Graph Summarization for Question Answering" [1] and returns all triples, which are returned by the endpoint. There is a parameter _limit_, which limits the number of triples by just returning the first _limit_ triples.

## Usage

A simple example for a question from _qald8_ is shown below:

```python
>>> from KBQA.appB.dataset_generator import Question
>>> from KBQA.appB.summarizers import LaurenSummarizer
>>>
>>> lauren_smr = LaurenSummarizer(limit=2)
>>> triples = lauren_smr.summarize(Question("What is the alma mater of Angela Merkel?"))
["<http://dbpedia.org/resource/Angela_Merkel> <http://dbpedia.org/ontology/almaMater> <http://dbpedia.org/resource/Leipzig_University>",
"<http://dbpedia.org/resource/Angela_Merkel> <http://dbpedia.org/ontology/almaMater> <http://dbpedia.org/resource/Leipzig_University>"]
```

# References

[1] Jalota, Rricha, et al. "LAUREN-Knowledge Graph Summarization for Question Answering." 2021 IEEE 15th International Conference on Semantic Computing (ICSC). IEEE, 2021.
