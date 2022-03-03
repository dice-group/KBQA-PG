from kb.include_all import ModelArchiveFromParams
from kb.knowbert_utils import KnowBertBatchifier
from allennlp.common import Params

import torch

# a pretrained model, e.g. for Wordnet+Wikipedia
archive_file = 'https://allennlp.s3-us-west-2.amazonaws.com/knowbert/models/knowbert_wiki_wordnet_model.tar.gz'

# load model and batcher
params = Params({"archive_file": archive_file})
model = ModelArchiveFromParams.from_params(params=params)
print('Loaded Model')
batcher = KnowBertBatchifier(archive_file)
print('Loaded Batches')

sentences = ["Paris is located in France.", "KnowBert is a knowledge enhanced BERT"]

# batcher takes raw untokenized sentences
# and yields batches of tensors needed to run KnowBert
for batch in batcher.iter_batches(sentences, verbose=True):
    # model_output['contextual_embeddings'] is (batch_size, seq_len, embed_dim) tensor of top layer activations
    print(type(batch))
    for k in batch:
        print(f"{k}: {batch[k]}")
    model_output = model(**batch)
    print(model_output)