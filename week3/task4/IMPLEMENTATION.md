
python eval_runner.py
```

Golden set: 30 cases total (`golden_set.py`), including refusal cases, scored
via `scorer.py`'s normalized field comparison.

## Prompt-change workflow

1. **Before editing**, run `python eval_runner.py` and record the current
   pass rate here as the "before" score — if it's unchanged from the last
   recorded baseline, skip this step and reuse the existing number.
2. Make the prompt edit.
3. **After editing**, run `python eval_runner.py` again and record the
   "after" score.
4. Compare: if the after-score is lower than before, treat that as a
   regression — inspect which specific golden cases flipped from pass to
   fail (add per-case printing in `eval_runner.py` if needed) before
   merging the prompt change.
5. Update this file's "Baseline pass rate" section with the new number and
   date once the change is accepted, so the next comparison starts from an
   accurate baseline.

## Example (to be filled in on the next real prompt change)

| Date | Change | Before | After |
|------|--------|--------|-------|
| 2026-09-01 | Initial baseline | — | 30/30 (100.0%) |