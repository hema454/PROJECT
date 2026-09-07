# Manual Review Findings (Step 3)

## Mid-sentence splits found
     (chunk_id, and the sentence it cut through)
      (5,d for at least twelve months after a new version is released, and breaking d for at least twelve months after a new version is released, and breaking changes are always announced at least ninety days in advance on the developer changelog.)
-

## Pure "page furniture" found
(chunk_id, and what it is -- header/footer/page number/boilerplate)
(3,source=platform_operations_manual.pdf | page=1 | section=None | date=2026-09-03)
-

## Chunks that lost their heading
(chunk_id where section=None but the text clearly belongs under a heading)
-
(2,source=platform_operations_manual.pdf | page=1 | section=Platform Operations Manual | date=2026-09-03
```
hput. Dashboards are automatically generated from these metrics and linked
hput. Dashboards are automatically generated from these metrics and linked
from the service catalog. Alerts are configured against these dashboards using thresholds
agreed upon during the service's initial design review.
Alert fatigue is taken seriously. Any alert that fires more than three times in a week
without leading to action is flagged for review during the next reliability meeting, and
either tuned, removed, or converted into an automated remediation.
4. On-Call Rotation
Engineers rotate through on-call duty on a weekly basis, with primary and secondary
assignments published two weeks in advance. Swapping shifts is allowed with mutual
agreement between engineers, recorded in the on-call scheduling tool so the paging system
stays accurate.)

 three specific useless chunks, and why

1. chunk_id: 5
       ed at least ninety days in advance on the developer changelog.
       Internal Engineering Docs -- Confidential -- Page 1
Why it's useless:
     It contains only the tail end of a sentence plus the footer. The footer is page furniture, and the incomplete sentence has very little standalone meaning.

2. chunk_id: 3
       om post-incident reviews are tracked to completion and reported on monthly

       during the reliability review meeting attended by engineering leadership.
   Why it's useless:
        This is just a small, incomplete fragment of content. It starts in the middle of a word (om) and mostly repeats content from the previous chunk, so it has poor standalone meaning for retrieval.

3. chunk_id:0
       meeting_notes_scanned.pdf_p2_struct_0
       meeting_notes_scanned.pdf_p1_struct_0
   
   Why it's useless:
       The two chunks are duplicates. Keeping both adds redundant information to your vector database and can cause the same information to be retrieved multiple times. One copy is enough
