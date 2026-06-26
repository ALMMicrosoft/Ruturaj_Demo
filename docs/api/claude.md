# Claude (Anthropic) - API Endpoint Reference

> Anthropic's Admin API and Claude Code Analytics API expose per-user productivity metrics (sessions, lines of code, commits, PRs, tool accept/reject) plus token-level usage and USD cost reporting for any organization holding an Admin API key.

- **Vendor:** Anthropic
- **Docs:** https://platform.claude.com/docs/en/api/administration-api
- **Stage:** AI Assistants
- **Ingestion pattern:** Direct paginated JSON over Admin API; Claude Code Analytics is per-day; real-time per-user token/cost via client-side OpenTelemetry push
- **Auth model:** Most endpoints use `x-api-key` (an Admin key `sk-ant-admin...`) plus an `anthropic-version: 2023-06-01` header. The Enterprise Analytics API uses an `x-api-key` key carrying the `read:analytics` scope (created at claude.ai/analytics/api-keys by a Primary Owner). The Compliance API uses a Compliance Access Key (claude.ai) for the full suite, or a Console Admin key for the Activity Feed only.

## Feasibility verdict

- **Status:** feasible-with-caveats
- **Verdict:** FEASIBLE and strong — the Claude Code Analytics API delivers exactly the per-user productivity metrics a CTO dashboard wants (sessions, LOC added/removed, commits, PRs, tool accept/reject rates, per-model tokens and estimated cost), plus first-class Usage and Cost reporting for finance.
- **Required plan:** Requires an organization. An API/Console org (pay-as-you-go) gets the full Admin API + Claude Code Analytics API (free for orgs with Admin API access) via an Admin API key, plus the Compliance Activity Feed (read-only) when it is a member of an Enterprise parent org. Claude for Teams adds the claude.ai analytics dashboard with GitHub contribution metrics (public beta). Claude for Enterprise additionally unlocks two dedicated subscription APIs: the Enterprise Analytics API (9 endpoints, read:analytics scope, Primary Owner) and the full Compliance API (directory + content, via a Compliance Access Key). Individual accounts get none of it.
- **Blockers:**
  1. Admin API key (`sk-ant-admin...`) required, provisioned only by an org admin; standard keys do not work.
  2. Most Admin API endpoints (usage/cost/claude_code/org-info/users) are NOT available on Claude Platform on AWS, and Claude Code Analytics only covers the Claude API — not Bedrock/Vertex/Microsoft Foundry.
  3. Claude Code Analytics is single-day-per-request, ~1 hour latency, not real-time (use OpenTelemetry export for real-time per-user token+cost).
  4. `estimated_cost` is an analytics estimate, not billing.
  5. Contribution metrics (PRs/lines via GitHub) are public beta, claude.ai-org only, require GitHub app install + Owner enablement, and are unavailable under Zero Data Retention.
  6. Enterprise Analytics API requires an Enterprise subscription and a key with the `read:analytics` scope created by a Primary Owner at claude.ai/analytics/api-keys; not available to Individual, API/Console, or Team plans. Data latency ~4h (up to 24h), revisable for 30 days; some metrics unavailable under Zero Data Retention.
  7. Compliance API: the full suite (directory + content) needs a Compliance Access Key on an Enterprise org; a Console Admin key reaches the Activity Feed only and only inside an Enterprise parent org. Directory endpoints span all linked child orgs; content endpoints (chats/files/projects) are claude.ai-org-only. Shared rate limit 600 req/min per parent org.

## Plans / tiers

| Plan | Price | Tier | Unlocks APIs | Metrics access |
|---|---|---|---|---|
| Individual account (no organization) | - | individual | No | NONE of the Admin/metrics APIs. Docs state explicitly: "The Admin API is unavailable for individual accounts." To unlock, set up an organization in Console -> Settings -> Organization. No Admin API key can be provisioned. |
| API / Console Organization (pay-as-you-go with an org) | - | business | Yes | Full Admin API: Usage Report (messages), Cost Report, Organization users/invites/workspaces/workspace-members/API-keys, Organization Info (/me), Rate Limits API, Compliance/Activity Feed (read), and Claude Code Analytics API (`/v1/organizations/usage_report/claude_code`). Requires an Admin API key (`sk-ant-admin...`) provisioned by an org admin. Console Claude Code dashboard at platform.claude.com/claude-code shows usage + spend (no GitHub contribution metrics for API customers). Console dashboard access requires UsageView permission (Developer, Billing, Admin, Owner, Primary Owner roles). Claude Code Analytics API is free for all orgs with Admin API access. Compliance: a Console Admin key (`sk-ant-admin...`) reaches the Compliance Activity Feed (`GET /v1/compliance/activities`) ONLY — and only when this org is a member of an Enterprise parent org; the full Compliance suite (directory + content) and the Enterprise Analytics API require an Enterprise subscription. |
| Claude for Teams | - | team | No | unlocksApis:false because a Claude Team subscription on its own provisions NO API key. What Team gets is the Claude Code analytics dashboard at claude.ai/analytics/claude-code (Admins and Owners can view): usage metrics (lines accepted, suggestion accept rate, DAU, sessions) plus contribution metrics via GitHub integration (PRs/lines, leaderboard, CSV export; public beta, claude.ai-org only, GitHub app + Owner enablement, not under ZDR). The dedicated Enterprise Analytics API is Enterprise-only — Team does NOT get it. Team Claude Code usage CAN appear in the Claude Code Analytics API (`/v1/organizations/usage_report/claude_code`) tagged `customer_type='subscription'`, but ONLY when queried with a Console Admin key from a linked API/Console org — that key/API comes from the Console org, not from the Team plan, so it does not make Team itself API-bearing. Likewise a Team inside an Enterprise parent org can read the Compliance Activity Feed (`GET /v1/compliance/activities`) via a Console Admin key. Per-user token/cost otherwise requires OpenTelemetry export. |
| Claude for Enterprise | - | enterprise | Yes | Two dedicated subscription data APIs in addition to the claude.ai Claude Code analytics dashboard. (1) Enterprise Analytics API — 9 endpoints under `/v1/organizations/analytics/` (users, summaries, apps/chat/projects, skills, connectors, user_usage_report, user_cost_report, usage_report, cost_report). Auth: `x-api-key` key carrying the `read:analytics` scope, created at claude.ai/analytics/api-keys by a Primary Owner. Surfaces per-user USD cost (pre/post-discount; breakdown by product/model/region/cost-type/token-type), engagement (conversations, messages, projects, files, artifacts, shared items, thinking messages, skills, connectors), Claude Code metrics (commits, PRs, lines added/removed) and Cowork metrics. Data latency ~4h (up to 24h), revisable 30 days. (2) Compliance API — full suite under `/v1/compliance/*` via a Compliance Access Key (created in claude.ai): Activity Feed, organization/user/role/group directory endpoints (span all linked child orgs), and claude.ai-org content endpoints (chats/files/projects). A Console Admin key reaches the Activity Feed only. Shared rate limit 600 req/min per parent org. Plus the same Claude Code analytics dashboard as Teams (usage + GitHub contribution metrics, leaderboard, CSV export; contribution metrics public beta, not under ZDR) and OpenTelemetry export (centralized OTel config distributable via managed settings/MDM). |
| Any plan running the Claude Code CLI (self-serve OpenTelemetry) | - | - | No | OpenTelemetry export of metrics/events/traces is available to anyone running the Claude Code client; enabled with `CLAUDE_CODE_ENABLE_TELEMETRY=1`. No Anthropic plan tier gate stated for OTel itself (you export to your own backend). Traces are beta (`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`); detailed hook tracing requires org allowlisting for interactive CLI. |

> Pricing note: exact monetary prices of the Teams / Enterprise / Console plans are not stated in the official pages used for this catalog; only feature/metrics access by tier was documented.

---

## Endpoints (30)

| id | name | method | path | response shape | deprecated? |
|---|---|---|---|---|---|
| messages-usage-report | Get Messages Usage Report | GET | /v1/organizations/usage_report/messages | inline-json | No |
| cost-report | Get Cost Report | GET | /v1/organizations/cost_report | inline-json | No |
| claude-code-usage-report | Get Claude Code Usage Report (Claude Code Analytics API) | GET | /v1/organizations/usage_report/claude_code | inline-json | No |
| organization-me | Get Organization Info | GET | /v1/organizations/me | inline-json | No |
| list-users | List Organization Members (Users) | GET | /v1/organizations/users | inline-json | No |
| list-api-keys | List API Keys (Admin) | GET | /v1/organizations/api_keys | inline-json | No |
| list-workspaces | List Workspaces | GET | /v1/organizations/workspaces | inline-json | No |
| claude-code-otel-export | Claude Code OpenTelemetry export (client-side push) | POST | OTEL_EXPORTER_OTLP_ENDPOINT (/v1/metrics, /v1/logs, /v1/traces) | inline-json | No |
| claude-code-analytics-dashboard | Claude Code Analytics Dashboard (Team/Enterprise + GitHub contribution metrics) | GET | claude.ai/analytics/claude-code ; platform.claude.com/claude-code | inline-json | No |
| enterprise-analytics-users | Enterprise Analytics — User Activity | GET | /v1/organizations/analytics/users | inline-json | No |
| enterprise-analytics-summaries | Enterprise Analytics — Activity Summaries | GET | /v1/organizations/analytics/summaries | inline-json | No |
| enterprise-analytics-chat-projects | Enterprise Analytics — Chat Projects | GET | /v1/organizations/analytics/apps/chat/projects | inline-json | No |
| enterprise-analytics-skills | Enterprise Analytics — Skills Usage | GET | /v1/organizations/analytics/skills | inline-json | No |
| enterprise-analytics-connectors | Enterprise Analytics — Connectors Usage | GET | /v1/organizations/analytics/connectors | inline-json | No |
| enterprise-analytics-user-usage-report | Enterprise Analytics — Per-User Usage Report | GET | /v1/organizations/analytics/user_usage_report | inline-json | No |
| enterprise-analytics-user-cost-report | Enterprise Analytics — Per-User Cost Report | GET | /v1/organizations/analytics/user_cost_report | inline-json | No |
| enterprise-analytics-usage-report | Enterprise Analytics — Usage Report (time series) | GET | /v1/organizations/analytics/usage_report | inline-json | No |
| enterprise-analytics-cost-report | Enterprise Analytics — Cost Report (time series) | GET | /v1/organizations/analytics/cost_report | inline-json | No |
| compliance-activities | Compliance — Activity Feed | GET | /v1/compliance/activities | inline-json | No |
| compliance-organizations | Compliance — List Organizations | GET | /v1/compliance/organizations | inline-json | No |
| compliance-organization | Compliance — Get Organization | GET | /v1/compliance/organizations/{org_uuid} | inline-json | No |
| compliance-organization-users | Compliance — List Org Users | GET | /v1/compliance/organizations/{org_uuid}/users | inline-json | No |
| compliance-organization-user | Compliance — Get Org User | GET | /v1/compliance/organizations/{org_uuid}/users/{user_uuid} | inline-json | No |
| compliance-organization-roles | Compliance — List Roles | GET | /v1/compliance/organizations/{org_uuid}/roles | inline-json | No |
| compliance-organization-groups | Compliance — List Groups | GET | /v1/compliance/organizations/{org_uuid}/groups | inline-json | No |
| compliance-chats | Compliance — List Chats | GET | /v1/compliance/chats | inline-json | No |
| compliance-chat | Compliance — Get Chat | GET | /v1/compliance/chats/{chat_id} | inline-json | No |
| compliance-files | Compliance — List Files | GET | /v1/compliance/files | inline-json | No |
| compliance-file | Compliance — Get File | GET | /v1/compliance/files/{file_id} | inline-json | No |
| compliance-projects | Compliance — List Projects | GET | /v1/compliance/projects | inline-json | No |

> Note: all 30 endpoints are enumerated individually below — the 7 Admin/Console surfaces (messages usage, cost, claude_code, org-me, users, api_keys, workspaces), the OTel export and the analytics dashboard, the 9 Enterprise Analytics endpoints, and the Compliance suite (Activity Feed + 6 directory + 5 content endpoints).

---

### messages-usage-report - Get Messages Usage Report

**Purpose:** Programmatic, granular token-usage tracking across the organization, with breakdowns/filters by model, workspace, API key, account, service tier, context window, inference geo, and speed (fast mode). Mirrors the Console Usage page.

**Request:** `GET https://api.anthropic.com/v1/organizations/usage_report/messages`

**Auth:** `x-api-key` scheme — Admin API key (`sk-ant-admin...`). Provisioned only by org members with admin role via Console (`/settings/admin-keys`). Standard API keys do NOT work. Not available on Claude Platform on AWS (use Console Usage page instead).

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $ANTHROPIC_ADMIN_KEY (sk-ant-admin...) | Yes |
| anthropic-version | 2023-06-01 | Yes |
| anthropic-beta | fast-mode-2026-02-01 (only when using speed group_by / speeds[] filter) | No |
| User-Agent | YourApp/1.0.0 (https://yourapp.com) — recommended for integrations | No |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_at | query | Yes | RFC 3339 timestamp; buckets starting on/after this time are returned. Snapped to start of minute/hour/day UTC. |
| ending_at | query | No | RFC 3339 timestamp; buckets ending before this are returned. |
| bucket_width | query | No | Time granularity: '1m', '1h', or '1d' (default 1d). |
| group_by[] | query | No | Any subset of: api_key_id, workspace_id, model, service_tier, context_window, inference_geo, speed, account_id, service_account_id. 'speed' requires fast-mode-2026-02-01 beta header. |
| models[] | query | No | Filter to specific model(s). |
| api_key_ids[] | query | No | Filter to specific API key ID(s). |
| workspace_ids[] | query | No | Filter to specific workspace ID(s). |
| account_ids[] | query | No | Filter to specific user account ID(s). |
| service_account_ids[] | query | No | Filter to specific service account ID(s). |
| service_tiers[] | query | No | Filter: standard, batch, priority, priority_on_demand, flex, flex_discount. |
| context_window[] | query | No | Filter: '0-200k' or '200k-1M'. |
| inference_geos[] | query | No | Filter: global, us, or not_available. |
| speeds[] | query | No | Filter: standard or fast (research preview). Requires fast-mode-2026-02-01 beta header. |
| limit | query | No | Max time buckets. 1d: default 7 / max 31; 1h: default 24 / max 168; 1m: default 60 / max 1440. |
| page | query | No | next_page token from previous response for pagination. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| uncached_input_tokens | cost | Uncached input tokens processed. |
| cache_creation.ephemeral_1h_input_tokens | cost | Input tokens used to create the 1-hour cache entry. |
| cache_creation.ephemeral_5m_input_tokens | cost | Input tokens used to create the 5-minute cache entry. |
| cache_read_input_tokens | cost | Input tokens read from cache. |
| output_tokens | cost | Output tokens generated. |
| server_tool_use.web_search_requests | engagement | Number of web search (server tool) requests. |
| model | adoption | Model used (null unless grouping by model). |
| workspace_id | adoption | Workspace used (null if default workspace or not grouped). |
| api_key_id | adoption | API key used (null for Console/Workbench usage or not grouped). |
| account_id | engagement | User account that made the request (null for non-OAuth or not grouped). |
| service_account_id | adoption | Service account (null for non-OIDC-federation or not grouped). |
| service_tier | cost | standard/batch/priority/priority_on_demand/flex/flex_discount (null if not grouped). |
| context_window | cost | 0-200k or 200k-1M (null if not grouped). |
| inference_geo | quality | global/us/not_available; geographic routing (data residency). |
| starting_at / ending_at | engagement | Time bucket boundaries (RFC 3339). |

**Rate limits:** Polling supported once per minute for sustained use; short bursts (paginated downloads) allowed more frequently. Cache results for dashboards.

**Gotchas:** Data latency ~5 min after request completion (occasionally longer). Workbench usage has api_key_id=null. Default workspace has workspace_id=null. Models before Feb 2026 (pre Opus 4.6/Sonnet 4.6) return inference_geo='not_available'. Code execution usage is NOT in this endpoint (cost endpoint only). Priority Tier costs tracked here (usage), not in cost endpoint.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at=2025-01-01T00:00:00Z&ending_at=2025-01-08T00:00:00Z&group_by[]=model&bucket_width=1d" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

**Example response:**

```json
{
  "data": [{
    "starting_at": "2025-08-01T00:00:00Z",
    "ending_at": "2025-08-02T00:00:00Z",
    "results": [{
      "account_id": "user_01WCz1FkmYMm4gnmykNKUu3Q",
      "api_key_id": "apikey_01Rj2N8SVvo6BePZj99NhmiT",
      "cache_creation": {"ephemeral_1h_input_tokens": 1000, "ephemeral_5m_input_tokens": 500},
      "cache_read_input_tokens": 200,
      "context_window": "0-200k",
      "inference_geo": "global",
      "model": "claude-opus-4-6",
      "output_tokens": 500,
      "server_tool_use": {"web_search_requests": 10},
      "service_tier": "standard",
      "uncached_input_tokens": 1500,
      "workspace_id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"
    }]
  }],
  "has_more": true,
  "next_page": "page_xyz..."
}
```

**Plans/tiers:** Org API

**Tryable:** Yes

**Live check:** HTTP 200 on 2026-06-03 — Anthropic org (admin-key verified).

**Verification:** confidence high; path/method/auth/datapoints all verified. Path, method, auth, all group_by options, filters, enums and limit defaults verified verbatim against official docs. Datapoint categories are this catalog's taxonomy, not Anthropic labels. Source: https://platform.claude.com/docs/en/api/admin-api/usage-cost/get-messages-usage-report

**Source URLs:**
- https://platform.claude.com/docs/en/api/usage-cost-api
- https://platform.claude.com/docs/en/api/admin-api/usage-cost/get-messages-usage-report

---

### cost-report - Get Cost Report

**Purpose:** Service-level cost breakdowns in USD for finance/chargeback reconciliation, grouped by workspace and/or description. Mirrors the Console Cost page.

**Request:** `GET https://api.anthropic.com/v1/organizations/cost_report`

**Auth:** `x-api-key` scheme — Admin API key (`sk-ant-admin...`). Admin role required. Not available on Claude Platform on AWS.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $ANTHROPIC_ADMIN_KEY | Yes |
| anthropic-version | 2023-06-01 | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_at | query | Yes | RFC 3339 timestamp; snapped to UTC day. |
| ending_at | query | No | RFC 3339 end bound. |
| bucket_width | query | No | Daily granularity only ('1d'). |
| group_by[] | query | No | Subset of: workspace_id, description. Grouping by description adds parsed model/inference_geo/service_tier/token_type fields. |
| limit | query | No | Max time buckets. |
| page | query | No | next_page token for pagination. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| amount | cost | Cost in lowest currency units as a decimal string, e.g. '123.78912'. |
| currency | cost | Currency code, currently always 'USD'. |
| cost_type | cost | tokens, web_search, code_execution, or session_usage (null if not grouping by description). |
| description | cost | Cost item description, e.g. 'Claude Sonnet 4 Usage - Input Tokens', 'Code Execution Usage' (null if not grouped). |
| token_type | cost | uncached_input_tokens, output_tokens, cache_read_input_tokens, cache_creation.ephemeral_1h_input_tokens, cache_creation.ephemeral_5m_input_tokens. |
| model | cost | Model name (null for non-token costs or not grouped). |
| service_tier | cost | standard or batch (null for non-token costs / not grouped). |
| context_window | cost | 0-200k or 200k-1M (null for non-token costs). |
| inference_geo | quality | global/us/not_available (null if not grouping by inference geo). |
| workspace_id | adoption | Workspace the cost is attributed to (null for default workspace / not grouped). |

**Rate limits:** Same as Usage API: ~1 poll/minute sustained.

**Gotchas:** Daily granularity only. Priority Tier costs use a different billing model and are NOT included here (track via Usage endpoint service_tier=priority). Code execution costs appear here under 'Code Execution Usage' description (not in Usage endpoint). Default workspace = null workspace_id. For per-user Claude Code cost, use Claude Code Analytics API instead.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/cost_report?starting_at=2025-01-01T00:00:00Z&ending_at=2025-01-31T00:00:00Z&group_by[]=workspace_id&group_by[]=description" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

**Example response:**

```json
{
  "data": [{
    "starting_at": "2025-08-01T00:00:00Z",
    "ending_at": "2025-08-02T00:00:00Z",
    "results": [{
      "amount": "123.78912",
      "context_window": "0-200k",
      "cost_type": "tokens",
      "currency": "USD",
      "description": "Claude Sonnet 4 Usage - Input Tokens",
      "inference_geo": "global",
      "model": "claude-opus-4-6",
      "service_tier": "standard",
      "token_type": "uncached_input_tokens",
      "workspace_id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"
    }]
  }],
  "has_more": true,
  "next_page": "page_xyz..."
}
```

**Plans/tiers:** Org API

**Tryable:** Yes

**Live check:** HTTP 200 on 2026-06-03 — Anthropic org (admin-key verified).

**Verification:** confidence high; path/method/auth/datapoints all verified. Path, method, auth, query params and all 10 datapoints verified against official docs. 'amount' is a decimal string in lowest currency units (not necessarily whole cents). Source: https://platform.claude.com/docs/en/api/admin-api/usage-cost/get-cost-report

**Source URLs:**
- https://platform.claude.com/docs/en/api/usage-cost-api
- https://platform.claude.com/docs/en/api/admin-api/usage-cost/get-cost-report

---

### claude-code-usage-report - Get Claude Code Usage Report (Claude Code Analytics API)

**Purpose:** Daily aggregated, per-user Claude Code productivity metrics: sessions, lines added/removed, commits, PRs, tool accept/reject rates, and per-model token/estimated-cost. Bridges the basic dashboard and full OTel integration.

**Request:** `GET https://api.anthropic.com/v1/organizations/usage_report/claude_code`

**Auth:** `x-api-key` scheme — Admin API key (`sk-ant-admin...`), provisioned by org admin via `/settings/admin-keys`. Free to use for all orgs with Admin API access. Only tracks Claude Code usage on the Claude API — NOT Bedrock, Vertex, Microsoft Foundry, or Claude Platform on AWS.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $ADMIN_API_KEY (sk-ant-admin...) | Yes |
| anthropic-version | 2023-06-01 | Yes |
| User-Agent | YourApp/1.0.0 (https://yourapp.com) — recommended | No |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_at | query | Yes | UTC date YYYY-MM-DD; returns metrics for this SINGLE day only (UTC midnight). |
| limit | query | No | Records per page; default 20, max 1000. |
| page | query | No | Opaque cursor token from previous response next_page (cursor-based, stable pagination). |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| date | engagement | Day in RFC 3339 (UTC). |
| actor (user_actor.email_address / api_actor.api_key_name) | adoption | User (OAuth email) or API key name performing actions. |
| organization_id | adoption | Organization UUID. |
| customer_type | adoption | 'api' (pay-as-you-go) or 'subscription' (Pro/Team). |
| terminal_type | adoption | Terminal/env, e.g. vscode, iTerm.app, tmux. |
| core_metrics.num_sessions | engagement | Distinct Claude Code sessions by this actor. |
| core_metrics.lines_of_code.added | activity-flow | Lines of code added by Claude Code. |
| core_metrics.lines_of_code.removed | activity-flow | Lines of code removed by Claude Code. |
| core_metrics.commits_by_claude_code | activity-flow | Git commits created via Claude Code. |
| core_metrics.pull_requests_by_claude_code | activity-flow | Pull requests created via Claude Code. |
| tool_actions.edit_tool.accepted/rejected | quality | Edit tool proposals accepted/rejected. |
| tool_actions.multi_edit_tool.accepted/rejected | quality | MultiEdit tool proposals accepted/rejected. |
| tool_actions.write_tool.accepted/rejected | quality | Write tool proposals accepted/rejected. |
| tool_actions.notebook_edit_tool.accepted/rejected | quality | NotebookEdit tool proposals accepted/rejected (acceptance rate = accepted/(accepted+rejected)). |
| model_breakdown[].model | adoption | Claude model identifier, e.g. claude-opus-4-8. |
| model_breakdown[].tokens.input/output/cache_read/cache_creation | cost | Per-model token counts. |
| model_breakdown[].estimated_cost.amount | cost | Estimated cost in cents USD for this model. |
| model_breakdown[].estimated_cost.currency | cost | Currency, always USD. |

**Rate limits:** Not numerically specified in docs beyond Admin-API guidance; daily aggregated data only.

**Gotchas:** Single-day only per request (starting_at = one UTC day). Data latency up to ~1 hour; only data older than 1 hour is returned to ensure stable pagination. NOT real-time (use OTel for real-time). estimated_cost is an estimate for analytics, not billing. Cost amounts in cents. Only covers Claude API deployments (not Bedrock/Vertex/Foundry/AWS). An optional subscription_type field (enterprise/team) also exists alongside customer_type.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/claude_code?starting_at=2025-09-08&limit=20" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ADMIN_API_KEY"
```

**Example response:**

```json
{
  "data": [{
    "date": "2025-09-08T00:00:00Z",
    "actor": {"type": "user_actor", "email_address": "developer@company.com"},
    "organization_id": "dc9f6c26-b22c-4831-8d01-0446bada88f1",
    "customer_type": "api",
    "terminal_type": "vscode",
    "core_metrics": {
      "num_sessions": 5,
      "lines_of_code": {"added": 1543, "removed": 892},
      "commits_by_claude_code": 12,
      "pull_requests_by_claude_code": 2
    },
    "tool_actions": {
      "edit_tool": {"accepted": 45, "rejected": 5},
      "multi_edit_tool": {"accepted": 12, "rejected": 2},
      "write_tool": {"accepted": 8, "rejected": 1},
      "notebook_edit_tool": {"accepted": 3, "rejected": 0}
    },
    "model_breakdown": [{
      "model": "claude-opus-4-8",
      "tokens": {"input": 100000, "output": 35000, "cache_read": 10000, "cache_creation": 5000},
      "estimated_cost": {"currency": "USD", "amount": 1025}
    }]
  }],
  "has_more": false,
  "next_page": null
}
```

**Plans/tiers:** Org API

**Tryable:** Yes

**Live check:** HTTP 200 on 2026-06-03 — Anthropic org (admin-key verified). Note: Verified live on day 2026-05-29 (single-day API). For the tested 28-day window the Messages Usage and Cost reports returned empty results — this org's activity is via Claude Code.

**Verification:** confidence high; path/method/auth/datapoints all verified. Only gap: the optional subscription_type field (enterprise/team) is documented but not enumerated here. date field format varies (YYYY-MM-DD vs RFC 3339) in Anthropic's own docs. Source: https://platform.claude.com/docs/en/api/admin-api/claude-code/get-claude-code-usage-report

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api
- https://platform.claude.com/docs/en/api/admin-api/claude-code/get-claude-code-usage-report

---

### organization-me - Get Organization Info

**Purpose:** Identify which organization an Admin API key belongs to (org id/name/type).

**Request:** `GET https://api.anthropic.com/v1/organizations/me`

**Auth:** `x-api-key` scheme — Admin API key (`sk-ant-admin...`). Admin role.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $ANTHROPIC_ADMIN_KEY | Yes |
| anthropic-version | 2023-06-01 | Yes |

**Parameters:** none.

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| id | adoption | Organization UUID. |
| type | adoption | Always 'organization'. |
| name | adoption | Organization name. |

**Rate limits:** Not specified.

**Gotchas:** Org info is not listed among the endpoints available on Claude Platform on AWS, so it is effectively unavailable there.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/me" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

**Example response:**

```json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "type": "organization",
  "name": "Organization Name"
}
```

**Plans/tiers:** Org API

**Tryable:** Yes

**Live check:** HTTP 200 on 2026-06-03 — Anthropic org (admin-key verified).

**Verification:** confidence high; path/method/auth/datapoints all verified. Path, GET method, x-api-key Admin auth and the { id, name, type } response object all confirmed verbatim against official docs. Source: https://platform.claude.com/docs/en/api/admin-api/organization/get-me

**Source URLs:**
- https://platform.claude.com/docs/en/api/administration-api
- https://platform.claude.com/docs/en/api/admin-api/organization/get-me

---

### list-users - List Organization Members (Users)

**Purpose:** List org members and their roles; supports seat/adoption auditing and onboarding/offboarding automation.

**Request:** `GET https://api.anthropic.com/v1/organizations/users`

**Auth:** `x-api-key` scheme — Admin API key (`sk-ant-admin...`). Admin role required. Org admins cannot be removed via API. Not available on Claude Platform on AWS.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $ANTHROPIC_ADMIN_KEY | Yes |
| anthropic-version | 2023-06-01 | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| limit | query | No | Page size (default 20, range 1-1000). |
| email | query | No | Filter by member email. |
| after_id | query | No | Cursor: return results after this user id. |
| before_id | query | No | Cursor: return results before this user id. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| user id | adoption | Org member identifier (user_...). |
| role | adoption | One of: user, claude_code_user, developer, billing, admin. |

**Rate limits:** Not specified.

**Gotchas:** Related endpoints: GET /v1/organizations/users/{user_id}, POST to update role, DELETE to remove a member. The 'claude_code_user' role grants Workbench + Claude Code.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/users?limit=10" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

**Example response:**

```json
{
  "data": [
    {
      "id": "user_xxx",
      "type": "user",
      "email": "developer@company.com",
      "name": "Dev Eloper",
      "role": "developer",
      "added_at": "2025-01-15T00:00:00Z"
    }
  ],
  "has_more": false,
  "first_id": "user_xxx",
  "last_id": "user_xxx"
}
```

**Plans/tiers:** Org API

**Tryable:** Yes

**Live check:** HTTP 200 on 2026-06-03 — Anthropic org (admin-key verified).

**Verification:** confidence high; path/method/auth/datapoints all verified. Path, GET method, x-api-key Admin auth and id/role datapoints confirmed. Docs also document after_id/before_id/email params and added_at/email/name/type per-user fields. Source: https://platform.claude.com/docs/en/api/admin-api/users/list-users

**Source URLs:**
- https://platform.claude.com/docs/en/api/administration-api
- https://platform.claude.com/docs/en/api/admin-api/users/list-users

---

### list-api-keys - List API Keys (Admin)

**Purpose:** Enumerate org API keys to resolve api_key_ids used in the Usage report and to manage (activate/deactivate/rename) keys.

**Request:** `GET https://api.anthropic.com/v1/organizations/api_keys`

**Auth:** `x-api-key` scheme — Admin API key (`sk-ant-admin...`). Admin role. New keys cannot be created via API (Console only). Not available on Claude Platform on AWS.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $ANTHROPIC_ADMIN_KEY | Yes |
| anthropic-version | 2023-06-01 | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| limit | query | No | Page size (default 20, range 1-1000). |
| status | query | No | Filter: active, inactive, archived, expired. |
| workspace_id | query | No | Filter by workspace. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| api_key id | adoption | API key ID (apikey_...) — input to Usage report api_key_ids[]. |
| status | adoption | active/inactive/archived/expired. |
| name | adoption | Key name. |
| workspace_id | adoption | Owning workspace (null for default workspace). |

**Rate limits:** Not specified.

**Gotchas:** Update via POST /v1/organizations/api_keys/{api_key_id} (status/name). Keys are org-scoped and persist when a user is removed.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/api_keys?limit=10&status=active&workspace_id=wrkspc_xxx" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

**Example response:**

```json
{
  "data": [
    {
      "id": "apikey_01Rj2N8SVvo6BePZj99NhmiT",
      "type": "api_key",
      "name": "Production key",
      "status": "active",
      "workspace_id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
      "partial_key_hint": "sk-ant-...AAAA",
      "created_at": "2025-01-15T00:00:00Z"
    }
  ],
  "has_more": false,
  "first_id": "apikey_01Rj2N8SVvo6BePZj99NhmiT",
  "last_id": "apikey_01Rj2N8SVvo6BePZj99NhmiT"
}
```

**Plans/tiers:** Org API

**Tryable:** Yes

**Live check:** HTTP 200 on 2026-06-03 — Anthropic org (admin-key verified).

**Verification:** confidence high; path/method/auth/datapoints all verified. Path, GET method, x-api-key Admin auth and id/status/name/workspace_id datapoints confirmed. status enum is active/inactive/archived/expired; cursor pagination (after_id/before_id, first_id/last_id/has_more). Source: https://platform.claude.com/docs/en/api/admin-api/apikeys/list-api-keys

**Source URLs:**
- https://platform.claude.com/docs/en/api/administration-api
- https://platform.claude.com/docs/en/api/admin-api/apikeys/list-api-keys

---

### list-workspaces - List Workspaces

**Purpose:** Enumerate workspaces to resolve workspace_ids used in Usage/Cost reports and manage workspace lifecycle.

**Request:** `GET https://api.anthropic.com/v1/organizations/workspaces`

**Auth:** `x-api-key` scheme — Admin API key (`sk-ant-admin...`). Admin role. Workspace endpoints (create/get/list/update/archive) ARE available on Claude Platform on AWS.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $ANTHROPIC_ADMIN_KEY | Yes |
| anthropic-version | 2023-06-01 | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| limit | query | No | Page size (default 20, range 1-1000). |
| include_archived | query | No | Whether to include archived workspaces. |
| after_id | query | No | Cursor: return results after this workspace id. |
| before_id | query | No | Cursor: return results before this workspace id. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| workspace id | adoption | Workspace ID (wrkspc_...) — input to Usage/Cost report workspace_ids[]. |
| name | adoption | Workspace name. |

**Rate limits:** Not specified.

**Gotchas:** Companion endpoints: workspace members (GET/POST/DELETE /v1/organizations/workspaces/{workspace_id}/members[/{user_id}]) with workspace_role (workspace_developer, workspace_admin, etc.).

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/workspaces?limit=10" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

**Example response:**

```json
{
  "data": [
    {
      "id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
      "type": "workspace",
      "name": "Engineering",
      "created_at": "2025-01-15T00:00:00Z",
      "archived_at": null
    }
  ],
  "has_more": false,
  "first_id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
  "last_id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"
}
```

**Plans/tiers:** Org API

**Tryable:** Yes

**Live check:** HTTP 200 on 2026-06-03 — Anthropic org (admin-key verified).

**Verification:** confidence high; path/method/auth/datapoints all verified. Path, GET method, x-api-key Admin auth and id/name datapoints confirmed; richer schema (type/created_at/archived_at/data_residency/tags) and after_id/before_id/include_archived params also documented. Workspace endpoints are explicitly available on Claude Platform on AWS. Source: https://platform.claude.com/docs/en/api/admin-api/workspaces/list-workspaces

**Source URLs:**
- https://platform.claude.com/docs/en/api/administration-api
- https://platform.claude.com/docs/en/api/admin-api/workspaces/list-workspaces

---

### claude-code-otel-export - Claude Code OpenTelemetry export (client-side push)

**Purpose:** Real-time per-session/per-user metrics, events, and (beta) traces from the Claude Code client, exported to your observability stack (Prometheus, Datadog, Honeycomb, Grafana, etc.).

**Request:** `POST <Your own OpenTelemetry collector / backend>` at `OTEL_EXPORTER_OTLP_ENDPOINT` (e.g. http://localhost:4317; /v1/metrics, /v1/logs, /v1/traces)

**Auth:** `x-api-key` scheme (schema-completeness only) — Bearer / mTLS to YOUR collector (not an Anthropic credential). `OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"`; or dynamic headers via otelHeadersHelper; mTLS via CLAUDE_CODE_CLIENT_CERT/KEY (http) or OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE/KEY (grpc). No Anthropic credential is used — this is a client-side OTLP push to your own collector. Enable with `CLAUDE_CODE_ENABLE_TELEMETRY=1`. `OTEL_METRICS_EXPORTER=otlp|prometheus|console|none`; `OTEL_LOGS_EXPORTER=otlp|console|none`. Default metric export 60s, logs 5s. Traces are beta (`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`).

**Headers:**

| Name | Value | Required |
|---|---|---|
| OTEL_EXPORTER_OTLP_HEADERS | Authorization=Bearer <token> (env var, not an HTTP header per se) | No |

**Parameters** (these are environment variables, not HTTP params):

| Name | In | Required | Description |
|---|---|---|---|
| OTEL_METRICS_INCLUDE_SESSION_ID | header | No | Cardinality control, set as an environment variable (default true). |
| OTEL_METRICS_INCLUDE_ACCOUNT_UUID | header | No | Include user.account_uuid/account_id, set as an environment variable (default true). |
| OTEL_METRICS_INCLUDE_VERSION | header | No | Include app.version, set as an environment variable (default false). |
| OTEL_METRICS_INCLUDE_ENTRYPOINT | header | No | Include app.entrypoint, set as an environment variable (default false). |
| OTEL_RESOURCE_ATTRIBUTES | header | No | Custom team/dept/cost_center attributes (no spaces), set as an environment variable. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| claude_code.session.count | engagement | CLI sessions started; attr start_type (fresh/resume/continue). |
| claude_code.active_time.total | engagement | Active time in seconds; attr type=user\|cli. |
| claude_code.lines_of_code.count | activity-flow | Lines modified; attr type=added\|removed. |
| claude_code.commit.count | activity-flow | Git commits created via Claude Code. |
| claude_code.pull_request.count | activity-flow | PRs/MRs created via shell or MCP tool. |
| claude_code.code_edit_tool.decision | quality | Code edit tool permission decisions; attrs tool_name (Edit/Write/NotebookEdit), decision (accept/reject), source, language. |
| claude_code.cost.usage | cost | Cost (USD) per API request; attrs model, query_source, speed, effort, agent/skill/plugin/mcp attribution. |
| claude_code.token.usage | cost | Tokens; attr type=input\|output\|cacheRead\|cacheCreation, model, query_source, speed, effort. |
| claude_code.user_prompt (event) | engagement | User prompt submitted; prompt_length, prompt (redacted by default), command_name/source. |
| claude_code.api_request (event) | cost | Per API request: model, cost_usd, duration_ms, input/output/cache tokens, request_id, speed, effort. |
| claude_code.tool_result / tool_decision (events) | quality | Tool execution outcome and accept/reject decisions with source and parameters. |
| claude_code.api_error (event) | quality | Failed API request: error, status_code, attempts. |

**Rate limits:** Client push at configured intervals (default metrics 60s, logs 5s, traces 5s). No Anthropic-side pull rate limit.

**Gotchas:** Push model (you host the backend), not a queryable Anthropic API. Default metrics temporality is delta (set OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=cumulative if needed). prompt.id is on events only, never metrics (cardinality). Traces beta; detailed hook tracing requires org allowlist for interactive CLI. OTEL_* vars are NOT passed to subprocesses (Bash, hooks, MCP).

**Example request:**

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1; export OTEL_METRICS_EXPORTER=otlp; export OTEL_LOGS_EXPORTER=otlp; export OTEL_EXPORTER_OTLP_PROTOCOL=grpc; export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317; export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"; claude
```

**Example response:**

```
(No HTTP JSON response — emits OTLP metric data points / log records. e.g. metric claude_code.token.usage{type="output",model="claude-sonnet-4-6",session.id=...} = 35000)
```

**Plans/tiers:** Free, Org API, Team, Enterprise, OTel (any plan)

**Tryable:** No

**Verification:** confidence high; path/method/auth/datapoints all verified. All metrics/events, auth mechanisms, cardinality controls and default intervals confirmed against official docs. Correctly characterized as a client-side OTLP push, not a queryable Anthropic HTTP pull API; the listed OTEL_* 'params' are environment variables, not HTTP headers. Source: https://code.claude.com/docs/en/monitoring-usage

**Source URLs:**
- https://code.claude.com/docs/en/monitoring-usage

---

### claude-code-analytics-dashboard - Claude Code Analytics Dashboard (Team/Enterprise + GitHub contribution metrics)

**Purpose:** No-code dashboard for adoption, acceptance, contribution (PRs/lines with Claude Code via GitHub), leaderboard, and spend; programmatic access of contribution data is via GitHub label search, not an Anthropic endpoint. Enterprise now also unlocks the dedicated Enterprise Analytics API (9 endpoints) and Compliance API in addition to this dashboard.

**Request:** `GET https://claude.ai / https://platform.claude.com` — `claude.ai/analytics/claude-code` (Team/Enterprise) ; `platform.claude.com/claude-code` (API/Console)

**Auth:** `x-api-key` scheme (schema-completeness only) — UI role-based (no API key). Team/Enterprise: Admin or Owner views; contribution metrics require Owner to enable + GitHub admin to install github.com/apps/claude. API/Console: UsageView permission (Developer, Billing, Admin, Owner, Primary Owner). Not a public REST API — this is a UI dashboard. Contribution metrics are public beta and cover only users in your claude.ai org (not Console API / third-party integrations). Not available with Zero Data Retention.

**Headers:** none.

**Parameters:** none.

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| Lines of code accepted | activity-flow | Total lines written by Claude Code that users accepted (excludes rejected; not net of later deletions). |
| Suggestion accept rate | quality | % of Edit/Write/NotebookEdit suggestions accepted. |
| Daily active users / sessions | engagement | DAU and active sessions per day. |
| PRs with CC / Lines of code with CC | activity-flow | Merged PRs and effective lines attributed to Claude Code via GitHub integration (conservative matching). |
| PRs with Claude Code (%) | activity-flow | Share of merged PRs containing Claude-Code-assisted code. |
| PRs per user | activity-flow | Merged PRs/day divided by DAU. |
| Leaderboard (top 10 contributors) | engagement | Top users by PRs or lines with vs without Claude Code; CSV export of ALL users. |
| Spend / Spend this month (Console) | cost | Daily API cost + per-user spend this month (estimates). |
| Lines this month (Console per-user) | activity-flow | Per-user accepted lines for the current month. |

**Rate limits:** N/A (UI).

**Gotchas:** Contribution data appears ~24h after enabling, daily updates. PR attribution time window: 21 days before to 2 days after merge. Excludes lock/generated/build/test-fixture files and lines >1000 chars. Code rewritten >20% by humans not attributed. Metrics deliberately conservative (underestimate). Console spend figures are estimates, not billing. Contribution metrics NOT available for API/Console customers nor with ZDR.

**Example request:**

```
(UI) Navigate to https://claude.ai/analytics/claude-code ; enable GitHub app at https://github.com/apps/claude and toggle GitHub analytics at https://claude.ai/admin-settings/claude-code. Programmatic contribution query: search GitHub PRs labeled 'claude-code-assisted'.
```

**Example response:**

```
(No JSON; CSV export of contribution data, and the GitHub label 'claude-code-assisted' on attributed merged PRs.)
```

**Plans/tiers:** Org API, Team, Enterprise

**Tryable:** No

**Verification:** confidence high; path/method/auth/datapoints all verified. All paths, role gating and dashboard datapoints confirmed against official docs. Correctly characterized as a UI dashboard rather than a public REST API; programmatic contribution access is via searching GitHub PRs labeled 'claude-code-assisted'. Source: https://code.claude.com/docs/en/analytics

**Source URLs:**
- https://code.claude.com/docs/en/analytics

---

### enterprise-analytics-users - Enterprise Analytics — User Activity

**Purpose:** Per-user activity and engagement for a single day.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/users`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope). `x-api-key: <key with read:analytics scope>`, created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys (`sk-ant-admin...`) do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| date | query | Yes | Reporting day, YYYY-MM-DD (UTC). |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| user_id | adoption |
| email | adoption |
| conversations_count | engagement |
| messages_count | engagement |
| projects_created | activity-flow |
| files_shared | activity-flow |
| artifacts_created | activity-flow |
| shared_items_count | engagement |
| thinking_messages_count | engagement |
| skills_used_count | adoption |
| connectors_used_count | adoption |

**Gotchas:** Single-day per request (date param). Data latency ~4h (up to 24h); revisable 30 days. Some fields blank under Zero Data Retention.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/users" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists — 403 (not 404) is the expected response for a non-Enterprise / non-scoped probe; no live data was retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded (not from a live 200). Path confirmed live (HTTP 403, not 404 — endpoint exists; our probe key lacks the read:analytics scope and/or our org is not an Enterprise parent org). Method, auth scheme and params verified against official Anthropic docs. Categories are this catalog's taxonomy, not Anthropic labels. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-summaries - Enterprise Analytics — Activity Summaries

**Purpose:** Org-wide activity summary aggregations over a date range.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/summaries`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_date | query | Yes | Range start, YYYY-MM-DD. |
| ending_date | query | No | Range end, YYYY-MM-DD (defaults to starting_date). |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| total_conversations | engagement |
| total_messages | engagement |
| active_users | engagement |

**Gotchas:** Date-range aggregation. ~4h latency, 30-day revisability.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/summaries" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-chat-projects - Enterprise Analytics — Chat Projects

**Purpose:** Chat project (Projects) usage metrics for a day.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/apps/chat/projects`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| date | query | Yes | Reporting day, YYYY-MM-DD. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| project_id | adoption |
| project_name | adoption |
| usage_count | engagement |
| active_users | engagement |
| messages_count | activity-flow |
| conversation_count | activity-flow |

**Gotchas:** Single-day. ~4h latency.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/apps/chat/projects" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-skills - Enterprise Analytics — Skills Usage

**Purpose:** Skill adoption and usage for a day.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/skills`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| date | query | Yes | Reporting day, YYYY-MM-DD. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| skill_id | adoption |
| skill_name | adoption |
| usage_count | engagement |
| active_users | engagement |

**Gotchas:** Single-day. ~4h latency.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/skills" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-connectors - Enterprise Analytics — Connectors Usage

**Purpose:** Connector integration usage and reliability for a day.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/connectors`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| date | query | Yes | Reporting day, YYYY-MM-DD. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| connector_id | adoption |
| connector_name | adoption |
| connector_type | adoption |
| usage_count | engagement |
| active_users | engagement |

**Gotchas:** Single-day. ~4h latency.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/connectors" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-user-usage-report - Enterprise Analytics — Per-User Usage Report

**Purpose:** Per-user token-level usage breakdown over time.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/user_usage_report`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_at | query | Yes | RFC 3339 timestamp; range start. |
| ending_at | query | No | RFC 3339 timestamp; range end. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| user_id | adoption |
| email | adoption |
| input_tokens | cost |
| output_tokens | cost |
| cache_read_tokens | cost |
| cache_creation_tokens | cost |
| model | adoption |
| timestamp | engagement |

**Gotchas:** Token usage, not billed cost (see user_cost_report for USD). ~4h latency, 30-day revisability.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/user_usage_report" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-user-cost-report - Enterprise Analytics — Per-User Cost Report

**Purpose:** Per-user USD cost with pre/post-discount and multi-dimensional breakdown.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/user_cost_report`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_at | query | Yes | RFC 3339 timestamp; range start. |
| ending_at | query | No | RFC 3339 timestamp; range end. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| user_id | adoption |
| email | adoption |
| cost_usd_pre_discount | cost |
| cost_usd_post_discount | cost |
| cost_breakdown_by_model | cost |
| cost_breakdown_by_region | cost |
| cost_breakdown_by_cost_type | cost |
| cost_breakdown_by_token_type | cost |
| organization_id | adoption |
| workspace_id | adoption |

**Gotchas:** Pre- and post-discount tracked separately. ~4h latency, 30-day revisability.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/user_cost_report" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-usage-report - Enterprise Analytics — Usage Report (time series)

**Purpose:** Aggregate token usage over time with bucket granularity.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/usage_report`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_at | query | Yes | RFC 3339 timestamp; range start. |
| ending_at | query | No | RFC 3339 timestamp; range end. |
| bucket_width | query | No | Time granularity, e.g. 1h / 1d / 1w. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| starting_at / ending_at | engagement |
| input_tokens | cost |
| output_tokens | cost |
| cache_read_tokens | cost |
| cache_creation_tokens | cost |
| model | adoption |

**Gotchas:** Org-aggregate, not per-user. ~4h latency.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/usage_report" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### enterprise-analytics-cost-report - Enterprise Analytics — Cost Report (time series)

**Purpose:** Aggregate USD cost over time with historical trending.

**Request:** `GET https://api.anthropic.com/v1/organizations/analytics/cost_report`

**Auth:** `x-api-key` scheme — Analytics API key (`read:analytics` scope), created at claude.ai/analytics/api-keys by a Primary Owner of an Enterprise org. Enterprise subscription only. Admin API keys do NOT carry read:analytics. Not available to Individual, API/Console, or Team plans.

**Headers:**

| Name | Value | Required |
|---|---|---|
| anthropic-version | 2023-06-01 | Yes |
| x-api-key | $ANTHROPIC_ANALYTICS_KEY (read:analytics scope) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| starting_at | query | Yes | RFC 3339 timestamp; range start. |
| ending_at | query | No | RFC 3339 timestamp; range end. |
| bucket_width | query | No | Time granularity, e.g. 1h / 1d / 1w. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| starting_at / ending_at | engagement |
| cost_usd | cost |
| cost_pre_discount | cost |
| cost_post_discount | cost |
| model | adoption |
| cost_breakdown_by_region | cost |
| cost_breakdown_by_cost_type | cost |

**Gotchas:** Org-aggregate USD. ~4h latency, 30-day revisability.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/organizations/analytics/cost_report" --header "anthropic-version: 2023-06-01" --header "x-api-key: $ANTHROPIC_ANALYTICS_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise parent / key lacks read:analytics). Path exists (403 not 404); no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/analytics-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/analytics-api
- https://platform.claude.com/docs/en/api/organizations-analytics-api

---

### compliance-activities - Compliance — Activity Feed

**Purpose:** Shared activity/audit log across the org and all linked child orgs.

**Request:** `GET https://api.anthropic.com/v1/compliance/activities`

**Auth:** `x-api-key` scheme — Compliance Access Key OR Console Admin key. `x-api-key:` Compliance Access Key (Enterprise, all endpoints) OR Admin API key `sk-ant-admin...` (Console, Activity Feed only). Activity Feed is the only Compliance endpoint reachable by a Console Admin key, and only when the org is a member of an Enterprise parent org.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| filter | query | No | Activity filter (type/user/date). |
| limit | query | No | Page size. |
| page | query | No | Pagination cursor. |
| sort | query | No | Sort order. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| action | security | login/logout/file_access/chat_access/share_created/share_revoked. |
| timestamp | security |  |
| user_id | adoption |  |
| ip_address | security |  |
| user_agent | security |  |
| result | security | success/failure. |
| org_id | adoption |  |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** Only Compliance endpoint reachable by a Console Admin key, and only inside an Enterprise parent org. Full suite needs a Compliance Access Key.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/activities" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise, Org API

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists — 403 expected for a non-Enterprise / non-compliance-scoped probe; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Path confirmed live (HTTP 403, not 404 — endpoint exists). 403 reflects either a missing Compliance Access Key OR a Console Admin key whose org is not in an Enterprise parent. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-activity-feed
- https://platform.claude.com/docs/en/manage-claude/compliance-api-access

---

### compliance-organizations - Compliance — List Organizations

**Purpose:** List parent + linked child orgs.

**Request:** `GET https://api.anthropic.com/v1/compliance/organizations`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:** none.

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | adoption |
| name | adoption |
| created_at | adoption |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** Directory endpoints span all linked child orgs.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/organizations" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-org-data

---

### compliance-organization - Compliance — Get Organization

**Purpose:** Single org metadata.

**Request:** `GET https://api.anthropic.com/v1/compliance/organizations/{org_uuid}`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| org_uuid | path | Yes | Organization UUID. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | adoption |
| name | adoption |
| created_at | adoption |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** Path param org_uuid.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/organizations/ORG_UUID" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-org-data

---

### compliance-organization-users - Compliance — List Org Users

**Purpose:** List users in a specific org.

**Request:** `GET https://api.anthropic.com/v1/compliance/organizations/{org_uuid}/users`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| org_uuid | path | Yes | Organization UUID. |
| limit | query | No | Page size. |
| page | query | No | Pagination cursor. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | adoption |
| email | adoption |
| name | adoption |
| role | adoption |
| created_at | adoption |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** Spans linked child orgs by org_uuid.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/organizations/ORG_UUID/users" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-org-data

---

### compliance-organization-user - Compliance — Get Org User

**Purpose:** Single user metadata.

**Request:** `GET https://api.anthropic.com/v1/compliance/organizations/{org_uuid}/users/{user_uuid}`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| org_uuid | path | Yes | Organization UUID. |
| user_uuid | path | Yes | User UUID. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | adoption |
| email | adoption |
| name | adoption |
| role | adoption |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** Two path params.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/organizations/ORG_UUID/users/USER_UUID" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-org-data

---

### compliance-organization-roles - Compliance — List Roles

**Purpose:** List role definitions in an org.

**Request:** `GET https://api.anthropic.com/v1/compliance/organizations/{org_uuid}/roles`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| org_uuid | path | Yes | Organization UUID. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | adoption |
| name | adoption |
| permissions | security |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** Role/permission inventory.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/organizations/ORG_UUID/roles" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-org-data

---

### compliance-organization-groups - Compliance — List Groups

**Purpose:** List admin-defined user groups.

**Request:** `GET https://api.anthropic.com/v1/compliance/organizations/{org_uuid}/groups`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| org_uuid | path | Yes | Organization UUID. |
| limit | query | No | Page size. |
| page | query | No | Pagination cursor. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | adoption |
| name | adoption |
| members | adoption |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** Group membership directory.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/organizations/ORG_UUID/groups" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-org-data

---

### compliance-chats - Compliance — List Chats

**Purpose:** Audit trail of chat conversations.

**Request:** `GET https://api.anthropic.com/v1/compliance/chats`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required |
|---|---|---|
| filter | query | No |
| limit | query | No |
| page | query | No |
| sort | query | No |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | engagement |
| title | engagement |
| created_at | engagement |
| user_id | adoption |
| is_shared | security |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** claude.ai-org-only (content endpoint). Unavailable under Zero Data Retention.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/chats" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-content-data

---

### compliance-chat - Compliance — Get Chat

**Purpose:** Chat conversation detail + messages.

**Request:** `GET https://api.anthropic.com/v1/compliance/chats/{chat_id}`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| chat_id | path | Yes | Chat ID. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category | Description |
|---|---|---|
| id | engagement |  |
| messages | engagement | Message array. |
| user_id | adoption |  |
| created_at | engagement |  |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** claude.ai-org-only. ZDR limits content.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/chats/CHAT_ID" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-content-data

---

### compliance-files - Compliance — List Files

**Purpose:** Audit trail of uploaded files.

**Request:** `GET https://api.anthropic.com/v1/compliance/files`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required |
|---|---|---|
| filter | query | No |
| limit | query | No |
| page | query | No |
| sort | query | No |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | engagement |
| filename | engagement |
| size | engagement |
| created_at | engagement |
| user_id | adoption |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** claude.ai-org-only content endpoint.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/files" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-content-data

---

### compliance-file - Compliance — Get File

**Purpose:** File metadata.

**Request:** `GET https://api.anthropic.com/v1/compliance/files/{file_id}`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required | Description |
|---|---|---|---|
| file_id | path | Yes | File ID. |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | engagement |
| filename | engagement |
| size | engagement |
| content_hash | security |
| created_at | engagement |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** claude.ai-org-only.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/files/FILE_ID" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-content-data

---

### compliance-projects - Compliance — List Projects

**Purpose:** Audit trail of Projects (shared workspaces).

**Request:** `GET https://api.anthropic.com/v1/compliance/projects`

**Auth:** `x-api-key` scheme — Compliance Access Key created in claude.ai (admin settings). Full Compliance suite requires an Enterprise org + Compliance Access Key. Console Admin keys reach the Activity Feed only.

**Headers:**

| Name | Value | Required |
|---|---|---|
| x-api-key | $CLAUDE_COMPLIANCE_KEY (or sk-ant-admin... for Activity Feed) | Yes |

**Parameters:**

| Name | In | Required |
|---|---|---|
| filter | query | No |
| limit | query | No |
| page | query | No |
| sort | query | No |

**Response shape:** inline-json

**Datapoints returned:**

| Datapoint | Category |
|---|---|
| id | engagement |
| name | engagement |
| created_at | engagement |
| owner_id | adoption |

**Rate limits:** 600 requests/minute per parent organization, shared across all linked child orgs.

**Gotchas:** claude.ai-org-only content endpoint.

**Example request:**

```bash
curl "https://api.anthropic.com/v1/compliance/projects" --header "x-api-key: $CLAUDE_COMPLIANCE_KEY"
```

**Plans/tiers:** Enterprise

**Tryable:** No

**Live check:** HTTP 403 on 2026-06-05 — probe org (not Enterprise / no Compliance Access Key). Path exists; no live data retrieved.

**Verification:** confidence high; path/method/auth verified, datapoints doc-grounded. Source: https://platform.claude.com/docs/en/manage-claude/compliance-api

**Source URLs:**
- https://platform.claude.com/docs/en/manage-claude/compliance-api
- https://platform.claude.com/docs/en/api/compliance
- https://platform.claude.com/docs/en/manage-claude/compliance-content-data

---

## Unverified claims (surfaced honestly)

- Exact monetary prices of Claude for Teams / Enterprise / Console plans — the provided official pages do not state dollar pricing; only feature/metrics access by tier was documented (see pricing page /docs/en/about-claude/pricing, not fetched).
- Exact numeric rate limit (requests/sec) for the Claude Code Analytics API and Admin management endpoints — docs give qualitative guidance only (Usage/Cost: ~1 poll/minute sustained).
- Full JSON response schemas for List Users / List API Keys / List Workspaces (only curl examples and field names were shown on the Administration API overview; per-field schemas live on individual reference pages not fetched here).
- Whether a minimum number of org members is required to view dashboards/analytics — no explicit minimum-member threshold was stated on the fetched pages (only role requirements and GitHub-app prerequisites).
- Precise pagination/limit defaults for the Cost Report endpoint (limit default/max not specified on the fetched reference page).
