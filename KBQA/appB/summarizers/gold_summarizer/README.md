# GoldSummarizer

The GoldSummarizer returns the exact triples, which answer a natural language question. The summarizer extracts the triples from a prepared dataset. Currently, questions from _qald8_ and _qald9_ can be answered. If the question does not exist, an empty list is returned.

## Usage

A simple example for a question from _qald8_ is shown below:

```python
>>> from KBQA.appB.data_generator import Question
>>> from KBQA.appB.summarizers import GoldSummarizer
>>>
>>> gold_smr = GoldSummarizer(dataset="qald8")
>>> triples = gold_smr.summarize(Question("What is the alma mater of the chancellor of Germany Angela Merkel?"))
["<http://dbpedia.org/resource/Angela_Merkel> <http://dbpedia.org/ontology/almaMater> <http://dbpedia.org/resource/German_Academy_of_Sciences_at_Berlin>",
"<http://dbpedia.org/resource/Angela_Merkel> <http://dbpedia.org/ontology/almaMater> <http://dbpedia.org/resource/Leipzig_University>"]
```
