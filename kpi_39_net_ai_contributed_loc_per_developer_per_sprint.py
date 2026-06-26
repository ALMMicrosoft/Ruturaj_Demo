"""
============================================================================
KPI #39 - Net AI-Contributed LOC per Developer per Sprint - Utilization index
           (Source: GitHub Copilot)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #39.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : Actual lines of code written by AI and retained in the
                  codebase per developer per sprint - the direct measure of
                  AI's coding output contribution to the product.
  How measured  : Count total accepted AI LOC per developer per sprint (from
                  telemetry). Cross-validate with git blame attribution for
                  AI-tagged commits.
  Formula       : Sum(AI-accepted and retained LOC) per developer per sprint
  Unit          : LOC/dev/sprint   Cadence: Monthly   Direction: higher-better
  Interpretation: <50 LOC/sprint=Negligible; 50-200=Low; 200-500=Moderate;
                  500-1,000=High - significant productivity uplift;
                  >1,000=Very High - AI writing substantial portion of code

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  Lines Accepted   = total AI-accepted LOC retained across the org over the
                     latest 28-day window. This is sum(day_totals[].loc_added_sum)
                     from the GitHub Copilot org 28-day metrics report.
                     (loc_added_sum is GitHub's telemetry count of lines of code
                     added from accepted Copilot suggestions - i.e. accepted and
                     retained AI LOC. The git-blame cross-validation mentioned in
                     the Excel "how measured" is a manual audit step, not part of
                     this telemetry calculation.)
  Active Devs      = distinct developers with Copilot activity in the same
                     28-day window = count of distinct user_login in the org
                     users-28-day report.
                     (NOTE: this script does NOT implement the route's
                     weekly_active_users fallback. If the per-user report has
                     no logins, this datapoint returns no value and the KPI is
                     reported as NOT COMPUTABLE rather than silently substituting
                     a different number.)
  Result           = Lines Accepted / Active Devs
                     (a plain division: total accepted AI lines / number of
                     developers = mean accepted AI lines per developer).

  WINDOW / "PER SPRINT" NOTE: Copilot reports are published on a fixed rolling
  28-day window; there is no sprint-boundary API. The executive route uses this
  28-day window as the documented PROXY for a sprint (the cadence is Monthly,
  which the 28-day window matches closely). The value is therefore "net AI LOC
  per active developer over the latest 28-day window".

RUN:
  python kpi_39_net_ai_contributed_loc_per_developer_per_sprint.py        # trimmed raw payloads
  python kpi_39_net_ai_contributed_loc_per_developer_per_sprint.py --raw  # full raw payloads
(Needs tools.github-copilot.githubKey + .org in your .secrets/project.json.)
============================================================================
"""
from _toolkit import Datapoint, cfg, gh_report, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github-copilot"

# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
KPI = {
    "num": 39,
    "name": "Net AI-Contributed LOC per Developer per Sprint",
    "index": "Utilization",
    "definition": "Actual lines of code written by AI and retained in the codebase "
                  "per developer per sprint - the direct measure of AI's coding "
                  "output contribution to the product.",
    "how_measured": "Count total accepted AI LOC per developer per sprint (from "
                    "telemetry). Cross-validate with git blame attribution for "
                    "AI-tagged commits.",
    "formula": "Sum(AI-accepted and retained LOC) per developer per sprint",
    "unit": "LOC/dev/sprint",
    "cadence": "Monthly",
    "direction": "higher-better",
    "interpretation": "<50 LOC/sprint=Negligible; 50-200=Low; 200-500=Moderate; "
                      "500-1,000=High - significant productivity uplift; "
                      ">1,000=Very High - AI writing substantial portion of code",
    "tools": "GitHub Copilot",
    "plain": "On average, how many lines of AI-written code each developer keeps in "
             "the codebase over a roughly month-long period. Higher = AI is writing "
             "and developers are keeping more of the actual code.",
    # How the formula combines the datapoint values, step by step. Each step is
    # self-contained so a brand-new developer needs no code to follow it.
    "steps": [
        "Take Lines Accepted as the numerator: the total count of lines of code "
        "that came from accepted Copilot suggestions and were kept (retained) in "
        "the codebase, added up over the latest 28-day window. (28 days is the only "
        "window the GitHub Copilot org metrics API returns; the 'Monthly' cadence "
        "refers to how often you READ this number.) NOTE: despite the word 'Net' in "
        "the KPI name, this counts only lines ADDED from accepted suggestions; no "
        "removed/deleted lines are subtracted here.",
        "Take Active Devs as the denominator: the number of DISTINCT developers "
        "(each counted once, no matter how many days they were active) who had any "
        "Copilot activity in the same 28-day window.",
        "Divide Lines Accepted by Active Devs. This gives the average (mean) number "
        "of accepted-and-retained AI lines per developer over the window.",
        "PROXY (a documented stand-in): the GitHub Copilot API only reports a fixed "
        "rolling 28-day window and has no concept of a sprint boundary, so the "
        "28-day window is used in place of 'a sprint'. The result therefore reads as "
        "'AI LOC per developer per sprint'.",
        "Guard: if Active Devs is 0 (nobody active), the division is undefined and "
        "the script reports NOT COMPUTABLE instead of dividing by zero.",
    ],
}


# ===========================================================================
# DATAPOINT 1 of 2 - "Lines Accepted" (the formula's numerator: total AI LOC)
# ===========================================================================
# WHERE FROM: GitHub Copilot org metrics report, latest 28-day window.
#   GET https://api.github.com/orgs/{org}/copilot/metrics/reports/organization-28-day/latest
#       Accept: application/vnd.github+json
#       X-GitHub-Api-Version: 2026-03-10
#       Authorization: Bearer <githubKey>
#
# IMPORTANT - this endpoint is a TWO-STAGE call (handled by _toolkit.gh_report):
#   1. The endpoint does NOT return the data. It returns signed download_links.
#   2. We follow the first link, gunzip it, and parse the report file. THAT file
#      (shown as `raw` in the trace) is what we extract from.
#
# THE LOGIC: the report's `day_totals` is an array, one object per day. Each day
# carries `loc_added_sum` = lines of code added from accepted Copilot suggestions
# that day (GitHub telemetry for accepted-and-retained AI LOC). The executive
# copilot route computes `kpis.linesAccepted` as the SUM of loc_added_sum across
# all day_totals in the window (see route.ts: `linesAccepted += num(d.loc_added_sum)`
# inside the `for (const d of dayTotals)` loop). We mirror that exactly:
# sum(day_totals[].loc_added_sum). This maps to the Excel "total accepted AI LOC".
async def fetch_lines_accepted(client):
    token = cfg(TOOL, "githubKey")
    org = cfg(TOOL, "org")
    if not token:
        raise RuntimeError("Set tools.github-copilot.githubKey in .secrets/project.json")
    if not org:
        raise RuntimeError("Set tools.github-copilot.org in .secrets/project.json")
    return await gh_report(
        client,
        f"/orgs/{org}/copilot/metrics/reports/organization-28-day/latest",
        token=token,
    )


def extract_lines_accepted(raw):
    # `raw` is the parsed report file: { "day_totals": [ {"loc_added_sum": N, ...}, ... ] }
    if not isinstance(raw, dict):
        return None
    day_totals = raw.get("day_totals") or []
    total = 0.0
    for d in day_totals:
        if isinstance(d, dict):
            v = d.get("loc_added_sum", 0)
            if isinstance(v, (int, float)):
                total += v
    return float(total)


# ===========================================================================
# DATAPOINT 2 of 2 - "Active Devs" (the formula's denominator: per-developer)
# ===========================================================================
# WHERE FROM: GitHub Copilot org PER-USER metrics report, latest 28-day window.
#   GET https://api.github.com/orgs/{org}/copilot/metrics/reports/users-28-day/latest
#       Accept: application/vnd.github+json
#       X-GitHub-Api-Version: 2026-03-10
#       Authorization: Bearer <githubKey>
#
# Same TWO-STAGE pattern as datapoint 1 (signed download_links -> follow first ->
# gunzip -> parse). The users report is JSONL: one row per (developer, day) with
# a `user_login` field.
#
# THE LOGIC: the executive route resolves activeDevCount as
#   d['github-copilot'].perUser.filter(u => u.activeThisCycle).length
# In route.ts, `perUser` with activeThisCycle=true is built ONLY for logins that
# appear in the users-28-day report rows (accMap is keyed by row.user_login). So
# that count is exactly the number of DISTINCT user_login values in this report.
# We mirror that: count distinct non-empty user_login across all rows.
#
# NO FALLBACK HERE: the live route has a fallback to the org report's peak
# weekly_active_users (route's `|| d[CP]?.kpis.weeklyActiveUsers`), but this
# verification script DELIBERATELY does not implement it. We fetch ONLY the
# per-user report and count distinct user_login. If that yields no logins, the
# extractor returns None and the runner surfaces the input as "not resolved"
# (NOT COMPUTABLE) - which is the honest, documented finding for an empty source,
# rather than silently swapping in a different number.
async def fetch_active_devs(client):
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


def extract_active_devs(raw):
    # `raw` is the parsed per-user report. It is normally JSONL -> a list of row
    # objects, each like { "user_login": "...", "day": "...", ... }. Count the
    # number of DISTINCT user_login values (the active developers in the window).
    rows = None
    if isinstance(raw, list):
        rows = raw
    elif isinstance(raw, dict):
        # Some report variants wrap rows; be tolerant of a "rows"/"users" key.
        for key in ("rows", "users", "user_totals", "day_totals"):
            v = raw.get(key)
            if isinstance(v, list):
                rows = v
                break
    if not rows:
        return None
    logins = set()
    for r in rows:
        if isinstance(r, dict):
            login = r.get("user_login")
            if isinstance(login, str) and login.strip():
                logins.add(login)
    return float(len(logins)) if logins else None


# ===========================================================================
# THE FORMULA - Sum(AI-accepted and retained LOC) per developer per sprint
#               = Lines Accepted / Active Devs
# ===========================================================================
# Arguments arrive in the same order as DATAPOINTS below.
def compute(lines_accepted, active_devs):
    if not active_devs:            # guard divide-by-zero / None (no active devs => undefined)
        return None
    if lines_accepted is None:
        return None
    return lines_accepted / active_devs


# The inputs the runner fetches, extracts, and feeds to compute() in this order.
DATAPOINTS = [
    Datapoint(
        label="Lines Accepted (total AI-accepted LOC, 28-day window)",
        description="The total lines of code added from accepted Copilot suggestions and "
                    "retained, summed across every day in the latest 28-day window. This is "
                    "the formula's numerator -- the total AI-contributed LOC for the org.",
        example="e.g. summing day_totals[].loc_added_sum across the 28-day report gave "
                "1404, so Lines Accepted = 1404.",
        plain="The total number of AI-written lines of code everyone kept, across the org, "
              "over the last ~month.",
        paths=["day_totals[].loc_added_sum"],
        steps=[
            "Call the org 28-day metrics report endpoint "
            "(GET /orgs/{org}/copilot/metrics/reports/organization-28-day/latest). 'Org "
            "report' = one combined report for the whole organization (not per person).",
            "The endpoint does NOT return the data directly; it returns signed "
            "download_links (temporary, pre-authorized download URLs). Follow the first "
            "link and decompress it (gunzip = un-zip a .gz-compressed file) to get the "
            "actual report file as JSON.",
            "Read the day_totals array (a list with one object per day in the 28-day "
            "window).",
            "From each day's object, read loc_added_sum (GitHub's telemetry count of lines "
            "of code that were added from accepted Copilot suggestions and kept).",
            "Add up (SUM) loc_added_sum across all the days to get the org's total accepted "
            "AI LOC for the window. This single sum is the numerator.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/organization-28-day/latest "
               "-> follow download_links[0] -> gunzip -> sum(day_totals[].loc_added_sum)",
        fetch=fetch_lines_accepted,
        extract=extract_lines_accepted,
    ),
    Datapoint(
        label="Active Devs (distinct developers with activity, 28-day window)",
        description="The number of DISTINCT developers who had Copilot activity in the latest "
                    "28-day window, counted as unique user_login values in the per-user report. "
                    "This is the formula's denominator -- it turns total AI LOC into LOC per dev.",
        example="e.g. the users-28-day report had rows for user_login values {alice, bob, carol, "
                "dave}, so distinct user_login = 4 and Active Devs = 4 (giving 1404 / 4 = 351 "
                "LOC/dev).",
        plain="How many different developers actually used Copilot at all in the last ~month.",
        paths=["[].user_login"],
        steps=[
            "Call the org PER-USER 28-day metrics report endpoint "
            "(GET /orgs/{org}/copilot/metrics/reports/users-28-day/latest). 'Per-user "
            "report' = one row per developer per day they were active (not a single org "
            "total).",
            "The endpoint returns signed download_links (temporary pre-authorized download "
            "URLs), not the data. Follow the first link and decompress it (gunzip = un-zip "
            "a .gz file). This report is JSONL (JSON Lines = one JSON object per line of "
            "text), so it parses into a list of per-developer-day row objects. (If instead "
            "the report comes back wrapped in a single object, the extractor also looks for "
            "the row list under any of these keys, in order: 'rows', 'users', 'user_totals', "
            "'day_totals'.)",
            "From every row, read the user_login field (the developer's GitHub username).",
            "Collect those usernames into a set so each is counted only ONCE, then count "
            "how many DISTINCT (unique), non-empty usernames there are. That count = the "
            "number of developers active in the window (the denominator).",
            "If no usernames are found, return no value (None) -> the KPI is reported as "
            "NOT COMPUTABLE. No substitute number is used.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/users-28-day/latest "
               "-> follow download_links[0] -> gunzip (JSONL) -> count(distinct user_login)",
        fetch=fetch_active_devs,
        extract=extract_active_devs,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
