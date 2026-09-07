# Nearest Neighbours: Manual numpy vs Library (Step 2)

**What this measures:** whether the manual numpy cosine-similarity implementation and the sentence-transformers library function agree on the same top-3 sentences for each query (correctness check, not a speed comparison). Timing is included for reference only.

## Query: "How do I get my money back?"

**Correctness check (manual == library top-3):** True
**Timing (reference only, not the pass/fail criterion):** manual 0.50ms, library 10.35ms

| Rank | Manual (numpy) | Score | Library | Score |
|---|---|---|---|---|
| 1 | How can I contact customer support? | 0.4922 | How can I contact customer support? | 0.4922 |
| 2 | Refunds are processed within 5 to 7 business days. | 0.4374 | Refunds are processed within 5 to 7 business days. | 0.4374 |
| 3 | How do I reset my password? | 0.3916 | How do I reset my password? | 0.3916 |

## Query: "My account got locked, what do I do?"

**Correctness check (manual == library top-3):** True
**Timing (reference only, not the pass/fail criterion):** manual 0.72ms, library 1.13ms

| Rank | Manual (numpy) | Score | Library | Score |
|---|---|---|---|---|
| 1 | How do I reset my password? | 0.6530 | How do I reset my password? | 0.6530 |
| 2 | Locked accounts are automatically unlocked after one hour. | 0.6057 | Locked accounts are automatically unlocked after one hour. | 0.6057 |
| 3 | Multiple failed login attempts will temporarily lock your account. | 0.5988 | Multiple failed login attempts will temporarily lock your account. | 0.5988 |

## Query: "What happens if I go over the API rate limit?"

**Correctness check (manual == library top-3):** True
**Timing (reference only, not the pass/fail criterion):** manual 0.88ms, library 1.24ms

| Rank | Manual (numpy) | Score | Library | Score |
|---|---|---|---|---|
| 1 | The API returns a 429 status code when you exceed the rate limit. | 0.7522 | The API returns a 429 status code when you exceed the rate limit. | 0.7522 |
| 2 | Rate limits for integrations are separate from your main API quota. | 0.6909 | Rate limits for integrations are separate from your main API quota. | 0.6909 |
| 3 | Rate limits are capped at 1000 requests per minute per key. | 0.6039 | Rate limits are capped at 1000 requests per minute per key. | 0.6039 |

## Query: "How can I make my app load faster?"

**Correctness check (manual == library top-3):** True
**Timing (reference only, not the pass/fail criterion):** manual 0.45ms, library 0.83ms

| Rank | Manual (numpy) | Score | Library | Score |
|---|---|---|---|---|
| 1 | Why is the dashboard loading slowly? | 0.5659 | Why is the dashboard loading slowly? | 0.5659 |
| 2 | The mobile app uses pagination to reduce initial load size. | 0.5176 | The mobile app uses pagination to reduce initial load size. | 0.5176 |
| 3 | Compressing images can noticeably speed up page load times. | 0.4268 | Compressing images can noticeably speed up page load times. | 0.4268 |

## Query: "Is my information safe with you?"

**Correctness check (manual == library top-3):** True
**Timing (reference only, not the pass/fail criterion):** manual 0.88ms, library 1.15ms

| Rank | Manual (numpy) | Score | Library | Score |
|---|---|---|---|---|
| 1 | How is my data encrypted? | 0.3883 | How is my data encrypted? | 0.3883 |
| 2 | Personal data can be deleted upon request under GDPR. | 0.3845 | Personal data can be deleted upon request under GDPR. | 0.3845 |
| 3 | Employee access to customer data is logged and reviewed regularly. | 0.2724 | Employee access to customer data is logged and reviewed regularly. | 0.2724 |

## Summary

All 5 queries matched between manual and library: **True**