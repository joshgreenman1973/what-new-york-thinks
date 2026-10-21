
Running `python3 compare.py` now prints 7 flags on marist-20260408-5 and -6. They are the first-pass readings of those two rows taken before the fix above (the checker read the trust table for row 5 because the bug had attached it there; its readings equal row 6's breakdown exactly). The second pass (readings-supplement.json) re-read both rows as they stand and matched.
