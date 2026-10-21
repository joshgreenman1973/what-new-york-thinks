# Blind fact-check: read poll figures from the source documents

You are an independent checker. Your input file lists polls and, for each, questions to read. It deliberately contains NO figures. Your job is to read every figure fresh from the pollster's own documents, so a separate comparison can catch errors in someone else's data.

## Rules (strict)
- Do NOT open, read, list or search any of these: anything under /Users/joshgreenman/Experiments (including what-new-york-thinks and mamdani-poll-tracker), anything under the scratchpad's `research/` or `pm-test/` folders, joshgreenman1973.github.io or vitalcity-nyc.github.io, Wikipedia, news coverage or aggregators. The ONLY sources are the URLs in your input file (release_url, tables_url) and links on those pages that lead to the same pollster's documents for the same poll (toplines, crosstabs, marginals, spreadsheets).
- Download into your own new folder: `mkdir -p "$BLIND_OUT/src"`. Use curl for PDFs and spreadsheets. Some sites (sri.siena.edu web pages, maristpoll.marist.edu pages, suffolk.edu) block curl; read those pages with WebFetch. Read PDFs with Python's PyMuPDF (`import fitz`); there is no pdftotext. Read .xlsx with openpyxl if available, else pandas.
- For each check, find the question and read the figure for EVERY answer label listed, in the column named (the total/topline column, or the New York City column of the crosstabs). In crosstabs, identify columns by the header positions on the page, not by counting values, because blank cells shift counts. Siena crosstabs: the NYC column sits under "Region".
- Record figures exactly as printed (keep decimals; "<1" or "*" as a string). If an answer label isn't printed, record null and say so. If a figure appears in both the release text and the tables and they differ, record both.
- For checks with `also_report`, also record those poll details as the pollster states them.
- Be thorough: read every check. If a document truly cannot be reached after two tries, mark those checks "unreachable" with the reason.

## Output
Write JSON to the path given in your task:
```json
{"checker": "<group>", "results": [
  {"check_id": "...", "figures": {"<answer label>": "<value as printed or null>", ...},
   "where": "document + page/table/row where you read it",
   "other_figures": {"release_text": {...}} ,
   "poll_details": {"field_start": "...", "field_end": "...", "n": ..., "moe": ..., "population": "..."},
   "status": "read" | "not found" | "unreachable", "note": "anything odd"}
]}
```
Validate it parses before finishing. Final reply: counts of read / not found / unreachable, and anything odd. Do not attempt to compare against any other data; you have none.
