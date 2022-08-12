# Preprocessors Library
In this folder you find some preprocessors.
- *basic_preprocessor* is an overhauled version of the SPARQL preprocessor.
- *labeling_preprocessor* is the basic preprocessor with the addition, that URIs are encoded by their 
  label.
- *wordpiece_version* includes the *basic_preprocessor* and *labeling_preprocessor* for the special case of using a 
  tokenizer which is based on WordPiece.

For more information and basic usage guides, see the readme files in the corresponding folders.

## Warning
In case a WordPiece tokenizer is used, only the wordpiece_version will work properly.