PAD_TOKEN, PAD_INDEX = '[PAD]', 0
UNK_TOKEN, UNK_INDEX = '[UNK]', 1
MASK_TOKEN, MASK_INDEX = '[MASK]', 2
CLS_TOKEN, CLS_INDEX = '[CLS]', 3
SEP_TOKEN, SEP_INDEX = '[SEP]', 4


def pad_masking(x):
    # x: (batch_size, seq_len)
    padded_positions = x == PAD_INDEX
    return padded_positions.unsqueeze(1)