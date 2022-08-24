# Module to fine-tune modified BERT model on pre-processed triples and generate tripleBERT model.
# from transformers import BertTokenizer, BertForMaskedLM
from bert_LM import BertForMaskedLM
import torch
from transformers import AdamW
from transformers import BertTokenizer
from transformers import Trainer
from transformers import TrainingArguments

sparql_vocab = False


tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForMaskedLM.from_pretrained("bert-base-uncased")
# config = BertConfig.from_json_file('out/config.json')
# model = BertForMaskedLM(config)

with open("preprocessed_data_files/qtq-qald-8-train.triple", "r") as fp:
    text = fp.read().split("\n")

#adds special sparql tokens to the model 
if sparql_vocab is True:
    with open('sparql_vocabulary.txt', 'r') as fp1 :
        new_tokens = fp1.read().split('\n')

    num_added_toks = tokenizer.add_tokens(new_tokens)
    model.resize_token_embeddings(len(tokenizer))

inputs = tokenizer(
    text, return_tensors="pt", max_length=512, truncation=True, padding="max_length"
)

inputs["labels"] = inputs.input_ids.detach().clone()


# create random array of floats with equal dimensions to input_ids tensor
rand = torch.rand(inputs.input_ids.shape)
# create mask array
mask_arr = (
    (rand < 0.15)
    * (inputs.input_ids != 101)
    * (inputs.input_ids != 102)
    * (inputs.input_ids != 0)
)

selection = []

for i in range(inputs.input_ids.shape[0]):
    selection.append(torch.flatten(mask_arr[i].nonzero()).tolist())

for i in range(inputs.input_ids.shape[0]):
    inputs.input_ids[i, selection[i]] = 103


class TripleDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings.input_ids)

#generate the dataset instance from input and fit it into dataloader
dataset = TripleDataset(inputs)
loader = torch.utils.data.DataLoader(dataset, batch_size=8, shuffle=True)


device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
# and move the model over to the selected device
model.to(device)
# activate training mode
model.train()


# initialize optimizer
optim = AdamW(model.parameters(), lr=5e-5)


args = TrainingArguments(
    output_dir="out", per_device_train_batch_size=2, num_train_epochs=100
)
trainer = Trainer(model=model, args=args, train_dataset=dataset)

#perform the training of the model
trainer.train()

#save the trained model to output directory
model.save_pretrained("out/")
