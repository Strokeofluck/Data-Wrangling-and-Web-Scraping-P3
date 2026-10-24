# P3 · In the record

**Sean Ryan · `sryan3` · DSA 405 (002) · Fall 2026**

An independent acquisition and integration project using **House Clerk PDFs + Senate eFD HTML**. Inspect a real source document, select an outlined field to see the exact code and rationale, and trace the combined result back to its filings.

Data Portfolio is unchanged and is not a runtime dependency. P3 bundles the needed archived sources, the audited P2 House input, Senate parsing code, verification, and an executed notebook. Its source inspector replaces P2's dense presentation with one document and one explanation at a time.

## Start here

Explore the result opens a disclosure search table modeled on Data Portfolio: individual report rows, global search, column filters, sortable headers, 10/25/50/100 rows per page, and source links. Switch to Ticker × month for the validated comparison and its row-level evidence. The 6,912 transaction rows are an append of the eligible 2025 reports; the 3,760-row ticker-month table remains the validated outer join. Each table has its own complete CSV download.

Click a source field to open a minimal code panel beside the document, without dimming or blocking it. The selected field stays marked; both panes scroll independently. Click another field to update the same panel, and close it to restore the field guide. Narrow screens stack the document above the inspector.

Underlined words in the plain-English notes link to checked literal code fragments. Hover or keyboard-focus a term such as “Copy” or “filer name” to highlight exactly the statement or value it describes. These are authored explanations, not generated guesses about arbitrary source code; the build rejects missing phrases, moved lines, and missing code fragments.

The connection works in reverse too: hover, focus, or tap a linked code fragment to highlight its matching plain-English words and show a small explanation. When a specific value overlaps a whole-statement link, the specific value takes priority. Tooltips clear when scrolling, changing steps, or closing the inspector.

Every highlighted code line has a reviewed plain-English note directly beneath it. The viewer still allows free scrolling through the complete file. Senate report title, filer name, and filing date are also interactive: their walkthroughs distinguish metadata collected by the original search scraper, preserved in the filing index, and carried into P3. Agency and section headings are fixed display labels. Report titles remain in the filing index rather than becoming transaction or join fields.

- **Submission notebook:** [DSA405_002_FA26_P3_sryan3.ipynb](notebooks/DSA405_002_FA26_P3_sryan3.ipynb)
- **Readable executed notebook:** [docs/P3-notebook.html](docs/P3-notebook.html)
- **Interactive inspector:** [docs/index.html](docs/index.html); run the local preview below. Download the repository before opening HTML; GitHub's file viewer does not execute it.
- **Suggested self-assessment, for Sean's review:** [SELF_ASSESSMENT.md](SELF_ASSESSMENT.md)
- **Course brief:** [P3: Acquisition & Integration](https://github.com/jon-holt/DSA-405-Student/blob/main/assignments/projects/DSA405_P3_AcquisitionIntegration_FA26.md)

The notebook and repository link are due **November 5, 2026, 11:59 PM Eastern**. The website supplements the notebook. This repository is private; it has not been made public or submitted to Moodle. Colab may require GitHub access. The notebook also supports uploading the complete project ZIP in Colab without putting credentials in code.

## Run from a fresh copy

Use Python 3.12. The default workflow is offline after dependency installation:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/build_site.py
python -m unittest discover -s tests -v
python scripts/execute_notebook.py
python -m http.server 8765 --bind 127.0.0.1
```

Open **http://127.0.0.1:8765/docs/** in your browser. Serving the repository root also makes each captured source download available. Stop the preview with Ctrl+C.

On macOS/Linux activate with `source .venv/bin/activate`. The static site also works by opening `docs/index.html` directly because its dataset is a local script, not a fetch call. Network is needed only to install dependencies, open external official-source links, or explicitly run acquisition. The notebook executor creates a fresh kernel using the Python interpreter that runs the script; it does not install a kernel in your user profile.

`build_site.py` regenerates the processed data, source examples, exact code excerpts and browser payload. `execute_notebook.py` executes the existing submitted notebook and exports its readable HTML. `build_notebook.py` is an authoring utility that **regenerates** notebook cells and clears saved outputs, so only run it when intentionally revising the notebook, then execute again.

`docs/data/house_geometry/` contains the source-hashed hover coordinates for all parsed rows on the displayed House pages. They are committed, so ordinary builds need no re-extraction. To regenerate them, run `python scripts/build_house_geometry.py` before `build_site.py`. The inherited P2 observer reads the pinned parser's accepted rows and does not change the parser, its decisions, or raw inputs.

## The integration question and join

Which reported **ticker × calendar-month** combinations occur in each source during transaction year **2025**?

| Input / output | House | Senate |
|---|---:|---:|
| Original parsed report rows | 7,667 | 5,069 |
| In-scope 2025 stock/fund rows with usable tickers | 6,394 | 518 |
| Unique ticker-month summary keys | 3,570 | 350 |

The **outer join** has **3,760 unique keys**: 3,410 House-only, 190 Senate-only, and 160 in both sources. Expected row count is calculated from the union of the two key sets **before** merging. `validate="one_to_one"` rejects duplicate summary keys; nine assertions verify row-count conservation, union preservation, key uniqueness, date scope, counts and overlap.

Do not merge raw House and Senate transaction rows on ticker/month: repeated records on both sides would multiply each other. Do not join on politician names: these chambers contain different people. The separate `combined_transactions.csv` is an append with chamber and source identity; it is not presented as the required relational join.

Unmatched chamber values remain **NA**, not zero. Counts describe disclosed report rows, with amendments retained. They are not deduplicated economic trades, exact dollar amounts, a complete census, or evidence of coordination or wrongdoing. Ticker strings are reported labels rather than permanent security identifiers; stock labels can include funds/ETFs.

## Source inspector

- **Random captured filings:** the full available collection, with 449 parsed House filings and all 583 electronic Senate filings. The picker starts with a random filing, and Random filing selects a different filing in the current chamber. This is a fixed snapshot; no scheduled updates or live screen capture is required. The comparison remains scoped to 2025 while the source browser includes the captured collection's broader dates.
- **House:** accurate source regions for every parsed transaction row on the displayed PDF page, plus matched filer metadata. All eight printed table columns are hoverable, including notification date. Dashed source-only regions explain that the capital-gains checkbox and printed item ID are not exported as separate structured values; empty extracted text is not interpreted as an unchecked checkbox. The parser generates its own sequential row identifier. Another 66 captured House PDFs have no parsed example and are not in the picker; 449 is not a census of all official 2025 filings.
- **Senate:** every transaction row in the selected filing, rendered as a simplified local reading view. Every cell in all nine collected columns is hoverable and clickable. External scripts are omitted from the displayed view; the source download is the captured HTML. This picker spans its saved collection's dates, while the analysis uses 2025 transaction dates.
- **Code walkthrough:** the entire source file with numbered lines, initially scrolled to the step's highlighted lines. Scroll freely from the first line to the last; Back to highlighted lines returns to the step. Previous/Next buttons, numbered steps, and left/right arrow keys follow extraction, transformation and P3 use. Hover or keyboard focus gives a source value, rationale and code pointer; click/Enter opens the full-file viewer. The steps distinguish historical P2 PDF parsing from P3's current audited-input loading.
- **Portfolio colors:** the portfolio's Quarto Cosmo white background, gray navigation, blue link/accent palette and dark code panel, with all assets kept local.
- **Join proof:** declared grains and cardinality, pre-merge expected counts, nine checks, two caught failure demonstrations.
- **Result:** ticker/month/match filters, pagination, full CSV download, and source-row lineage for every combined key.

## Acquisition and immutable raw files

`scripts/acquisition.py` enumerates a fixed 1,098-document inventory: 515 House PDFs + 583 Senate HTML pages. No page of the frozen inventory is hidden behind pagination. Original live Senate discovery and pagination code is preserved as provenance, not run by this project.

```powershell
# Optional network checks; the default pipeline does not need these.
python scripts/acquisition.py --chamber Senate --limit 1
python scripts/acquisition.py --chamber House --limit 1
```

The current acquisition client enforces a minimum one-second interval, identifies itself as coursework, uses a timeout, stops on non-200/empty responses, verifies cached hashes, and memoizes successful and failed URL attempts. Later runs read the immutable response cache. Corrupt or incomplete caches fail rather than refreshing silently. Static file downloads are not API calls; safe returned headers, including rate limits when supplied, are recorded rather than inventing a limit from documentation.

House URLs are official Clerk PDFs. Senate URLs point to an exact commit of Sean's existing archive of official HTML. The code does not newly accept the Senate agreement, sign in, or bypass access controls. It is **not** a live 2026 Senate collection system. The original scraper is retained for attribution; do not treat it as P3's current acquisition implementation.

`provenance/raw_sha256.json` verifies 1,105 original raw files. New HTTP responses are stored separately under `data/raw/http_cache/`. Windows Git text checkouts used CRLF, whereas GitHub raw transport uses LF: the acquisition inventory records a separate transport hash for that text-only difference. Archived files are never rewritten. `.gitattributes` disables line-ending conversion for raw, vendor and provenance files so hashes survive future checkouts.

## Provenance and limitations

- House input: audited P2 extract from commit `429c32a23a9d3236f59df1a94a321fbc0054afb1`. It preserves the 7,667 rows and P2 review decisions; the raw PDFs and pinned original parser came from `510945b2b1d600dd90b183858b86419926b81e65`.
- Senate input: archive and index at `611e7ff2ffe5a26b9b5d2a6978cc4a5c85cf8d37`, metadata dated October 22, 2026. All 583 electronic reports are reparsed; 97 paper reports remain deferred. Reparsed identities and source fields reconcile to the 5,069 upstream records, with the documented `--` ticker placeholder normalized only for that audit.
- Portfolio reference: two QMD pages copied at `f93fbbebc6f281f70f76f8c61fc94dd942ffe70f`. They demonstrate presentation and original input paths. They are not executed or required to build P3.
- House archive coverage: 515 PDFs, 449 with extracted transactions, 66 without extracted rows. No extracted row does not establish no reported transaction; scanned/handwritten documents may need OCR.
- Source collection windows differ and Senate includes later-filed reports of 2025 transactions. This is an archived comparison, not equally sampled chamber activity. Amendments remain separate.
- Missing/invalid tickers, out-of-year rows, and out-of-scope asset types remain accounted for in `excluded_rows.csv`. Original amount brackets and review flags are retained. No exact investment totals are calculated.

See [PROVENANCE.md](PROVENANCE.md), [ETHICS_AND_DRIFT.md](ETHICS_AND_DRIFT.md), and the notebook for fuller scope. The optional `scripts/rebuild_house.py` rebuilds the earlier House extraction into `data/work/`; the bundled P2 notebook records its audit/cleaning decisions. Default P3 analysis deliberately uses the frozen, already-audited extract.

## Files

```text
data/raw/                  original House inputs, audited P2 extract, Senate HTML/index, HTTP cache
data/processed/            comparable rows, exclusions, chamber summaries, joined result, verification
data/review/               inherited P2 review decisions
scripts/                   acquisition, strict parser, integration, build and notebook execution
notebooks/                 submitted P3 notebook with saved outputs
docs/                      self-contained source inspector and executed notebook HTML
provenance/                source commits, SHA-256 manifest, original pages and prior code
vendor/house-ptr-scraper/   pinned House parser and its original fingerprints
tests/                     failure-oriented acquisition and join checks
```

## Verification recorded for this version

Fresh-kernel notebook execution, complete offline pipeline rebuild, nine data assertions, upstream Senate reconciliation, raw checksums, seven reliability tests, and browser checks of source popups, chamber/filing switching, join proof, filters and lineage. Desktop and phone layouts are reviewed. The Colab ZIP-upload branch is provided but has not been executed inside Colab.

The A8 source pair was confirmed by Sean; the exact A8 text, personal reflection and suggested self-scores are clearly marked for review. These are preparation notes, not confirmation that a Moodle submission was made.
