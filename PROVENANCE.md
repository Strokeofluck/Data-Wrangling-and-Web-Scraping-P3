# Provenance and preserved source boundaries

| Artifact | Source repository / commit | P3 location |
|---|---|---|
| Audited House snapshot, PDFs, review decisions | [dsa405-part-2](https://github.com/Strokeofluck/dsa405-part-2/tree/429c32a23a9d3236f59df1a94a321fbc0054afb1) | `data/raw/`, `data/review/` |
| Original House parsing code | [house-ptr-scraper](https://github.com/Strokeofluck/house-ptr-scraper/tree/510945b2b1d600dd90b183858b86419926b81e65) through P2's unchanged vendor copy | `vendor/house-ptr-scraper/` |
| Archived Senate HTML, index and upstream transaction table | [senate-ptr-scraper](https://github.com/Strokeofluck/senate-ptr-scraper/tree/611e7ff2ffe5a26b9b5d2a6978cc4a5c85cf8d37) | `data/raw/senate/` |
| Prior Senate scraper | Same Senate commit | `provenance/senate_scraper_original.py` (historical reference only) |
| Portfolio source pages | [sean-data-portfolio](https://github.com/Strokeofluck/sean-data-portfolio/tree/f93fbbebc6f281f70f76f8c61fc94dd942ffe70f) | `provenance/stock-disclosures*.qmd` (reference only) |
| P2 audit notebook | P2 commit above | `provenance/P2_reference.ipynb` (historical reference only) |

Data Portfolio was read through a separate reference checkout. No portfolio source, branch, workflow, or published site was changed. P3's build and analysis contain no reference to an absolute source checkout or a required sibling repository.

## What is original, and what is derived

`data/raw/house_transactions_p2.csv` is an untouched copy of P2's audited **derived** extract, used as a frozen input to P3. Its placement under P3 raw inputs does not mean those rows were supplied directly as CSV by the House Clerk. The primary official evidence is the PDF archive.

Senate HTML under `data/raw/senate/html/` is the original page content archived by the prior scraper. The new strict parser reads it locally; its 5,069 report/item identities reconcile to the bundled upstream table. The upstream parser stores the source ticker placeholder `--` as blank in 1,625 rows; P3 preserves the placeholder and normalizes only this documented representation difference during reconciliation. Other compared source fields match exactly.

The metadata's October 22, 2026 collection timestamp and 2021–2026 filing window belong to the source archive, not to P3's 2025 transaction-year population. House uses the earlier P2 archive. These are unequal snapshots.

`provenance/raw_sha256.json` records fingerprints for all 1,105 original P3 inputs; `verify_raw()` verifies every file before building. The HTTP cache stores raw response bodies and safe metadata separately. Windows Git checkout line endings and raw GitHub response line endings can differ for text; separate transport checksums document this difference without changing a raw file.

## Source visualization

The House WebP examples and coordinate records are copied from P2's source inspector. They show actual PDF pages, and the outlines use P2's recorded PDF rectangles. The P3 website displays excerpts of exact code from the vendored parser or current scripts, with line references generated from the local AST.

The source picker includes all 449 parsed House filings in the captured 2025 filing-index collection and all 583 captured electronic Senate filings across their saved dates. It is not a census of all official 2025 disclosures. The other 66 House PDFs remain in raw inputs without interactive parsed examples. The ticker-month comparison uses 2025 transaction dates.

`scripts/build_house_geometry.py` reuses P2's unchanged AST observer in `scripts/trace_geometry.py` to record every accepted transaction row on each displayed House PDF page, with coordinates cached under `docs/data/house_geometry/`. Each filing's observed row count is checked against its P2 metadata; transformed values come from the audited input. Original raw files and pinned parser code are not changed. Matched first-page filer name, status and state/district text can also be inspected.

All eight House table columns are hoverable, including notification date. The capital-gains and printed item-ID cells are marked as source-only: geometry clips their text, but the parser does not export a structured checkbox state or separate printed-ID value. Empty extracted text is not labeled unchecked. The generated sequential transaction number is explained separately. Senate views make every collected cell on every row hoverable without executing the original page scripts. Download links reference complete local sources. Random selection does not trigger live collection.

The field walkthroughs include complete source files, with step focus targets resolved from the Python AST. A missing focus anchor fails the build. The code pane initially jumps to those targets but can scroll above and below them through the entire file; Back to highlighted lines restores the step. Left/right navigation follows each field through its functions. These presentation changes do not alter the raw manifest, parser decisions, analysis population, or join.

The processed CSVs and `docs/data/project.js` are generated outputs. The combined transaction file is an append preserving chamber and source identities. `combined_ticker_month.csv` is the separately validated one-to-one outer join. No amount range is turned into a made-up exact value.

No third-party license is invented for the inherited code; the source attribution and original vendor notes are retained. The two original portfolio QMD files are archival references, not independent executable P3 pages.
