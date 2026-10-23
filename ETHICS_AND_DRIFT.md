# Ethics, access and A8 drift

Sean confirmed on October 23, 2026 that the A8 plan named **House + Senate disclosures**. The original A8 text was not available during this build. Compare the following implementation details with that text before submission; do not claim a verbatim plan comparison has already been performed.

| Plan element | P3 implementation | Reason / drift to review |
|---|---|---|
| House + Senate sources | Same official disclosure sources, via preserved local archives | Source pair is retained |
| Acquire a web source | Reparse Senate source HTML; optional verified download from Sean's pinned archive; official URL retained for every report | Reuse prior collection as permitted in the P3 brief, without newly accepting the Senate agreement |
| Combine sources | Aggregate each to ticker-month, then validated one-to-one outer join | Legislators differ across chambers; raw joins on ticker-month would multiply rows |
| Analysis dates | 2025 transaction year | Shared reproducible comparison, not current/live coverage |
| Original records | Keep raw files and reported amendments | Report-row counts remain distinct from deduplicated economic events |

## Access behavior

The default pipeline is offline. Optional HTTP acquisition uses public House PDF URLs and exact-commit copies of Senate HTML. It sets an honest coursework User-Agent, waits at least one second between requests, caches responses, uses a timeout, and stops on denials or unexpected structure. It never attempts a login, paywall, CAPTCHA solution, agreement submission, or circumvention. A failure is not permission to bypass a restriction.

The original Senate collection code accepted an eFD use notice. That code is included only as historical provenance, not executed or automatically authorized by P3. P3 does not claim that an earlier acceptance constitutes fresh consent. The current frozen inventory is finite and does not use an API or live search pagination.

## Personal information and purpose

These public disclosure reports contain official names and publicly disclosed financial interests. They are still personal information; a claim that the dataset contains literally “no personal data” would be inaccurate. The coursework interpretation is limited to public official records needed to demonstrate wrangling and integration, with no private identifiers or unrelated personal information added. If the instructor's guardrail excludes even these public disclosures, clarify the topic with the instructor before submitting.

This is noncommercial coursework, not credit assessment, solicitation, trading advice, or an allegation of wrongdoing. The [Senate's access notice](https://efdsearch.senate.gov/search/home/) states restrictions on report use. The [House Clerk's disclosure page](https://disclosures-clerk.house.gov/FinancialDisclosure) identifies the official House collection. These notes describe the implementation and intended purpose; they are not a legal determination.

## Interpretive limits

House scanned/handwritten filings and Senate paper reports have incomplete extraction coverage. Collection dates differ. Amendments can repeat economic events, ticker strings can be ambiguous or reused, and stock labels can include funds. A missing match means missing coverage in these archives, not an observed zero. Range amounts are not exact investment values. The outer join keeps unmatched keys visible rather than hiding these limitations in an inner-join result.
