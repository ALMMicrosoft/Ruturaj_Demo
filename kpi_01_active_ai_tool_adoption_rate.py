"""
============================================================================
KPI #01 · Active AI Tool Adoption Rate · Adoption index   (Source: GitHub Copilot)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #1.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : % of licensed AI tool seats with genuine active weekly usage.
                  Distinguishes license purchase from real capability activation.
  How measured  : Count developers who triggered at least 1 AI-assisted action in
                  the reporting week; divide by total licensed seats x 100.
  Formula       : (Active Users / Licensed Seats) x 100
  Unit          : %        Cadence: Weekly       Direction: higher-better
  Interpretation: 40% Critical · 70% Acceptable · 85% Good · 90%+ Excellent

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  Active Users   = peak weekly-active Copilot developers upto specific date
                    (one GitHub Copilot report call).
  Licensed Seats = total Copilot seats provisioned for the org
                   (one GitHub Copilot billing call).
  Result         = Active Users / Licensed Seats * 100.

RUN:
  python kpi_01_active_ai_tool_adoption_rate.py          # trimmed raw payloads
  python kpi_01_active_ai_tool_adoption_rate.py --raw    # full raw payloads
(Needs tools.github-copilot.githubKey + .org in your .secrets/project.json.)
============================================================================
"""
from _toolkit import Datapoint, cfg, gh_get, gh_report, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github-copilot"
DAY = "2026-04-05"     # the date whose weekly report we want to read (format: YYYY-MM-DD)

# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
KPI = {
    "num": 1,
    "name": "Active AI Tool Adoption Rate",
    "index": "Adoption",
    "definition": "% of licensed AI tool seats with genuine active weekly usage. "
                  "Distinguishes license purchase from real capability activation.",
    "how_measured": "Count developers who triggered at least 1 AI-assisted action in "
                    "the reporting week; divide by total licensed seats x 100.",
    "formula": "(Active Users / Licensed Seats) x 100",
    "unit": "%",
    "cadence": "Weekly",
    "direction": "higher-better",
    "interpretation": "40%=Critical; 70%=Acceptable; 85%=Good; 90%+=Excellent",
    "tools": "GitHub Copilot",
    "plain": "Of all the Copilot seats you pay for, what share are actually used in a "
             "week. High = most paid seats are active; low = you are paying for seats "
             "nobody uses.",
    # How the formula combines the datapoint values, step by step.
    "steps": [
        "Divide Active Users by Licensed Seats -> the fraction of provisioned seats "
        "that are actually active this week.",
        "Multiply by 100 to express that fraction as a percentage.",
    ],
}


# ===========================================================================
# DATAPOINT 1 of 2 — "Active Users" (the formula's numerator)
# ===========================================================================
# WHERE FROM: GitHub Copilot org metrics report, for specific date.
#   GET https://api.github.com/orgs/{org}/copilot/metrics/reports/organization-1-day?day={day}
#       Accept: application/vnd.github+json
#       X-GitHub-Api-Version: 2026-03-10
#       Authorization: Bearer <githubKey>
#
# IMPORTANT — this endpoint is a TWO-STAGE call (handled by _toolkit.gh_report):
#   1. The endpoint does NOT return the data. It returns signed download_links.
#   2. We follow the first link, gunzip it, and parse the report file. THAT file
#      (shown as `raw` in the trace) is what we extract from.
#
# THE LOGIC: the report's `weekly_active_users`  (distinct devs active in the rolling week ending that day).
# The Excel KPI wants the week's active developers

async def fetch_active_users(client):
    token = cfg(TOOL, "githubKey")
    org = cfg(TOOL, "org")
    if not token:
        raise RuntimeError("Set tools.github-copilot.githubKey in .secrets/project.json")
    if not org:
        raise RuntimeError("Set tools.github-copilot.org in .secrets/project.json")
    return await gh_report(
        client,
        f"/orgs/{org}/copilot/metrics/reports/organization-1-day?day={DAY}",
        token=token,
    )


def extract_active_users(raw):
    # `raw` is the parsed report file: { "weekly_active_users": N }
    if not isinstance(raw, dict):
        return None
    day_totals = raw.get("weekly_active_users")
    return float(day_totals)


# ===========================================================================
# DATAPOINT 2 of 2 — "Licensed Seats" (the formula's denominator)
# ===========================================================================
# WHERE FROM: GitHub Copilot billing (inline JSON, no download link).
#   GET https://api.github.com/orgs/{org}/copilot/billing
#       X-GitHub-Api-Version: 2022-11-28
#       Authorization: Bearer <githubKey>
#
# THE LOGIC: the response has `seat_breakdown.total` = total provisioned seats.
async def fetch_licensed_seats(client):
    token = cfg(TOOL, "githubKey")
    org = cfg(TOOL, "org")
    if not token or not org:
        raise RuntimeError("Set tools.github-copilot.githubKey and .org in .secrets/project.json")
    return await gh_get(client, f"/orgs/{org}/copilot/billing",
                        token=token, api_version="2022-11-28")


def extract_licensed_seats(raw):
    # `raw` is: { "seat_breakdown": { "total": N, "active_this_cycle": ..., ... }, ... }
    if not isinstance(raw, dict):
        return None
    total = (raw.get("seat_breakdown") or {}).get("total")
    return float(total) if isinstance(total, (int, float)) else None


# ===========================================================================
# THE FORMULA — (Active Users / Licensed Seats) x 100
# ===========================================================================
# Arguments arrive in the same order as DATAPOINTS below.
def compute(active_users, licensed_seats):
    if not licensed_seats:          # guard against divide-by-zero (no seats => undefined)
        return None
    return active_users / licensed_seats * 100


# The inputs the runner fetches, extracts, and feeds to compute() in this order.
DATAPOINTS = [
    Datapoint(
        label="Active Users (peak weekly-active developers)",
        description="The number of DISTINCT developers who actually used Copilot in a week"
                    "This is the formula's numerator -- the 'active' in adoption.",
        example="e.g. if 4 developers used Copilot in the week, then Active Users = 4.",
        plain="How many different developers used Copilot in the busiest week of the period.",
        paths=["weekly_active_users"],
        steps=[
            "Call the org 1-day metrics report endpoint for specific date"
            "(GET /orgs/{org}/copilot/metrics/reports/organization-1-day/day={DATE}).",
            "This endpoint does NOT return the numbers directly - it returns 'download_links' "
            "(temporary, pre-authorized download URLs). Follow the first link to download the "
            "report file, then decompress it (gunzip = un-zip a .gz-compressed file) to get "
            "readable JSON.",
            "In that JSON, read the 'weekly_active_users' list = how many DISTINCT developers were "
            "active in the 7-day week ending that day.",
        ],
        source="GET /orgs/{org}/copilot/metrics/reports/organization-1-day/day={DATE} "
               "-> follow download_links[0] -> gunzip -> weekly_active_users",
        fetch=fetch_active_users,
        extract=extract_active_users,
    ),
    Datapoint(
        label="Licensed Seats (total provisioned)",
        description="Total Copilot seats provisioned for the organization, whether used "
                    "or not. This is the formula's denominator -- everyone who COULD use it.",
        example="e.g. billing.seat_breakdown.total = 11, so Licensed Seats = 11 (and "
                "adoption = 5 / 11 = 45%).",
        plain="How many Copilot seats you are paying for in total (used or not).",
        paths=["seat_breakdown.total"],
        steps=[
            "Call the Copilot billing endpoint (GET /orgs/{org}/copilot/billing) - "
            "inline JSON, no download link.",
            "Read seat_breakdown.total from the response.",
            "That total is the number of provisioned Copilot seats (the denominator).",
        ],
        source="GET /orgs/{org}/copilot/billing -> seat_breakdown.total",
        fetch=fetch_licensed_seats,
        extract=extract_licensed_seats,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
