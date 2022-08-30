# BaseSummarizer

The BaseSummarizer is used as a superclass for all summarizers. It forces a subclass to overwrite the _summarize_ function, which is used to collect all triples for a natural language question. The _summarize_ function requires a **Question** object, which has to be imported from **KBQA/appB/data_generator**. Since this class is abstract, there is no example usage.
