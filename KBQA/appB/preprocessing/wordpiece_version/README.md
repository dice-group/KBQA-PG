# WordPiece Version
This is the preprocessing in case a WordPiece tokenizer is used.

## Rationale
The WordPiece tokenizer *BertTokenizer* is removing spaces around special characters. This is invalidating many 
SPARQLs. So we implemented a special version to work around this.

There is an optional argument *clean_up_tokenization_spaces* for decoding of the tokenizer. This might solve our 
problem. This argument is not working properly at the moment, see 
https://github.com/huggingface/transformers/issues/15956 .

## Note
This version is a quick and dirty fix. It is not Linter approved. It is not working as good as the base version.

## TODO
- Test this with the tokenizer which is used.
- The encoding "variable:" probably yields problems in token- and untokenization.