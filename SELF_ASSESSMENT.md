# P3 self-assessment — suggested scores for Sean to review

**Sean Ryan · sryan3 · DSA 405 (002) · Fall 2026**

The following scores are evidence-based suggestions, not Sean's confirmed self-scores and not an instructor grade. Review the exact A8 wording, public-disclosure ethics interpretation, and personal reflection before submitting.

| Criterion | Weight | Suggested score (0–4) | Evidence |
|---|---:|---:|---|
| Acquisition code | ×2 | 4 | `scripts/acquisition.py`: one-second minimum interval, coursework agent, timeout, non-200/empty failure, immutable disk cache, safe observed headers, finite complete URL inventory; cached/offline proof and a caught missing-table failure in notebook §1 |
| Ethics & legality in practice | ×2 | 3 | Source pair confirmed by Sean; implementation choices and public personal information documented in notebook §3 and `ETHICS_AND_DRIFT.md`. Exact A8 text remains to be compared; no new Senate agreement is accepted |
| Join design | ×2 | 4 | Notebook §4 states keys, both grains, one-to-one relationship, numeric expected count **3,760**, outer-join choice, NA policy and rejected alternatives before merging |
| Verification suite | ×3 | 4 | Notebook §5: nine real data assumptions, immutable raw hashes, upstream Senate reconciliation; seven reliability tests covering missing selectors, HTTP/timeouts, spacing, caching, duplicate keys and retained unmatched rows |
| Reproducibility & readability | ×1 | 4 | Fresh-kernel execution, saved outputs, complete local inputs and vendored code, pinned dependencies, README, and source-code inspector; Colab upload branch is provided but not tested inside Colab |

Suggested weighted total: `(4×2 + 3×2 + 4×2 + 4×3 + 4×1) / 40 = 38/40 = 95%`.

The frozen archive and comparison are fully runnable. The suggested ethics score deliberately reflects a remaining author-review item rather than claiming an exact plan comparison or legal determination. Adjust any score based on your own assessment and the instructor's rubric.

**Reflection to personalize:** Only 160 of the 3,760 ticker-month keys occur in both archives, so an inner join would lose 3,600 keys. Explain what you learned from checking this, in your own words; keep the incomplete-coverage caveat.

**Submission:** `notebooks/DSA405_002_FA26_P3_sryan3.ipynb` plus this repository link, due November 5, 2026, 11:59 PM Eastern. No Moodle submission is included in this build.
