"""Generate the course notebook; execution is a separate, visible verification step."""
from pathlib import Path
import json
import nbformat as nbf
from integration import ROOT

def generate():
    cells=[]
    def md(text):cells.append(nbf.v4.new_markdown_cell(text))
    def code(text):cells.append(nbf.v4.new_code_cell(text))
    md('''# P3 · Acquisition & Integration
**Sean Ryan · sryan3 · DSA 405 (002) · Fall 2026**

**Question:** Which reported ticker–calendar-month combinations occur in the archived House and Senate disclosure sources during transaction year 2025?

This independent repository reuses the audited P2 House snapshot and reparses official Senate HTML preserved by the existing scraper. It carries every required source file locally; it does not read from Data Portfolio or a sibling repository. The website is a supplementary source/code inspector; this executed notebook is the course deliverable.

**Observed result:** 6,394 in-scope House report rows and 518 Senate report rows form 3,760 ticker-month keys: 160 in both sources, 3,410 House-only, and 190 Senate-only. These are coverage observations about unequal, incomplete archives, not a census of actual trading. Amendments remain separate reported records.

**Run order:** Setup → acquisition → source parsing → ethics/drift → join design **before** the merge → verification → finding → self-assessment. Default execution is offline. Optional network acquisition is explicit and never submits a Senate agreement.''')
    md('''## 0. Setup and independent inputs
Run from the repository or its `notebooks/` directory. Install `requirements.txt` in a Python 3.12 environment first.

**Colab:** This repository is private. Download the repository ZIP (or the supplied `P3-project.zip`) while signed in, then run this cell and upload that ZIP when prompted. The cell extracts the project safely and installs its declared dependencies in Colab. No GitHub token belongs in this notebook.''')
    code('''from pathlib import Path
import sys, json, hashlib, zipfile, subprocess, importlib.util

candidates = [Path.cwd(), Path.cwd().parent, Path.cwd() / "P3"]
ROOT = next((p for p in candidates if (p / "scripts/integration.py").is_file()), None)
try:
    IN_COLAB = importlib.util.find_spec("google.colab") is not None
except ModuleNotFoundError:
    IN_COLAB = False
if ROOT is None and IN_COLAB:
    from google.colab import files
    uploads = files.upload()
    archives = [name for name in uploads if name.lower().endswith(".zip")]
    if len(archives) != 1:
        raise ValueError("Upload exactly one P3 project ZIP, containing scripts/ and data/raw/.")
    destination = Path("/content/p3_uploaded_project")
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(archives[0]) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError("Unsafe ZIP member path")
        archive.extractall(destination)
    ROOT = next((p.parent.parent for p in destination.rglob("scripts/integration.py")), None)
if ROOT is None:
    raise FileNotFoundError("Open this notebook inside the complete P3 repository, or upload its ZIP in Colab.")
if IN_COLAB:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")])
sys.path.insert(0, str(ROOT / "scripts"))
import pandas as pd
from IPython.display import display, Code, HTML, SVG
from integration import (verify_raw, load_house, prepare_comparable, aggregate,
                         join_design, merge_summaries, verify_join)
from senate import parse_archive, find_table, SourceStructureError
from acquisition import CachedFetcher, acquisition_plan, USER_AGENT
from build_site import failure_cases
print("Project root located. Python", sys.version.split()[0])
print("Unchanged original raw files verified:", verify_raw(ROOT))
display(pd.DataFrame(json.loads((ROOT / "provenance/source_commits.json").read_text())).T)
''')
    md('''## 1. Acquisition code
The source inventory is fixed, with 515 archived House PDFs and 583 Senate HTML filings. A finite inventory has no pagination; all 1,098 document URLs are enumerated. The original Senate live-search pagination code is retained for provenance in `provenance/senate_scraper_original.py`; this version does not run that agreement-gated search.

`CachedFetcher` identifies the requests as noncommercial coursework, waits at least one second between requests, uses a 30-second timeout, stops on non-200/empty responses, verifies cached hashes, and remembers both successes and failures for the run. The default parser reads `data/raw/`; optional `python scripts/acquisition.py --chamber Senate --limit 1` retrieves the pinned public archive copy. House URLs point to official PDFs.

The static-file downloads are **not API calls**. Safe response headers are archived, including rate-limit headers if the server supplies them; no documented API limit is assumed. The Senate acquisition path uses previously collected source HTML rather than silently accepting an access agreement. Windows text checkout CRLF bytes and GitHub raw LF transport bytes have separate documented hashes; archived inputs are not rewritten.''')
    code('''import inspect
# These are the exact implementations used, displayed here for grading.
print("User-Agent:", USER_AGENT)
display(Code(inspect.getsource(CachedFetcher), language="python"))
plan = acquisition_plan()
print("Enumerated source documents:", len(plan))
assert len(plan) == 1098  # protects against a missing document inventory
sample = next(row for row in plan if "/senate/" in row["path"])
client = CachedFetcher()
body = client.fetch(sample["url"])
assert hashlib.sha256(body).hexdigest() == sample["sha256"]
assert client.fetch(sample["url"]) == body  # same URL reuses memory
assert all(event["from"] != "network" for event in client.events)
print("Offline repeat-run proof:", [event["from"] for event in client.events])
header_rows = []
for path in (ROOT / "data/raw/http_cache").glob("*.json"):
    meta = json.loads(path.read_text())
    rate_headers = {k:v for k,v in meta["headers"].items() if "ratelimit" in k.lower() or k.lower() == "retry-after"}
    header_rows.append({"status":meta["status"],"source":meta["url"],
                        "observed rate-limit headers":rate_headers or "none returned (static file)",
                        "retrieved UTC":meta["retrieved_at_utc"]})
display(pd.DataFrame(header_rows))
''')
    md('''### Demonstrate a loud failure
A maintenance page is valid HTML but not a transaction table. Continuing would silently produce an empty dataset. A second demonstration duplicates a summary key: `validate="one_to_one"` must reject it.''')
    code('''caught = failure_cases()
assert {case["caught"] for case in caught} == {"SourceStructureError", "MergeError"}
for case in caught:
    print(case["title"], "→", case["caught"] + ":", case["message"])
print("Both deliberately broken inputs were caught; no bad output was accepted.")
''')
    md('''## 2. Source parsing and comparable scope
**House:** reuse P2's 7,667-row audited extract and its preserved decisions; do not silently rerun P2 cleaning. All 515 original PDFs and the pinned House parser are bundled. `scripts/rebuild_house.py` optionally rebuilds the earlier extraction into a working directory; it is not required by this frozen P3 analysis.

**Senate:** parse every one of the 583 archived electronic reports. Require the nine expected HTML headers and nine cells per transaction row. Missing tables, dates, amounts, files, and duplicate report/item identities stop the pipeline. The filing index keeps 97 deferred paper reports visible.

**Comparable population:** transaction dates in 2025, reported stock/fund records (`ST` for House; `Stock` for Senate), usable reported ticker text, and House resolver status `accepted`. Preserve all exclusions in a separate table. Preserve report-level identities and source URLs; keep amendments. Funds/ETFs can appear under these source labels. Ticker text is not a permanent security identifier, so overlap is descriptive rather than proof that securities are economically identical.''')
    code('''house_all = load_house(ROOT)
senate_all, senate_coverage = parse_archive(ROOT)
# Confirm the new strict parser reproduces the upstream archive's record identities and fields.
upstream = pd.read_csv(ROOT / "data/raw/senate/transactions_upstream.csv", dtype=str, keep_default_na=False)
upstream["row_key"] = upstream.report_id + ":" + upstream.item_number
audit_new = senate_all.assign(row_key=senate_all.filing_id + ":" + senate_all.row_number)
assert upstream.row_key.is_unique and audit_new.row_key.is_unique
assert set(upstream.row_key) == set(audit_new.row_key)
audit = audit_new.merge(upstream, on="row_key", validate="one_to_one", suffixes=("_new", "_upstream"))
for column in ["transaction_date", "ticker", "asset_name", "transaction_type"]:
    # Upstream converts the source placeholder -- to blank; the strict parser
    # retains it as evidence. Normalize ONLY that documented placeholder here.
    parsed_values = audit[column+"_new"].fillna("").replace({"--":""})
    assert parsed_values.eq(audit[column+"_upstream"].fillna("")).all(), column
print("Source ticker placeholder -- retained in", int(audit.ticker_new.eq("--").sum()), "rows; upstream stored these as blanks.")
house, house_excluded, house_counts = prepare_comparable(house_all, "House")
senate, senate_excluded, senate_counts = prepare_comparable(senate_all, "Senate")
display(pd.DataFrame([house_counts, senate_counts], index=["House", "Senate"]))
print("Senate filing coverage:", senate_coverage)
print("All 5,069 Senate parsed records reconcile to the upstream archived table.")
''')
    md('''## 3. Ethics and A8 plan drift
Sean confirmed on October 23 that A8 named **House + Senate disclosures**. This keeps those sources. The exact A8 text was not available in this build; Sean should compare its wording before submission.

Implementation choices to review as potential drift:

- Use transaction year 2025 and a frozen source snapshot so another reader can reproduce the result offline.
- Read the previously collected Senate electronic HTML and expose deferred paper reports. New acquisition can verify the pinned source copy without submitting the Senate agreement.
- Aggregate each source to ticker-month before merging, because House and Senate legislators are different entities. Keep the transaction append separate from the required validated join.

**Guardrails:** no account login, paywall, CAPTCHA solving, circumvention, or submission of the Senate access agreement is performed by P3. Public reports still contain names and disclosed financial interests, so the assignment's “no personal data” language cannot honestly be described as literal absence of personal information. The intended scope is public official disclosure data for noncommercial coursework; omit unrelated private identifiers and make no credit, solicitation, or wrongdoing inference. Consult the instructor if their phrase excludes this public-disclosure topic.

The [Senate access notice](https://efdsearch.senate.gov/search/home/) lists restrictions on report use. The [House Clerk](https://disclosures-clerk.house.gov/FinancialDisclosure) is the official House source. This notebook records the scope and access path; it does not claim a legal determination or that a previous agreement grants new consent.

**Coverage:** House's P2 archive has 515 PDFs, 449 with extracted rows and 66 without extracted rows. Senate has 583 electronic and 97 deferred paper reports across the index's 2021–2026 filing window. Their collection dates differ. Amount ranges are not exact amounts, and amendments may repeat economic events.''')
    md('''## 4. Join design — before writing the merge
**Do not merge transaction rows directly on ticker and month.** That would create a many-to-many multiplication when both chambers report several rows for the same ticker-month. Summarize each source first.

| Design item | Decision |
|---|---|
| Keys | reported ticker + calendar month, within 2025 |
| Left grain | one ticker-month in the House archive |
| Right grain | one ticker-month in the Senate electronic archive |
| Relationship | one-to-one after aggregation |
| Expected rows | **3,760**, independently counted as the union of key sets |
| Join type | outer: compare both sources while keeping unmatched keys |
| Unmatched values | retained with NA in the absent chamber; not filled with zero |

An inner join would discard 3,600 keys. Joining legislators across chambers does not answer this question. An append produces a common transaction table but does not compare the source summaries or prove join cardinality.''')
    code('''house_summary = aggregate(house, "house")
senate_summary = aggregate(senate, "senate")
design = join_design(house_summary, senate_summary)
display(pd.DataFrame([design]).T.rename(columns={0:"Declared before merge"}))
assert design["expected_rows"] == 3760  # protects the frozen snapshot's expected union size
assert len(house_summary) == 3570 and len(senate_summary) == 350
''')
    md('''### Run the declared merge
`validate=` rejects fan-out caused by duplicate summary keys. The union assertion in the next section independently rejects row loss from an accidental inner join.''')
    code('''joined = house_summary.merge(
    senate_summary,
    on=["ticker", "month"],
    how="outer",
    validate="one_to_one",
    indicator=True,
).sort_values(["ticker", "month"]).reset_index(drop=True)
display(joined.head(8))
''')
    md('''## 5. Verification suite
Each assertion protects a real assumption. These checks cover both unwanted row multiplication and lost unmatched records. The function is included in the repository and shown in full below.''')
    code('''display(Code(inspect.getsource(verify_join), language="python"))
checks = verify_join(joined, house_summary, senate_summary, design, house, senate)
for index, description in enumerate(checks, 1):
    print(f"PASS {index}: {description}")
assert verify_raw(ROOT) == 1105  # protects untouched original raw inputs
# Run the separate timeout, HTTP, cache, rate-limit, and deliberate join-failure tests too.
test_run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"], capture_output=True, text=True)
print(test_run.stderr.strip())
assert test_run.returncode == 0, "Reliability tests failed"
''')
    md('''## 6. One thing that surprised me — evidence to review
The overlap is small: **160 of 3,760 ticker-month keys (4.26%) occur in both archives**. An inner join would remove **3,600 keys (95.74%)**. This makes the choice of an outer join material, rather than cosmetic.

This observation is supported by the archived records; the first-person reflection should be reviewed and rewritten by Sean as needed. It does not establish that the chambers' actual investments differ by that amount, because coverage, filings, amendments, and source formats differ.''')
    code('''coverage = joined["_merge"].value_counts().reindex(["left_only", "right_only", "both"])
display(coverage.rename(index={"left_only":"House only", "right_only":"Senate only", "both":"Both chambers"}).to_frame("Unique ticker-month keys"))
print(f"Overlap: {design['both'] / design['expected_rows']:.2%}")
print(f"Keys an inner join would lose: {design['left_only'] + design['right_only']:,}")
# A static, directly labeled count diagram; widths use a shared zero-based scale.
labels = [("House only",design["left_only"]),("Senate only",design["right_only"]),("Both chambers",design["both"])]
bars = []
for i, (label, count) in enumerate(labels):
    y = 65 + i*48
    bars.append(f'<text x="12" y="{y+14}" font-size="13">{label}</text><rect x="125" y="{y}" width="{count/design["expected_rows"]*390}" height="19" fill="#216453"/><text x="540" y="{y+14}" font-size="13">{count:,}</text>')
display(SVG('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 240" width="620" role="img" aria-label="House only 3410; Senate only 190; both chambers 160 ticker-month keys"><rect width="620" height="240" fill="white"/><g font-family="Arial" fill="#162d36"><text x="12" y="25" font-size="17">2025 ticker-month keys by archive coverage</text>' + ''.join(bars) + '<text x="12" y="225" font-size="11">3,760 unique keys. Missing archive coverage is not an observed zero.</text></g></svg>'))
''')
    md('''## 7. Write reproducible outputs
The exclusion table accounts for every original row; source identities and URLs remain available. The interactive website is built from these same functions and output schemas.''')
    code('''output = ROOT / "data/processed"
output.mkdir(parents=True, exist_ok=True)
joined.to_csv(output / "combined_ticker_month.csv", index=False)
combined = pd.concat([house, senate.drop(columns="row_key",errors="ignore")], ignore_index=True)
assert combined.transaction_id.is_unique
combined.to_csv(output / "combined_transactions.csv", index=False)
pd.concat([house_excluded, senate_excluded], ignore_index=True).to_csv(output / "excluded_rows.csv", index=False)
print(f"Saved {len(joined):,} summary rows and {len(combined):,} comparable source rows.")
print("Raw inputs still verified:", verify_raw(ROOT))
''')
    md('''## 8. Suggested self-scored rubric — Sean to confirm
| Criterion | Weight | Suggested score (0–4) | Evidence / limit |
|---|---:|---:|---|
| Acquisition code | ×2 | 4 | explicit URL inventory, one-second throttle, honest agent, immutable cache, headers, timeouts/errors, demonstrated selector catch |
| Ethics & legality in practice | ×2 | 3 | sources confirmed verbally; exact A8 text and the instructor's public-personal-data wording still need review |
| Join design | ×2 | 4 | grain, keys, cardinality, expected numeric count, unmatched policy and alternatives stated before merge |
| Verification suite | ×3 | 4 | nine data assumptions, upstream reconciliation, seven failure-oriented tests |
| Reproducibility & readability | ×1 | 4 | self-contained archives and code, pinned environment, restarted execution, README, source inspector |

Suggested weighted self-score: **38/40 = 95%**, not an instructor grade and not Sean's confirmed self-score. Review `SELF_ASSESSMENT.md`, the A8 wording, and the reflection before submitting the notebook and repository link. No Moodle submission has been made by this build.''')
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12.14'}})
    nbf.validate(nb)
    path=ROOT/'notebooks/DSA405_002_FA26_P3_sryan3.ipynb'
    nbf.write(nb,path)
    print('Generated',path.name, 'with',len(cells),'cells')

if __name__=='__main__':generate()
