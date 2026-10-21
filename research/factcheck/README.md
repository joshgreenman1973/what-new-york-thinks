# Blind fact-check, October 21, 2026

Every figure on the page was read again from the pollsters' own documents by checkers who were given only each poll's source links, the questions and the answer choices. They never saw the page's numbers, the research files or the live site (rules in INSTRUCTIONS.md). Their readings are in readings-<group>.json; compare.py lines them up against data/polls.json.

Result: 3,962 figures compared across all 23 polls, statewide and New York City columns. No figure on the page was wrong.

| Group | Figures | Match | Wrong |
|---|---|---|---|
| Siena, January-May (incl. NYCJI) | 1,024 | 1,024 | 0 |
| Siena, June-October | 808 | 808 | 0 |
| Marist | 315 | 315 | 0 |
| Quinnipiac | 310 | 310 | 0 |
| Emerson, Suffolk, Honan | 214 | 214 | 0 |
| Advocacy-paid polls | 932 | 932 | 0 |
| Main bars of folded questions (second pass) | 171 | 171 | 0 |
| Two advocacy polls added by the coverage pass | 195 | 195 | 0 |

Field dates, sample sizes and margins of error also matched for every poll. (The Business Council's release gives Tunnl's field dates as "March 11-15th" without a year; 2026 follows from its April 29, 2026 release date.)

**One error found and fixed, in the page's build, not the figures:** the build folds a pollster's "detailed version" of a question into the main row as its breakdown. For Marist's April New York City poll it matched by subject alone and attached the detailed trust-in-Mamdani table to the unite-or-divide question. The build now also matches by question wording; the corrected rows were re-read blind in the second pass.

**Places where pollsters' own release text differs from their tables** (the page follows the tables):
- Siena, September: Joseph Hernandez favorability, release 16-9-71, table 16-9-74 (noted on the row).
- Siena, August: comptroller race, release summary bullet says DiNapoli 56%, release body and table 55%.
- Marist, April: Mamdani "understands the problems facing New York City," release 61%, table 64% (noted on the row).
- Emerson, April: corporate tax question, release 44%, spreadsheet 43.5; Mamdani on the city budget, release 40%, spreadsheet 39.5. The page shows the spreadsheet figures with their decimal.
- Echelon/Tusk: three printed nets differ by one point from the sum of their parts (rounding in the pollster's tables).

Running `python3 compare.py` now prints 7 flags on marist-20260408-5 and -6. They are the first-pass readings of those two rows taken before the fix above (the checker read the trust table for row 5 because the bug had attached it there; its readings equal row 6's breakdown exactly). The second pass (readings-supplement.json) re-read both rows as they stand and matched.
