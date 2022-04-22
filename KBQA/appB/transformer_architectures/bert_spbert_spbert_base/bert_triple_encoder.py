
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.TransformerEncoder as TransformerEncoder

class ConexEmbedding(nn.Module):
        pass


class SegmentEmbedding(nn.Module):

    def __init__( self, hidden_size):
        super(SegmentEmbedding, self).__init__()
        self.segment_embedding = nn.Embedding(2, hidden_size)

        def forward(self, segments):
            return self.segment_embedding(segments)   #batch_size, seq_len, hidden_size)


class TripleBERT(nn.Module):
    def __init__(self, encoder, conex_embedding, segment_embedding, hidden_size, vocabulary_size):

        super(TripleBERT, self).__init__()

        self.encoder = encoder
        self.conex_embedding = conex_embedding
        self.segment_embedding = segment_embedding
        self.triple_prediction_layer = nn.Linear(hidden_size, vocabulary_size)
        self.classification_layer = nn.Linear(hidden_size, 2)


        def forward(self, inputs):
            sequence, segment = inputs
            triple_embedded = self.conex_embedding(sequbece)
            segment_embedded = self.segment_embedding(segment)
            embedded_sources = triple_embedded + segment_embedded

            mask = pad_masking(sequence)
            encoded_sources = self.encoder(embedded_sources, mask)
            triple_predictions = self.triple_prediction_layer(encoded)
            classification_embedding = encoded_sources[:, 0, :]
            classification_output = self.classification_layer(classification_embedding)
            return token_predictions, classification_output

