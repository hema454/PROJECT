# Semantic Search vs Keyword Search (Step 3)

**What this measures:** for each case, whether each method's top-1 result equals the known expected match (pass/fail).

## Case A: where semantic search wins

**Query:** "How can I make my app load faster?"
**Expected match:** "Why is the dashboard loading slowly?"
**Why:** Verified from Step 2 (nearest_neighbors_results.md): this was the real top-1 semantic match, similarity 0.5659, with zero shared content words between query and match ('load'/'faster' vs 'loading'/'slowly' -- not even the same literal tokens).

**Keyword top-1 == expected: False**
- (2) The mobile app uses pagination to reduce initial load size.
- (1) Update your recovery phone number to regain access faster.
- (1) Screen recordings help our team diagnose issues faster.

**Semantic top-1 == expected: True**
- (0.5659) Why is the dashboard loading slowly? <- expected
- (0.5176) The mobile app uses pagination to reduce initial load size.
- (0.4268) Compressing images can noticeably speed up page load times.

## Case B candidates: where keyword search should win

## Case B candidate 1

**Query:** "TXN-88214"
**Expected match:** "Transaction TXN-88214 failed due to an expired card."
**Keyword top-1 == expected: True**
- (6) Transaction TXN-88214 failed due to an expired card. <- expected
- (0) How do I reset my password?
- (0) Steps to change your login credentials.

**Semantic top-1 == expected: True**
- (0.6137) Transaction TXN-88214 failed due to an expired card. <- expected
- (0.5906) Transaction TXN-88215 failed due to an expired card.
- (0.2920) You can open a support ticket directly from the help center.

## Case B candidate 2

**Query:** "TXN-88215"
**Expected match:** "Transaction TXN-88215 failed due to an expired card."
**Keyword top-1 == expected: True**
- (6) Transaction TXN-88215 failed due to an expired card. <- expected
- (0) How do I reset my password?
- (0) Steps to change your login credentials.

**Semantic top-1 == expected: False**
- (0.6112) Transaction TXN-88214 failed due to an expired card.
- (0.6097) Transaction TXN-88215 failed due to an expired card. <- expected
- (0.2988) You can open a support ticket directly from the help center.

## Summary

| Case | Keyword top-1 correct | Semantic top-1 correct |
|---|---|---|
| Case A: where semantic search wins | False | True |
| Case B candidate 1: "TXN-88214" | True | True |
| Case B candidate 2: "TXN-88215" | True | False |