"""
============================================================================
KPI #23 - Sprint Completion Rate - Velocity index   (Source: Jira)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #23.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx):
  Definition    : % of committed sprint story points delivered by end-of-sprint,
                  measuring delivery predictability and AI impact on estimation
                  accuracy.
  How measured  : Query Jira sprint report endpoint for completed story points
                  divided by committed story points x 100. Track trend over
                  rolling 4 sprints.
  Formula       : (Story points completed by sprint end / Story points committed
                  at sprint start) x 100
  Unit          : %        Cadence: Per sprint     Direction: higher-better
  Interpretation: <70%=Critical (teams chronically over-committing);
                  70-80%=Needs improvement; 80-90%=Good (L3 target);
                  >90%=Excellent; 95%+=L5

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  Jira has no single "sprint report" REST endpoint that returns a ready-made
  committed-vs-completed number, so this script RECONSTRUCTS it from the public
  Agile API, BY STORY POINTS, exactly as the Excel formula asks:

    1. Find which Jira field holds story points (its id differs per site, e.g.
       customfield_10016). We auto-discover it from GET /rest/api/3/field by
       looking for a field named "Story Points" or "Story point estimate".
    2. List the most recent CLOSED sprints on the board and keep the latest 4
       (the Excel "rolling 4 sprints").
    3. For each sprint, pull ALL its issues (paginated - no 100-issue cap), and
       add up story points:
         committed_points = sum of story points over every issue in the sprint
         completed_points = sum of story points over the DONE issues only
       An issue is "done" when it has a resolution (fields.resolution is set) OR
       its status category key == "done". Per-sprint ratio = completed_points /
       committed_points.
    4. Sprint Completion Rate (ratio form) = MEAN of those per-sprint ratios.
       compute() multiplies by 100 to match the Excel formula's "x 100".

  Note: story points are the default. If NONE of the sampled sprints have any
  points (nothing was estimated), points give 0/0, so the script FALLS BACK to
  ISSUE COUNT (completed issues / committed issues) and labels the trace
  'method: issue-count'. Issue counts are captured alongside points either way, so
  you always see both.

RUN:
  python kpi_23_sprint_completion_rate.py          # trimmed raw payloads
  python kpi_23_sprint_completion_rate.py --raw    # full raw payloads
(Needs tools.jira.{apiToken,email,site,boardId} in your .secrets/project.json.
 boardId is REQUIRED - sprints only exist under a Scrum board scope. The board
 must estimate in STORY POINTS for this KPI to compute.)
============================================================================
"""
from _toolkit import Datapoint, cfg, jira_get, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "jira"

# How many recent CLOSED sprints to roll into the mean. The Excel "how measured"
# asks for a rolling 4-sprint trend, so we use 4.
SPRINT_SAMPLE = 4

# Page size when fetching a sprint's issues (we page through ALL of them).
ISSUE_PAGE = 50

# Field NAMES Jira uses for story points, in fallback preference order (the
# team-managed "Story point estimate" first). Only used if the board configuration
# does not expose its estimation field.
STORY_POINT_FIELD_NAMES = ("story point estimate", "story points")


# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. -----------------------
KPI = {
    "num": 23,
    "name": "Sprint Completion Rate",
    "index": "Velocity",
    "definition": "% of committed sprint story points delivered by end-of-sprint, "
                  "measuring delivery predictability and AI impact on estimation accuracy.",
    "how_measured": "Query Jira sprint report endpoint for completed story points "
                    "divided by committed story points x 100. Track trend over "
                    "rolling 4 sprints.",
    "formula": "(Story points completed by sprint end / Story points committed at "
               "sprint start) x 100",
    "unit": "%",
    "cadence": "Per sprint",
    "direction": "higher-better",
    "interpretation": "<70%=Critical - teams chronically over-committing; "
                      "70-80%=Needs improvement; 80-90%=Good - L3 target; "
                      ">90%=Excellent; 95%+=L5",
    "tools": "Jira",
    "plain": "Of the work a team promised to finish in its sprints (measured in story "
             "points), what share they actually finished. High = the team reliably "
             "delivers what it plans; low = the team keeps planning more than it can do.",
    "steps": [
        "Start from the single datapoint. It is already a ratio between 0 and 1 "
        "(0 = no planned points finished, 1 = all of them). It is the average, across "
        "the last 4 closed sprints, of each sprint's 'completed story points / "
        "committed story points' fraction.",
        "Multiply that 0..1 ratio by 100 to turn it into a percentage (e.g. 0.85 "
        "becomes 85%), matching the Excel formula's 'x 100'. That percentage is the "
        "KPI result.",
    ],
}


# ===========================================================================
# DATAPOINT 1 of 1 - "Sprint completion ratio by story points" (0..1)
# ===========================================================================
# WHERE FROM: the Jira Cloud REST/Agile API, reconstructed from several GET calls
# (HTTP Basic email:apiToken against https://{site}):
#
#   (a) discover the story-point field id (its id differs per Jira site)
#       GET https://{site}/rest/api/3/field
#       -> array of field objects; pick the one whose name is "Story Points" or
#          "Story point estimate"; remember its id (e.g. customfield_10016).
#
#   (b) recent CLOSED sprints on the board
#       GET https://{site}/rest/agile/1.0/board/{boardId}/sprint?state=closed&maxResults=50
#       -> values[] of sprints; keep the latest SPRINT_SAMPLE (4) by completeDate.
#
#   (c) per-sprint issues, PAGED so every issue is counted (no 100 cap)
#       GET https://{site}/rest/agile/1.0/sprint/{sprintId}/issue
#           ?startAt=N&maxResults=50&fields=status,resolution,{storyPointFieldId}
#       -> issues[]; loop startAt until all `total` issues are fetched.
#
# THE LOGIC (story points, matching the Excel formula):
#   For each sprint:
#       committed_points = sum of story points over EVERY issue
#       completed_points = sum of story points over the DONE issues
#                          (done = fields.resolution set OR status category 'done')
#       ratio            = completed_points / committed_points     (per-sprint)
#   Sprint Completion Rate (ratio form) = mean(ratio over the 4 closed sprints).
#   This datapoint returns that 0..1 mean; compute() multiplies by 100.
#
# fetch returns a synthetic "Call" whose .raw bundles every sprint's points so the
# trace shows exactly what was summed and divided.
_SP_FIELDS: dict = {}


async def _candidate_point_fields(client, board_id, email, token, site):
    """Ordered, de-duplicated candidate story-point fields to READ from.

    A Jira site often has more than one points field (e.g. 'Story Points' AND
    'Story point estimate'), and the data may sit in a different one than the board
    config names, or the board's field may be read-only while issues are pointed in
    another. So we collect candidates - the board's CONFIGURED estimation field
    first, then any field literally named like story points - and the caller later
    uses whichever actually carries the estimates."""
    if "list" in _SP_FIELDS:
        return _SP_FIELDS["list"]
    cands = []
    cfg_call = await jira_get(
        client, f"/rest/agile/1.0/board/{board_id}/configuration",
        email=email, token=token, site=site)
    if cfg_call.ok and isinstance(cfg_call.raw, dict):
        field = (cfg_call.raw.get("estimation") or {}).get("field") or {}
        if field.get("fieldId"):
            cands.append((field["fieldId"], field.get("displayName") or field["fieldId"]))
    call = await jira_get(client, "/rest/api/3/field", email=email, token=token, site=site)
    for f in (call.raw if isinstance(call.raw, list) else []):
        if isinstance(f, dict) and (f.get("name") or "").strip().lower() in STORY_POINT_FIELD_NAMES:
            cands.append((f.get("id"), f.get("name")))
    seen, out = set(), []
    for fid, name in cands:
        if fid and fid not in seen:
            seen.add(fid)
            out.append((fid, name))
    if not out:
        raise RuntimeError(
            "Could not find any story-point field (board configuration estimation.field, "
            "or a field named 'Story Points' / 'Story point estimate' via /rest/api/3/field).")
    _SP_FIELDS["list"] = out
    return out


def _points(issue, field_ids):
    """Story points for an issue: the first candidate field that has a numeric value."""
    f = issue.get("fields") or {}
    for fid in field_ids:
        v = f.get(fid)
        if isinstance(v, (int, float)):
            return float(v)
    return 0.0


def _is_done(issue):
    f = issue.get("fields") or {}
    status = f.get("status") or {}
    cat = (status.get("statusCategory") or {}).get("key") if isinstance(status, dict) else ""
    return bool(f.get("resolution")) or cat == "done"


async def _all_sprint_issues(client, sid, fields_param, email, token, site):
    """Every issue in a sprint, paged (no 100-issue cap). `fields_param` is the
    comma-separated Jira fields= value (status,resolution + candidate point fields)."""
    issues, start = [], 0
    for _ in range(40):  # safety cap (40 * 50 = 2000 issues/sprint)
        call = await jira_get(
            client,
            f"/rest/agile/1.0/sprint/{sid}/issue?startAt={start}&maxResults={ISSUE_PAGE}"
            f"&fields={fields_param}",
            email=email, token=token, site=site)
        if not call.ok or not isinstance(call.raw, dict):
            break
        batch = call.raw.get("issues") or []
        issues.extend(batch)
        total = call.raw.get("total")
        start += len(batch)
        if not batch or len(batch) < ISSUE_PAGE or (total is not None and start >= total):
            break
    return issues


async def fetch_sprint_completion(client):
    email = cfg(TOOL, "email")
    token = cfg(TOOL, "apiToken")
    site = cfg(TOOL, "site").replace("https://", "").replace("http://", "").rstrip("/")
    board_id = cfg(TOOL, "boardId")
    if not site or not email or not token:
        raise RuntimeError(
            "Set tools.jira.site, .email and .apiToken in .secrets/project.json")
    if not board_id:
        raise RuntimeError(
            "Set tools.jira.boardId in .secrets/project.json - sprint completion "
            "is a board-scoped (Scrum) metric; without a board there are no sprints.")

    candidates = await _candidate_point_fields(client, board_id, email, token, site)
    cand_ids = [c[0] for c in candidates]
    fields_param = "status,resolution," + ",".join(cand_ids)

    # (b) most recent CLOSED sprints on the board.
    sprints_call = await jira_get(
        client, f"/rest/agile/1.0/board/{board_id}/sprint?state=closed&maxResults=50",
        email=email, token=token, site=site)
    sprints = []
    if sprints_call.ok and isinstance(sprints_call.raw, dict):
        values = sprints_call.raw.get("values") or []
        ended = [s for s in values if isinstance(s, dict)
                 and (s.get("completeDate") or s.get("endDate"))]
        ended.sort(key=lambda s: s.get("completeDate") or s.get("endDate") or "", reverse=True)
        sprints = ended[:SPRINT_SAMPLE]

    # (c) pull every sprint's issues (paged), then pick the candidate points field
    #     that ACTUALLY carries estimates (the highest total across sampled issues).
    sprint_issues = []
    for s in sprints:
        if s.get("id") is None:
            continue
        sprint_issues.append(
            (s, await _all_sprint_issues(client, s["id"], fields_param, email, token, site)))

    field_totals = {fid: 0.0 for fid in cand_ids}
    for _s, issues in sprint_issues:
        for it in issues:
            fvals = (it.get("fields") or {}) if isinstance(it, dict) else {}
            for fid in cand_ids:
                v = fvals.get(fid)
                if isinstance(v, (int, float)):
                    field_totals[fid] += v
    used_field = (max(field_totals, key=lambda k: field_totals[k])
                  if any(field_totals.values()) else (cand_ids[0] if cand_ids else None))
    used_name = next((n for i, n in candidates if i == used_field), used_field)

    per_sprint = []
    for s, issues in sprint_issues:
        committed_pts = completed_pts = 0.0
        committed_issues = completed_issues = 0
        for it in issues:
            if not isinstance(it, dict):
                continue
            pts = _points(it, [used_field]) if used_field else 0.0
            committed_pts += pts
            committed_issues += 1
            if _is_done(it):
                completed_pts += pts
                completed_issues += 1
        per_sprint.append({
            "sprintId": s.get("id"),
            "name": s.get("name"),
            "committedPoints": committed_pts,
            "completedPoints": completed_pts,
            "pointsRatio": (completed_pts / committed_pts) if committed_pts > 0 else None,
            "committedIssues": committed_issues,
            "completedIssues": completed_issues,
            "issueRatio": (completed_issues / committed_issues) if committed_issues > 0 else None,
            "completionRatio": None,
        })

    # The Excel formula asks for STORY POINTS. But if the sampled sprints carry NO
    # points at all (nothing was estimated), points give 0/0 = nothing to compute,
    # so we FALL BACK to ISSUE COUNT (completed issues / committed issues) and say so
    # plainly. Points stay the default whenever any sprint is pointed.
    total_points = sum(p["committedPoints"] for p in per_sprint)
    method = "story-points" if total_points > 0 else "issue-count"
    for p in per_sprint:
        p["completionRatio"] = p["pointsRatio"] if method == "story-points" else p["issueRatio"]

    base = sprints_call  # reuse status/url/headers of the principal call for the trace
    # This .raw is a summary COMPUTED by the script. The viewer also shows the actual
    # Jira API responses (board config, field list, sprint list, per-sprint issue
    # pages) separately under "Actual API responses", so every number is verifiable.
    base.raw = {
        "method": method,
        "storyPointField": {"id": used_field, "name": used_name},
        "candidatePointFields": [{"id": i, "name": n} for i, n in candidates],
        "sprintsConsidered": len(sprints),
        "perSprint": per_sprint,
    }
    base.note = (
        (f"computed by STORY POINTS (the Excel method) using the field that actually "
         f"holds the estimates: '{used_name}' ({used_field})"
         if method == "story-points" else
         f"NO story points were set on these sprints (checked "
         f"{', '.join(i for i, _ in candidates)}), so FELL BACK to ISSUE COUNT - the "
         "completion rate below is completed issues / committed issues, NOT story points") +
        "; per closed sprint ratio = completed/committed; value = mean of the per-sprint "
        f"ratios over the last {SPRINT_SAMPLE} closed sprints (issues paged, no cap)")
    return base


def extract_sprint_completion(raw):
    # `raw` is the bundle from fetch_sprint_completion. The KPI value (0..1) is the
    # MEAN of the per-sprint completed/committed POINT ratios; sprints with zero
    # committed points contribute None and are skipped.
    if not isinstance(raw, dict):
        return None
    ratios = [s.get("completionRatio") for s in (raw.get("perSprint") or [])
              if isinstance(s, dict) and s.get("completionRatio") is not None]
    if not ratios:
        return None
    return sum(ratios) / len(ratios)


# ===========================================================================
# THE FORMULA - (completed story points / committed story points) x 100
# ===========================================================================
# The single datapoint already carries the mean completed/committed POINT ratio
# (0..1) across the last 4 closed sprints. The Excel formula expresses it as a
# percent, so we multiply by 100. Arguments arrive in DATAPOINTS order.
def compute(completion_ratio):
    if completion_ratio is None:        # guard: no sprint had any committed points
        return None
    return completion_ratio * 100


DATAPOINTS = [
    Datapoint(
        label="Sprint completion ratio (mean completed/committed story points, last 4 closed sprints)",
        description="The whole formula in one number: the mean per-sprint ratio of completed "
                    "story points to committed story points (0..1) across the last 4 closed "
                    "sprints. Per sprint, committed = sum of story points over all issues and "
                    "completed = sum of story points over the done issues; ratio = "
                    "completed/committed. compute() only multiplies the mean by 100.",
        example="e.g. across 4 closed sprints, one committed 20 points and completed 18 "
                "(ratio 0.90), another committed 25 and completed 20 (0.80); the mean of the "
                "per-sprint ratios is 0.85, so the ratio = 0.85 and the KPI = 85%.",
        plain="On average across the last 4 finished sprints, the share of the story points "
              "the team committed to that it actually completed (1.0 = all of them).",
        paths=["perSprint[].completionRatio", "perSprint[].committedPoints",
               "perSprint[].completedPoints", "perSprint[].committedIssues",
               "perSprint[].completedIssues"],
        steps=[
            "Find which field THIS board estimates story points in: call GET https://{site}/"
            "rest/agile/1.0/board/{boardId}/configuration (HTTP Basic auth, email:apiToken) and "
            "read estimation.field.fieldId - the board's own setting, which is authoritative "
            "even when the site has more than one points field. If that is missing, fall back "
            "to GET /rest/api/3/field and pick a field named 'Story point estimate' or 'Story "
            "Points'. The field id (e.g. customfield_10016) differs per site, so we look it up "
            "instead of hard-coding it.",
            "A 'sprint' is a fixed time-box (often 2 weeks) of planned work; a 'closed' sprint "
            "has ended. Call GET https://{site}/rest/agile/1.0/board/{boardId}/sprint?"
            "state=closed&maxResults=50, read values[], keep only sprints with a completeDate "
            "or endDate, sort newest-first, and take the most recent 4 (the Excel 'rolling 4 "
            "sprints'). 'board' = the Scrum board; boardId comes from .secrets/project.json.",
            "For each kept sprint, fetch ALL its issues, a page at a time: GET https://{site}/"
            "rest/agile/1.0/sprint/{sprintId}/issue?startAt=N&maxResults=50&fields=status,"
            "resolution,{storyPointFieldId}. Keep increasing startAt by 50 until the response's "
            "'total' is reached, so a sprint with more than 100 issues is fully counted (no "
            "cap). 'issue' = one Jira ticket; fields= keeps only the fields we need.",
            "Read each issue's story points from the field found in step 1 (a number; a blank/"
            "missing estimate counts as 0 points). Sum them two ways per sprint: committed "
            "points = the points of EVERY issue (the work planned); completed points = the "
            "points of the DONE issues only. An issue is 'done' if its fields.resolution is set "
            "(e.g. 'Done'/'Fixed') OR its fields.status.statusCategory.key equals 'done' (Jira "
            "sorts every status into 'new', 'indeterminate', or 'done'). This sprint's "
            "completionRatio = completed points / committed points.",
            "Take the mean (add the values, divide by how many) of the per-sprint ratios "
            "across the 4 sprints; that average (0 to 1) is this datapoint's value. IMPORTANT "
            "fallback: if NONE of the sampled sprints have any story points (nothing was "
            "estimated), the points formula would be 0/0, so the script falls back to ISSUE "
            "COUNT (completed issues / committed issues) and labels the result 'method: "
            "issue-count' in the trace. Points are always used whenever at least one sprint is "
            "pointed.",
        ],
        source="GET /rest/api/3/field (find story-point field) + GET /rest/agile/1.0/board/"
               "{boardId}/sprint?state=closed -> last 4 closed sprints; per sprint GET "
               "/rest/agile/1.0/sprint/{id}/issue (paged) -> committedPoints = sum of points, "
               "completedPoints = sum of points on done issues; ratio = completed/committed "
               "points; value = mean of those ratios (story-point method, matches the Excel).",
        fetch=fetch_sprint_completion,
        extract=extract_sprint_completion,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
