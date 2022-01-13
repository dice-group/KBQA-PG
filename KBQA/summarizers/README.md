# Summarizers

In this directory you can find our summarizers.

## OneHopRankSummarizer

The OneHopRankSummarizer combines two approaches for extracting a subgraph from DBpedia. Given a natural language question, this summarizer tries to recognize entities from DBpedia, which are used as root nodes for the summarized subgraphs. The first approach tries to recognize relations from DBpedia additionaly, which are then used for creating triples containing the entities and relations. This way, for each recognized entity a subgraph with outgoing (regular) and ingoing (inverse) edges of length 1 is extracted (one hop from an entity). In the second approach relations from a given dataset are extracted and ranked by their occurrence. In the next step triples based on these relations and the recognized entities are created. This way, for each recognized entity a subgraph containing triples, whose predicates occur in the dataset at least once, is summarized. The OneHopRankSummarizer just combines all triples found by the two approaches.

### Parameters:

##### datasetset_path

This parameter specifies the dataset to work with. Currently, only datasets of the type "qald" and "lc-quad" are supported.

##### lower_rank

By default, all triples with at least rank 1 are included in the summarized subgraph. This way all triples, whose relation occurs at least once in the dataset, is also added to the subgraph. However, it is possible to choose a higher rank to exclude triples with lower ranks. This might be useful, if there are too many ranked triples.

##### limit

In general it is possible that many triples have the same form, i.e. they differ only in their object or subject. Setting this parameter will restrict the number of triples of the same form by the value. For example, if the parameter is set to 2 and there are summarized triples

- dbr:Germany dbp:leaderName dbr:Angela_Merkel
- dbr:Germany dbp:leaderName dbr:Frank-Walter_Steinmeier
- dbr:Germany dbp:leaderName dbr:Olaf_Scholz

then only two of those triples are actually summarized. It is recommended to set this parameter in order to avoid getting subgraphs, which are too large. The default value is 3.

##### extend_preds

Since DBpedia makes a difference between "ontology" and "property" relations, it might be useful to add the corresponding counterpart to the set of possible relations (ranked and recognized). For example, if there is a relation "dbo:capital", setting this parameter will also add "dbp:capital" to the relation set. By default, this parameter is not set.

### Shortcomings:

This summarizer will only consider triples based on one hop. Since there are some questions, which might require two hops or a more complex SPARQL-query, it is possible that no triples will be found, because relations based on two hops are not supported yet.
