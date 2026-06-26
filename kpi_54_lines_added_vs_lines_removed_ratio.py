"""
============================================================================
KPI #54 - Lines Added vs Lines Removed Ratio - Utilization index   (Source: GitHub Copilot)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #54.

From the Excel master (catalogGenerated.ts / KPIs.xlsx):
  Definition    : Ratio of AI-assisted lines added to lines removed per developer
                  per period, measuring the balance between net new code creation
                  and AI-assisted refactoring/cleanup. Helps distinguish feature
                  development from housekeeping work.
  How measured  : Divide total Lines Added by total Lines Removed per developer per
                  sprint. Values >1 indicate net code growth; <1 indicates net code
                  removal (heavy refactoring).
  Formula       : Lines Added / Lines Removed
  Unit          : ratio   Cadence: Per sprint   Direction: higher-better
  Interpretation: Ratio >10=Heavy net creation (feature sprints); 3-10=Active
                  development; 1-3=Balanced (feature + refactor); 0.5-1=Refactoring
                  sprint; <0.5=Major cleanup phase

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  Lines Added   = sum of loc_added_sum across the org's latest 28-day report
                  day_totals  (one GitHub Copilot report call).
  Lines Removed = sum of loc_deleted_sum across the SAME org 28-day report
                  day_totals  (same report call, no extra fetch).
  Result        = Lines Added / Lines Removed.
  Both inputs come from ONE org 28-day report, so a single successful report
  call resolves both - never one without the other.

RUN:
  python kpi_54_lines_added_vs_lines_removed_ratio.py          # trimmed raw payloads
  python kpi_54_lines_added_vs_lines_removed_ratio.py --raw    # full raw payloads
(Needs tools.github-copilot.githubKey + .org in your .secrets/project.json.)
============================================================================
"""
from _toolkit import Datapoint, cfg, gh_report, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github-copilot"

# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
KPI = {
    "num": 54,
    "name": "Lines Added vs Lines Removed Ratio",
    "index": "Utilization",
    "definition": "Ratio of AI-assisted lines added to lines removed per developer per "
                  "period, measuring the balance between net new code creation and "
                  "AI-assisted refactoring/cleanup. Helps distinguish feature "
                  "development from housekeeping work.",
    "how_measured": "Divide total Lines Added by total Lines Removed per developer per "
                    "sprint. Values >1 indicate net code growth; <1 indicates net code "
                    "removal (heavy refactoring).",
    "formula": "Lines Added / Lines Removed",
    "unit": "ratio",
    "cadence": "Per sprint",
    "direction": "higher-better",
    "interpretation": "Ratio >10=Heavy net creation (feature sprints); 3-10=Active "
                      "development; 1-3=Balanced (feature + refactor); 0.5-1=Refactoring "
                      "sprint; <0.5=Major cleanup phase",
    "tools": "GitHub Copilot",
    "plain": "For every line of code Copilot helped REMOVE, how many lines did it "
             "help ADD. Above 1 means more new code than deletions (building "
             "features); below 1 means more deletions than additions (cleaning up "
             "or refactoring).",
    # How the formula combines the datapoint values, step by step.
    # NOTE ON SCOPE (proxy): the Excel row says 'per developer per sprint', but
    # GitHub Copilot's report API has no per-sprint or per-developer line-count
    # field. This script uses the documented stand-in (a 'proxy'): the WHOLE
    # organization's totals over the latest fixed 28-day window. So the number is
    # an org-wide 28-day ratio, NOT a single developer's one-sprint ratio.
    "steps": [
        "Take Lines Added as the numerator. Lines Added = the sum of the field "
        "'loc_added_sum' (AI-assisted lines of code added that day) across every "
        "day in the latest 28-day org report.",
        "Take Lines Removed as the denominator. Lines Removed = the sum of the "
        "field 'loc_deleted_sum' (AI-assisted lines of code deleted that day) "
        "across every day in the SAME 28-day org report.",
        "Divide Lines Added by Lines Removed (numerator / denominator) to get the "
        "ratio. Example: 8420 added / 2105 removed = 4.0.",
        "Guard: if Lines Removed is zero or a negative number the division is "
        "undefined (you cannot divide by zero), so the script returns no value "
        "instead of a ratio.",
    ],
}


# ===========================================================================
# ONE FETCH FOR BOTH DATAPOINTS - the org 28-day metrics report
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
# Both datapoints below read from the SAME report file, so they share this one
# fetch. That is deliberate: the catalog (inputs.ts linesAccepted) sources
# loc_added_sum from this org report, and the verified executive route
# (app/api/executive/copilot/route.ts) sums BOTH loc_added_sum and
# loc_deleted_sum over this same report's day_totals. Sharing the fetch keeps
# the two inputs from ever diverging into "one resolved, one None".
async def fetch_org_28day_report(client):
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


# ===========================================================================
# DATAPOINT 1 of 2 - "Lines Added" (the formula's numerator)
# ===========================================================================
# THE LOGIC: the report's `day_totals` is an array, one object per day, each with
# `loc_added_sum` (AI-assisted lines of code accepted/added that day). The verified
# route accumulates this across the window (route.ts line 341:
#   linesAccepted += num(d.loc_added_sum)). We port that exactly: sum over all days.
def extract_lines_added(raw):
    # `raw` is the parsed report file: { "day_totals": [ {"loc_added_sum": N, ...}, ... ] }
    if not isinstance(raw, dict):
        return None
    day_totals = raw.get("day_totals") or []
    total = 0.0
    for d in day_totals:
        if isinstance(d, dict):
            v = d.get("loc_added_sum")
            if isinstance(v, (int, float)):
                total += v
    return float(total)


# ===========================================================================
# DATAPOINT 2 of 2 - "Lines Removed" (the formula's denominator)
# ===========================================================================
# THE LOGIC: same org 28-day report, summed over `day_totals[].loc_deleted_sum`
# (AI-assisted lines of code removed/deleted). The verified route computes this
# org total the same way (route.ts line 640:
#   dayTotals.reduce((s, d) => s + num(d.loc_deleted_sum), 0)). We port that exactly.
def extract_lines_removed(raw):
    # `raw` is the parsed report file: { "day_totals": [ {"loc_deleted_sum": N, ...}, ... ] }
    if not isinstance(raw, dict):
        return None
    day_totals = raw.get("day_totals") or []
    total = 0.0
    for d in day_totals:
        if isinstance(d, dict):
            v = d.get("loc_deleted_sum")
            if isinstance(v, (int, float)):
                total += v
    return float(total)


# ===========================================================================
# THE FORMULA - Lines Added / Lines Removed
# ===========================================================================
# Arguments arrive in the same order as DATAPOINTS below.
# Guard b>0: a zero OR negative denominator makes the ratio undefined, so we
# return None - matching the catalog evaluate (b > 0 ? a / b : null).
def compute(lines_added, lines_removed):
    if not (lines_removed > 0):     # zero AND negative denominator => undefined
        return None
    return lines_added / lines_removed


# The inputs the runner fetches, extracts, and feeds to compute() in this order.
# Both read from the same org 28-day report (one fetch, two extracts).
DATAPOINTS = [
    Datapoint(
        label="Lines Added (loc_added_sum, 28-day org total)",
        description="Total AI-assisted lines of code added/accepted across the WHOLE "
                    "organization over the latest 28-day window, summed from every day's "
                    "loc_added_sum field. This is the formula's numerator -- the net new "
                    "code creation side of the ratio.",
        example="e.g. summing loc_added_sum over all 28 day_totals entries gave 8420, so "
                "Lines Added = 8420.",
        plain="The total number of lines Copilot helped ADD across the whole team in the "
              "last 28 days.",
        paths=["day_totals[].loc_added_sum"],
        steps=[
            "Call this exact GitHub endpoint: GET "
            "https://api.github.com/orgs/{org}/copilot/metrics/reports/"
            "organization-28-day/latest (sent with header X-GitHub-Api-Version: "
            "2026-03-10 and a Bearer token). {org} is your GitHub organization name "
            "from .secrets/project.json.",
            "This endpoint does NOT return the numbers directly. It returns a JSON object "
            "with a 'download_links' list (temporary signed URLs to a report file). The "
            "toolkit follows the first link and downloads that file.",
            "The downloaded file is gzip-compressed. 'gunzip' = decompress it back to plain "
            "text. The text is then parsed as JSON.",
            "Inside the parsed report, read 'day_totals' -- an array (list) holding one "
            "object per calendar day in the 28-day window (so about 28 entries).",
            "From each day's object take the number field 'loc_added_sum' (AI-assisted "
            "lines of code added that day) and ADD them all together (a simple sum). The "
            "total is Lines Added, the org-wide 28-day count.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/organization-28-day/latest "
               "-> follow download_links[0] -> gunzip -> sum(day_totals[].loc_added_sum)",
        fetch=fetch_org_28day_report,
        extract=extract_lines_added,
    ),
    Datapoint(
        label="Lines Removed (loc_deleted_sum, 28-day org total)",
        description="Total AI-assisted lines of code removed/deleted across the WHOLE "
                    "organization over the same latest 28-day window, summed from every "
                    "day's loc_deleted_sum field. This is the formula's denominator -- the "
                    "refactoring/cleanup side of the ratio.",
        example="e.g. summing loc_deleted_sum over all 28 day_totals entries gave 2105, so "
                "Lines Removed = 2105 (and the ratio = 8420 / 2105 = 4.0).",
        plain="The total number of lines Copilot helped REMOVE across the whole team in the "
              "last 28 days.",
        paths=["day_totals[].loc_deleted_sum"],
        steps=[
            "Use the SAME report file already downloaded and decompressed (gunzipped) for "
            "Lines Added. Both numbers come from one call to GET "
            "https://api.github.com/orgs/{org}/copilot/metrics/reports/"
            "organization-28-day/latest, so there is no second request here.",
            "Inside that parsed report, read 'day_totals' -- the array with one object per "
            "calendar day in the 28-day window (about 28 entries).",
            "From each day's object take the number field 'loc_deleted_sum' (AI-assisted "
            "lines of code deleted that day) and ADD them all together (a simple sum). The "
            "total is Lines Removed, the org-wide 28-day count.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/organization-28-day/latest "
               "-> follow download_links[0] -> gunzip -> sum(day_totals[].loc_deleted_sum)",
        fetch=fetch_org_28day_report,
        extract=extract_lines_removed,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
