from preprocessing import preprocess_qtq_file
from preprocessing import preprocess_sparql
from preprocessing import decode
from preprocessing import preprocess_sparql_file

# preprocess_qtq_file(input_file_path="../../../datasets/qtq-qald-9-train.json",
#                     keep_separated_input_file=True, checkpointing_period=1)

# s = "SELECT DISTINCT ?uri WHERE { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> " \
#     "<http://dbpedia.org/ontology/WorldHeritageSite> . <http://dbpedia.org/ontology/worldHeritageSite> " \
#     "<http://dbpedia.org/ontology/worldHeritageSite> <http://dbpedia.org/ontology/WorldHeritageSite> .{ ?uri " \
#     "<http://dbpedia.org/property/year> '2013'^^xsd:integer " \
#     ". } UNION { ?uri <http://dbpedia.org/property/year> '2014'^^xsd:integer . } } "
# print(s)
# s = preprocess_sparql(s)
# print(s)
# s = decode(s)
# print(s)

# with open("preprocessed_data_files/qtq-qald-9-train-subset.sparql") as file:
#     for i, line in enumerate(file, start=1):
#         print(f"Example {i}: {decode(line)}")

# preprocess_sparql_file(input_file_path="../../../datasets/test.txt", checkpointing_period=1)
