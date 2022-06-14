import requests
from rdflib import URIRef
import pickle
webserver_address = "https://api.dbpedia-spotlight.org/en/annotate"
confidence = 0.5
from get_embeddings import get_embeddings
questions_list = []
with open('qtq-updated-qald-8-9-merged-train-multilingual.en', 'r',encoding = 'utf-8') as file:
    for line in file:
        questions_list.append(line[:-1])

named_entities = []
not_avilable = []
for count, question in enumerate(questions_list):
    response = requests.post(
        webserver_address,
        data={"text": question, "confidence": confidence},
        headers={"Accept": "application/json"},
    ).json()
    try :
        for resource in response["Resources"]:
            named_entities.append(resource["@URI"])
            break
    except:
        not_avilable.append(count)
entity2vec = get_embeddings(named_entities)

new_ques = []
for cnt, ques in enumerate(questions_list):
    if cnt not in not_avilable:
        new_ques.append(ques)

triples_list = []
with open('qtq-updated-qald-8-9-merged-train-multilingual.triple', 'r',encoding = 'utf-8') as tfile:
    for line in tfile:
        triples_list.append(line[:-1])


sparql_list = []
with open('qtq-updated-qald-8-9-merged-train-multilingual.sparql', 'r',encoding = 'utf-8') as sfile:
    for line in sfile:
        sparql_list.append(line[:-1])     

new_triples = []
for cnt, triples in enumerate(triples_list):
    if cnt not in not_avilable:
        new_triples.append(triples)

new_sparqls = []
for cnt, sparql in enumerate(sparql_list):
    if cnt not in not_avilable:
        new_sparqls.append(sparql)       

with open('train_data/qtq-updated-qald-8-9-merged-train-multilingual.en', 'w') as outfile:
    outfile.write("\n".join(str(item) for item in new_ques))

with open('train_data/qtq-updated-qald-8-9-merged-train-multilingual.sparql', 'w') as outfile:
    outfile.write("\n".join(str(item) for item in new_sparqls))

with open('train_data/qtq-updated-qald-8-9-merged-train-multilingual.triples', 'w') as outfile:
    outfile.write("\n".join(str(item) for item in new_triples))

with open('train_data/qtq-updated-qald-8-9-merged-train-multilingual.ner', 'w') as outfile:
    outfile.write("\n".join(str(item) for item in named_entities))

with open('train_data/entity2vec.pickle', 'wb') as handle:
    pickle.dump(entity2vec, handle, protocol=pickle.HIGHEST_PROTOCOL)

