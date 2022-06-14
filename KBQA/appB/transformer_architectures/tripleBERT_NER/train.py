from pyt_model import BertforEntityConcat
from dataloaders import prepare_data_loaders
import torch.nn as nn
import torch
from tqdm import tqdm
HIDDEN_DIM = 768
MLP_DIM = 100

MAX_SEQ_LENGTH = 768
batch_size = 4
#model = BertforEntityConcat.from_pretrained('bert-base-uncased')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


train_dataloader, entity_found = prepare_data_loaders(MAX_SEQ_LENGTH, batch_size )

model = BertforEntityConcat(
                    bert_model_path= 'bert-base-uncased',
                    labels_count=entity_found,
                    hidden_dim=HIDDEN_DIM,
                    mlp_dim=MLP_DIM,
                )
model.to(device)
for epoch_num in range(20):
    model.train()
    for step_num, batch_data in enumerate(tqdm(train_dataloader, desc="Iteration")):
        token_ids, masks, _ = tuple(t.to(device) for t in batch_data)
        probas = model(token_ids, masks)