"""Arguments for all architectures."""
from types import SimpleNamespace

BERT_SPBERT_SPBERT = SimpleNamespace(
    **{
        # --encoder_model_name_or_path, default=None, type=str, required=True,
        # help="Path to pre-trained model: e.g. roberta-base"
        "encoder_model_name_or_path": "bert-base-cased",
        # --decoder_model_name_or_path, default: None, type=str, required=True,
        # help="Path to pre-trained model: e.g. roberta-base"
        "decoder_model_name_or_path": "razent/spbert-mlm-wso-base",
        # --load_model_checkpoint, default="Dynamic", type=str, choices=["Yes", "No"],
        # help="Should the model weights at load_model_path be loaded. Defaults to "No" in training and "Yes" in testing"
        "load_model_checkpoint": "Yes",
        # --load_model_path, default="./output/checkpoint-best-bleu/pytorch_model.bin", type=str,
        # help="Path to trained model: Should contain the .bin files"
        "load_model_path": "/models/pytorch_model.bin",
        # --model_type, default="bert", type=str,
        # help="Model type: e.g. roberta"
        "model_type": "bert",
        # --model_architecture, default='bert2bert', type=str,
        # help="Model architecture: e.g. bert2bert, bert2rnd"
        "model_architecture": "bert2bert",
        # --output_dir, default="./output/", type=str,
        # help="The output directory where the model predictions and checkpoints will be written."
        "output_dir": "app/output/",
        # --train_filename, default=None, type=str,
        # help="The train filename. Should contain the .jsonl files for this task."
        "train_filename": None,
        # --dev_filename, default=None, type=str,
        # help="The dev filename. Should contain the .jsonl files for this task."
        "dev_filename": None,
        # --test_filename, default=None, type=str,
        # help="The test filename. Should contain the .jsonl files for this task."
        "test_filename": None,
        # --predict_filename, default=None, type=str,
        # help="The prediction filename."
        "predict_filename": "app/data/output/question",  # "./data/output/qald_9_test",
        # --source, default="en", type=str,
        # help="The source language (for file extension)"
        "source": "en",
        # --target, default="sparql", type=str,
        # help="The target language (for file extension)"
        "target": "sparql",
        # --config_name, default="", type=str,
        # help="Pretrained config name or path if not the same as model_name"
        "config_name": "",
        # --tokenizer_name, default="", type=str,
        # help="Pretrained tokenizer name or path if not the same as model_name"
        "tokenizer_name": "",
        # --max_source_length, default=64, type=int,
        # help="The maximum total source sequence length after tokenization. Sequences longer
        # than this will be truncated, sequences shorter will be padded."
        "max_source_length": 256,
        # --max_triples_length, default=128, type=int,
        # help="The maximum total triples sequence length after tokenization. Sequences longer
        # than this will be truncated, sequences shorter will be padded."
        "max_triples_length": 256,
        # --max_target_length, default=32, type=int,
        # help="The maximum total target sequence length after tokenization. Sequences longer
        # than this will be truncated, sequences shorter will be padded.",
        "max_target_length": 256,
        # --do_train, action="store_true", help="Whether to run training."
        "do_train": False,
        # --do_eval, action="store_true", help="Whether to run eval on the dev set."
        "do_eval": False,
        # --do_test, action="store_true", help="Whether to run eval on the dev set."
        "do_test": False,
        # --do_predict, action="store_true", help="Whether to run prediction on the predict set."
        "do_predict": True,
        # --do_lower_case, action="store_true",
        # help="Set this flag if you are using an uncased model."
        "do_lower_case": False,
        # --no_cuda, action="store_true", help="Avoid using CUDA when available"
        "no_cuda": True,
        # --train_batch_size, default=8, type=int,
        # help="Batch size per GPU/CPU for training."
        "train_batch_size": 8,
        # --eval_batch_size, default=8, type=int,
        # help="Batch size per GPU/CPU for evaluation."
        "eval_batch_size": 1,
        # --gradient_accumulation_steps, type=int, default=1,
        # help="Number of updates steps to accumulate before performing a backward/update pass."
        "gradient_accumulation_steps": 1,
        # --learning_rate, default=5e-5, type=float,
        # help="The initial learning rate for Adam."
        "learning_rate": 5e-5,
        # --beam_size, default=10, type=int, help="beam size for beam search"
        "beam_size": 1,
        # --weight_decay, default=0.0, type=float, help="Weight deay if we apply some."
        "weight_decay": 0.0,
        # --adam_epsilon, default=1e-8, type=float, help="Epsilon for Adam optimizer."
        "adam_epsilon": 1e-8,
        # --max_grad_norm, default=1.0, type=float, help="Max gradient norm."
        "max_grad_norm": 1.0,
        # --num_train_epochs, default=3, type=int,
        # help="Total number of training epochs to perform."
        "num_train_epochs": 3,
        # --max_steps, default=-1, type=int,
        # help="If > 0: set total number of training steps to perform. Override num_train_epochs."
        "max_steps": -1,
        # --eval_steps, default=-1, type=int, help=""
        "eval_steps": -1,
        # --train_steps, default=-1, type=int, help=""
        "train_steps": -1,
        # --warmup_steps, default=0, type=int, help="Linear warmup over warmup_steps."
        "warmup_steps": 0,
        # --local_rank, type=int, default=-1,
        # help="For distributed training: local_rank"
        "local_rank": -1,
        # --seed, type=int, default=42, help="random seed for initialization"
        "seed": 42,
        # --save_inverval, type=int, default=1, help="save checkpoint every N epochs"
        "save_interval": 1,
    }
)
