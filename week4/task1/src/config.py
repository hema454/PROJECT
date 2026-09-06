"""
Single source of truth for the embedding model used across the whole
pipeline (generate -> embed -> nearest neighbours -> search comparison).

Every script imports MODEL_NAME and EMBED_DIM from here instead of
hardcoding the model string. Change the model in exactly one place.
"""

MODEL_NAME = "all-MiniLM-L6-v2"   # sentence-transformers model
EMBED_DIM = 384                    # output vector length for MODEL_NAME above

TOP_K = 3                          # default number of neighbours to return