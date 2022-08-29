""" A model to retrive Knowledge graph embeddings for given entities from embeddings server."""
import requests
from requests.exceptions import RequestException
import requests
import json
import re
import time
import numpy as np


def append_embeddings(response, embeddingss):
    """ A function append the embeddings from response to embeddingss dict."""
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
    """ A function to process a batch of entites and retive embeddings from embedding server on remote machine."""
    uri_list = batch_entities
    uri_dict = {"entities": uri_list, "relations" :[]}
    r = requests.post("http://kbqa-pg.cs.upb.de/dev/embedding_query/", json=uri_dict)
    append_embeddings(r.json()['entity_embeddings'],embeddingss )
    return

def get_embeddings(uri_list):
    """ 
    Function to  retirve input and convert it to batches of size 50 each.
     When a batch is ready, sends it for embeddings retival.
     
    input_parameter : list of URIs
    returns : emnedding matrix with entities and respective embeddings.
    """
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
