# NES

This library provides the summarizer NES. NES recognizes and links entities in a given question using
[DBpedia Spotlight](https://www.dbpedia-spotlight.org/). Then it extracts all adjacent triples of the found entities
with respect to the DBpedia Knowledge Graph.

The summarizer NES can be found in [nes_summarizer.py](nes_summarizer.py).

# Installation

To use NES, you can install the libary with

```bash
pip install -e <path to cloned library>/KBQA-PG
```

and

```bash
pip install -r requirements.txt
```

To use it seperately, use

```bash
python <path_to_this_directory>/setup.py install
```
