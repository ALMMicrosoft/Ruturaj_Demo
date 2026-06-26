"""
============================================================================
KPI #22 - PR Merge Time - Velocity index   (Source: GitHub)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #22.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : Median time from pull request open to merge, measuring review
                  throughput improvement from AI-assisted code review and
                  higher-quality first submissions.
  How measured  : Query GitHub GraphQL API for all merged PRs: subtract createdAt
                  from mergedAt. Report median separately for AI-reviewed vs
                  human-only reviewed PRs.
  Formula       : Median(PR merge timestamp - PR open timestamp)
  Unit          : hours    Cadence: Weekly    Direction: lower-better
  Interpretation: >5 days=Critical - review bottleneck; 3-5 days=Needs improvement;
                  1-3 days=Good; <24 hours=Excellent - AI review removing bottleneck

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  The verified executive route (app/api/executive/github/route.ts) does NOT use
  the GraphQL API the Excel sheet imagines; it derives the same number from the
  GitHub REST Pulls API as kpis.medianTimeToMergeHours. We PORT that route field
  EXACTLY so the verified value matches the dashboard:
    1. List the repo's CLOSED pull requests, most-recently-updated first
       (GET /repos/{owner}/{repo}/pulls?state=closed&sort=updated&direction=desc
        &per_page=100), paginating a few pages.
    2. Keep only PRs that HAVE a merged_at timestamp AND merged within the latest
       ~28-day window (merged_at >= now - 28 days) - the route's WINDOW_DAYS=28
       KPI window (route accumulates timeToMerge only when mergedAt >= sinceIso).
    3. For each kept PR compute hoursBetween(created_at, merged_at) =
       (merged_at - created_at) / 3600s, clamped at 0 (route's Math.max(0, ...)).
    4. Take the MEDIAN of those per-PR durations.
  That median (route field kpis.medianTimeToMergeHours) IS the KPI value.

  WHY THE FIX MATTERS: the earlier version listed state=all over a single short
  page sorted by update time. That page is dominated by still-OPEN PRs (which
  have no merged_at), so the durations list came out empty and the KPI printed
  NOT COMPUTABLE. Selecting state=closed and paginating a few pages guarantees
  merged PRs are actually in the sample, so the single datapoint resolves.

  NOTE on the "AI-reviewed vs human-only" split in the Excel "how measured":
  the live route does NOT label PRs as AI-reviewed vs human-only (GitHub exposes
  no such flag on a PR), so it reports a SINGLE blended median across all merged
  PRs. This script mirrors that single-median behaviour; the split is not
  computable from the available API and is therefore not invented here.

  NOTE on sampling: the route samples for dashboard responsiveness (most-recently
  -pushed repos, a capped page of PRs per repo). This script verifies one repo
  (tools.github.owner/repo) over a few pages of closed PRs - the same derivation,
  one repo's worth of data.

RUN:
  python kpi_22_pr_merge_time.py          # trimmed raw payloads
  python kpi_22_pr_merge_time.py --raw    # full raw payloads
(Needs tools.github.githubKey + .owner + .repo in your .secrets/project.json.)
============================================================================
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from _toolkit import Call, Datapoint, cfg, gh_get, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github"

# The executive route's API_VERSION constant.
API_VERSION = "2022-11-28"

# The executive route's fixed KPI analysis window (route.ts WINDOW_DAYS).
WINDOW_DAYS = 28

# Closed PRs are listed 100/page; we walk a few pages so merged PRs from the
# latest 28-day window are reliably in the sample (the route caps its per-repo
# PR sample too - this is the same idea, one repo over a handful of pages).
PER_PAGE = 100
PAGES = 3


# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
# ASCII-only: the Excel uses an en-dash in the formula ("timestamp - timestamp")
# and the interpretation; we render those as plain hyphens so the trace prints
# cleanly on any console.
KPI = {
    "num": 22,
    "name": "PR Merge Time",
    "index": "Velocity",
    "definition": "Median time from pull request open to merge, measuring review "
                  "throughput improvement from AI-assisted code review and "
                  "higher-quality first submissions.",
    "how_measured": "Query GitHub GraphQL API for all merged PRs: subtract createdAt "
                    "from mergedAt. Report median separately for AI-reviewed vs "
                    "human-only reviewed PRs.",
    "formula": "Median(PR merge timestamp - PR open timestamp)",
    "unit": "hours",
    "cadence": "Weekly",
    "direction": "lower-better",
    "interpretation": ">5 days=Critical - review bottleneck; 3-5 days=Needs "
                      "improvement; 1-3 days=Good; <24 hours=Excellent - AI review "
                      "removing bottleneck",
    "tools": "GitHub",
    "plain": "The typical time - the median (middle value), not the average - that a pull "
             "request takes to go from opened to merged, in hours. Lower is better: small "
             "numbers mean code gets reviewed and merged fast.",
    # How the formula turns the per-PR durations into the KPI value, step by step.
    # 'PR' = pull request, a GitHub request to merge one branch of code into another.
    # 'merged' = the PR's changes were accepted and combined into the target branch.
    # 'median' = the middle value once all numbers are sorted smallest to largest
    #            (for an even count, the average of the two middle values); it is
    #            used instead of the mean so a few very slow PRs do not skew it.
    "steps": [
        "Start from the list built by the single datapoint below: one number per "
        "merged pull request, where each number is the hours that PR took from "
        "opened to merged, computed as max(0, hoursBetween(created_at, merged_at)) "
        "and kept only if the merge happened in the last 28 days.",
        "Sort that list of hour-durations from smallest to largest.",
        "Take the MEDIAN = the middle value of the sorted list; if the list has an "
        "even number of entries, average the two middle values.",
        "That median, in hours, IS the KPI result - there is no further division, "
        "multiplication, or scaling applied.",
    ],
}


# ===========================================================================
# DATAPOINT 1 of 1 - "Median PR open->merge, hours" (the whole KPI)
# ===========================================================================
# WHERE FROM: GitHub REST Pulls API (inline JSON, no download link), paginated.
#   GET https://api.github.com/repos/{owner}/{repo}/pulls
#         ?state=closed&sort=updated&direction=desc&per_page=100&page={1..N}
#       Accept: application/vnd.github+json
#       X-GitHub-Api-Version: 2022-11-28
#       Authorization: Bearer <githubKey>
#
#   This ports the verified executive route's medianTimeToMergeHours field
#   (app/api/executive/github/route.ts): the route lists repo pulls and builds a
#   timeToMerge[] array of hoursBetween(created_at, merged_at) for PRs whose
#   merged_at falls inside the 28-day window, then reports median(timeToMerge).
#   We select state=closed (a merged PR is always closed) and walk a few pages so
#   merged PRs are actually present - the previous state=all single page returned
#   mostly OPEN PRs and produced an empty list -> NOT COMPUTABLE.
#
# THE LOGIC (ports the route's timeToMerge accumulator + median()):
#   Each page is a JSON array of pull-request objects. We concatenate the pages,
#   then for each PR object:
#     - read created_at  (ISO 8601, when the PR was opened)
#     - read merged_at   (ISO 8601, when it merged; null/absent if never merged)
#   Keep a PR only when it HAS a merged_at AND merged_at >= (now - 28 days)
#   (route: `if (mergedAt && mergedAt >= sinceIso)`). For each kept PR push:
#       hoursBetween(created_at, merged_at)
#         = (merged_at_epoch_ms - created_at_epoch_ms) / 3_600_000
#       clamped at 0 (route uses Math.max(0, ...)).
#   The KPI value is the MEDIAN of that list of per-PR hour durations -- i.e.
#   median(merged_at - created_at), the Excel formula. Median of an even-length
#   list is the mean of the two middle values (same as the route's median()).
#
#   This maps to Excel "how measured" (subtract createdAt from mergedAt over
#   merged PRs, take the median). The GraphQL API and the AI-vs-human split named
#   in the Excel are NOT used by the live route and are not synthesised here -
#   see the module docstring.
async def fetch_merge_times(client):
    token = cfg(TOOL, "githubKey")
    owner = cfg(TOOL, "owner")
    repo = cfg(TOOL, "repo")
    if not token:
        raise RuntimeError("Set tools.github.githubKey in .secrets/project.json")
    if not owner or not repo:
        raise RuntimeError("Set tools.github.owner and tools.github.repo in .secrets/project.json")

    # Paginate a few pages of CLOSED PRs and merge them into ONE Call so the trace
    # reads as a single datapoint. raw is the concatenated list of PR objects.
    merged_prs: list = []
    last_status: int | None = None
    last_url = ""
    pages_pulled = 0
    for page in range(1, PAGES + 1):
        path = (f"/repos/{owner}/{repo}/pulls"
                f"?state=closed&sort=updated&direction=desc"
                f"&per_page={PER_PAGE}&page={page}")
        res = await gh_get(client, path, token=token, api_version=API_VERSION)
        last_status = res.status
        last_url = res.url
        if not res.ok or not isinstance(res.raw, list):
            break
        pages_pulled += 1
        merged_prs.extend(res.raw)
        if len(res.raw) < PER_PAGE:        # last page reached; no more to fetch
            break

    note = (f"listed CLOSED PRs over {pages_pulled} page(s) "
            f"(per_page={PER_PAGE}, sort=updated desc); kept merged_at within "
            f"the last {WINDOW_DAYS} days; raw below is the concatenated PR list")
    # Reuse the last call's redacted headers shape by issuing one already; here we
    # synthesise the merged Call from the recorded url/status and the joined raw.
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "***redacted***",
        "X-GitHub-Api-Version": API_VERSION,
    }
    return Call("GET", last_url, headers, last_status, merged_prs, note)


def _epoch_ms(iso):
    # Parse an ISO 8601 timestamp like "2026-06-01T12:34:56Z" to epoch ms using
    # only the standard library (datetime). Returns None on bad/missing input.
    if not isinstance(iso, str) or not iso:
        return None
    s = iso.strip()
    # GitHub uses a trailing "Z"; Python's fromisoformat wants "+00:00".
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp() * 1000.0


def _hours_between(a_iso, b_iso):
    # (b - a) in hours; mirrors the route's hoursBetween(a, b) = (Date(b)-Date(a))/36e5.
    a = _epoch_ms(a_iso)
    b = _epoch_ms(b_iso)
    if a is None or b is None:
        return None
    return (b - a) / 3_600_000.0


def _median(xs):
    # Median, matching the route's median(): sort, take middle (or mean of the
    # two middle values for even length). Returns None for an empty list.
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return (s[mid - 1] + s[mid]) / 2.0


def extract_merge_times(raw):
    # `raw` is a JSON array of PR objects: [ {created_at, merged_at, ...}, ... ].
    if not isinstance(raw, list):
        return None
    # The route keeps only PRs merged inside the 28-day KPI window
    # (mergedAt >= sinceIso). Compute that cutoff as an epoch-ms threshold.
    cutoff_ms = (
        (datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).timestamp()
        * 1000.0
    )
    durations = []
    for pr in raw:
        if not isinstance(pr, dict):
            continue
        merged_at = pr.get("merged_at")
        created_at = pr.get("created_at")
        if not merged_at:                 # only merged PRs count (route checks mergedAt)
            continue
        merged_ms = _epoch_ms(merged_at)
        if merged_ms is None or merged_ms < cutoff_ms:   # outside the 28-day window
            continue
        hrs = _hours_between(created_at, merged_at)
        if hrs is None:
            continue
        durations.append(max(0.0, hrs))   # route clamps at 0 with Math.max(0, ...)
    # No merged PRs in the 28-day window -> not computable (route returns
    # unavailable "No merged PRs in the sampled window" in that case).
    return _median(durations)


# ===========================================================================
# THE FORMULA - Median(PR merge timestamp - PR open timestamp)
# ===========================================================================
# Single-input KPI: the extracted median IS the result. compute() simply passes
# it through, guarding None. Argument order matches DATAPOINTS below.
def compute(median_merge_hours):
    if median_merge_hours is None:
        return None
    return median_merge_hours


# The inputs the runner fetches, extracts, and feeds to compute() in this order.
DATAPOINTS = [
    Datapoint(
        label="Median PR open->merge, hours (latest 28-day window)",
        description="The median (middle value) number of hours each merged pull request "
                    "took from opened to merged, across PRs whose merge happened in the "
                    "last 28 days. This single value IS the whole KPI (there is no separate "
                    "numerator/denominator): for each kept PR we compute its open-to-merge "
                    "hours, then report the median of all those per-PR durations.",
        example="e.g. three pull requests merged within the last 28 days took 12.0, 36.0, "
                "and 60.0 hours each from opened to merged; sorted that is [12.0, 36.0, "
                "60.0], the middle value is 36.0, so the KPI value is 36 hours.",
        plain="The typical (middle) number of hours a pull request takes to get merged, "
              "looking only at PRs merged in the last 28 days.",
        paths=["[].merged_at", "[].created_at"],
        steps=[
            "A pull request (PR) is a GitHub request to merge code changes; it is 'merged' "
            "when those changes are accepted. Call GitHub's REST 'list pull requests' "
            "endpoint for this repo, asking only for CLOSED PRs, newest-updated first: "
            "GET https://api.github.com/repos/{owner}/{repo}/pulls?state=closed&sort=updated"
            "&direction=desc&per_page=100 (per_page=100 = up to 100 PRs per response page). "
            "Send header X-GitHub-Api-Version: 2022-11-28 and Authorization: Bearer <token>.",
            "Fetch up to 3 pages (page=1, then page=2, then page=3, stopping early if a page "
            "returns fewer than 100 PRs) and join all the returned PR objects into one list. "
            "Closed PRs are requested because a merged PR is always closed, so this guarantees "
            "merged PRs appear in the sample.",
            "From that combined list keep a PR only if BOTH are true: (a) it has a non-empty "
            "merged_at field, which drops PRs that were closed without merging and PRs still "
            "open; and (b) its merged_at is within the last 28 days, i.e. merged_at is greater "
            "than or equal to (the moment this runs) minus 28 days.",
            "For each kept PR read two timestamps in ISO 8601 format (e.g. "
            "'2026-06-01T12:34:56Z', a standard date-time text): created_at (when the PR was "
            "opened) and merged_at (when it was merged). Compute the gap in hours as "
            "(merged_at - created_at) converted to hours = (difference in milliseconds) / "
            "3,600,000, then replace any negative result with 0 via max(0, ...).",
            "Collect all those per-PR hour values into a list and take its MEDIAN: sort the "
            "list smallest to largest and take the middle value (for an even count, average "
            "the two middle values). That median in hours is this datapoint's value. If no "
            "merged PR fell inside the 28-day window the list is empty and the value is "
            "reported as not computable.",
        ],
        source="GET /repos/{owner}/{repo}/pulls?state=closed&sort=updated&direction=desc"
               "&per_page=100 (a few pages) -> for PRs with merged_at within the last "
               "28 days push max(0, hoursBetween(created_at,merged_at)) -> median()",
        fetch=fetch_merge_times,
        extract=extract_merge_times,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
