""" A module to create BERT model with entity concatination following HuggingFace implementation of  BERT model."""
import torch
from KBQA.appB.transformer_architectures.bert_spbert_spbert_base.tripleBERT.tripleBERT import BertModel
from transformers.models.bert.modeling_bert import  BertPreTrainedModel
import torch.nn as nn
from torch.nn import CrossEntropyLoss


class BertforEntityConcat(BertPreTrainedModel):
    """Class for creating instance of modified BERT model by concatinating it with MLP to process entity embedding. """
    def __init__(self, config, mlp_dim = 100, hidden_dim = 768):
        super().__init__(config)
        assert (
            not config.is_decoder
        ), "If you want to use `BertForMaskedLM` make sure `config.is_decoder=False` for bi-directional self-attention."
        hidden_dim = hidden_dim
        mlp_dim = mlp_dim
        self.bert = BertModel(config)
        self.mlp = nn.Sequential(
            nn.Linear(hidden_dim  , mlp_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, mlp_dim),
            # nn.ReLU(),
            # nn.Linear(mlp_dim, mlp_dim),
            # nn.ReLU(),
            # nn.Linear()   
            
        )
        # self.sigmoid = nn.Sigmoid()
        self.softmax = nn.Softmax()

        self.init_weights()

    

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        head_mask=None,
        inputs_embeds=None,
        labels=None,
        encoder_hidden_states=None,
        encoder_attention_mask=None,
        output_attentions=None,
        output_hidden_states=None,
        entity_table = None,
        **kwargs
    ):
        
    
        assert kwargs == {}, f"Unexpected keyword arguments: {list(kwargs.keys())}."

        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
        )

        sequence_output = outputs[0]
        print(sequence_output, entity_table)
        entity_merged = torch.cat(sequence_output + entity_table)
        merged_output = self.mlp(entity_merged)
        prediction_scores = self.cls(merged_output)

        outputs = (prediction_scores,) + outputs[2:]  # Add hidden states and attention if they are here

        if labels is not None:
            loss_fct = CrossEntropyLoss()  # -100 index = padding token
            masked_lm_loss = loss_fct(prediction_scores.view(-1, self.config.vocab_size), labels.view(-1))
            outputs = (masked_lm_loss,) + outputs

        return outputs  # (masked_lm_loss), prediction_scores, (hidden_states), (attentions)


