## Why rerank after hybrid retrieval?

BM25 uses an inverted index with term-frequency saturation, rare-term weighting and document-length normalization. It preserves exact identifiers; repair analyzers/fields when tokenization breaks a model number. Dense retrieval separately encodes queries and passages into a compatible space. Changing embedding models requires reindexing rather than comparing new queries with old vectors.

RRF adds `1/(k + rank)` per document; an absent document contributes zero. `k=60` is a smoothing constant, not a candidate count. Candidate windows and final Top-N are separate parameters. Rank fusion avoids adding incompatible raw scores but cannot establish that a passage contains complete terms.

A cross-encoder jointly scores each query/passage pair, spending more computation on a bounded candidate set. Retrieval seeks coverage; reranking distinguishes relevance. Neither can recover a shipping clause absent from all candidates.

| Observed failure | Diagnosis | Remedy |
|---|---|---|
| Relevant clause absent | Ingestion, chunking, analyzer, embedding version, filters | Repair recall/indexing; measure Recall@K |
| Relevant candidate ranked too low | Pair relevance and duplicates | Rerank a bounded set; deduplicate |
| High-ranked evidence lacks conditions | Nearby limits, table headers, footnotes | Preserve structure and expand bounded parent context |
| Complete evidence but invented answer | Citation alignment and unknown-value rules | Validate claims against evidence rather than tuning retrieval |

Apply scope filters in both retrieval paths and recheck document access before reading text. The ranking diagram is synthetic arithmetic; no embedding or reranker model is run.

References: [Elasticsearch RRF](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion), [semantic reranking](https://www.elastic.co/docs/solutions/search/ranking/semantic-reranking).
