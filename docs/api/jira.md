# Jira (Cloud) - API Endpoint Reference

**Tool:** Jira (id: `jira`) | **Vendor:** Atlassian | **Stage:** Plan & Track (`plan`)

Atlassian's Plan & Track system of record as a delivery-telemetry source: project/user/seat provisioning, JQL issue flow (created/resolved/WIP, cycle & lead time), agile boards/sprints/velocity, workflow & status metadata for quality classification, permission/audit governance, and org-level seats & cost - across the platform REST API (`/rest/api/3`), the Jira Software agile API (`/rest/agile/1.0`), and the Organizations admin API.

**Docs:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/

**Ingestion pattern:** Direct inline JSON for almost all reads. Issue-flow counts come from JQL: `POST /search/jql` (token pagination via `nextPageToken`, NO total - detect last page by absent token) and `POST /search/approximate-count` for counts. Site reads use Basic (`email:token`); org-wide seats/audit use the Organizations admin API (different host + org API key). Rate limiting is a points budget (429 with no gradual throttle) so paginated sweeps must be paced.

## Plans / Tiers

| Name | Price | Tier | Unlocks APIs | Metrics Access |
|------|-------|------|--------------|----------------|
| Jira Cloud Free | $0 (up to 10 users) | individual | yes | Full platform REST read surface (`/rest/api/3`): users/projects/groups, JQL issue flow (search/jql + approximate-count), changelog & worklog cycle time, workflow/status/priority/resolution metadata, permissions & permission schemes. Agile (`/rest/agile/1.0`) works wherever Jira Software boards/sprints are provisioned. CAVEAT: the in-product audit log (`/auditing/record`) returns no data when ALL apps are Free - treat it as Standard+. |
| Jira Cloud Standard | Per-user (Atlassian pricing) | team | yes | Everything in Free plus a working site audit log (`/auditing/record`, ~180-day retention) and the full Jira Software agile surface (boards, sprints, velocity, backlog, epics). Higher rate-limit point budget (~100,000 + 10/user per hour). |
| Jira Cloud Premium | Per-user (Atlassian pricing) | business | yes | Same REST/agile read surface as Standard with a larger rate-limit budget (~130,000 + 20/user per hour). Atlassian Guard Standard (subscribed separately) unlocks full org audit-log coverage (e.g. user_login) via the Organizations admin API. |
| Jira Cloud Enterprise | Per-user, annual (Atlassian pricing) | enterprise | yes | Same REST/agile read surface; largest rate-limit budget (~150,000 + 30/user per hour, cap ~500,000). Cloud Enterprise (or Atlassian Guard) gives full org audit-log coverage via the Organizations admin API across all sites in the org. |
| Organizations admin API (org admin key) | Included with any paid subscription (org admin role required) | enterprise | yes | NOT a Jira product tier - a separate access path. An Organization API key (Bearer) from admin.atlassian.com on the host `https://api.atlassian.com/admin` unlocks org-wide seats/product-access/last-active, directory user counts/stats, domains, workspaces (provisioned products), and the org audit-events API. v1 users/last-active endpoints (the only source of `product_access`/`access_billable`) are DEPRECATED and stop working after 30 Jun 2026; full org audit coverage requires Atlassian Guard or Cloud Enterprise. |

Plan source URLs:
- Free: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- Standard/Premium/Enterprise: https://developer.atlassian.com/cloud/jira/platform/rate-limiting/
- Org-admin API: https://developer.atlassian.com/cloud/admin/organization/rest/intro/

## Feasibility Verdict

**Status:** feasible-with-caveats

DORMANT / DOC-GROUNDED (2026-06-04). 93 endpoints and 192 datapoints were verified against official Atlassian docs only - NO live call has been made (no API token / org API key in hand), so this tool is intentionally NOT registered in index.ts. The core flow surface (issue search via JQL, changelog/worklog cycle time, workflow/status metadata, permissions) is Free-tier and reachable with a simple Basic email+token call; agile boards/sprints/velocity need Jira Software (effectively Standard+, but present on any plan where Jira Software is provisioned); org-wide seats, product access, last-active and the org audit log need the Organizations admin API (org admin role + org API key) and, for full audit coverage, Atlassian Guard or Cloud Enterprise.

**Required plan:** Free for site reads: users/projects/groups, JQL issue flow, changelog/worklog cycle time, workflow/status/priority/resolution metadata, permissions & permission schemes, and the in-product audit log (Standard+ in practice - see blockers). Standard+ (Jira Software) for agile boards/sprints/velocity/backlog. Org admin + Organization API key (independent of Jira product tier) for org-wide seats/product-access/last-active and the org audit-events API; Atlassian Guard (Standard/Premium) or Cloud Enterprise for full org audit-log coverage (e.g. user_login).

**Blockers:**
1. Seat/cost data cliff: per-product `product_access` + `last_active` + `access_billable` come ONLY from the v1 org users endpoints, which STOP WORKING after 30 Jun 2026; the v2 directory users API does NOT return `product_access` - no confirmed v2 successor for seat-waste/cost metrics.
2. Site audit log (`/auditing/record`) is effectively Standard+ (no audit log when ALL apps are Free) despite the merged record's free min-tier; the org audit-events API is Guard/Enterprise-gated for full coverage and rate-limited to 10 req/min per user AND per path.
3. Scope strictness: `/statuses/search`, `/statuses`, `/workflow/search`, `/workflowscheme`, `/priority/search` require classic `manage:jira-configuration` (not `read:jira-work`); `/rest/agile/1.0` has NO classic-scope support (granular `*:jira-software` mandatory); `/users/search` is forbidden to Connect apps (use `/user/search`).
4. `/search/jql` has NO total field (use `/search/approximate-count`) and empty JQL returns ALL visible issues unbounded.
5. Rate limiting is a points budget with hard 429s (no gradual throttle); org last-active is capped at 200 req/60s.
6. `/configuration` field set is low-confidence (verified=false); `/changelog/bulkfetch` is flagged EXPERIMENTAL; agile random-access (startAt) pagination is being removed after 2026-11-01.

## Endpoints (93)

| id | name | method | path | response | deprecated |
|----|------|--------|------|----------|------------|
| get-myself | Get current user (myself) | GET | /rest/api/3/myself | inline-json | - |
| bulk-get-users | Get all users (bulk default) | GET | /rest/api/3/users/search | inline-json | - |
| get-user | Get user | GET | /rest/api/3/user | inline-json | - |
| find-users | Find users (search by query) | GET | /rest/api/3/user/search | inline-json | - |
| find-users-assignable-issue | Find users assignable to issues | GET | /rest/api/3/user/assignable/search | inline-json | - |
| find-users-with-permissions | Find users with permissions | GET | /rest/api/3/user/permission/search | inline-json | - |
| project-search | Get projects paginated (project search) | GET | /rest/api/3/project/search | inline-json | - |
| get-project | Get project | GET | /rest/api/3/project/{projectIdOrKey} | inline-json | - |
| get-project-roles | Get project roles for project | GET | /rest/api/3/project/{projectIdOrKey}/role | inline-json | - |
| get-project-role-actors | Get project role for project (actors under a role) | GET | /rest/api/3/project/{projectIdOrKey}/role/{id} | inline-json | - |
| get-project-components | Get project components paginated | GET | /rest/api/3/project/{projectIdOrKey}/component | inline-json | - |
| get-project-versions | Get project versions paginated | GET | /rest/api/3/project/{projectIdOrKey}/version | inline-json | - |
| bulk-get-groups | Bulk get groups | GET | /rest/api/3/group/bulk | inline-json | - |
| get-group-members | Get users from group | GET | /rest/api/3/group/member | inline-json | - |
| get-configuration | Get global Jira configuration | GET | /rest/api/3/configuration | inline-json | - |
| org-get-users-v1 | Get users in organization (managed accounts) [v1, deprecated] | GET | /admin/v1/orgs/{orgId}/users | inline-json | DEPRECATED (retired 2026-06-30) |
| org-get-directory-users-v2 | Get users in organization directory [v2, current] | GET | /admin/v2/orgs/{orgId}/directories/{directoryId}/users | inline-json | - |
| org-user-last-active-dates | Get user last-active dates (org) | GET | /admin/v1/orgs/{orgId}/directory/users/{accountId}/last-active-dates | inline-json | DEPRECATED (retired 2026-06-30) |
| org-get-managed-account-v1 | Get account profile / managed account (org) | GET | /admin/v1/orgs/{orgId}/directory/users/{accountId} | inline-json | DEPRECATED (retired 2026-06-30) |
| search-jql-post | Search for issues using JQL (enhanced, POST) | POST | /rest/api/3/search/jql | inline-json | - |
| search-jql-get | Search for issues using JQL (enhanced, GET) | GET | /rest/api/3/search/jql | inline-json | - |
| search-approximate-count-post | Get approximate issue count for a JQL query | POST | /rest/api/3/search/approximate-count | inline-json | - |
| get-fields | Get fields (custom field discovery) | GET | /rest/api/3/field | inline-json | - |
| get-issue-changelog | Get changelogs (issue history) | GET | /rest/api/3/issue/{issueIdOrKey}/changelog | inline-json | - |
| get-issue-expand-changelog | Get issue with expand=changelog | GET | /rest/api/3/issue/{issueIdOrKey} | inline-json | - |
| get-changelogs-by-ids | Get changelogs by IDs | POST | /rest/api/3/issue/{issueIdOrKey}/changelog/list | inline-json | - |
| bulk-fetch-changelogs | Bulk fetch changelogs (token-paginated) | POST | /rest/api/3/changelog/bulkfetch | inline-json | - |
| get-issue-worklog | Get issue worklogs (time spent / effort) | GET | /rest/api/3/issue/{issueIdOrKey}/worklog | inline-json | - |
| get-worklogs-modified-since | Get IDs of worklogs modified since | GET | /rest/api/3/worklog/updated | inline-json | - |
| get-worklogs-deleted-since | Get IDs of deleted worklogs since | GET | /rest/api/3/worklog/deleted | inline-json | - |
| get-worklogs-by-ids | Get worklogs by IDs (bulk hydrate) | POST | /rest/api/3/worklog/list | inline-json | - |
| get-issue-comments | Get issue comments | GET | /rest/api/3/issue/{issueIdOrKey}/comment | inline-json | - |
| agile-get-all-boards | Get all boards | GET | /rest/agile/1.0/board | inline-json | - |
| agile-get-board | Get board | GET | /rest/agile/1.0/board/{boardId} | inline-json | - |
| agile-get-board-configuration | Get board configuration | GET | /rest/agile/1.0/board/{boardId}/configuration | inline-json | - |
| agile-get-board-sprints | Get all sprints for board | GET | /rest/agile/1.0/board/{boardId}/sprint | inline-json | - |
| agile-get-sprint | Get sprint | GET | /rest/agile/1.0/sprint/{sprintId} | inline-json | - |
| agile-get-sprint-issues | Get issues for sprint | GET | /rest/agile/1.0/sprint/{sprintId}/issue | inline-json | - |
| agile-get-board-issues-for-sprint | Get board issues for sprint | GET | /rest/agile/1.0/board/{boardId}/sprint/{sprintId}/issue | inline-json | - |
| agile-get-board-backlog | Get issues for backlog (board) | GET | /rest/agile/1.0/board/{boardId}/backlog | inline-json | - |
| agile-get-board-backlog-approx-count | Get approximate backlog count (enhanced) | GET | /rest/software/1.0/board/{boardId}/backlog/approximate-count | inline-json | - |
| agile-get-board-issue-approx-count | Get approximate board issue count (enhanced) | GET | /rest/software/1.0/board/{boardId}/issue/approximate-count | inline-json | - |
| agile-get-board-issues | Get issues for board | GET | /rest/agile/1.0/board/{boardId}/issue | inline-json | - |
| agile-get-board-epics | Get epics for board | GET | /rest/agile/1.0/board/{boardId}/epic | inline-json | - |
| agile-get-epic-issues | Get issues for epic | GET | /rest/agile/1.0/epic/{epicIdOrKey}/issue | inline-json | DEPRECATED (epic/none/issue variant) |
| jira-statuses-search | Search statuses (workflow status metadata) | GET | /rest/api/3/statuses/search | inline-json | - |
| jira-statuses-bulk-get | Bulk get statuses by id | GET | /rest/api/3/statuses | inline-json | - |
| jira-status-get-all-legacy | Get all statuses (legacy/simple) | GET | /rest/api/3/status | inline-json | DEPRECATED |
| jira-statuscategory-get-all | Get all status categories | GET | /rest/api/3/statuscategory | inline-json | - |
| jira-statuscategory-get-one | Get status category by id or key | GET | /rest/api/3/statuscategory/{idOrKey} | inline-json | - |
| jira-issuetype-get-all | Get all issue types for user | GET | /rest/api/3/issuetype | inline-json | - |
| jira-issuetype-get-one | Get issue type by id | GET | /rest/api/3/issuetype/{id} | inline-json | - |
| jira-field-search-paginated | Get fields paginated (search) | GET | /rest/api/3/field/search | inline-json | - |
| jira-priority-search | Search priorities (paginated) | GET | /rest/api/3/priority/search | inline-json | - |
| jira-priority-get-all-deprecated | Get priorities (DEPRECATED) | GET | /rest/api/3/priority | inline-json | DEPRECATED |
| jira-resolution-search | Search resolutions (paginated) | GET | /rest/api/3/resolution/search | inline-json | - |
| jira-resolution-get-all-deprecated | Get resolutions (DEPRECATED) | GET | /rest/api/3/resolution | inline-json | DEPRECATED |
| jira-workflow-search | Search workflows (with statuses & transitions) | GET | /rest/api/3/workflow/search | inline-json | - |
| jira-workflowscheme-get-all | Get all workflow schemes (paginated) | GET | /rest/api/3/workflowscheme | inline-json | - |
| jira-workflowscheme-project | Get workflow scheme for project | GET | /rest/api/3/workflowscheme/project | inline-json | - |
| jira-project-statuses | Get all statuses for project | GET | /rest/api/3/project/{projectIdOrKey}/statuses | inline-json | - |
| jira-auditing-record-get | Get audit records (in-product Jira audit log) | GET | /rest/api/3/auditing/record | inline-json | - |
| jira-permissions-get-all | Get all (available) permissions | GET | /rest/api/3/permissions | inline-json | - |
| jira-mypermissions-get | Get my permissions | GET | /rest/api/3/mypermissions | inline-json | - |
| jira-permissions-check-bulk | Get bulk permissions | POST | /rest/api/3/permissions/check | inline-json | - |
| jira-permissions-project | Get permitted projects | POST | /rest/api/3/permissions/project | inline-json | - |
| jira-permissionschemes-list | Get all permission schemes | GET | /rest/api/3/permissionscheme | inline-json | - |
| jira-permissionscheme-get | Get permission scheme (single) | GET | /rest/api/3/permissionscheme/{schemeId} | inline-json | - |
| jira-permissionscheme-grants-get | Get permission scheme grants | GET | /rest/api/3/permissionscheme/{schemeId}/permission | inline-json | - |
| jira-project-permissionscheme-get | Get assigned permission scheme for a project | GET | /rest/api/3/project/{projectKeyOrId}/permissionscheme | inline-json | - |
| jira-project-securitylevel-get | Get project issue security levels | GET | /rest/api/3/project/{projectKeyOrId}/securitylevel | inline-json | - |
| org-events-list | Get organization audit events | GET | /admin/v1/orgs/{orgId}/events | inline-json | - |
| org-events-stream | Poll organization events (events-stream) | GET | /admin/v1/orgs/{orgId}/events-stream | inline-json | - |
| org-event-get | Get a single organization event | GET | /admin/v1/orgs/{orgId}/events/{eventId} | inline-json | - |
| org-event-actions | Get list of event actions | GET | /admin/v1/orgs/{orgId}/event-actions | inline-json | - |
| jira-issue-security-schemes-get | Get all issue security schemes | GET | /rest/api/3/issuesecurityschemes | inline-json | - |
| jira-notification-schemes-get | Get notification schemes | GET | /rest/api/3/notificationscheme | inline-json | - |
| org-admin-list-orgs | List organizations | GET | /admin/v1/orgs | inline-json | - |
| org-admin-get-org | Get organization by ID | GET | /admin/v1/orgs/{orgId} | inline-json | - |
| org-admin-list-directories | List directories in an organization | GET | /admin/v2/orgs/{orgId}/directories | inline-json | - |
| org-admin-directory-user-count | Get directory user count | GET | /admin/v2/orgs/{orgId}/directories/{directoryId}/users/count | inline-json | - |
| org-admin-directory-user-stats | Get directory user stats | GET | /admin/v2/orgs/{orgId}/directories/{directoryId}/users/stats | inline-json | - |
| org-admin-directory-get-user | Get a user in a directory | GET | /admin/v2/orgs/{orgId}/directories/{directoryId}/users/{userId} | inline-json | - |
| org-admin-user-role-assignments | Get user role assignments | GET | /admin/v2/orgs/{orgId}/directories/{directoryId}/users/{accountId}/role-assignments | inline-json | - |
| org-admin-list-domains | Get domains in an organization | GET | /admin/v1/orgs/{orgId}/domains | inline-json | - |
| org-admin-get-domain | Get domain by ID | GET | /admin/v1/orgs/{orgId}/domains/{domainId} | inline-json | - |
| org-admin-list-workspaces | List workspaces (products) in an organization | POST | /admin/v2/orgs/{orgId}/workspaces | inline-json | - |
| auth-basic-email-token | Basic auth (pseudo-endpoint) | GET | /rest/api/3/* (auth scheme) | inline-json | - |
| auth-oauth2-3lo-platform-read-scopes | OAuth 2.0 (3LO) READ scopes - platform (pseudo) | GET | /ex/jira/{cloudid}/rest/api/3/* (auth scheme) | inline-json | - |
| auth-oauth2-3lo-software-read-scopes | OAuth 2.0 (3LO) READ scopes - Jira Software (pseudo) | GET | /ex/jira/{cloudid}/rest/agile/1.0/* (auth scheme) | inline-json | - |
| auth-org-api-key | Organizations admin API - org API key (pseudo) | GET | /v1/orgs/{orgId}/* (auth scheme) | inline-json | - |
| search-legacy-deprecated | Search for issues using JQL (legacy, DEPRECATED) | GET | /rest/api/3/search | inline-json | DEPRECATED/removed |
| rate-limiting-cost-budget | Rate limiting / cost budget (cross-cutting pseudo) | GET | /rest/api/3/* and /rest/agile/1.0/* | inline-json | - |

> Notes on response shape: every endpoint in this catalog is `inline-json` (default). No `download-links` endpoints exist for Jira, so there are no "Report file fields" tables. No endpoint in this catalog carries `exampleRequest`, `exampleResponse`, or a `liveCheck` block (the tool is DORMANT / doc-grounded only - no live call has been made).

---

## Users, Projects & Adoption

### get-myself - Get current user (myself)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/myself`
- **Auth:** scheme `basic-username` - Basic (Atlassian account email + API token). Credential: `Authorization: Basic base64(email:apiToken)`. Supply the secret as `email:token`.
  - Scopes: `read:jira-user`, `read:user:jira`, `read:application-role:jira`, `read:group:jira`
  - Auth notes: No special permission; returns the authenticated principal. Classic OAuth scope `read:jira-user`; granular `read:user:jira`. OAuth 3LO base is `https://api.atlassian.com/ex/jira/{cloudid}`. `expand=groups,applicationRoles`.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Current user identity (adoption) - Confirms authenticated user, account type, active status; basis for engagement attribution (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: platform site read. Basic = base64(email:apiToken); OAuth 3LO host is `https://api.atlassian.com/ex/jira/{cloudid}`. Subject to the points-based rate-limit budget.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-myself/
  - https://developer.atlassian.com/cloud/jira/platform/scopes-for-oauth-2-3LO-and-forge-apps/

### bulk-get-users - Get all users (bulk default)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/users/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-user`, `read:user:jira`, `read:application-role:jira`, `read:avatar:jira`
  - Auth notes: Requires Browse users and groups global permission. VERIFIED GOTCHA: Connect apps cannot access this resource (403) - use `/user/search` in that context. Returns active and inactive site accounts.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Total user count (adoption) - Count of all site accounts (filter accountType=atlassian, active=true) for adoption/seat usage.
  - Active vs inactive users (adoption) - Ratio of active to deactivated accounts.
  - User directory roster (adoption) - Per-user accountId/displayName/email for identity mapping (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Browse users and groups global permission required; unprivileged calls return empty. NOT org-wide seat billing (use the Organizations admin API). Forbidden to Connect apps - use `/user/search`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/

### get-user - Get user

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/user`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-user`, `read:user:jira`, `read:application-role:jira`, `read:avatar:jira`, `read:group:jira`
  - Auth notes: Browse users and groups global permission. accountId only (username/key removed for GDPR). `expand=groups,applicationRoles`.
- **Response shape:** inline-json
- **Datapoints returned:**
  - User profile + license role (adoption) - Per-user detail incl. application (licensed product) roles and group membership (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. accountId only (GDPR). Browse users and groups global permission.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/
  - https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/

### find-users - Find users (search by query)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/user/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-user`, `read:user:jira`, `read:application-role:jira`, `read:avatar:jira`
  - Auth notes: Browse users permission. `query` matches displayName/emailAddress (prefix). Either `query` OR `accountId` required. Accessible to Connect apps (unlike `/users/search`).
- **Response shape:** inline-json
- **Datapoints returned:**
  - User lookup/search (adoption) - Resolve users by name/email for dashboard filters and identity mapping (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Connect-app-safe alternative to `/users/search`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/

### find-users-assignable-issue - Find users assignable to issues

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/user/assignable/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-user`, `read:user:jira`, `read:application-role:jira`, `read:avatar:jira`, `read:project:jira`
  - Auth notes: Browse users + Assign issues project permission. Use `project` OR `issueKey`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | (none declared) | | | Use project OR issueKey (per auth notes) | |
- **Datapoints returned:**
  - Assignable user pool per project (adoption) - Number/identity of users who can be assigned work in a project (team-size proxy; PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Requires `project` param or `issueKey`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/

### find-users-with-permissions - Find users with permissions

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/user/permission/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-user`, `read:user:jira`, `read:application-role:jira`, `read:avatar:jira`, `read:permission:jira`
  - Auth notes: Returns users with a given permission for a project/issue. Administer Jira global permission, or project-scoped. Permission keys e.g. `BROWSE_PROJECTS`.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Users holding a permission (security) - Who can browse/admin a project; permission-coverage and access-governance metric (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: project/global. Requires elevated permission (Administer Jira). Confidence medium - detail page JS-rendered.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence medium; note: "Detail page JS-rendered; corroborated via user-search group listing."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/

### project-search - Get projects paginated (project search)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:project:jira`, `read:project-category:jira`, `read:user:jira`, `read:avatar:jira`
  - Auth notes: Returns projects visible to user (Browse Projects). Primary project enumeration. PageBeanProject (offset pagination). `expand=insight` for issue count + last update. Merged: project-search-tier.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Total project count (adoption) - Number of projects overall and by typeKey/style - core adoption metric.
  - Project type/style breakdown (adoption) - Team-managed vs company-managed; software/business/JSM split.
  - Project last-activity & issue count (activity-flow) - `insight.lastIssueUpdateTime` + `totalIssueCount` per project (active vs dormant).
  - Project lead (adoption) - Lead account per project (ownership; PII).
  - Project inventory (adoption) - Number and type of active projects - adoption/breadth metric.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. `expand=insight` gives issue count + last-update time. Offset pagination. Merged near-duplicate: project-search-tier.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/

### get-project - Get project

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectIdOrKey}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:project:jira`, `read:user:jira`, `read:avatar:jira`, `read:issue-type:jira`
  - Auth notes: Browse Projects permission. `expand=description,lead,issueTypes,url,projectKeys,permissions,insight`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectIdOrKey | path | yes | Project id or key | PROJ |
- **Datapoints returned:**
  - Single project detail (adoption) - Per-project metadata + insight (issue count, last activity) (PII via lead).
- **Gotchas:** Min tier: Free (all tiers). Scope: project. `expand=insight` for issue count + last activity.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/

### get-project-roles - Get project roles for project

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectIdOrKey}/role`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:project-role:jira`, `read:project:jira`
  - Auth notes: Administer Projects project permission, or Administer Jira. Map of role name -> role URL.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectIdOrKey | path | yes | Project id or key | PROJ |
- **Datapoints returned:**
  - Project roles available (adoption) - Which roles exist per project (precursor to role-actor counts).
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Administer Projects (or Administer Jira).
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-role-actors/

### get-project-role-actors - Get project role for project (actors under a role)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectIdOrKey}/role/{id}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:project-role:jira`, `read:project:jira`, `read:user:jira`, `read:group:jira`, `read:avatar:jira`
  - Auth notes: Administer Projects (project) permission. Returns user and group actors assigned to a role. Merged: jira-project-role-actors-get.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectIdOrKey | path | yes | Project id or key | PROJ |
  | id | path | yes | Project role id | 10002 |
- **Datapoints returned:**
  - Project membership by role (adoption) - Count/identity of users and groups in each project role - team-size & access-distribution (PII).
  - Project role assignments (security) - Who is granted which project role (access governance; PII).
  - Project role membership (security) - Who (users/groups) holds each project role per project - feeds permission-scheme role grants (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Requires Administer Projects. Merged near-duplicate: jira-project-role-actors-get.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-role-actors/
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-roles/

### get-project-components - Get project components paginated

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectIdOrKey}/component`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:project:jira`, `read:project.component:jira`, `read:user:jira`, `read:application-role:jira`, `read:avatar:jira`
  - Auth notes: Browse Projects permission. PageBean (offset). Also non-paginated `/components`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectIdOrKey | path | yes | Project id or key | PROJ |
- **Datapoints returned:**
  - Components per project (adoption) - Count of components - configuration depth / usage maturity.
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Offset pagination.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/

### get-project-versions - Get project versions paginated

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectIdOrKey}/version`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:project:jira`, `read:project-version:jira`, `read:user:jira`, `read:avatar:jira`
  - Auth notes: Browse Projects permission. PageBeanVersion. `expand=issuesstatus,operations` for release roll-up.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectIdOrKey | path | yes | Project id or key | PROJ |
- **Datapoints returned:**
  - Releases per project (delivery) - Count of versions, released vs unreleased, release dates - delivery cadence.
  - Version completion status (delivery) - Issue done/in-progress/todo roll-up per version (release readiness).
- **Gotchas:** Min tier: Free (all tiers). Scope: project. `expand=issuesstatus` for release readiness.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-versions/

### bulk-get-groups - Bulk get groups

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/group/bulk`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:group:jira`
  - Auth notes: Administer Jira global permission. Paginated groups with groupId + name. Preferred over deprecated name-only lookups.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Group inventory (adoption) - Count and names of groups; product-access groups (jira-software-users) indicate licensed populations.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Requires Administer Jira.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/

### get-group-members - Get users from group

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/group/member`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:group:jira`, `read:user:jira`, `read:avatar:jira`
  - Auth notes: Administer Jira (or Browse users and groups) global permission. Paginated members. Use groupId (GDPR-stable) over groupname.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Group membership count (adoption) - Members per group - sizing licensed product groups (jira-software-users count ~= seats in use).
  - Group member roster (adoption) - Per-user membership for access mapping (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. NOT billing source of truth - use the Organizations admin API for seats.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/

### get-configuration - Get global Jira configuration

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/configuration`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:configuration:jira`
  - Auth notes: No special permission to read. Returns feature flags: votingEnabled, watchingEnabled, subTasksEnabled, attachmentsEnabled, timeTrackingConfiguration. CORRECTION: belongs to jira-settings group, not time-tracking. The timeTrackingEnabled-field-removal claim is UNVERIFIED - treat with caution.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Site feature configuration (adoption) - Which Jira capabilities (voting, watching, sub-tasks, attachments, time tracking) are enabled site-wide - feature-adoption baseline.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. LOW CONFIDENCE / verified=false: endpoint exists and is current, but the exact field set (timeTrackingEnabled removal nuance) could not be confirmed - re-verify before relying on site feature flags.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence **low**; datapointsVerified=false. Note: "Endpoint current; field-removal nuance (timeTrackingEnabled) unconfirmed - verified=false in research."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-jira-settings/

### org-get-users-v1 - Get users in organization (managed accounts) [v1, deprecated]

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/users`
- **Auth:** scheme `bearer` - Organization API key (Bearer). Credential: `Authorization: Bearer <org-api-key>` from admin.atlassian.com. Org admin role required.
  - Scopes: (none)
  - Auth notes: Org admin only. Base `https://api.atlassian.com/admin`. CONFIRMED DEPRECATED: v1 user/group/directory APIs stop working after 30 Jun 2026; migrate to v2 directory APIs. Only with centralized/new user management. Merged: org-admin-get-managed-accounts, org-list-users.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Atlassian organization id | <orgId> |
- **Datapoints returned:**
  - Org licensed seats / product access (cost) - Per-user product_access across org = billable seats per product (jira-software) - cost/license metric (PII).
  - Org-wide active users (engagement) - last_active per product across org - true active-user signal beyond a single site (PII).
  - Org user count by status (adoption) - active/inactive/closed account counts org-wide.
  - managed_account_count (adoption) - Total managed Atlassian accounts in the org.
  - billable_seats (cost) - Count of accounts where access_billable=true - licensed/billed seats.
  - product_access_per_user (cost) - Which products each user can access, for seat allocation/cost attribution.
  - user_last_active (engagement) - Last-active timestamp per account/product for active-user utilization.
  - account_status_breakdown (adoption) - active/inactive/closed account distribution.
  - account_identity (adoption) - account_id, email, name (identity; PII).
  - Managed account list + product access (cost) - Enumerate org users and product/seat access for licensed-seat and adoption metrics (PII).
  - Org user identities (adoption) - Account IDs and emails of all managed users (PII).
- **Rate limits:** Org admin API rate limits apply (see org last-active dedicated 200/60s limit).
- **Gotchas:** Min tier: org-admin (Organizations admin API; independent of Jira product tier). DIFFERENT host: `https://api.atlassian.com/admin` with an org API key as Bearer. DEPRECATED - stops working after 30 Jun 2026. IMPORTANT: this v1 endpoint is the ONLY source of product_access/last_active per product; v2 directory users does NOT return them - a seat/cost data gap looms at the v1 sunset.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host (api.atlassian.com/admin) with a different credential (org API key as Bearer) - not reachable by the site Basic-auth proxy.
- **DEPRECATED. Retired on: 2026-06-30**
- **Plans:** Org-admin API
- **Verification:** confidence high; note: "Deprecated; v1 sunset 30 Jun 2026; only source of product_access/last_active."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/
  - https://developer.atlassian.com/cloud/admin/changelog/
  - https://support.atlassian.com/user-management/docs/what-are-managed-accounts/

### org-get-directory-users-v2 - Get users in organization directory [v2, current]

- **Request line:** `GET https://api.atlassian.com/admin/admin/v2/orgs/{orgId}/directories/{directoryId}/users`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: (none)
  - Auth notes: Org admin only. Base `https://api.atlassian.com/admin`. Current replacement for deprecated v1 users API. Available on new user management with at least one paid subscription. Merged: org-admin-directory-list-users.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | directoryId | path | yes | Identity directory id | <directoryId> |
- **Datapoints returned:**
  - Org directory user roster (adoption) - Current org-managed user list with status, MFA, claim state, platformRoles (PII).
  - MFA adoption (security) - Share of org users with MFA enabled (mfaEnabled field) - security posture metric.
  - directory_user_roster (adoption) - Per-directory user roster with status and roles (PII).
  - mfa_enabled_rate (security) - Share of users with MFA enabled.
  - account_claim_status (adoption) - Managed/claimed status of accounts (governance/adoption).
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Current v2 API replacing v1. CONFIRMED: returns accountId, accountStatus, mfaEnabled, claimStatus, platformRoles, name, email, department, jobTitle - but NOT product_access/seat detail (v1-only). Seat/cost metrics relying on product_access have no confirmed v2 equivalent.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/
  - https://developer.atlassian.com/cloud/admin/changelog/

### org-user-last-active-dates - Get user last-active dates (org)

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/directory/users/{accountId}/last-active-dates`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: (none)
  - Auth notes: Org admin only. CONFIRMED dedicated rate limit: 200 requests / 60s per org. Activity delayed up to 24h. v1 - subject to 30 Jun 2026 deprecation. Merged: org-admin-user-last-active-dates, org-user-last-active.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | accountId | path | yes | Atlassian account id | <accountId> |
- **Datapoints returned:**
  - Per-user last active per product (engagement) - Last-active date per product per user - org-wide engagement/active-user metric (PII).
  - per_product_last_active (engagement) - Last-active date per product per user - drives active-vs-licensed utilization (seat-waste detection).
  - user_provisioning_date (adoption) - When a user was added to the org.
  - Per-product last-active date (engagement) - Org-level active-user/engagement signal per product per account (PII).
- **Rate limits:** CONFIRMED hard limit: 200 requests / 60s per org (dedicated doc page). Activity delayed up to 24h.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. DEPRECATED v1 - 30 Jun 2026 sunset; no confirmed v2 equivalent for per-product last_active. 200/60s rate cap.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **DEPRECATED. Retired on: 2026-06-30**
- **Plans:** Org-admin API
- **Verification:** confidence high; note: "Deprecated v1; 200/60s rate limit."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/
  - https://developer.atlassian.com/cloud/admin/organization/user-last-active-dates/
  - https://developer.atlassian.com/cloud/admin/organization/rest/intro/

### org-get-managed-account-v1 - Get account profile / managed account (org)

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/directory/users/{accountId}`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: (none)
  - Auth notes: Org admin. Managed-account profile detail. v1 - 30 Jun 2026 deprecation; use v2 directory user detail going forward.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | accountId | path | yes | Atlassian account id | <accountId> |
- **Datapoints returned:**
  - Managed account profile (cost) - Single managed account product access/status - seat detail (PII).
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. DEPRECATED v1 - 30 Jun 2026 sunset; use v2 directory user detail. Confidence medium.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **DEPRECATED. Retired on: 2026-06-30**
- **Plans:** Org-admin API
- **Verification:** confidence medium; note: "Deprecated v1."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/

---

## Issue Search (JQL) & Flow

### search-jql-post - Search for issues using JQL (enhanced, POST)

- **Purpose:** Primary engine for issue-derived flow metrics (throughput, WIP, cycle time, defects).
- **Request line:** `POST https://your-domain.atlassian.net/rest/api/3/search/jql`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-details:jira`, `read:jql:jira`, `read:issue:jira`, `read:project:jira`, `read:user:jira`
  - Auth notes: VERIFIED current. Classic `read:jira-work` covers it; granular `read:issue-details:jira` + `read:jql:jira` (+ `read:project:jira`, `read:user:jira`). Results limited to issues the caller can Browse. Merged: search-jql-current.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | jql | body | yes | Bounded JQL. EMPTY jql returns ALL visible issues (unbounded) - always bound it. | created >= -30d |
  | nextPageToken | body | no | Token pagination cursor; no total field - last page = absent token. | |
  | fields | body | no | Fields to return, e.g. status,resolutiondate,created,assignee. | |
- **Datapoints returned:**
  - Created issue count (period) (activity-flow) - Issues created in a window (created >= start AND created < end); throughput-in / arrival rate.
  - Resolved issue count (period) (activity-flow) - Resolved in window via resolutiondate or statusCategory = Done; throughput-out.
  - Open / WIP issue count (activity-flow) - statusCategory IN (To Do, In Progress) / resolution = Unresolved; WIP and backlog size.
  - Created-vs-resolved net flow (activity-flow) - Created minus resolved over same window; backlog growth/burn-down trend.
  - Lead/cycle time per issue (delivery) - resolutiondate - created per issue; aggregate to median/percentile cycle time.
  - Throughput by assignee/type/priority (activity-flow) - Group resolved counts by assignee.accountId / issuetype / priority.
  - Bug/defect counts (quality) - issuetype = Bug by created/resolved windows; defect arrival and resolution.
  - Assignee identity (engagement) - assignee.displayName/emailAddress - identity attribution (PII).
  - JQL issue query (token pagination) (activity-flow) - Primary metric engine; nextPageToken-based, no total.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. tryable:false - POST needs a JSON body. NO total field (use `/search/approximate-count`). Empty/absent JQL returns ALL visible issues unbounded - always pass a bounded JQL. Detect last page by ABSENT nextPageToken (do NOT rely on isLast - JRACLOUD-94648). Merged: search-jql-current.
- **Tryable:** no. Not tested reason: POST requires a JSON request body (jql, fields, nextPageToken) - not fireable from a GET-only Basic try-it console.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
  - https://confluence.atlassian.com/jirakb/run-jql-search-query-using-jira-cloud-rest-api-1289424308.html
  - https://developer.atlassian.com/cloud/jira/platform/search-and-reconcile/
  - https://jira.atlassian.com/browse/JRACLOUD-94648

### search-jql-get - Search for issues using JQL (enhanced, GET)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/search/jql`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-details:jira`, `read:jql:jira`
  - Auth notes: VERIFIED current (KB documents GET form for smaller queries; switch to POST for larger JQL). Same scopes as POST.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | jql | query | yes | Bounded JQL (short queries). | created >= -30d |
  | fields | query | no | Fields to return. | status,created,resolutiondate |
- **Datapoints returned:**
  - Created/resolved/open issue counts (activity-flow) - Same flow metrics as the POST form via short JQL recipes.
  - Status-category WIP slice (activity-flow) - statusCategory grouping for work-in-progress.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. GET form is for SHORT JQL only (URL length limits) - use POST for larger queries. Same no-total / token-pagination behaviour as POST.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://confluence.atlassian.com/jirakb/run-jql-search-query-using-jira-cloud-rest-api-1289424308.html
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/

### search-approximate-count-post - Get approximate issue count for a JQL query

- **Request line:** `POST https://your-domain.atlassian.net/rest/api/3/search/approximate-count`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-details:jira`, `read:jql:jira`
  - Auth notes: VERIFIED current. `/search/jql` has no total field, so this is the way to get counts without paginating. Returns an approximate, eventually-consistent count. Merged: search-approximate-count.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | jql | body | yes | Bounded JQL whose match count is wanted. | resolution = Unresolved |
- **Datapoints returned:**
  - Created count (approx) (activity-flow) - count for created window - arrival/throughput-in without fetching issues.
  - Resolved count (approx) (activity-flow) - count for resolutiondate window or statusCategory = Done changed window - throughput-out.
  - Open/WIP count (approx) (activity-flow) - count for resolution = Unresolved / statusCategory != Done - backlog & WIP size.
  - Bug count (approx) (quality) - count for issuetype = Bug within a window - defect volume.
  - Net flow (created - resolved) (activity-flow) - Two approximate-count calls differenced over the same window.
  - Approximate JQL issue count (activity-flow) - Count-only metric source (backlog size, open defects, WIP totals).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. tryable:false - POST needs a JSON body. Count is APPROXIMATE and eventually consistent. Merged: search-approximate-count.
- **Tryable:** no. Not tested reason: POST requires a JSON request body (jql) - not fireable from a GET-only Basic try-it console.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://support.atlassian.com/jira/kb/find-the-total-number-of-work-items-in-jira-cloud-using-jql-or-issue-search/
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/

### get-fields - Get fields (custom field discovery for Story Points / numeric custom fields)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/field`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:field:jira`, `read:field-configuration:jira`
  - Auth notes: Required to resolve the site-specific Story Points custom field id (customfield_XXXXX) before selecting it in `/search/jql` fields[] for velocity/effort metrics. Merged: jira-field-get-all.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Story Points custom field ID resolution (delivery) - Maps Story Points (and other numeric custom fields) to their site-specific customfield_XXXXX id, enabling effort/velocity aggregation.
  - Story Points field discovery (delivery) - Locate Story Points by schema.custom = ...customfieldtypes:float (names mutable) for velocity / committed-vs-completed points.
  - Sprint field discovery (delivery) - Locate the Sprint field by schema.custom = com.pyxis.greenhopper.jira:gh-sprint to attribute issues to sprints.
  - Custom field inventory (adoption) - Full field catalog to map any custom field used in metric JQL.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Flat (non-paginated) field list - use `/field/search` for large field sets. Merged: jira-field-get-all.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Promoted from medium; granular scope set not re-confirmed live this pass."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/
  - https://confluence.atlassian.com/jirakb/get-custom-field-ids-for-jira-and-jira-service-management-744522503.html

---

## Changelog, Worklog & Cycle Time

### get-issue-changelog - Get changelogs (issue history -> time-in-status, cycle/lead time, reopen count)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/issue/{issueIdOrKey}/changelog`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue.changelog:jira`
  - Auth notes: Browse Projects permission required (issue-security level honored). Can be accessed anonymously where the project allows. Merged: issue-changelog.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | issueIdOrKey | path | yes | Issue id or key | PROJ-123 |
- **Datapoints returned:**
  - Time-in-status (activity-flow) - Duration per status from diffing consecutive status-change timestamps.
  - Cycle time (activity-flow) - First in-progress transition to first done transition.
  - Lead time (delivery) - Issue created to first Done transition.
  - Reopen count (quality) - Backward status transitions out of a done set. Rework signal.
  - Status transition history (activity-flow) - Ordered transitions for CFD/flow analysis.
  - Field-change author (engagement) - Who performed transitions; identity fields are PII.
  - Field change audit per issue (activity-flow) - Reopen counts, flow efficiency, rework signals.
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Offset (startAt/maxResults) pagination, NOT token pagination. Anonymous-capable where the project allows. Merged: issue-changelog.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/

### get-issue-expand-changelog - Get issue with expand=changelog (single call: fields + history)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/issue/{issueIdOrKey}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue:jira`, `read:issue.changelog:jira`, `read:issue-meta:jira`
  - Auth notes: Browse Projects permission required. `expand=changelog` appends capped history inline.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | issueIdOrKey | path | yes | Issue id or key | PROJ-123 |
  | expand | query | no | Use changelog to inline history. | changelog |
- **Datapoints returned:**
  - Lead time (created->resolution) (delivery) - resolutiondate minus created in one call when resolutiondate is set.
  - Status category classification (activity-flow) - statusCategory.key (new/indeterminate/done) for workflow-agnostic cycle-time mapping.
  - Embedded transition history (activity-flow) - changelog.histories for time-in-status when total <= embedded page.
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Embedded changelog is CAPPED - check changelog.total vs histories.length and fall back to `/changelog` for long histories.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/

### get-changelogs-by-ids - Get changelogs by IDs (fetch specific history entries)

- **Request line:** `POST https://your-domain.atlassian.net/rest/api/3/issue/{issueIdOrKey}/changelog/list`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue.changelog:jira`
  - Auth notes: Read-only POST (body carries changelog IDs). Browse Projects permission required.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | issueIdOrKey | path | yes | Issue id or key | PROJ-123 |
  | changelogIds | body | yes | List of changelog ids to fetch. | |
- **Datapoints returned:**
  - Targeted transition lookup (activity-flow) - Re-fetch specific changelog entries for incremental time-in-status recompute.
- **Gotchas:** Min tier: Free (all tiers). Scope: project. tryable:false - read-only POST carries a JSON body (changelog ids). Returns PageOfChangelogs.
- **Tryable:** no. Not tested reason: Read-only but POST with a JSON body (changelog ids) - not fireable from a GET-only Basic try-it console.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/

### bulk-fetch-changelogs - Bulk fetch changelogs (multi-issue history, token-paginated)

- **Request line:** `POST https://your-domain.atlassian.net/rest/api/3/changelog/bulkfetch`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue.changelog:jira`, `read:issue-meta:jira`, `read:avatar:jira`
  - Auth notes: Read-only POST. Browse Projects per issue. Most efficient cross-issue history pull. EXPERIMENTAL.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | issueIdsOrKeys | body | yes | Batch of issue ids/keys; optional fieldIds=['status','resolution']. | |
- **Datapoints returned:**
  - Portfolio cycle/lead time (activity-flow) - time-in-status, cycle/lead time, reopen counts across a batch of issues in one request.
  - Reopen / rework rate (bulk) (quality) - Count backward status transitions across issues with fieldIds=['status','resolution'].
- **Gotchas:** Min tier: Free (all tiers). Scope: site. tryable:false - POST needs a JSON body. Flagged EXPERIMENTAL by Atlassian - schema/availability may change; keep per-issue `/changelog` as a stable fallback. Confidence medium.
- **Tryable:** no. Not tested reason: POST requires a JSON body (issue ids); also EXPERIMENTAL - not fireable from a GET-only Basic try-it console.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence medium; note: "EXPERIMENTAL API; schema/availability may change."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/
  - https://community.developer.atlassian.com/t/bulk-fetch-changelogs-experimental-api/87240

### get-issue-worklog - Get issue worklogs (time spent / effort)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/issue/{issueIdOrKey}/worklog`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-worklog:jira`, `read:issue-worklog.property:jira`, `read:group:jira`, `read:project-role:jira`, `read:user:jira`, `read:avatar:jira`, `read:application-role:jira`
  - Auth notes: Can be accessed anonymously. Time tracking MUST be enabled or the call errors. Visibility-restricted worklogs filtered by group/role. Merged: issue-worklog.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | issueIdOrKey | path | yes | Issue id or key | PROJ-123 |
- **Datapoints returned:**
  - Time spent per issue (activity-flow) - Sum of timeSpentSeconds = actual effort on an issue.
  - Effort by person (activity-flow) - Group timeSpentSeconds by author.accountId (PII).
  - Effort by period (activity-flow) - Bucket timeSpentSeconds by started date for weekly/sprint trends.
  - Estimate accuracy input (quality) - Summed timeSpentSeconds vs original/remaining estimate (timetracking).
  - Logged effort per author (delivery) - Effort/throughput and capacity-utilization delivery metrics (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Time tracking MUST be enabled. Offset pagination, ordered by created (oldest first). Merged: issue-worklog.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/

### get-worklogs-modified-since - Get IDs of worklogs modified since (incremental worklog sync)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/worklog/updated`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-worklog:jira`
  - Auth notes: Returns IDs + update timestamps for worklogs changed after a time, across all visible issues. Pair with `POST /worklog/list` to hydrate.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | since | query | no | Epoch ms; return worklogs updated after this time. | |
- **Datapoints returned:**
  - Incremental effort sync (activity-flow) - Detect changed worklogs since last poll to keep an effort store current.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Custom cursor pagination: 1000/page, oldest->youngest, follow nextPage / pass since=until until lastPage=true.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/

### get-worklogs-deleted-since - Get IDs of deleted worklogs since (tombstones for sync)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/worklog/deleted`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-worklog:jira`
  - Auth notes: Returns IDs + delete timestamps for worklogs deleted after a time. Remove stale effort records downstream.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | since | query | no | Epoch ms; return worklogs deleted after this time. | |
- **Datapoints returned:**
  - Worklog deletion tombstones (activity-flow) - Subtract deleted worklogs from a cached effort store.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Same 1000/page cursor pagination as `/worklog/updated`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/

### get-worklogs-by-ids - Get worklogs by IDs (bulk hydrate)

- **Request line:** `POST https://your-domain.atlassian.net/rest/api/3/worklog/list`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-worklog:jira`, `read:issue-worklog.property:jira`
  - Auth notes: Read-only POST. Bulk-fetch full worklog details for up to 1000 IDs (typically from `/worklog/updated`).
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | ids | body | yes | Up to 1000 worklog ids to hydrate. | |
- **Datapoints returned:**
  - Bulk effort hydration (activity-flow) - Resolve worklog IDs into timeSpentSeconds/started/author records in one call (<=1000); author is PII.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. tryable:false - POST needs a JSON body (ids). Body limited to 1000 IDs; invisible/non-existent worklogs filtered out.
- **Tryable:** no. Not tested reason: Read-only but POST with a JSON body (worklog ids) - not fireable from a GET-only Basic try-it console.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/

### get-issue-comments - Get issue comments (engagement / collaboration signal)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/issue/{issueIdOrKey}/comment`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:comment:jira`, `read:comment.property:jira`, `read:group:jira`, `read:project-role:jira`, `read:user:jira`, `read:avatar:jira`
  - Auth notes: Browse Projects permission required; visibility-restricted comments filtered by group/role. Can be accessed anonymously where allowed.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | issueIdOrKey | path | yes | Issue id or key | PROJ-123 |
- **Datapoints returned:**
  - Comment count per issue (engagement) - total comments = collaboration intensity.
  - Comments by author (engagement) - Group by author.accountId for per-person participation (PII).
  - Comment activity over time (engagement) - Bucket comments[].created by period for engagement trend.
  - Time-to-first-comment (engagement) - First comment.created minus issue.created (responsiveness proxy).
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Offset pagination. body is ADF; use `expand=renderedBody` for HTML. Anonymous-capable where allowed.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/

---

## Agile: Boards, Sprints & Velocity

> Surface: `/rest/agile/1.0` (+ enhanced `/rest/software/1.0`). No classic-scope support - granular `*:jira-software` scopes mandatory.

### agile-get-all-boards - Get all boards

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:board-scope:jira-software`, `read:project:jira`
  - Auth notes: Granular scopes confirmed. NO classic-scope support on `/rest/agile/1.0`. OAuth host `https://api.atlassian.com/ex/jira/{cloudid}`.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Number of agile boards (adoption) - Count and scrum/kanban split = agile-practice adoption.
  - Board-to-project mapping (activity-flow) - Maps boards to projects for per-team flow metrics.
- **Gotchas:** Min tier: Standard (Jira Software; present on any plan where Jira Software is provisioned, incl. some Free). Surface: `/rest/agile/1.0` (not `/rest/api/3`). Granular `*:jira-software` scopes mandatory.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/

### agile-get-board - Get board

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board/{boardId}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:board-scope:jira-software`, `read:project:jira`
  - Auth notes: Granular `*:jira-software` scopes mandatory.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - Board metadata (adoption) - Board type and location.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/

### agile-get-board-configuration - Get board configuration (story-points field discovery)

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board/{boardId}/configuration`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:board-scope:jira-software`, `read:issue-details:jira`, `read:project:jira`, `read:user:jira`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - Story-points estimation field id (activity-flow) - Discovers per-board estimate field; prerequisite for velocity.
  - Board column-to-status mapping (activity-flow) - Basis for WIP-per-column and column cycle time.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`. Canonical way to discover the per-board estimation custom field id.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/
  - https://support.atlassian.com/jira-software-cloud/docs/configure-estimation-and-tracking/

### agile-get-board-sprints - Get all sprints for board

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board/{boardId}/sprint`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:sprint:jira-software`, `read:board-scope:jira-software`
  - Auth notes: Merged: agile-board-sprints.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - Sprint cadence and count (delivery) - Sprint count, durations, active/closed mix per board.
  - Sprint schedule adherence (delivery) - completeDate vs planned endDate.
  - Sprint inventory for velocity series (activity-flow) - Enumerates closed sprints for velocity time series.
  - Sprint cadence and completion (delivery) - Velocity, sprint completion rate, commitment-vs-delivered.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`. Sprints only on SCRUM boards; kanban returns 400/empty. Merged: agile-board-sprints.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/

### agile-get-sprint - Get sprint

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/sprint/{sprintId}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:sprint:jira-software`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | sprintId | path | yes | Sprint id | 10 |
- **Datapoints returned:**
  - Sprint window and goal (delivery) - Time window for burndown and commitment-vs-done snapshots.
  - Sprint duration (delivery) - Planned length for normalizing throughput.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/

### agile-get-sprint-issues - Get issues for sprint

- **Purpose:** Primary velocity endpoint: sum the estimation field over done issues.
- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/sprint/{sprintId}/issue`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:sprint:jira-software`, `read:issue-details:jira`, `read:jql:jira`, `read:board-scope:jira-software`
  - Auth notes: Request estimation field id (from board configuration) plus status,resolution,resolutiondate via fields param. Identity fields (assignee/reporter) trigger PII if requested.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | sprintId | path | yes | Sprint id | 10 |
  | fields | query | no | Include the estimation field id + status,resolution,resolutiondate. | customfield_10016,status,resolutiondate |
- **Datapoints returned:**
  - Sprint velocity (story points completed) (activity-flow) - Sum of estimation field over done issues = core velocity.
  - Commitment vs completed (delivery) - Committed vs done points/issues = sprint completion rate.
  - Sprint throughput (issues done) (activity-flow) - Count of completed issues per sprint.
  - Carryover / spillover (delivery) - closedSprints reveals work carried across sprints.
  - Burndown inputs (activity-flow) - Per-issue status + resolutiondate (expand=changelog for true burndown).
  - Sprint assignee distribution (engagement) - If assignee requested, per-person sprint workload distribution (PII).
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`. Enhanced token-paginated variant `GET /rest/software/1.0/sprint/{sprintId}/issue` exists.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/

### agile-get-board-issues-for-sprint - Get board issues for sprint

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board/{boardId}/sprint/{sprintId}/issue`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:sprint:jira-software`, `read:board-scope:jira-software`, `read:issue-details:jira`, `read:jql:jira`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
  | sprintId | path | yes | Sprint id | 10 |
- **Datapoints returned:**
  - Board-scoped sprint velocity (activity-flow) - Velocity within a board's filter scope.
  - Board-scoped commitment vs done (delivery) - Completion rate respecting board JQL.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`. Enhanced `GET /rest/software/1.0/board/{boardId}/sprint/{sprintId}/issue` exists.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/

### agile-get-board-backlog - Get issues for backlog (board)

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board/{boardId}/backlog`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:board-scope:jira-software`, `read:issue-details:jira`, `read:jql:jira`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - Backlog size / points (activity-flow) - Count and summed points of un-sprinted backlog = queue depth; pairs with velocity for forecast.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`. The Backlog group itself only exposes POST move ops (excluded as mutations). Enhanced `GET /rest/software/1.0/board/{boardId}/backlog` exists.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/

### agile-get-board-backlog-approx-count - Get approximate backlog count (enhanced)

- **Request line:** `GET https://your-domain.atlassian.net/rest/software/1.0/board/{boardId}/backlog/approximate-count`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:board-scope:jira-software`, `read:issue-details:jira`, `read:jql:jira`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - Approximate backlog volume (activity-flow) - Cheap backlog depth estimate for dashboards at scale.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: ENHANCED `/rest/software/1.0` (not `/rest/agile/1.0`). Cheap approximate count, avoids full counts.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/

### agile-get-board-issue-approx-count - Get approximate board issue count (enhanced)

- **Request line:** `GET https://your-domain.atlassian.net/rest/software/1.0/board/{boardId}/issue/approximate-count`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:board-scope:jira-software`, `read:issue-details:jira`, `read:jql:jira`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - Approximate board issue volume (activity-flow) - Cheap total-issues-on-board estimate for WIP/throughput dashboards.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: ENHANCED `/rest/software/1.0`. ADDED BY VERIFIER (confirmed on Board group docs alongside backlog/approximate-count).
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/

### agile-get-board-issues - Get issues for board

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board/{boardId}/issue`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:board-scope:jira-software`, `read:issue-details:jira`, `read:jql:jira`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - WIP by status category (activity-flow) - Distribution across new/indeterminate/done = WIP and flow distribution.
  - Board throughput over window (activity-flow) - Issues to done in a window (expand=changelog) = throughput/cycle time.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`. Enhanced token-paginated variant `GET /rest/software/1.0/board/{boardId}/issue` (nextPageToken).
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/

### agile-get-board-epics - Get epics for board

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/board/{boardId}/epic`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:epic:jira-software`, `read:board-scope:jira-software`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | boardId | path | yes | Board id | 1 |
- **Datapoints returned:**
  - Epic count and completion (delivery) - Epic count and done/not-done split per board = larger-grain delivery progress.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`.
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-epic/

### agile-get-epic-issues - Get issues for epic

- **Request line:** `GET https://your-domain.atlassian.net/rest/agile/1.0/epic/{epicIdOrKey}/issue`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:epic:jira-software`, `read:issue-details:jira`, `read:jql:jira`
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | epicIdOrKey | path | yes | Epic id or key | PROJ-1 |
- **Datapoints returned:**
  - Epic progress (points/issues done) (delivery) - Sum/ratio of done points within an epic = epic burn-up / delivery progress.
- **Gotchas:** Min tier: Standard (Jira Software). Surface: `/rest/agile/1.0`. Enhanced token-paginated variant `GET /rest/software/1.0/epic/{epicIdOrKey}/issue` exists. NOTE: the epic/none/issue variant is DEPRECATED - use JQL 'parent is empty' for issues with no epic.
- **Tryable:** yes
- **DEPRECATED** (epic/none/issue variant). 
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; note: "epic/none/issue variant deprecated - use JQL 'parent is empty'."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/rest/api-group-epic/

---

## Workflow / Status Metadata

### jira-statuses-search - Search statuses (workflow status metadata)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/statuses/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `manage:jira-configuration`, `read:workflow:jira`
  - Auth notes: CORRECTED: classic RECOMMENDED scope is `manage:jira-configuration`; granular is `read:workflow:jira`. NOT `read:status:jira` / `read:jira-work` for this status-management resource. maxResults max 200.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Status -> done/in-progress classification (quality) - statusCategory (TODO/IN_PROGRESS/DONE) classifies Done vs WIP - basis for cycle-time/throughput/completion.
  - Status inventory & scope (activity-flow) - Enumerate all global/project statuses + usages to build the status model flow metrics depend on.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. SCOPE STRICTNESS: requires classic `manage:jira-configuration` (not `read:jira-work`). New status management API; returns global + project-scoped statuses with usages.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-status/
  - https://community.developer.atlassian.com/t/status-management-api-shipped-to-jira-cloud/58044

### jira-statuses-bulk-get - Bulk get statuses by id

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/statuses`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `manage:jira-configuration`, `read:workflow:jira`
  - Auth notes: CORRECTED: same as `/statuses/search` - classic `manage:jira-configuration`, granular `read:workflow:jira`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | id | query | yes | Up to 50 status ids. | 10000 |
- **Datapoints returned:**
  - Status detail resolution (quality) - Resolve specific status ids to statusCategory for done/in-progress tagging in metric pipelines.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. SCOPE STRICTNESS: `manage:jira-configuration`. Returns full status objects (statusCategory & scope) for up to 50 ids.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-status/

### jira-status-get-all-legacy - Get all statuses (legacy/simple)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/status`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:status:jira`
  - Auth notes: Classic `read:jira-work` (RECOMMENDED), granular `read:status:jira`. No pagination (returns full array).
- **Response shape:** inline-json
- **Datapoints returned:**
  - Global status->category map (quality) - One-call map of every status to its statusCategory key (new/indeterminate/done) when project-scoping is not needed.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. DEPRECATED - prefer `/statuses/search` for scope+usages+pagination. Still supported.
- **Tryable:** yes
- **DEPRECATED**
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Legacy flat /status - prefer /statuses/search."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-statuses/

### jira-statuscategory-get-all - Get all status categories

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/statuscategory`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:status:jira`
  - Auth notes: Classic `read:jira-work` (RECOMMENDED), granular `read:status:jira`. Reference data.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Status category reference (done/in-progress canon) (quality) - Canonical fixed list (new/indeterminate/done) used to interpret each status's statusCategory.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Returns the fixed set of status categories (cannot be modified/extended).
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-status-categories/

### jira-statuscategory-get-one - Get status category by id or key

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/statuscategory/{idOrKey}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:status:jira`
  - Auth notes: Classic `read:jira-work` (RECOMMENDED), granular `read:status:jira`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | idOrKey | path | yes | Status category id or key | done |
- **Datapoints returned:**
  - Single status category lookup (quality) - Resolve one status category (e.g. 'done') for classification logic.
- **Gotchas:** Min tier: Free (all tiers). Scope: site.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-status-categories/

### jira-issuetype-get-all - Get all issue types for user

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/issuetype`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-type:jira`, `read:avatar:jira`, `read:project-category:jira`, `read:project:jira`
  - Auth notes: Classic `read:jira-work` (RECOMMENDED). Can be called anonymously for anonymous-allowed projects.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Issue type taxonomy (activity-flow) - Enumerate issue types + hierarchy levels to segment throughput/cycle-time by Story/Bug/Epic and identify Bug types.
  - Bug type discovery (quality) - Identify Bug/defect issue type ids to scope quality (defect count/reopen) JQL queries.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. With Administer Jira all types returned; otherwise only types in browsable projects. hierarchyLevel: Epic=1, standard=0, Subtask=-1. Anonymous-capable.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/

### jira-issuetype-get-one - Get issue type by id

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/issuetype/{id}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-type:jira`, `read:avatar:jira`
  - Auth notes: Classic `read:jira-work`; granular `read:issue-type:jira` (+ `read:avatar:jira`).
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | id | path | yes | Issue type id | 10001 |
- **Datapoints returned:**
  - Issue type detail (activity-flow) - Resolve a single issue type for classification.
- **Gotchas:** Min tier: Free (all tiers). Scope: site.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/

### jira-field-search-paginated - Get fields paginated (search)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/field/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:field:jira`, `read:field-configuration:jira`
  - Auth notes: CORRECTED: classic `read:jira-work`, granular `read:field:jira` + `read:field-configuration:jira`. Administer Jira is NOT required to call it; it only affects which fields are visible.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Filtered custom field discovery (delivery) - Paginated/queryable lookup of Story Points & Sprint fields by type and schema for metric configuration.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Paginated/filterable view of custom fields (by type, query, screen usage) - better than `/field` for large field sets.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/

### jira-priority-search - Search priorities (paginated)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/priority/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `manage:jira-configuration`
  - Auth notes: CONFIRMED quirk: Search priorities requires `manage:jira-configuration` despite being read-only. Caller needs Administer Jira permission.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Priority taxonomy (quality) - Enumerate priorities to weight/segment defect & flow metrics (e.g. count of Highest-priority bugs open).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. SCOPE STRICTNESS: requires `manage:jira-configuration` despite read-only (confirmed community thread 78396). Replacement for deprecated `/priority`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/
  - https://community.developer.atlassian.com/t/why-does-search-priorities-require-the-manage-jira-configuration-scope/78396

### jira-priority-get-all-deprecated - Get priorities (DEPRECATED)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/priority`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:priority:jira`
  - Auth notes: Deprecated. Classic `read:jira-work`, granular `read:priority:jira`. Replacement `/priority/search` needs `manage:jira-configuration`.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Priority list (legacy) (quality) - Legacy flat priority list; superseded by `/priority/search`.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. DEPRECATED - use `/priority/search`. Do not build new integrations on it.
- **Tryable:** yes
- **DEPRECATED**
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Use /priority/search (needs manage:jira-configuration)."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/

### jira-resolution-search - Search resolutions (paginated)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/resolution/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:resolution:jira`
  - Auth notes: CONFIRMED: classic `read:jira-work`, granular `read:resolution:jira`. Needs Permission to access Jira. Send `Accept: application/json` (406 if missing).
- **Response shape:** inline-json
- **Datapoints returned:**
  - Resolution taxonomy (quality) - Enumerate resolutions to distinguish genuinely-fixed (Done) from Won't Do/Duplicate when computing defect resolution & true-done metrics.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Send `Accept: application/json` (406 otherwise). Replacement for deprecated `/resolution`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/
  - https://community.developer.atlassian.com/t/http-406-status-code-from-rest-api-3-resolution-search/75381

### jira-resolution-get-all-deprecated - Get resolutions (DEPRECATED)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/resolution`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:resolution:jira`
  - Auth notes: Deprecated. Classic `read:jira-work`, granular `read:resolution:jira`.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Resolution list (legacy) (quality) - Legacy flat resolution list; superseded by `/resolution/search`.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. DEPRECATED - use `/resolution/search`. Do not build new integrations on it.
- **Tryable:** yes
- **DEPRECATED**
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Use /resolution/search."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/

### jira-workflow-search - Search workflows (with statuses & transitions)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/workflow/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `manage:jira-configuration`, `read:workflow:jira`
  - Auth notes: CORRECTED: classic RECOMMENDED is `manage:jira-configuration`. Granular `read:workflow:jira`. Requires Administer Jira global permission.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Workflow state model (activity-flow) - Map each workflow's statuses + transitions (legal To Do -> In Progress -> Done) - underpins cycle-time/lead-time segmentation.
  - Done/in-progress status set per workflow (quality) - With statusCategory, identifies which statuses constitute Done vs WIP within each project's workflow.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. ADMIN-gated (Administer Jira). SCOPE STRICTNESS: `manage:jira-configuration`. `expand=statuses,transitions` for the state model. Confidence medium.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence medium; note: "Detail page corroborated indirectly; re-confirm scopes/fields."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/

### jira-workflowscheme-get-all - Get all workflow schemes (paginated)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/workflowscheme`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `manage:jira-configuration`, `read:workflow-scheme:jira`
  - Auth notes: CORRECTED: classic RECOMMENDED is `manage:jira-configuration`. Granular `read:workflow-scheme:jira` (+ `read:workflow:jira`). Requires Administer Jira global permission.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Issue type -> workflow mapping (activity-flow) - Resolve which workflow each issue type uses (via the scheme) so flow metrics apply the right done/in-progress status set per project.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. ADMIN-gated (Administer Jira). SCOPE STRICTNESS: `manage:jira-configuration`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/

### jira-workflowscheme-project - Get workflow scheme for project

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/workflowscheme/project`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `manage:jira-configuration`, `read:workflow-scheme:jira`
  - Auth notes: CORRECTED: classic `manage:jira-configuration`, granular `read:workflow-scheme:jira`. Requires Administer Jira. projectId is a required repeated query param.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectId | query | yes | Project id (repeatable). | 10000 |
- **Datapoints returned:**
  - Project -> workflow scheme link (activity-flow) - Directly resolve a project's workflow scheme to determine its status/transition model for flow metrics.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. ADMIN-gated. SCOPE STRICTNESS: `manage:jira-configuration`. projectId required. Confidence medium.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence medium; note: "Re-confirm scopes/fields."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/

### jira-project-statuses - Get all statuses for project (issue types -> valid statuses)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectIdOrKey}/statuses`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`, `read:issue-type:jira`, `read:project:jira`, `read:status:jira`, `read:workflow:jira`
  - Auth notes: Classic `read:jira-work`. Only needs Browse Projects on the project - NOT Administer Jira, unlike `/workflow/search`. Strong non-admin fallback for per-project flow metrics.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectIdOrKey | path | yes | Project id or key | PROJ |
- **Datapoints returned:**
  - Per-project issue-type status model (activity-flow) - Map each issue type in a project to its valid statuses (and statusCategory) for accurate per-project cycle-time/WIP/done classification without admin permission.
  - Done-status set per project (non-admin) (quality) - Derive which statuses count as Done/In-Progress per project workflow using only Browse Projects permission.
- **Gotchas:** Min tier: Free (all tiers). Scope: project. ADDED by verifier. The most direct NON-admin way to get a project's status model (Browse Projects only). Confidence medium.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence medium; note: "Added by verifier; re-confirm."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/

---

## Audit, Permissions & Governance

### jira-auditing-record-get - Get audit records (in-product Jira audit log)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/auditing/record`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:audit-log:jira`, `read:user:jira`, `read:avatar:jira`
  - Auth notes: Granular `read:audit-log:jira` + `read:user:jira` confirmed. Classic recommended `manage:jira-configuration`. Requires 'Administer Jira' global permission. Merged: audit-records-tier-gated.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Audit event volume / count (security) - Total admin/config/permission audit events over a window (total field, time-filtered).
  - Permission & access changes (security) - Permission scheme edits, group membership changes, role grants (category=permissions / group management).
  - Admin actor identity (security) - Who performed an admin change (authorAccountId/authorKey, remoteAddress) (PII).
  - Configuration change activity (activity-flow) - Volume/timeline of configuration changes as a governance activity signal.
  - Audit records (security) - Permission/config change audit trail. Site-level on Standard+; org-wide/granular on Enterprise/Guard (PII).
- **Gotchas:** Min tier: Free per the API doc, BUT effective gate is Standard+ (no audit log when ALL apps are Free - Atlassian support docs). ADMIN-gated (Administer Jira). In-product per-product audit log, ~180-day retention. Merged: audit-records-tier-gated (which carried minTier=standard).
- **Tryable:** yes
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Tier conflict: API min-tier free but effective gate Standard+ (merged audit-records-tier-gated)."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/
  - https://support.atlassian.com/jira-cloud-administration/docs/audit-activities-in-jira-applications/

### jira-permissions-get-all - Get all (available) permissions

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/permissions`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission:jira`
  - Auth notes: Classic scope `manage:jira-configuration`. Requires Administer Jira global permission.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Supported permission catalogue (security) - Enumeration of all global and project permission keys defined on the instance.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. ADMIN-gated (Administer Jira).
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/

### jira-mypermissions-get - Get my permissions

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/mypermissions`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission:jira`
  - Auth notes: No specific Jira permission required; can be anonymous. 'permissions' query param mandatory since 1 Feb 2019.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | permissions | query | yes | Comma-separated permission keys (REQUIRED). | BROWSE_PROJECTS,ADMINISTER |
- **Datapoints returned:**
  - Effective permission check (self) (security) - Whether the authenticated user holds specified permissions in a given context (havePermission booleans).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Can be anonymous. The 'permissions' query param has been REQUIRED since 1 Feb 2019.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/
  - https://developer.atlassian.com/cloud/jira/platform/change-notice-get-my-permissions-requires-permissions-query-parameter/

### jira-permissions-check-bulk - Get bulk permissions (check permissions for an account across projects)

- **Request line:** `POST https://your-domain.atlassian.net/rest/api/3/permissions/check`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission:jira`
  - Auth notes: Body accountId lets an admin evaluate another user (then Administer Jira required); self-check needs none. Max 1000 projects and 1000 issues per call.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | accountId | body | no | Evaluate another user (admin only); omit for self-check. | |
  | projectPermissions | body | no | Permission keys + project/issue ids to evaluate. | |
- **Datapoints returned:**
  - Effective permission check (any user) (security) - Which global/project/issue permissions a specified account holds (admin required to check others) (PII).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. tryable:false - POST carries a JSON body. Administer Jira required ONLY to check OTHER users; self-checks need none.
- **Tryable:** no. Not tested reason: Permission-evaluation READ but POST with a JSON body (accountId, projectPermissions) - not fireable from a GET-only Basic try-it console.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/

### jira-permissions-project - Get permitted projects (projects where caller has a permission)

- **Request line:** `POST https://your-domain.atlassian.net/rest/api/3/permissions/project`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission:jira`, `read:project:jira`
  - Auth notes: Classic scope `read:jira-work`. Evaluates the authenticated caller only.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | permissions | body | yes | Project permission keys to evaluate. | BROWSE_PROJECTS |
- **Datapoints returned:**
  - Accessible project scope (self) (security) - Set of projects the user can act on under a given permission.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. tryable:false - POST carries a JSON body. READ returning project ids the caller can act on. No admin permission needed.
- **Tryable:** no. Not tested reason: READ but POST with a JSON body (permission keys) - not fireable from a GET-only Basic try-it console.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/

### jira-permissionschemes-list - Get all permission schemes

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/permissionscheme`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission-scheme:jira`, `read:permission:jira`, `read:application-role:jira`, `read:group:jira`, `read:field:jira`, `read:user:jira`, `read:project-role:jira`, `read:avatar:jira`
  - Auth notes: Granular `read:permission-scheme:jira` confirmed. Classic scope `manage:jira-configuration`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | expand | query | no | Inline grants. | permissions,user,group,projectRole,field,all |
- **Datapoints returned:**
  - Permission scheme inventory (security) - All permission schemes and their grant structure (user/group/role -> permission).
- **Gotchas:** Min tier: Free (all tiers). Scope: site. Use `?expand=permissions,user,group,projectRole,field,all` to inline grants. Administer Jira for full grant detail.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/

### jira-permissionscheme-get - Get permission scheme (single)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/permissionscheme/{schemeId}`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission-scheme:jira`, `read:permission:jira`, `read:group:jira`, `read:user:jira`, `read:project-role:jira`, `read:field:jira`, `read:application-role:jira`, `read:avatar:jira`
  - Auth notes: Classic scope `manage:jira-configuration`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | schemeId | path | yes | Permission scheme id | 10000 |
- **Datapoints returned:**
  - Permission scheme grants (security) - Detailed grant list for a scheme - who (user/group/role) holds which permission.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. expand to inline grants/holders.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/

### jira-permissionscheme-grants-get - Get permission scheme grants

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/permissionscheme/{schemeId}/permission`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission-scheme:jira`, `read:permission:jira`, `read:group:jira`, `read:user:jira`, `read:project-role:jira`, `read:field:jira`, `read:avatar:jira`
  - Auth notes: Classic scope `manage:jira-configuration`. holder.parameter is an accountId when holder type is user (PII).
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | schemeId | path | yes | Permission scheme id | 10000 |
- **Datapoints returned:**
  - Permission grant holders (security) - Who is granted each permission (group/role/user) within a scheme; PII when holder is a specific accountId.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. `GET /permission/{permissionId}` returns a single grant.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/

### jira-project-permissionscheme-get - Get assigned permission scheme for a project

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectKeyOrId}/permissionscheme`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:permission-scheme:jira`, `read:project:jira`
  - Auth notes: Classic scope `manage:jira-configuration`. Administer Jira / Administer Projects required.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectKeyOrId | path | yes | Project key or id | PROJ |
- **Datapoints returned:**
  - Project-to-scheme mapping (security) - Which permission scheme governs each project - access-governance coverage map.
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Requires Administer Jira global OR Administer Projects project permission.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-permission-schemes/

### jira-project-securitylevel-get - Get project issue security levels

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/project/{projectKeyOrId}/securitylevel`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:issue-security-level:jira`, `read:project:jira`
  - Auth notes: Granular `read:issue-security-level:jira` confirmed. Classic scope `read:jira-work`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | projectKeyOrId | path | yes | Project key or id | PROJ |
- **Datapoints returned:**
  - Issue security levels (security) - Confidentiality/visibility levels configured per project - data-governance posture.
- **Gotchas:** Min tier: Free (all tiers). Scope: project. Requires Administer Jira global OR Administer Projects project permission.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-permission-schemes/

### org-events-list - Get organization audit events (Organizations admin API)

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/events`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: (none)
  - Auth notes: Base URL `https://api.atlassian.com/admin`. `Authorization: Bearer {org-api-key}`. Not OAuth 3LO; not Basic. Merged: org-admin-query-audit-events.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
- **Datapoints returned:**
  - Org-wide security events (security) - Org audit trail: logins, group/permission changes, product-access grants, policy changes (PII).
  - Login / access activity (engagement) - user_login and access events as an org-level active-use signal (Guard/Enterprise gated) (PII).
  - Product access provisioning events (cost) - Grant/revoke of product access (seat lifecycle) captured as audit events (PII).
  - admin_audit_events (security) - Org-level administrative/security events (user/product/policy changes) (PII).
  - admin_activity_volume (security) - Volume/trend of admin actions over time.
- **Rate limits:** Heavily rate-limited: 10 req/min per user AND per path.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key (Bearer). Callable with at least one paid subscription, but FULL org audit coverage (e.g. user_login) is gated behind Atlassian Guard (Standard/Premium) or Cloud Enterprise. Retention up to 180 days. Merged: org-admin-query-audit-events.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy; also Guard/Enterprise-gated.
- **Plans:** Org-admin API, Atlassian Guard
- **Verification:** confidence high; note: "Guard/Enterprise-gated for full coverage; 10 req/min per user and per path."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-events/
  - https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-guard/

### org-events-stream - Poll organization events (events-stream polling API)

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/events-stream`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: (none)
  - Auth notes: Base URL `https://api.atlassian.com/admin`. Bearer org API key. Org admin only. Merged: org-admin-poll-audit-events-stream.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
- **Datapoints returned:**
  - Streaming org audit ingestion (security) - Gap-free polling of org audit events for continuous governance/SIEM ingestion (PII).
  - audit_event_stream (security) - Sequential org audit event feed for continuous ingestion / activity monitoring (PII).
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Recommended gap-free polling endpoint; sorts by event PROCESSING time (processedAt). Default page size 200. Same Guard/Enterprise coverage gating as `/events`. Merged: org-admin-poll-audit-events-stream.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API, Atlassian Guard
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/poll-events-migration/
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-events/

### org-event-get - Get a single organization event

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/events/{eventId}`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: (none)
  - Auth notes: Base URL `https://api.atlassian.com/admin`. Bearer org API key. Merged: org-admin-get-event-by-id.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | eventId | path | yes | Audit event id | <eventId> |
- **Datapoints returned:**
  - Single audit event detail (security) - Full detail of one org-level audit event for investigation (PII).
  - audit_event_detail (security) - Single audit event detail (forensic lookup) (PII).
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Merged: org-admin-get-event-by-id.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-events/

### org-event-actions - Get list of event actions (org audit action types)

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/event-actions`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: (none)
  - Auth notes: Base URL `https://api.atlassian.com/admin`. Bearer org API key. Merged: org-admin-list-event-actions.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
- **Datapoints returned:**
  - Audit action taxonomy (security) - Reference list of all org audit action types for categorising governance events.
  - audit_action_catalog (security) - Taxonomy of audit action types available for classifying admin/security activity.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Merged: org-admin-list-event-actions.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; note: "Promoted from medium confidence."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-events/

### jira-issue-security-schemes-get - Get all issue security schemes

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/issuesecurityschemes`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:issue-security-scheme:jira`, `read:issue-security-level:jira`
  - Auth notes: Granular `read:issue-security-scheme:jira` + `read:issue-security-level:jira` confirmed.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Issue security scheme inventory (security) - All issue security schemes and their default levels - data-confidentiality governance posture across the site.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. ADDED - missed by researcher. Requires Administer Jira global permission. Companions: `/issuesecurityschemes/{id}`, `/{schemeId}/members`.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-security-schemes/

### jira-notification-schemes-get - Get notification schemes

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/notificationscheme`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:notification-scheme:jira`, `read:field:jira`, `read:project:jira`, `read:project-role:jira`, `read:user:jira`
  - Auth notes: Granular scopes confirmed. Uses startAt/maxResults pagination.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Notification scheme inventory (security) - Which events notify which recipients (users/groups/roles) - information-flow / disclosure governance signal.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. ADDED - missed by researcher. Offset pagination; expand for event->recipient mappings. Administer Jira for full detail. Confidence medium.
- **Tryable:** yes
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence medium; note: "Detail page JS-rendered; re-confirm scopes/fields."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-notification-schemes/

---

## Org Admin: Seats & Cost

> All on the Organizations admin API host (`api.atlassian.com/admin`).

### org-admin-list-orgs - List organizations

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:organization:admin`
  - Auth notes: Org API key as Bearer (classic scope `manage:org-data:atlassian-admin`) OR OAuth app authorized by an org admin (granular `read:organization:admin`). Base `https://api.atlassian.com/admin`.
- **Response shape:** inline-json
- **Datapoints returned:**
  - organization_count (adoption) - Number of Atlassian organizations the credential governs.
  - organization_identity (adoption) - orgId + name; top-level tenant boundary.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Foundational call to obtain orgId. No product-tier gating.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-orgs/

### org-admin-get-org - Get organization by ID

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:organization:admin`
  - Auth notes: Org admin required.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
- **Datapoints returned:**
  - organization_profile (adoption) - Org name/identity and related resource links.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Single-org detail with links to domains and users.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-orgs/

### org-admin-list-directories - List directories in an organization

- **Request line:** `GET https://api.atlassian.com/admin/admin/v2/orgs/{orgId}/directories`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:directories:admin`
  - Auth notes: Org admin. Granular OAuth scope `read:directories:admin` confirmed.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
- **Datapoints returned:**
  - directory_count (adoption) - Number of identity directories in the org.
  - directory_inventory (adoption) - Directory IDs/names that hold managed identities.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Directories underpin managed accounts. Supports filter by accountId, directoryIds, searchTerm.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-directory/

### org-admin-directory-user-count - Get directory user count

- **Request line:** `GET https://api.atlassian.com/admin/admin/v2/orgs/{orgId}/directories/{directoryId}/users/count`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:directories:admin`
  - Auth notes: Org admin. Scope `read:directories:admin`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | directoryId | path | yes | Directory id | <directoryId> |
- **Datapoints returned:**
  - directory_user_count (adoption) - Total users in an identity directory.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Fast count without paging the full list - efficient seat/adoption headline metric.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/

### org-admin-directory-user-stats - Get directory user stats

- **Request line:** `GET https://api.atlassian.com/admin/admin/v2/orgs/{orgId}/directories/{directoryId}/users/stats`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:directories:admin`
  - Auth notes: Org admin.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | directoryId | path | yes | Directory id | <directoryId> |
- **Datapoints returned:**
  - users_by_role (adoption) - Distribution of directory users by platform role.
  - users_by_status (adoption) - Active vs inactive account counts in a directory.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Pre-computed adoption breakdown by role and account status.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/

### org-admin-directory-get-user - Get a user in a directory (single user detail)

- **Request line:** `GET https://api.atlassian.com/admin/admin/v2/orgs/{orgId}/directories/{directoryId}/users/{userId}`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:directories:admin`
  - Auth notes: Org admin. Granular scope `read:directories:admin`.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | directoryId | path | yes | Directory id | <directoryId> |
  | userId | path | yes | User account id | <userId> |
- **Datapoints returned:**
  - user_security_posture (security) - Per-user MFA + claim/membership status (PII).
  - user_deactivation_lifecycle (adoption) - addedToOrg / deactivatedOn lifecycle dates per user.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. MISSED BY RESEARCHER. Richest v2 user field set: mfaEnabled, claimStatus, membershipStatus, deactivatedOn, addedToOrg, platformRoles, jobTitle, department, location, timeZone.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/

### org-admin-user-role-assignments - Get user role assignments

- **Request line:** `GET https://api.atlassian.com/admin/admin/v2/orgs/{orgId}/directories/{directoryId}/users/{accountId}/role-assignments`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:directories:admin`
  - Auth notes: Org admin.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | directoryId | path | yes | Directory id | <directoryId> |
  | accountId | path | yes | Account id | <accountId> |
- **Datapoints returned:**
  - user_resource_roles (security) - Which products/resources a user can access and at what role.
  - product_access_attribution (cost) - User-to-product mapping for seat/cost attribution (partial v2 substitute for v1 product_access).
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Per-user role assignments across resources (which Jira sites/products and what role). PARTIAL v2 substitute for v1 product_access (resource->role, not access_billable).
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-users/

### org-admin-list-domains - Get domains in an organization

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/domains`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:domains:admin`
  - Auth notes: Org admin. Granular scope `read:domains:admin` confirmed.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
- **Datapoints returned:**
  - verified_domain_count (adoption) - Number of verified domains (managed-account governance footprint).
  - domain_claim_status (adoption) - Claim/verification status per domain.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Verified domains are the prerequisite that turns accounts into managed/billable accounts.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-domains/

### org-admin-get-domain - Get domain by ID

- **Request line:** `GET https://api.atlassian.com/admin/admin/v1/orgs/{orgId}/domains/{domainId}`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:domains:admin`
  - Auth notes: Org admin.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
  | domainId | path | yes | Domain id | <domainId> |
- **Datapoints returned:**
  - domain_detail (adoption) - Single domain verification detail.
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. Single verified-domain detail.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-domains/

### org-admin-list-workspaces - List workspaces (products) in an organization

- **Request line:** `POST https://api.atlassian.com/admin/admin/v2/orgs/{orgId}/workspaces`
- **Auth:** scheme `bearer` - Organization API key (Bearer).
  - Scopes: `read:workspaces:admin`
  - Auth notes: Org admin. Read-only despite POST verb (filters/sort/cursor in body). Scope `read:workspaces:admin` confirmed.
- **Response shape:** inline-json
- **Parameters:**

  | name | in | required | description | example |
  |------|----|----------|-------------|---------|
  | orgId | path | yes | Organization id | <orgId> |
- **Datapoints returned:**
  - provisioned_product_count (adoption) - Number of Jira (and other) product workspaces provisioned in the org.
  - product_inventory (cost) - Product type + hostUrl per workspace - basis for per-product licensing/cost rollup.
  - workspace_provisioning_date (adoption) - When each product was created (adoption timeline).
  - workspace_usage_capacity (cost) - Per-workspace usage/capacity metrics (storage/seat headroom).
- **Gotchas:** Min tier: org-admin. DIFFERENT host api.atlassian.com/admin + org API key. tryable:false - also POST SEARCH semantics (filters/sort/cursor in body), non-mutating. Canonical way to enumerate every product workspace (Jira sites) with hostUrl, typeKey, status, usage, capacity.
- **Tryable:** no. Not tested reason: Organizations admin API on a different host with an org API key, AND a POST with a JSON search body - not reachable by the site Basic-auth GET proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; path/datapoints/auth verified.
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/api-group-workspaces/

---

## Tier / Auth Matrix (cross-cutting pseudo-endpoints)

> These four are AUTH-SCHEME descriptors, not addressable paths - all `tryable:false`. The legacy JQL search is retained ONLY as a deprecation flag, and rate-limiting is the single cross-cutting reliability signal.

### auth-basic-email-token - Basic auth (Atlassian account email + API token)

- **Purpose:** Auth-scheme descriptor: the lowest-friction read path for `/rest/api/3` + `/rest/agile/1.0` site reads.
- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/* (auth scheme, not an endpoint)`
- **Auth:** scheme `basic-username` - Basic (Atlassian account email + API token). Credential: `Authorization: Basic base64(email:apiToken)`. Token from id.atlassian.com/manage/api-tokens.
  - Scopes: (none)
  - Auth notes: Acts as the authenticating user; that user's permissions constrain all reads. NOT valid for the Organizations admin API. API tokens do NOT use OAuth scopes.
- **Response shape:** inline-json
- **Datapoints returned:**
  - API access (any tier) (adoption) - Lowest-friction read path; available on every tier for the authenticating user's permitted data.
- **Gotchas:** Min tier: Free (all tiers). NOT a real endpoint - an auth-scheme descriptor for site reads. No tier gating on the scheme itself. Not valid for the org-admin API.
- **Tryable:** no. Not tested reason: Auth-scheme descriptor, not an addressable path - exercised implicitly by every Basic-auth site read.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Auth-scheme pseudo-endpoint."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/

### auth-oauth2-3lo-platform-read-scopes - OAuth 2.0 (3LO) READ scopes - platform

- **Purpose:** Auth-scheme descriptor: granular/classic OAuth scopes for platform (`/rest/api/3`) reads via `api.atlassian.com/ex/jira/{cloudid}`.
- **Request line:** `GET https://api.atlassian.com/ex/jira/{cloudid}/rest/api/3/* (auth scheme)`
- **Auth:** scheme `bearer` - OAuth 2.0 (3LO) access token.
  - Scopes: `read:jira-work`, `read:jira-user`, `read:issue:jira`, `read:comment:jira`, `read:issue-worklog:jira`, `read:issue.changelog:jira`, `read:project:jira`, `read:user:jira`, `read:audit-log:jira`, `offline_access`
  - Auth notes: Authorize at auth.atlassian.com/authorize; calls go to api.atlassian.com/ex/jira/{cloudid}. Classic `read:jira-work` + `read:jira-user` cover most platform reads. Always bounded by acting-user permissions. `read:audit-log:jira` only returns data on paid plans (Standard+).
- **Response shape:** inline-json
- **Datapoints returned:**
  - read:jira-work (activity-flow) - Read project/issue data, search issues, attachments, worklogs.
  - read:jira-user (adoption) - View user info (names, emails, avatars); PII-bearing.
- **Gotchas:** Min tier: Free (3LO works on all tiers). NOT a real endpoint - an OAuth-scope descriptor. OAuth host is `https://api.atlassian.com/ex/jira/{cloudid}` (different from the Basic per-site host). `read:audit-log:jira` returns data only on Standard+.
- **Tryable:** no. Not tested reason: Auth-scheme descriptor, not an addressable path - and the OAuth 3LO host/flow differs from the Basic-auth proxy.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Auth-scheme pseudo-endpoint."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/scopes-for-oauth-2-3LO-and-forge-apps/
  - https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/

### auth-oauth2-3lo-software-read-scopes - OAuth 2.0 (3LO) READ scopes - Jira Software / agile

- **Purpose:** Auth-scheme descriptor: mandatory granular `*:jira-software` scopes for `/rest/agile/1.0` reads.
- **Request line:** `GET https://api.atlassian.com/ex/jira/{cloudid}/rest/agile/1.0/* (auth scheme)`
- **Auth:** scheme `bearer` - OAuth 2.0 (3LO) access token.
  - Scopes: `read:board-scope:jira-software`, `read:sprint:jira-software`, `read:epic:jira-software`, `read:issue:jira-software`, `read:board-scope.admin:jira-software`
  - Auth notes: CONFIRMED: Jira Software does NOT support classic scopes; granular `*:jira-software` scopes are mandatory for `/rest/agile/1.0`. 'scope does not match' 401s stem from missing granular agile scopes.
- **Response shape:** inline-json
- **Datapoints returned:**
  - read:board-scope:jira-software (activity-flow) - View boards/backlogs for throughput and WIP metrics.
  - read:sprint:jira-software (delivery) - View sprints for velocity and sprint-completion metrics.
- **Gotchas:** Min tier: Standard (Jira Software; any plan where it is provisioned). NOT a real endpoint - an OAuth-scope descriptor. NO classic-scope support on `/rest/agile/1.0`.
- **Tryable:** no. Not tested reason: Auth-scheme descriptor, not an addressable path - OAuth 3LO host/flow differs from the Basic-auth proxy.
- **Plans:** Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Auth-scheme pseudo-endpoint."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/software/scopes-for-oauth-2-3LO-and-forge-apps/
  - https://developer.atlassian.com/cloud/jira/software/jira-software-rest-api-scopes/

### auth-org-api-key - Organizations admin API - Organization API key (Bearer)

- **Purpose:** Auth-scheme descriptor: the org API key path for `api.atlassian.com/admin` reads (seats, cost, audit).
- **Request line:** `GET https://api.atlassian.com/admin/v1/orgs/{orgId}/* (auth scheme)`
- **Auth:** scheme `bearer` - Organization API key (Bearer). Credential: `Authorization: Bearer <org-api-key>`. Org ID + key from admin.atlassian.com.
  - Scopes: (none)
  - Auth notes: CONFIRMED: API key as Bearer; requires Organization admin permission. Base URL `https://api.atlassian.com/admin`. Distinct from user API tokens / OAuth. Some directory/v2 and security-policy endpoints additionally require Atlassian Guard/Access.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Organization API key access (cost) - Org-level read access to managed accounts, product access and seats.
- **Gotchas:** Min tier: org-admin. NOT a real endpoint - an auth-scheme descriptor for the Organizations admin API on the DIFFERENT host api.atlassian.com/admin. Independent of Jira product tier.
- **Tryable:** no. Not tested reason: Auth-scheme descriptor on a different host (api.atlassian.com/admin) with a different credential (org API key) - not reachable by the site Basic-auth proxy.
- **Plans:** Org-admin API
- **Verification:** confidence high; note: "Auth-scheme pseudo-endpoint."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/admin/organization/rest/intro/

### search-legacy-deprecated - Search for issues using JQL (legacy, DEPRECATED/removed)

- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/search`
- **Auth:** scheme `basic-username` - Basic (email + API token).
  - Scopes: `read:jira-work`
  - Auth notes: CONFIRMED deprecated and being removed (offset startAt/maxResults/total). Migrate to `POST /rest/api/3/search/jql` + `/search/approximate-count`. Listed only to flag deprecation.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Legacy JQL search (activity-flow) - Deprecated offset-paginated search; superseded by `/search/jql`.
- **Gotchas:** Min tier: Free (all tiers). Scope: site. DEPRECATED/REMOVED - offset startAt/maxResults/total. Use `/search/jql` + `/search/approximate-count`. Retained only as a deprecation flag; do NOT build on it.
- **Tryable:** no. Not tested reason: Deprecated/removed offset search - superseded by `/search/jql`; retained only as a deprecation flag, not callable for new builds.
- **DEPRECATED / removed**
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Deprecation flag only; removed offset search."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
  - https://docs.adaptavist.com/sr4jc/latest/release-notes/breaking-changes/atlassian-rest-api-search-endpoints-deprecation

### rate-limiting-cost-budget - Rate limiting / cost budget (cross-cutting)

- **Purpose:** Points-based hourly budget + per-second burst + per-issue-write limits; operational reliability signal, not a product metric.
- **Request line:** `GET https://your-domain.atlassian.net/rest/api/3/* and /rest/agile/1.0/* (applies to all calls)`
- **Auth:** scheme `basic-username` - Basic (email + API token), OAuth 3LO, or org API key (applies to all).
  - Scopes: (none)
  - Auth notes: CONFIRMED points-based hourly budget + per-second burst + per-issue-write limits. Read cost = 1 base + per-object cost (issues/projects +1; users/groups +2). 429 on breach with NO gradual throttling. RateLimit-Reason values: jira-quota-global-based, jira-quota-tenant-based, jira-burst-based, jira-per-issue-on-write.
- **Response shape:** inline-json
- **Datapoints returned:**
  - Rate-limit headers (reliability) - Cost-budget signals (RateLimit-* / Retry-After) to pace polling; operational, not a product metric.
- **Rate limits:** Per-tenant points scale with tier+users: Standard ~100,000 + 10/user; Premium ~130,000 + 20/user; Enterprise ~150,000 + 30/user per hour (cap ~500,000). Global pool ~65,000/hr. Numbers indicative; may drift.
- **Gotchas:** Min tier: Free (cross-cutting - applies to all surfaces and credentials). NOT a real read endpoint: this is the rate-limit/cost-budget signal carried on every call's headers. The ONLY reliability-category signal Jira Cloud exposes (no uptime/SLA read API). 429 has no gradual throttle - pace paginated sweeps.
- **Tryable:** no. Not tested reason: Not an addressable endpoint - a cross-cutting rate-limit/cost-budget signal carried on every response's headers, not a callable path.
- **Plans:** Free, Standard, Premium, Enterprise
- **Verification:** confidence high; note: "Cross-cutting pseudo-endpoint; tier point budgets indicative."
- **Source URLs:**
  - https://developer.atlassian.com/cloud/jira/platform/rate-limiting/

---

## Unverified / Caveat Claims (from catalog `unverified[]`)

- **get-configuration** (`/rest/api/3/configuration`) - endpoint is current but the exact field set (timeTrackingEnabled removal nuance) is UNCONFIRMED; research marks it confidence=low / verified=false. Re-verify the response fields before relying on site feature flags.
- **bulk-fetch-changelogs** (`/rest/api/3/changelog/bulkfetch`) - flagged EXPERIMENTAL by Atlassian; schema/availability may change. Keep per-issue `/changelog` as a stable fallback.
- **Seat/cost v2 gap** - per-product product_access / last_active / access_billable come ONLY from the v1 org endpoints (org-get-users-v1, org-user-last-active-dates, org-get-managed-account-v1), all DEPRECATED and removed after 30 Jun 2026. v2 directory users does NOT return product_access; org-admin-user-role-assignments is only a partial (resource->role) substitute. No confirmed v2 successor for seat-waste/cost metrics - re-verify before the v1 sunset.
- **Site audit-log tier conflict** - jira-auditing-record-get carries the API's free min-tier, but the merged audit-records-tier-gated and Atlassian support docs say the effective gate is Standard+ (no audit log when ALL apps are Free). Treat the site audit log as Standard+.
- **Org audit-events coverage** - org-events-list / org-events-stream require Atlassian Guard (Standard/Premium) or Cloud Enterprise for FULL coverage (e.g. user_login) and are rate-limited to 10 req/min per user and per path; plain paid tiers see partial coverage.
- **Medium-confidence endpoints** (detail pages JS-rendered or corroborated indirectly): find-users-with-permissions, jira-workflow-search, jira-workflowscheme-project, jira-project-statuses, jira-notification-schemes-get, org-get-managed-account-v1 - usable but re-confirm scopes/fields.
- **Agile pagination** - random-access startAt pagination on `/rest/agile/1.0` is being removed after 2026-11-01; migrate agile reads to the enhanced token-paginated `/rest/software/1.0/*` variants. Agile tier is 'wherever Jira Software is provisioned' (incl. some Free) rather than a hard Standard gate.
- **Plan pricing** - exact per-seat Jira Cloud prices (Standard/Premium/Enterprise) are not printed in the research; the plans[] prices are left qualitative. Rate-limit point budgets per tier are indicative and may drift (Atlassian rate-limiting doc).
- **DORMANT / not live-verified** - every endpoint here is doc-grounded only; NO call was made against a real Jira site or org. Confirm against a live account (Basic email+token for site reads; org API key for the Organizations admin API) before registering this tool in index.ts.
