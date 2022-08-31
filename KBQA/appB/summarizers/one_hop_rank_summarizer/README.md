# OneHopRankSummarizer

### Parameters:

##### datasets

Order of the datasets 'qald8', 'qald9' and 'lcquad'. The value has to be in '["qald8_qald9_lcquad", "qald9_qald8_lcquad", "qald8_lcquad_qald9", "qald9_lcquad_qald8", "lcquad_qald8_qald9", "lcquad_qald9_qald8"]'.

##### lower_rank

By default, all triples with at least rank 1 are included in the summarized subgraph. This way all triples, whose relation occurs at least once in the dataset, is also added to the subgraph. However, it is possible to choose a higher rank to exclude triples with lower ranks. This might be useful, if there are too many ranked triples.

##### max_triples

In general it is possible that many triples have the same form, i.e. they differ only in their object or subject. Setting this parameter will restrict the number of triples of the same form by the value. For example, if the parameter is set to 2 and there are summarized triples

- dbr:Germany dbp:leaderName dbr:Angela_Merkel
- dbr:Germany dbp:leaderName dbr:Frank-Walter_Steinmeier
- dbr:Germany dbp:leaderName dbr:Olaf_Scholz

then only two of those triples are actually summarized. It is recommended to set this parameter in order to avoid getting subgraphs, which are too large. The default value is 3.

##### limit

Setting this parameter will return at most _limit_ triples. Use -1 to use not any limit.

##### timeout

In some cases it might be helpful to have a timeout between requests to avoid connection errors. Setting this parameter will apply a timeout between the requests in seconds.

##### verbose

Print some statements while summarizing.
