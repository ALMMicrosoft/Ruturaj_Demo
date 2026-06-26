"""
============================================================================
KPI #17 - Rework Rate (AI-Attributed) - Quality index   (Source: GitHub)
============================================================================
VERIFY THIS SCRIPT AGAINST THE MASTER SHEET ROW FOR KPI #17.

Row num=17 (Rework Rate (AI-Attributed)):
  What measured : % of AI-assisted code changes that require substantial revision
                  shortly after creation - indicates poor first-pass AI quality.
  How measured  : Identify AI-assisted PRs whose follow-up commits modify >50% of
                  the original lines within 48 hours. Divide by total AI-assisted
                  PRs x 100.
  Datapoints    : 1. Total AI-assisted PRs
                  2. AI-assisted PRs with >50% line rework within 48 hours
  Formula       : (AI-assisted PRs with >50% line rework within 48h /
                   Total AI-assisted PRs) x 100
  Unit          : %        Cadence: Weekly        Direction: lower-better (banded)
  Interpretation: <5%=Excellent; 5-10%=Acceptable; 10-15%=Needs improvement;
                  >15%=Critical
  Notes         : Feeds Engineering Capacity Reclaimed + Cost Per Feature. LinearB
                  provides this out of the box; here we derive it from GitHub.

consider the PRs whose author is AI (or have an AI commit/trailer) - that's the
denominator - then count only those where MORE THAN 50% of the ORIGINAL lines were
reworked (changed/deleted) within 48h of creation (by anyone, AI or human).

SCOPE / PROXY NOTE (important - the spec status is "In-Progress, needs agreement"):
  Two things have NO direct API and are modeled as documented PROXIES:
    1. "AI-assisted PR": GitHub never tags a PR as AI. We treat a PR as AI-assisted
       when its author is an AI agent (Copilot/CodeRabbit/Qodo) OR a commit on it
       carries an AI co-author / "assisted-by" trailer. (Generic bots excluded.)
    2. "% of original lines reworked": we measure how much of the ORIGINAL code did
       NOT survive, using a single diff from the original commit to the head commit:
         - the original commit is the BASE of the diff, so every DELETED line in that
           diff is, by definition, an ORIGINAL line that was changed or removed.
         - new lines added later (and lines added-then-deleted in between) can NOT
           appear as deletions, so generation/churn does not pollute the number, and
           a line edited many times is counted once.

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  Eligible PR        = ANY AI-assisted PR - merged OR not (rework can happen during
                       review or on a PR that is later abandoned).  GET /pulls (state=all).
  Original commit    = the FIRST commit that actually has content (additions > 0).
                       Copilot's very first commit is often an empty setup checkpoint,
                       so we skip empties and anchor on the first commit that added code.
  Baseline LOC       = that original commit's added lines (the size of the original).
  48h window         = original_commit_time .. original_commit_time + 48h.
  Head commit        = the LAST commit inside that 48h window.
  Rework LOC         = deletions from a SINGLE compare(original_sha ... head_sha):
                       GET /repos/{o}/{r}/compare/{base}...{head} -> sum files[].deletions.
                       = how many of the ORIGINAL lines did not survive to head.
  Revision %         = rework LOC / baseline LOC x 100  (capped at 100 - you cannot
                       rework more than 100% of the original).
  Reworked PR        = revision % > 50  (REWORK_THRESHOLD_PCT).
  DENOMINATOR        = total AI-assisted PRs (merged or not).
  NUMERATOR          = those marked reworked.
  Value              = numerator / denominator x 100.

  Few AI PRs exist per repo, so by default the script scans EVERY repo the token can
  see in the org (tools.github.org) and aggregates. Pass --repo owner/name for one.

RUN:
  python kpi_17.py                       # scan the whole org
  python kpi_17.py --repo ALMCybage/26074_BranchRuleset_Demo
  python kpi_17.py --raw                 # full per-PR detail
(Needs tools.github.githubKey + .org in your .secrets/project.json; .owner/.repo
 are used only as a fallback when --repo is not given and no org is set.)
============================================================================
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from _toolkit import Call, Datapoint, cfg, gh_get, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github"
API_VERSION = "2022-11-28"

# How widely to look + the proxy knobs (tunable without touching logic).
REPO_PAGES = 2              # pages of /orgs/{org}/repos
PR_PAGES = 2               # pages of /repos/{o}/{r}/pulls per repo
PER_PAGE = 100
WINDOW_HOURS = 48          # the rework clock, measured from the original commit
REWORK_THRESHOLD_PCT = 50  # a PR is "reworked" if > this % of its original lines change

# WHO classification hints.
AI_AGENT_HINTS = ("copilot", "coderabbit", "qodo")
BOT_HINTS = ("github-actions", "dependabot", "renovate")
AI_COMMIT_HINTS = (
    "co-authored-by: copilot", "assisted-by", "co-authored-by: github copilot",
    "generated with copilot", "ai-assisted", "copilot-generated",
)


# --- KPI definition (matches the master-sheet row; ASCII-only for any console). ---
KPI = {
    "num": 17,
    "name": "Rework Rate (AI-Attributed)",
    "index": "Quality",
    "definition": "% of AI-assisted code changes that require substantial revision "
                  "shortly after creation (>50% of the original lines reworked within "
                  "48h), indicating poor first-pass AI code quality.",
    "how_measured": "Identify AI-assisted PRs where >50% of the original lines were "
                    "changed/deleted within 48 hours; divide by total AI-assisted "
                    "PRs x 100.",
    "formula": "(AI-assisted PRs with >50% line rework within 48h / Total AI-assisted "
               "PRs) x 100",
    "unit": "%",
    "cadence": "Weekly",
    "direction": "",
    "interpretation": "<5%=Excellent; 5-10%=Acceptable; 10-15%=Needs improvement; "
                      ">15%=Critical",
    "tools": "GitHub (PRs/Commits/Compare). AI attribution + rework baseline are "
             "documented PROXIES; the spec methodology is In-Progress.",
    "plain": "Of the AI-written pull requests (merged or not), what share had more "
             "than 50% of their original lines rewritten within 2 days - a sign the "
             "AI code needed quick fixing. LOWER is better.",
    "steps": [
        "Count the total AI-assisted PRs in scope, merged OR not (author is an AI "
        "agent, or a commit carries an AI trailer; generic bots excluded).",
        "Original = the FIRST commit that has content; baseline = its added lines. Open "
        "a 48h window from it; head = the last commit inside that window.",
        "Rework LOC = deletions from one compare(original...head) = how many ORIGINAL "
        "lines did not survive (new lines / churn cannot appear, repeats counted once).",
        "Mark the PR reworked if rework LOC / baseline > 50% (capped at 100%).",
        "Count the reworked PRs, then Result = reworked / total x 100. If no AI PR was "
        "found (total = 0) the KPI is NOT COMPUTABLE for the scope.",
    ],
}


# ===========================================================================
# Small helpers
# ===========================================================================
def _parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def _author_kind(user):
    """WHO, classified: AI-AGENT (Copilot/CodeRabbit/Qodo) | BOT | human | unknown."""
    if not isinstance(user, dict):
        return "unknown"
    login = (user.get("login") or "").lower()
    if any(h in login for h in AI_AGENT_HINTS):
        return "AI-AGENT"
    if (user.get("type") or "").lower() == "bot" or login.endswith("[bot]") \
            or any(h in login for h in BOT_HINTS):
        return "BOT"
    return "human"


def _commit_is_ai(message):
    low = (message or "").lower()
    return any(h in low for h in AI_COMMIT_HINTS)


def _arg_repo():
    for i, a in enumerate(sys.argv):
        if a == "--repo" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if a.startswith("--repo="):
            return a.split("=", 1)[1]
    return None


async def _gh_json(client, path, token):
    """gh_get returning (ok, raw)."""
    res = await gh_get(client, path, token=token, api_version=API_VERSION)
    return res.ok, res.raw


# ===========================================================================
# SHARED SCAN - both datapoints (total + reworked) read from this single scan.
# Scan once, cache, and let each Datapoint pull its own number out of it.
# ===========================================================================
_SCAN: dict | None = None


async def _list_target_repos(client, token):
    """The repos to scan: just --repo if given, else every repo the token can see
    in tools.github.org (a couple of pages), else the single .owner/.repo fallback."""
    override = _arg_repo()
    if override and "/" in override:
        return [tuple(override.split("/", 1))]
    org = cfg(TOOL, "org")
    if org:
        repos = []
        for page in range(1, REPO_PAGES + 1):
            ok, raw = await _gh_json(
                client, f"/orgs/{org}/repos?per_page={PER_PAGE}&sort=updated&page={page}", token)
            if not ok or not isinstance(raw, list) or not raw:
                break
            repos.extend((org, r.get("name")) for r in raw if isinstance(r, dict) and r.get("name"))
            if len(raw) < PER_PAGE:
                break
        if repos:
            return repos
    owner, repo = cfg(TOOL, "owner"), cfg(TOOL, "repo")
    return [(owner, repo)] if owner and repo else []


async def _pr_commits(client, owner, repo, n, token):
    """The PR's commits as [{sha, date, message, author}], in API order."""
    ok, commits = await _gh_json(
        client, f"/repos/{owner}/{repo}/pulls/{n}/commits?per_page=100", token)
    out = []
    if ok and isinstance(commits, list):
        for c in commits:
            cm = c.get("commit") or {}
            out.append({
                "sha": c.get("sha"),
                "date": _parse_ts((cm.get("author") or {}).get("date")),
                "message": cm.get("message") or "",
                "author": c.get("author"),
            })
    return out


def _is_ai_pr(pr, commits):
    """True if AI-assisted: AI-agent author, or any commit has an AI trailer/author."""
    if _author_kind(pr.get("user")) == "AI-AGENT":
        return True
    for c in commits:
        if _commit_is_ai(c["message"]) or _author_kind(c["author"]) == "AI-AGENT":
            return True
    return False


async def _commit_stats(client, owner, repo, sha, token):
    """(additions, deletions, total) line stats for a single commit."""
    ok, d = await _gh_json(client, f"/repos/{owner}/{repo}/commits/{sha}", token)
    s = (d.get("stats") or {}) if ok and isinstance(d, dict) else {}
    return int(s.get("additions") or 0), int(s.get("deletions") or 0), int(s.get("total") or 0)


async def _compare_lines(client, owner, repo, base_sha, head_sha, token):
    """Net line change between two commits via the Compare API: (additions, deletions),
    summed across files of base...head.

    Because `base` is the ORIGINAL commit, deletions = lines that were in the original
    but are gone/changed at head = ORIGINAL lines reworked. New lines added after the
    original (and lines added-then-deleted in between) cannot appear as deletions, and
    a line edited many times is counted once."""
    if not base_sha or not head_sha or base_sha == head_sha:
        return 0, 0
    ok, d = await _gh_json(
        client, f"/repos/{owner}/{repo}/compare/{base_sha}...{head_sha}", token)
    if not ok or not isinstance(d, dict):
        return 0, 0
    files = d.get("files") or []
    adds = sum(int(f.get("additions") or 0) for f in files)
    dels = sum(int(f.get("deletions") or 0) for f in files)
    return adds, dels


async def _rework_verdict(client, owner, repo, commits, token):
    """Rework verdict for one PR using the COMPARE method (original -> head).

    Baseline (the ORIGINAL code) = additions of the FIRST commit that has content
      (empty setup checkpoints are skipped). That commit is the diff's base.
    Head = the LAST commit inside the 48h window measured from the original commit.
    Rework LOC = deletions from ONE compare(original_sha ... head_sha) = how many of
      the ORIGINAL lines did not survive to head. New-line generation and churn that
      was added-then-removed cannot appear; a line reworked many times counts once.
    Returns (baseline, rework_loc, n_followups)."""
    dated = sorted([c for c in commits if c["date"] and c["sha"]], key=lambda c: c["date"])
    if not dated:
        return 0, 0, 0

    # ORIGINAL = first commit that has content. Skip empty setup commits.
    baseline = 0
    anchor = None
    for i, c in enumerate(dated):
        add, _, _ = await _commit_stats(client, owner, repo, c["sha"], token)
        if add > 0:
            baseline, anchor = add, i
            break
    if anchor is None:                       # no commit ever added code -> nothing original
        return 0, 0, 0

    # HEAD = the last commit within 48h of the original commit.
    window_end = dated[anchor]["date"] + timedelta(hours=WINDOW_HOURS)
    later = [c for c in dated[anchor + 1:] if c["date"] <= window_end]
    if not later:                            # nothing happened after the original -> no rework
        return baseline, 0, 0
    head_sha = later[-1]["sha"]

    # ONE compare original -> head: its deletions = ORIGINAL lines reworked.
    _, rework = await _compare_lines(client, owner, repo, dated[anchor]["sha"], head_sha, token)
    return baseline, rework, len(later)


async def _scan(client):
    """Walk every target repo's PRs, keep AI-assisted PRs (merged or not), and compute
    the 48h rework verdict per PR. Returns an aggregate dict cached in _SCAN."""
    global _SCAN
    if _SCAN is not None:
        return _SCAN

    token = cfg(TOOL, "githubKey")
    if not token:
        raise RuntimeError("Set tools.github.githubKey in .secrets/project.json")

    repos = await _list_target_repos(client, token)
    if not repos:
        raise RuntimeError(
            "No repos to scan. Set tools.github.org (preferred) or .owner/.repo in "
            ".secrets/project.json, or pass --repo owner/name.")

    detail = []
    by_repo = []
    total_ai = reworked = prs_total = repos_with_prs = 0

    for owner, repo in repos:
        repo_has_pr = False
        r_prs = r_ai = r_rew = 0           # per-repo tallies for the repo-level table
        for page in range(1, PR_PAGES + 1):
            ok, prs = await _gh_json(
                client,
                f"/repos/{owner}/{repo}/pulls?state=all&sort=updated&direction=desc"
                f"&per_page={PER_PAGE}&page={page}", token)
            if not ok or not isinstance(prs, list) or not prs:
                break
            repo_has_pr = True
            for pr in prs:
                prs_total += 1
                r_prs += 1
                n = pr.get("number")
                commits = await _pr_commits(client, owner, repo, n, token)
                if not _is_ai_pr(pr, commits):
                    continue
                total_ai += 1
                r_ai += 1

                # baseline = original commit's additions; rework_loc = original lines
                # that did not survive to head, via one compare(original...head).
                baseline, rework_loc, n_followups = await _rework_verdict(
                    client, owner, repo, commits, token)
                # revision is capped at 100% - you cannot rework more than the original.
                revision_pct = min(100.0, rework_loc / baseline * 100) if baseline > 0 else 0.0
                is_reworked = baseline > 0 and revision_pct > REWORK_THRESHOLD_PCT
                if is_reworked:
                    reworked += 1
                    r_rew += 1

                detail.append({
                    "repo": f"{owner}/{repo}", "pr": n,
                    "title": (pr.get("title") or "")[:80],
                    "author": (pr.get("user") or {}).get("login"),
                    "author_kind": _author_kind(pr.get("user")),
                    "merged": bool(pr.get("merged_at")),
                    "state": pr.get("state"),
                    "baseline_original_loc": baseline,
                    "followup_commits_48h": n_followups,
                    "rework_loc": rework_loc,
                    "revision_pct": round(revision_pct, 1),
                    "reworked": is_reworked,
                })
            if len(prs) < PER_PAGE:
                break
        if repo_has_pr:
            repos_with_prs += 1
        by_repo.append({"repo": repo, "owner": owner,
                        "prs": r_prs, "ai_prs": r_ai, "reworked": r_rew})

    _SCAN = {
        "scope": _arg_repo() or f"org:{cfg(TOOL, 'org')} ({len(repos)} repos)",
        "org": _arg_repo() or cfg(TOOL, "org") or "",
        "repos_scanned": len(repos), "repos_with_prs": repos_with_prs,
        "prs_scanned": prs_total,
        "window_hours": WINDOW_HOURS, "rework_threshold_pct": REWORK_THRESHOLD_PCT,
        "total_ai_assisted_prs": total_ai,
        "reworked_prs": reworked,
        "by_repo": by_repo,
        "detail": detail,
    }
    return _SCAN


def _scan_call(raw):
    """Wrap the cached scan dict in a Call so run_kpi prints it as the datapoint raw."""
    headers = {"Accept": "application/vnd.github+json",
               "Authorization": "***redacted***", "X-GitHub-Api-Version": API_VERSION}
    note = ("aggregated GitHub PR scan + per-PR compare(original...head) rework proxy; "
            "raw below is the computed aggregate + per-PR rework verdicts")
    return Call("GET", f"{__name__}: GitHub Pulls/Commits/Compare scan", headers, 200, raw, note)


# ===========================================================================
# DATAPOINT 1 of 2 - DENOMINATOR: total AI-assisted PRs (merged or not, in scope)
# ===========================================================================
async def fetch_total_ai_prs(client):
    return _scan_call(await _scan(client))


def extract_total_ai_prs(raw):
    return float(raw["total_ai_assisted_prs"]) if isinstance(raw, dict) else None


# ===========================================================================
# DATAPOINT 2 of 2 - NUMERATOR: AI-assisted PRs reworked >50% within 48h
# ===========================================================================
async def fetch_reworked_prs(client):
    return _scan_call(await _scan(client))


def extract_reworked_prs(raw):
    return float(raw["reworked_prs"]) if isinstance(raw, dict) else None


# ===========================================================================
# THE FORMULA - (reworked AI PRs / total AI PRs) x 100
# ===========================================================================
def compute(total_ai_prs, reworked_prs):
    if total_ai_prs is None or reworked_prs is None:
        return None

    # Per-PR rework detail + the proxy caveat, printed for context.
    if isinstance(_SCAN, dict):
        print("\n" + "=" * 74)
        print(f"Rework Rate (AI-Attributed) - scope: {_SCAN['scope']}")
        print("-" * 74)
        print(f"  repos scanned={_SCAN['repos_scanned']} (with PRs={_SCAN['repos_with_prs']})  "
              f"PRs scanned={_SCAN['prs_scanned']}  "
              f"window={_SCAN['window_hours']}h  threshold>{_SCAN['rework_threshold_pct']}%")
        print(f"  total AI-assisted PRs (merged or not)={_SCAN['total_ai_assisted_prs']}  "
              f"reworked={_SCAN['reworked_prs']}")
        print("  Per-PR rework verdicts (baseline = original commit's additions; "
              "rework = original lines changed at head via compare):")
        for d in _SCAN["detail"]:
            v = "REWORKED" if d["reworked"] else "ok"
            m = "merged" if d["merged"] else d["state"]
            print(f"    - {d['repo']}#{d['pr']} [{m}] author=@{d['author']}({d['author_kind']}) "
                  f"orig={d['baseline_original_loc']} reworkLOC={d['rework_loc']} "
                  f"({d['followup_commits_48h']} commits/48h) "
                  f"revision={d['revision_pct']}% => {v}")
        print("  CAVEAT: PROXY only - 'AI-assisted' is inferred from author/commit trailers.")
        print("          Baseline = additions of the first commit that has content (the")
        print("          original). Rework = deletions from compare(original...head within")
        print("          48h) = ORIGINAL lines that did not survive (any author). New-line")
        print("          churn cancels out; revision capped at 100%. Methodology In-Progress.")
        print("=" * 74)

    if not total_ai_prs:          # no AI PR found -> not computable
        return None
    return reworked_prs / total_ai_prs * 100


# The inputs run_kpi fetches, extracts, and feeds to compute() in this order.
DATAPOINTS = [
    Datapoint(
        label="Total AI-assisted PRs",
        description="Count of AI-assisted Pull Requests in scope, MERGED OR NOT. A PR "
                    "is AI-assisted if its author is an AI agent (Copilot/CodeRabbit/"
                    "Qodo) or a commit carries an AI trailer; generic bots are excluded.",
        example="e.g. across the org scan, 5 AI-assisted PRs (merged or open), so "
                "denominator = 5.",
        plain="How many AI-written PRs existed this period (merged or not).",
        source="GET /orgs/{org}/repos -> per repo GET /pulls (state=all) -> keep PRs "
               "that are AI-attributed (author or commit-trailer).",
        paths=["pulls[].user.login", "pulls/{n}/commits[].commit.message"],
        steps=[
            "Scan every accessible repo in the org for pull requests (any state).",
            "Keep PRs that are AI-assisted (AI-agent author or AI commit trailer).",
            "Count them - this is the denominator.",
        ],
        fetch=fetch_total_ai_prs,
        extract=extract_total_ai_prs,
    ),
    Datapoint(
        label="AI-assisted PRs reworked >50% within 48h",
        description="Of those PRs, the count where more than 50% of the ORIGINAL lines "
                    "were changed/deleted within 48h. Baseline = the first content "
                    "commit's added lines; rework = deletions from one "
                    "compare(original...head) = original lines that did not survive.",
        example="e.g. 1 of the 5 PRs had >50% of its original lines reworked in 48h, "
                "so numerator = 1.",
        plain="How many of those PRs had >50% of their original lines rewritten within 2 days.",
        source="For each AI PR: find the first content commit (baseline = its additions) "
               "and the last commit within 48h; rework = deletions from "
               "GET /repos/{o}/{r}/compare/{original_sha}...{head_sha}; reworked if "
               "rework/baseline > 50% (capped at 100%).",
        paths=["pulls/{n}/commits[].sha", "pulls/{n}/commits[].commit.author.date",
               "commits/{sha}.stats.additions", "compare/{base}...{head}.files[].deletions"],
        steps=[
            "Use the same AI-PR scan as the denominator.",
            "Original = first commit with content (baseline = its added lines); head = "
            "last commit within 48h of it.",
            "Rework = deletions from one compare(original...head) = original lines that "
            "did not survive (new lines / churn excluded, repeats counted once).",
            "Mark reworked if rework/baseline > 50% (capped at 100%); count such PRs.",
        ],
        fetch=fetch_reworked_prs,
        extract=extract_reworked_prs,
    ),
]


# ===========================================================================
# PDF REPORT - two tables (org-level + repo-level), via export_pdf.py's optional
# report_sections() hook. Replaces the generic numerator/denominator tables, the GET
# API sources, and the raw "underlying data" detail with just the two tables below.
# ===========================================================================
def _rate_cells(reworked, total, interp):
    """(formula_html, interpretation_label) for a reworked/total pair. The Formula
    cell shows the applied formula -> %, the band maps that % via export_pdf."""
    if not total:
        return ("n/a", "-")
    pct = reworked / total * 100
    formula = f"{reworked} / {total} &times; 100 = {pct:.1f}%"
    band = ""
    try:
        import export_pdf
        band = export_pdf._interpretation_band(interp, pct) or ""
    except Exception:
        band = ""
    return (formula, band or "-")


def report_sections(env):
    """TWO tables for the PDF:
       1) Organization summary: Org_name | Repo Count | Total PR's |
          PR qualified (>50% rework) | Formula | Interpretation.
       2) Repository breakdown: Repo Name | PR's | PR qualified (>50% rework in 48 hrs)
          | Formula | Interpretation.
       'PR's' / 'Total PR's' are the AI-assisted PRs (the formula's denominator)."""
    import html as _html
    esc = lambda x: _html.escape(str(x))

    dps = env.get("datapoints") or []
    raw = next((dp.get("raw") for dp in dps if isinstance(dp.get("raw"), dict)), {}) or {}
    interp = (env.get("kpi") or {}).get("interpretation")

    # ---- 1) Organization-level (one row for the scanned org) ----
    org = raw.get("org") or "-"
    repo_count = raw.get("repos_scanned", 0)
    total_ai = raw.get("total_ai_assisted_prs", 0)
    reworked = raw.get("reworked_prs", 0)
    o_formula, o_band = _rate_cells(reworked, total_ai, interp)
    org_head = ("<tr><th>Org name</th><th>Repo Count</th><th>Total PR's</th>"
                "<th>PR qualified (&gt;50% rework)</th><th>Formula</th>"
                "<th>Interpretation</th></tr>")
    org_row = (f"<tr><td>{esc(org)}</td><td class='num'>{esc(repo_count)}</td>"
               f"<td class='num'>{esc(total_ai)}</td><td class='num'>{esc(reworked)}</td>"
               f"<td>{o_formula}</td><td>{esc(o_band)}</td></tr>")
    org_table = (f"<table class='grid'><thead>{org_head}</thead>"
                 f"<tbody>{org_row}</tbody></table>")

    # ---- 2) Repository-level (one row per repo that had AI-assisted PRs) ----
    repo_head = ("<tr><th>Repo Name</th><th>PR's</th>"
                 "<th>PR qualified (&gt;50% rework in 48 hrs)</th>"
                 "<th>Formula</th><th>Interpretation</th></tr>")
    rows = []
    for r in raw.get("by_repo", []) or []:
        if not r.get("ai_prs"):
            continue                                 # skip repos with no AI PRs
        rf, rb = _rate_cells(r.get("reworked", 0), r.get("ai_prs", 0), interp)
        rows.append(
            f"<tr><td>{esc(r.get('repo'))}</td><td class='num'>{esc(r.get('ai_prs'))}</td>"
            f"<td class='num'>{esc(r.get('reworked'))}</td>"
            f"<td>{rf}</td><td>{esc(rb)}</td></tr>")
    if not rows:
        rows.append("<tr><td colspan='5'>No AI-assisted PRs found in scope.</td></tr>")
    repo_table = (f"<table class='grid'><thead>{repo_head}</thead>"
                  f"<tbody>{''.join(rows)}</tbody></table>")

    return {"heading": None,
            "sections": [("Organization", org_table), ("Repository", repo_table)]}


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)
