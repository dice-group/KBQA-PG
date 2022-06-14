import requests
from requests.exceptions import RequestException
import requests
import json
import re
import time
import numpy as np


def append_embeddings(response, embeddingss):
    for embeddings_raw in response:
        if (len(embeddings_raw) > 0):
            embeddings_raw = embeddings_raw.split('\t')
            embeddings = ' '.join(ent[:-1] if re.search("\n$", ent) else ent for ent in embeddings_raw)
            
            entity_list = embeddings.split(' ')
            entity = entity_list[0]
            embedding = np.array(entity_list[1:])
            embeddingss[entity] = embedding
           
    return

def process_batch(batch_entities, embeddingss):
    uri_list = batch_entities
    uri_dict = {"entities": uri_list, "relations" :[]}
    r = requests.post("http://kbqa-pg.cs.upb.de/dev/embedding_query/", json=uri_dict)
    append_embeddings(r.json()['entity_embeddings'],embeddingss )
    return

def get_embeddings(uri_list):
    embeddingss = {}
    t_count, count= 0, 0
    current_batch = []
    batch_count = 0
    for line in uri_list:
        count += 1
        t_count += 1
        entity = line
        current_batch.append(entity)
        if count == 50:
            batch_count += 1
            process_batch(current_batch, embeddingss)
            current_batch = []
            time.sleep(1)
            count = 0
    process_batch(current_batch,embeddingss)
    return embeddingss
