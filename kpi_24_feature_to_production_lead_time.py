"""
============================================================================
KPI #24 - Feature-to-Production Lead Time - Velocity index   (Source: Jira)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #24.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : End-to-end elapsed time from feature story creation to
                  production release, measuring the full development pipeline
                  speed including AI's contribution.
  How measured  : Jira issue 'created' timestamp to fix version release
                  timestamp. Report median in calendar days per release.
  Formula       : Median(Production deployment timestamp - Story creation timestamp)
  Unit          : hours      Cadence: Per release     Direction: lower-better
  Interpretation: >45 days=Critical - slow pipeline; 30-45 days=Needs improvement;
                  14-30 days=Good - L3 target; <14 days=Excellent; <7 days=L5

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  This KPI has ONE datapoint: the median lead time in hours.
  We sample the most recently RESOLVED issues in the project (last 28 days) via
  Jira's /rest/api/3/search/jql, pulling only the `created` and `resolutiondate`
  fields. For each sampled issue we compute hoursBetween(created, resolutiondate)
  and then take the MEDIAN across the sample.

  PROXY NOTE (important - this is a documented approximation):
    The Excel "how measured" wants story-creation -> *fix version release*
    timestamp (i.e. the actual production deployment time). Jira's REST API does
    not expose a reliable per-issue "production release" timestamp without a
    release/version + deployment integration, so the verified executive route
    (app/api/executive/jira/route.ts -> kpis.leadTimeHoursMedian) uses the
    issue `resolutiondate` as the END of the pipeline. resolutiondate is the
    closest universally-available signal for "work finished / shipped". This
    script ports that exact behavior. The number is therefore a lead-time PROXY
    keyed on resolution, not on a fix-version release event.

  Result = Median over the sampled issues of
           (resolutiondate - created) expressed in hours.

RUN:
  python kpi_24_feature_to_production_lead_time.py          # trimmed raw payloads
  python kpi_24_feature_to_production_lead_time.py --raw    # full raw payloads
(Needs tools.jira.{apiToken,email,site,projectKey} in your .secrets/project.json.)
============================================================================
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from _toolkit import Datapoint, cfg, jira_get, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "jira"

# How far back the executive route samples recently-resolved issues, and how
# many issues it samples for the lead-time median. These mirror WINDOW_DAYS=28
# and CYCLE_SAMPLE=60 in app/api/executive/jira/route.ts so the ported number
# matches the dashboard.
WINDOW_DAYS = 28
CYCLE_SAMPLE = 60

# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
# (Note: the verbatim Excel text uses a Unicode minus in the formula; we keep the
#  PRINTED value ASCII-only as required, so "-" stands in for that minus sign.)
KPI = {
    "num": 24,
    "name": "Feature-to-Production Lead Time",
    "index": "Velocity",
    "definition": "End-to-end elapsed time from feature story creation to "
                  "production release, measuring the full development pipeline "
                  "speed including AI's contribution.",
    "how_measured": "Jira issue 'created' timestamp to fix version release "
                    "timestamp. Report median in calendar days per release.",
    "formula": "Median(Production deployment timestamp - Story creation timestamp)",
    "unit": "hours",
    "cadence": "Per release",
    "direction": "lower-better",
    "interpretation": ">45 days=Critical - slow pipeline; 30-45 days=Needs "
                      "improvement; 14-30 days=Good - L3 target; <14 days=Excellent; "
                      "<7 days=L5",
    "tools": "Jira",
    "plain": "On average (middle value), how many hours it takes a work item to go "
             "from being created to being finished. Lower is faster; we report it in "
             "hours.",
    # How the formula combines the datapoint values, step by step. The single
    # datapoint is ALREADY the median lead time in hours (the median is taken
    # inside the extractor), so the formula just surfaces that value.
    "steps": [
        "This KPI has only ONE datapoint, 'Median lead time (hours)', and that "
        "datapoint already IS the final answer. There is no second number to "
        "combine it with and no division.",
        "How that one number was built: for each sampled Jira issue we measured "
        "its lead time = resolutiondate (when the issue was marked resolved) minus "
        "created (when the issue was first opened), expressed in hours. Then we took "
        "the MEDIAN of all those per-issue hours. MEDIAN = sort the values from "
        "smallest to largest and take the middle one (for an even count, average the "
        "two middle values); it is preferred over a plain average because one freak "
        "slow issue cannot skew it.",
        "Report that median straight out as the KPI result, in hours. No further "
        "arithmetic is done here: the formula's Median() was already applied inside "
        "the extractor (extract_lead_time_hours).",
        "PROXY (a documented stand-in because the API has no exact field): the result "
        "is keyed on resolutiondate standing in for the fix-version / production "
        "release timestamp. Jira's REST API does not expose a reliable per-issue "
        "'released to production' time, so 'resolved' is used as the end of the "
        "pipeline. The number is therefore a lead-time proxy, not a true "
        "release-event lead time.",
    ],
}


# ===========================================================================
# DATAPOINT 1 of 1 - "Median lead time, hours" (the whole KPI)
# ===========================================================================
# input key  : jiraLeadTimeHours  (lib/kpi/inputs.ts)
# source     : { toolId: "jira", endpointId: "search", field: "leadTimeHoursMedian" }
# resolver   : kv(d['jira'].kpis.leadTimeHoursMedian)
#
# WHERE FROM: Jira Cloud issue search (JQL), sampling recently-resolved issues.
#   POST is what the app uses, but the SAME query is expressible as a GET on the
#   enhanced search endpoint; _toolkit only ships a GET helper (jira_get), so we
#   issue an authenticated GET with the JQL + fields + ordering as query params:
#
#   GET https://{site}/rest/api/3/search/jql
#         ?jql=<project = "KEY" AND resolutiondate >= -28d ORDER BY resolutiondate DESC>
#         &maxResults=60
#         &fields=created,resolutiondate
#       Accept: application/json
#       Authorization: Basic base64(email:apiToken)
#
#   (No X-GitHub-Api-Version header - this is Jira Cloud REST v3, Basic auth.)
#
# THE LOGIC: the response is { "issues": [ { "fields": { "created": "...",
#   "resolutiondate": "..." } }, ... ] }. For each issue with BOTH timestamps we
#   compute hoursBetween(created, resolutiondate) = (resolutiondate - created)/3600s,
#   floored at 0. We then take the MEDIAN of those per-issue hours. This is exactly
#   route.ts:  median(leadTimes) where leadTimes.push(hoursBetween(created, resolved)).
#
#   MAPPING TO EXCEL "how measured": created -> story creation timestamp (exact);
#   resolutiondate -> stands in for "fix version release timestamp" (PROXY, see the
#   PROXY NOTE in the module docstring). Median in hours; the Excel reports median
#   in calendar days (hours / 24) but the catalog unit for this KPI is hours.
async def fetch_lead_time_hours(client):
    token = cfg(TOOL, "apiToken")
    email = cfg(TOOL, "email")
    site = cfg(TOOL, "site")
    project_key = cfg(TOOL, "projectKey")
    if not token or not email or not site:
        raise RuntimeError(
            "Set tools.jira.apiToken, .email and .site in .secrets/project.json"
        )
    # A bounded "in this project" prefix; empty when scoped to the whole site -
    # this mirrors projectClause() in route.ts.
    pc = f'project = "{project_key}" AND ' if project_key else ""
    jql = f"{pc}resolutiondate >= -{WINDOW_DAYS}d ORDER BY resolutiondate DESC"
    # URL-encode the JQL and field list into the query string for the GET.
    from urllib.parse import urlencode
    qs = urlencode({
        "jql": jql,
        "maxResults": CYCLE_SAMPLE,
        "fields": "created,resolutiondate",
    })
    return await jira_get(
        client,
        f"/rest/api/3/search/jql?{qs}",
        email=email,
        token=token,
        site=site,
    )


def _parse_iso(ts):
    # Jira timestamps look like "2026-06-01T12:34:56.000+0000". Normalize the
    # trailing +0000 to +00:00 so datetime.fromisoformat can parse it.
    if not isinstance(ts, str) or not ts:
        return None
    s = ts.strip()
    if len(s) >= 5 and (s[-5] in "+-") and s[-3] != ":":
        s = s[:-2] + ":" + s[-2:]
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _hours_between(a, b):
    # (b - a) in hours, like route.ts hoursBetween: (Date(b) - Date(a)) / 36e5.
    da = _parse_iso(a)
    db = _parse_iso(b)
    if da is None or db is None:
        return None
    return (db - da).total_seconds() / 3600.0


def _median(xs):
    if not xs:
        return None
    s = sorted(xs)
    mid = len(s) // 2
    if len(s) % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def extract_lead_time_hours(raw):
    # `raw` is: { "issues": [ { "fields": { "created": "...", "resolutiondate": "..." } }, ... ] }
    if not isinstance(raw, dict):
        return None
    issues = raw.get("issues")
    if not isinstance(issues, list):
        return None
    lead_times = []
    for it in issues:
        if not isinstance(it, dict):
            continue
        fields = it.get("fields") or {}
        if not isinstance(fields, dict):
            continue
        created = fields.get("created")
        resolved = fields.get("resolutiondate")
        if not created or not resolved:
            continue
        h = _hours_between(created, resolved)
        if h is None:
            continue
        lead_times.append(max(0.0, h))   # floor at 0, like Math.max(0, ...) in route.ts
    return _median(lead_times)


# ===========================================================================
# THE FORMULA - Median(resolution_timestamp - creation_timestamp), in hours
# ===========================================================================
# This KPI's single datapoint is ALREADY the median lead time in hours (the
# median is computed inside extract_lead_time_hours, exactly as the executive
# route does). compute() therefore just passes the value through, guarding None.
# Arguments arrive in the same order as DATAPOINTS below.
def compute(lead_time_hours_median):
    if lead_time_hours_median is None:
        return None
    return lead_time_hours_median


# The inputs the runner fetches, extracts, and feeds to compute() in this order.
DATAPOINTS = [
    Datapoint(
        label="Median lead time, hours (created -> resolutiondate)",
        description="The median, across the sampled recently-resolved issues, of the "
                    "elapsed hours between each issue's fields.created and its "
                    "fields.resolutiondate. This single value IS the whole KPI: the "
                    "median lead time the formula reports (no separate numerator/"
                    "denominator -- the median is computed inside the extractor).",
        example="e.g. of the issues[] returned, 5 had both fields.created and "
                "fields.resolutiondate; their per-issue hoursBetween(created, "
                "resolutiondate) were [72, 96, 120, 168, 240], so the median = 120, "
                "i.e. Median lead time = 120 hours (5 days).",
        plain="The typical (middle) number of hours between when a Jira work item is "
              "opened and when it is marked resolved, across recently finished items.",
        paths=["issues[].fields.created", "issues[].fields.resolutiondate"],
        steps=[
            "Call the Jira Cloud issue-search endpoint: GET /rest/api/3/search/jql on "
            "your Jira site (https://{site}). JQL = Jira Query Language, Jira's filter "
            "syntax. The query we send is: project = \"KEY\" AND resolutiondate >= -28d "
            "ORDER BY resolutiondate DESC. In plain words: only issues in this project, "
            "only those whose resolved-date is within the last 28 days (-28d means '28 "
            "days ago until now'), sorted newest-resolved first. If no projectKey is "
            "configured the 'project = ...' part is dropped and the whole site is "
            "searched.",
            "Limit the call with two query parameters: maxResults=60 (return at most the "
            "60 most-recently-resolved issues = our sample) and fields=created,"
            "resolutiondate (ask Jira to send back ONLY those two date fields per issue, "
            "to keep the payload small).",
            "The response is JSON shaped { \"issues\": [ { \"fields\": { \"created\": "
            "\"...\", \"resolutiondate\": \"...\" } }, ... ] }. Walk the issues[] array "
            "and, for each issue, read fields.created (timestamp the issue was first "
            "opened) and fields.resolutiondate (timestamp it was marked resolved). Skip "
            "any issue that is missing either timestamp.",
            "Both timestamps are ISO-8601 strings like '2026-06-01T12:34:56.000+0000' "
            "(date, then 'T', then time, then a +HHMM timezone offset). Parse each into "
            "a real date-time, then compute that issue's lead time in hours = "
            "(resolutiondate - created) total seconds / 3600. If the result is negative "
            "it is floored to 0 (lead time can never be below zero).",
            "Collect every issue's hours into one list and take the MEDIAN: sort the "
            "list smallest-to-largest and pick the middle value; if the count is even, "
            "average the two middle values. That single median number is this "
            "datapoint's value (and the whole KPI's value).",
            "PROXY (documented stand-in because the API lacks the exact field): "
            "resolutiondate is used in place of the fix-version / production-release "
            "timestamp, because Jira's REST API exposes no reliable per-issue "
            "'released to production' time. So this measures created -> resolved, an "
            "approximation of created -> released.",
        ],
        source="GET /rest/api/3/search/jql?jql=<project AND resolutiondate>=-28d "
               "ORDER BY resolutiondate DESC>&maxResults=60&fields=created,resolutiondate "
               "-> median over issues of hoursBetween(created, resolutiondate). "
               "PROXY: resolutiondate stands in for the fix-version/production "
               "release timestamp (Jira REST exposes no per-issue release time).",
        fetch=fetch_lead_time_hours,
        extract=extract_lead_time_hours,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
