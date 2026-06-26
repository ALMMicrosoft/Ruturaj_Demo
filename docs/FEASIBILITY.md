# KPI Feasibility Reference (kpi-verify, 4-tool scope)

Self-contained snapshot of the full KPI feasibility research, preserved so the
`kpi-verify` bundle no longer depends on the `genai-tracker` project. It captures
all 62 KPIs, their formulas, every input datapoint, and the per-datapoint
availability, faithfully reproduced from the genai-tracker source files
(`lib/kpi/catalogGenerated.ts`, `lib/kpi/inputs.ts`, `lib/kpi/indexes.ts`,
`lib/kpi/types.ts`, `lib/kpi/feasibility.ts`).

## 0. Scope: FOUR tools

`kpi-verify` is in scope for **four configured tools: GitHub Copilot, GitHub,
Jira (Cloud), and Claude (Anthropic).** This matches the genai-tracker
classification exactly, so the **4-tool verdicts in this document equal the
genai-tracker source** (`catalogGenerated.ts` + `inputs.ts`, rolled up by
`kpiFeasibility()`). The 4-tool classification is the PRIMARY view throughout.

External sources remain out of scope (LMS, survey/NPS, finance/budget,
coverage/SonarQube, HRIS/SCIM, manual rubric, incident/APM, CRM/support);
inputs needing those stay `blocked`.

### Secondary view: without Claude (3-tool)

Some teams will not have Claude (Anthropic) provisioned. For them, every input
whose only `live`/`pending` source is Claude falls back to `blocked`, which
re-blocks eight KPIs. Throughout this document each input shows BOTH its 4-tool
(primary) availability AND its 3-tool ("without Claude") availability, and any
KPI whose verdict depends on Claude is tagged **`(needs Claude)`** in its
headline so a Claude-less team immediately knows it degrades to blocked.

The eight Claude-dependent KPIs (the token / cost / spend / chat-session
cluster), with their 4-tool verdict and the 3-tool fallback:

| # | KPI | 4-tool verdict | 3-tool (no Claude) | Reason |
|---|-----|----------------|--------------------|--------|
| 35 | Daily AI Token Consumption per Developer | computable | **blocked** | Tokens + active devs are live only via Claude |
| 36 | Token Cost per Story Point | computable | **blocked** | Metered token cost (Claude totalCostUsd) only; Jira velocity alone is insufficient |
| 40 | AI Chat Sessions per Developer per Sprint | computable | **blocked** | Sessions + active devs are live only via Claude |
| 41 | AI Chat Session Depth (Turns per Session) | pending | **blocked** | Turn count (pending) + sessions (live) are Claude-only |
| 44 | Context Window Utilization Rate | pending | **blocked** | Per-session prompt tokens + max-window are Claude-sourced |
| 53 | AI Coding Efficiency (Lines per Dollar) | computable | **blocked** | linesAdded + metered cost are live only via Claude |
| 55 | AI Spend per Developer per Week | computable | **blocked** | Metered cost + active devs are live only via Claude |
| 59 | Lines Added per AI Session | computable | **blocked** | linesAdded + sessions are live only via Claude |

## 1. The feasibility model

A KPI is only as feasible as its weakest input. Feasibility rolls up from inputs
-> KPI -> index. The verdict is computed exactly as genai-tracker's
`kpiFeasibility()`: a single `unavailable`/blocked input blocks the KPI;
otherwise a single `pending` input makes it pending; all-`live` is computable.

Each input is graded against what a configured tool's VERIFIED pipeline actually
exposes:

- **computable** — every input is live from an in-scope tool; a real value can be
  fetched now.
- **pending** — the signal exists but the aggregation / proxy / history is not
  wired (cohort ETL, per-commit attribution, team join, per-session turn counts),
  or only a documented proxy is available. The data path exists; the rollup does
  not.
- **blocked** — no in-scope tool exposes the input. Names the external source
  needed (LMS, survey/NPS, finance/budget, coverage tool, HRIS/SCIM, incident/APM,
  CRM/support, manual rubric/baseline). In the secondary 3-tool view, an input
  that is only live via Claude is also blocked.

## 2. The five leadership indexes

KPIs are grouped under five leadership indexes (these replaced the older
datapoint categories as the product's primary axis).

| Index | One-line description |
|-------|----------------------|
| **Adoption** | Is the AI capability actually being activated and sustained — seats turning into real, repeat usage across the team. |
| **Outcome** | What the investment returns — efficiency, cost, and business value from AI-assisted delivery. |
| **Quality** | Whether AI-assisted work holds up — defects, rework, security, and test health of AI-influenced code. |
| **Utilization** | How deeply developers use the AI — acceptance, lines, chat, and the day-to-day intensity of engagement. |
| **Velocity** | How fast work moves end to end — cycle time, lead time, throughput, and DORA delivery signals. |

## 3. Summary — verdict counts (PRIMARY: 4-tool scope)

Per-index counts (computable / pending / blocked), 4-tool scope (GitHub Copilot,
GitHub, Jira, Claude). These are the headline numbers and equal the genai-tracker
source rollup.

| Index | Total | Computable | Pending | Blocked |
|-------|------:|-----------:|--------:|--------:|
| Adoption | 16 | 1 | 11 | 4 |
| Outcome | 12 | 3 | 1 | 8 |
| Quality | 7 | 0 | 3 | 4 |
| Utilization | 19 | 8 | 8 | 3 |
| Velocity | 8 | 4 | 1 | 3 |
| **Total** | **62** | **16** | **24** | **22** |

Overall 4-tool totals: **16 computable, 24 pending, 22 blocked.**

> Secondary view — **Without Claude (3-tool): 10 computable / 22 pending / 30
> blocked.** Dropping Claude re-blocks the eight Claude-dependent KPIs (#35, #36,
> #40, #41, #44, #53, #55, #59): six move computable -> blocked (#35, #36, #40,
> #53, #55, #59) and two move pending -> blocked (#41, #44). Per index, the 3-tool
> shifts hit Utilization (8/8/3 -> 5/6/8) and Outcome (3/1/8 -> 0/1/11); the other
> three indexes are unchanged.

Per-index 3-tool (without Claude) counts, for reference:

| Index | Total | Computable | Pending | Blocked |
|-------|------:|-----------:|--------:|--------:|
| Adoption | 16 | 1 | 11 | 4 |
| Outcome | 12 | 0 | 1 | 11 |
| Quality | 7 | 0 | 3 | 4 |
| Utilization | 19 | 5 | 6 | 8 |
| Velocity | 8 | 4 | 1 | 3 |
| **Total** | **62** | **10** | **22** | **30** |

Per-index membership (by KPI number; authoritative index per KPI is given in each
matrix entry below):

- **Adoption (16):** #1, #2, #3, #4, #5, #42, #45, #46, #47, #48, #49, #50, #52, #60, #61, #62
- **Outcome (12):** #28, #29, #30, #31, #32, #33, #34, #36, #53, #55, #56, #57
- **Quality (7):** #14, #15, #16, #17, #18, #19, #20
- **Utilization (19):** #6, #7, #8, #9, #10, #11, #12, #13, #35, #37, #38, #39, #40, #41, #44, #51, #54, #58, #59
- **Velocity (8):** #21, #22, #23, #24, #25, #26, #27, #43

## 4. KPIs with a verification script

These 11 KPIs already ship a kpi-verify verification script and are flagged with
a check mark (`[script]`) in the matrix below:

> #1, #5, #8, #22, #23, #24, #25, #37, #38, #39, #54

Script files:
- `kpi_01_active_ai_tool_adoption_rate.py`
- `kpi_05_ai_tool_retention_rate.py`
- `kpi_08_ai_code_acceptance_rate.py`
- `kpi_22_pr_merge_time.py`
- `kpi_23_sprint_completion_rate.py`
- `kpi_24_feature_to_production_lead_time.py`
- `kpi_25_dora_deployment_frequency.py`
- `kpi_37_ai_suggested_loc_per_developer_per_sprint.py`
- `kpi_38_ai_accepted_lines_of_code_loc_rate.py`
- `kpi_39_net_ai_contributed_loc_per_developer_per_sprint.py`
- `kpi_54_lines_added_vs_lines_removed_ratio.py`

(Note: #5 is pending in both scopes — the cohort retention ETL is not wired — but
a verification script exists for it.)

## 5. The full 62-KPI matrix

Each entry shows: index, 4-tool verdict (headline, with `(needs Claude)` where the
verdict depends on a Claude-sourced input), formula, the inputs table (label |
4-tool availability | tool | endpoint | field | reason-if-not-live), and — when
not computable — the blocker. Where an input's 3-tool ("without Claude")
availability differs from its 4-tool availability, the difference is called out in
the row and in the blocker/notes line.

Tool legend: CP = GitHub Copilot, GH = GitHub, JR = Jira, CL = Claude, ext =
external source.

---

### #1 Active AI Tool Adoption Rate — Adoption — computable `[script]`

**Formula:** (Active Users / Licensed Seats) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Weekly active developers | live | CP | org-metrics-organization-28-day-latest | weekly_active_users | — |
| Licensed seats | live | CP | org-billing-seats | total_seats | — |

Both inputs live from Copilot. Computable in both 4-tool and 3-tool scope.

---

### #2 Time-to-First-AI-Commit — Adoption — blocked

**Formula:** First-AI-PR merge date - AI tool provisioning date

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| AI tool provisioning date per developer | unavailable | CP/ext | — | scim.user.provisionedAt | Requires SCIM/HRIS (Okta, Azure AD, Workday) seat-provisioning timestamp; no GenAI tool supplies the license-grant date |
| First AI-assisted PR merge date per developer | pending | CP/GH | — | github.pulls.mergedAt | GitHub exposes PR merge timestamps and Copilot exposes per-user activity, but the pipeline does not join Copilot accept events to a developer's first merged PR yet |

**Blocker:** HRIS/SCIM provisioning timestamp (external). Blocked in both scopes.

---

### #3 Training Completion Rate — Adoption — blocked

**Formula:** (Completed modules / Enrolled developers) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Completed training modules | unavailable | ext | — | lms.completions.count | Requires an LMS (Workday Learning, Cornerstone, TalentLMS, Docebo); no GenAI coding tool tracks training completion |
| Enrolled developers | unavailable | ext | — | lms.enrollments.count | Requires LMS/HR enrollment records; not available from Copilot, GitHub, Jira or Claude |

**Blocker:** LMS (training-completion system). Blocked in both scopes.

---

### #4 Prompt Engineering Proficiency Score — Adoption — blocked

**Formula:** Rubric score = Specificity(25) + Context(25) + Constraints(25) + Output Format(25)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Rubric-assessed prompt quality score | unavailable | ext | — | manual.rubric.median | Requires a manual rubric / CoE prompt-audit of prompt text; no tool surfaces raw prompt content scored on this rubric |

**Blocker:** Manual rubric / CoE prompt-audit. Blocked in both scopes.

---

### #5 AI Tool Retention Rate — Adoption — pending `[script]`

**Formula:** (Active users at Day 90 / Active users at Day 30) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Active users at Day 90 (cohort) | pending | CP | org-metrics-users-1-day | day / user_login | Same cohort-history ETL as Day 30; the daily data exists but the 90-day rollup isn't built |
| Active users at Day 30 (cohort) | pending | CP | org-metrics-users-1-day | day / user_login | Per-user daily activity is available (users-1-day, ~1yr), but cohort retention needs a time-series ETL not yet wired |

**Blocker:** Unwired cohort-retention ETL over Copilot's daily per-user data
(signal exists, aggregation not built). Pending in both scopes. A verification
script exists.

---

### #6 Use Case Activation Coverage — Utilization — blocked

**Formula:** Count(Active AI capability areas) / 19 x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Active AI capability areas (of 19) | unavailable | ext | — | CoE capability tracker | No tool tracks SDLC capability-area activation; this is a manual CoE capability tracker (Notion/Confluence/rubric) |

**Blocker:** Manual CoE capability tracker. Blocked in both scopes.

---

### #7 AI-Assisted Commit Ratio — Utilization — pending

**Formula:** (AI-assisted commits / Total commits) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| AI-assisted commits | pending | CP | — | copilot.metrics accepted-suggestion-to-commit attribution | Copilot exposes accepted-suggestion telemetry attributable to commits, but per-commit AI attribution is not surfaced yet; needs wiring |
| Total commits | pending | GH | — | github commits API | GitHub exposes commit counts but total-commits-per-period is not surfaced yet; needs wiring |

**Blocker:** Unwired per-commit AI attribution + total-commits rollup. Pending in
both scopes.

---

### #8 AI Code Acceptance Rate — Utilization — computable `[script]`

**Formula:** (Accepted AI suggestions / Total AI suggestions shown) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Accepted suggestions | live | CP | org-metrics-organization-28-day-latest | code_acceptance_activity_count | — |
| Suggestions shown | live | CP | org-metrics-organization-28-day-latest | code_generation_activity_count | Copilot reports code_generation_activity_count (suggestions generated), the closest documented proxy for "shown" |

Computable in both scopes (the "shown" proxy is accepted as live).

---

### #9 Review Automation Rate — Utilization — pending

**Formula:** (PRs with AI first-pass review / Total PRs merged) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| PRs with AI first-pass review | pending | GH | — | github PR review events (bot author) | GitHub exposes PR review events incl. bot/AI reviewer authorship, but AI-first-pass-review counts are not surfaced yet; needs wiring |
| PRs merged per week | live | GH | pulls | prsMergedPerWeek | — |

**Blocker:** Unwired AI-first-pass-review classification on GitHub PR review
events. Pending in both scopes.

---

### #10 Test Generation Rate — Utilization — pending

**Formula:** (Modules with AI-generated test stubs / Total new modules merged) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Modules with AI-generated test stubs | pending | GH | — | github Actions CI annotation / commit label | CI metadata can carry AI test-stub annotations, but AI-test-generation counts are not surfaced yet; needs wiring |
| Total new modules merged | pending | GH | — | github merged PR file stats | GitHub exposes merged-PR/file data but new-modules-merged counts are not surfaced yet; needs wiring |

**Blocker:** Unwired AI-test-stub annotation + new-modules rollup. Pending in both
scopes.

---

### #11 Documentation Generation Rate — Utilization — pending

**Formula:** (PRs with accepted AI-generated docs / Total PRs merged) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| PRs with accepted AI-generated docs | pending | GH | — | github PR label 'ai-docs-included' | GitHub exposes PR labels and checks, but AI-docs PR counts are not surfaced yet; needs wiring |
| PRs merged per week | live | GH | pulls | prsMergedPerWeek | — |

**Blocker:** Unwired AI-docs PR-label classification. Pending in both scopes.

---

### #12 Agentic Workflow Activation Rate — Utilization — blocked

**Formula:** Count(Active agent roles) / 6 x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Active agentic mesh roles (of 6) | unavailable | ext | — | agent orchestration tracker | No tool tracks multi-step agent-mesh activation; requires an external agent-orchestration tracker (LangSmith/AutoGen/CrewAI) plus manual CoE rollup |

**Blocker:** External agent-orchestration tracker + manual rollup. Blocked in both
scopes.

---

### #13 AI Ceremony Overhead Reduction — Utilization — blocked

**Formula:** ((Pre-AI ceremony time - Post-AI ceremony time) / Pre-AI ceremony time) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Pre-AI ceremony time per sprint | unavailable | ext | — | calendar API / time-tracking baseline | Requires calendar/time-tracking of meeting durations and a pre-AI baseline; no tool supplies ceremony/meeting time |
| Post-AI ceremony time per sprint | unavailable | ext | — | calendar API / time-tracking | Requires calendar/time-tracking of meeting durations; no tool supplies ceremony/meeting time |

**Blocker:** Calendar/time-tracking source + pre-AI baseline. Blocked in both
scopes.

---

### #14 AI-Assisted Defect Density — Quality — blocked

**Formula:** (Defects tagged 'AI-gen-source' / KLOC of AI-assisted code) x 1000

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Defects tagged AI-gen-source | pending | JR | — | issue.fields.customfield_aiGenSource | Jira exposes bugs and custom fields, but an 'AI-gen-source' field attributing defects to AI code is not wired; only total openBugs is wired |
| Lines accepted (loc_added_sum) | live | CP | org-metrics-organization-28-day-latest | loc_added_sum | — |
| Pre-AI defect density baseline | unavailable | ext | — | manual baseline (historical defect tracker analysis) | Requires a historical pre-AI defect-density baseline; must be established manually |

**Blocker:** Manual pre-AI defect-density baseline (external/manual). Blocked in
both scopes.

---

### #15 SAST/DAST Vulnerability Injection Rate — Quality — pending

**Formula:** (New SAST/DAST findings in AI-assisted PRs / Total AI-assisted PRs)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| New SAST/code-scanning findings | pending | GH | — | github.code_scanning.alerts (per PR) | GitHub exposes code-scanning/secret-scanning/Dependabot counts, but per-PR scan findings are not wired as a live input yet |
| AI-assisted PR count | pending | GH | — | github.pulls (AI-assisted label/attribution) | PR metadata + Copilot aggregates exist, but which PRs are AI-assisted is not surfaced yet |

**Blocker:** Unwired per-PR code-scanning findings + AI-assisted attribution.
Pending in both scopes.

---

### #16 AI Output Hallucination / Error Rate — Quality — blocked

**Formula:** (AI-generated blocks rejected for errors / Total AI-generated blocks reviewed) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| AI blocks rejected for factual errors / hallucination | unavailable | ext | — | manual review rubric / external AI-review classifier | No tool supplies an error/hallucination classification of AI review comments; needs manual rubric or third-party classifier (CodeRabbit/Qodo) |
| Total AI-generated blocks reviewed | unavailable | ext | — | manual review tagging / external AI-review tool | Count of discrete AI-generated blocks entering review is not produced by any tool; needs manual tagging or external review-bot |

**Blocker:** Manual review rubric / external AI-review classifier. Blocked in both
scopes.

---

### #17 Rework Rate (AI-Attributed) — Quality — pending

**Formula:** (AI-assisted PRs with >50% line rework / Total AI-assisted PRs) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| AI-assisted PRs with >50% line rework within 48h | pending | GH | — | github.commits (line delta within 48h window) | GitHub exposes commit line-delta data to compute rework, but a rework metric is not surfaced yet |
| Total AI-assisted PRs | pending | GH | — | github.pulls (AI-assisted attribution) | PR metadata + Copilot aggregates exist, but which PRs are AI-assisted is not surfaced yet |

**Blocker:** Unwired rework computation + AI-assisted attribution. Pending in both
scopes.

---

### #18 HITL Gate Pass Rate — Quality — pending

**Formula:** (AI outputs approved at HITL gate without rework / Total HITL gate submissions) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| AI outputs approved at gate without rework | pending | GH | — | github.required_status_checks / review approval events | GitHub exposes required-review status-check pass/fail that can model an HITL gate, but gate events scoped to AI outputs are not surfaced yet |
| Total HITL gate submissions | pending | GH | — | github.pull_request_review / status-check submissions | GitHub exposes review/status-check submissions, but totals scoped to AI-generated outputs are not surfaced yet |

**Blocker:** Unwired AI-scoped gate pass/submission events. Pending in both scopes.

---

### #19 Mean Time to Detect AI-Introduced Issues (MTTD) — Quality — blocked

**Formula:** Median(Defect detection timestamp - AI-commit merge timestamp)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Defect/incident detection timestamps | unavailable | ext | — | external incident/APM tool (PagerDuty/Datadog) | Requires incident/defect detection timestamps from an external incident/APM source; not modelled in our tools |
| AI-attributed defects with merge timestamp | pending | JR | — | issue.fields.customfield_aiGenSource + merge timestamp | Jira exposes bug timestamps, but AI-gen-source attribution linked to AI-commit merge timestamp is not surfaced yet |

**Blocker:** External incident/APM source (PagerDuty/Datadog). Blocked in both
scopes.

---

### #20 Test Coverage Delta (AI-Assisted) — Quality — blocked

**Formula:** (Test coverage % for AI-assisted code) - (Pre-AI baseline coverage %)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Test coverage % for AI-assisted code | unavailable | ext | — | external coverage tool (Codecov/SonarQube) | Coverage is not supplied by any tool; requires an external coverage tool not wired into the pipeline |
| Pre-AI baseline coverage % | unavailable | ext | — | manual baseline (historical coverage tool data) | Requires a manually established pre-AI coverage baseline; no live tool supplies it |

**Blocker:** Coverage tool (Codecov/SonarQube) + manual baseline. Blocked in both
scopes.

---

### #21 Cycle Time Reduction (Commit-to-Deploy) — Velocity — blocked

**Formula:** ((Pre-AI median cycle time - Post-AI median cycle time) / Pre-AI median cycle time) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Lead time for changes, hours (DORA) | live | GH | actions/commits | leadTimeHours (commit->deploy proxy) | — |
| Pre-AI median commit-to-deploy baseline | unavailable | ext | — | manual baseline snapshot | Requires a manually captured pre-AI baseline; no tool supplies a point-in-time baseline. Post-AI value is computable via GitHub DORA lead time |

**Blocker:** Manual pre-AI baseline snapshot. Blocked in both scopes (post-AI
value alone is live via GitHub).

---

### #22 PR Merge Time — Velocity — computable `[script]`

**Formula:** Median(PR merge timestamp - PR open timestamp)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Median PR open->merge, hours | live | GH | pulls | medianTimeToMergeHours | — |

Computable in both scopes.

---

### #23 Sprint Completion Rate — Velocity — computable `[script]`

**Formula:** (Story points completed by sprint end / Story points committed at sprint start) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Sprint completion rate | live | JR | agile/sprints | sprintCompletionRate | — |

Computable in both scopes.

---

### #24 Feature-to-Production Lead Time — Velocity — computable `[script]`

**Formula:** Median(Production deployment timestamp - Story creation timestamp)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Median lead time, hours | live | JR | search | leadTimeHoursMedian | — |

Computable in both scopes.

---

### #25 DORA: Deployment Frequency — Velocity — computable `[script]`

**Formula:** Count(successful production deployments) per week

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Deployments per week (DORA) | live | GH | actions/deployments | deploymentFrequencyPerWeek | — |

Computable in both scopes.

---

### #26 DORA: Change Failure Rate — Velocity — pending

**Formula:** (Deployments causing incident or rollback / Total production deployments) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| DORA change failure rate (%) | pending | GH | — | github deployment status (success vs failure/rollback) ratio | GitHub exposes deployment statuses and Actions outcomes from which CFR can be derived, but a CFR field is not wired yet |

**Blocker:** Unwired failed/rolled-back deployment classification. Pending in both
scopes.

---

### #27 DORA: Mean Time to Restore (MTTR) — Velocity — blocked

**Formula:** Median(Incident resolution timestamp - Incident creation timestamp)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Mean time to restore (hours) | unavailable | ext | — | PagerDuty incident open/resolve timestamps | Requires incident open/resolve timestamps from an incident-management tool (PagerDuty/OpsGenie/Datadog); incidents not modelled in our pipeline |

**Blocker:** Incident-management tool (PagerDuty/OpsGenie/Datadog). Blocked in
both scopes.

---

### #28 Time-to-Market Improvement — Outcome — pending

**Formula:** ((Pre-AI median TTM - Post-AI median TTM) / Pre-AI median TTM) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Median lead time, hours | live | JR | search | leadTimeHoursMedian | — |
| Pre-AI median time-to-market baseline | pending | ext/manual | — | manual.preAiMedianTtm | Post-AI TTM is derivable from Jira lead time, but the pre-AI median TTM must be captured manually before the % reduction can be computed |

**Blocker:** Manual pre-AI TTM baseline (signal-needed). Pending in both scopes.

---

### #29 Cost Per Feature (TCO Delta) — Outcome — blocked

**Formula:** Cost per SP = (Labor hours x rate + Tooling cost + Rework cost) / Story points delivered

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Sprint velocity (points) | live | JR | agile/sprints | sprintVelocity | — |
| Actual AI spend (USD, billed) | live | CL | claude-cost-report | total_cost_usd | — (3-tool: blocked — Claude out of scope) |
| Engineering labor hours x hourly rate | unavailable | ext | — | hris.laborCost | Requires HRIS/payroll (Workday) for labor hours/rates plus a rework-cost feed; no tool supplies labor cost |

**Blocker:** HRIS/payroll labor cost (external) — blocks the KPI in both scopes.
The Claude spend input is live in 4-tool but also blocked in 3-tool.

---

### #30 AI Program ROI — Outcome — blocked

**Formula:** ROI = ((Net Benefits - Total Program Cost) / Total Program Cost) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Actual AI spend (USD, billed) | live | CL | claude-cost-report | total_cost_usd | — (3-tool: blocked — Claude out of scope) |
| Net programme benefits (labor saved + rework reduction + revenue acceleration) | unavailable | ext | — | finance.netBenefits | Requires finance/ERP (SAP, Workday Financials); no engineering tool supplies monetised benefits |

**Blocker:** Finance/ERP net-benefits (external) — blocks the KPI in both scopes.
The Claude spend input is live in 4-tool but also blocked in 3-tool.

---

### #31 Developer NPS (dNPS) — Outcome — blocked

**Formula:** NPS = % Promoters (score 9-10) - % Detractors (score 0-6)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Quarterly developer NPS survey result | unavailable | ext | — | survey.dnps | Requires a survey/dNPS platform (Glint, Culture Amp, DX/GetDX, Typeform); no tool collects survey sentiment |

**Blocker:** Survey/dNPS platform (external). Blocked in both scopes.

---

### #32 Client-Visible Defect Rate — Outcome — blocked

**Formula:** (Client-reported defects per release / Release size in story points) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Sprint velocity (points) | live | JR | agile/sprints | sprintVelocity | — |
| Client-reported defects per release | unavailable | ext | — | zendesk.clientDefects | Requires a customer support/CRM (Zendesk, Salesforce Service Cloud, HubSpot); Jira openBugs are internal-only |

**Blocker:** CRM/support system (Zendesk/SFDC) for externally-reported defects.
Blocked in both scopes.

---

### #33 Engineering Capacity Reclaimed — Outcome — blocked

**Formula:** ((Pre-AI non-feature time % - Post-AI non-feature time %) / Pre-AI non-feature time %) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Non-feature time % (pre and post AI) | unavailable | ext | — | linearb.nonFeatureTimePct | Requires a flow-time/time-tracking source (LinearB, DX) plus a manual pre-AI baseline; no tool supplies time-allocation breakdown |

**Blocker:** Flow-time/time-tracking tool (LinearB/DX) + baseline. Blocked in both
scopes.

---

### #34 AI Maturity Level (L1-L5) — Outcome — blocked

**Formula:** Aggregate rubric score across 7 dimensions (0-5 each) -> map to L1-L5 scale

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Quarterly 7-dimension maturity rubric score | unavailable | ext | — | manual.maturityRubricScore | Requires a manual structured assessment (Cybage AI Maturity Assessment rubric); no tool produces a maturity-level rubric score |

**Blocker:** Manual maturity-rubric assessment. Blocked in both scopes.

---

### #35 Daily AI Token Consumption per Developer — Utilization — computable (needs Claude)

**Formula:** Sum(Prompt tokens + Completion tokens) per developer per day

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Tokens consumed (input + output) | live | CL | claude-code-analytics | input_tokens + output_tokens | — (3-tool: blocked — Claude out of scope; Copilot exposes no token counts) |
| Active Claude developers | live | CL | claude-code-analytics | distinct actors | — (3-tool: blocked — Claude out of scope) |

Computable in 4-tool scope. **Without Claude (3-tool): blocked** — token data is
Claude-only; GitHub Copilot exposes no per-developer/org token counts.

---

### #36 Token Cost per Story Point — Outcome — computable (needs Claude)

**Formula:** Total AI token cost ($) / Story points delivered

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Actual AI spend (USD, billed) | live | CL | claude-cost-report | total_cost_usd | — (3-tool: blocked — Claude is the only source of real metered token cost) |
| Sprint velocity (points) | live | JR | agile/sprints | sprintVelocity | — |

Computable in 4-tool scope. **Without Claude (3-tool): blocked** — metered token
cost (totalCostUsd) is Claude-only; Jira velocity alone is insufficient.

---

### #37 AI-Suggested LOC per Developer per Sprint — Utilization — computable `[script]`

**Formula:** Sum(LOC in AI suggestions shown) per developer per sprint

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Lines suggested (loc_suggested_to_add_sum) | live | CP | org-metrics-users-28-day-latest | loc_suggested_to_add_sum | — |
| Active developers (window) | live | CP | org-metrics-users-28-day-latest | user_login (distinct active) | — |

Computable in both scopes.

---

### #38 AI-Accepted LOC Rate — Utilization — computable `[script]`

**Formula:** (AI-accepted LOC / AI-suggested LOC) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Lines accepted (loc_added_sum) | live | CP | org-metrics-organization-28-day-latest | loc_added_sum | — |
| Lines suggested (loc_suggested_to_add_sum) | live | CP | org-metrics-users-28-day-latest | loc_suggested_to_add_sum | — |

Computable in both scopes.

---

### #39 Net AI-Contributed LOC per Developer per Sprint — Utilization — computable `[script]`

**Formula:** Sum(AI-accepted and retained LOC) per developer per sprint

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Lines accepted (loc_added_sum) | live | CP | org-metrics-organization-28-day-latest | loc_added_sum | — |
| Active developers (window) | live | CP | org-metrics-users-28-day-latest | user_login (distinct active) | — |

Computable in both scopes.

---

### #40 AI Chat Sessions per Developer per Sprint — Utilization — computable (needs Claude)

**Formula:** Count(AI chat sessions) per developer per sprint

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Claude Code sessions | live | CL | claude-code-analytics | sessions | — (3-tool: blocked — Claude out of scope; Copilot exposes no IDE session counts) |
| Active Claude developers | live | CL | claude-code-analytics | distinct actors | — (3-tool: blocked — Claude out of scope) |

Computable in 4-tool scope. **Without Claude (3-tool): blocked** — chat sessions
are Claude-only (Claude Code Analytics); Copilot exposes no IDE session metric.

---

### #41 AI Chat Session Depth (Average Turns per Session) — Utilization — pending (needs Claude)

**Formula:** Total prompt-response turns / Number of chat sessions

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Total prompt-response turns | pending | CL | — | claude conversation turn count | Per-session turn counts are a Claude pending input (3-tool: blocked — Claude out of scope) |
| Claude Code sessions | live | CL | claude-code-analytics | sessions | — (3-tool: blocked — Claude out of scope) |

Pending in 4-tool scope (turn count pending). **Without Claude (3-tool):
blocked** — both turn count and sessions are Claude-only; no in-scope tool
supplies chat session depth.

---

### #42 AI Suggestion Response Latency — Adoption — blocked

**Formula:** Median(Suggestion render timestamp - Trigger timestamp) in ms

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| AI suggestion render latency (ms) | unavailable | ext | — | apm.suggestionLatency.p95 | Requires IDE/APM client-side telemetry of trigger-to-render time; no executive API exposes per-suggestion latency |

**Blocker:** IDE/APM client-side latency telemetry (external). Blocked in both
scopes.

---

### #43 AI-Assisted Debugging Time Reduction — Velocity — blocked

**Formula:** ((Unassisted debug time - AI-assisted debug time) / Unassisted debug time) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Debug time per bug, AI-assisted vs unassisted | unavailable | ext | — | IDE time-tracking (WakaTime/Haystack) + Jira time-in-status | Requires per-bug debugging duration split by AI vs non-AI from IDE time-tracking correlated with defect resolution; no tool attributes debugging time to a bug |

**Blocker:** IDE time-tracking (WakaTime/Haystack). Blocked in both scopes.

---

### #44 Context Window Utilization Rate — Utilization — pending (needs Claude)

**Formula:** (Actual prompt tokens / Max context window tokens) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Actual prompt tokens per session | pending | CL | — | claude input tokens per session | Per-session prompt-token utilisation is a Claude pending input (3-tool: blocked — Claude out of scope) |
| Max context window (tokens) | pending | CL | — | claude model max context tokens | Model context-window size is a Claude pending input (3-tool: blocked — Claude out of scope) |

Pending in 4-tool scope. **Without Claude (3-tool): blocked** — both inputs are
Claude-sourced; no in-scope tool surfaces per-session prompt tokens or model
context-window size.

---

### #45 Developer Adoption Level Distribution (Level 0-5 + Rockstar) — Adoption — pending

**Formula:** % at each level = Count(developers at Level N) / Total licensed developers x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Per-developer Copilot adoption level (0-5 + Rockstar) | pending | CP | — | copilot.adoptionLevels.byDeveloper | Copilot exposes an Adoption Levels API but per-developer level classification is not surfaced yet |
| Licensed seats | live | CP | org-billing-seats | total_seats | — |

**Blocker:** Unwired Copilot Adoption Levels per-developer classification. Pending
in both scopes.

---

### #46 % Developers at Adoption Level 3+ (Consistent Daily Usage) — Adoption — pending

**Formula:** (Developers at Level 3 or above / Total licensed developers) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Count of developers at Copilot adoption Level 3+ | pending | CP | — | copilot.adoptionLevels.level3PlusCount | Copilot exposes the Adoption Levels API but the count at Level 3+ is not surfaced yet |
| Licensed seats | live | CP | org-billing-seats | total_seats | — |

**Blocker:** Unwired Level 3+ count from Copilot Adoption Levels. Pending in both
scopes.

---

### #47 % Developers at Rockstar Adoption Level — Adoption — pending

**Formula:** (Developers at Rockstar level / Total licensed developers) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Count of developers at Copilot Rockstar tier | pending | CP | — | copilot.adoptionLevels.rockstarCount | Copilot exposes the Adoption Levels API but the Rockstar-tier count is not surfaced yet |
| Licensed seats | live | CP | org-billing-seats | total_seats | — |

**Blocker:** Unwired Rockstar-tier count. Pending in both scopes.

---

### #48 Mean Time to Advance Adoption Level — Adoption — pending

**Formula:** Median(Date reached Level N+1 - Date reached Level N) per transition in days

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Copilot adoption level-change timestamps per developer | pending | CP | — | copilot.adoptionLevels.levelChangeEvents | Copilot Adoption Levels API can emit level-change events but per-developer transition timestamps are not surfaced yet |

**Blocker:** Unwired level-change event timestamps. Pending in both scopes.

---

### #49 Average Daily Active AI Days per Developer per Week — Adoption — pending

**Formula:** Mean(Days with >=1 AI action per week) per developer

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Per-developer count of daily-active days per week | pending | CP | — | copilot.dailyActiveUsers.daysPerDeveloper | Copilot exposes daily active events but only the weekly active aggregate is surfaced, not per-developer active-day counts |

**Blocker:** Unwired per-developer daily-active-day counts. Pending in both scopes.

---

### #50 Consecutive Active Weeks Streak (Adoption Consistency Score) — Adoption — pending

**Formula:** Max consecutive weeks meeting daily active threshold per developer

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Per-developer consecutive active-week streak | pending | CP | — | copilot.weeklyActiveUsers.streakPerDeveloper | Streaks need per-developer weekly active history; Copilot exposes weekly active events but the pipeline does not retain the per-developer history needed |

**Blocker:** Unwired per-developer weekly active history (for streaks). Pending in
both scopes.

---

### #51 High-Output Week Rate (Level 4/5 Threshold Metric) — Utilization — pending

**Formula:** (Weeks meeting high-output LOC threshold / Total active weeks) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Per-developer weekly accepted-LOC history (for P75 + thresholding) | pending | CP | — | copilot.linesAccepted weekly per-user series | Copilot exposes weekly lines_accepted per user, but the per-developer weekly cohort history to compute the P75 threshold is not surfaced yet |
| Total active weeks per developer | pending | CP | — | copilot weekly active-user series | Derivable from Copilot weekly active history but not surfaced as a pipeline input yet |

**Blocker:** Unwired per-developer weekly LOC/active-week history. Pending in both
scopes.

---

### #52 AI Tool Active User Churn Rate (Level Regression Rate) — Adoption — pending

**Formula:** (Developers who regressed in level / Developers at L3+ at month start) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Copilot adoption level downgrade events per month | pending | CP | — | copilot.adoptionLevels.levelChangeEvents.downgrade | Copilot can emit level_change events with direction, but downgrade events and the L3+ baseline cohort are not surfaced yet |

**Blocker:** Unwired downgrade events + L3+ baseline cohort. Pending in both scopes.

---

### #53 AI Coding Efficiency (Lines Added per Dollar Spent) — Outcome — computable (needs Claude)

**Formula:** Lines Added / AI Spend ($) = Lines per Dollar

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Lines added (Claude Code) | live | CL | claude-code-analytics | lines_added | — (3-tool: blocked — Claude out of scope) |
| Actual AI spend (USD, billed) | live | CL | claude-cost-report | total_cost_usd | — (3-tool: blocked — no in-scope tool supplies metered AI spend) |

Computable in 4-tool scope. **Without Claude (3-tool): blocked** — both
lines-added and metered billed cost are supplied only by Claude Code Analytics /
Cost Report.

---

### #54 Lines Added vs Lines Removed Ratio — Utilization — computable `[script]`

**Formula:** Lines Added / Lines Removed

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Lines accepted (loc_added_sum) | live | CP | org-metrics-organization-28-day-latest | loc_added_sum | — |
| Lines deleted (loc_deleted_sum) | live | CP | org-metrics-users-28-day-latest | loc_deleted_sum | — |

Computable in both scopes (Copilot supplies both accepted/added and deleted
lines).

---

### #55 AI Spend per Developer per Week — Outcome — computable (needs Claude)

**Formula:** Sum(AI inference cost + pro-rated subscription) per developer per week

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Actual AI spend (USD, billed) | live | CL | claude-cost-report | total_cost_usd | — (3-tool: blocked — Claude out of scope) |
| Active Claude developers | live | CL | claude-code-analytics | distinct actors | — (3-tool: blocked — Claude out of scope) |

Computable in 4-tool scope. **Without Claude (3-tool): blocked** — billed cost +
active-dev count are supplied only by Claude (Cost Report / Code Analytics).

---

### #56 Team AI Budget Utilisation Rate — Outcome — blocked

**Formula:** (Actual AI spend to date / Allocated budget) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Actual AI spend (USD, billed) | live | CL | claude-cost-report | total_cost_usd | — (3-tool: blocked — Claude out of scope) |
| Allocated AI budget ($) | unavailable | ext | — | finance.allocatedBudget | Requires a finance/ERP or budget-management system (Azure Cost Management, AWS Budgets, finance allocation); no tool supplies the allocated budget |

**Blocker:** Finance/budget system for the allocated-budget denominator (external)
— blocks the KPI in both scopes. The Claude spend numerator is live in 4-tool but
also blocked in 3-tool.

---

### #57 AI Spend Forecast Accuracy (Best vs Expected vs Actual) — Outcome — blocked

**Formula:** Forecast Variance % = ((Actual - Expected) / Expected) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Actual AI spend (USD, billed) | live | CL | claude-cost-report | total_cost_usd | — (3-tool: blocked — Claude out of scope) |
| BEST/WORST/EXPECTED AI spend forecast | unavailable | ext | — | finance.spendForecast | Requires a finance/budget forecast module (GitClear budget forecast, finance ERP forecast vs actual); no tool produces three-point spend forecasts |

**Blocker:** Finance/budget forecast module (external) — blocks the KPI in both
scopes. The Claude actual-spend input is live in 4-tool but also blocked in
3-tool.

---

### #58 Copilot Interactions per Session — Utilization — pending

**Formula:** Total Copilot interaction events / Number of sessions

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| User-initiated interactions | live | CP | org-metrics-organization-28-day-latest | user_initiated_interaction_count | — |
| Copilot sessions | pending | CP | — | copilot session count (not in Copilot Metrics API) | Copilot exposes interaction events but does NOT provide IDE session counts; the per-session denominator needs wiring (or a session proxy) |

**Blocker:** Copilot exposes no IDE session count; the denominator needs a wired
proxy. Pending in both scopes.

---

### #59 Lines Added per AI Session — Utilization — computable (needs Claude)

**Formula:** Total Lines Added / Number of Sessions

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Lines added (Claude Code) | live | CL | claude-code-analytics | lines_added | — (3-tool: blocked — Claude out of scope) |
| Claude Code sessions | live | CL | claude-code-analytics | sessions | — (3-tool: blocked — Copilot cannot supply sessions) |

Computable in 4-tool scope. **Without Claude (3-tool): blocked** — both
lines-added and sessions are Claude-only; Copilot cannot supply a session count.

---

### #60 Individual Developer AI Maturity Level (Team Distribution) — Adoption — pending

**Formula:** Distribution: % of developers at each Level (1-5); Mean = Sum(levels) / Count(developers)

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Per-developer AI maturity level (1-5) | pending | CP | — | copilot.adoptionLevels.maturityByDeveloper | Copilot's adoption/maturity level can be classified per developer, but per-developer maturity badges / the team distribution are not surfaced yet |

**Blocker:** Unwired per-developer Copilot maturity classification. Pending in both
scopes.

---

### #61 Team Adoption Score (Average vs Top Developer) — Adoption — pending

**Formula:** AVG = Mean(adoption scores); TOP = Max(adoption score); Gap = TOP - AVG

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Per-developer adoption score within a team | pending | CP | — | copilot.adoptionLevels.scoreByDeveloperByTeam | Team AVG/TOP need per-developer adoption scores grouped by team; Copilot exposes per-user activity but no per-developer adoption score or team grouping is surfaced yet |

**Blocker:** Unwired per-developer adoption score + team grouping. Pending in both
scopes.

---

### #62 Active Users Rate per Team (Licences Activated) — Adoption — pending

**Formula:** (Active team members / Total licensed team members) x 100

| Input | 4-tool avail | Tool | Endpoint | Field | Reason if not live |
|-------|--------------|------|----------|-------|--------------------|
| Active members per team | pending | CP | org-metrics-user-teams-1-day | team_id / slug | Needs the user-teams report joined with per-user activity; not yet aggregated (org-level is live) |
| Licensed members per team | pending | CP | org-metrics-user-teams-1-day | team_id / slug | Per-team licensed counts need the same user-teams join; teams with <5 seats/day are excluded by GitHub |

**Blocker:** Unwired user-teams join (per-team active + licensed members). Pending
in both scopes.

---

## 6. Datapoint catalog (appendix)

Canonical per-datapoint availability list. Two parts:

1. **INPUTS registry** (the reusable `INPUTS.<key>` entries from `inputs.ts`).
2. **Inline KPI inputs** (datapoints defined directly on a KPI, not in the
   registry) — listed by the KPI that owns them.

The "4-tool avail" column is the primary in-scope value (GitHub Copilot, GitHub,
Jira, Claude). The "3-tool avail" column applies the without-Claude fallback;
where it differs from the 4-tool value the change is the Claude drop.

### 6a. INPUTS registry (from inputs.ts)

| Key | Label | 4-tool avail | 3-tool avail | Tool | Endpoint | Field | Reason |
|-----|-------|--------------|--------------|------|----------|-------|--------|
| activeUsersWeekly | Weekly active developers | live | live | CP | org-metrics-organization-28-day-latest | weekly_active_users | — |
| activeDevCount | Active developers (window) | live | live | CP | org-metrics-users-28-day-latest | user_login (distinct active) | — |
| licensedSeats | Licensed seats | live | live | CP | org-billing-seats | total_seats | — |
| acceptedSuggestions | Accepted suggestions | live | live | CP | org-metrics-organization-28-day-latest | code_acceptance_activity_count | — |
| shownSuggestions | Suggestions shown | live | live | CP | org-metrics-organization-28-day-latest | code_generation_activity_count | Copilot reports code_generation_activity_count (suggestions generated), the closest documented proxy for "shown" |
| linesAccepted | Lines accepted (loc_added_sum) | live | live | CP | org-metrics-organization-28-day-latest | loc_added_sum | — |
| linesSuggested | Lines suggested (loc_suggested_to_add_sum) | live | live | CP | org-metrics-users-28-day-latest | loc_suggested_to_add_sum | — |
| linesDeleted | Lines deleted (loc_deleted_sum) | live | live | CP | org-metrics-users-28-day-latest | loc_deleted_sum | — |
| interactions | User-initiated interactions | live | live | CP | org-metrics-organization-28-day-latest | user_initiated_interaction_count | — |
| activeUsersDay30 | Active users at Day 30 (cohort) | pending | pending | CP | org-metrics-users-1-day | day / user_login | Per-user daily activity is available (users-1-day, ~1yr), but cohort retention needs a time-series ETL not wired |
| activeUsersDay90 | Active users at Day 90 (cohort) | pending | pending | CP | org-metrics-users-1-day | day / user_login | Same cohort-history ETL as Day 30; daily data exists but the 90-day rollup isn't built |
| teamActiveMembers | Active members per team | pending | pending | CP | org-metrics-user-teams-1-day | team_id / slug | Needs the user-teams report joined with per-user activity; not yet aggregated (org-level is live) |
| teamLicensedMembers | Licensed members per team | pending | pending | CP | org-metrics-user-teams-1-day | team_id / slug | Per-team licensed counts need the same user-teams join; teams with <5 seats/day are excluded by GitHub |
| claudeTokensPerWindow | Tokens consumed (input + output) | live | **blocked** | CL | claude-code-analytics | input_tokens + output_tokens | Live via Claude in 4-tool; blocked without Claude |
| claudeActiveDevelopers | Active Claude developers | live | **blocked** | CL | claude-code-analytics | distinct actors | Live via Claude in 4-tool; blocked without Claude |
| claudeTotalCostUsd | Actual AI spend (USD, billed) | live | **blocked** | CL | claude-cost-report | total_cost_usd | Live via Claude in 4-tool; blocked without Claude |
| claudeCodeCostUsd | Claude Code estimated cost (USD) | live | **blocked** | CL | claude-code-analytics | estimated_cost | Live via Claude in 4-tool; blocked without Claude |
| claudeSessions | Claude Code sessions | live | **blocked** | CL | claude-code-analytics | sessions | Live via Claude in 4-tool; blocked without Claude |
| claudeLinesAdded | Lines added (Claude Code) | live | **blocked** | CL | claude-code-analytics | lines_added | Live via Claude in 4-tool; blocked without Claude |
| claudeAcceptanceRate | Tool acceptance rate (Claude Code) | live | **blocked** | CL | claude-code-analytics | tool_acceptance_rate | Live via Claude in 4-tool; blocked without Claude |
| ghDeploymentFreqPerWeek | Deployments per week (DORA) | live | live | GH | actions/deployments | deploymentFrequencyPerWeek | — |
| ghLeadTimeHours | Lead time for changes, hours (DORA) | live | live | GH | actions/commits | leadTimeHours (commit->deploy proxy) | — |
| ghTimeToMergeHours | Median PR open->merge, hours | live | live | GH | pulls | medianTimeToMergeHours | — |
| ghPrsMergedPerWeek | PRs merged per week | live | live | GH | pulls | prsMergedPerWeek | — |
| ghCiSuccessRate | CI success rate | live | live | GH | actions/runs | ciSuccessRate | — |
| jiraSprintCompletionRate | Sprint completion rate | live | live | JR | agile/sprints | sprintCompletionRate | — |
| jiraSprintVelocity | Sprint velocity (points) | live | live | JR | agile/sprints | sprintVelocity | — |
| jiraCycleTimeHours | Median cycle time, hours | live | live | JR | search + changelog | cycleTimeHoursMedian | — |
| jiraLeadTimeHours | Median lead time, hours | live | live | JR | search | leadTimeHoursMedian | — |
| jiraThroughputPerWeek | Issues resolved per week | live | live | JR | search | throughputPerWeek | — |
| jiraOpenBugs | Open bugs (defects) | live | live | JR | search (type=Bug) | openBugs | — |
| tokensPerDev | Tokens consumed per developer (Copilot) | unavailable | unavailable | CP | — | — | GitHub Copilot exposes no per-developer/org token counts. (Use Claude tokens instead for Claude users.) |
| suggestionLatency | Suggestion response latency (ms) | unavailable | unavailable | CP | — | — | No tool exposes suggestion render latency; requires client-side IDE telemetry no API surfaces |
| allocatedBudget | Allocated AI budget ($) | unavailable | unavailable | CL/ext | — | — | Budget is finance/ERP data — not exposed by any tool API. Needs a manual budget input |
| trainingCompletion | Training module completion | unavailable | unavailable | CP/ext | — | — | Lives in an LMS (Workday Learning, Cornerstone, etc.) — no AI-tool API supplies it |
| surveyNps | Developer NPS / survey responses | unavailable | unavailable | CP/ext | — | — | Requires a developer survey (dNPS); no tool API supplies sentiment |
| testCoverage | Test coverage % | unavailable | unavailable | GH/ext | — | — | Requires a coverage tool (SonarQube/Codecov) or CI coverage artifacts — not surfaced by Copilot/GitHub/Jira/Claude |

Note on the seven Claude registry inputs (claudeTokensPerWindow, claudeActiveDevelopers,
claudeTotalCostUsd, claudeCodeCostUsd, claudeSessions, claudeLinesAdded,
claudeAcceptanceRate): all are `live` in the 4-tool scope and all fall back to
`blocked` in the without-Claude (3-tool) view. There is no in-scope substitute —
GitHub Copilot exposes no token, cost, or IDE-session data.

### 6b. Inline KPI inputs (defined on a KPI, not in the registry)

| Owner KPI | Input id | Label | 4-tool avail | 3-tool avail | Tool | Field | Reason |
|-----------|----------|-------|--------------|--------------|------|-------|--------|
| #2 | hr.provisioningDate | AI tool provisioning date per developer | unavailable | unavailable | CP/ext | scim.user.provisionedAt | Requires SCIM/HRIS seat-provisioning timestamp; no GenAI tool supplies the license-grant date |
| #2 | github.firstAiAssistedPrMergeDate | First AI-assisted PR merge date per developer | pending | pending | CP/GH | github.pulls.mergedAt | GitHub PR merge timestamps + Copilot per-user activity exist, but accept events are not joined to a first merged PR yet |
| #3 | lms.completedModules | Completed training modules | unavailable | unavailable | ext | lms.completions.count | Requires an LMS; no GenAI coding tool tracks training completion |
| #3 | lms.enrolledDevelopers | Enrolled developers | unavailable | unavailable | ext | lms.enrollments.count | Requires LMS/HR enrollment records |
| #4 | manual.promptRubricScore | Rubric-assessed prompt quality score | unavailable | unavailable | ext | manual.rubric.median | Requires a manual rubric / CoE prompt-audit of prompt text |
| #6 | manual.activeCapabilityAreas | Active AI capability areas (of 19) | unavailable | unavailable | ext | CoE capability tracker | No tool tracks SDLC capability-area activation; manual CoE tracker |
| #7 | copilot.aiAssistedCommits | AI-assisted commits | pending | pending | CP | accepted-suggestion-to-commit attribution | Copilot accept telemetry attributable to commits, but per-commit AI attribution not surfaced yet |
| #7 | github.totalCommits | Total commits | pending | pending | GH | github commits API | GitHub commit counts exist but total-commits-per-period not surfaced yet |
| #9 | github.prsWithAiFirstPassReview | PRs with AI first-pass review | pending | pending | GH | github PR review events (bot author) | Bot/AI reviewer authorship exposed, but AI-first-pass-review counts not surfaced yet |
| #10 | github.modulesWithAiTestStubs | Modules with AI-generated test stubs | pending | pending | GH | github Actions CI annotation / commit label | CI metadata can carry AI test-stub annotations, but AI-test-generation counts not surfaced yet |
| #10 | github.newModulesMerged | Total new modules merged | pending | pending | GH | github merged PR file stats | Merged-PR/file data exists but new-modules-merged counts not surfaced yet |
| #11 | github.prsWithAiDocs | PRs with accepted AI-generated docs | pending | pending | GH | github PR label 'ai-docs-included' | PR labels/checks exposed, but AI-docs PR counts not surfaced yet |
| #12 | manual.activeAgentRoles | Active agentic mesh roles (of 6) | unavailable | unavailable | ext | agent orchestration tracker | No tool tracks agent-mesh activation; external tracker + manual rollup |
| #13 | manual.preAiCeremonyTime | Pre-AI ceremony time per sprint | unavailable | unavailable | ext | calendar API / time-tracking baseline | Requires calendar/time-tracking + pre-AI baseline; no tool supplies ceremony time |
| #13 | manual.postAiCeremonyTime | Post-AI ceremony time per sprint | unavailable | unavailable | ext | calendar API / time-tracking | Requires calendar/time-tracking of meeting durations |
| #14 | jira.aiTaggedDefects | Defects tagged AI-gen-source | pending | pending | JR | issue.fields.customfield_aiGenSource | Jira bugs + custom fields exist, but an AI-gen-source field attributing defects to AI code is not wired (only openBugs) |
| #14 | quality.preAiDefectBaseline | Pre-AI defect density baseline | unavailable | unavailable | ext | manual baseline (historical defect tracker) | Requires a historical pre-AI defect-density baseline; manual |
| #15 | github.codeScanningFindings | New SAST/code-scanning findings | pending | pending | GH | github.code_scanning.alerts (per PR) | Code/secret-scanning + Dependabot counts exposed, but per-PR scan findings not wired yet |
| #15 | github.aiAssistedPrCount | AI-assisted PR count | pending | pending | GH | github.pulls (AI-assisted attribution) | PR metadata + Copilot aggregates exist, but AI-assisted attribution not surfaced |
| #16 | quality.aiErrorClassifiedBlocks | AI blocks rejected for factual errors / hallucination | unavailable | unavailable | ext | manual review rubric / external AI-review classifier | No tool classifies error/hallucination of AI review comments; needs manual rubric or CodeRabbit/Qodo |
| #16 | quality.aiBlocksReviewed | Total AI-generated blocks reviewed | unavailable | unavailable | ext | manual review tagging / external AI-review tool | Count of AI-generated blocks entering review not produced by any tool |
| #17 | github.reworkPrCount | AI-assisted PRs with >50% line rework within 48h | pending | pending | GH | github.commits (line delta within 48h) | Commit line-delta data exists, but a rework metric not surfaced yet |
| #17 | github.aiAssistedPrCount | Total AI-assisted PRs | pending | pending | GH | github.pulls (AI-assisted attribution) | Which PRs are AI-assisted not surfaced yet |
| #18 | github.gatePassEvents | AI outputs approved at gate without rework | pending | pending | GH | github.required_status_checks / review approval events | Required-review status-check pass/fail can model HITL gate, but AI-scoped gate events not surfaced yet |
| #18 | github.gateSubmissions | Total HITL gate submissions | pending | pending | GH | github.pull_request_review / status-check submissions | Review/status-check submissions exposed, but AI-scoped totals not surfaced yet |
| #19 | quality.incidentDetectionTimestamps | Defect/incident detection timestamps | unavailable | unavailable | ext | external incident/APM (PagerDuty/Datadog) | Requires incident/defect detection timestamps from an external incident/APM source |
| #19 | jira.aiTaggedDefects | AI-attributed defects with merge timestamp | pending | pending | JR | issue.fields.customfield_aiGenSource + merge timestamp | Jira bug timestamps exist, but AI-gen-source attribution + AI-commit merge linkage not surfaced yet |
| #20 | quality.testCoverageAiAssisted | Test coverage % for AI-assisted code | unavailable | unavailable | ext | external coverage tool (Codecov/SonarQube) | Coverage not supplied by any tool; external coverage tool not wired |
| #20 | quality.preAiCoverageBaseline | Pre-AI baseline coverage % | unavailable | unavailable | ext | manual baseline (historical coverage data) | Requires a manually established pre-AI coverage baseline |
| #21 | manual.preAiCycleTimeBaseline | Pre-AI median commit-to-deploy baseline | unavailable | unavailable | ext | manual baseline snapshot | Requires a manually captured pre-AI baseline; post-AI value is computable via GitHub DORA lead time |
| #26 | github.changeFailureRate | DORA change failure rate (%) | pending | pending | GH | github deployment status (success vs failure/rollback) ratio | Deployment statuses + Actions outcomes exist to derive CFR, but a CFR field is not wired yet |
| #27 | incident.mttrHours | Mean time to restore (hours) | unavailable | unavailable | ext | PagerDuty incident open/resolve timestamps | Requires incident open/resolve timestamps from an incident-management tool; incidents not modelled |
| #28 | preAiMedianTtm | Pre-AI median time-to-market baseline | pending | pending | ext/manual | manual.preAiMedianTtm | Post-AI TTM derivable from Jira lead time, but pre-AI median TTM must be captured manually |
| #29 | laborCost | Engineering labor hours x hourly rate | unavailable | unavailable | ext | hris.laborCost | Requires HRIS/payroll (Workday) for labor hours/rates plus a rework-cost feed |
| #30 | netBenefits | Net programme benefits | unavailable | unavailable | ext | finance.netBenefits | Requires finance/ERP (SAP, Workday Financials) for labor savings, rework reduction, revenue acceleration |
| #31 | surveyNps | Quarterly developer NPS survey result | unavailable | unavailable | ext | survey.dnps | Requires a survey/dNPS platform (Glint, Culture Amp, DX/GetDX, Typeform) |
| #32 | clientDefects | Client-reported defects per release | unavailable | unavailable | ext | zendesk.clientDefects | Requires a customer support/CRM (Zendesk, Salesforce Service Cloud, HubSpot); Jira openBugs are internal-only |
| #33 | flowTimeNonFeaturePct | Non-feature time % (pre and post AI) | unavailable | unavailable | ext | linearb.nonFeatureTimePct | Requires flow-time/time-tracking (LinearB, DX) + manual pre-AI baseline |
| #34 | maturityRubricScore | Quarterly 7-dimension maturity rubric score | unavailable | unavailable | ext | manual.maturityRubricScore | Requires a manual structured assessment (Cybage AI Maturity rubric) |
| #41 | claude.chatTurns | Total prompt-response turns | pending | **blocked** | CL | claude conversation turn count | Pending via Claude in 4-tool; blocked without Claude; per-session turn counts not surfaced |
| #42 | manual.suggestionLatencyMs | AI suggestion render latency (ms) | unavailable | unavailable | ext | apm.suggestionLatency.p95 | Requires IDE/APM client-side trigger-to-render telemetry; no API exposes per-suggestion latency |
| #43 | timetracking.debugTimeAiVsUnassisted | Debug time per bug, AI-assisted vs unassisted | unavailable | unavailable | ext | IDE time-tracking (WakaTime/Haystack) + Jira time-in-status | Requires per-bug debugging duration split by AI vs non-AI; no tool attributes debugging time to a bug |
| #44 | claude.promptTokensPerSession | Actual prompt tokens per session | pending | **blocked** | CL | claude input tokens per session | Pending via Claude in 4-tool; blocked without Claude; per-session prompt-token utilisation not surfaced |
| #44 | claude.maxContextWindow | Max context window (tokens) | pending | **blocked** | CL | claude model max context tokens | Pending via Claude in 4-tool; blocked without Claude; model context-window size not surfaced alongside session tokens |
| #45 | copilot.adoptionLevelDistribution | Per-developer Copilot adoption level (0-5 + Rockstar) | pending | pending | CP | copilot.adoptionLevels.byDeveloper | Adoption Levels API exists but per-developer level classification not surfaced yet |
| #46 | copilot.developersAtLevel3Plus | Count of developers at Copilot adoption Level 3+ | pending | pending | CP | copilot.adoptionLevels.level3PlusCount | Adoption Levels API exists but Level 3+ count not surfaced yet |
| #47 | copilot.developersAtRockstarLevel | Count of developers at Copilot Rockstar tier | pending | pending | CP | copilot.adoptionLevels.rockstarCount | Adoption Levels API exists but Rockstar-tier count not surfaced yet |
| #48 | copilot.adoptionLevelChangeTimestamps | Copilot adoption level-change timestamps per developer | pending | pending | CP | copilot.adoptionLevels.levelChangeEvents | Level-change events possible but per-developer transition timestamps not surfaced yet |
| #49 | copilot.dailyActiveDaysPerDeveloper | Per-developer count of daily-active days per week | pending | pending | CP | copilot.dailyActiveUsers.daysPerDeveloper | Daily active events exposed but only weekly aggregate surfaced, not per-developer active-day counts |
| #50 | copilot.weeklyActiveStreakPerDeveloper | Per-developer consecutive active-week streak | pending | pending | CP | copilot.weeklyActiveUsers.streakPerDeveloper | Weekly active events exposed but per-developer weekly history (for streaks) not retained |
| #51 | copilot.weeklyLinesAcceptedHistory | Per-developer weekly accepted-LOC history | pending | pending | CP | copilot.linesAccepted weekly per-user series | Weekly lines_accepted per user exposed, but per-developer weekly cohort history (for P75) not surfaced yet |
| #51 | copilot.activeWeeks | Total active weeks per developer | pending | pending | CP | copilot weekly active-user series | Derivable from weekly active history but not surfaced as a pipeline input yet |
| #52 | copilot.adoptionLevelDowngradeEvents | Copilot adoption level downgrade events per month | pending | pending | CP | copilot.adoptionLevels.levelChangeEvents.downgrade | Level_change events with direction possible, but downgrade events + L3+ baseline cohort not surfaced yet |
| #56 | allocatedBudget | Allocated AI budget ($) | unavailable | unavailable | ext | finance.allocatedBudget | Requires a finance/ERP or budget-management system (Azure Cost Management, AWS Budgets, finance allocation) |
| #57 | spendForecast | BEST/WORST/EXPECTED AI spend forecast | unavailable | unavailable | ext | finance.spendForecast | Requires a finance/budget forecast module (GitClear budget forecast, finance ERP forecast vs actual) |
| #58 | copilot.sessions | Copilot sessions | pending | pending | CP | copilot session count (not in Copilot Metrics API) | Copilot exposes interaction events but NOT IDE session counts; denominator needs wiring (or a session proxy) |
| #60 | copilot.maturityLevelPerDeveloper | Per-developer AI maturity level (1-5) | pending | pending | CP | copilot.adoptionLevels.maturityByDeveloper | Per-developer maturity can be classified, but per-developer badges / team distribution not surfaced yet |
| #61 | copilot.adoptionScorePerDeveloper | Per-developer adoption score within a team | pending | pending | CP | copilot.adoptionLevels.scoreByDeveloperByTeam | Team AVG/TOP need per-developer scores grouped by team; not surfaced yet |

---

## Appendix: derivation notes

- Verdict roll-up: `unavailable` in any input -> blocked; else `pending` in any
  input -> pending; else computable. (Mirrors genai-tracker `kpiFeasibility()`.)
  The 4-tool verdicts in this document equal that source rollup.
- Without-Claude (3-tool) reclassification: every input whose only live/pending
  source is Claude is reclassified to blocked. This affects the seven Claude
  registry inputs and the three inline Claude inputs (#41 claude.chatTurns,
  #44 claude.promptTokensPerSession, #44 claude.maxContextWindow), which in turn
  changes the verdict of KPIs #35, #36, #40, #41, #44, #53, #55, #59 (each tagged
  `(needs Claude)` above).
- External-source inputs (LMS, survey, finance/budget, coverage, HRIS/SCIM,
  incident/APM, CRM/support, manual rubric/baseline) are `unavailable` in both the
  4-tool and 3-tool scope.
- GitHub Copilot, GitHub, and Jira inputs are identical in both scopes.
- The headline 4-tool counts (16 computable / 24 pending / 22 blocked) are derived
  directly from the per-KPI verdicts above and reconcile with the genai-tracker
  source (`catalogGenerated.ts` + `inputs.ts`). The 3-tool counts (10 / 22 / 30)
  differ only by the eight `(needs Claude)` KPIs falling back to blocked.
