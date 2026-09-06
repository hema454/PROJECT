# Analysis

## 1. Cosine distance, explained with two sentences from my own corpus

- Sentence A (query): "How can I make my app load faster?"
- Sentence B (corpus): "Why is the dashboard loading slowly?"
- Cosine similarity (from outputs/search_comparison_results.md): 0.5659
- Cosine distance = 1 - similarity = 0.4341

Sentence A and Sentence B are both embedded into 384-number vectors by
the same model. Cosine similarity measures the angle between those two
vectors: 1.0 would mean they point in exactly the same direction
(identical meaning), 0 means unrelated, negative means opposite
meaning. Here the score is 0.5659 -- meaningfully close, but not
near-identical -- which lines up with the sentences: they're about the
same underlying problem (something in the app is slow) but phrased
from two different angles (a user asking how to fix it vs. someone
noticing the symptom). Cosine distance is just `1 - similarity`, so a
distance of 0.4341 is "moderately close." Critically, Sentence A and B
share zero exact words in common ("load"/"faster" vs "loading"/"slowly"
aren't even the same literal tokens) -- keyword search found nothing
useful here (its top-1 was a different, wrong sentence), but the
embedding model still placed them close together because it captured
the shared *meaning*, not shared spelling.

## 2. Where keyword search would have won -- design implications

Case B (from outputs/search_comparison_results.md, candidate 2): query
"TXN-88215". Keyword search matched the correct sentence
("Transaction TXN-88215 failed due to an expired card.") immediately
via exact substring match. Semantic search's top-1 result was instead
"Transaction TXN-88214 failed due to an expired card." (similarity
0.6112) -- the *wrong* transaction, differing from the query by a
single digit, and its score was barely below the correct sentence's
own similarity to itself (0.6137). The two sentences are nearly
word-for-word identical except for one digit in the transaction code,
and the embedding model could not reliably separate them.

This matters for design because rare, high-precision identifiers
(transaction IDs, ticket numbers, SKUs, error codes) carry little
semantic "meaning" for an embedding model -- it has seen few or no
examples of that specific string during training, so nearby but
distinct identifiers can end up almost indistinguishable in vector
space, even though they refer to completely different, specific
records. A production retrieval system should not rely on embeddings
alone for these cases. It should combine semantic search with an
exact-match or metadata filter (see 4.8) whenever a query looks like
an ID, code, or other structured token -- e.g. detecting an ID-shaped
query and running a `WHERE transaction_id = ...` lookup instead of, or
alongside, vector similarity search -- rather than trusting distance-
based ranking to distinguish "TXN-88214" from "TXN-88215."