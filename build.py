#!/usr/bin/env python3
"""Build the tracker's data files from the research files.

research/*.json  (one file per research pass, shape in research/SPEC.md)
  -> data/polls.json      one entry per poll, with its questions
  -> data/questions.csv   one row per question (and one per city column)
  -> data/meta.json       counts and dates the page writes into sentences

Run after any change to research/: python3 build.py
"""
import csv, json, glob, os, re, sys, urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
R = lambda *p: os.path.join(ROOT, *p)

CATEGORIES = ["Mayor", "Governor", "Other officials", "Trump and Washington",
              "2026 governor race", "Other 2026 races", "Direction of state/city",
              "Housing and rent", "Taxes and budget", "Transit and congestion pricing",
              "Public safety and policing", "Immigration", "Schools and child care",
              "Economy and cost of living", "Health", "Ballot proposals", "Other issues"]

# Short names used on the page. Anything not listed keeps its full name.
SHORT = [
    (r"siena", "Siena"), (r"marist", "Marist"), (r"quinnipiac", "Quinnipiac"),
    (r"emerson", "Emerson"), (r"suffolk", "Suffolk"), (r"honan", "Honan"),
    (r"manhattan institute", "Manhattan Institute"), (r"data for progress", "Data for Progress"),
    (r"slingshot", "Slingshot"), (r"change research", "Change Research"),
    (r"public policy polling", "PPP"), (r"echelon", "Echelon"), (r"co/efficient", "co/efficient"),
    (r"gotham", "Gotham"), (r"yougov", "YouGov"), (r"surveyusa", "SurveyUSA"),
]

POP = {"rv": "registered voters", "lv": "likely voters", "adults": "adults",
       "adult": "adults", "residents": "adults"}


def short_name(full):
    for pat, s in SHORT:
        if re.search(pat, full or "", re.I):
            return s
    return full


def pop_label(p):
    if not p:
        return None
    k = p.strip().lower()
    for key, lab in POP.items():
        if k == key or k.endswith(" " + key) or k == "nys " + key:
            return lab
    return p


def clean_results(rs):
    out = []
    for r in rs or []:
        if r is None or r.get("pct") is None or r.get("label") in (None, ""):
            continue
        raw = str(r["pct"]).strip()
        if raw in ("<1", "<0.5", "*"):
            out.append({"label": str(r["label"]).strip(), "pct": 0, "shown": "<1"})
            continue
        try:
            pct = float(raw)
        except ValueError:
            continue
        out.append({"label": str(r["label"]).strip(), "pct": int(pct) if pct == int(pct) else pct})
    return out


STRENGTH = re.compile(r"^(strongly|somewhat|just|very|not so|not at all)\b", re.I)


def collapse(res):
    """Where a pollster prints "Total approve" beside the strongly/somewhat rows,
    the bar shows the totals and the don't-knows; the full breakdown is kept for the detail view."""
    if not any(x["label"].lower().startswith("total ") for x in res):
        return res, None
    main = []
    for x in res:
        if x["label"].lower().startswith("total "):
            main.append(dict(x, label=x["label"][6:].strip().capitalize()))
        elif not STRENGTH.match(x["label"]):
            main.append(x)
    return main, res


NOTE_ONLY = re.compile(r"completed the full survey|column order|all adults shown|release text|version|crosstab|table [A-Z]", re.I)
ITEM = re.compile(r"^(trait( statement)?|better job on|item)\s*:\s*", re.I)
VERSION = re.compile(r"^(intensity|detailed|combined|follow-up) version", re.I)


def split_note(q):
    """population_note was used by the research passes for three things.
    Returns (item, asked_of, note)."""
    item = q.get("item")
    n = (q.get("population_note") or "").strip()
    if not n:
        return item, None, None
    if ITEM.match(n):
        it = ITEM.sub("", n).strip()
        extra = None
        if " (" in it:  # a research note in parentheses after the item
            it, extra = it.split(" (", 1)
            extra = extra.rstrip(")")
        return item or it[0].upper() + it[1:], None, extra
    if NOTE_ONLY.search(n):
        return item, None, n
    return item, n, None


# The research passes named some subjects differently; these make the same question group together.
ALIAS = {
    "Hochul vs. Blakeman": "2026 governor: Hochul vs. Blakeman",
    "2026 U.S. House generic ballot in New York": "2026 U.S. House generic ballot",
    "Generic congressional ballot": "2026 U.S. House generic ballot",
    "U.S. direction": "Direction of the country", "United States direction": "Direction of the country",
    "Direction of New York City": "New York City direction",
    "Most important issue facing New Yorkers": "Most important issue facing New York",
    "Trump handling": "Donald Trump",
    "Statement": "Statements about injury lawyers' contingent fees",
    "One-year moratorium on new large data centers": "Data center moratorium",
    "Hochul one-year moratorium on new state environmental permits for large data centers": "Data center moratorium",
}
DIRECTION_ON = re.compile(r"^(New York State|U\.S\.) direction on (.+)$")


ANNOT = re.compile(r"\s*\[((?:NYC|Crosstab|Full list)[^\]]*)\]")


def split_quote(text):
    """One pass appended crosstab readings to the release quote in [brackets].
    Keep the release text verbatim and put those readings in their own field."""
    extra = [m.strip() for m in ANNOT.findall(text or "")]
    return ANNOT.sub("", text or "").strip(), ("; ".join(extra) or None)


def split_subject(q):
    """Some passes wrote "Kathy Hochul: honest" as the subject; make that subject + item."""
    s = q.get("subject") or ""
    m = DIRECTION_ON.match(s)
    if m and not q.get("item"):
        q["subject"] = "New York State direction" if m.group(1) == "New York State" else "Direction of the country"
        q["item"] = "On " + m.group(2)
        return q
    if s in ALIAS:
        q["subject"] = s = ALIAS[s]
    if ": " in s and not s.startswith("2026 ") and not q.get("item"):
        a, b = s.split(": ", 1)
        q["subject"], q["item"] = ALIAS.get(a.strip(), a.strip()), b.strip()[0].upper() + b.strip()[1:]
    return q


def load_research():
    polls = {}
    gaps, problems = [], []
    for f in sorted(glob.glob(R("research", "*.json"))):
        try:
            doc = json.load(open(f))
        except Exception as e:
            problems.append(f"{os.path.basename(f)}: does not parse ({e})")
            continue
        gaps += [dict(g, file=os.path.basename(f)) for g in doc.get("gaps", [])]
        for p in doc.get("polls", []):
            pid = p.get("poll_id")
            if not pid:
                problems.append(f"{os.path.basename(f)}: a poll has no poll_id")
                continue
            p = dict(p, research_file=os.path.basename(f))
            if pid in polls:
                # Same poll found by two passes: keep the first, add questions it lacks.
                have = {(q.get("subject"), q.get("measure"), q.get("wording")) for q in polls[pid]["questions"]}
                for q in p.get("questions", []):
                    if (q.get("subject"), q.get("measure"), q.get("wording")) not in have:
                        polls[pid]["questions"].append(q)
            else:
                polls[pid] = p
    return polls, gaps, problems


def check_poll(p, problems):
    pid = p["poll_id"]
    for k in ("pollster", "url", "field_end", "geography"):
        if not p.get(k):
            problems.append(f"{pid}: missing {k}")
    for i, q in enumerate(p.get("questions", [])):
        if not q.get("quote"):
            problems.append(f"{pid} q{i} ({q.get('subject')}): no quote")
        if q.get("category") not in CATEGORIES:
            problems.append(f"{pid} q{i}: category {q.get('category')!r} not in list; filed under Other issues")
            q["category"] = "Other issues"
        if not clean_results(q.get("results")):
            problems.append(f"{pid} q{i} ({q.get('subject')}): no usable results")


def main():
    polls, gaps, problems = load_research()
    rows, out_polls = [], []
    for pid in sorted(polls, key=lambda k: (polls[k].get("field_end") or "", k), reverse=True):
        p = polls[pid]
        check_poll(p, problems)
        if p.get("field_end", "") < "2026-01-01":
            continue
        if p.get("exclude"):
            gaps.append({"what": f"{p.get('pollster')}, fielded {p.get('field_start')} to {p.get('field_end')}",
                         "where_seen": p.get("url"), "why_excluded": p["exclude"], "file": p["research_file"]})
            continue
        base = {
            "poll_id": pid,
            "pollster": short_name(p.get("pollster")),
            "pollster_full": p.get("pollster"),
            "sponsor": p.get("sponsor"),
            "sponsor_type": p.get("sponsor_type") or "independent",
            "field_start": p.get("field_start"), "field_end": p.get("field_end"),
            "release_date": p.get("release_date"),
            "n": p.get("n"), "moe": p.get("moe"), "mode": p.get("mode"),
            "url": p.get("url"), "tables_url": p.get("tables_url"),
            "confidence": p.get("confidence"),
        }
        qs = []
        questions = [split_subject(dict(q)) for q in p.get("questions", [])]
        # A "detailed version" of a question already in the poll becomes that question's breakdown.
        for q in questions:
            if VERSION.match(q.get("population_note") or ""):
                twin = next((t for t in questions if t is not q and not VERSION.match(t.get("population_note") or "")
                             and t.get("subject") == q.get("subject") and t.get("measure") == q.get("measure")
                             and t.get("item") == q.get("item")
                             and (t.get("wording") or "")[:40].lower() == (q.get("wording") or "")[:40].lower()), None)
                if twin:
                    twin["_breakdown"], twin["_breakdown_nyc"] = q.get("results"), q.get("nyc_results")
                    q["_drop"] = True
        for i, q in enumerate(questions):
            if q.get("_drop"):
                continue
            res = clean_results(q.get("results"))
            if not res:
                continue
            item, asked_of, note = split_note(q)
            common = dict(base,
                          subject=q.get("subject"), subject_type=q.get("subject_type"),
                          item=item, asked_of=asked_of, note=note,
                          measure=q.get("measure"), category=q.get("category"),
                          wording=q.get("wording"),
                          quote=split_quote(q.get("quote"))[0], quote_tables=split_quote(q.get("quote"))[1],
                          source_kind=q.get("source_kind") or "release")
            res, brk = collapse(res)
            if q.get("_breakdown"):
                brk = clean_results(q["_breakdown"])
            rows.append(dict(common, id=f"{pid}-{i}", geography=p.get("geography"),
                             population=pop_label(p.get("population")), city_column=False,
                             results=res, breakdown=brk))
            nyc, nbrk = collapse(clean_results(q.get("nyc_results")))
            if q.get("_breakdown_nyc"):
                nbrk = clean_results(q["_breakdown_nyc"])
            if nyc and p.get("geography") == "New York State":
                rows.append(dict(common, id=f"{pid}-{i}c", geography="New York City",
                                 population=pop_label(p.get("population")), city_column=True,
                                 results=nyc, breakdown=nbrk, source_kind="crosstab", n=None, moe=None))
            qs.append(i)
        out_polls.append(dict(base, geography=p.get("geography"), population=pop_label(p.get("population")),
                              notes=p.get("notes"), questions=len(qs)))

    rows.sort(key=lambda r: (r["field_end"] or "", r["id"]), reverse=True)
    json.dump({"built": date.today().isoformat(), "categories": CATEGORIES,
               "polls": out_polls, "questions": rows},
              open(R("data", "polls.json"), "w"), ensure_ascii=False, indent=1)

    with open(R("data", "questions.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["field_start", "field_end", "pollster", "sponsor", "geography", "city_column_of_statewide_poll",
                    "population", "n", "moe", "category", "subject", "item", "asked_of", "measure", "wording", "results", "source_url", "tables_url"])
        for r in rows:
            w.writerow([r["field_start"], r["field_end"], r["pollster"], r["sponsor"] or "", r["geography"],
                        "yes" if r["city_column"] else "no", r["population"], r["n"] or "", r["moe"] or "",
                        r["category"], r["subject"], r["item"] or "", r["asked_of"] or "", r["measure"], r["wording"] or "",
                        "; ".join(f"{x['label']} {x.get('shown', x['pct'])}" for x in (r["breakdown"] or r["results"])), r["url"], r["tables_url"] or ""])

    json.dump(gaps, open(R("data", "gaps.json"), "w"), ensure_ascii=False, indent=1)

    # Snapshot of the prediction-market tracker, used only if the live file can't be reached.
    try:
        live = urllib.request.urlopen("https://joshgreenman1973.github.io/experiments/nyc-prediction-markets/data/markets.json", timeout=30).read()
        json.loads(live)
        open(R("data", "markets-snapshot.json"), "wb").write(live)
    except Exception as e:
        problems.append(f"market snapshot not refreshed: {e}")

    ind = [r for r in rows if r["sponsor_type"] == "independent"]
    pollsters = sorted({r["pollster"] for r in ind})
    meta = {"polls": len({r["poll_id"] for r in ind}), "questions": sum(1 for r in ind if not r["city_column"]),
            "city_columns": sum(1 for r in ind if r["city_column"]), "pollsters": pollsters,
            "advocacy_polls": len({r["poll_id"] for r in rows if r["sponsor_type"] != "independent"}),
            "advocacy_questions": sum(1 for r in rows if r["sponsor_type"] != "independent" and not r["city_column"]),
            "first_field": min((r["field_start"] or r["field_end"] for r in ind), default=None),
            "last_field": max((r["field_end"] for r in ind), default=None)}
    json.dump(meta, open(R("data", "meta.json"), "w"), indent=1)

    print(json.dumps(meta, indent=1))
    if problems:
        print(f"\n{len(problems)} problems:")
        for x in problems:
            print("  -", x)


if __name__ == "__main__":
    main()
