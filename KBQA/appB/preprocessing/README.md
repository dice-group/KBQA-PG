# Preprocessors
In this folder you find some preprocessors.
- [basic_preprocessor](basic_preprocessor/README.md) is an overhauled version of the SPARQL preprocessor.
- [labeling_preprocessor](labeling_preprocessor/README.md) is the basic preprocessor with the addition, that URIs are encoded by their 
  label.
- [wordpiece_version](wordpiece_version/README.md) includes the [basic_preprocessor](basic_preprocessor/README.md) and 
[labeling_preprocessor](labeling_preprocessor/README.md) for the special case of using a 
tokenizer which is based on WordPiece.

For more information and basic usage guides, see the readme files in the corresponding folders.

## Warning
In case a WordPiece tokenizer is used, only the [wordpiece_version](wordpiece_version/README.md) will work properly.