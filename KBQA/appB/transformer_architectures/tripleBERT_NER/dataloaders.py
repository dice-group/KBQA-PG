""" A module to create dataloader objects for training BERT model with entitiy concatenation."""
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import TensorDataset, RandomSampler, DataLoader
from keras.utils import pad_sequences
from transformers import BertTokenizer
import pickle


def text_to_train_tensors(texts, tokenizer, max_seq_length):
    """ 
    A function to convert input training text into tensors for BERT model.
    
    input_parameters:
    ---------------------------------------------------------
    texts : text in natural language
    tokenizer : tokenizer object to convert text into tokens
    max_seq_length : maximium number of tokens per input line

    returns:
    -------------------------------------------------
    train_tokens_ids : ids for tokens based on tokenizer
    train_mask : ids of the masked tokens
    """
    train_tokens = list(map(lambda t: ['[CLS]'] + tokenizer.tokenize(t)[:max_seq_length - 1], texts))
    train_tokens_ids = list(map(tokenizer.convert_tokens_to_ids, train_tokens))
    train_tokens_ids = pad_sequences(train_tokens_ids, maxlen=max_seq_length, truncating="post", padding="post",
                                     dtype="int")

    train_masks = [[float(i > 0) for i in ii] for ii in train_tokens_ids]

    # to tensors
    # train_tokens_tensor, train_masks_tensor
    return torch.tensor(train_tokens_ids), torch.tensor(train_masks)

def text_to_predict_tensors(texts, tokenizer, max_seq_length):

    """ 
    A function to convert prediction text into tensors for BERT model.
    
    input_parameters:
    ---------------------------------------------------------
    texts : text in natural language
    tokenizer : tokenizer object to convert text into tokens
    max_seq_length : maximium number of tokens per input line

    returns:
    -------------------------------------------------
    train_tokens_ids : ids for tokens based on tokenizer

    """
    train_tokens = list(map(lambda t: ['[CLS]'] + tokenizer.tokenize(t)[:max_seq_length - 1], texts))
    train_tokens_ids = list(map(tokenizer.convert_tokens_to_ids, train_tokens))
    train_tokens_ids = pad_sequences(train_tokens_ids, maxlen=max_seq_length, truncating="post", padding="post",
                                     dtype="int")



    # to tensors
    # train_tokens_tensor, train_masks_tensor
    return torch.tensor(train_tokens_ids)



def to_dataloader(texts, entity_table, ys,
                 tokenizer,
                 max_seq_length,
                 batch_size,
                 dataset_cls=TensorDataset,
                 sampler_cls=RandomSampler):
    """
    Convert raw input into PyTorch dataloader.

    input_parameters:
    -----------------------------------
    texts : text in natural language
    entity_table : table for entities with embeddings
    ys : prediction target text i.e. sparql queries
    max_seq_length : maximium number of tokens per input line
    batch_size : size of input lines to feed into the model at once

    returns: Dataloader object.
    
    """
    #train_y = train_df[labels].values

    # Labels
    train_y_tensor =  text_to_predict_tensors(ys, tokenizer, max_seq_length)

    entity_tensor = torch.tensor(entity_table, dtype = torch.float)
    
    train_tokens_tensor, train_masks_tensor = text_to_train_tensors(texts, tokenizer, max_seq_length)

    train_dataset = dataset_cls(train_tokens_tensor, train_masks_tensor, entity_tensor,  train_y_tensor)

    train_sampler = sampler_cls(train_dataset)
    
    return DataLoader(train_dataset, sampler=train_sampler, batch_size=batch_size)


def get_entity_embeddings(triple_list, entity2vec):
    """
    Build matrix for extra data (i.e. entity embeddings ).

    """
    
    ENTITY_DIM = len(next(iter(entity2vec.values())))
    
    entity_table = np.zeros((len(triple_list),  ENTITY_DIM ))
    entity_found = 0
    
    
    for i, entity in enumerate(triple_list):
            if entity in entity2vec:
                entity_found += 1

                entity_table[i][:ENTITY_DIM] = entity2vec[entity]
                
          
    return entity_table, entity_found



def prepare_data_loaders(MAX_SEQ_LENGTH, batch_size):
    """ A function to prepare input dataloader for training model using dataloader object."""
    batch_size = batch_size
    MAX_SEQ_LENGTH = 512

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    #read input data
    with open('train_data/entity2vec.pickle', 'rb') as f:
        entity2vec = pickle.load(f)
    triple_list = []
    with open('train_data/qtq-updated-qald-8-9-merged-train-multilingual.ner') as triple_file:
        triple_list = triple_file.read().splitlines()
    
    natural_questions = []
    with open('train_data/qtq-updated-qald-8-9-merged-train-multilingual.ner') as question_file:
        natural_questions = question_file.read().splitlines()

    sparql_data = []
    with open('train_data/qtq-updated-qald-8-9-merged-train-multilingual.ner') as sparql_file:
        sparql_data = sparql_file.read().splitlines()

    entity_table, entity_found  = get_entity_embeddings(
        triple_list,
        entity2vec
               
            )

    train_texts = natural_questions
    train_y = sparql_data
    
    #create dataloader for training
    train_dataloader = to_dataloader(train_texts, entity_table, train_y,
                                         tokenizer,
                                         MAX_SEQ_LENGTH,
                                         batch_size,
                                         dataset_cls=TensorDataset,
                                         sampler_cls=RandomSampler)
    return train_dataloader, entity_found
