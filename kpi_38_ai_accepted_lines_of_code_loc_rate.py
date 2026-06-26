"""
KPI #38 - AI-Accepted Lines of Code (LOC) Rate
===============================================
Of every line Copilot SUGGESTED, what share did developers ACCEPT?
    rate = accepted LOC / suggested LOC * 100

FLOW (top to bottom):
    1. Get the GitHub token + org name from secrets.
    2. Download two Copilot reports: org-wide totals and per-user activity.
    3. Drop broken features that report accepted lines but no suggested ones
       (they fake rates above 100%). The list is in _STRIP_FEATURES.
    4. Add up accepted lines (top) and suggested lines (bottom).
    5. rate = accepted / suggested * 100, then label it POOR..EXCELLENT.
    6. Print the breakdown tables (feature, developer, timeline, language).
    7. Auto-find the timeline users from the report and save them for auditing.

HOW EACH BREAKDOWN TABLE IS BUILT (step 6 in detail):
    Every table uses the same two-stage engine, then changes only WHAT it groups by:
      - _walk_feature_entries(record, array) -> reads (feature, language,
        suggested, accepted) from one record and drops broken features.
      - _tally(records, array, group_of)     -> sums suggested/accepted into
        buckets; group_of(record, feature, language) picks the bucket.

    6.1  PER-FEATURE breakdown  (source: org-28-day report)
         a) The org report has 28 day_totals[] (one per day, 1st..28th).
         b) Each day holds totals_by_feature[] (code_completion, chat_*, ...).
         c) We walk all 28 days and SUM suggested/accepted per FEATURE name,
            so each feature's 28 daily numbers collapse into one running total.
         d) One row per feature, sorted by accepted DESC, + a Rate->Band line.
         e) Answers: "which Copilot feature gets accepted the most?"

    6.2  PER-DEVELOPER breakdown  (source: users-28-day report)
         a) The users report has one record per user per active day.
         b) Each record holds the SAME totals_by_feature[] array as the org one.
         c) We walk every record and SUM suggested/accepted per USER_LOGIN
            (group by the person instead of the feature).
         d) One row per developer, sorted by accepted DESC, + a Rate->Band line.
         e) Answers: "which developer accepts the most?"  Same layout as 6.1.

    6.3  PER-USER TIMELINE  (source: users-28-day report, one table per dev)
         a) Filter the users rows to a single user_login.
         b) Sort that user's records by day (chronological).
         c) For each day, SUM its totals_by_feature[] -> that day's two numbers.
         d) One row per DAY (not per feature); TOTAL row sums the whole window.
         e) Answers: "how did this one developer trend day by day?"

    6.4  PER-LANGUAGE breakdown  (source: users-28-day report, one table per lang)
         a) Use totals_by_language_feature[] (the only array carrying a language).
         b) SUM suggested/accepted per (LANGUAGE, USER) pair -> one shared matrix.
         c) Discover the languages from the data (no hardcoded list), alphabetical.
         d) For each language, slice out its users and print a table: one row per
            user, sorted by accepted DESC. Two-level split: language -> user.
         e) Answers: "per language, who accepts the most?"

    6.5  PER-LANGUAGE x PER-USER matrix  (optional; same data as 6.4)
         a) Reuses the exact (language, user) buckets from 6.4.
         b) Prints them ALL in one flat table with per-language subtotals and a
            grand total, instead of a separate table per language.

DATA FLOW
                 GitHub Copilot REST API (org, 28-day reports)
                                 |
                 +---------------+----------------+
                 |                                |
            org-28-day                       users-28-day
        (daily org totals)             (per-user-per-day rows)
                 |                                |
   extract_accepted_loc / suggested      extract_users_stash
                 |                          |  saves users_28day_raw.json
                 |                          |        + timeline_users.json
            _LAST_ORG_RAW               _LAST_USERS_RAW
                 |                                |
                 +---------------+----------------+
                                 v
                compute() = accepted / suggested * 100
                                 v
                           REPORT TABLES

REPORT LAYOUT (output order)
    1. Headline KPI                              <- org report   (run_kpi)
    2. PER-FEATURE breakdown      + band line    <- org report
    3. PER-DEVELOPER breakdown    + band line    <- users report
    4. PER-USER timelines (one table per dev)    <- users report
    5. PER-LANGUAGE tables (one table per lang)  <- users report
    6. PER-LANGUAGE x PER-USER matrix [optional] <- users report

KEY BUG WE FIXED:
    Some Copilot features (agent_edit, copilot_cli, agent-mode...) write code
    directly instead of showing inline "ghost text", so the API reports ACCEPTED
    lines (loc_added_sum) but ZERO SUGGESTED lines. Counting them inflates the
    rate above 100% (e.g. fake 248% / 933%). We strip them via _STRIP_FEATURES,
    applied in exactly ONE place (_walk_feature_entries) so every table agrees.
"""
import datetime
import html
import json
import os

from _toolkit import Datapoint, cfg, gh_report, run_kpi

# ============================================================================
# SECTION 1 - CONFIGURATION (edit these without touching code logic)
# ============================================================================
TOOL = "github-copilot"
_STRIP_FEATURES = {"agent_edit", "chat_panel_custom_mode", "copilot_cli"}  # broken: excluded everywhere

# Per-user timeline tables:
#   AUTO_TIMELINE_USERS=True  -> auto-populate from every active user in the live
#       users-28-day report (the manual list below is ignored). The raw JSON and
#       the discovered user list are saved to ARTIFACT_DIR for auditing.
#   AUTO_TIMELINE_USERS=False -> use the hardcoded TIMELINE_USERS list (or ["*"]).
AUTO_TIMELINE_USERS = True
ARTIFACT_DIR = r"\\172.27.59.130\Users\ruturajkh\Desktop\sharable"
TIMELINE_USERS = []  # manual fallback, e.g. ["pranavjames", "shubhamchav"]


# ============================================================================
# SECTION 2 - KPI METADATA (printed by run_kpi as the report header)
# ============================================================================
KPI = {
    "num": 38,
    "name": "AI-Accepted Lines of Code (LOC) Rate",
    "index": "Utilization",
    "definition": "% of AI-suggested lines of code that developers accept and retain.",
    "how_measured": "accepted LOC / suggested LOC * 100 per sprint, per language, per dev.",
    "formula": "(AI-accepted LOC / AI-suggested LOC) x 100",
    "unit": "%", "cadence": "Weekly",
    "interpretation": "<15%=Poor; 15-25%=Industry average; 25-35%=Good; >35%=Excellent",
    "tools": "GitHub Copilot",
    "plain": "Of every line of code Copilot offered, what share did developers accept?",
    "steps": [
        "Fetch the org 28-day report.",
        "Sum loc_added_sum across day_totals[].totals_by_feature[] -> numerator.",
        "Sum loc_suggested_to_add_sum across same path -> denominator.",
        "Result = numerator / denominator * 100.",
    ],
}


# ============================================================================
# SECTION 3 - API FETCHES (two endpoints, both gzipped JSON via signed links)
# ============================================================================
async def _fetch(client, path):
    """Shared GitHub caller - reads token+org from secrets, returns parsed JSON."""
    token, org = cfg(TOOL, "githubKey"), cfg(TOOL, "org")
    if not token or not org:
        raise RuntimeError("Set tools.github-copilot.githubKey AND .org in secrets")
    return await gh_report(client, f"/orgs/{org}{path}", token=token)


async def fetch_org_report(client):
    """Org-wide daily totals -> headline KPI + feature table."""
    return await _fetch(client, "/copilot/metrics/reports/organization-28-day/latest")


async def fetch_users_report(client):
    """One record per user per day -> timelines + developer/language tables."""
    return await _fetch(client, "/copilot/metrics/reports/users-28-day/latest")


# ============================================================================
# SECTION 4 - CORE HELPERS (the whole script is built on these three)
# ============================================================================
# _walk_feature_entries is the ONE place agent_edit/broken features get stripped,
# so every table and the headline KPI stay consistent. _tally aggregates over it.
def _walk_feature_entries(record, array_key):
    """Yield (feature, language, suggested, accepted) from record[array_key],
    skipping stripped features. Both totals_by_feature[] and
    totals_by_language_feature[] entries share this shape."""
    if not isinstance(record, dict):
        return
    for e in record.get(array_key) or []:
        if not isinstance(e, dict) or e.get("feature") in _STRIP_FEATURES:
            continue
        yield (e.get("feature"), e.get("language"),
               e.get("loc_suggested_to_add_sum") or 0,
               e.get("loc_added_sum") or 0)


def _tally(records, array_key, group_of):
    """Aggregate -> {group: {"s": suggested, "a": accepted}}.
    group_of(record, feature, language) returns the group key, or None to skip."""
    out = {}
    for rec in records or []:
        for feat, lang, sugg, acc in _walk_feature_entries(rec, array_key):
            g = group_of(rec, feat, lang)
            if g is None:
                continue
            slot = out.setdefault(g, {"s": 0, "a": 0})
            slot["s"] += sugg
            slot["a"] += acc
    return out


def _rate(sugg, acc, width=5):
    """Format an acceptance rate, or right-aligned 'n/a' when nothing suggested."""
    return f"{(acc / sugg * 100):>{width}.1f}%" if sugg > 0 else f"{'n/a':>{width + 1}}"


def _band(rate):
    """Numeric rate -> POOR / INDUSTRY AVERAGE / GOOD / EXCELLENT."""
    if rate < 15: return "POOR"
    if rate < 25: return "INDUSTRY AVERAGE"
    if rate < 35: return "GOOD"
    return "EXCELLENT"


def _interp(sugg, acc):
    """Interpretation band from suggested/accepted, per the KPI definition:
    <15%=Poor; 15-25%=Industry average; 25-35%=Good; >35%=Excellent."""
    if sugg <= 0:
        return "n/a"
    r = acc / sugg * 100
    if r < 15: return "Poor"
    if r < 25: return "Industry average"
    if r < 35: return "Good"
    return "Excellent"


# ============================================================================
# SECTION 5 - EXTRACTORS + FORMULA
# ============================================================================
# run_kpi expects each extractor to return ONE number, but the tables need the
# full raw payload. So extractors stash the raw data into these dicts as a side
# effect, and the table printers read from them (no re-fetching).
_LAST_ORG_RAW = {}    # {"report": <org 28-day report>}
_LAST_USERS_RAW = {}  # {"rows": [...], "users": [...]}


def _org_feature_totals(report):
    """{feature: {s, a}} from the org report's day_totals[].totals_by_feature[]."""
    days = report.get("day_totals") if isinstance(report, dict) else None
    return _tally(days, "totals_by_feature", lambda rec, f, l: f or "unknown")


def extract_accepted_loc(raw):
    _LAST_ORG_RAW["report"] = raw
    t = _org_feature_totals(raw)
    return sum(v["a"] for v in t.values()) if t else None


def extract_suggested_loc(raw):
    _LAST_ORG_RAW["report"] = raw
    t = _org_feature_totals(raw)
    return sum(v["s"] for v in t.values()) if t else None


def _unique_users(rows):
    """Distinct user_login values, sorted alphabetically."""
    return sorted({r.get("user_login") for r in rows
                   if isinstance(r, dict) and r.get("user_login")})


def _save_users_artifacts(rows):
    """Save the raw users report + discovered user list to ARTIFACT_DIR (audit
    trail; failures are non-fatal). Returns the user list and caches it."""
    users = _unique_users(rows)
    _LAST_USERS_RAW["users"] = users
    try:
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        raw_path = os.path.join(ARTIFACT_DIR, "users_28day_raw.json")
        users_path = os.path.join(ARTIFACT_DIR, "timeline_users.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        print(f"  [saved] {len(rows)} rows -> {raw_path}")
        print(f"  [saved] {len(users)} unique users -> {users_path}")
    except Exception as e:  # noqa: BLE001 - artifact save is best-effort
        print(f"  (could not save users artifacts to {ARTIFACT_DIR}: {e})")
    return users


def extract_users_stash(raw):
    """Stash per-user rows + auto-discover/save the user list."""
    rows = raw if isinstance(raw, list) else (raw.get("rows") or raw.get("data") or [])
    _LAST_USERS_RAW["rows"] = rows
    _save_users_artifacts(rows)
    return float(len(rows)) if rows else None  # filler number for the 3rd datapoint


def compute(accepted, suggested, _row_count=None):
    """The KPI formula. _row_count exists only to consume the 3rd datapoint."""
    if accepted is None or not suggested:
        return None
    return accepted / suggested * 100


# ============================================================================
# SECTION 6 - TABLE RENDERING (one renderer + one breakdown helper)
# ============================================================================
def _print_table(title, headers, rows, total_sugg, total_acc, width=62):
    """Generic ASCII table: title, header row, body rows, TOTAL row."""
    print()
    print("+" + "-" * width + "+")
    print("|" + f"  {title}".ljust(width) + "|")
    print("+" + "-" * width + "+")
    print("| " + headers + " |")
    print("|" + "-" * width + "|")
    for row in rows:
        print("| " + row + " |")
    print("|" + "-" * width + "|")
    print(f"| {'TOTAL':<22} {total_sugg:>10} {total_acc:>10} {_rate(total_sugg, total_acc):>14} |")
    print("+" + "-" * width + "+")


def _print_breakdown(title, label_head, totals, band=True, drop_empty=True, label_w=26):
    """Render {name: {s, a}} as a breakdown table sorted by accepted DESC, then
    suggested DESC. Optionally append a 'Rate -> Band' line; optionally hide rows
    with no activity at all."""
    if drop_empty:
        totals = {k: v for k, v in totals.items() if v["s"] or v["a"]}
    if not totals:
        return
    rows, ts, ta = [], 0, 0
    for name, v in sorted(totals.items(), key=lambda kv: (-kv[1]["a"], -kv[1]["s"])):
        rows.append(f"{str(name):<{label_w}} {v['s']:>10} {v['a']:>10} {_rate(v['s'], v['a']):>14}")
        ts += v["s"]
        ta += v["a"]
    _print_table(title, f"{label_head:<{label_w}} {'Suggested':>10} {'Accepted':>10} {'Rate':>14}",
                 rows, ts, ta)
    if band and ts > 0:
        rate = ta / ts * 100
        print(f"\n  Rate: {rate:.2f}%  ->  Band: {_band(rate)}\n")


# ============================================================================
# SECTION 7 - TABLES (each is a few lines thanks to _tally + _print_breakdown)
# ============================================================================
def print_developer_breakdown_table():
    """Table #1b: which developer accepts most (users report). Same shape as #1."""
    rows = _LAST_USERS_RAW.get("rows")
    totals = _tally(rows, "totals_by_feature", lambda rec, f, l: rec.get("user_login"))
    _print_breakdown("PER-DEVELOPER BREAKDOWN (28-day window)", "Developer", totals)


# ----------------------------------------------------------------------------
# EXPORTS
#   1. JSON   : per-developer breakdown data -> kpi_38_tables.json
#   2. PDF    : via the shared export_pdf.py pipeline. run_kpi writes a run
#               "envelope" to docs/reports/_data/; `--pdf` renders it to HTML+PDF
#               with headless Edge. We expose report_sections() below so the PDF
#               shows our rich developer table instead of a raw dump.
# ----------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
BREAKDOWN_JSON_PATH = os.path.join(_HERE, "kpi_38_tables.json")


def _breakdown_json(title, label_field, totals, drop_empty=True):
    """Turn a {name: {s, a}} breakdown into a JSON-ready dict (rows + total),
    sorted by accepted DESC then suggested DESC - mirrors the printed table."""
    rows, ts, ta = [], 0, 0
    for name, v in sorted(totals.items(), key=lambda kv: (-kv[1]["a"], -kv[1]["s"])):
        if drop_empty and not (v["s"] or v["a"]):
            continue
        rate = round(v["a"] / v["s"] * 100, 1) if v["s"] else None
        rows.append({label_field: str(name), "suggested": v["s"], "accepted": v["a"], "rate_pct": rate})
        ts += v["s"]
        ta += v["a"]
    return {"title": title, "label_field": label_field, "rows": rows,
            "total": {"suggested": ts, "accepted": ta,
                      "rate_pct": round(ta / ts * 100, 1) if ts else None}}


def _build_breakdowns(users_rows):
    """The per-developer breakdown table from raw report data. Pure: takes the
    raw payload, so it works from module globals OR a saved envelope
    (report_sections runs in a fresh import with no globals)."""
    developer = _tally(users_rows,
                       "totals_by_feature", lambda rec, f, l: rec.get("user_login"))
    return [
        _breakdown_json("PER-DEVELOPER BREAKDOWN (28-day window)", "developer", developer),
    ]


def export_breakdowns_json():
    """Write the per-developer breakdown DATA to one JSON file."""
    tables = _build_breakdowns(_LAST_USERS_RAW.get("rows"))
    try:
        with open(BREAKDOWN_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(tables, f, indent=2, ensure_ascii=False)
        print(f"  [saved] developer breakdown -> {BREAKDOWN_JSON_PATH}")
    except Exception as e:  # noqa: BLE001 - JSON export is best-effort
        print(f"  (could not write {BREAKDOWN_JSON_PATH}: {e})")


def _html_ratio(s, a):
    return f"{a / s * 100:.1f}%" if s > 0 else ""        # blank instead of n/a in the report


def _html_interp(s, a):
    return _interp(s, a) if s > 0 else ""                # blank instead of n/a in the report


def _grouped_html(head1, head2, groups):
    """HTML for a two-label grouped breakdown (group label printed once per group)
    with a TOTAL row, including an Interpretation column. Uses .grid/.num CSS."""
    body, gs, ga = [], 0, 0
    for glabel, items in groups:
        first = True
        for item, s, a in items:
            c1 = html.escape(str(glabel)) if first else ""
            first = False
            body.append(f"<tr><td>{c1}</td><td>{html.escape(str(item))}</td>"
                        f"<td class='num'>{s}</td><td class='num'>{a}</td>"
                        f"<td class='num'>{_html_ratio(s, a)}</td><td>{_html_interp(s, a)}</td></tr>")
            gs += s
            ga += a
    head = (f"<tr><th>{html.escape(head1)}</th><th>{html.escape(head2)}</th>"
            f"<th class='num'>Suggested</th><th class='num'>Accepted</th>"
            f"<th class='num'>Ratio</th><th>Interpretation</th></tr>")
    foot = (f"<tfoot><tr><td>TOTAL</td><td></td><td class='num'>{gs}</td>"
            f"<td class='num'>{ga}</td><td class='num'>{_html_ratio(gs, ga)}</td>"
            f"<td>{_interp(gs, ga)}</td></tr></tfoot>")
    return f"<table class='grid'><thead>{head}</thead><tbody>{''.join(body)}</tbody>{foot}</table>"


def _sprint_summary_html(windows):
    """HTML for the per-sprint totals table (one row per 14-day sprint), with
    Start/End date and Interpretation columns."""
    body, ts, ta = [], 0, 0
    for i, (_, start, end, wrows) in enumerate(windows, 1):
        t = _tally(wrows, "totals_by_feature", lambda rec, f, l: "x").get("x", {"s": 0, "a": 0})
        s, a = t["s"], t["a"]
        body.append(f"<tr><td>sprint-{i}</td><td>{html.escape(str(start))}</td>"
                    f"<td>{html.escape(str(end))}</td><td class='num'>{s}</td>"
                    f"<td class='num'>{a}</td><td class='num'>{_html_ratio(s, a)}</td>"
                    f"<td>{_interp(s, a)}</td></tr>")
        ts += s
        ta += a
    head = ("<tr><th>Sprint</th><th>Start Date</th><th>End Date</th>"
            "<th class='num'>Suggested</th><th class='num'>Accepted</th>"
            "<th class='num'>Ratio</th><th>Interpretation</th></tr>")
    foot = (f"<tfoot><tr><td>TOTAL</td><td></td><td></td><td class='num'>{ts}</td>"
            f"<td class='num'>{ta}</td><td class='num'>{_html_ratio(ts, ta)}</td>"
            f"<td>{_interp(ts, ta)}</td></tr></tfoot>")
    return f"<table class='grid'><thead>{head}</thead><tbody>{''.join(body)}</tbody>{foot}</table>"


def report_sections(env):
    """export_pdf.py hook: return [(title, html), ...] for the PDF body, MIRRORING
    the terminal output - a sprint summary, then per-sprint dev->language and
    language->developer tables. Reads the users rows from the run ENVELOPE
    (datapoint 2), since this runs in a fresh import with no module globals."""
    dps = env.get("datapoints") or []
    users_raw = dps[2].get("raw") if len(dps) > 2 else None
    rows = users_raw if isinstance(users_raw, list) else \
        ((users_raw or {}).get("rows") or (users_raw or {}).get("data") or [])
    windows = _sprint_windows(rows)
    sections = [("Sprint summary (two 14-day sprints)", _sprint_summary_html(windows))]
    for label, _start, _end, wrows in windows:
        sections.append((label,
                         _grouped_html("Developer", "Language", _dev_lang_groups(wrows))))
    sections.append(("Note",
                     "<p>Features like Agent_edit and chat_panel_custom_mode are "
                     "excluded from  LOC_Accepted and LOC_Suggested metrics</p>"))
    return sections


def print_user_timeline(user):
    """Table #2: one developer's day-by-day suggested/accepted."""
    rows = [r for r in (_LAST_USERS_RAW.get("rows") or [])
            if isinstance(r, dict) and r.get("user_login") == user]
    if not rows:
        print(f"\n  (no timeline data for '{user}')")
        return
    rows.sort(key=lambda r: r.get("day") or "")
    table_rows, total_s, total_a = [], 0, 0
    for r in rows:
        day = r.get("day") or "????-??-??"
        per_day = _tally([r], "totals_by_feature", lambda rec, f, l: "x").get("x", {"s": 0, "a": 0})
        s, a = per_day["s"], per_day["a"]
        table_rows.append(f"{day:<22} {s:>10} {a:>10} {_rate(s, a):>14}")
        total_s += s
        total_a += a
    _print_table(f"TIMELINE -- {user}",
                 f"{'Day':<22} {'Suggested':>10} {'Accepted':>10} {'Rate':>14}",
                 table_rows, total_s, total_a)


def print_all_timelines():
    """Table #2 driver: resolve the user list, then print one timeline each."""
    rows = _LAST_USERS_RAW.get("rows") or []
    if not rows:
        print("\n  (no per-user data fetched)")
        return
    if AUTO_TIMELINE_USERS or TIMELINE_USERS == ["*"]:
        users = _LAST_USERS_RAW.get("users") or _unique_users(rows)
    else:
        users = TIMELINE_USERS
    print("\n" + "=" * 64)
    print("  PER-USER TIMELINES (28-day window)")
    print("=" * 64)
    for u in users:
        print_user_timeline(u)


def _lang_user_matrix(rows):
    """{(language, user): {s, a}} from totals_by_language_feature[]."""
    return _tally(rows, "totals_by_language_feature",
                  lambda rec, f, l: (l, rec.get("user_login"))
                  if l and rec.get("user_login") else None)


def print_all_language_tables():
    """Table #3: one per-user table per language (alphabetical)."""
    matrix = _lang_user_matrix(_LAST_USERS_RAW.get("rows") or [])
    if not matrix:
        return
    languages = sorted({lang for lang, _ in matrix})
    print("\n" + "=" * 64)
    print(f"  PER-LANGUAGE BREAKDOWN ({len(languages)} languages found, alphabetical)")
    print(f"  {', '.join(languages)}")
    print("=" * 64)
    for lang in languages:
        per_user = {user: v for (l, user), v in matrix.items() if l == lang}
        _print_breakdown(f"LANGUAGE: {lang}", "User", per_user, band=False, label_w=22)


def print_language_user_matrix(width=64):
    """Table #4: every (language, user) pair in ONE table, grouped by language,
    with per-language subtotals and a grand total."""
    matrix = _lang_user_matrix(_LAST_USERS_RAW.get("rows") or [])
    if not matrix:
        return
    print("\n" + "+" + "-" * width + "+")
    print("|" + "  PER-LANGUAGE x PER-USER MATRIX (28-day window)".ljust(width) + "|")
    print("+" + "-" * width + "+")
    print("| " + f"{'Language':<14} {'User':<20} {'Suggested':>9} {'Accepted':>8} {'Rate':>7}" + " |")
    print("|" + "-" * width + "|")

    grand_s = grand_a = 0
    for lang in sorted({lang for lang, _ in matrix}):
        per_user = {user: v for (l, user), v in matrix.items() if l == lang and (v["s"] or v["a"])}
        if not per_user:
            continue
        lang_s = lang_a = 0
        for user, v in sorted(per_user.items(), key=lambda kv: (-kv[1]["a"], -kv[1]["s"])):
            print("| " + f"{lang:<14} {user:<20} {v['s']:>9} {v['a']:>8} {_rate(v['s'], v['a']):>7}" + " |")
            lang_s += v["s"]
            lang_a += v["a"]
        print("| " + f"{'  -> ' + lang + ' subtotal':<35} {lang_s:>9} {lang_a:>8} {_rate(lang_s, lang_a):>7}" + " |")
        print("|" + "-" * width + "|")
        grand_s += lang_s
        grand_a += lang_a
    print("| " + f"{'GRAND TOTAL':<35} {grand_s:>9} {grand_a:>8} {_rate(grand_s, grand_a):>7}" + " |")
    print("+" + "-" * width + "+")


# ============================================================================
# SECTION 9c - TABLE #5/#6: PER-DEVELOPER (dev->lang) and PER-LANGUAGE (lang->dev)
# ============================================================================
# Two two-column grouped tables over the 28-day window, both from the users
# report's totals_by_language_feature[] (same strip-feature exclusion):
#   #5 PER-DEVELOPER : group by developer, one row per language under them.
#   #6 PER-LANGUAGE  : group by language, one row per developer under it.
# Ratio = (accepted / suggested) * 100, the KPI's acceptance rate.
# ============================================================================
def _ratio(sugg, acc):
    """Acceptance rate as a string, or 'n/a' when nothing was suggested."""
    return f"{acc / sugg * 100:.1f}%" if sugg > 0 else "n/a"


def _print_grouped(title, head1, head2, groups, width=79):
    """Render grouped rows: groups = [(group_label, [(item_label, sugg, acc), ...]), ...].
    The group label prints once per group (blank on following rows); a blank line
    separates groups; a final TOTAL row sums everything.
    Columns: label/label/Suggested/Accepted/Ratio/Interpretation = 16/16/9/8/7/16."""
    def line(c1, c2, s, a):
        return (f"{str(c1)[:16]:<16} {str(c2)[:16]:<16} {s:>9} {a:>8} "
                f"{_ratio(s, a):>7} {_interp(s, a):<16}")
    print("\n+" + "-" * width + "+")
    print("|" + f"  {title}".ljust(width) + "|")
    print("+" + "-" * width + "+")
    print("| " + f"{head1:<16} {head2:<16} {'Suggested':>9} {'Accepted':>8} "
          f"{'Ratio':>7} {'Interpretation':<16}" + " |")
    print("|" + "-" * width + "|")
    grand_s = grand_a = 0
    for gi, (glabel, items) in enumerate(groups):
        if gi:
            print("|" + " " * width + "|")                 # blank separator between groups
        first = True
        for item, s, a in items:
            print("| " + line(glabel if first else "", item, s, a) + " |")
            first = False
            grand_s += s
            grand_a += a
    print("|" + "-" * width + "|")
    print("| " + line("TOTAL", "", grand_s, grand_a) + " |")
    print("+" + "-" * width + "+")


def _dev_lang_groups(rows):
    """[(developer, [(language, sugg, acc), ...]), ...] - developers by accepted
    DESC, languages within by accepted then suggested DESC."""
    matrix = _tally(rows or [], "totals_by_language_feature",
                    lambda rec, f, l: (rec.get("user_login"), l)
                    if l and rec.get("user_login") else None)
    by_dev = {}
    for (user, lang), v in matrix.items():
        by_dev.setdefault(user, []).append((lang, v["s"], v["a"]))
    return [(user, sorted(by_dev[user], key=lambda t: (-t[2], -t[1])))
            for user in sorted(by_dev, key=lambda u: -sum(a for _, _, a in by_dev[u]))]


def print_developer_language_table(rows):
    """Table #5: PER-DEVELOPER, broken down by language (dev -> language)."""
    groups = _dev_lang_groups(rows)
    if not groups:
        print("\n  (no per-developer/language data in this window)")
        return
    _print_grouped("PER-DEVELOPER (dev -> language)", "Developer", "Language", groups)


def _sprint_windows(rows):
    """Split the 28-day rows into two 14-day sprints by each row's `day`.
    Anchored on the most recent day: the last 14 days are the 'next' sprint, the
    14 before that are the 'first' sprint.
    Returns [(label, start_date, end_date, rows), ...] (dates as 'YYYY-MM-DD')."""
    dated = [(datetime.date.fromisoformat(r["day"]), r) for r in (rows or [])
             if isinstance(r, dict) and r.get("day")]
    if not dated:
        return [("28-DAY WINDOW", "", "", rows or [])]
    max_d = max(d for d, _ in dated)
    cutoff = max_d - datetime.timedelta(days=13)        # sprint 2 = [cutoff .. max_d] = 14 days

    def d(n):
        return (max_d - datetime.timedelta(days=n)).isoformat()

    first = [r for dd, r in dated if dd < cutoff]
    nxt = [r for dd, r in dated if dd >= cutoff]
    return [
        ("Sprint 1", d(27), d(14), first),
        ("Sprint 2", d(13), d(0), nxt),
    ]


def print_sprint_summary_table(width=90):
    """One row per sprint: start/end dates + total suggested/accepted/ratio/
    interpretation for each 14-day window.
    Columns: Sprint/Start Date/End Date/Suggested/Accepted/Ratio/Interpretation."""
    rows = _LAST_USERS_RAW.get("rows") or []
    windows = _sprint_windows(rows)

    def line(label, start, end, s, a):
        return (f"{str(label):<10} {str(start):<12} {str(end):<12} "
                f"{s:>10} {a:>10} {_ratio(s, a):>8} {_interp(s, a):<18}")

    header = (f"{'Sprint':<10} {'Start Date':<12} {'End Date':<12} "
              f"{'Suggested':>10} {'Accepted':>10} {'Ratio':>8} {'Interpretation':<18}")
    print("\n+" + "-" * width + "+")
    print("|" + "  SPRINT SUMMARY (two 14-day sprints)".ljust(width) + "|")
    print("+" + "-" * width + "+")
    print("| " + header + " |")
    print("|" + "-" * width + "|")
    total_s = total_a = 0
    for i, (_, start, end, window_rows) in enumerate(windows, 1):
        t = _tally(window_rows, "totals_by_feature", lambda rec, f, l: "x").get("x", {"s": 0, "a": 0})
        s, a = t["s"], t["a"]
        print("| " + line(f"sprint-{i}", start, end, s, a) + " |")
        total_s += s
        total_a += a
    print("|" + "-" * width + "|")
    print("| " + line("TOTAL", "", "", total_s, total_a) + " |")
    print("+" + "-" * width + "+")
    print(f"  Interpretation: {KPI['interpretation']}")


def print_sprint_breakdowns():
    """Split the 28-day window into two 14-day sprints and, for each, print the
    PER-DEVELOPER (dev -> language) table."""
    rows = _LAST_USERS_RAW.get("rows") or []
    for label, start, end, window_rows in _sprint_windows(rows):
        print("\n" + "#" * 74)
        print(f"  FOR {label} ({start} .. {end})   ({len(window_rows)} user-day rows)")
        print("#" * 74)
        print_developer_language_table(window_rows)


# ============================================================================
# SECTION 8 - DATAPOINTS (wire each fetch+extract pair to the toolkit)
# ============================================================================
# #1, #2 feed the KPI formula; #3 triggers the users fetch so the tables have data.
DATAPOINTS = [
    Datapoint(
        label="AI-accepted LOC",
        description="Lines of code from accepted Copilot suggestions over 28 days.",
        example="If suggestions added 45 lines, AI-accepted LOC = 45.",
        plain="Code lines from Copilot suggestions that developers kept.",
        paths=["day_totals[].totals_by_feature[].loc_added_sum"],
        steps=["GET org-28-day report",
               "Walk day_totals[].totals_by_feature[]",
               "Sum loc_added_sum (skip stripped features)"],
        source="org-28-day report -> sum(day_totals[].totals_by_feature[].loc_added_sum)",
        fetch=fetch_org_report, extract=extract_accepted_loc,
    ),
    Datapoint(
        label="AI-suggested LOC",
        description="Lines of code Copilot suggested over the same 28 days.",
        example="If features offered 1949 lines, AI-suggested LOC = 1949.",
        plain="Code lines Copilot offered to write.",
        paths=["day_totals[].totals_by_feature[].loc_suggested_to_add_sum"],
        steps=["Reuse org-28-day report",
               "Sum loc_suggested_to_add_sum (skip stripped features)"],
        source="org-28-day report -> sum(...loc_suggested_to_add_sum)",
        fetch=fetch_org_report, extract=extract_suggested_loc,
    ),
    Datapoint(
        label="Per-user JSONL row count",
        description="Per-user-per-day records powering timelines + language tables.",
        example="13 users x ~4 active days each ~= 47 records.",
        plain="How many per-user-per-day records were fetched.",
        paths=["[].user_login + [].day + [].totals_by_language_feature[]"],
        steps=["GET users-28-day report",
               "Parse JSONL rows",
               "Auto-discover users + stash for table printers"],
        source="users-28-day report -> JSONL list of per-user-per-day rows",
        fetch=fetch_users_report, extract=extract_users_stash,
    ),
]


# ============================================================================
# SECTION 9 - ENTRY POINT (order matters: stashes must fill before prints)
# ============================================================================
if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)    # 1. fetch + stash + print headline KPI
    print_sprint_summary_table()         # 2. sprint summary (sprint-1 / sprint-2 totals)
    export_breakdowns_json()             # 2b. save developer data to JSON
    print_sprint_breakdowns()            # 3. two 14-day sprints x (dev->lang, lang->dev)
    # PDF: run_kpi already wrote the report envelope; add `--pdf` on the command
    # line to render it via export_pdf.py (report_sections() above feeds the tables).
  #  print_all_timelines()                # (opt) per-user timelines
   # print_all_language_tables()          # (opt) per-language tables
    # print_language_user_matrix()       # (opt) one flat language x user matrix
