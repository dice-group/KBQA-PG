from tokenize import Token
from allennlp.data import Instance, Vocabulary
from allennlp.data.fields import TextField
from allennlp.data.tokenizers import PretrainedTransformerTokenizer
from allennlp.data.token_indexers import SingleIdTokenIndexer

bert_vocab = Vocabulary.from_pretrained_transformer(model_name='bert-base-uncased')
vocab = Vocabulary.from_files(directory="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/models/vocabulary_wordnet_wiki.tar.gz")
bert_vocab.extend_from_vocab(vocab)
print(bert_vocab)
text = "Paris is located in France."
tokenizer = PretrainedTransformerTokenizer(model_name='bert-base-uncased')
tokenized_text = TextField(tokenizer.tokenize(text), token_indexers={"tokens" : SingleIdTokenIndexer()})
print(tokenized_text)
instance = Instance({"tokens": tokenized_text})
print(instance)
instance.index_fields(vocab=vocab)
print(instance.as_tensor_dict())
print()
