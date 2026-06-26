"""
============================================================================
KPI #25 - DORA: Deployment Frequency - Velocity index   (Source: GitHub)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #25.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : How often code is successfully deployed to production. DORA
                  Elite benchmark is multiple deployments per day. Measures
                  CI/CD pipeline maturity and AI acceleration.
  How measured  : Count successful production deployments per week from pipeline
                  events API. Map to DORA tiers: Elite >1/day, High 1/week-1/day,
                  Medium 1/month-1/week, Low <1/month.
  Formula       : Count(successful production deployments) per week
  Unit          : deploys/week   Cadence: Weekly   Direction: higher-better
  Interpretation: <1/month=Low/Critical; 1/month-1/week=Medium;
                  1/week-1/day=High/Good; >1/day=Elite - L5 target with
                  AI-enabled CI automation

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  GitHub exposes no single "production deployments per week" number, so the
  verified executive route (app/api/executive/github/route.ts) uses a DOCUMENTED
  PROXY: it lists GitHub Actions workflow runs over a fixed 28-day window and
  counts the runs that represent a successful deploy. A run counts as a
  deployment when ALL of these hold:
      conclusion == "success"
      event in {"deployment", "release", "push"}
      run name matches /deploy|release|cd\\b/  (case-insensitive)
  That count of successful deploy runs in the 28-day window is then divided by
  the number of weeks in the window (28 / 7 = 4) to give deployments per week.

      deployments_per_week = successful_deploy_runs_in_28d / 4

  This is exactly route.ts:  deploymentFrequencyPerWeek = deploymentRuns / weeks
  (weeks = WINDOW_DAYS / 7 = 4), labelled "derived" / "Actions proxy" in the UI,
  and is the single input inputs.ts maps for this KPI (ghDeploymentFreqPerWeek ->
  github.deploymentFrequencyPerWeek). There is exactly ONE datapoint: any extra
  "cross-check" input that can return None would gate the whole KPI via the
  runner's all-non-None rule, so it is deliberately omitted. An idle repo with
  zero deploy runs reports 0.0 deploys/week (a valid number), not "NOT
  COMPUTABLE".

RUN:
  python kpi_25_dora_deployment_frequency.py          # trimmed raw payloads
  python kpi_25_dora_deployment_frequency.py --raw    # full raw payloads
(Needs tools.github.githubKey + .owner + .repo in your .secrets/project.json.)
============================================================================
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from _toolkit import Datapoint, cfg, gh_get, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github"

# The executive route's fixed analysis window. WINDOW_DAYS / 7 = weeks.
WINDOW_DAYS = 28
WEEKS = WINDOW_DAYS / 7  # = 4.0 ; the divisor the route uses


# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
KPI = {
    "num": 25,
    "name": "DORA: Deployment Frequency",
    "index": "Velocity",
    "definition": "How often code is successfully deployed to production. DORA "
                  "Elite benchmark is multiple deployments per day. Measures CI/CD "
                  "pipeline maturity and AI acceleration.",
    "how_measured": "Count successful production deployments per week from pipeline "
                    "events API. Map to DORA tiers: Elite >1/day, High 1/week-1/day, "
                    "Medium 1/month-1/week, Low <1/month.",
    "formula": "Count(successful production deployments) per week",
    "unit": "deploys/week",
    "cadence": "Weekly",
    "direction": "higher-better",
    "interpretation": "<1/month=Low/Critical; 1/month-1/week=Medium; "
                      "1/week-1/day=High/Good; >1/day=Elite - L5 target with "
                      "AI-enabled CI automation",
    "tools": "GitHub",
    "plain": "How many times per week your team successfully ships code to production. "
             "Higher is better: shipping many times a week (or daily) means a fast, "
             "automated pipeline; shipping less than once a month is slow.",
    # How the formula turns the single datapoint into the KPI result, step by step.
    "steps": [
        "Start from the one datapoint: the count of successful deploy-like GitHub "
        "Actions runs (automated pipeline jobs) seen in the last 28 days, already "
        "divided by 4 (because 28 days / 7 days = 4 weeks) to give a per-week rate.",
        "There is no further math to do: this single value already IS the "
        "'deployments per week' number the formula asks for, so the KPI result equals "
        "that datapoint unchanged.",
        "Note on the word 'proxy': GitHub has no exact 'production deployment per week' "
        "field, so we use a documented stand-in (proxy) -- successful deploy/release/cd "
        "Actions runs divided by 4 weeks -- as the closest measurable equivalent.",
    ],
}


# Compute the route's `created=>=YYYY-MM-DD` window-start filter once (28 days ago,
# UTC), matching route.ts: sinceIso = now - WINDOW_DAYS*864e5; windowStart = date.
def _window_start_date() -> str:
    since = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
    return since.date().isoformat()  # "YYYY-MM-DD"


# Regex + event set that define a "deployment" run, ported verbatim from route.ts.
_DEPLOY_NAME_RE = re.compile(r"deploy|release|cd\b", re.IGNORECASE)
_DEPLOY_EVENTS = {"deployment", "release", "push"}


# ===========================================================================
# DATAPOINT 1 of 1 - "Deployments per week" (the KPI value)
# ===========================================================================
# WHERE FROM: GitHub Actions runs for the repo, filtered to the 28-day window.
#   GET https://api.github.com/repos/{owner}/{repo}/actions/runs
#         ?created=>={windowStart}&per_page=100
#       Accept: application/vnd.github+json
#       X-GitHub-Api-Version: 2022-11-28
#       Authorization: Bearer <githubKey>
#   (windowStart = today - 28 days, UTC date; route.ts uses created=>= on this
#    endpoint with the same window.)
#
# THE LOGIC (ports route.ts deploymentRuns -> deploymentFrequencyPerWeek):
#   The payload is { "workflow_runs": [ {status, conclusion, event, name, ...}, ... ] }.
#   For each run, count it as a successful deployment when:
#       conclusion == "success"
#       AND event in {"deployment", "release", "push"}
#       AND name matches /deploy|release|cd\b/ (case-insensitive)
#   deploymentRuns = number of runs satisfying all three.
#   Then per the Excel "per week": divide by WEEKS (28/7 = 4):
#       deployments_per_week = deploymentRuns / 4
#   This is a DOCUMENTED PROXY for production deployments: GitHub has no generic
#   "production deployment" event in the REST runs feed, so successful
#   deploy/release/cd Actions runs stand in for them (route.ts labels it
#   "derived" / "Actions proxy"). It is the single input inputs.ts maps for this
#   KPI; no second datapoint is fetched, so nothing can gate the result to None.
async def fetch_deployment_frequency(client):
    token = cfg(TOOL, "githubKey")
    owner = cfg(TOOL, "owner")
    repo = cfg(TOOL, "repo")
    if not token:
        raise RuntimeError("Set tools.github.githubKey in .secrets/project.json")
    if not owner or not repo:
        raise RuntimeError("Set tools.github.owner and tools.github.repo in .secrets/project.json")
    start = _window_start_date()
    # GitHub wants the '>=' encoded; %3E%3D = '>='. Mirrors route.ts created=>=.
    path = (f"/repos/{owner}/{repo}/actions/runs"
            f"?created=%3E%3D{start}&per_page=100")
    return await gh_get(client, path, token=token, api_version="2022-11-28")


def extract_deployment_frequency(raw):
    # raw is: { "total_count": N, "workflow_runs": [ {conclusion, event, name, ...}, ... ] }
    if not isinstance(raw, dict):
        return None
    runs = raw.get("workflow_runs")
    if not isinstance(runs, list):
        return None
    deployment_runs = 0
    for it in runs:
        if not isinstance(it, dict):
            continue
        conclusion = it.get("conclusion") or ""
        event = it.get("event") or ""
        name = it.get("name") or ""
        if (conclusion == "success"
                and event in _DEPLOY_EVENTS
                and _DEPLOY_NAME_RE.search(str(name))):
            deployment_runs += 1
    # Excel "per week": divide the 28-day count by the number of weeks (4).
    # Zero deploy runs is a valid 0.0 deploys/week (an idle repo), NOT None -- so
    # this single datapoint always resolves and the KPI stays computable.
    return deployment_runs / WEEKS


# ===========================================================================
# THE FORMULA - Count(successful production deployments) per week
# ===========================================================================
# Exactly one argument, in the same order as DATAPOINTS below. The value IS the
# Actions-runs proxy deployments-per-week, mirroring route.ts deploymentFrequencyPerWeek.
def compute(deployments_per_week):
    # Single source; guard a None (only happens if the payload shape was wrong).
    if deployments_per_week is None:
        return None
    return deployments_per_week


# The input the runner fetches, extracts, and feeds to compute().
DATAPOINTS = [
    Datapoint(
        label="Deployments per week (DORA - Actions-runs proxy, the KPI value)",
        description="The KPI value itself: how many successful production deployments "
                    "happened per week, derived by counting deploy-like GitHub Actions "
                    "runs in the 28-day window and dividing by WEEKS (4). This single "
                    "value IS the formula result (no separate numerator/denominator).",
        example="e.g. of the workflow_runs[] in the window, 8 had conclusion=='success' "
                "AND event in {deployment,release,push} AND name~/deploy|release|cd/i, "
                "so deployment_runs = 8 and 8 / 4 weeks = 2.0 deploys/week.",
        plain="How many times a week the project shipped to production, counted from the "
              "successful deploy jobs GitHub ran in the last 28 days, divided by 4 weeks.",
        paths=["workflow_runs[].conclusion", "workflow_runs[].event", "workflow_runs[].name"],
        steps=[
            "Work out the start of the window: take today's date in UTC (the global "
            "reference time zone) and subtract 28 days. Call this the 28-days-ago date.",
            "Call GitHub's Actions-runs endpoint for the repo, asking only for runs "
            "created on or after that date: GET /repos/{owner}/{repo}/actions/runs"
            "?created=>={28-days-ago}&per_page=100 . ('Actions runs' are the automated "
            "pipeline jobs GitHub executes; 'created=>=DATE' means created on or after "
            "DATE -- in the real URL the '>=' is percent-encoded as %3E%3D; per_page=100 "
            "returns at most the first 100 runs, no extra pages are fetched.) The reply "
            "is JSON (text the program parses) holding a workflow_runs[] array -- one "
            "object per run.",
            "Loop over every run in workflow_runs[] and read three fields from each: "
            "conclusion (how the run ended, e.g. 'success' or 'failure'), event (what "
            "triggered the run, e.g. 'push', 'release', 'deployment'), and name (the "
            "workflow's title).",
            "Count a run as one successful production deployment only when ALL three "
            "hold: conclusion equals exactly 'success'; AND event is one of the set "
            "{deployment, release, push}; AND name contains the words deploy, release, "
            "or cd ignoring upper/lower case (this is a regex -- a text-pattern match -- "
            "written /deploy|release|cd\\b/i, where '\\b' means 'cd' match as a whole "
            "word -- the boundary marker applies ONLY to 'cd', so 'cd' matches but 'cdk' "
            "does not, whereas 'deploy' and 'release' have no boundary and match anywhere, "
            "even inside a longer word like 'redeploy'). This rule is a DOCUMENTED PROXY (a "
            "deliberate stand-in) because GitHub's runs feed has no exact 'production "
            "deployment' marker, so successful deploy/release/cd runs are used instead.",
            "Add up the runs that pass all three checks into a running total called "
            "deployment_runs (a plain count over the 28-day window).",
            "Divide deployment_runs by 4 (the number of weeks in 28 days, since 28 / 7 = "
            "4) to get the final deployments-per-week rate. If no runs matched, the count "
            "is 0 and the result is 0.0 deploys/week (a valid number for an idle repo), "
            "not a missing value.",
        ],
        source="GET /repos/{owner}/{repo}/actions/runs?created=>={28d-ago}&per_page=100 "
               "-> count workflow_runs where conclusion==success AND "
               "event in {deployment,release,push} AND name~/deploy|release|cd/i, "
               "then divide by 4 weeks (DOCUMENTED Actions-runs proxy for prod deploys; "
               "mirrors route.ts deploymentFrequencyPerWeek = deploymentRuns / weeks)",
        fetch=fetch_deployment_frequency,
        extract=extract_deployment_frequency,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
