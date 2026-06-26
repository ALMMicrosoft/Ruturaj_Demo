# GitHub Copilot - API Endpoint Reference

> Exposes org- and enterprise-scoped Copilot usage metrics reports plus seat/billing admin APIs, available on Copilot Business and Enterprise plans.

- **Vendor:** GitHub (Microsoft)
- **Docs:** https://docs.github.com/en/rest/copilot
- **Stage:** ai-assistant
- **Ingestion pattern:** Two-stage ETL for metrics reports (call report endpoint -> follow signed download link -> parse file); direct inline JSON for seat/billing endpoints.

## Plans / Tiers

| Plan | Price | Tier | Unlocks APIs | Metrics Access |
|------|-------|------|--------------|----------------|
| Copilot Free | Free | individual | No | No org/enterprise metrics or admin APIs. Individual plan with no centralized reporting, seat management, or Metrics API access. |
| Copilot Pro | $10/month (per fetched plans page) | individual | No | No org/enterprise metrics or admin APIs (individual subscription). No seat/billing API, no usage-metrics report endpoints. |
| Copilot Pro+ | $39/month (per fetched plans page) | individual | No | No org/enterprise metrics or admin APIs (individual subscription). |
| Copilot Business | $19/seat/month (per fetched plans page) | business | Yes | Unlocks centralized management and Copilot policy control. Org-level seat/billing admin API (GET/POST/DELETE /orgs/{org}/copilot/billing*), per-user seat detail (GET /orgs/{org}/members/{username}/copilot), and the org-level Copilot usage metrics report endpoints (/orgs/{org}/copilot/metrics/reports/*) once the 'Copilot usage metrics' policy is enabled. plan_type returned as 'business'. |
| Copilot Enterprise | $39/seat/month (per fetched plans page) | enterprise | Yes | All of Business PLUS enterprise-level usage metrics report endpoints (/enterprises/{enterprise}/copilot/metrics/reports/*: enterprise-1-day, enterprise-28-day/latest, users-1-day, users-28-day/latest, user-teams-1-day). Requires the 'Copilot usage metrics' policy enabled across the enterprise; only enterprise owners/billing managers can read. plan_type returned as 'enterprise'. Requires GitHub Enterprise Cloud. |

Plan sourceUrl (all rows): https://docs.github.com/en/copilot/get-started/plans-for-github-copilot

## Feasibility Verdict

**Status:** feasible-with-caveats

LIVE RE-VERIFIED 2026-06-04 (full GET sweep against org ALMCybage + enterprise cybage): all 13 tryable GET endpoints returned 200 - org + enterprise metrics reports (1-day & 28-day/latest), Copilot billing, billing seats, and per-member seat - and both retired endpoints confirmed 404. FEASIBLE on Copilot Business and Enterprise; NOT feasible on Free/Pro/Pro+ (individual plans have no org/enterprise metrics or admin APIs). Current API only; legacy endpoints retired 2026-04-02.

**Required plan:** Copilot Business ($19/seat/mo) for org-level metrics + seat/billing admin; Copilot Enterprise ($39/seat/mo, requires GitHub Enterprise Cloud) for enterprise-level rollups across orgs. The 'Copilot usage metrics' policy MUST be enabled, and only org owners / enterprise owners or billing managers can read.

**Blockers:**
1. Metrics endpoints return ONLY signed download links - you must build an ETL step to fetch and parse report files (links expire).
2. No single team-metrics endpoint - join the user-teams report with the per-user report yourself; teams with <5 seated users/day are excluded.
3. Only users with IDE telemetry enabled are counted; dashboard charts exclude CLI (CLI appears in API exports only).
4. ~2-day data latency and 204-no-data behavior are operational notes, not schema-verified.
5. Use a fine-grained PAT (View Organization/Enterprise Copilot Metrics) or classic PAT with read:org / read:enterprise.
6. Per-tier pricing/API mapping was inferred, not stated verbatim - confirm on the live plans page.

## Endpoints (20)

| id | name | method | path | response shape | deprecated? |
|----|------|--------|------|----------------|-------------|
| org-metrics-organization-1-day | Get Copilot usage metrics report for an organization (1-day) | GET | /orgs/{org}/copilot/metrics/reports/organization-1-day | download-links | no |
| org-metrics-organization-28-day-latest | Get Copilot usage metrics report for an organization (28-day latest) | GET | /orgs/{org}/copilot/metrics/reports/organization-28-day/latest | download-links | no |
| org-metrics-users-1-day | Get Copilot per-user usage metrics for an organization (1-day) | GET | /orgs/{org}/copilot/metrics/reports/users-1-day | download-links | no |
| org-metrics-users-28-day-latest | Get Copilot per-user usage metrics for an organization (28-day latest) | GET | /orgs/{org}/copilot/metrics/reports/users-28-day/latest | download-links | no |
| org-metrics-user-teams-1-day | Get Copilot user-teams report for an organization (1-day) | GET | /orgs/{org}/copilot/metrics/reports/user-teams-1-day | download-links | no |
| enterprise-metrics-enterprise-1-day | Get Copilot usage metrics report for an enterprise (1-day) | GET | /enterprises/{enterprise}/copilot/metrics/reports/enterprise-1-day | download-links | no |
| enterprise-metrics-enterprise-28-day-latest | Get Copilot usage metrics report for an enterprise (28-day latest) | GET | /enterprises/{enterprise}/copilot/metrics/reports/enterprise-28-day/latest | download-links | no |
| enterprise-metrics-users-1-day | Get Copilot per-user usage metrics for an enterprise (1-day) | GET | /enterprises/{enterprise}/copilot/metrics/reports/users-1-day | download-links | no |
| enterprise-metrics-users-28-day-latest | Get Copilot per-user usage metrics for an enterprise (28-day latest) | GET | /enterprises/{enterprise}/copilot/metrics/reports/users-28-day/latest | download-links | no |
| enterprise-metrics-user-teams-1-day | Get Copilot user-teams report for an enterprise (1-day) | GET | /enterprises/{enterprise}/copilot/metrics/reports/user-teams-1-day | download-links | no |
| org-billing | Get Copilot billing information for an organization (seat breakdown) | GET | /orgs/{org}/copilot/billing | inline-json | no |
| org-billing-seats | List all Copilot seat assignments for an organization | GET | /orgs/{org}/copilot/billing/seats | inline-json | no |
| org-member-copilot-seat | Get Copilot seat assignment details for a user | GET | /orgs/{org}/members/{username}/copilot | inline-json | no |
| org-content-exclusion | Get Copilot content exclusion rules (org) | GET | /orgs/{org}/copilot/content_exclusion | inline-json | no |
| org-coding-agent-permissions | Get Copilot coding-agent permissions (org) | GET | /orgs/{org}/copilot/coding-agent/permissions | inline-json | no |
| org-coding-agent-repositories | List repositories with Copilot coding-agent enabled (org) | GET | /orgs/{org}/copilot/coding-agent/permissions/repositories | inline-json | no |
| enterprise-custom-agents | List Copilot custom agents (enterprise) | GET | /enterprises/{enterprise}/copilot/custom-agents | inline-json | no |
| enterprise-custom-agents-source | Get Copilot custom-agents source (enterprise) | GET | /enterprises/{enterprise}/copilot/custom-agents/source | inline-json | no |
| retired-org-metrics | [RETIRED] Copilot Metrics API - organization | GET | /orgs/{org}/copilot/metrics | inline-json | YES (retired 2026-04-02) |
| retired-org-usage | [RETIRED] Copilot Usage API - organization (legacy) | GET | /orgs/{org}/copilot/usage | inline-json | YES (retired 2026-04-02) |

> Note: the catalog `endpoints[]` array contains 20 entries: 10 download-link metrics-report endpoints (5 org + 5 enterprise), 3 inline seat/billing admin endpoints, 5 governance/config readers (public preview, doc-grounded), and 2 retired endpoints (kept for documentation only, confirmed 404 live). Every one is documented in full below.

---

### org-metrics-organization-1-day - Get Copilot usage metrics report for an organization (1-day)

**Purpose:** Returns signed download link(s) to the org's Copilot usage metrics report for a single specified day. CURRENT replacement for the retired /copilot/metrics endpoint.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/metrics/reports/organization-1-day`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic personal access token or OAuth app token, or a fine-grained PAT with the 'View Organization Copilot Metrics' permission.
- Scopes: `read:org`
- Notes: Org owners and authorized users. The 'Copilot usage metrics' policy must be enabled. Fine-grained PATs ARE supported via the 'View Organization Copilot Metrics' permission.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name (case-insensitive) | octo-org |
| day | query | yes | Report day in YYYY-MM-DD format | 2026-05-30 |

**Response shape:** download-links

**Rate limits:** Subject to standard GitHub REST API rate limits; no Copilot-specific limit documented. Download links are signed URLs with limited expiration.

**Gotchas:** Returns 204 No Content if no data for that day. Data available ~within two full UTC days after the day closes. Only users with IDE telemetry enabled are counted. Dashboard charts exclude CLI usage; CLI appears in API exports only.

**Datapoints returned:**
- `daily_active_users / weekly_active_users / monthly_active_users` (engagement) - Org-wide active-user counts for the day (full schema in reportFields)
- `code_generation_activity_count / code_acceptance_activity_count` (activity-flow) - Org-wide code generation and acceptance activity for the day
- `loc_added_sum / loc_deleted_sum / loc_suggested_to_add_sum` (activity-flow) - Org-wide lines-of-code suggestion/acceptance sums
- `pull_requests.total_created_by_copilot / total_reviewed_by_copilot` (quality) - Org-wide Copilot pull-request authorship and review counts

**Report file fields:**

| path | type | category | description |
|------|------|----------|-------------|
| report_day | string | adoption | The calendar day the report covers (envelope) |
| day | string | adoption | Calendar day covered |
| organization_id | string | adoption | Organization identifier |
| enterprise_id | string | adoption | Enterprise identifier |
| daily_active_users | number | engagement | Daily active Copilot users |
| daily_active_copilot_cloud_agent_users | number | engagement | Daily active cloud agent users |
| weekly_active_users | number | engagement | Weekly active users |
| weekly_active_copilot_cloud_agent_users | number | engagement | Weekly active cloud agent users |
| monthly_active_users | number | engagement | Monthly active users |
| monthly_active_chat_users | number | engagement | Monthly active chat users |
| monthly_active_agent_users | number | engagement | Monthly active agent users |
| monthly_active_copilot_cloud_agent_users | number | engagement | Monthly active cloud agent users |
| user_initiated_interaction_count | number | engagement | User-initiated interactions |
| code_generation_activity_count | number | activity-flow | Code generation activities |
| code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| totals_by_ide[].ide | string | adoption | IDE name for the breakdown row |
| totals_by_ide[].user_initiated_interaction_count | number | engagement | User-initiated Copilot interactions in this slice |
| totals_by_ide[].code_generation_activity_count | number | activity-flow | Code generation activities in this slice |
| totals_by_ide[].code_acceptance_activity_count | number | activity-flow | Code acceptance activities in this slice |
| totals_by_ide[].loc_suggested_to_add_sum | number | activity-flow | Lines of code suggested for addition |
| totals_by_ide[].loc_suggested_to_delete_sum | number | activity-flow | Lines of code suggested for deletion |
| totals_by_ide[].loc_added_sum | number | activity-flow | Lines of code added |
| totals_by_ide[].loc_deleted_sum | number | activity-flow | Lines of code deleted |
| totals_by_feature[].feature | string | adoption | Copilot feature for the breakdown row |
| totals_by_feature[].user_initiated_interaction_count | number | engagement | User-initiated Copilot interactions in this slice |
| totals_by_feature[].code_generation_activity_count | number | activity-flow | Code generation activities in this slice |
| totals_by_feature[].code_acceptance_activity_count | number | activity-flow | Code acceptance activities in this slice |
| totals_by_feature[].loc_suggested_to_add_sum | number | activity-flow | Lines of code suggested for addition |
| totals_by_feature[].loc_suggested_to_delete_sum | number | activity-flow | Lines of code suggested for deletion |
| totals_by_feature[].loc_added_sum | number | activity-flow | Lines of code added |
| totals_by_feature[].loc_deleted_sum | number | activity-flow | Lines of code deleted |
| totals_by_language_feature[].language | string | adoption | Language for the breakdown row |
| totals_by_language_feature[].feature | string | adoption | Feature for the language breakdown row |
| totals_by_language_feature[].code_generation_activity_count | number | activity-flow | Code generation activities in this slice |
| totals_by_language_feature[].code_acceptance_activity_count | number | activity-flow | Code acceptance activities in this slice |
| totals_by_language_feature[].loc_suggested_to_add_sum | number | activity-flow | Lines of code suggested for addition |
| totals_by_language_feature[].loc_suggested_to_delete_sum | number | activity-flow | Lines of code suggested for deletion |
| totals_by_language_feature[].loc_added_sum | number | activity-flow | Lines of code added |
| totals_by_language_feature[].loc_deleted_sum | number | activity-flow | Lines of code deleted |
| totals_by_language_model[].language | string | adoption | Language for the model breakdown row |
| totals_by_language_model[].model | string | activity-flow | Model for the language breakdown row |
| totals_by_language_model[].code_generation_activity_count | number | activity-flow | Code generation activities in this slice |
| totals_by_language_model[].code_acceptance_activity_count | number | activity-flow | Code acceptance activities in this slice |
| totals_by_language_model[].loc_suggested_to_add_sum | number | activity-flow | Lines of code suggested for addition |
| totals_by_language_model[].loc_suggested_to_delete_sum | number | activity-flow | Lines of code suggested for deletion |
| totals_by_language_model[].loc_added_sum | number | activity-flow | Lines of code added |
| totals_by_language_model[].loc_deleted_sum | number | activity-flow | Lines of code deleted |
| totals_by_model_feature[].model | string | activity-flow | Model for the model/feature breakdown row |
| totals_by_model_feature[].feature | string | adoption | Feature for the model/feature breakdown row |
| totals_by_model_feature[].user_initiated_interaction_count | number | engagement | User-initiated Copilot interactions in this slice |
| totals_by_model_feature[].code_generation_activity_count | number | activity-flow | Code generation activities in this slice |
| totals_by_model_feature[].code_acceptance_activity_count | number | activity-flow | Code acceptance activities in this slice |
| totals_by_model_feature[].loc_suggested_to_add_sum | number | activity-flow | Lines of code suggested for addition |
| totals_by_model_feature[].loc_suggested_to_delete_sum | number | activity-flow | Lines of code suggested for deletion |
| totals_by_model_feature[].loc_added_sum | number | activity-flow | Lines of code added |
| totals_by_model_feature[].loc_deleted_sum | number | activity-flow | Lines of code deleted |
| loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (day total) |
| loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (day total) |
| loc_added_sum | number | activity-flow | Lines added (day total) |
| loc_deleted_sum | number | activity-flow | Lines deleted (day total) |
| pull_requests.total_reviewed | number | quality | Total PRs reviewed |
| pull_requests.total_created | number | quality | Total PRs created |
| pull_requests.total_created_by_copilot | number | quality | PRs created by Copilot |
| pull_requests.total_reviewed_by_copilot | number | quality | PRs reviewed by Copilot |
| pull_requests.total_merged | number | quality | Total PRs merged |
| pull_requests.total_suggestions | number | quality | Total review suggestions |
| pull_requests.total_applied_suggestions | number | quality | Review suggestions applied |
| pull_requests.total_merged_created_by_copilot | number | quality | Merged PRs originally created by Copilot |
| pull_requests.total_copilot_suggestions | number | quality | Total Copilot review suggestions |
| pull_requests.total_copilot_applied_suggestions | number | quality | Copilot review suggestions applied |
| pull_requests.total_merged_reviewed_by_copilot | number | quality | Merged PRs reviewed by Copilot |
| pull_requests.copilot_suggestions_by_comment_type[].comment_type | string | quality | Review comment type |
| pull_requests.copilot_suggestions_by_comment_type[].total_copilot_suggestions | number | quality | Copilot suggestions of this comment type |
| pull_requests.copilot_suggestions_by_comment_type[].total_applied_suggestions | number | quality | Applied Copilot suggestions of this comment type |
| daily_active_copilot_code_review_users | number | engagement | Daily active code-review users |
| weekly_active_copilot_code_review_users | number | engagement | Weekly active code-review users |
| monthly_active_copilot_code_review_users | number | engagement | Monthly active code-review users |
| daily_passive_copilot_code_review_users | number | engagement | Daily passive code-review users |
| weekly_passive_copilot_code_review_users | number | engagement | Weekly passive code-review users |
| monthly_passive_copilot_code_review_users | number | engagement | Monthly passive code-review users |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/orgs/octo-org/copilot/metrics/reports/organization-1-day?day=2026-05-30"
```

**Example response:**

```json
{
  "report_day": "2026-05-30",
  "download_links": [
    "https://objects.githubusercontent.com/copilot-metrics/...signed..."
  ]
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics
- https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics
- https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET method, read:org scope, fine-grained 'View Organization Copilot Metrics' permission, required YYYY-MM-DD 'day' query param, and download_links/report_day datapoints all confirmed. Fine-grained PATs ARE supported (correcting an earlier claim). 204-no-data and ~2-day latency are lower-confidence operational notes. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics?apiVersion=2026-03-10)

---

### org-metrics-organization-28-day-latest - Get Copilot usage metrics report for an organization (28-day latest)

**Purpose:** Returns download link(s) to the latest 28-day aggregated org usage metrics report.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/metrics/reports/organization-28-day/latest`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token; fine-grained PAT with 'View Organization Copilot Metrics' permission.
- Scopes: `read:org`
- Notes: Org owners; 'Copilot usage metrics' policy enabled.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits; signed URLs expire.

**Gotchas:** 28-day rolling window. Aggregated daily; latest available reflects ~2 UTC-day latency.

**Datapoints returned:**
- `day_totals[].daily_active_users / weekly_active_users / monthly_active_users` (engagement) - Per-day active-user counts across the 28-day window (one entry per day)
- `day_totals[].code_generation_activity_count / loc_added_sum` (activity-flow) - Per-day org code generation and lines-added sums
- `day_totals[].pull_requests.total_created_by_copilot` (quality) - Per-day Copilot-authored pull-request counts

**Report file fields:** (envelope + `day_totals[]` per-day rows; the per-day row schema below matches the org 1-day report fields, re-rooted under `day_totals[]`)

| path | type | category | description |
|------|------|----------|-------------|
| report_start_day | string | adoption | First day of the 28-day window (envelope) |
| report_end_day | string | adoption | Last day of the 28-day window (envelope) |
| organization_id | string | adoption | Organization identifier (report file) |
| enterprise_id | string | adoption | Enterprise identifier (report file) |
| created_at | string | adoption | When the aggregated report was created |
| day_totals[].day | string | adoption | Calendar day covered |
| day_totals[].organization_id | string | adoption | Organization identifier |
| day_totals[].enterprise_id | string | adoption | Enterprise identifier |
| day_totals[].daily_active_users | number | engagement | Daily active Copilot users |
| day_totals[].daily_active_copilot_cloud_agent_users | number | engagement | Daily active cloud agent users |
| day_totals[].weekly_active_users | number | engagement | Weekly active users |
| day_totals[].weekly_active_copilot_cloud_agent_users | number | engagement | Weekly active cloud agent users |
| day_totals[].monthly_active_users | number | engagement | Monthly active users |
| day_totals[].monthly_active_chat_users | number | engagement | Monthly active chat users |
| day_totals[].monthly_active_agent_users | number | engagement | Monthly active agent users |
| day_totals[].monthly_active_copilot_cloud_agent_users | number | engagement | Monthly active cloud agent users |
| day_totals[].user_initiated_interaction_count | number | engagement | User-initiated interactions |
| day_totals[].code_generation_activity_count | number | activity-flow | Code generation activities |
| day_totals[].code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| day_totals[].totals_by_ide[].ide | string | adoption | IDE name for the breakdown row |
| day_totals[].totals_by_ide[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-IDE code-activity breakdown (see org 1-day for full per-field descriptions) |
| day_totals[].totals_by_feature[].feature | string | adoption | Copilot feature for the breakdown row |
| day_totals[].totals_by_feature[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-feature code-activity breakdown |
| day_totals[].totals_by_language_feature[].language | string | adoption | Language for the breakdown row |
| day_totals[].totals_by_language_feature[].feature | string | adoption | Feature for the language breakdown row |
| day_totals[].totals_by_language_feature[].(code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | activity-flow | Per-language/feature code-activity breakdown (no user_initiated_interaction_count) |
| day_totals[].totals_by_language_model[].language | string | adoption | Language for the model breakdown row |
| day_totals[].totals_by_language_model[].model | string | activity-flow | Model for the language breakdown row |
| day_totals[].totals_by_language_model[].(code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | activity-flow | Per-language/model code-activity breakdown (no user_initiated_interaction_count) |
| day_totals[].totals_by_model_feature[].model | string | activity-flow | Model for the model/feature breakdown row |
| day_totals[].totals_by_model_feature[].feature | string | adoption | Feature for the model/feature breakdown row |
| day_totals[].totals_by_model_feature[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-model/feature code-activity breakdown |
| day_totals[].loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (day total) |
| day_totals[].loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (day total) |
| day_totals[].loc_added_sum | number | activity-flow | Lines added (day total) |
| day_totals[].loc_deleted_sum | number | activity-flow | Lines deleted (day total) |
| day_totals[].pull_requests.* | number/string | quality | Full pull_requests sub-object (total_reviewed, total_created, total_created_by_copilot, total_reviewed_by_copilot, total_merged, total_suggestions, total_applied_suggestions, total_merged_created_by_copilot, total_copilot_suggestions, total_copilot_applied_suggestions, total_merged_reviewed_by_copilot, copilot_suggestions_by_comment_type[].comment_type/total_copilot_suggestions/total_applied_suggestions) - medians NOT included for org reports |
| day_totals[].daily_active_copilot_code_review_users | number | engagement | Daily active code-review users |
| day_totals[].weekly_active_copilot_code_review_users | number | engagement | Weekly active code-review users |
| day_totals[].monthly_active_copilot_code_review_users | number | engagement | Monthly active code-review users |
| day_totals[].daily_passive_copilot_code_review_users | number | engagement | Daily passive code-review users |
| day_totals[].weekly_passive_copilot_code_review_users | number | engagement | Weekly passive code-review users |
| day_totals[].monthly_passive_copilot_code_review_users | number | engagement | Monthly passive code-review users |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/orgs/octo-org/copilot/metrics/reports/organization-28-day/latest"
```

**Example response:**

```json
{
  "report_start_day": "2026-05-03",
  "report_end_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics
- https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, method, read:org scope (fine-grained 'View Organization Copilot Metrics'), and download_links/report_start_day/report_end_day all confirmed. Current replacement for retired endpoints. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics)

---

### org-metrics-users-1-day - Get Copilot per-user usage metrics for an organization (1-day)

**Purpose:** Download link(s) to user-level usage data and engagement metrics for one day.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/metrics/reports/users-1-day`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token; fine-grained PAT with 'View Organization Copilot Metrics' permission.
- Scopes: `read:org`
- Notes: Org owners.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |
| day | query | yes | Report day in YYYY-MM-DD format | 2026-05-30 |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits.

**Gotchas:** 204 if no data. Per-user granularity (PII: user_login). Telemetry must be enabled in IDE.

**Datapoints returned:**
- `user_id / user_login` (adoption) - Per-user identity (PII) for one report day (full schema in reportFields)
- `used_chat / used_agent / used_cli / used_copilot_cloud_agent` (engagement) - Per-user feature-usage booleans for the day
- `code_generation_activity_count / loc_added_sum` (activity-flow) - Per-user code generation and lines-added totals
- `ai_adoption_phase.phase` (engagement) - Per-user AI adoption phase classification

**Report file fields:** (org, 1-day, with adoption phase)

| path | type | category | description |
|------|------|----------|-------------|
| report_day | string | adoption | The calendar day the report covers (envelope) |
| day | string | adoption | Calendar day for the row |
| user_id | number | adoption | GitHub user id |
| user_login | string | adoption | GitHub user login (PII) |
| organization_id | string | adoption | Organization identifier |
| enterprise_id | string | adoption | Enterprise identifier |
| user_initiated_interaction_count | number | engagement | User-initiated interactions |
| code_generation_activity_count | number | activity-flow | Code generation activities |
| code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| totals_by_ide[].ide | string | adoption | IDE name for the breakdown row |
| totals_by_ide[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-IDE code-activity breakdown |
| totals_by_ide[].last_known_plugin_version.sampled_at | string | engagement | When the plugin version was sampled |
| totals_by_ide[].last_known_plugin_version.plugin | string | engagement | Last known Copilot plugin |
| totals_by_ide[].last_known_plugin_version.plugin_version | string | engagement | Last known plugin version |
| totals_by_ide[].last_known_ide_version.sampled_at | string | engagement | When the IDE version was sampled |
| totals_by_ide[].last_known_ide_version.ide_version | string | engagement | Last known IDE version |
| totals_by_feature[].feature | string | adoption | Copilot feature for the breakdown row |
| totals_by_feature[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-feature code-activity breakdown |
| totals_by_language_feature[].language | string | adoption | Language for the breakdown row |
| totals_by_language_feature[].feature | string | adoption | Feature for the language breakdown row |
| totals_by_language_feature[].(code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | activity-flow | Per-language/feature code-activity breakdown (no user_initiated_interaction_count) |
| totals_by_language_model[].language | string | adoption | Language for the model breakdown row |
| totals_by_language_model[].model | string | activity-flow | Model for the language breakdown row |
| totals_by_language_model[].(code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | activity-flow | Per-language/model code-activity breakdown (no user_initiated_interaction_count) |
| totals_by_model_feature[].model | string | activity-flow | Model for the model/feature breakdown row |
| totals_by_model_feature[].feature | string | adoption | Feature for the model/feature breakdown row |
| totals_by_model_feature[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-model/feature code-activity breakdown |
| used_agent | boolean | engagement | Whether the user used the agent |
| used_chat | boolean | engagement | Whether the user used chat |
| loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (user total) |
| loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (user total) |
| loc_added_sum | number | activity-flow | Lines added (user total) |
| loc_deleted_sum | number | activity-flow | Lines deleted (user total) |
| used_cli | boolean | engagement | Whether the user used the CLI |
| used_copilot_coding_agent | boolean | engagement | Whether the user used the coding agent |
| used_copilot_cloud_agent | boolean | engagement | Whether the user used the cloud agent |
| ai_adoption_phase.phase_number | number | engagement | AI adoption phase number |
| ai_adoption_phase.phase | string | engagement | AI adoption phase name |
| ai_adoption_phase.version | string | engagement | AI adoption phase model version |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/orgs/octo-org/copilot/metrics/reports/users-1-day?day=2026-05-30"
```

**Example response:**

```json
{
  "report_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics
- https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, read:org scope, fine-grained 'View Organization Copilot Metrics', required day param, and download_links/report_day all match the official docs. The signed file contains the rich per-user fields. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics?apiVersion=2022-11-28)

---

### org-metrics-users-28-day-latest - Get Copilot per-user usage metrics for an organization (28-day latest)

**Purpose:** Latest 28-day aggregated per-user adoption and engagement metrics download.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/metrics/reports/users-28-day/latest`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token; fine-grained PAT with 'View Organization Copilot Metrics' permission.
- Scopes: `read:org`
- Notes: Org owners.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits.

**Gotchas:** 28-day window. Use with user-teams report to build team-level views.

**Datapoints returned:**
- `user_id / user_login` (adoption) - Per-user identity (PII), aggregated over the 28-day window (full schema in reportFields)
- `used_chat / used_agent / used_cli / used_copilot_cloud_agent` (engagement) - Per-user feature-usage booleans for the window
- `code_generation_activity_count / loc_added_sum` (activity-flow) - Per-user code generation and lines-added totals

**Report file fields:** (org, 28-day, no adoption phase; 28-day adds report_start_day/report_end_day at row start; org 28-day still carries language_model + model_feature breakdowns)

| path | type | category | description |
|------|------|----------|-------------|
| report_start_day | string | adoption | First day of the 28-day window |
| report_end_day | string | adoption | Last day of the 28-day window |
| day | string | adoption | Calendar day for the row |
| user_id | number | adoption | GitHub user id |
| user_login | string | adoption | GitHub user login (PII) |
| organization_id | string | adoption | Organization identifier |
| enterprise_id | string | adoption | Enterprise identifier |
| user_initiated_interaction_count | number | engagement | User-initiated interactions |
| code_generation_activity_count | number | activity-flow | Code generation activities |
| code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| totals_by_ide[].ide | string | adoption | IDE name for the breakdown row |
| totals_by_ide[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-IDE code-activity breakdown |
| totals_by_ide[].last_known_plugin_version.sampled_at | string | engagement | When the plugin version was sampled |
| totals_by_ide[].last_known_plugin_version.plugin | string | engagement | Last known Copilot plugin |
| totals_by_ide[].last_known_plugin_version.plugin_version | string | engagement | Last known plugin version |
| totals_by_ide[].last_known_ide_version.sampled_at | string | engagement | When the IDE version was sampled |
| totals_by_ide[].last_known_ide_version.ide_version | string | engagement | Last known IDE version |
| totals_by_feature[].feature | string | adoption | Copilot feature for the breakdown row |
| totals_by_feature[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-feature code-activity breakdown |
| totals_by_language_feature[].language | string | adoption | Language for the breakdown row |
| totals_by_language_feature[].feature | string | adoption | Feature for the language breakdown row |
| totals_by_language_feature[].(code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | activity-flow | Per-language/feature code-activity breakdown (no user_initiated_interaction_count) |
| totals_by_language_model[].language | string | adoption | Language for the model breakdown row |
| totals_by_language_model[].model | string | activity-flow | Model for the language breakdown row |
| totals_by_language_model[].(code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | activity-flow | Per-language/model code-activity breakdown (no user_initiated_interaction_count) |
| totals_by_model_feature[].model | string | activity-flow | Model for the model/feature breakdown row |
| totals_by_model_feature[].feature | string | adoption | Feature for the model/feature breakdown row |
| totals_by_model_feature[].(user_initiated_interaction_count, code_generation_activity_count, code_acceptance_activity_count, loc_suggested_to_add_sum, loc_suggested_to_delete_sum, loc_added_sum, loc_deleted_sum) | number | engagement/activity-flow | Per-model/feature code-activity breakdown |
| used_agent | boolean | engagement | Whether the user used the agent |
| used_chat | boolean | engagement | Whether the user used chat |
| loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (user total) |
| loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (user total) |
| loc_added_sum | number | activity-flow | Lines added (user total) |
| loc_deleted_sum | number | activity-flow | Lines deleted (user total) |
| used_cli | boolean | engagement | Whether the user used the CLI |
| used_copilot_coding_agent | boolean | engagement | Whether the user used the coding agent |
| used_copilot_cloud_agent | boolean | engagement | Whether the user used the cloud agent |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/orgs/octo-org/copilot/metrics/reports/users-28-day/latest"
```

**Example response:**

```json
{
  "report_start_day": "2026-05-03",
  "report_end_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics
- https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: All core claims verified. Documented title: 'Get Copilot organization users usage metrics'. read:org scope; fine-grained PATs also supported. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics)

---

### org-metrics-user-teams-1-day - Get Copilot user-teams report for an organization (1-day)

**Purpose:** Download link(s) to user-to-team membership join data (one entry per user-team pair) for a day; used to construct team-level metrics by joining with the per-user report.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/metrics/reports/user-teams-1-day`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token; fine-grained PAT with 'View Organization Copilot Metrics' permission.
- Scopes: `read:org`
- Notes: Org owners.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |
| day | query | yes | Report day in YYYY-MM-DD format | 2026-05-30 |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits.

**Gotchas:** There is no single team-metrics endpoint in the current API: build team views by joining this report with users-*-day. Teams with fewer than 5 seated Copilot users on a given day are excluded.

**Datapoints returned:**
- `user_id / user_login` (adoption) - User identity for the user-team membership row (PII)
- `team_id / slug` (adoption) - Team the user belongs to (join key for team-level rollups)

**Report file fields:**

| path | type | category | description |
|------|------|----------|-------------|
| report_day | string | adoption | The calendar day the report covers (envelope) |
| user_id | number | adoption | GitHub user id |
| user_login | string | adoption | GitHub user login (PII) |
| day | string | adoption | Calendar day covered |
| organization_id | string | adoption | Organization identifier |
| team_id | number | adoption | Team identifier |
| slug | string | adoption | Team slug |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/orgs/octo-org/copilot/metrics/reports/user-teams-1-day?day=2026-05-30"
```

**Example response:**

```json
{
  "report_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics
- https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, read:org scope, required day param, and download_links/report_day confirmed. Doc directs joining this report with the per-user report; <5-seated-user team exclusion per concept docs. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics)

---

### enterprise-metrics-enterprise-1-day - Get Copilot usage metrics report for an enterprise (1-day)

**Purpose:** Download link(s) to enterprise-level Copilot usage metrics for a specified day.

**Request line:** `GET https://api.github.com/enterprises/{enterprise}/copilot/metrics/reports/enterprise-1-day`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:enterprise; fine-grained PAT with the 'View Enterprise Copilot Metrics' permission.
- Scopes: `manage_billing:copilot`, `read:enterprise`
- Notes: Enterprise owners or billing managers only. 'Copilot usage metrics' policy must be Enabled everywhere (or no policy) for the enterprise. Fine-grained PATs ARE supported via 'View Enterprise Copilot Metrics'.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| enterprise | path | yes | Enterprise slug | octo-ent |
| day | query | yes | Report day in YYYY-MM-DD format | 2026-05-30 |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits; signed URLs expire.

**Gotchas:** GitHub Enterprise Cloud only. Org- and enterprise-level PR reports may show different totals due to dedup/attribution timing differences.

**Datapoints returned:**
- `daily_active_users / weekly_active_users / monthly_active_users` (engagement) - Enterprise-wide active-user counts for the day (full schema in reportFields)
- `code_generation_activity_count / loc_added_sum` (activity-flow) - Enterprise-wide code generation and lines-added sums
- `pull_requests.total_created_by_copilot / total_reviewed_by_copilot` (quality) - Enterprise-wide Copilot pull-request authorship and review counts
- `totals_by_ai_adoption_phase[].total_engaged_users` (engagement) - Engaged-user counts bucketed by AI adoption phase

**Report file fields:** (enterprise 1-day: no organization_id, no medians, no CLI; includes totals_by_ai_adoption_phase[])

| path | type | category | description |
|------|------|----------|-------------|
| report_day | string | adoption | The calendar day the report covers (envelope) |
| day | string | adoption | Calendar day covered |
| enterprise_id | string | adoption | Enterprise identifier |
| daily_active_users | number | engagement | Daily active Copilot users |
| daily_active_copilot_cloud_agent_users | number | engagement | Daily active cloud agent users |
| weekly_active_users | number | engagement | Weekly active users |
| weekly_active_copilot_cloud_agent_users | number | engagement | Weekly active cloud agent users |
| monthly_active_users | number | engagement | Monthly active users |
| monthly_active_chat_users | number | engagement | Monthly active chat users |
| monthly_active_agent_users | number | engagement | Monthly active agent users |
| monthly_active_copilot_cloud_agent_users | number | engagement | Monthly active cloud agent users |
| user_initiated_interaction_count | number | engagement | User-initiated interactions |
| code_generation_activity_count | number | activity-flow | Code generation activities |
| code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| totals_by_ide[].ide + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-IDE breakdown (see org 1-day) |
| totals_by_feature[].feature + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-feature breakdown |
| totals_by_language_feature[].language/feature + 6 code-activity fields | string/number | adoption/activity-flow | Per-language/feature breakdown (no user_initiated_interaction_count) |
| totals_by_language_model[].language/model + 6 code-activity fields | string/number | adoption/activity-flow | Per-language/model breakdown (no user_initiated_interaction_count) |
| totals_by_model_feature[].model/feature + 7 code-activity fields | string/number | activity-flow/adoption/engagement | Per-model/feature breakdown |
| loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (day total) |
| loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (day total) |
| loc_added_sum | number | activity-flow | Lines added (day total) |
| loc_deleted_sum | number | activity-flow | Lines deleted (day total) |
| pull_requests.* (11 base fields + copilot_suggestions_by_comment_type[]) | number/string | quality | Full pull_requests sub-object; medians NOT included (1-day report) |
| daily_active_copilot_code_review_users | number | engagement | Daily active code-review users |
| weekly_active_copilot_code_review_users | number | engagement | Weekly active code-review users |
| monthly_active_copilot_code_review_users | number | engagement | Monthly active code-review users |
| daily_passive_copilot_code_review_users | number | engagement | Daily passive code-review users |
| weekly_passive_copilot_code_review_users | number | engagement | Weekly passive code-review users |
| monthly_passive_copilot_code_review_users | number | engagement | Monthly passive code-review users |
| totals_by_ai_adoption_phase[].phase | string | engagement | AI adoption phase name |
| totals_by_ai_adoption_phase[].phase_number | number | engagement | AI adoption phase number |
| totals_by_ai_adoption_phase[].total_engaged_users | number | engagement | Engaged users in this phase |
| totals_by_ai_adoption_phase[].avg_user_initiated_interactions | number | engagement | Avg user-initiated interactions in phase |
| totals_by_ai_adoption_phase[].avg_code_generation_activities | number | activity-flow | Avg code generation activities in phase |
| totals_by_ai_adoption_phase[].avg_code_acceptance_activities | number | activity-flow | Avg code acceptance activities in phase |
| totals_by_ai_adoption_phase[].avg_loc_added | number | activity-flow | Avg lines added in phase |
| totals_by_ai_adoption_phase[].avg_loc_deleted | number | activity-flow | Avg lines deleted in phase |
| totals_by_ai_adoption_phase[].avg_pull_requests_reviewed | number | quality | Avg PRs reviewed in phase |
| totals_by_ai_adoption_phase[].avg_pull_requests_created | number | quality | Avg PRs created in phase |
| totals_by_ai_adoption_phase[].avg_pull_requests_merged | number | quality | Avg PRs merged in phase |
| totals_by_ai_adoption_phase[].avg_pull_requests_median_minutes_to_merge | number | quality | Avg median minutes-to-merge in phase |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/enterprises/octo-ent/copilot/metrics/reports/enterprise-1-day?day=2026-05-30"
```

**Example response:**

```json
{
  "report_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics
- https://docs.github.com/en/enterprise-cloud@latest/rest/copilot/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Verified on both docs.github.com and enterprise-cloud@latest. Classic scopes manage_billing:copilot OR read:enterprise; fine-grained 'View Enterprise Copilot Metrics' IS supported (correcting an earlier claim). (source: https://docs.github.com/en/enterprise-cloud@latest/rest/copilot/copilot-usage-metrics)

---

### enterprise-metrics-enterprise-28-day-latest - Get Copilot usage metrics report for an enterprise (28-day latest)

**Purpose:** Latest 28-day aggregated enterprise usage metrics report download.

**Request line:** `GET https://api.github.com/enterprises/{enterprise}/copilot/metrics/reports/enterprise-28-day/latest`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:enterprise; fine-grained PAT with 'View Enterprise Copilot Metrics'.
- Scopes: `manage_billing:copilot`, `read:enterprise`
- Notes: Enterprise owners/billing managers; 'Copilot usage metrics' policy enabled.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| enterprise | path | yes | Enterprise slug | octo-ent |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits.

**Gotchas:** 28-day rolling window.

**Datapoints returned:**
- `day_totals[].daily_active_users / daily_active_cli_users` (engagement) - Per-day enterprise active-user counts (incl. CLI) across the 28-day window
- `day_totals[].code_generation_activity_count / loc_added_sum` (activity-flow) - Per-day enterprise code generation and lines-added sums
- `day_totals[].pull_requests.median_minutes_to_merge / total_created_by_copilot` (quality) - Per-day enterprise pull-request quality and Copilot authorship metrics
- `day_totals[].totals_by_cli.token_usage.prompt_tokens_sum` (cost) - Per-day CLI token consumption (usage-based cost driver)

**Report file fields:** (enterprise 28-day: includes medians, daily_active_cli_users, totals_by_cli.* + token_usage)

| path | type | category | description |
|------|------|----------|-------------|
| report_start_day | string | adoption | First day of the 28-day window (envelope) |
| report_end_day | string | adoption | Last day of the 28-day window (envelope) |
| enterprise_id | string | adoption | Enterprise identifier (report file) |
| created_at | string | adoption | When the aggregated report was created |
| day_totals[].day | string | adoption | Calendar day covered |
| day_totals[].enterprise_id | string | adoption | Enterprise identifier |
| day_totals[].daily_active_users | number | engagement | Daily active Copilot users |
| day_totals[].daily_active_cli_users | number | engagement | Daily active Copilot CLI users |
| day_totals[].daily_active_copilot_cloud_agent_users | number | engagement | Daily active cloud agent users |
| day_totals[].weekly_active_users | number | engagement | Weekly active users |
| day_totals[].weekly_active_copilot_cloud_agent_users | number | engagement | Weekly active cloud agent users |
| day_totals[].monthly_active_users | number | engagement | Monthly active users |
| day_totals[].monthly_active_chat_users | number | engagement | Monthly active chat users |
| day_totals[].monthly_active_agent_users | number | engagement | Monthly active agent users |
| day_totals[].monthly_active_copilot_cloud_agent_users | number | engagement | Monthly active cloud agent users |
| day_totals[].user_initiated_interaction_count | number | engagement | User-initiated interactions |
| day_totals[].code_generation_activity_count | number | activity-flow | Code generation activities |
| day_totals[].code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| day_totals[].totals_by_ide[].ide + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-IDE breakdown |
| day_totals[].totals_by_feature[].feature + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-feature breakdown |
| day_totals[].totals_by_language_feature[].language/feature + 6 code-activity fields | string/number | adoption/activity-flow | Per-language/feature breakdown (no user_initiated_interaction_count) |
| day_totals[].totals_by_language_model[].language/model + 6 code-activity fields | string/number | adoption/activity-flow | Per-language/model breakdown (no user_initiated_interaction_count) |
| day_totals[].totals_by_model_feature[].model/feature + 7 code-activity fields | string/number | activity-flow/adoption/engagement | Per-model/feature breakdown |
| day_totals[].loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (day total) |
| day_totals[].loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (day total) |
| day_totals[].loc_added_sum | number | activity-flow | Lines added (day total) |
| day_totals[].loc_deleted_sum | number | activity-flow | Lines deleted (day total) |
| day_totals[].pull_requests.* (11 base fields) | number | quality | total_reviewed, total_created, total_created_by_copilot, total_reviewed_by_copilot, total_merged, total_suggestions, total_applied_suggestions, total_merged_created_by_copilot, total_copilot_suggestions, total_copilot_applied_suggestions, total_merged_reviewed_by_copilot |
| day_totals[].pull_requests.median_minutes_to_merge | number | quality | Median minutes from open to merge (enterprise-only) |
| day_totals[].pull_requests.median_minutes_to_merge_copilot_authored | number | quality | Median minutes to merge for Copilot-authored PRs (enterprise-only) |
| day_totals[].pull_requests.copilot_suggestions_by_comment_type[].comment_type/total_copilot_suggestions/total_applied_suggestions | string/number | quality | Per-comment-type suggestion stats |
| day_totals[].totals_by_cli.session_count | number | engagement | Copilot CLI sessions |
| day_totals[].totals_by_cli.request_count | number | engagement | Copilot CLI requests |
| day_totals[].totals_by_cli.prompt_count | number | engagement | Copilot CLI prompts |
| day_totals[].totals_by_cli.token_usage.output_tokens_sum | number | cost | CLI output tokens consumed |
| day_totals[].totals_by_cli.token_usage.prompt_tokens_sum | number | cost | CLI prompt tokens consumed |
| day_totals[].totals_by_cli.token_usage.avg_tokens_per_request | number | cost | Average tokens per CLI request |
| day_totals[].daily_active_copilot_code_review_users | number | engagement | Daily active code-review users |
| day_totals[].weekly_active_copilot_code_review_users | number | engagement | Weekly active code-review users |
| day_totals[].monthly_active_copilot_code_review_users | number | engagement | Monthly active code-review users |
| day_totals[].daily_passive_copilot_code_review_users | number | engagement | Daily passive code-review users |
| day_totals[].weekly_passive_copilot_code_review_users | number | engagement | Weekly passive code-review users |
| day_totals[].monthly_passive_copilot_code_review_users | number | engagement | Monthly passive code-review users |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/enterprises/octo-ent/copilot/metrics/reports/enterprise-28-day/latest"
```

**Example response:**

```json
{
  "report_start_day": "2026-05-03",
  "report_end_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics
- https://docs.github.com/en/enterprise-cloud@latest/rest/copilot/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, scopes (manage_billing:copilot OR read:enterprise; fine-grained 'View Enterprise Copilot Metrics'), and download_links/report_start_day/report_end_day all confirmed. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics)

---

### enterprise-metrics-users-1-day - Get Copilot per-user usage metrics for an enterprise (1-day)

**Purpose:** Download link(s) to enterprise per-user usage and engagement metrics for one day. Available from October 10, 2025; up to 1 year of historical access.

**Request line:** `GET https://api.github.com/enterprises/{enterprise}/copilot/metrics/reports/users-1-day`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:enterprise; fine-grained PAT with 'View Enterprise Copilot Metrics'.
- Scopes: `manage_billing:copilot`, `read:enterprise`
- Notes: Enterprise owners/billing managers.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| enterprise | path | yes | Enterprise slug | octo-ent |
| day | query | yes | Report day in YYYY-MM-DD format | 2026-05-30 |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits.

**Gotchas:** Historical access ~1 year; data only from 2025-10-10 onward for this report.

**Datapoints returned:**
- `user_id / user_login` (adoption) - Per-user identity (PII) for one report day (full schema in reportFields)
- `used_chat / used_agent / used_cli / used_copilot_cloud_agent` (engagement) - Per-user feature-usage booleans for the day
- `code_generation_activity_count / loc_added_sum` (activity-flow) - Per-user code generation and lines-added totals
- `ai_adoption_phase.phase` (engagement) - Per-user AI adoption phase classification

**Report file fields:** (enterprise, 1-day, with adoption phase; enterprise per-user rows omit organization_id; 1-day carries language_model + model_feature breakdowns)

| path | type | category | description |
|------|------|----------|-------------|
| report_day | string | adoption | The calendar day the report covers (envelope) |
| day | string | adoption | Calendar day for the row |
| user_id | number | adoption | GitHub user id |
| user_login | string | adoption | GitHub user login (PII) |
| enterprise_id | string | adoption | Enterprise identifier |
| user_initiated_interaction_count | number | engagement | User-initiated interactions |
| code_generation_activity_count | number | activity-flow | Code generation activities |
| code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| totals_by_ide[].ide + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-IDE breakdown |
| totals_by_ide[].last_known_plugin_version.(sampled_at/plugin/plugin_version) | string | engagement | Last known plugin metadata |
| totals_by_ide[].last_known_ide_version.(sampled_at/ide_version) | string | engagement | Last known IDE metadata |
| totals_by_feature[].feature + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-feature breakdown |
| totals_by_language_feature[].language/feature + 6 code-activity fields | string/number | adoption/activity-flow | Per-language/feature breakdown (no user_initiated_interaction_count) |
| totals_by_language_model[].language/model + 6 code-activity fields | string/number | adoption/activity-flow | Per-language/model breakdown (no user_initiated_interaction_count) |
| totals_by_model_feature[].model/feature + 7 code-activity fields | string/number | activity-flow/adoption/engagement | Per-model/feature breakdown |
| used_agent | boolean | engagement | Whether the user used the agent |
| used_chat | boolean | engagement | Whether the user used chat |
| loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (user total) |
| loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (user total) |
| loc_added_sum | number | activity-flow | Lines added (user total) |
| loc_deleted_sum | number | activity-flow | Lines deleted (user total) |
| used_cli | boolean | engagement | Whether the user used the CLI |
| used_copilot_coding_agent | boolean | engagement | Whether the user used the coding agent |
| used_copilot_cloud_agent | boolean | engagement | Whether the user used the cloud agent |
| ai_adoption_phase.phase_number | number | engagement | AI adoption phase number |
| ai_adoption_phase.phase | string | engagement | AI adoption phase name |
| ai_adoption_phase.version | string | engagement | AI adoption phase model version |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/enterprises/octo-ent/copilot/metrics/reports/users-1-day?day=2026-05-30"
```

**Example response:**

```json
{
  "report_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Documented title: 'Get Copilot users usage metrics for a specific day'. Path, GET, scopes, required day param, and download_links/report_day all confirmed; reports start 2025-10-10 with up to 1 year history. (source: https://docs.github.com/en/enterprise-cloud@latest/rest/copilot/copilot-usage-metrics?apiVersion=2026-03-10)

---

### enterprise-metrics-users-28-day-latest - Get Copilot per-user usage metrics for an enterprise (28-day latest)

**Purpose:** Latest 28-day enterprise per-user adoption/engagement metrics download.

**Request line:** `GET https://api.github.com/enterprises/{enterprise}/copilot/metrics/reports/users-28-day/latest`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:enterprise; fine-grained PAT with 'View Enterprise Copilot Metrics'.
- Scopes: `manage_billing:copilot`, `read:enterprise`
- Notes: Enterprise owners/billing managers.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| enterprise | path | yes | Enterprise slug | octo-ent |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits.

**Gotchas:** 28-day window.

**Datapoints returned:**
- `user_id / user_login` (adoption) - Per-user identity (PII), aggregated over the 28-day window (full schema in reportFields)
- `used_chat / used_agent / used_cli / used_copilot_cloud_agent` (engagement) - Per-user feature-usage booleans for the window
- `code_generation_activity_count / loc_added_sum` (activity-flow) - Per-user code generation and lines-added totals

**Report file fields:** (enterprise, 28-day, no adoption phase; for enterprise 28-day the language_model + model_feature breakdowns are EMPTY/omitted per the catalog comment)

| path | type | category | description |
|------|------|----------|-------------|
| report_start_day | string | adoption | First day of the 28-day window |
| report_end_day | string | adoption | Last day of the 28-day window |
| day | string | adoption | Calendar day for the row |
| user_id | number | adoption | GitHub user id |
| user_login | string | adoption | GitHub user login (PII) |
| enterprise_id | string | adoption | Enterprise identifier |
| user_initiated_interaction_count | number | engagement | User-initiated interactions |
| code_generation_activity_count | number | activity-flow | Code generation activities |
| code_acceptance_activity_count | number | activity-flow | Code acceptance activities |
| totals_by_ide[].ide + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-IDE breakdown |
| totals_by_ide[].last_known_plugin_version.(sampled_at/plugin/plugin_version) | string | engagement | Last known plugin metadata |
| totals_by_ide[].last_known_ide_version.(sampled_at/ide_version) | string | engagement | Last known IDE metadata |
| totals_by_feature[].feature + 7 code-activity fields | string/number | adoption/engagement/activity-flow | Per-feature breakdown |
| totals_by_language_feature[].language/feature + 6 code-activity fields | string/number | adoption/activity-flow | Per-language/feature breakdown (no user_initiated_interaction_count) |
| used_agent | boolean | engagement | Whether the user used the agent |
| used_chat | boolean | engagement | Whether the user used chat |
| loc_suggested_to_add_sum | number | activity-flow | Lines suggested to add (user total) |
| loc_suggested_to_delete_sum | number | activity-flow | Lines suggested to delete (user total) |
| loc_added_sum | number | activity-flow | Lines added (user total) |
| loc_deleted_sum | number | activity-flow | Lines deleted (user total) |
| used_cli | boolean | engagement | Whether the user used the CLI |
| used_copilot_coding_agent | boolean | engagement | Whether the user used the coding agent |
| used_copilot_cloud_agent | boolean | engagement | Whether the user used the cloud agent |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/enterprises/octo-ent/copilot/metrics/reports/users-28-day/latest"
```

**Example response:**

```json
{
  "report_start_day": "2026-05-03",
  "report_end_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, scopes (manage_billing:copilot OR read:enterprise; fine-grained 'View Enterprise Copilot Metrics'), and all three datapoints confirmed in the documented response schema. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics)

---

### enterprise-metrics-user-teams-1-day - Get Copilot user-teams report for an enterprise (1-day)

**Purpose:** Download link(s) to enterprise user-to-team membership join data (includes both enterprise teams and business/org teams) for the specified day.

**Request line:** `GET https://api.github.com/enterprises/{enterprise}/copilot/metrics/reports/user-teams-1-day`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:enterprise; fine-grained PAT with 'View Enterprise Copilot Metrics'.
- Scopes: `manage_billing:copilot`, `read:enterprise`
- Notes: Enterprise owners/billing managers.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| enterprise | path | yes | Enterprise slug | octo-ent |
| day | query | yes | Report day in YYYY-MM-DD format | 2026-05-30 |

**Response shape:** download-links

**Rate limits:** Standard REST rate limits.

**Gotchas:** Join with users-*-day to derive team metrics; teams with <5 seated users/day excluded.

**Datapoints returned:**
- `user_id / user_login` (adoption) - User identity for the user-team membership row (PII)
- `team_id / slug` (adoption) - Team the user belongs to (join key for team-level rollups)

**Report file fields:**

| path | type | category | description |
|------|------|----------|-------------|
| report_day | string | adoption | The calendar day the report covers (envelope) |
| user_id | number | adoption | GitHub user id |
| user_login | string | adoption | GitHub user login (PII) |
| day | string | adoption | Calendar day covered |
| organization_id | string | adoption | Organization identifier |
| team_id | number | adoption | Team identifier |
| slug | string | adoption | Team slug |

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/enterprises/octo-ent/copilot/metrics/reports/user-teams-1-day?day=2026-05-30"
```

**Example response:**

```json
{
  "report_day": "2026-05-30",
  "download_links": ["https://objects.githubusercontent.com/...signed..."]
}
```

**Plans/tiers:** Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage); followed download link: yes. Note: 200; report body had no parseable rows for the tested day (empty teams data).

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage-metrics

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Documented title: 'Get Copilot enterprise user-teams report for a specific day'. Path, GET, scopes, required day param, and download_links/report_day confirmed. (source: https://docs.github.com/en/rest/copilot/copilot-usage-metrics)

---

### org-billing - Get Copilot billing information for an organization (seat breakdown)

**Purpose:** Returns Copilot seat-breakdown counts and policy settings for the org. Core Adoption/Seats + Cost/Billing endpoint.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/billing`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:org. Fine-grained PATs are also supported. Org owners only.
- Scopes: `manage_billing:copilot`, `read:org`
- Notes: Org owners only. The seat-breakdown billing endpoint is generally available; seat add/remove (user-management) endpoints are in public preview and subject to change.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name (case-insensitive) | octo-org |

**Response shape:** inline-json

**Rate limits:** Standard REST rate limits.

**Gotchas:** Activity counts require IDE telemetry enabled. Documented title is 'Get Copilot seat information and settings for an organization'.

**Datapoints returned:**
- `seat_breakdown.total` (cost) - Total seats assigned/billed
- `seat_breakdown.added_this_cycle` (cost) - Seats added in the current billing cycle
- `seat_breakdown.pending_cancellation` (cost) - Seats set to cancel at end of cycle
- `seat_breakdown.pending_invitation` (adoption) - Seats with invitations not yet accepted
- `seat_breakdown.active_this_cycle` (engagement) - Seats with activity this cycle
- `seat_breakdown.inactive_this_cycle` (engagement) - Seats with no activity this cycle
- `public_code_suggestions` (quality) - Policy enum: allow|block|unconfigured (matching-public-code filter)
- `ide_chat` (engagement) - Policy enum: enabled|disabled|unconfigured
- `platform_chat` (engagement) - Policy enum: enabled|disabled|unconfigured
- `cli` (engagement) - Policy enum: enabled|disabled|unconfigured
- `seat_management_setting` (adoption) - Enum: assign_all|assign_selected|disabled|unconfigured
- `plan_type` (cost) - Enum: business|enterprise

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" https://api.github.com/orgs/octo-org/copilot/billing
```

**Example response:**

```json
{
  "seat_breakdown": {
    "total": 12,
    "added_this_cycle": 9,
    "pending_cancellation": 0,
    "pending_invitation": 0,
    "active_this_cycle": 12,
    "inactive_this_cycle": 11
  },
  "seat_management_setting": "assign_selected",
  "public_code_suggestions": "block",
  "ide_chat": "enabled",
  "platform_chat": "enabled",
  "cli": "enabled",
  "plan_type": "business"
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-user-management

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, scopes (manage_billing:copilot OR read:org; org owners only), and all 12 datapoints confirmed against the documented response schema. Fine-grained PATs also supported. (source: https://docs.github.com/en/rest/copilot/copilot-user-management)

---

### org-billing-seats - List all Copilot seat assignments for an organization

**Purpose:** Lists every assigned Copilot seat with per-user last-activity data. Key per-seat engagement/adoption endpoint.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/billing/seats`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:org. Org owners only.
- Scopes: `manage_billing:copilot`, `read:org`
- Notes: Org owners only. Endpoint is in public preview.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |
| page | query | no | Page number; default 1 | 1 |
| per_page | query | no | Results per page; default 50, max 100 | 100 |

**Response shape:** inline-json

**Rate limits:** Standard REST rate limits; paginate via page/per_page.

**Gotchas:** last_activity_* requires IDE telemetry. updated_at is deprecated. Public preview.

**Datapoints returned:**
- `total_seats` (adoption) - Total number of seat assignments
- `seats[].assignee` (adoption) - User object the seat is assigned to (or null)
- `seats[].assigning_team` (adoption) - Team (or enterprise team) that granted the seat (or null)
- `seats[].pending_cancellation_date` (cost) - Date seat is scheduled to be cancelled (or null)
- `seats[].last_activity_at` (engagement) - Timestamp of the user's last Copilot activity
- `seats[].last_activity_editor` (engagement) - Editor/IDE used at last activity
- `seats[].last_authenticated_at` (engagement) - Last time the user authenticated to Copilot
- `seats[].created_at` (adoption) - When the seat was created
- `seats[].updated_at` (adoption) - Last seat update (field marked deprecated)
- `seats[].plan_type` (cost) - Enum: business|enterprise|unknown

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/orgs/octo-org/copilot/billing/seats?per_page=100&page=1"
```

**Example response:**

```json
{
  "total_seats": 2,
  "seats": [
    {
      "assignee": { "login": "octocat", "id": 1 },
      "assigning_team": { "slug": "engineering" },
      "last_activity_at": "2026-05-30T10:11:22-06:00",
      "last_activity_editor": "vscode/1.99.0/copilot/1.250.0",
      "last_authenticated_at": "2026-05-30T09:00:00-06:00",
      "created_at": "2024-12-01T19:00:00-06:00",
      "pending_cancellation_date": null,
      "plan_type": "business"
    }
  ]
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-user-management

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, scopes (manage_billing:copilot OR read:org; org owners only), pagination (default 50, max 100), and all 10 datapoints confirmed. assigning_team may be a Team OR Enterprise Team object. Public preview. (source: https://docs.github.com/en/rest/copilot/copilot-user-management)

---

### org-member-copilot-seat - Get Copilot seat assignment details for a user

**Purpose:** Returns the Copilot seat detail (incl. last activity) for one organization member.

**Request line:** `GET https://api.github.com/orgs/{org}/members/{username}/copilot`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Classic PAT or OAuth app token with manage_billing:copilot OR read:org. Fine-grained PATs also supported.
- Scopes: `manage_billing:copilot`, `read:org`
- Notes: Org owners only. Public preview.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |
| username | path | yes | GitHub user handle | octocat |

**Response shape:** inline-json

**Rate limits:** Standard REST rate limits.

**Gotchas:** Requires telemetry for activity fields. Public preview.

**Datapoints returned:**
- `assignee` (adoption) - The user the seat belongs to
- `last_activity_at` (engagement) - Last Copilot activity timestamp
- `last_activity_editor` (engagement) - Editor at last activity
- `pending_cancellation_date` (cost) - Scheduled cancellation date or null
- `plan_type` (cost) - business|enterprise|unknown

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" https://api.github.com/orgs/octo-org/members/octocat/copilot
```

**Example response:**

```json
{
  "assignee": { "login": "octocat", "id": 1 },
  "last_activity_at": "2026-05-30T10:11:22-06:00",
  "last_activity_editor": "vscode/1.99.0",
  "pending_cancellation_date": null,
  "plan_type": "business"
}
```

**Plans/tiers:** Business, Enterprise

**Live check:** status 200 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-user-management

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, Bearer auth (manage_billing:copilot OR read:org; org owners; public preview), and all five datapoints confirmed. Response also includes organization/assigning_team/created_at and a deprecated updated_at not listed here. (source: https://docs.github.com/en/rest/copilot/copilot-user-management)

---

### org-content-exclusion - Get Copilot content exclusion rules (org)

**Purpose:** Read the org's Copilot content-exclusion rules - a governance/security control over what Copilot may read.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/content_exclusion`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Token with the copilot OR read:org scope.
- Scopes: `copilot`, `read:org`
- Notes: Org admin context. Public preview.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |

**Response shape:** inline-json

**Gotchas:** Min plan: Copilot Business/Enterprise (org Copilot APIs). Public preview - subject to change. The PUT (set rules) variant is mutating and not catalogued.

**Datapoints returned:**
- `content_exclusion_rules` (security) - Per-repo/path glob patterns Copilot must not read - content-governance posture (rule count + scope).

**Plans/tiers:** Business, Enterprise

**Live check:** none (doc-grounded; not live-tested)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-content-exclusion-management

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: GET path/auth/response confirmed from official docs (public preview); not live-tested - doc-grounded. (source: https://docs.github.com/en/rest/copilot/copilot-content-exclusion-management)

---

### org-coding-agent-permissions - Get Copilot coding-agent permissions (org)

**Purpose:** Read whether the Copilot coding agent is enabled for the org and across which repositories (adoption/governance of autonomous coding).

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/coding-agent/permissions`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Token with the admin:org scope.
- Scopes: `admin:org`
- Notes: Org admin. Public preview.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |

**Response shape:** inline-json

**Gotchas:** Min plan: Copilot Business/Enterprise. Public preview. PUT (set permissions) variant is mutating and not catalogued.

**Datapoints returned:**
- `enabled_repositories` (adoption) - Coding-agent enablement scope: all | selected | none.

**Plans/tiers:** Business, Enterprise

**Live check:** none (doc-grounded; not live-tested)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-coding-agent-management

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: GET path/auth/response confirmed from official docs (public preview); not live-tested - doc-grounded. (source: https://docs.github.com/en/rest/copilot/copilot-coding-agent-management)

---

### org-coding-agent-repositories - List repositories with Copilot coding-agent enabled (org)

**Purpose:** Enumerate the repositories where the Copilot coding agent is enabled - adoption breadth of autonomous coding.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/coding-agent/permissions/repositories`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT, fine-grained PAT, or OAuth app token
- Credential: Token with the admin:org scope.
- Scopes: `admin:org`
- Notes: Org admin. Public preview. Paginated (per_page/page).

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |

**Response shape:** inline-json

**Gotchas:** Min plan: Copilot Business/Enterprise. Public preview. Paginated.

**Datapoints returned:**
- `total_count` (adoption) - Number of repositories with the coding agent enabled.
- `repositories` (adoption) - Per-repo objects the coding agent is enabled on.

**Plans/tiers:** Business, Enterprise

**Live check:** none (doc-grounded; not live-tested)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-coding-agent-management

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: GET path/auth/response confirmed from official docs (public preview); not live-tested - doc-grounded. (source: https://docs.github.com/en/rest/copilot/copilot-coding-agent-management)

---

### enterprise-custom-agents - List Copilot custom agents (enterprise)

**Purpose:** List the custom agents defined for the enterprise (from /agents/*.md) - adoption of standardized Copilot agents.

**Request line:** `GET https://api.github.com/enterprises/{enterprise}/copilot/custom-agents`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT or OAuth app token
- Credential: Token with the admin:enterprise scope (enterprise owner with AI Controls access).
- Scopes: `admin:enterprise`
- Notes: Enterprise owners only.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| enterprise | path | yes | Enterprise slug | octo-enterprise |

**Response shape:** inline-json

**Gotchas:** Min plan: GitHub Enterprise (enterprise-scoped Copilot endpoint). admin:enterprise required.

**Datapoints returned:**
- `custom_agents` (adoption) - Defined custom agents (name, file_path, url) - count and inventory of standardized agents.

**Plans/tiers:** Enterprise

**Live check:** none (doc-grounded; not live-tested)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-custom-agents

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: GET path/auth/response schema (custom_agents[].name/file_path/url) confirmed from official docs; not live-tested - doc-grounded. (source: https://docs.github.com/en/rest/copilot/copilot-custom-agents)

---

### enterprise-custom-agents-source - Get Copilot custom-agents source (enterprise)

**Purpose:** Read which org/repo is the source of the enterprise's custom-agent definitions (governance of agent provenance).

**Request line:** `GET https://api.github.com/enterprises/{enterprise}/copilot/custom-agents/source`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT or OAuth app token
- Credential: Token with the admin:enterprise scope.
- Scopes: `admin:enterprise`
- Notes: Enterprise owners only.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| enterprise | path | yes | Enterprise slug | octo-enterprise |

**Response shape:** inline-json

**Gotchas:** Min plan: GitHub Enterprise. admin:enterprise required. PUT/DELETE (set/remove source) variants are mutating and not catalogued.

**Datapoints returned:**
- `custom_agents_source` (adoption) - Configured source organization + repository for custom-agent definitions.

**Plans/tiers:** Enterprise

**Live check:** none (doc-grounded; not live-tested)

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-custom-agents

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: GET path/auth/response confirmed from official docs; not live-tested - doc-grounded. (source: https://docs.github.com/en/rest/copilot/copilot-custom-agents)

---

### retired-org-metrics - [RETIRED] Copilot Metrics API - organization

> DEPRECATED - retired on 2026-04-02.

**Purpose:** Former engaged-users metrics API returning daily aggregated objects with IDE completions, chat, and PR breakdowns. CLOSED DOWN on April 2, 2026 - replaced by /copilot/metrics/reports/* usage metrics endpoints.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/metrics`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT or OAuth app token
- Credential: Classic PAT or OAuth app token. Required 'Copilot Metrics API access' policy enabled.
- Scopes: `manage_billing:copilot`, `read:org`, `read:enterprise`
- Notes: RETIRED 2026-04-02. Scopes were alternatives (any one of the three).

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2026-03-10 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |
| since | query | no | ISO 8601 start, max 100 days ago | - |
| until | query | no | ISO 8601 end | - |
| page | query | no | Default 1 | - |
| per_page | query | no | Default 100, max 100 | - |

**Response shape:** inline-json

**Rate limits:** Standard REST rate limits (historical).

**Gotchas:** RETIRED 2026-04-02. Also had team variant /orgs/{org}/team/{team_slug}/copilot/metrics and enterprise /enterprises/{enterprise}/copilot/metrics. Required 28-day-aware processing, minimum 5 members/day, IDE telemetry, and 'Copilot Metrics API access' policy enabled (422 if disabled).

**Datapoints returned:**
- `date` (engagement) - Day (YYYY-MM-DD)
- `total_active_users` (engagement) - Users with any Copilot activity that day
- `total_engaged_users` (engagement) - Users who actively engaged with a feature
- `copilot_ide_code_completions` (activity-flow) - Completions engagement with languages[] and editors[].models[] breakdown
- `copilot_ide_chat` (engagement) - IDE chat: editors[].models[] with total_chats, total_chat_insertion_events, total_chat_copy_events
- `copilot_dotcom_chat` (engagement) - github.com chat: models[] with total_chats
- `copilot_dotcom_pull_requests` (activity-flow) - PR summaries: repositories[].models[].total_pr_summaries_created

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2026-03-10" "https://api.github.com/orgs/octo-org/copilot/metrics?since=2026-01-01"  # NOTE: now returns retired/closed behavior
```

**Example response:**

```json
[
  {
    "date": "2026-01-01",
    "total_active_users": 24,
    "total_engaged_users": 20,
    "copilot_ide_code_completions": { "total_engaged_users": 20, "languages": [{"name":"python","total_engaged_users":10}], "editors": [{"name":"vscode","total_engaged_users":18,"models":[{"name":"default","is_custom_model":false,"total_engaged_users":18}]}] }
  }
]
```

**Plans/tiers:** (none - retired)

**Live check:** status 404 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage). Note: Confirmed retired (404) - endpoint no longer exists.

**Deprecated:** yes. **Retired on:** 2026-04-02

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-metrics
- https://docs.github.com/en/rest/copilot/copilot-usage

**Verification:** path/method/auth/datapoints all verified; confidence high. Note: Path, GET, scopes, query params, and all seven datapoints verified. Retirement (closed down April 2, 2026) confirmed by the docs warning and the GitHub Changelog. Replaced by /copilot/metrics/reports/* endpoints. (source: https://docs.github.com/en/rest/copilot/copilot-metrics)

---

### retired-org-usage - [RETIRED] Copilot Usage API - organization (legacy)

> DEPRECATED - retired on 2026-04-02.

**Purpose:** Original (oldest) Copilot usage summary API returning daily suggestion/acceptance/line counts and chat counts with language+editor breakdown. Deprecated in favor of the Metrics API, and the whole metrics/usage family was closed down April 2, 2026.

**Request line:** `GET https://api.github.com/orgs/{org}/copilot/usage`

**Auth:**
- Scheme: `bearer`
- Type: Classic PAT or OAuth app token
- Credential: Classic PAT or OAuth app token.
- Scopes: `manage_billing:copilot`, `read:org`, `read:enterprise`
- Notes: DEPRECATED; superseded by Copilot Metrics API then retired 2026-04-02.

**Headers:**

| Name | Value | Required |
|------|-------|----------|
| Authorization | Bearer \<TOKEN\> | yes |
| Accept | application/vnd.github+json | yes |
| X-GitHub-Api-Version | 2022-11-28 | yes |

**Parameters:**

| name | in | required | description | example |
|------|----|----------|-------------|---------|
| org | path | yes | Organization name | octo-org |
| since | query | no | Start date | - |
| until | query | no | End date | - |
| page | query | no | Page number | - |
| per_page | query | no | Per page (max 100) | - |

**Response shape:** inline-json

**Rate limits:** Standard REST rate limits (historical).

**Gotchas:** DEPRECATED and RETIRED 2026-04-02. Had org/team/enterprise/enterprise-team variants (e.g. /orgs/{org}/team/{team_slug}/copilot/usage, /enterprises/{enterprise}/copilot/usage). Replaced by Copilot Metrics API, then by the report-download usage metrics endpoints. Exact legacy field names could not be re-fetched from a live official page - see unverified.

**Datapoints returned:**
- `day` (engagement) - Date of the usage summary
- `total_suggestions_count` (activity-flow) - Total code completion suggestions shown
- `total_acceptances_count` (activity-flow) - Total suggestions accepted
- `total_lines_suggested` (activity-flow) - Total lines of code suggested
- `total_lines_accepted` (activity-flow) - Total lines of code accepted
- `total_active_users` (engagement) - Active Copilot users that day
- `total_chat_acceptances` (engagement) - Chat suggestions accepted
- `total_chat_turns` (engagement) - Total chat turns/messages
- `total_active_chat_users` (engagement) - Users active in chat
- `breakdown[]` (activity-flow) - Per language+editor: language, editor, suggestions_count, acceptances_count, lines_suggested, lines_accepted, active_users

**Example request:**

```bash
curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28" "https://api.github.com/orgs/octo-org/copilot/usage"  # retired
```

**Example response:**

```json
[
  {
    "day": "2023-10-15",
    "total_suggestions_count": 1000,
    "total_acceptances_count": 800,
    "total_lines_suggested": 1800,
    "total_lines_accepted": 1200,
    "total_active_users": 10,
    "total_chat_acceptances": 32,
    "total_chat_turns": 200,
    "total_active_chat_users": 4,
    "breakdown": [{"language":"python","editor":"vscode","suggestions_count":300,"acceptances_count":250,"lines_suggested":900,"lines_accepted":700,"active_users":5}]
  }
]
```

**Plans/tiers:** (none - retired)

**Live check:** status 404 on 2026-06-04 (account: enterprise: cybage / org: ALMCybage). Note: Confirmed retired (404) - endpoint no longer exists.

**Deprecated:** yes. **Retired on:** 2026-04-02

**Source URLs:**
- https://docs.github.com/en/rest/copilot/copilot-usage
- https://docs.github.com/en/enterprise-cloud@latest/rest/copilot/copilot-usage

**Verification:** pathVerified=false, methodVerified=false, authVerified=true, datapointsVerified=false; confidence medium. Note: Historically real but NOT independently verifiable against live official docs: the /copilot/usage page now redirects to /copilot/metrics. Path, method, and the flat legacy datapoint schema are UNVERIFIED; auth and the 2026-04-02 retirement are VERIFIED. (source: https://docs.github.com/en/rest/copilot/copilot-usage (redirects to https://docs.github.com/en/rest/copilot/copilot-metrics))

---

## Tool-level Unverified Claims

1. The plans/pricing page summary (via WebFetch) listed Copilot Free, Student, Pro ($10/mo), Pro+ ($39/mo), Max ($100/mo), Business ($19/seat/mo), Enterprise ($39/seat/mo). The exact current prices should be re-checked against the live plans page; the plans page itself did not enumerate which specific Metrics/Admin APIs unlock per tier beyond stating Business/Enterprise provide centralized management and policy control. The per-tier API mapping in 'plans' is inferred from the API docs' org/enterprise scoping, not stated verbatim on the plans page.
2. The legacy Copilot Usage API field names (total_suggestions_count, total_acceptances_count, total_lines_suggested, total_lines_accepted, total_active_users, total_chat_acceptances, total_chat_turns, total_active_chat_users, breakdown[].language/editor/...) were confirmed via a docs.github.com search snippet and prior knowledge, but the original apiVersion=2022-11-28 schema page could not be re-fetched directly (the current copilot-usage page now redirects/reflects the retired-metrics content). Treat the exact legacy field list as high-confidence-but-not-freshly-fetched.
3. Whether the retired /copilot/metrics (engaged-users) API and the older /copilot/usage API are documented as TWO distinct deprecated APIs vs one: current docs collapse messaging to 'Copilot metrics endpoints were closed down on April 2, 2026; use Copilot usage metrics endpoints.' The precise historical relationship (usage -> metrics -> usage-metrics-reports) is reconstructed and not all stated on a single fetched page.
4. Exact rate-limit numbers for the usage-metrics report endpoints are not published in the fetched docs; 'standard REST API rate limits' is an inference. Signed download-link expiration duration ('limited expiration') is stated but no exact TTL is given.
5. The minimum '5 members/5 seated users' threshold is confirmed for team-level construction (user-teams + per-user join) and was stated for the retired metrics API; whether it still applies identically to the org-1-day report itself was not explicitly restated on the current concept page fetched (which instead emphasized telemetry + ~2 UTC-day latency).
6. The enterprise users-1-day report 'available from October 10, 2025 with up to 1 year historical access' came from the usage-metrics endpoints page summary and was not independently cross-confirmed on a second page.
</content>
</invoke>
