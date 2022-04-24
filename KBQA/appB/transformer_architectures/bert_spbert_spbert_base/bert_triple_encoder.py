
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.TransformerEncoder as TransformerEncoder
import torch.nn.TransformerEncoderLayer as EncoderLayer 


class ConexEmbedding(nn.Module):
        def __init__(self, max_len, hidden_size):
            super(ConexEmbedding, self).__init__()
            self.positional_embedding = nn.Embedding(max_len, hidden_size)
            positions = torch.arrange(0, max_len)
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



def build_model(layers_count, hidden_size, heads_count, d_ff, dropout_prob, max_len, vocabulary_size):
    conex_embedding = ConexEmbedding(num_embeddings = vocabulary_size, embedding_dim = hidden_size)
    segment_embedding =SegmentEmbedding(hidden_size = hidden_size)


    encoder_layer = EncoderLayer(d_model = hidden_size, nhead = heads_count)
    encoder = TransformerEncoder(
     encoder_layer, num_layers = layers_count

     )

    TripleBERT = TripleBERT(
        encoder = encoder,
        conex_embedding = conex_embedding,
        segment_embedding = segment_embedding,
        hidden_size = hidden_size,
        vocabulary_size = vocabulary_size
    )



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
            triple_embedded = self.conex_embedding(sequence)
            segment_embedded = self.segment_embedding(segment)
            embedded_sources = triple_embedded + segment_embedded
            #embedded_sources =  segment_embedded

            mask = pad_masking(sequence)
            encoded_sources = self.encoder(embedded_sources, mask)
            triple_predictions = self.triple_prediction_layer(encoded)
            classification_embedding = encoded_sources[:, 0, :]
            classification_output = self.classification_layer(classification_embedding)
            return token_predictions, classification_output

