# MULTIHOP SUMMARIZER

This is a first part of summarizer, which summarizes database for the entity and outputs triples in the ranked order.

# Modul Relatedness_triples

This module summarizes the triples based on semantically relatedness. For two DBPedia subgraph G1 and G2 of different entities and for two triples f1 and f2 from the graps we take the labels of predicates and retrieve two sets of hypernyms S1 and S2 from the lexical database WordNet. We compute similarity score of predicates for every pair of triples. Dictionary {Tuple - Relatedness score} or {Triple-Relatedness score} can be returned.

### Functions:

##### graphs_for_the_question(entities).

Entities is list of DBPedia entities. List of graphs will be returned.

##### calclualteRelatenessOfGraphs(graphs)

For the list of graphs computes dictionary (Tuple - Relatedness score) in sorted according score order .

##### dictTripleRelateness(tupleRelatedness)

For dictionary (tuple-relatedness score) dictionary (triple- relatedness score) will be returned.

# Modul Multihope_triples

The module summarizes the triples for entities in the question and uses predicates from QALD8, QALD9 and LCQALD data sets. It uses prepared Pickle objects with the match table predicate or tuple of predicates (if multihop) - rank. It extracts triples from DBPedia, that have predicates from the dataset and rank them according frequency of predicates in the data sets. There is possibility to set number of triples, that are nessesary. If the number of founded triples is less then required it additionaly adds triples with high relatedness score if the question has more than one entity.

### Functions:

To get summarization you need to call only one function.

#### triples_for_predicates_all_datasets.

The function returns final_triples_list of tuples(triple, rank, confidence).

### Parameters.

These parameters you need to set for the summarization.

#### question.

question: str: question string in a natural language.

#### predicate_table.

name of the file with predicates from data sets qald8, qald9, lcquad. Order of the datasets 'qald8', 'qald9' and 'lcquad'. The value has to be in '["qald8_qald9_lcquad", "qald9_qald8_lcquad", "qald8_lcquad_qald9", "qald9_lcquad_qald8", "lcquad_qald8_qald9", "lcquad_qald9_qald8"]'.

#### filtering.

filtering: bool: true if we need only triples, where the literal in English.

#### number_of_triples.

number_of_triples: int: how many triples are needed.

#### confidence.

confidence: float:start confidence score for the entity linker.

# Modul Ranking

If you need precompute table with rank and predicate from another dataset, you can use the function create_table_predicate_rank(dataset: str, lcquad: bool) -> List[Tuple[Tuple, int]]. This function may need some modification since it parses json file and depends from format of json. If you have two datasets you can combine predicates table in one predicate table with the function combine_predicates_without_dublicates(first_dataset: List[Tuple], second_dataset: List[Tuple[Tuple, int]]) -> List[Tuple[Tuple, int]].
