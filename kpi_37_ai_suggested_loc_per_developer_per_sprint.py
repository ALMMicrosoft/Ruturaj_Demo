"""
============================================================================
KPI #37 . AI-Suggested Lines of Code (LOC) per Developer per Sprint . Utilization index   (Source: GitHub Copilot)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #37.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : Total lines of code suggested by AI tools to a developer per
                  sprint, regardless of acceptance. Measures the volume of
                  AI-generated output offered to the team and the AI tool's
                  coverage of active development.
  How measured  : Sum lines of code in all AI completions shown to the developer
                  across all IDEs per sprint from telemetry APIs. Report as mean
                  per developer.
  Formula       : Sum(LOC in AI suggestions shown) per developer per sprint
  Unit          : LOC/dev/sprint   Cadence: Weekly   Direction: higher-better
  Interpretation: <200 LOC/sprint=Low - minimal AI coding assistance;
                  200-500=Developing; 500-1,500=Active; 1,500-3,000=High;
                  >3,000=Very High - AI is a primary coding partner

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  Lines Suggested = total loc_suggested_to_add_sum across the org's latest
                    Copilot 28-day per-user report (summed over every user-day
                    row, across all IDEs/features). One GitHub Copilot report call.
  Active Devs     = number of DISTINCT developers (user_login) with any activity
                    in that same 28-day per-user report. Same report file - so a
                    single upstream call yields both inputs.
  Result          = Lines Suggested / Active Devs  (mean LOC suggested per dev).

  PROXY NOTE: GitHub Copilot exposes a rolling 28-day window, not a sprint
  boundary. The 28-day window is used as the documented proxy for "per sprint";
  this matches the verified executive Copilot route, which aggregates the same
  28-day report. Both datapoints come from the per-user report, exactly as
  genai-tracker/lib/kpi/inputs.ts (INPUTS.linesSuggested, INPUTS.activeDevCount)
  and app/api/executive/copilot/route.ts derive them.

RUN:
  python kpi_37_ai_suggested_loc_per_developer_per_sprint.py          # trimmed raw payloads
  python kpi_37_ai_suggested_loc_per_developer_per_sprint.py --raw    # full raw payloads
(Needs tools.github-copilot.githubKey + .org in your .secrets/project.json.)
============================================================================
"""
from _toolkit import Datapoint, cfg, gh_report, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github-copilot"

# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
KPI = {
    "num": 37,
    "name": "AI-Suggested Lines of Code (LOC) per Developer per Sprint",
    "index": "Utilization",
    "definition": "Total lines of code suggested by AI tools to a developer per "
                  "sprint, regardless of acceptance. Measures the volume of "
                  "AI-generated output offered to the team and the AI tool's "
                  "coverage of active development.",
    "how_measured": "Sum lines of code in all AI completions shown to the developer "
                    "across all IDEs per sprint from telemetry APIs. Report as mean "
                    "per developer.",
    "formula": "Sum(LOC in AI suggestions shown) per developer per sprint",
    "unit": "LOC/dev/sprint",
    "cadence": "Weekly",
    "direction": "higher-better",
    "interpretation": "<200 LOC/sprint=Low - minimal AI coding assistance; "
                      "200-500=Developing; 500-1500=Active; 1500-3000=High; "
                      ">3000=Very High - AI is a primary coding partner",
    "tools": "GitHub Copilot",
    "plain": "On average, how many lines of code Copilot offered to each developer "
             "during the sprint (counting every suggestion shown, whether the developer "
             "kept it or not). Higher means developers are getting more AI help.",
    # How the formula combines the datapoint values, step by step.
    "steps": [
        "Lines Suggested = the org-wide total of all code lines Copilot offered in the "
        "window (the field 'loc_suggested_to_add_sum', added up across every row and "
        "every IDE/feature). Active Developers = how many different people used Copilot "
        "(distinct = each person counted once, even across many days).",
        "Divide Lines Suggested by Active Developers. This gives the mean (average) lines "
        "suggested per developer: total lines offered shared evenly across the people who "
        "were active.",
        "Report that average as the per-developer LOC for the sprint. PROXY (a documented "
        "stand-in because the API has no sprint field): Copilot only exposes a rolling "
        "28-day window, so that 28-day window is used in place of one sprint.",
    ],
}


# ===========================================================================
# DATAPOINT 1 of 2 - "Lines Suggested" (the formula's numerator)
# ===========================================================================
# WHERE FROM: GitHub Copilot org PER-USER metrics report, latest 28-day window.
#   GET https://api.github.com/orgs/{org}/copilot/metrics/reports/users-28-day/latest
#       Accept: application/vnd.github+json
#       X-GitHub-Api-Version: 2026-03-10
#       Authorization: Bearer <githubKey>
#
# IMPORTANT - this endpoint is a TWO-STAGE call (handled by _toolkit.gh_report):
#   1. The endpoint does NOT return the data. It returns signed download_links.
#   2. We follow the first link, gunzip it, and parse the report file. THAT file
#      (shown as `raw` in the trace) is what we extract from. It is JSONL: one
#      object per developer-day row.
#
# THE LOGIC (ported verbatim from app/api/executive/copilot/route.ts): the LOC
# totals live INSIDE each row's `totals_by_feature` array (the feature partition
# sums to the row total). For every row, for every totals_by_feature entry, we
# add `loc_suggested_to_add_sum`. The grand sum over all rows is the org's total
# lines suggested in the window - exactly INPUTS.linesSuggested in inputs.ts
# (sumPerUser over u.linesSuggested, where linesSuggested accumulates
# loc_suggested_to_add_sum from totals_by_feature).
async def fetch_lines_suggested(client):
    token = cfg(TOOL, "githubKey")
    org = cfg(TOOL, "org")
    if not token:
        raise RuntimeError("Set tools.github-copilot.githubKey in .secrets/project.json")
    if not org:
        raise RuntimeError("Set tools.github-copilot.org in .secrets/project.json")
    return await gh_report(
        client,
        f"/orgs/{org}/copilot/metrics/reports/users-28-day/latest",
        token=token,
    )


def extract_lines_suggested(raw):
    # `raw` is the parsed per-user report file: a list of developer-day rows, each
    # like { "user_login": "...", "totals_by_feature": [ {"loc_suggested_to_add_sum": N, ...}, ... ], ... }
    rows = raw if isinstance(raw, list) else []
    total = 0.0
    for row in rows:
        if not isinstance(row, dict):
            continue
        feats = row.get("totals_by_feature")
        if not isinstance(feats, list):
            continue
        for entry in feats:
            if isinstance(entry, dict):
                v = entry.get("loc_suggested_to_add_sum")
                if isinstance(v, (int, float)):
                    total += float(v)
    return total


# ===========================================================================
# DATAPOINT 2 of 2 - "Active Developers" (the formula's denominator)
# ===========================================================================
# WHERE FROM: the SAME GitHub Copilot per-user 28-day report as above
#   GET https://api.github.com/orgs/{org}/copilot/metrics/reports/users-28-day/latest
#   (same two-stage signed-download-link call via _toolkit.gh_report).
#
# THE LOGIC (ported from route.ts accMap.size / inputs.ts INPUTS.activeDevCount):
# the per-user report has one row per developer per active day; the count of
# DISTINCT `user_login` values is the number of developers with any activity in
# the window. inputs.ts resolves this as perUser.filter(activeThisCycle).length,
# which equals the distinct active logins built from this very report.
async def fetch_active_devs(client):
    token = cfg(TOOL, "githubKey")
    org = cfg(TOOL, "org")
    if not token or not org:
        raise RuntimeError("Set tools.github-copilot.githubKey and .org in .secrets/project.json")
    return await gh_report(
        client,
        f"/orgs/{org}/copilot/metrics/reports/users-28-day/latest",
        token=token,
    )


def extract_active_devs(raw):
    # `raw` is the parsed per-user report file (list of developer-day rows).
    # Count distinct, non-empty user_login values = developers active in the window.
    rows = raw if isinstance(raw, list) else []
    logins = set()
    for row in rows:
        if isinstance(row, dict):
            login = row.get("user_login")
            if isinstance(login, str) and login:
                logins.add(login)
    return float(len(logins)) if logins else None


# ===========================================================================
# THE FORMULA - Sum(LOC suggested) / Active Developers  (mean per developer)
# ===========================================================================
# Arguments arrive in the same order as DATAPOINTS below.
def compute(lines_suggested, active_devs):
    if not active_devs:        # guard against divide-by-zero (no active devs => undefined)
        return None
    return lines_suggested / active_devs


# The inputs the runner fetches, extracts, and feeds to compute() in this order.
DATAPOINTS = [
    Datapoint(
        label="Lines Suggested (total loc_suggested_to_add_sum, 28-day window)",
        description="The total lines of code Copilot OFFERED to developers across the org "
                    "in the 28-day window, regardless of whether they were accepted. Summed "
                    "from every developer-day row's totals_by_feature entries (all IDEs/features). "
                    "This is the formula's numerator -- the volume of AI-suggested output.",
        example="e.g. adding loc_suggested_to_add_sum across every totals_by_feature entry of "
                "every per-user row totalled 4200, so Lines Suggested = 4200.",
        plain="The total number of code lines Copilot suggested to all developers over the "
              "period, counting every suggestion shown whether or not it was kept.",
        paths=["[].totals_by_feature[].loc_suggested_to_add_sum"],
        steps=[
            "Call the GitHub Copilot org PER-USER 28-day metrics report endpoint: "
            "GET https://api.github.com/orgs/{org}/copilot/metrics/reports/users-28-day/latest "
            "(28-day = a rolling window of the most recent 28 days; per-user = the report is "
            "broken down by individual developer).",
            "This endpoint does NOT return the numbers directly. It returns 'download_links' "
            "(temporary signed URLs pointing to a separate report file). Follow the first "
            "link to download that file.",
            "The downloaded file is gzipped (compressed). Decompress it (gunzip = undo gzip "
            "compression). The result is JSONL: a text file where each line is one separate "
            "JSON object, and here each line is one developer-day row (one developer's activity "
            "on one day), e.g. { \"user_login\": \"alice\", \"totals_by_feature\": [...] }.",
            "Inside each row is a list called totals_by_feature (one entry per Copilot feature, "
            "such as code completion or chat, across every IDE). For each row, add up the field "
            "'loc_suggested_to_add_sum' (lines of code Copilot offered to insert) from every "
            "entry in that list.",
            "Add (sum) those per-row totals together across every row in the file. The grand "
            "total is the org's total lines Copilot suggested in the 28-day window -- the "
            "formula's numerator.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/users-28-day/latest "
               "-> follow download_links[0] -> gunzip -> "
               "sum over rows of sum(totals_by_feature[].loc_suggested_to_add_sum)",
        fetch=fetch_lines_suggested,
        extract=extract_lines_suggested,
    ),
    Datapoint(
        label="Active Developers (distinct user_login in 28-day window)",
        description="The number of DISTINCT developers (counted by user_login) with any "
                    "activity in the same 28-day per-user report. This is the formula's "
                    "denominator -- it turns the total lines suggested into a mean per developer.",
        example="e.g. the per-user rows contained 7 distinct user_login values, so Active "
                "Developers = 7 (and the mean = 4200 / 7 = 600 LOC/dev).",
        plain="How many different developers actually used Copilot during the period (each "
              "person counted once, no matter how many days they were active).",
        paths=["[].user_login"],
        steps=[
            "Reuse the SAME per-user 28-day report file as the numerator above (same endpoint, "
            "same two-stage call: download the signed link, then gunzip the gzipped file into "
            "JSONL rows). No second network call is made for this datapoint.",
            "From every developer-day row, read the field 'user_login' (the developer's GitHub "
            "username). The same person appears in many rows -- one row per day they were active.",
            "Collect those usernames into a set. A set automatically keeps only DISTINCT values "
            "(each username appears once, duplicates dropped); empty/blank usernames are skipped.",
            "Count how many usernames are in the set. That count = the number of different "
            "developers with any Copilot activity in the window -- the formula's denominator. "
            "PROXY (documented stand-in, no sprint field exists): the 28-day window stands in "
            "for one sprint.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/users-28-day/latest "
               "-> follow download_links[0] -> gunzip -> "
               "count of distinct rows[].user_login (PROXY: 28-day window for sprint)",
        fetch=fetch_active_devs,
        extract=extract_active_devs,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
