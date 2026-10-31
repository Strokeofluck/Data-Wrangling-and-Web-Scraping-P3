# P3 self-assessment

**Sean Ryan · sryan3 · DSA 405 (002) · Fall 2026**

Sean selected the maximum self-score on every criterion. The evidence and remaining limitations are stated below; these self-scores are not an instructor-awarded grade.

| Criterion | Weight | Self-score (1–4) | Evidence |
|---|---:|---:|---|
| Acquisition code | ×2 | 4 | `scripts/acquisition.py`: one-second minimum interval, coursework agent, timeout, non-200/empty failure, immutable disk cache, safe observed headers, finite complete URL inventory; cached/offline proof and a caught missing-table failure in notebook §1 |
| Ethics & legality in practice | ×2 | 4 | Notebook §3 compares P3 with the actual A8 submitted October 14; records the source approval stated in A8; explains changes in year, snapshot, acquisition path and request delay. Identifiable public disclosures and use limits remain explicit; no new Senate agreement is accepted |
| Join design | ×2 | 4 | Notebook §4 states keys, both grains, one-to-one relationship, numeric expected count **3,760**, outer-join choice, NA policy and rejected alternatives before merging |
| Verification suite | ×3 | 4 | Notebook §5: nine real data assumptions, immutable raw hashes, upstream Senate reconciliation, twelve reliability tests, and printed catches from copies of the actual summaries: duplicate Senate key, missing unmatched result row, and incorrect House report count. Original frames and raw files are checked unchanged |
| Reproducibility & readability | ×1 | 4 | Fresh-kernel execution, saved outputs, complete local inputs and vendored code, pinned dependencies, README, and source-code inspector; Colab upload branch is provided but not tested inside Colab |

Weighted points: `4×2 + 4×2 + 4×2 + 4×3 + 4×1 = 40/40`.

Weighted mean: `40 / (2 + 2 + 2 + 3 + 1) = 4.0`. Course conversion: `88 + (4.0 − 3) × 12 = 100%`.

**Limits:** The archives have incomplete and unequal coverage. Public names and financial disclosures remain personal information; A8 records approval of the topic, not an unrestricted data license or general permission to automate access. The Colab upload branch has not been tested inside Colab. The notebook's finding explains why an inner join would hide 3,600 of 3,760 keys without treating that overlap as a census of actual trading.

**Bench Check 2:** Scheduled; status confirmed by Sean on October 31, 2026.

**Submission:** `notebooks/DSA405_002_FA26_P3_sryan3.ipynb` plus this repository link, due November 5, 2026, 11:59 PM Eastern. No Moodle submission is included in this build.
