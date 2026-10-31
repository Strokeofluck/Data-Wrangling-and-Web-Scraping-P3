# Ethics, access and A8 drift
Compared with `DSA405_002_FA26_A8_sryan3.ipynb`, submitted to Moodle on October 14, 2026. A8 names **House + Senate disclosures** and records that Sean asked the instructor about these sources and received approval. P3 retains that topic and the public-official disclosure scope; it does not claim that topic approval establishes an unrestricted license or automated-access permission.

| A8 plan | P3 implementation and reason for drift |
|---|---|
| Reuse archives; obtain missing official PDFs and Senate HTML through the normal agreement/session flow | Reuse frozen archives by default. Optional House acquisition uses official PDF URLs; Senate acquisition retrieves exact-commit archive copies. This avoids repeating an agreement-gated live search and keeps the build reproducible offline. The original collector remains attributed. |
| October 14 snapshot: 581 electronic Senate filings and 5,052 rows | P3 pins the October 22 archive: 583 electronic filings and 5,069 rows. The 97 deferred paper reports remain an explicit gap. Snapshot growth is not a claim of completeness. |
| At least two seconds between requests | P3 uses the brief's one-second minimum, with one request at a time, caching, timeouts and loud errors. Denied requests are not automatically retried. The default build makes no source requests. This rate change is documented rather than described as an exact match to A8. |
| Standardize transactions and compare chambers | Aggregate each chamber to one row per ticker-month before a one-to-one outer join. Different legislators cannot be matched across chambers, and repeated raw ticker-month rows would multiply. Keep the transaction append separate. |

**Guardrails:** no account login, paywall, CAPTCHA solving, circumvention, or submission of the Senate access agreement is performed by P3. Public reports still contain names and disclosed financial interests, so the assignment's “no personal data” language cannot honestly be described as literal absence of personal information. The intended scope is the public-official disclosure topic recorded as instructor-approved in A8, for noncommercial coursework; omit unrelated private identifiers and make no credit, solicitation, or wrongdoing inference.

The [Senate access notice](https://efdsearch.senate.gov/search/home/) lists restrictions on report use. The [House Clerk](https://disclosures-clerk.house.gov/FinancialDisclosure) is the official House source. This notebook records the scope and access path; it does not claim a legal determination or that a previous agreement grants new consent.

**Coverage:** The captured House archive has 515 PDFs, 449 with extracted rows and 66 without extracted rows. Senate has 583 electronic and 97 deferred paper reports across the index's 2021–2026 filing window. Their collection dates differ. Amount ranges are not exact amounts, and amendments may repeat economic events.
