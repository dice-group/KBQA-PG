# FromAnswer Summarizer

The FromAnswer summarizer is used for generating triples by extracting them from a SPARQL query. This may be used with QA-datasets that offer an expected SPARQL query, like the QALD and LC-QuAD datasets. The FromAnswer summarizer inherits from the BaseSummarizer and therefore has the same interface. The list of triples generated is PREFIX free, additionally typed-literals in the 3rd position of a triple are annotated with their datatype ("example"@en, "42"^^xsd::integer, ...).

## Usage

The FromAnswer summarizer may be used with the [data_generator](../../data_generator) to generate a qtq-dataset. Simply specify _FromAnswer_ as the summarizer.

## Limitations

The FromAnswer summarizer does not work with questions that do not have an answer, either because they are outdated or because they are ASK questions that are supposed to return _false_.  
Also, it does not work with the VALUES keyword, and it ignores FILTERs and OPTIONALs.
