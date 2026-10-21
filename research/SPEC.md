# Research spec: New York public opinion tracker

We are building one public page that collects every question asked of the public in independent polls of New York City and New York State about policy and politics: ratings of politicians (job approval, favorability, re-elect), election matchups (2026 governor race, primaries, Senate/House where polled statewide or citywide), right track/wrong track, and major issues (housing, rent, taxes, transit, congestion pricing, free buses, child care, crime and policing, immigration and ICE, schools, budget, Trump administration actions as they affect New York, ballot proposals, etc.).

Window: polls FIELDED from 2026-01-01 through today (2026-10-21).

## Rigor rules (non-negotiable)

1. Every number must come from a page or PDF you actually fetched in this session (WebFetch, or curl to download a PDF and then read it, e.g. with `pdftotext -layout` if available, or Python). Never reconstruct a URL or a number from memory or from news coverage alone.
2. Every question entry carries `quote`: verbatim text copied from the fetched source that contains the headline numbers (from the press release text or a crosstab line). If the numbers come only from a crosstab table, put the table row text verbatim in `quote` and set `source_kind: "crosstab"`.
3. Prefer the pollster's own release and crosstabs. If a poll's numbers are available only in news coverage, record it in `gaps` instead of `polls`, with the URL where you saw it.
4. Record exact question wording when the pollster publishes it. Otherwise null.
5. Report figures exactly as published (no rounding or combining) — except a `net` you may NOT compute; leave calculation to us.
6. If unsure of anything, say so in `notes`. Confidence per poll: HIGH = primary release/crosstabs fetched; MEDIUM = primary source fetched but some details (e.g. field dates) from elsewhere.

## Output

Write ONE JSON file to the path given in your task, shaped like this:

```json
{
  "agent": "<your task name>",
  "compiled": "2026-10-21",
  "polls": [
    {
      "poll_id": "siena-20260915",            // pollster slug + release date yyyymmdd
      "pollster": "Siena Research Institute",
      "sponsor": null,                         // media partner/client, e.g. "PIX11", "Spectrum News NY1"
      "geography": "New York State",          // or "New York City"
      "population": "RV",                      // "adults" | "RV" | "LV" | e.g. "likely Democratic primary voters"
      "n": 802, "moe": 4.3,
      "field_start": "2026-09-13", "field_end": "2026-09-17", "release_date": "2026-09-22",
      "mode": "phone and online panel",
      "url": "https://... (press release page)",
      "tables_url": "https://... (crosstabs PDF) or null",
      "confidence": "HIGH",
      "notes": "",
      "questions": [
        {
          "subject": "Kathy Hochul",            // the person, race or issue the question is about, short and consistent
          "subject_type": "person",             // person | race | issue | direction | institution
          "measure": "job approval",            // job approval | favorability | job performance | re-elect | horse race | primary | issue support | issue priority | direction | other
          "category": "Governor",               // see list below
          "wording": "verbatim question or null",
          "results": [ {"label": "Approve", "pct": 51}, {"label": "Disapprove", "pct": 45}, {"label": "Don't know/No opinion", "pct": 4} ],
          "nyc_results": null,                  // for STATEWIDE polls only: the New York City column from the crosstabs, same shape, or null if not read
          "population_note": null,              // if this question was asked of a subset (e.g. "Democrats only", "likely voters")
          "quote": "verbatim source text with the numbers",
          "source_kind": "release"              // release | crosstab
        }
      ]
    }
  ],
  "gaps": [ {"what": "...", "where_seen": "url", "why_excluded": "..."} ],
  "searches": ["list of searches and sites you checked"]
}
```

Categories (use these exact strings): Mayor, Governor, Other officials, Trump and Washington, 2026 governor race, Other 2026 races, Direction of state/city, Housing and rent, Taxes and budget, Transit and congestion pricing, Public safety and policing, Immigration, Schools and child care, Economy and cost of living, Health, Ballot proposals, Other issues.

Subject naming: use full names for people ("Zohran Mamdani", "Kathy Hochul", "Bruce Blakeman", "Chuck Schumer", "Kirsten Gillibrand", "Donald Trump", "Letitia James", "Antonio Delgado", "Jumaane Williams", "Hakeem Jeffries", "Alexandria Ocasio-Cortez", "Mark Levine", "Julie Menin", "Tom DiNapoli", "Carl Heastie", "Andrea Stewart-Cousins", etc.). For races: "2026 governor: Hochul vs. Blakeman" style. For issues: a short plain noun phrase ("Free buses", "Rent freeze on stabilized apartments", "Raising taxes on high earners", "Congestion pricing", "ICE enforcement in New York").

Capture EVERY question in each release that touches New York policy or politics — not just the headline. For horse races, record each candidate as a result row. For multi-item batteries (e.g. "how important is X"), make one question entry per item.

Be thorough but don't loop forever: if a source refuses to load after two tries, log it in `gaps` and move on. Validate your JSON file parses (`python3 -c "import json;json.load(open(PATH))"`) before finishing. Your final reply should be a short summary: how many polls, how many questions, notable gaps.
