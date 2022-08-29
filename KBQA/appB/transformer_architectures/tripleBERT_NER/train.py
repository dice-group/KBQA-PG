""" A module for training of BERT model with entity concatination."""
from pyt_model import BertforEntityConcat
from dataloaders import prepare_data_loaders
import torch.nn as nn
import torch
from tqdm import tqdm
from torch.optim import AdamW


#define pramater values for model for training
HIDDEN_DIM = 512
MLP_DIM = 50

MAX_SEQ_LENGTH = 512 
batch_size = 2

#model = BertforEntityConcat.from_pretrained('bert-base-uncased')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#biuld data to load into the model
train_dataloader, entity_found = prepare_data_loaders(MAX_SEQ_LENGTH, batch_size )

#initialize Model with defined prameters
model = BertforEntityConcat(
                    bert_model_path= 'bert-base-uncased',
                    labels_count=entity_found,
                    hidden_dim=HIDDEN_DIM,
                    mlp_dim=MLP_DIM,
                )
optimizer = AdamW(model.parameters(), lr=0.05)

#load the model to computing device
model.to(device)
epochs = 20

#start of the training process
for epoch_num in range(epochs):
    model.train()
    train_loss = 0
    print(f'Epoch: {epoch_num + 1}/{epochs}')

    for step_num, batch_data in enumerate(tqdm(train_dataloader, desc="Iteration")):
        token_ids, masks, entities, gold_labels = tuple(t.to(device) for t in batch_data)
        
       
        probas = model(token_ids, masks, entities)
        
        loss_func = nn.BCELoss()
        batch_loss = loss_func(probas, gold_labels)
        train_loss += batch_loss.item()

        model.zero_grad()
        batch_loss.backward()
        optimizer.step()
        print(f'\r{epoch_num} loss: {train_loss / (step_num + 1)}')

        print(str(torch.cuda.memory_allocated(device) / 1000000) + 'M')
