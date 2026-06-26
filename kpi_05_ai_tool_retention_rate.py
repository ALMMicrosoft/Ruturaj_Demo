"""
============================================================================
KPI #05 · AI Tool Retention Rate · Adoption index   (Source: GitHub Copilot)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #5.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : % of developers who remain active AI tool users at 90 days after
                  initial adoption, measuring sustainable engagement vs short-lived
                  curiosity spikes.
  How measured  : Active users at Day 90 divided by active users at Day 30 x 100.
                  Also track Day 180 cohort separately.
  Formula       : (Active users at Day 90 / Active users at Day 30) x 100
  Unit          : %        Cadence: Quarterly    Direction: higher-better
  Interpretation: <60% Critical · 60-75% Needs improvement · 75-90% Good · 90%+ Excellent

WHY THIS NEEDS A COHORT (read carefully — this is the crux of the logic):
  Retention is NOT a single snapshot. It follows ONE group of developers (a
  "cohort") over time: of the people who first adopted the tool, how many are
  still active 30 days later, and how many 90 days later.

  GitHub Copilot exposes per-user activity for any single past day via:
     GET /orgs/{org}/copilot/metrics/reports/users-1-day?day=YYYY-MM-DD
  with history from 2025-10-10 (up to 1 year). "Active on day D" = the user_login
  appears in that day's report. We reconstruct the cohort from this history.

HOW THIS SCRIPT COMPUTES IT:
  1. Auto-detect Day 0 = the org's FIRST active day. (No Copilot data exists before
     2025-10-10, so the first day with activity is the first observable adoption.)
  2. Cohort = the set of developers active in the {ADOPT_DAYS}-day adoption window
     starting at Day 0.
  3. Active at Day 30 = cohort members still active in a +/-{WINDOW_HALF}-day window
     around Day 0 + 30.   Active at Day 90 = same around Day 0 + 90.
  4. Result = (cohort active at Day 90 / cohort active at Day 30) x 100.

  If the org has < 90 days of history, the script says so honestly (Day-90
  retention is not measurable yet) instead of inventing a number.

  NOTE: both inputs come from ONE shared cohort scan (cached), so the ~30-50 dated
  report calls run only once per execution.

RUN:
  python kpi_05_ai_tool_retention_rate.py            # trimmed raw payloads
  python kpi_05_ai_tool_retention_rate.py --raw      # full cohort detail
(Needs tools.github-copilot.githubKey + .org in your .secrets/project.json.)
============================================================================
"""
from __future__ import annotations

import datetime as dt

from _toolkit import Call, Datapoint, cfg, gh_report, run_kpi

TOOL = "github-copilot"

KPI = {
    "num": 5,
    "name": "AI Tool Retention Rate",
    "index": "Adoption",
    "definition": "% of developers who remain active AI tool users at 90 days after "
                  "initial adoption, measuring sustainable engagement vs short-lived "
                  "curiosity spikes.",
    "how_measured": "Active users at Day 90 divided by active users at Day 30 x 100. "
                    "Also track Day 180 cohort separately.",
    "formula": "(Active users at Day 90 / Active users at Day 30) x 100",
    "unit": "%",
    "cadence": "Quarterly",
    "direction": "higher-better",
    "interpretation": "<60%=Critical; 60-75%=Needs improvement; 75-90%=Good; 90%+=Excellent",
    "tools": "GitHub Copilot",
    "plain": "Of the developers who started using Copilot, what share are still using it "
             "three months later. High = the tool stuck; low = people tried it once and "
             "dropped off.",
    # How the formula combines the two datapoint values, step by step.
    "steps": [
        "Take the count of cohort developers still active at Day 90 (numerator) and the "
        "count still active at Day 30 (denominator). A 'cohort' = the one fixed group of "
        "developers who first adopted Copilot; we follow that same group over time.",
        "Divide Day-90 count by Day-30 count -> the fraction of the Day-30 active group "
        "that is still active at Day 90.",
        "Multiply by 100 to express that fraction as a percentage (the retention rate).",
        "Guard: if the Day-30 count is 0 (nobody to retain), the result is undefined and "
        "the script reports NOT COMPUTABLE instead of dividing by zero.",
    ],
}

# ---- Tunable cohort knobs (documented so a reviewer can adjust + re-verify) ----
DATA_START = dt.date(2025, 10, 10)   # Copilot per-user history starts here
ADOPT_DAYS = 14                       # length of the adoption window (defines the cohort)
WINDOW_HALF = 3                       # +/- days sampled around the Day 30 / Day 90 marks
PROBE_STRIDE = 14                     # coarse step when hunting for the first active day


# ---- one dated per-user report -> the set of logins active that day -----------
async def _active_logins(client, org, token, day: dt.date) -> set[str] | None:
    # users-1-day is a 2-stage report (download link -> gunzip -> JSONL of per-user rows).
    call = await gh_report(
        client,
        f"/orgs/{org}/copilot/metrics/reports/users-1-day?day={day.isoformat()}",
        token=token,
    )
    if not call.ok:
        return None
    rows = call.raw if isinstance(call.raw, list) else []
    return {r["user_login"] for r in rows if isinstance(r, dict) and r.get("user_login")}


async def _union_active(client, org, token, days: list[dt.date]) -> set[str]:
    """Union of active logins across several days (a sampled window)."""
    out: set[str] = set()
    for d in days:
        s = await _active_logins(client, org, token, d)
        if s:
            out |= s
    return out


async def _find_first_active(client, org, token, start: dt.date, latest: dt.date):
    """The org's first active day: coarse forward stride, then refine backward."""
    d, hit = start, None
    while d <= latest:
        if await _active_logins(client, org, token, d):
            hit = d
            break
        d += dt.timedelta(days=PROBE_STRIDE)
    if hit is None:
        return None
    first = hit
    probe = hit - dt.timedelta(days=1)
    stop = max(start, hit - dt.timedelta(days=PROBE_STRIDE))
    while probe >= stop:
        if await _active_logins(client, org, token, probe):
            first = probe
        probe -= dt.timedelta(days=1)
    return first


# ---- the cohort scan (computed once, shared by both datapoints) ----------------
_CACHE: dict[str, dict] = {}
# The real API exchanges the scan made, captured once so BOTH datapoints (Day 30
# and Day 90) can show them in the viewer even though the scan runs a single time.
_CALLS: list = []


def _cache(summary, client, start):
    _CACHE["summary"] = summary
    log = getattr(client, "_kpi_log", None)
    if isinstance(log, list) and start is not None:
        _CALLS[:] = log[start:]
    return summary


async def _cohort(client) -> dict:
    log = getattr(client, "_kpi_log", None)
    if "summary" in _CACHE:
        if isinstance(log, list):
            log.extend(_CALLS)   # re-attribute the shared scan's real calls to this datapoint
        return _CACHE["summary"]
    start = len(log) if isinstance(log, list) else None
    token, org = cfg(TOOL, "githubKey"), cfg(TOOL, "org")
    if not token or not org:
        raise RuntimeError("Set tools.github-copilot.githubKey and .org in .secrets/project.json")

    today = dt.date.today()
    latest_anchor = today - dt.timedelta(days=90)   # need >= 90 days of follow-up
    anchor = await _find_first_active(client, org, token, DATA_START, today)

    summary: dict = {
        "data_start": DATA_START.isoformat(),
        "today": today.isoformat(),
        "anchor (Day 0 = first active day)": anchor.isoformat() if anchor else None,
        "cohort_active_day30": None,
        "cohort_active_day90": None,
        "blocker": None,
    }
    if anchor is None:
        summary["blocker"] = "No Copilot activity found in the available history for this org."
        return _cache(summary, client, start)
    if anchor > latest_anchor:
        days_hist = (today - anchor).days
        summary["blocker"] = (
            f"Adoption began {anchor.isoformat()} ({days_hist} days ago) - fewer than 90 "
            f"days of history, so Day-90 retention is not yet measurable. Available on "
            f"{(anchor + dt.timedelta(days=90)).isoformat()}."
        )
        return _cache(summary, client, start)

    adopt_days = [anchor + dt.timedelta(days=k) for k in range(ADOPT_DAYS)]
    d30_days = [anchor + dt.timedelta(days=30 + k) for k in range(-WINDOW_HALF, WINDOW_HALF + 1)]
    d90_days = [anchor + dt.timedelta(days=90 + k) for k in range(-WINDOW_HALF, WINDOW_HALF + 1)]

    cohort = await _union_active(client, org, token, adopt_days)
    d30 = cohort & await _union_active(client, org, token, d30_days)
    d90 = cohort & await _union_active(client, org, token, d90_days)

    summary.update({
        "adoption_window": [adopt_days[0].isoformat(), adopt_days[-1].isoformat()],
        "cohort_size": len(cohort),
        "cohort_sample": sorted(cohort)[:20],
        "day30_window": [d30_days[0].isoformat(), d30_days[-1].isoformat()],
        "day90_window": [d90_days[0].isoformat(), d90_days[-1].isoformat()],
        "cohort_active_day30": len(d30),
        "cohort_active_day90": len(d90),
    })
    if len(d30) == 0:
        summary["blocker"] = ("No cohort members were active in the Day-30 window "
                              "(cohort churned immediately); retention is undefined (denominator 0).")
    return _cache(summary, client, start)


# ---- the two formula inputs, both reading the shared cohort summary ------------
async def _fetch_cohort(client) -> Call:
    summary = await _cohort(client)
    return Call(
        method="GET (xN dated calls)",
        url="https://api.github.com/orgs/{org}/copilot/metrics/reports/users-1-day?day=YYYY-MM-DD",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": "***redacted***", "X-GitHub-Api-Version": "2026-03-10"},
        status=200,
        raw=summary,
        note="cohort scan: one dated users-1-day call per sampled day; see raw for the cohort",
    )


def _count(key):
    def extract(raw):
        if isinstance(raw, dict) and raw.get(key) is not None:
            return float(raw[key])
        return None      # None when blocked -> KPI reports NOT COMPUTABLE with the reason in raw
    return extract


def compute(active_day30, active_day90):
    if not active_day30:        # denominator 0 / missing -> undefined
        return None
    return active_day90 / active_day30 * 100


# Order matters: compute(active_day30, active_day90).
DATAPOINTS = [
    Datapoint(
        label="Cohort active at Day 30",
        description="Of the developers who first adopted Copilot (the cohort), how many "
                    "were still active about 30 days later. This is the retention BASELINE "
                    "-- the formula's denominator.",
        example="e.g. the cohort of 7 (first active 2025-12-15) had 5 still active in the "
                "Jan 11-17 window, so Day 30 = 5.",
        plain="How many of the developers who first tried Copilot were still using it "
              "about one month later.",
        paths=["cohort_active_day30"],
        steps=[
            "ENDPOINT used everywhere below: GET /orgs/{org}/copilot/metrics/reports/"
            "users-1-day?day=YYYY-MM-DD . It returns per-user Copilot activity for that "
            "ONE calendar day. 'Active on day D' = the developer's user_login appears in "
            "that day's report.",
            "Each users-1-day call is a 2-stage download: the endpoint first returns signed "
            "download_links (not the data); the toolkit follows the first link, gunzips it "
            "(gunzip = decompress a .gz file) and parses the file as JSONL (JSONL = one JSON "
            "object per line, here one line per active developer). The set of user_login "
            "values in those lines = the developers active that day.",
            "Find Day 0 (the org's first active day): call the endpoint forward in time "
            "starting at 2025-10-10 (the earliest day Copilot has per-user history) in coarse "
            "14-day jumps until the first day that has any active developer is found; then "
            "step backward one day at a time (up to 14 days) and keep the EARLIEST day that "
            "still has activity. That earliest day is Day 0.",
            "GATE before any counting: the script needs at least 90 days of follow-up. If "
            "Day 0 is more recent than (today minus 90 days), Day-90 retention is not "
            "measurable yet, so BOTH datapoints return no value and the KPI reports NOT "
            "COMPUTABLE with the date it will become available.",
            "Build the cohort: call the endpoint for each of the 14 days starting at Day 0 "
            "(the adoption window) and take the UNION of their active user_login sets (union "
            "= every developer who was active on at least one of those 14 days). That set of "
            "developers is the fixed cohort reused for Day 30 and Day 90.",
            "Sample the Day-30 window: call the endpoint for each day from (Day 0 + 30 - 3) "
            "to (Day 0 + 30 + 3) inclusive (7 days), and take the union of their active "
            "user_login sets.",
            "Count = number of cohort developers who also appear in that Day-30 active set "
            "(set intersection: members present in BOTH the cohort AND the Day-30 window). "
            "This count is the value (the formula's denominator).",
            "Edge case: if this count is 0 the cohort churned immediately and retention is "
            "undefined (division by zero); the raw payload records that as the blocker.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/users-1-day?day=YYYY-MM-DD (one call "
               "per sampled day) -> count of cohort developers also active in the Day0+30 "
               "+/-3-day window (cohort and Day-30 active sets intersected)",
        fetch=_fetch_cohort,
        extract=_count("cohort_active_day30"),
    ),
    Datapoint(
        label="Cohort active at Day 90",
        description="Of that SAME adoption cohort, how many were still active about 90 "
                    "days later. This is the RETAINED set -- the formula's numerator.",
        example="e.g. 3 of the 7 were active in the Mar 12-18 window, so Day 90 = 3 "
                "(retention = 3 / 5 = 60%).",
        plain="How many of those same first-time developers were still using Copilot "
              "about three months later.",
        paths=["cohort_active_day90"],
        steps=[
            "Reuse the SAME Day 0 and the SAME cohort already built in the Day-30 datapoint. "
            "The cohort scan runs once and is cached, so the ~30-50 dated report calls are "
            "not repeated. (Cohort = the fixed group of developers active in the 14-day "
            "adoption window starting at Day 0.)",
            "Sample the Day-90 window: call GET /orgs/{org}/copilot/metrics/reports/"
            "users-1-day?day=YYYY-MM-DD for each day from (Day 0 + 90 - 3) to (Day 0 + 90 + 3) "
            "inclusive (7 days). Each call is the same 2-stage download (signed link -> gunzip "
            "-> JSONL of per-user rows); a developer is 'active' if their user_login appears.",
            "Take the union of the active user_login sets across those 7 days (union = active "
            "on at least one of the days).",
            "Count = number of cohort developers who also appear in that Day-90 active set "
            "(set intersection of the cohort with the Day-90 window). This count is the value "
            "(the formula's numerator).",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/users-1-day?day=YYYY-MM-DD (one call "
               "per sampled day) -> count of cohort developers also active in the Day0+90 "
               "+/-3-day window (cohort and Day-90 active sets intersected)",
        fetch=_fetch_cohort,
        extract=_count("cohort_active_day90"),
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
