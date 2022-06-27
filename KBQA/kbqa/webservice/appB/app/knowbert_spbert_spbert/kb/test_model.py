from allennlp.common import Params
from allennlp.data import Vocabulary
from allennlp.modules.token_embedders import Embedding
from KBQA.appB.transformer_architectures.kb.knowbert import EntityLinkingWithCandidateMentions
from KBQA.appB.transformer_architectures.kb.knowbert import KnowBert
from KBQA.appB.transformer_architectures.kb.knowbert import SolderedKG
from KBQA.appB.transformer_architectures.kb.knowbert_utils import KnowBertBatchifier
from KBQA.appB.transformer_architectures.kb.wordnet import WordNetAllEmbedding
import torch


def load_entity_linking_wiki(vocab):
    print("Load wiki embedding")
    entity_embedding = Embedding(
        num_embeddings=vocab.get_vocab_size(namespace="entity_wiki"),
        embedding_dim=300,
        pretrained_file="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wiki_entity_linking/entities_glove_format.gz",
        sparse=False,
        trainable=False,
        vocab_namespace="entity_wiki",
        vocab=vocab,
    )
    print("Loaded wiki embedding")
    span_encoder_config = {
        "hidden_size": 300,
        "intermediate_size": 1024,
        "num_attention_heads": 4,
        "num_hidden_layers": 1,
    }
    return EntityLinkingWithCandidateMentions(
        vocab=vocab,
        contextual_embedding_dim=768,
        entity_embedding=entity_embedding,
        namespace="entity_wiki",
        span_encoder_config=span_encoder_config,
    )


def load_soldered_kg_wiki(vocab):
    entity_linker = load_entity_linking_wiki(vocab)
    print("Loaded wiki entity linker")
    span_attention_config = {
        "hidden_size": 300,
        "intermediate_size": 1024,
        "num_attention_heads": 4,
        "num_hidden_layers": 1,
    }
    return SolderedKG(
        vocab=vocab,
        entity_linker=entity_linker,
        should_init_kg_to_bert_inverse=False,
        span_attention_config=span_attention_config,
    )


def load_entity_linking_wordnet(vocab):
    concat_entity_embedder = WordNetAllEmbedding(
        embedding_file="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wordnet/wordnet_synsets_mask_null_vocab_embeddings_tucker_gensen.hdf5",
        entity_dim=200,
        entity_file="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wordnet/entities.jsonl",
        entity_h5_key="tucker_gensen",
        vocab_file="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wordnet/wordnet_synsets_mask_null_vocab.txt",
    )
    print("Loaded wordnet embedding")
    span_encoder_config = {
        "hidden_size": 200,
        "intermediate_size": 1024,
        "num_attention_heads": 4,
        "num_hidden_layers": 1,
    }
    return EntityLinkingWithCandidateMentions(
        vocab=vocab,
        concat_entity_embedder=concat_entity_embedder,
        contextual_embedding_dim=768,
        loss_type="softmax",
        namespace="entity_wordnet",
        span_encoder_config=span_encoder_config,
    )


def load_soldered_kg_wordnet(vocab):
    entity_linker = load_entity_linking_wordnet(vocab)
    print("Loaded wordnet entity linker")
    span_attention_config = {
        "hidden_size": 200,
        "intermediate_size": 1024,
        "num_attention_heads": 4,
        "num_hidden_layers": 1,
    }
    return SolderedKG(
        vocab=vocab,
        entity_linker=entity_linker,
        should_init_kg_to_bert_inverse=False,
        span_attention_config=span_attention_config,
    )


def load_model(
    preloaded_wiki_soldered_kg=None,
    preloaded_wordnet_soldered_kg=None,
    preloaded_vocab=None,
):
    # vocab = Vocabulary.from_params(Params({"directory_path": "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/models/vocabulary_wordnet_wiki.tar.gz"}))
    vocab = (
        preloaded_vocab
        if preloaded_vocab
        else Vocabulary.from_files(
            directory="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/models/vocabulary_wordnet_wiki.tar.gz"
        )
    )
    print("Loaded Vocabulary")
    print(vocab)
    wiki_soldered_kg = (
        preloaded_wiki_soldered_kg
        if preloaded_wiki_soldered_kg
        else load_soldered_kg_wiki(vocab)
    )
    print("Loaded wiki soldered KG")
    wordnet_soldered_kg = (
        preloaded_wordnet_soldered_kg
        if preloaded_wordnet_soldered_kg
        else load_soldered_kg_wordnet(vocab)
    )
    print("Loaded wordnet soldered KG")
    return KnowBert(
        vocab=vocab,
        bert_model_name="bert-base-uncased",
        soldered_kgs={"wiki": wiki_soldered_kg, "wordnet": wordnet_soldered_kg},
        soldered_layers={"wiki": 9, "wordnet": 10},
        model_archive="/home/jmenzel/Downloads/knowbert_wiki_wordnet_model.tar.gz",
    )


if __name__ == "__main__":
    # a pretrained model, e.g. for Wordnet+Wikipedia
    archive_file = "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/models/knowbert_wiki_wordnet_model.tar.gz"

    # load model and batcher
    params = Params({"archive_file": archive_file})
    print("Loading Model")
    model = load_model()  # ModelArchiveFromParams.from_params(params=params)
    model.eval()
    print("Loaded Knowbert")
    print("Loading Batchifier")
    batcher = KnowBertBatchifier(archive_file)

    sentences = ["Paris is located in France.", "KnowBert is a knowledge enhanced BERT"]

    # batcher takes raw untokenized sentences
    # and yields batches of tensors needed to run KnowBert
    for batch in batcher.iter_batches(sentences, verbose=True):

        batch["tokens"]["tokens"] = batch["tokens"]["tokens"]["tokens"]
        batch["candidates"]["wiki"]["candidate_entities"]["ids"] = batch["candidates"][
            "wiki"
        ]["candidate_entities"]["ids"]["token_characters"]

        candidate_mask = (
            batch["candidates"]["wiki"]["candidate_entities"]["ids"] > 0
        ).type(torch.uint8)
        batch["candidates"]["wiki"]["candidate_entities"]["ids"] -= candidate_mask
        print(candidate_mask)

        batch["candidates"]["wordnet"]["candidate_entities"]["ids"] = batch[
            "candidates"
        ]["wordnet"]["candidate_entities"]["ids"]["token_characters"]

        candidate_mask = (
            batch["candidates"]["wordnet"]["candidate_entities"]["ids"] > 0
        ).type(torch.uint8)
        batch["candidates"]["wordnet"]["candidate_entities"]["ids"] -= candidate_mask
        # model_output['contextual_embeddings'] is (batch_size, seq_len, embed_dim) tensor of top layer activations
        print(batch)
        model_output = model(**batch)
        print(model_output)