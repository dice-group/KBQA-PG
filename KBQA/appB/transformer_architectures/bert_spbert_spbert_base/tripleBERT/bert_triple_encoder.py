
import torch
import torch.nn as nn
import torch.nn.functional as F 
from transformer import TransformerEncoder 
from preprocess import pad_masking

# class TransformerEncoder(nn.Module):

#     def __init__(self, layers_count, d_model, heads_count, d_ff, dropout_prob):
#         super(TransformerEncoder, self).__init__()

#         self.d_model = d_model
#         self.encoder_layers = nn.ModuleList(
#             [TransformerEncoderLayer(d_model, heads_count, d_ff, dropout_prob) for _ in range(layers_count)]
#         )

#     def forward(self, sources, mask):
#         """Transformer bidirectional encoder
#         args:
#            sources: embedded_sequence, (batch_size, seq_len, embed_size)
#         """
#         for encoder_layer in self.encoder_layers:
#             sources = encoder_layer(sources, mask)

#         return sources



class ConexEmbedding(nn.Module):
    pass


class PositionalEmbedding(nn.Module):

    def __init__(self, max_len, hidden_size, ):
        super(PositionalEmbedding, self).__init__()
        self.positional_embedding = nn.Embedding(max_len, hidden_size)
        positions = torch.arange(0, max_len)
        self.register_buffer('positions', positions)

    def forward(self, sequence):
        batch_size, seq_len = sequence.size()
        positions = self.positions[:seq_len].unsqueeze(0).repeat(batch_size, 1)
        return self.positional_embedding(positions)


class SegmentEmbedding(nn.Module):

    def __init__( self, hidden_size):
        super(SegmentEmbedding, self).__init__()
        self.segment_embedding = nn.Embedding(2, hidden_size)

    def forward(self, segments):
            return self.segment_embedding(segments)   #batch_size, seq_len, hidden_size)


class TripleBERT(nn.Module):
    def __init__(self, encoder, token_embedding,  positional_embedding, segment_embedding, hidden_size, vocabulary_size):

        super(TripleBERT, self).__init__()

        self.encoder = encoder
        self.token_embedding = token_embedding
        self.positional_embedding = positional_embedding
        self.segment_embedding = segment_embedding
        self.token_prediction_layer = nn.Linear(hidden_size, vocabulary_size)
        self.classification_layer = nn.Linear(hidden_size, 2)


    def forward(self, inputs):
        sequence, segment = inputs
        token_embedded = self.token_embedding(sequence)
        positional_embedded = self.positional_embedding(sequence)
        segment_embedded = self.segment_embedding(segment)
        embedded_sources = token_embedded + positional_embedded + segment_embedded
        #embedded_sources =  segment_embedded

        mask = pad_masking(sequence)
        encoded_sources = self.encoder(embedded_sources, mask)
        token_predictions = self.token_prediction_layer(encoded_sources)
        classification_embedding = encoded_sources[:, 0, :]
        classification_output = self.classification_layer(classification_embedding)
        return token_predictions, classification_output


def build_model(layers_count, hidden_size, heads_count, d_ff, dropout_prob, max_len, vocabulary_size):
    #conex_embedding = ConexEmbedding(max_len = max_len, hidden_size = hidden_size)
    token_embedding = nn.Embedding(num_embeddings=vocabulary_size, embedding_dim=hidden_size)
    positional_embedding = PositionalEmbedding(max_len=max_len, hidden_size=hidden_size)
    segment_embedding = SegmentEmbedding(hidden_size = hidden_size)

    encoder = TransformerEncoder(
        layers_count = layers_count,
        d_model = hidden_size,
        heads_count = heads_count,
        d_ff = d_ff,
        dropout_prob=dropout_prob)

    triple_bert = TripleBERT(
        encoder = encoder,
        positional_embedding = positional_embedding,
        token_embedding = token_embedding,
        segment_embedding = segment_embedding,
        hidden_size = hidden_size,
        vocabulary_size = vocabulary_size
    )

    return triple_bert




