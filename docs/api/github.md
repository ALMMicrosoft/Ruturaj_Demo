# GitHub - API Endpoint Reference

The full GitHub platform as a software-delivery telemetry source: org/repo provisioning, PR/issue/commit activity, Actions & deployments (DORA), Checks & statuses (quality), GHAS security (code/secret scanning, Dependabot, advisories, audit log), and enhanced billing — exposed across REST and GraphQL.

**Vendor:** GitHub (Microsoft)

**Docs:** https://docs.github.com/en/rest

**Toolchain stage:** source-control

**Ingestion pattern:** Direct inline JSON for almost all REST reads (paginate via Link rel=next); single-POST GraphQL for O(1) aggregate counts and cross-repo contribution rollups. A few stats endpoints return 202 while cache-warming (retry).

## Plans / Tiers

| Name | Price | Tier | Unlocks APIs | Metrics access |
| --- | --- | --- | --- | --- |
| GitHub Free | $0 (personal & organizations) | individual | yes | 159 of 191 endpoints. Full REST/GraphQL access to org/repo provisioning, members/teams, PR/issue/commit activity, Actions & deployments (DORA), Checks & commit statuses (quality), repo traffic/insights, and Dependabot alerts (free on all repos). No custom org roles, no audit-log API, no enterprise billing/licensing. |
| GitHub Team | $4/user/mo (per GitHub plans page) | team | yes | Everything in Free plus Team-tier collaboration. 6 endpoints are gated at Team or higher. Org-level seat/billing context richer than Free for paid orgs. |
| GitHub Enterprise Cloud (GHEC) | $21/user/mo (per GitHub plans page) | enterprise | yes | Unlocks 23 enterprise-cloud endpoints: custom organization roles, the audit-log API (/orgs/{org}/audit-log, /enterprises/{enterprise}/audit-log), consumed-licenses, enterprise billing/cost-centers/budgets, and enterprise GraphQL rollups. Audit log is GHEC-only and rate-limited to 1,750 q/h. |
| GitHub Enterprise Server (GHES) | Self-hosted (per-seat licensing) | enterprise | yes | Self-hosted GitHub. Same REST/GraphQL surface as GHEC for most endpoints, served under https://HOST/api/v3 (REST) and https://HOST/api/graphql (GraphQL). Custom org roles available on recent GHES (>=3.13). Some cloud-only features (data residency, certain enterprise rollups) differ. |
| GitHub Advanced Security (add-on) | Add-on; unbundled as Code Security & Secret Protection (Apr 2025) | enterprise | yes | Add-on (not a standalone tier). Required to read code scanning and secret scanning on PRIVATE/internal repos (3 GHAS-gated endpoints; public repos are free). Also unlocks GHAS committer/active-committer billing. Dependabot alerts do NOT require GHAS — they are free on all repos. |

- GitHub Free source: https://docs.github.com/en/get-started/learning-about-github/githubs-plans
- GitHub Team source: https://docs.github.com/en/get-started/learning-about-github/githubs-plans
- GitHub Enterprise Cloud (GHEC) source: https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud
- GitHub Enterprise Server (GHES) source: https://docs.github.com/en/enterprise-server@latest/rest
- GitHub Advanced Security (add-on) source: https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security

## Feasibility Verdict

**Status:** feasible-with-caveats

LIVE-VERIFIED 2026-06-04 against org ALMCybage + enterprise cybage (classic PAT scopes: repo, read:org, read:enterprise, read:audit_log, manage_billing:copilot, held by an org owner). A FULL sweep fired every tryable GET: 137 of 178 read endpoints returned live data across all eight categories (org/repo/PR/commit/Actions/Checks flow, Dependabot/code/secret-scanning alerts, billing usage, org+enterprise audit log, consumed-licenses) and the Executive dashboard rendered real numbers end to end at org, enterprise, AND repo scope. The remaining endpoints returned honest non-2xx outcomes (recorded in _research/github/live-sweep-results.json): role-gated (org rulesets need admin:org), user-level billing (this token is org-scoped), retired legacy billing (410 Gone), or simply no live instance in the test account (no releases/deployments/custom-roles) — none are catalog bugs. FEASIBLE on all GitHub tiers for the core (159/191 endpoints are Free-tier). A subset requires GitHub Team, Enterprise Cloud (custom org roles, audit log, enterprise billing/licensing — 23 endpoints), or the GitHub Advanced Security add-on for private/internal code & secret scanning (3 endpoints). GraphQL adds metrics with no cheap REST equivalent.

**Required plan:** Free for org/repo/PR/issue/commit/Actions/Checks/Dependabot reads. GitHub Team for some collaboration features. GitHub Enterprise Cloud for custom organization roles, the audit log API, consumed-licenses, cost centers, and enterprise rollups. GitHub Advanced Security (or unbundled Code Security / Secret Protection) to read code/secret scanning on PRIVATE/internal repos.

**Blockers:** 1) Role gating is independent of license: /orgs/{org} full plan/seat block is OWNER-only; /traffic/* needs repo write/push + Metadata:read; GET /orgs/{org}/rulesets needs Org Administration WRITE; Checks fine-grained read is effectively GitHub-App-only (PATs read via repo read). 2) Stats endpoints (/stats/contributors, /commit_activity, /code_frequency) return 202 while computing and 0/422 for repos with >=10,000 commits. 3) Audit log is GHEC-only, needs include=git|all for git events, and is rate-limited to 1,750 q/h (enterprise endpoint is classic-PAT-only). 4) Private-repo code/secret scanning returns 403/404 without GHAS. 5) Legacy billing endpoints are removed from current docs — use /settings/billing/usage. 6) Some GraphQL field shapes are unverified (confidence low) — re-confirm before relying.

### Unverified claims (tool-level)

- graphql-repository-engagement — GraphQL Repository engagement fields (stargazerCount/forkCount/watchers/diskUsage/pushedAt) not confirmed against the live schema this session.
- graphql-commit-status-check-rollup — statusCheckRollup.state enum unconfirmed.
- graphql-contribution-calendar / graphql-contributions-by-repository / graphql-organization-counts / graphql-repository-counts / graphql-enterprise-rollup / graphql-enterprise-billing-info — object/field schema (esp. scalar types) provisional.
- Legacy billing endpoints (org/enterprise actions/packages/shared-storage) — removed from current GitHub.com REST reference; enterprise packages/storage field shapes inferred by symmetry. Use /settings/billing/usage instead.
- Billing usage report fine-grained PAT support is contradictory in GitHub docs; catalog defaults to classic PAT for /settings/billing/usage* endpoints.

## Endpoints (192)

| id | name | method | path | response shape | deprecated? |
| --- | --- | --- | --- | --- | --- |
| `get-an-organization` | Get an organization | GET | `/orgs/{org}` | - | no |
| `list-organizations-for-user` | List organizations for the authenticated user / for a user | GET | `/user/orgs and /users/{username}/orgs` | - | no |
| `list-org-members` | List organization members | GET | `/orgs/{org}/members` | - | no |
| `list-public-org-members` | List public organization members | GET | `/orgs/{org}/public_members` | - | no |
| `get-org-membership-for-user` | Get organization membership for a user | GET | `/orgs/{org}/memberships/{username}` | - | no |
| `list-pending-org-invitations` | List pending organization invitations | GET | `/orgs/{org}/invitations` | - | no |
| `list-failed-org-invitations` | List failed organization invitations | GET | `/orgs/{org}/failed_invitations` | - | no |
| `list-org-memberships-auth-user` | List/Get organization memberships for the authenticated user | GET | `/user/memberships/orgs and /user/memberships/orgs/{org}` | - | no |
| `list-outside-collaborators` | List outside collaborators for an organization | GET | `/orgs/{org}/outside_collaborators` | - | no |
| `get-all-org-roles` | Get all organization roles | GET | `/orgs/{org}/organization-roles` | - | no |
| `list-users-assigned-org-role` | List users assigned to an organization role | GET | `/orgs/{org}/organization-roles/{role_id}/users` | - | no |
| `list-teams-assigned-org-role` | List teams assigned to an organization role | GET | `/orgs/{org}/organization-roles/{role_id}/teams` | - | no |
| `list-teams` | List teams | GET | `/orgs/{org}/teams` | - | no |
| `get-team-by-name` | Get a team by name (with member/repo counts) | GET | `/orgs/{org}/teams/{team_slug}` | - | no |
| `list-child-teams` | List child teams | GET | `/orgs/{org}/teams/{team_slug}/teams` | - | no |
| `list-team-repos` | List team repositories | GET | `/orgs/{org}/teams/{team_slug}/repos` | - | no |
| `list-team-members` | List team members | GET | `/orgs/{org}/teams/{team_slug}/members` | - | no |
| `get-team-membership-for-user` | Get team membership for a user | GET | `/orgs/{org}/teams/{team_slug}/memberships/{username}` | - | no |
| `list-team-pending-invitations` | List pending team invitations | GET | `/orgs/{org}/teams/{team_slug}/invitations` | - | no |
| `list-org-repositories` | List organization repositories | GET | `/orgs/{org}/repos` | - | no |
| `get-a-repository` | Get a repository | GET | `/repos/{owner}/{repo}` | - | no |
| `get-repository-topics` | Get all repository topics | GET | `/repos/{owner}/{repo}/topics` | - | no |
| `list-repository-languages-org` | List repository languages | GET | `/repos/{owner}/{repo}/languages` | - | no |
| `list-org-repository-rulesets` | Get all organization repository rulesets | GET | `/orgs/{org}/rulesets` | - | no |
| `list-org-custom-properties` | Get all custom properties for an organization | GET | `/orgs/{org}/properties/schema` | - | no |
| `get-enterprise-custom-properties` | Get all custom properties for an enterprise | GET | `/enterprises/{enterprise}/properties/schema` | - | no |
| `graphql-org-aggregate-counts` | GraphQL: organization aggregate counts (members/repos/teams) | POST | `/graphql` | - | no |
| `get-contributor-commit-activity` | Get all contributor commit activity | GET | `/repos/{owner}/{repo}/stats/contributors` | - | no |
| `get-commit-activity` | Get the last year of commit activity | GET | `/repos/{owner}/{repo}/stats/commit_activity` | - | no |
| `get-code-frequency` | Get the weekly commit activity (code frequency) | GET | `/repos/{owner}/{repo}/stats/code_frequency` | - | no |
| `get-participation` | Get the weekly commit count (participation) | GET | `/repos/{owner}/{repo}/stats/participation` | - | no |
| `get-punch-card` | Get the hourly commit count for each day (punch card) | GET | `/repos/{owner}/{repo}/stats/punch_card` | - | no |
| `get-traffic-views` | Get repository page views | GET | `/repos/{owner}/{repo}/traffic/views` | - | no |
| `get-traffic-clones` | Get repository clones | GET | `/repos/{owner}/{repo}/traffic/clones` | - | no |
| `get-traffic-popular-referrers` | Get top referral sources | GET | `/repos/{owner}/{repo}/traffic/popular/referrers` | - | no |
| `get-traffic-popular-paths` | Get top referral paths | GET | `/repos/{owner}/{repo}/traffic/popular/paths` | - | no |
| `get-community-profile` | Get community profile metrics | GET | `/repos/{owner}/{repo}/community/profile` | - | no |
| `list-repository-languages-traffic` | List repository languages | GET | `/repos/{owner}/{repo}/languages` | - | no |
| `get-repository-popularity-counts` | Get a repository (popularity / engagement counts) | GET | `/repos/{owner}/{repo}` | - | no |
| `list-repository-activity` | List repository activity | GET | `/repos/{owner}/{repo}/activity` | - | no |
| `list-repository-contributors` | List repository contributors | GET | `/repos/{owner}/{repo}/contributors` | - | no |
| `graphql-repository-engagement` | Repository object engagement fields (GraphQL) | POST | `/graphql` | - | no |
| `list-commits` | List commits | GET | `/repos/{owner}/{repo}/commits` | - | no |
| `get-commit` | Get a commit | GET | `/repos/{owner}/{repo}/commits/{ref}` | - | no |
| `compare-commits` | Compare two commits | GET | `/repos/{owner}/{repo}/compare/{basehead}` | - | no |
| `list-pull-requests-associated-with-commit` | List pull requests associated with a commit | GET | `/repos/{owner}/{repo}/commits/{commit_sha}/pulls` | - | no |
| `list-commit-comments-repo` | List commit comments for a repository | GET | `/repos/{owner}/{repo}/comments` | - | no |
| `list-commit-comments-for-commit` | List commit comments (for a commit) | GET | `/repos/{owner}/{repo}/commits/{commit_sha}/comments` | - | no |
| `list-pull-requests` | List pull requests | GET | `/repos/{owner}/{repo}/pulls` | - | no |
| `get-pull-request` | Get a pull request | GET | `/repos/{owner}/{repo}/pulls/{pull_number}` | - | no |
| `list-commits-on-pull-request` | List commits on a pull request | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/commits` | - | no |
| `list-pull-request-files` | List pull request files | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/files` | - | no |
| `check-pull-request-merged` | Check if a pull request has been merged | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/merge` | - | no |
| `list-pull-request-reviews` | List reviews for a pull request | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/reviews` | - | no |
| `get-pull-request-review` | Get a review for a pull request | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` | - | no |
| `list-review-comments-for-review` | List comments for a pull request review | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/comments` | - | no |
| `get-requested-reviewers` | Get all requested reviewers for a pull request | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | - | no |
| `list-review-comments-on-pull-request` | List review comments on a pull request | GET | `/repos/{owner}/{repo}/pulls/{pull_number}/comments` | - | no |
| `list-review-comments-in-repository` | List review comments in a repository | GET | `/repos/{owner}/{repo}/pulls/comments` | - | no |
| `list-repository-issues` | List repository issues | GET | `/repos/{owner}/{repo}/issues` | - | no |
| `get-issue` | Get an issue | GET | `/repos/{owner}/{repo}/issues/{issue_number}` | - | no |
| `list-user-assigned-issues` | List issues assigned to the authenticated user | GET | `/issues` | - | no |
| `list-org-assigned-issues` | List organization issues assigned to the authenticated user | GET | `/orgs/{org}/issues` | - | no |
| `list-issue-events-for-repository` | List issue events for a repository | GET | `/repos/{owner}/{repo}/issues/events` | - | no |
| `list-issue-events` | List events for an issue | GET | `/repos/{owner}/{repo}/issues/{issue_number}/events` | - | no |
| `list-issue-timeline` | List timeline events for an issue | GET | `/repos/{owner}/{repo}/issues/{issue_number}/timeline` | - | no |
| `list-issue-comments-repo` | List issue comments for a repository | GET | `/repos/{owner}/{repo}/issues/comments` | - | no |
| `list-issue-comments` | List comments on an issue | GET | `/repos/{owner}/{repo}/issues/{issue_number}/comments` | - | no |
| `list-milestones` | List milestones | GET | `/repos/{owner}/{repo}/milestones` | - | no |
| `get-milestone` | Get a milestone | GET | `/repos/{owner}/{repo}/milestones/{milestone_number}` | - | no |
| `list-repository-labels` | List labels for a repository | GET | `/repos/{owner}/{repo}/labels` | - | no |
| `list-labels-for-issue` | List labels for an issue | GET | `/repos/{owner}/{repo}/issues/{issue_number}/labels` | - | no |
| `list-assignees` | List assignees | GET | `/repos/{owner}/{repo}/assignees` | - | no |
| `list-issue-reactions` | List reactions for an issue | GET | `/repos/{owner}/{repo}/issues/{issue_number}/reactions` | - | no |
| `list-issue-comment-reactions` | List reactions for an issue comment | GET | `/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions` | - | no |
| `list-pr-review-comment-reactions` | List reactions for a pull request review comment | GET | `/repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions` | - | no |
| `list-commit-comment-reactions` | List reactions for a commit comment | GET | `/repos/{owner}/{repo}/comments/{comment_id}/reactions` | - | no |
| `list-sub-issues` | List sub-issues | GET | `/repos/{owner}/{repo}/issues/{issue_number}/sub_issues` | - | no |
| `graphql-pullrequest-metrics` | GraphQL PullRequest review/cycle metrics | POST | `/graphql` | - | no |
| `list-workflow-runs-repo` | List workflow runs for a repository | GET | `/repos/{owner}/{repo}/actions/runs` | - | no |
| `get-workflow-run` | Get a workflow run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}` | - | no |
| `get-workflow-run-attempt` | Get a workflow run attempt | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}` | - | no |
| `get-workflow-run-usage` | Get workflow run usage (timing) | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/timing` | - | no |
| `get-workflow-usage` | Get workflow usage (timing) | GET | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/timing` | - | no |
| `list-workflow-runs-for-workflow` | List workflow runs for a workflow | GET | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs` | - | no |
| `list-repo-workflows` | List repository workflows | GET | `/repos/{owner}/{repo}/actions/workflows` | - | no |
| `get-workflow` | Get a workflow | GET | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}` | - | no |
| `list-jobs-for-workflow-run` | List jobs for a workflow run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | - | no |
| `list-jobs-for-run-attempt` | List jobs for a workflow run attempt | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}/jobs` | - | no |
| `get-job` | Get a job for a workflow run | GET | `/repos/{owner}/{repo}/actions/jobs/{job_id}` | - | no |
| `get-pending-deployments` | Get pending deployments for a workflow run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/pending_deployments` | - | no |
| `get-workflow-run-approvals` | Get the review history for a workflow run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/approvals` | - | no |
| `list-repo-artifacts` | List artifacts for a repository | GET | `/repos/{owner}/{repo}/actions/artifacts` | - | no |
| `get-repo-cache-usage` | Get GitHub Actions cache usage for a repository | GET | `/repos/{owner}/{repo}/actions/cache/usage` | - | no |
| `list-repo-caches` | List GitHub Actions caches for a repository | GET | `/repos/{owner}/{repo}/actions/caches` | - | no |
| `get-org-cache-usage` | Get GitHub Actions cache usage for an organization | GET | `/orgs/{org}/actions/cache/usage` | - | no |
| `get-org-cache-usage-by-repo` | List repositories with GitHub Actions cache usage for an organization | GET | `/orgs/{org}/actions/cache/usage-by-repository` | - | no |
| `get-org-billing-usage` | Get billing usage report for an organization (enhanced billing) | GET | `/organizations/{org}/settings/billing/usage` | - | no |
| `list-deployments` | List deployments | GET | `/repos/{owner}/{repo}/deployments` | - | no |
| `get-deployment` | Get a deployment | GET | `/repos/{owner}/{repo}/deployments/{deployment_id}` | - | no |
| `list-deployment-statuses` | List deployment statuses | GET | `/repos/{owner}/{repo}/deployments/{deployment_id}/statuses` | - | no |
| `get-deployment-status` | Get a deployment status | GET | `/repos/{owner}/{repo}/deployments/{deployment_id}/statuses/{status_id}` | - | no |
| `list-environments` | List environments | GET | `/repos/{owner}/{repo}/environments` | - | no |
| `get-environment` | Get an environment | GET | `/repos/{owner}/{repo}/environments/{environment_name}` | - | no |
| `list-releases` | List releases | GET | `/repos/{owner}/{repo}/releases` | - | no |
| `get-latest-release` | Get the latest release | GET | `/repos/{owner}/{repo}/releases/latest` | - | no |
| `get-release-by-tag` | Get a release by tag name | GET | `/repos/{owner}/{repo}/releases/tags/{tag}` | - | no |
| `get-release-by-id` | Get a release | GET | `/repos/{owner}/{repo}/releases/{release_id}` | - | no |
| `get-check-run` | Get a check run | GET | `/repos/{owner}/{repo}/check-runs/{check_run_id}` | - | no |
| `list-check-runs-for-ref` | List check runs for a Git reference | GET | `/repos/{owner}/{repo}/commits/{ref}/check-runs` | - | no |
| `list-check-runs-in-suite` | List check runs in a check suite | GET | `/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs` | - | no |
| `list-check-run-annotations` | List check run annotations | GET | `/repos/{owner}/{repo}/check-runs/{check_run_id}/annotations` | - | no |
| `get-check-suite` | Get a check suite | GET | `/repos/{owner}/{repo}/check-suites/{check_suite_id}` | - | no |
| `list-check-suites-for-ref` | List check suites for a Git reference | GET | `/repos/{owner}/{repo}/commits/{ref}/check-suites` | - | no |
| `get-combined-commit-status` | Get the combined status for a specific reference | GET | `/repos/{owner}/{repo}/commits/{ref}/status` | - | no |
| `list-commit-statuses` | List commit statuses for a reference | GET | `/repos/{owner}/{repo}/commits/{ref}/statuses` | - | no |
| `list-workflow-runs-for-repo-quality` | List workflow runs for a repository | GET | `/repos/{owner}/{repo}/actions/runs` | - | no |
| `get-workflow-run-quality` | Get a workflow run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}` | - | no |
| `list-workflow-runs-for-workflow-quality` | List workflow runs for a workflow | GET | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs` | - | no |
| `get-workflow-run-attempt-quality` | Get a workflow run attempt | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}` | - | no |
| `list-jobs-for-workflow-run-quality` | List jobs for a workflow run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | - | no |
| `list-jobs-for-workflow-run-attempt` | List jobs for a workflow run attempt | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}/jobs` | - | no |
| `get-job-for-workflow-run` | Get a job for a workflow run | GET | `/repos/{owner}/{repo}/actions/jobs/{job_id}` | - | no |
| `list-artifacts-for-repo` | List artifacts for a repository | GET | `/repos/{owner}/{repo}/actions/artifacts` | - | no |
| `list-workflow-run-artifacts` | List workflow run artifacts | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts` | - | no |
| `get-artifact` | Get an artifact | GET | `/repos/{owner}/{repo}/actions/artifacts/{artifact_id}` | - | no |
| `graphql-commit-status-check-rollup` | Commit.statusCheckRollup (GraphQL) | POST | `/graphql` | - | no |
| `list-code-scanning-alerts-repo` | List code scanning alerts for a repository | GET | `/repos/{owner}/{repo}/code-scanning/alerts` | - | no |
| `get-code-scanning-alert-repo` | Get a code scanning alert | GET | `/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}` | - | no |
| `list-code-scanning-alert-instances` | List instances of a code scanning alert | GET | `/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}/instances` | - | no |
| `get-code-scanning-alert-autofix` | Get the status of a code scanning autofix | GET | `/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}/autofix` | - | no |
| `list-code-scanning-analyses` | List code scanning analyses for a repository | GET | `/repos/{owner}/{repo}/code-scanning/analyses` | - | no |
| `get-code-scanning-analysis` | Get a code scanning analysis for a repository | GET | `/repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}` | - | no |
| `get-code-scanning-default-setup` | Get code scanning default setup configuration | GET | `/repos/{owner}/{repo}/code-scanning/default-setup` | - | no |
| `list-codeql-databases` | List CodeQL databases for a repository | GET | `/repos/{owner}/{repo}/code-scanning/codeql/databases` | - | no |
| `get-code-scanning-sarif-status` | Get information about a SARIF upload | GET | `/repos/{owner}/{repo}/code-scanning/sarifs/{sarif_id}` | - | no |
| `list-code-scanning-alerts-org` | List code scanning alerts for an organization | GET | `/orgs/{org}/code-scanning/alerts` | - | no |
| `list-code-scanning-alerts-enterprise` | List code scanning alerts for an enterprise | GET | `/enterprises/{enterprise}/code-scanning/alerts` | - | no |
| `list-secret-scanning-alerts-repo` | List secret scanning alerts for a repository | GET | `/repos/{owner}/{repo}/secret-scanning/alerts` | - | no |
| `get-secret-scanning-alert` | Get a secret scanning alert | GET | `/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}` | - | no |
| `list-secret-scanning-alert-locations` | List locations for a secret scanning alert | GET | `/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}/locations` | - | no |
| `get-secret-scanning-scan-history` | Get secret scanning scan history for a repository | GET | `/repos/{owner}/{repo}/secret-scanning/scan-history` | - | no |
| `list-secret-scanning-alerts-org` | List secret scanning alerts for an organization | GET | `/orgs/{org}/secret-scanning/alerts` | - | no |
| `list-secret-scanning-alerts-enterprise` | List secret scanning alerts for an enterprise | GET | `/enterprises/{enterprise}/secret-scanning/alerts` | - | no |
| `list-dependabot-alerts-repo` | List Dependabot alerts for a repository | GET | `/repos/{owner}/{repo}/dependabot/alerts` | - | no |
| `get-dependabot-alert-repo` | Get a Dependabot alert | GET | `/repos/{owner}/{repo}/dependabot/alerts/{alert_number}` | - | no |
| `list-dependabot-alerts-org` | List Dependabot alerts for an organization | GET | `/orgs/{org}/dependabot/alerts` | - | no |
| `list-dependabot-alerts-enterprise` | List Dependabot alerts for an enterprise | GET | `/enterprises/{enterprise}/dependabot/alerts` | - | no |
| `export-sbom` | Export SBOM for a repository | GET | `/repos/{owner}/{repo}/dependency-graph/sbom` | - | no |
| `dependency-review-compare` | Get dependency review (diff between two commits) | GET | `/repos/{owner}/{repo}/dependency-graph/compare/{basehead}` | - | no |
| `list-repo-security-advisories` | List repository security advisories | GET | `/repos/{owner}/{repo}/security-advisories` | - | no |
| `get-repo-security-advisory` | Get a repository security advisory | GET | `/repos/{owner}/{repo}/security-advisories/{ghsa_id}` | - | no |
| `list-org-security-advisories` | List organization repository security advisories | GET | `/orgs/{org}/security-advisories` | - | no |
| `list-global-advisories` | List global security advisories (GitHub Advisory Database) | GET | `/advisories` | - | no |
| `get-global-advisory` | Get a global security advisory | GET | `/advisories/{ghsa_id}` | - | no |
| `get-org-audit-log` | Get the audit log for an organization | GET | `/orgs/{org}/audit-log` | - | no |
| `get-enterprise-audit-log` | Get the audit log for an enterprise | GET | `/enterprises/{enterprise}/audit-log` | - | no |
| `org-billing-usage-report` | Get billing usage report for an organization (enhanced billing platform) | GET | `/organizations/{org}/settings/billing/usage` | - | no |
| `org-billing-usage-summary` | Get billing usage summary for an organization (public preview) | GET | `/organizations/{org}/settings/billing/usage/summary` | - | no |
| `org-ai-credit-usage` | Get billing AI credit usage report for an organization | GET | `/organizations/{org}/settings/billing/ai_credit/usage` | - | no |
| `org-premium-request-usage` | Get billing premium request usage report for an organization | GET | `/organizations/{org}/settings/billing/premium_request/usage` | - | no |
| `user-billing-usage-report` | Get billing usage report for a user (enhanced billing platform) | GET | `/users/{username}/settings/billing/usage` | - | no |
| `user-billing-usage-summary` | Get billing usage summary for a user (public preview) | GET | `/users/{username}/settings/billing/usage/summary` | - | no |
| `user-ai-credit-usage` | Get billing AI credit usage report for a user | GET | `/users/{username}/settings/billing/ai_credit/usage` | - | no |
| `user-premium-request-usage` | Get billing premium request usage report for a user | GET | `/users/{username}/settings/billing/premium_request/usage` | - | no |
| `enterprise-billing-usage-report` | Get billing usage report for an enterprise (usage by cost center) | GET | `/enterprises/{enterprise}/settings/billing/usage` | - | no |
| `enterprise-billing-usage-summary` | Get billing usage summary for an enterprise (public preview) | GET | `/enterprises/{enterprise}/settings/billing/usage/summary` | - | no |
| `enterprise-ai-credit-usage` | Get billing AI credit usage report for an enterprise | GET | `/enterprises/{enterprise}/settings/billing/ai_credit/usage` | - | no |
| `enterprise-premium-request-usage` | Get billing premium request usage report for an enterprise | GET | `/enterprises/{enterprise}/settings/billing/premium_request/usage` | - | no |
| `ghas-active-committers-org` | Get GitHub Advanced Security active committers for an organization | GET | `/orgs/{org}/settings/billing/advanced-security` | - | no |
| `ghas-active-committers-enterprise` | Get GitHub Advanced Security active committers for an enterprise | GET | `/enterprises/{enterprise}/settings/billing/advanced-security` | - | no |
| `enterprise-consumed-licenses` | List enterprise consumed licenses (seats) | GET | `/enterprises/{enterprise}/consumed-licenses` | - | no |
| `enterprise-license-sync-status` | Get a license sync status (GHES connected to GHEC) | GET | `/enterprises/{enterprise}/license-sync-status` | - | no |
| `enterprise-cost-centers-list` | List cost centers for an enterprise | GET | `/enterprises/{enterprise}/settings/billing/cost-centers` | - | no |
| `enterprise-cost-center-get` | Get a cost center by ID for an enterprise | GET | `/enterprises/{enterprise}/settings/billing/cost-centers/{cost_center_id}` | - | no |
| `enterprise-budgets-list` | List budgets for an enterprise | GET | `/enterprises/{enterprise}/settings/billing/budgets` | - | no |
| `org-codespaces-list` | List Codespaces for the organization (billable ownership) | GET | `/orgs/{org}/codespaces` | - | no |
| `org-actions-billing-legacy` | Get GitHub Actions billing for an organization (LEGACY billing platform / GHES) | GET | `/orgs/{org}/settings/billing/actions` | - | yes |
| `org-packages-billing-legacy` | Get GitHub Packages billing for an organization (LEGACY / GHES) | GET | `/orgs/{org}/settings/billing/packages` | - | yes |
| `org-shared-storage-billing-legacy` | Get shared storage billing for an organization (LEGACY / GHES) | GET | `/orgs/{org}/settings/billing/shared-storage` | - | yes |
| `enterprise-actions-billing-legacy` | Get GitHub Actions billing for an enterprise (LEGACY billing platform) | GET | `/enterprises/{enterprise}/settings/billing/actions` | - | yes |
| `enterprise-packages-billing-legacy` | Get GitHub Packages billing for an enterprise (LEGACY) | GET | `/enterprises/{enterprise}/settings/billing/packages` | - | yes |
| `enterprise-shared-storage-billing-legacy` | Get shared storage billing for an enterprise (LEGACY) | GET | `/enterprises/{enterprise}/settings/billing/shared-storage` | - | yes |
| `graphql-user-contributions-collection` | User contributionsCollection (totals) | POST | `/graphql` | - | no |
| `graphql-contribution-calendar` | ContributionCalendar (daily heatmap) | POST | `/graphql` | - | no |
| `graphql-contributions-by-repository` | ContributionsCollection by-repository breakdowns | POST | `/graphql` | - | no |
| `graphql-search-issuecount` | search() aggregate counts (issueCount / repositoryCount / userCount / discussionCount) | POST | `/graphql` | - | no |
| `graphql-ratelimit` | rateLimit (budget introspection) | POST | `/graphql` | - | no |
| `graphql-organization-counts` | Organization rollup counts | POST | `/graphql` | - | no |
| `graphql-repository-counts` | Repository connection totalCounts | POST | `/graphql` | - | no |
| `graphql-enterprise-rollup` | Enterprise rollup (members/orgs/owner info) | POST | `/graphql` | - | no |
| `graphql-enterprise-billing-info` | EnterpriseBillingInfo (license/storage/bandwidth) | POST | `/graphql` | - | no |

### get-an-organization - Get an organization

**Request:** `GET https://api.github.com/orgs/{org}`

**Auth:** bearer - Classic PAT (admin:org) or fine-grained PAT

- Scopes: `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: No permission required for the public org view; full details require the caller to be an organization owner Confirmed on docs: classic PATs need admin:org to see FULL details, and the authenticated user must be an organization OWNER for plan/seat/private-repo/2FA fields. Public callers get a trimmed view. The docs page does not print a literal fine-grained permission string for the full view; owner-level org access is the practical gate.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | github |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Confirmed on docs: classic PATs need admin:org to see FULL details, and the authenticated user must be an organization OWNER for plan/seat/private-repo/2FA fields. Public callers get a trimmed view. The docs page does not print a literal fine-grained permission string for the full view; owner-level org access is the practical gate.

**Datapoints returned (12):**

- filled_seats - plan.filled_seats - paid seats currently consumed (owner-only)
- purchased_seats - plan.seats - total paid seats purchased (owner-only)
- plan_name - plan.name - subscription tier (owner-only)
- private_repo_quota - plan.private_repos / plan.space - allowances (owner-only)
- total_private_repos - Private repos owned by the org (owner-only)
- owned_private_repos - Owned (non-fork) private repos (owner-only)
- public_repos - Public repository count
- collaborators - Total collaborators across org repos (owner-only)
- disk_usage - Storage consumed in KB (owner-only)
- followers - Org follower count
- created_at - Org creation timestamp (tenure)
- two_factor_requirement_enabled - Whether org enforces 2FA (owner-only field)

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `plan.seats` | integer | Purchased seats |
| `plan.filled_seats` | integer | Consumed seats |
| `plan.name` | string | Plan tier |
| `total_private_repos` | integer | Private repo count |
| `disk_usage` | integer | Disk usage KB |
| `collaborators` | integer | Collaborator count |
| `two_factor_requirement_enabled` | boolean | 2FA enforced |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/orgs

**Source URLs:**
- https://docs.github.com/en/rest/orgs/orgs

---

### list-organizations-for-user - List organizations for the authenticated user / for a user

**Request:** `GET https://api.github.com/user/orgs and /users/{username}/orgs`

**Auth:** bearer - Classic PAT (read:org, user) or fine-grained PAT

- Scopes: `read:org`, `user`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: /users/{username}/orgs returns public memberships with no special permission Confirmed both paths exist on orgs page. /user/orgs lists the authenticated user's memberships; classic PAT needs read:org (or user). Public-membership variant needs no permission.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| username | path | no | For /users/{username}/orgs | octocat |
| per_page | query | no | max 100 | - |
| page | query | no | page number | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Confirmed both paths exist on orgs page. /user/orgs lists the authenticated user's memberships; classic PAT needs read:org (or user). Public-membership variant needs no permission.

**Datapoints returned (1):**

- org_membership_login - Organizations a user is a member of (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Org login |
| `[].id` | integer | Org id |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/orgs

**Source URLs:**
- https://docs.github.com/en/rest/orgs/orgs

---

### list-org-members - List organization members

**Request:** `GET https://api.github.com/orgs/{org}/members`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Fine-grained permission confirmed as 'Members: read' on the permissions reference page. filter=2fa_disabled/2fa_insecure require org owner. role=all/admin/member.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| filter | query | no | all / 2fa_disabled / 2fa_insecure (owner only) | - |
| role | query | no | all / admin / member | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Fine-grained permission confirmed as 'Members: read' on the permissions reference page. filter=2fa_disabled/2fa_insecure require org owner. role=all/admin/member.

**Datapoints returned (4):**

- member_login - Individual org members (seat occupancy roster) (PII)
- member_count - Total active members (derive via pagination last page or GraphQL totalCount)
- admin_count - Count of owners/admins via role=admin
- members_2fa_disabled - Members without 2FA (filter=2fa_disabled, owner only) (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Member login |
| `[].id` | integer | Member id |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/members

**Source URLs:**
- https://docs.github.com/en/rest/orgs/members
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### list-public-org-members - List public organization members

**Request:** `GET https://api.github.com/orgs/{org}/public_members`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: No special permission (public data) Publicly visible subset; readable without auth for public orgs.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Publicly visible subset; readable without auth for public orgs.

**Datapoints returned (1):**

- public_member_login - Members who made membership public (PII)

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Member login |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/members

**Source URLs:**
- https://docs.github.com/en/rest/orgs/members

---

### get-org-membership-for-user - Get organization membership for a user

**Request:** `GET https://api.github.com/orgs/{org}/memberships/{username}`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Returns state (active/pending) and role (admin/member).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| username | path | yes | User login | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Returns state (active/pending) and role (admin/member).

**Datapoints returned (2):**

- membership_state - active vs pending - seat provisioning lifecycle (PII)
- membership_role - admin (owner) vs member (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `state` | string | active\|pending |
| `role` | string | admin\|member |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/members

**Source URLs:**
- https://docs.github.com/en/rest/orgs/members

---

### list-pending-org-invitations - List pending organization invitations

**Request:** `GET https://api.github.com/orgs/{org}/invitations`

**Auth:** bearer - Classic PAT (admin:org) or fine-grained PAT

- Scopes: `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Fine-grained permission confirmed as 'Members: read' (NOT admin) on the permissions reference page; classic PAT path uses admin:org. role and invitation_source filters available.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| role | query | no | all/admin/direct_member/billing_manager/hiring_manager | - |
| invitation_source | query | no | all/member/scim | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Fine-grained permission confirmed as 'Members: read' (NOT admin) on the permissions reference page; classic PAT path uses admin:org. role and invitation_source filters available.

**Datapoints returned (4):**

- pending_invitation_count - Outstanding member invitations (onboarding funnel)
- invitee_email_or_login - Who is being onboarded (PII)
- invitation_role - Role being granted (incl. billing_manager)
- invitation_source - Manual (member) vs SCIM provisioning

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Invitee login |
| `[].email` | string | Invitee email |
| `[].role` | string | Role |
| `[].created_at` | string | Invited at |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/members

**Source URLs:**
- https://docs.github.com/en/rest/orgs/members
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### list-failed-org-invitations - List failed organization invitations

**Request:** `GET https://api.github.com/orgs/{org}/failed_invitations`

**Auth:** bearer - Classic PAT (admin:org) or fine-grained PAT

- Scopes: `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Fine-grained 'Members: read' confirmed. Provisioning-failure visibility.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Fine-grained 'Members: read' confirmed. Provisioning-failure visibility.

**Datapoints returned (2):**

- failed_invitation_count - Invitations that failed to provision
- failure_reason - failed_reason - why provisioning failed

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].failed_at` | string | Failure time |
| `[].failed_reason` | string | Reason |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/members

**Source URLs:**
- https://docs.github.com/en/rest/orgs/members
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### list-org-memberships-auth-user - List/Get organization memberships for the authenticated user

**Request:** `GET https://api.github.com/user/memberships/orgs and /user/memberships/orgs/{org}`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read state filter active/pending.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| state | query | no | active/pending | - |
| org | path | no | For the single-org variant | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. state filter active/pending.

**Datapoints returned (1):**

- user_org_membership_role - Authenticated user role/state per org (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].role` | string | admin\|member |
| `[].state` | string | active\|pending |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/members

**Source URLs:**
- https://docs.github.com/en/rest/orgs/members

---

### list-outside-collaborators - List outside collaborators for an organization

**Request:** `GET https://api.github.com/orgs/{org}/outside_collaborators`

**Auth:** bearer - Classic PAT (read:org, admin:org) or fine-grained PAT

- Scopes: `read:org`, `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Path and 'Members: read' fine-grained permission confirmed. filter=2fa_disabled/2fa_insecure (owner) for insecure collaborators.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| filter | query | no | all/2fa_disabled/2fa_insecure | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path and 'Members: read' fine-grained permission confirmed. filter=2fa_disabled/2fa_insecure (owner) for insecure collaborators.

**Datapoints returned (3):**

- outside_collaborator_count - Non-member external collaborators (access surface / non-seat consumers)
- outside_collaborator_login - External collaborator identities (PII)
- outside_collab_2fa_disabled - External collaborators without 2FA (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Collaborator login |
| `[].id` | integer | User id |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/outside-collaborators

**Source URLs:**
- https://docs.github.com/en/rest/orgs/outside-collaborators
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-all-org-roles - Get all organization roles

**Request:** `GET https://api.github.com/orgs/{org}/organization-roles`

**Auth:** bearer - Classic PAT (admin:org) or fine-grained PAT

- Scopes: `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization administration: read (or custom org role with manage roles) Path confirmed. Custom organization roles are a GitHub Enterprise Cloud feature (also on recent GHES >=3.13), NOT on standalone Free/Team orgs - confirmed via GA changelog and GHEC-scoped docs. Classic PAT admin:org. Returns total_count + roles[].

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed. Custom organization roles are a GitHub Enterprise Cloud feature (also on recent GHES >=3.13), NOT on standalone Free/Team orgs - confirmed via GA changelog and GHEC-scoped docs. Classic PAT admin:org. Returns total_count + roles[].

**Datapoints returned (2):**

- org_role_count - total_count of defined org roles (governance/RBAC maturity)
- role_base_permission - base_role + permissions per custom role

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | Number of roles |
| `roles[].name` | string | Role name |
| `roles[].base_role` | string | Base role |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/organization-roles

**Source URLs:**
- https://docs.github.com/en/rest/orgs/organization-roles
- https://github.blog/changelog/2023-11-16-custom-organization-roles-are-now-ga/

---

### list-users-assigned-org-role - List users assigned to an organization role

**Request:** `GET https://api.github.com/orgs/{org}/organization-roles/{role_id}/users`

**Auth:** bearer - Classic PAT (admin:org) or fine-grained PAT

- Scopes: `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization administration: read GHEC (and recent GHES). assignment field enum direct/indirect/mixed confirmed.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| role_id | path | yes | Role id | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. GHEC (and recent GHES). assignment field enum direct/indirect/mixed confirmed.

**Datapoints returned (2):**

- users_per_role - Who holds each custom role (privilege distribution) (PII)
- role_assignment_type - direct vs indirect (team-inherited) vs mixed assignment

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | User login |
| `[].assignment` | string | direct\|indirect\|mixed |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/organization-roles

**Source URLs:**
- https://docs.github.com/en/rest/orgs/organization-roles

---

### list-teams-assigned-org-role - List teams assigned to an organization role

**Request:** `GET https://api.github.com/orgs/{org}/organization-roles/{role_id}/teams`

**Auth:** bearer - Classic PAT (admin:org) or fine-grained PAT

- Scopes: `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization administration: read GHEC (and recent GHES).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| role_id | path | yes | Role id | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. GHEC (and recent GHES).

**Datapoints returned (1):**

- teams_per_role - Teams granted each custom role

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `[].name` | string | Team name |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/organization-roles

**Source URLs:**
- https://docs.github.com/en/rest/orgs/organization-roles

---

### list-teams - List teams

**Request:** `GET https://api.github.com/orgs/{org}/teams`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Confirmed. read:org for classic.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Confirmed. read:org for classic.

**Datapoints returned (2):**

- team_count - Number of teams (org structure/collaboration breadth)
- team_privacy - secret vs closed visibility

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].slug` | string | Team slug |
| `[].privacy` | string | Visibility |
| `[].parent` | object | Parent team for nesting |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/teams/teams

**Source URLs:**
- https://docs.github.com/en/rest/teams/teams

---

### get-team-by-name - Get a team by name (with member/repo counts)

**Request:** `GET https://api.github.com/orgs/{org}/teams/{team_slug}`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Confirmed: full Team object includes members_count and repos_count (absent from the list endpoint).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| team_slug | path | yes | Team slug | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Confirmed: full Team object includes members_count and repos_count (absent from the list endpoint).

**Datapoints returned (2):**

- team_members_count - members_count - team size
- team_repos_count - repos_count - repositories the team can access

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `members_count` | integer | Team member count |
| `repos_count` | integer | Team repo count |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/teams/teams

**Source URLs:**
- https://docs.github.com/en/rest/teams/teams

---

### list-child-teams - List child teams

**Request:** `GET https://api.github.com/orgs/{org}/teams/{team_slug}/teams`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Team hierarchy depth.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| team_slug | path | yes | Parent team slug | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Team hierarchy depth.

**Datapoints returned (1):**

- child_team_count - Nested team structure

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `[].slug` | string | Child team slug |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/teams/teams

**Source URLs:**
- https://docs.github.com/en/rest/teams/teams

---

### list-team-repos - List team repositories

**Request:** `GET https://api.github.com/orgs/{org}/teams/{team_slug}/repos`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Maps teams to repos and permission level (permissions object).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| team_slug | path | yes | Team slug | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Maps teams to repos and permission level (permissions object).

**Datapoints returned (1):**

- team_repo_access_map - Which repos a team accesses and at what permission

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].full_name` | string | Repo full name |
| `[].permissions` | object | admin/maintain/push/triage/pull |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/teams/teams

**Source URLs:**
- https://docs.github.com/en/rest/teams/teams

---

### list-team-members - List team members

**Request:** `GET https://api.github.com/orgs/{org}/teams/{team_slug}/members`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Includes child-team members. role filter member/maintainer/all.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| team_slug | path | yes | Team slug | - |
| role | query | no | member/maintainer/all | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Includes child-team members. role filter member/maintainer/all.

**Datapoints returned (2):**

- team_member_login - Roster of each team (PII)
- team_maintainer_count - Maintainers per team via role=maintainer

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Member login |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/teams/members

**Source URLs:**
- https://docs.github.com/en/rest/teams/members

---

### get-team-membership-for-user - Get team membership for a user

**Request:** `GET https://api.github.com/orgs/{org}/teams/{team_slug}/memberships/{username}`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Returns role (member/maintainer) and state (active/pending).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| team_slug | path | yes | Team slug | - |
| username | path | yes | User login | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Returns role (member/maintainer) and state (active/pending).

**Datapoints returned (1):**

- team_membership_role_state - Role and provisioning state in a team (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `role` | string | member\|maintainer |
| `state` | string | active\|pending |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/teams/members

**Source URLs:**
- https://docs.github.com/en/rest/teams/members

---

### list-team-pending-invitations - List pending team invitations

**Request:** `GET https://api.github.com/orgs/{org}/teams/{team_slug}/invitations`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization members: read Team-level onboarding pipeline.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| team_slug | path | yes | Team slug | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Team-level onboarding pipeline.

**Datapoints returned (1):**

- team_pending_invite_count - Outstanding team invitations

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Invitee |
| `[].role` | string | Role |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/teams/members

**Source URLs:**
- https://docs.github.com/en/rest/teams/members

---

### list-org-repositories - List organization repositories

**Request:** `GET https://api.github.com/orgs/{org}/repos`

**Auth:** bearer - Classic PAT (public_repo, repo) or fine-grained PAT

- Scopes: `public_repo`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Repository metadata: read Minimal Repository objects. security_and_analysis block needs repo admin/org owner/security manager. type/sort filters confirmed.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| type | query | no | all/public/private/forks/sources/member | - |
| sort | query | no | created/updated/pushed/full_name | - |
| direction | query | no | asc/desc | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Minimal Repository objects. security_and_analysis block needs repo admin/org owner/security manager. type/sort filters confirmed.

**Datapoints returned (10):**

- repo_count - Total repos in org (by type)
- repo_visibility_mix - public/private/internal breakdown via visibility field
- archived_disabled_count - archived / disabled repos (active vs dormant footprint)
- stargazers_count - Stars per repo
- forks_count - Forks per repo
- open_issues_count - Open issues+PRs per repo
- primary_language - language field per repo
- repo_size - size (KB) per repo - storage footprint
- pushed_at - Last push timestamp (active repo signal)
- created_at - Repo creation date (growth over time)

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `[].visibility` | string | public/private/internal |
| `[].language` | string | Primary language |
| `[].size` | integer | KB |
| `[].pushed_at` | string | Last push |
| `[].archived` | boolean | Archived |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/repos/repos

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos

---

### get-a-repository - Get a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}`

**Auth:** bearer - Classic PAT (public_repo, repo) or fine-grained PAT

- Scopes: `public_repo`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Repository metadata: read Full Repository object adds subscribers_count, network_count, topics, license, parent/source.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | Owner login | - |
| repo | path | yes | Repo name | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Full Repository object adds subscribers_count, network_count, topics, license, parent/source.

**Datapoints returned (6):**

- subscribers_count - Watchers subscribed to notifications
- network_count - Fork network size
- topics - topics[] - classification tags
- license - license.spdx_id - license adoption
- default_branch - Default branch name
- fork_flag - fork + parent/source - derivative vs original

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `subscribers_count` | integer | Subscribers |
| `network_count` | integer | Fork network |
| `topics` | array | Topic strings |
| `license.spdx_id` | string | License id |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/repos/repos

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos

---

### get-repository-topics - Get all repository topics

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/topics`

**Auth:** bearer - Classic PAT (public_repo, repo) or fine-grained PAT

- Scopes: `public_repo`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Repository metadata: read Returns names[].

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | Owner | - |
| repo | path | yes | Repo | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Returns names[].

**Datapoints returned (1):**

- repo_topics - Topic taxonomy applied to repo

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `names` | array | Topic strings |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/repos/repos

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos

---

### list-repository-languages-org - List repository languages

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/languages`

**Auth:** bearer - Classic PAT (public_repo, repo) or fine-grained PAT

- Scopes: `public_repo`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Repository metadata: read Returns map language -> bytes.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | Owner | - |
| repo | path | yes | Repo | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Returns map language -> bytes.

**Datapoints returned (1):**

- language_byte_breakdown - Bytes per language (tech-stack mix)

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `{language}` | integer | Bytes of that language |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/repos/repos

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos

---

### list-org-repository-rulesets - Get all organization repository rulesets

**Request:** `GET https://api.github.com/orgs/{org}/rulesets`

**Auth:** bearer - Classic PAT (admin:org, repo) or fine-grained PAT

- Scopes: `admin:org`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization administration: write MISSED by researcher. Confirmed on permissions reference: the GET (read) operation maps to Organization Administration: WRITE (read is insufficient) - a key gating gotcha. Governance maturity signal: count and enforcement status of org-level repo rulesets.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |
| per_page | query | no | max 100 | - |
| page | query | no | page | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Team (org rulesets are not available to Free organizations; available on Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED by researcher. Confirmed on permissions reference: the GET (read) operation maps to Organization Administration: WRITE (read is insufficient) - a key gating gotcha. Governance maturity signal: count and enforcement status of org-level repo rulesets.

**Datapoints returned (2):**

- org_ruleset_count - Number of org-level repo rulesets (policy governance breadth)
- ruleset_enforcement - enforcement field (active/evaluate/disabled) per ruleset

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].id` | integer | Ruleset id |
| `[].name` | string | Ruleset name |
| `[].enforcement` | string | active\|evaluate\|disabled |
| `[].target` | string | branch\|tag\|push\|repository |

**Plans/tiers:** Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/orgs/rules

**Source URLs:**
- https://docs.github.com/en/rest/orgs/rules
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### list-org-custom-properties - Get all custom properties for an organization

**Request:** `GET https://api.github.com/orgs/{org}/properties/schema`

**Auth:** bearer - Classic PAT (admin:org, read:org) or fine-grained PAT

- Scopes: `admin:org`, `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization custom properties: read MISSED by researcher. Custom properties are readable by org members; the schema lists defined properties. Companion GET /orgs/{org}/properties/values lists per-repo values. Governance/classification metadata for provisioned repos.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Org login | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: requires an ORGANIZATION (not personal accounts); the exact minimum org plan is NOT stated in GitHub docs — Free-org inclusion is UNVERIFIED (this is org-level repository custom properties via /orgs/{org}/properties/schema; distinct from enterprise-level 'organization custom properties', which are Enterprise-only). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Custom properties are readable by org members; the schema lists defined properties. Companion GET /orgs/{org}/properties/values lists per-repo values. Governance/classification metadata for provisioned repos.

**Datapoints returned (2):**

- custom_property_count - Number of defined org custom properties (metadata governance)
- custom_property_definitions - Property names, value types, and whether required on new repos

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].property_name` | string | Property name |
| `[].value_type` | string | string\|single_select\|multi_select\|true_false |
| `[].required` | boolean | Required on new repos |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/orgs/custom-properties

**Source URLs:**
- https://docs.github.com/en/rest/orgs/custom-properties

---

### get-enterprise-custom-properties - Get all custom properties for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/properties/schema`

**Auth:** bearer - Classic PAT (admin:enterprise / read:enterprise) or fine-grained PAT

- Scopes: `admin:enterprise`, `read:enterprise`
- Credential: GitHub PAT sent as Authorization: Bearer <token>. Enterprise members can read; admin:enterprise required for write.
- Notes: Enterprise-level custom properties (distinct from the org-level /orgs/{org}/properties/schema). Header X-GitHub-Api-Version: 2026-03-10. Added by the 2026-06-05 audit (axis B).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | Enterprise slug | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated).

**Gotchas:** Min plan: GitHub Enterprise (Cloud or Server) — enterprise-scoped governance API. GHES uses base https://HOST/api/v3. Companion PATCH/PUT/DELETE manage the schema (mutating, not catalogued). Enterprise-level properties can be promoted from org-level ones.

**Datapoints returned (2):**

- enterprise_custom_property_count - Number of enterprise-level custom properties defined (governance metadata footprint)
- enterprise_custom_property_definitions - Property names, value types, required flag, and allowed values at the enterprise level

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** verified: path, auth, datapoints; confidence: high; note: GET path/auth/response confirmed from official GitHub Enterprise docs; not live-tested (no enterprise-admin token swept) — doc-grounded.; source: https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/custom-properties

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/custom-properties

---

### graphql-org-aggregate-counts - GraphQL: organization aggregate counts (members/repos/teams)

**Purpose:** GraphQL query. Selection: organization(login){ membersWithRole{totalCount} repositories{totalCount} teams{totalCount} }

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (read:org, repo) or fine-grained PAT

- Scopes: `read:org`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Organization members: read; Repository metadata: read membersWithRole/repositories/teams connections all expose totalCount - confirmed via community-verified queries and the managing-enterprise-accounts guide. Single-call exact counts avoid paging thousands of REST results. Endpoint https://api.github.com/graphql (GHES: https://HOST/api/graphql). Upgraded to verified=true.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| login | body | yes | Org login | github |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. membersWithRole/repositories/teams connections all expose totalCount - confirmed via community-verified queries and the managing-enterprise-accounts guide. Single-call exact counts avoid paging thousands of REST results. Endpoint https://api.github.com/graphql (GHES: https://HOST/api/graphql). Upgraded to verified=true.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (3):**

- members_total_count - membersWithRole.totalCount - exact active member count in one query
- repositories_total_count - repositories.totalCount
- teams_total_count - teams.totalCount

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `data.organization.membersWithRole.totalCount` | integer | Members |
| `data.organization.repositories.totalCount` | integer | Repos |
| `data.organization.teams.totalCount` | integer | Teams |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/graphql/reference/objects
- https://docs.github.com/en/enterprise-cloud@latest/graphql/guides/managing-enterprise-accounts

---

### get-contributor-commit-activity - Get all contributor commit activity

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/stats/contributors`

**Auth:** bearer - Classic PAT (repo (private repos), public_repo or no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `public_repo or no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read Fine-grained PAT requires Repository permissions for Metadata (read), confirmed on the FG PAT permissions page. Works unauthenticated for public repos. Author objects expose individual logins (PII). Returns 202 while statistics are still being computed (cache warming) — retry. Returns 0 for all addition/deletion counts in repos with 10,000+ commits.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Fine-grained PAT requires Repository permissions for Metadata (read), confirmed on the FG PAT permissions page. Works unauthenticated for public repos. Author objects expose individual logins (PII). Returns 202 while statistics are still being computed (cache warming) — retry. Returns 0 for all addition/deletion counts in repos with 10,000+ commits.

**Datapoints returned (5):**

- contributor_total_commits - Total number of commits authored by each contributor. (PII)
- contributor_weekly_additions - Per-contributor weekly additions (a), starting Sunday. Returns 0 for repos with 10,000+ commits. (PII)
- contributor_weekly_deletions - Per-contributor weekly deletions (d). Returns 0 for repos with 10,000+ commits. (PII)
- contributor_weekly_commits - Per-contributor weekly commit count (c) keyed by Unix week timestamp (w). (PII)
- contributor_count - Number of distinct contributors (length of returned array).

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `[].author` | object\|null | Simple user object for the contributor (login, id) — PII. |
| `[].total` | integer | Total commits by this author. |
| `[].weeks[].w` | integer | Unix timestamp (start of week, Sunday UTC). |
| `[].weeks[].a` | integer | Additions that week. |
| `[].weeks[].d` | integer | Deletions that week. |
| `[].weeks[].c` | integer | Commits that week. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 202; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-commit-activity - Get the last year of commit activity

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/stats/commit_activity`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos. Returns last 52 weeks grouped by week. Returns 202 while computing.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos. Returns last 52 weeks grouped by week. Returns 202 while computing.

**Datapoints returned (2):**

- weekly_commit_total - Total commits per week over the last year.
- daily_commit_distribution - Commits per day within each week (array of 7, starting Sunday).

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].week` | integer | Unix timestamp for the week. |
| `[].total` | integer | Total commits that week. |
| `[].days` | array[integer] | Commits per day, index 0=Sunday..6=Saturday. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 202; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-code-frequency - Get the weekly commit activity (code frequency)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/stats/code_frequency`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos. Returns 202 while computing. Returns 422 for repos with 10,000 or more commits (endpoint only supports repos with fewer than 10,000 commits).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos. Returns 202 while computing. Returns 422 for repos with 10,000 or more commits (endpoint only supports repos with fewer than 10,000 commits).

**Datapoints returned (3):**

- weekly_additions - Lines of code added per week across the whole repo history.
- weekly_deletions - Lines of code deleted per week (returned as a negative number).
- code_churn - Net additions+deletions per week (code churn / velocity proxy), derived.

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `[]` | array[integer] | Each entry is [unix_week_timestamp, additions, deletions]. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 202; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-participation - Get the weekly commit count (participation)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/stats/participation`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read FG PAT permission Metadata: read. Unauthenticated for public repos. Returns 52 weeks. No 202/422 documented for this endpoint.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. FG PAT permission Metadata: read. Unauthenticated for public repos. Returns 52 weeks. No 202/422 documented for this endpoint.

**Datapoints returned (2):**

- weekly_commits_all - Total commit count by everyone (including owner) per week over last 52 weeks.
- weekly_commits_owner - Commit count by the repo owner per week — distinguishes owner vs community activity.

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `all` | array[integer] | 52 weekly totals for all contributors. |
| `owner` | array[integer] | 52 weekly totals for the owner only. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-punch-card - Get the hourly commit count for each day (punch card)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/stats/punch_card`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read FG PAT permission Metadata: read. Unauthenticated for public repos. May return 204 (no content) for repos with no data. Times based on each commit's own time zone.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. FG PAT permission Metadata: read. Unauthenticated for public repos. May return 204 (no content) for repos with no data. Times based on each commit's own time zone.

**Datapoints returned (1):**

- commits_by_day_hour - Number of commits per (day-of-week, hour-of-day) bucket — reveals team working-hours patterns.

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `[]` | array[integer] | Each entry is [day(0-6 Sun-Sat), hour(0-23), commit_count]. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-traffic-views - Get repository page views

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/traffic/views`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read as researcher claimed). Confirmed on the FG PAT permissions page. HOWEVER, the caller's repository ROLE must have write/push access — the traffic API docs state these endpoints work only 'for repositories that you have write access to.' So the gating is role-based (write/push access) plus a Metadata:read-scoped token; the elevated permission is NOT Administration. No anonymous/public read of traffic data.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| per | query | no | day (default) or week | week |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read as researcher claimed). Confirmed on the FG PAT permissions page. HOWEVER, the caller's repository ROLE must have write/push access — the traffic API docs state these endpoints work only 'for repositories that you have write access to.' So the gating is role-based (write/push access) plus a Metadata:read-scoped token; the elevated permission is NOT Administration. No anonymous/public read of traffic data.

**Datapoints returned (3):**

- total_views_14d - Total page views in the last 14 days.
- unique_visitors_14d - Unique visitors in the last 14 days.
- views_timeseries - Per-day or per-week breakdown of views and uniques over 14 days.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `count` | integer | Total views over 14 days. |
| `uniques` | integer | Unique visitors over 14 days. |
| `views[].timestamp` | string(date-time) | Bucket start time. |
| `views[].count` | integer | Views in bucket. |
| `views[].uniques` | integer | Unique visitors in bucket. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-traffic-clones - Get repository clones

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/traffic/clones`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read). Confirmed on FG PAT permissions page. Caller role must have write/push access to the repo. Counts full clones, not fetches.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| per | query | no | day (default) or week | week |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read). Confirmed on FG PAT permissions page. Caller role must have write/push access to the repo. Counts full clones, not fetches.

**Datapoints returned (3):**

- total_clones_14d - Total full clones in last 14 days.
- unique_cloners_14d - Unique cloners in last 14 days.
- clones_timeseries - Per-day or per-week clone and unique counts over 14 days.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `count` | integer | Total clones over 14 days. |
| `uniques` | integer | Unique cloners over 14 days. |
| `clones[].timestamp` | string(date-time) | Bucket start time. |
| `clones[].count` | integer | Clones in bucket. |
| `clones[].uniques` | integer | Unique cloners in bucket. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-traffic-popular-referrers - Get top referral sources

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/traffic/popular/referrers`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read). Caller role must have write/push access. Returns top 10 referrers over last 14 days. No 'per' parameter.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read). Caller role must have write/push access. Returns top 10 referrers over last 14 days. No 'per' parameter.

**Datapoints returned (1):**

- top_referrers - Top 10 referring sites with view counts and unique visitors (last 14 days).

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].referrer` | string | Referring site name. |
| `[].count` | integer | Views from this referrer. |
| `[].uniques` | integer | Unique visitors from this referrer. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-traffic-popular-paths - Get top referral paths

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/traffic/popular/paths`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read). Caller role must have write/push access. Returns top 10 popular content paths over last 14 days. No 'per' parameter.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. CORRECTION: FG PAT permission is Metadata: read (NOT Administration: read). Caller role must have write/push access. Returns top 10 popular content paths over last 14 days. No 'per' parameter.

**Datapoints returned (1):**

- top_content_paths - Top 10 visited paths/pages within the repo with views and uniques (last 14 days).

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].path` | string | Repo path. |
| `[].title` | string | Page title. |
| `[].count` | integer | Views of this path. |
| `[].uniques` | integer | Unique visitors of this path. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/traffic?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-community-profile - Get community profile metrics

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/community/profile`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read FG PAT permission confirmed as Contents: read on the FG PAT permissions page. The repository cannot be a fork. content_reports_enabled returned only for organization-owned repos.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. FG PAT permission confirmed as Contents: read on the FG PAT permissions page. The repository cannot be a fork. content_reports_enabled returned only for organization-owned repos.

**Datapoints returned (8):**

- community_health_percentage - Overall community health score (0-100) based on presence of recommended community health files.
- has_readme - Presence/details of README file.
- has_license - Presence of a recognized LICENSE.
- has_code_of_conduct - Presence of a code of conduct.
- has_contributing - Presence of CONTRIBUTING guidelines.
- has_issue_template - Presence of an issue template.
- has_pull_request_template - Presence of a PR template.
- content_reports_enabled - Whether content reporting is enabled (org-owned repos only).

**Report / response file fields (11):**

| path | type | description |
| --- | --- | --- |
| `health_percentage` | integer | Community health score 0-100. |
| `description` | string\|null | Repo description. |
| `documentation` | string\|null | Documentation URL/indicator. |
| `files.code_of_conduct` | object\|null | Code of conduct metadata. |
| `files.license` | object\|null | License metadata (key, name, spdx_id, node_id). |
| `files.contributing` | object\|null | Contributing file metadata. |
| `files.readme` | object\|null | README metadata. |
| `files.issue_template` | object\|null | Issue template metadata. |
| `files.pull_request_template` | object\|null | PR template metadata. |
| `updated_at` | string(date-time)\|null | Last update timestamp. |
| `content_reports_enabled` | boolean | Org-owned repos only. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/metrics/community?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/metrics/community?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### list-repository-languages-traffic - List repository languages

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/languages`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos.

**Datapoints returned (1):**

- language_byte_breakdown - Map of programming language -> bytes of code; tech-stack composition / language mix. Recategorized from engagement to adoption (tech-stack adoption signal).

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `<language>` | integer | Bytes of code in that language (object with language-name keys). |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### get-repository-popularity-counts - Get a repository (popularity / engagement counts)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos. Single-call source for star/fork/watcher/subscriber counts. Note: subscribers_count and network_count appear in the single-repo GET but not in list responses.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. FG PAT permission confirmed as Metadata: read. Unauthenticated for public repos. Single-call source for star/fork/watcher/subscriber counts. Note: subscribers_count and network_count appear in the single-repo GET but not in list responses.

**Datapoints returned (9):**

- stargazers_count - Number of users who starred the repo.
- watchers_count - Watchers count (in REST v3, equals stargazers_count — historical quirk).
- subscribers_count - Actual number of users watching/subscribed for notifications (true watcher count).
- forks_count - Number of forks.
- network_count - Size of the fork network.
- open_issues_count - Open issues + open PRs count.
- size - Repository size in KB.
- pushed_at - Timestamp of last push (recency of activity).
- archived_disabled - archived/disabled flags indicating repo maintenance state.

**Report / response file fields (8):**

| path | type | description |
| --- | --- | --- |
| `stargazers_count` | integer | Stars. |
| `watchers_count` | integer | Watchers (= stars in v3). |
| `subscribers_count` | integer | Subscribers (true watchers). |
| `forks_count` | integer | Forks. |
| `network_count` | integer | Fork network size. |
| `open_issues_count` | integer | Open issues + PRs. |
| `size` | integer | Size in KB. |
| `pushed_at` | string(date-time) | Last push. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### list-repository-activity - List repository activity

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/activity`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read MISSED BY RESEARCHER. Returns a timeline of repository activity events (pushes, force-pushes, branch creation/deletion, PR merges, merge-queue merges) with the acting user. actor exposes individual logins (PII). Supports cursor pagination and filtering by actor, ref, time_period, activity_type. FG PAT permission is Contents: read per the FG PAT permissions page.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| direction | query | no | asc or desc | - |
| per_page | query | no | results per page (max 100) | - |
| before | query | no | cursor pagination | - |
| after | query | no | cursor pagination | - |
| ref | query | no | filter by branch/ref | - |
| actor | query | no | filter by username | - |
| time_period | query | no | day\|week\|month\|quarter\|year | - |
| activity_type | query | no | push\|force_push\|branch_creation\|branch_deletion\|pr_merge\|merge_queue_merge | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED BY RESEARCHER. Returns a timeline of repository activity events (pushes, force-pushes, branch creation/deletion, PR merges, merge-queue merges) with the acting user. actor exposes individual logins (PII). Supports cursor pagination and filtering by actor, ref, time_period, activity_type. FG PAT permission is Contents: read per the FG PAT permissions page.

**Datapoints returned (3):**

- activity_events - Push / force-push / branch creation / branch deletion / PR-merge / merge-queue-merge events with timestamps — granular activity-flow signal. (PII)
- force_push_count - Count of force-push events (derived) — a hygiene/quality signal for history rewriting.
- actor_per_event - Acting user per event (login) — who did what; per-developer activity attribution. (PII)

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `[].id` | integer | Activity id. |
| `[].timestamp` | string(date-time) | When the activity occurred. |
| `[].activity_type` | string | push\|force_push\|branch_creation\|branch_deletion\|pr_merge\|merge_queue_merge. |
| `[].actor` | object\|null | Simple user object — PII. |
| `[].ref` | string | Git ref affected. |
| `[].before` | string | Commit SHA before. |
| `[].after` | string | Commit SHA after. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### list-repository-contributors - List repository contributors

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/contributors`

**Auth:** bearer - Classic PAT (repo (private repos), no scope (public repos)) or fine-grained PAT

- Scopes: `repo (private repos)`, `no scope (public repos)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read MISSED BY RESEARCHER. Lighter-weight than stats/contributors and not subject to the 202/cache-warming behavior; returns per-user lifetime contribution counts. Each contributor exposes login (PII). anon=1 includes anonymous contributors by email.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| anon | query | no | Set to 1/true to include anonymous contributors. | - |
| per_page | query | no | results per page (max 100) | - |
| page | query | no | page number | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED BY RESEARCHER. Lighter-weight than stats/contributors and not subject to the 202/cache-warming behavior; returns per-user lifetime contribution counts. Each contributor exposes login (PII). anon=1 includes anonymous contributors by email.

**Datapoints returned (2):**

- contributor_contributions - Lifetime commit contribution count per contributor. (PII)
- contributor_count - Distinct contributor count (via pagination).

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].login` | string | Contributor login — PII. |
| `[].id` | integer | User id. |
| `[].contributions` | integer | Number of contributions (commits) by this user. |
| `[].type` | string | User or Bot. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens

---

### graphql-repository-engagement - Repository object engagement fields (GraphQL)

**Purpose:** GraphQL query. Selection: repository (stargazerCount, forkCount, watchers, diskUsage, pushedAt, isArchived, primaryLanguage, languages)

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (repo (private repos), read:org for org-scoped fields) or fine-grained PAT

- Scopes: `repo (private repos)`, `read:org for org-scoped fields`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Metadata: read NOT CONFIRMED THIS SESSION: GraphQL reference object page (docs.github.com/en/graphql/reference/objects) is JavaScript-rendered and field-level schema could not be extracted via fetch. stargazerCount/forkCount/watchers/diskUsage/languages field names are from established schema knowledge, NOT a confirmed doc fetch. Re-verify via introspection before publication. Lets you batch popularity + language data across many repos in one query.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| query | body | yes | GraphQL query selecting repository(owner,name){ stargazerCount forkCount watchers{totalCount} diskUsage pushedAt isArchived primaryLanguage{name} languages{edges{size node{name}}} } | - |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. NOT CONFIRMED THIS SESSION: GraphQL reference object page (docs.github.com/en/graphql/reference/objects) is JavaScript-rendered and field-level schema could not be extracted via fetch. stargazerCount/forkCount/watchers/diskUsage/languages field names are from established schema knowledge, NOT a confirmed doc fetch. Re-verify via introspection before publication. Lets you batch popularity + language data across many repos in one query.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (6):**

- stargazerCount - Star count (GraphQL Int).
- forkCount - Fork count.
- watchers_totalCount - Number of watchers via watchers.totalCount.
- diskUsage - Repo size in KB.
- languages_size - Per-language byte size with ordering, exposes percentages REST lacks.
- pushedAt - Last push time.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `data.repository.stargazerCount` | Int | Stars. |
| `data.repository.forkCount` | Int | Forks. |
| `data.repository.watchers.totalCount` | Int | Watchers. |
| `data.repository.diskUsage` | Int | Size KB. |
| `data.repository.languages.edges[].size` | Int | Bytes per language. |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/graphql/reference/objects

---

### list-commits - List commits

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read public_repo for public repos; repo for private. Fine-grained Contents: read.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. public_repo for public repos; repo for private. Fine-grained Contents: read.

**Datapoints returned (4):**

- commit_count - Number of commits in a range/branch
- commit_authored_date - Authorship timestamp for time-series
- commit_author_login - Author identity per commit (PII)
- merge_commit_indicator - parents.length>1 marks merge commits

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/commits

**Source URLs:**
- https://docs.github.com/en/rest/commits/commits

---

### get-commit - Get a commit

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits/{ref}`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read Supports diff/patch media types. Diffs >300 files paginate.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Supports diff/patch media types. Diffs >300 files paginate.

**Datapoints returned (3):**

- commit_churn - additions+deletions per commit
- commit_files_changed - files modified per commit
- commit_signature_verified - GPG/SSH/S-MIME signature verification status

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/commits

**Source URLs:**
- https://docs.github.com/en/rest/commits/commits

---

### compare-commits - Compare two commits

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/compare/{basehead}`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read basehead = BASE...HEAD. Caps at 250 commits; files only on page 1.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. basehead = BASE...HEAD. Caps at 250 commits; files only on page 1.

**Datapoints returned (2):**

- diff_size_between_refs - aggregate additions/deletions/files between refs
- branch_divergence - ahead_by/behind_by commit counts

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/commits#compare-two-commits

**Source URLs:**
- https://docs.github.com/en/rest/commits/commits#compare-two-commits

---

### list-pull-requests-associated-with-commit - List pull requests associated with a commit

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/pulls`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read; Contents: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- commit_to_pr_linkage - Maps commit SHA to merging/introducing PRs

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/commits#list-pull-requests-associated-with-a-commit

**Source URLs:**
- https://docs.github.com/en/rest/commits/commits#list-pull-requests-associated-with-a-commit

---

### list-commit-comments-repo - List commit comments for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/comments`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read Corrected: public_repo also works for public repos (researcher listed only repo).

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Corrected: public_repo also works for public repos (researcher listed only repo).

**Datapoints returned (2):**

- commit_comment_volume - Count of standalone commit comments
- commit_comment_author - Commit comment author login (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/comments

**Source URLs:**
- https://docs.github.com/en/rest/commits/comments

---

### list-commit-comments-for-commit - List commit comments (for a commit)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/comments`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read Corrected: public_repo also valid.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Corrected: public_repo also valid.

**Datapoints returned (1):**

- per_commit_comment_count - Comments on a specific commit

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/comments

**Source URLs:**
- https://docs.github.com/en/rest/commits/comments

---

### list-pull-requests - List pull requests

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (5):**

- pr_count_by_state - Open/closed/merged PR counts
- pr_open_to_merge_time - merged_at - created_at lead time
- pr_author - PR creator login (PII)
- pr_draft_ratio - Share of PRs in draft
- pr_target_branch - base branch distribution

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/pulls

**Source URLs:**
- https://docs.github.com/en/rest/pulls/pulls

---

### get-pull-request - Get a pull request

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read Only single-PR GET returns additions/deletions/changed_files/commits/mergeable.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Only single-PR GET returns additions/deletions/changed_files/commits/mergeable.

**Datapoints returned (5):**

- pr_size_additions_deletions - PR change size
- pr_commit_count - commits per PR
- pr_review_comment_count - review_comments review-depth signal
- pr_merge_readiness - mergeable_state
- pr_cycle_time - merged_at/closed_at - created_at

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request

**Source URLs:**
- https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request

---

### list-commits-on-pull-request - List commits on a pull request

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/commits`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read Max 250 commits. Contents:read not strictly required (Pull requests:read suffices).

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Max 250 commits. Contents:read not strictly required (Pull requests:read suffices).

**Datapoints returned (2):**

- pr_first_commit_time - Earliest commit authored date — coding-start anchor
- pr_commit_timeline - Commit cadence within a PR

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/pulls#list-commits-on-a-pull-request

**Source URLs:**
- https://docs.github.com/en/rest/pulls/pulls#list-commits-on-a-pull-request

---

### list-pull-request-files - List pull request files

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read Max 3000 files; 30/page default.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Max 3000 files; 30/page default.

**Datapoints returned (2):**

- pr_file_level_churn - Per-file additions/deletions
- pr_file_types_touched - Distribution of file paths/extensions

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files

**Source URLs:**
- https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files

---

### check-pull-request-merged - Check if a pull request has been merged

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/merge`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read 204=merged, 404=not merged.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. 204=merged, 404=not merged.

**Datapoints returned (1):**

- pr_merged_boolean - Lightweight merged check

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/pulls#check-if-a-pull-request-has-been-merged

**Source URLs:**
- https://docs.github.com/en/rest/pulls/pulls#check-if-a-pull-request-has-been-merged

---

### list-pull-request-reviews - List reviews for a pull request

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (4):**

- pr_review_latency - first submitted_at - created_at
- pr_review_decision_breakdown - APPROVED/CHANGES_REQUESTED/COMMENTED counts
- reviewer_identity - Reviewer login (PII)
- review_count_per_pr - Number of review rounds

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/reviews

**Source URLs:**
- https://docs.github.com/en/rest/pulls/reviews

---

### get-pull-request-review - Get a review for a pull request

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- single_review_detail - State/body/timestamp of one review

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/reviews#get-a-review-for-a-pull-request

**Source URLs:**
- https://docs.github.com/en/rest/pulls/reviews#get-a-review-for-a-pull-request

---

### list-review-comments-for-review - List comments for a pull request review

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/comments`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- review_inline_comment_count - Inline comments attached to a review

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/reviews#list-comments-for-a-pull-request-review

**Source URLs:**
- https://docs.github.com/en/rest/pulls/reviews#list-comments-for-a-pull-request-review

---

### get-requested-reviewers - Get all requested reviewers for a pull request

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (2):**

- pending_reviewer_load - Outstanding review requests per PR
- requested_reviewer_identity - Who is asked to review (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/review-requests

**Source URLs:**
- https://docs.github.com/en/rest/pulls/review-requests

---

### list-review-comments-on-pull-request - List review comments on a pull request

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (3):**

- pr_inline_comment_volume - Total inline review comments per PR
- review_comment_threading - Reply chains via in_reply_to_id
- review_comment_author - Commenter login (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/comments

**Source URLs:**
- https://docs.github.com/en/rest/pulls/comments

---

### list-review-comments-in-repository - List review comments in a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/comments`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- repo_review_comment_activity - Repo-wide review comment time-series

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/pulls/comments#list-review-comments-in-a-repository

**Source URLs:**
- https://docs.github.com/en/rest/pulls/comments#list-review-comments-in-a-repository

---

### list-repository-issues - List repository issues

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read; Pull requests: read PRs returned too; pull_request field distinguishes. Pull requests:read needed to surface PR entries.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. PRs returned too; pull_request field distinguishes. Pull requests:read needed to surface PR entries.

**Datapoints returned (5):**

- issue_count_by_state - Open/closed counts with state_reason
- issue_resolution_time - closed_at - created_at
- issue_label_distribution - Label/type breakdown
- issue_comment_count - comments field discussion volume
- issue_assignee - Assigned owner(s) (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/issues

**Source URLs:**
- https://docs.github.com/en/rest/issues/issues

---

### get-issue - Get an issue

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read; Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (2):**

- issue_closer_identity - closed_by login (PII)
- issue_detail_resolution - Single-issue close time and reason

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/issues#get-an-issue

**Source URLs:**
- https://docs.github.com/en/rest/issues/issues#get-an-issue

---

### list-user-assigned-issues - List issues assigned to the authenticated user

**Request:** `GET https://api.github.com/issues`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- user_issue_workload - Issues assigned to/created by the authenticated user across repos (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/issues#list-issues-assigned-to-the-authenticated-user

**Source URLs:**
- https://docs.github.com/en/rest/issues/issues#list-issues-assigned-to-the-authenticated-user

---

### list-org-assigned-issues - List organization issues assigned to the authenticated user

**Request:** `GET https://api.github.com/orgs/{org}/issues`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- org_user_issue_workload - Org-scoped assigned issue count for a user (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/issues#list-organization-issues-assigned-to-the-authenticated-user

**Source URLs:**
- https://docs.github.com/en/rest/issues/issues#list-organization-issues-assigned-to-the-authenticated-user

---

### list-issue-events-for-repository - List issue events for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/events`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (2):**

- issue_lifecycle_events - Repo-wide state-change events with timestamps
- event_actor - Who performed each event (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/events

**Source URLs:**
- https://docs.github.com/en/rest/issues/events

---

### list-issue-events - List events for an issue

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/events`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- per_issue_event_history - Ordered lifecycle events for time-in-state analysis

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/events#list-issue-events

**Source URLs:**
- https://docs.github.com/en/rest/issues/events#list-issue-events

---

### list-issue-timeline - List timeline events for an issue

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/timeline`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read; Pull requests: read Richest event source; works on issues and PRs.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Richest event source; works on issues and PRs.

**Datapoints returned (3):**

- pr_review_request_to_review_latency - Gap between review_requested and reviewed events
- cross_reference_links - Linked issues/PRs via cross-referenced events
- full_lifecycle_timeline - Unified ordered event log for stage-by-stage cycle time

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/timeline

**Source URLs:**
- https://docs.github.com/en/rest/issues/timeline

---

### list-issue-comments-repo - List issue comments for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/comments`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read Corrected: public_repo also valid (researcher listed only repo).

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Corrected: public_repo also valid (researcher listed only repo).

**Datapoints returned (1):**

- repo_issue_comment_activity - Repo-wide issue/PR comment time-series

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/comments

**Source URLs:**
- https://docs.github.com/en/rest/issues/comments

---

### list-issue-comments - List comments on an issue

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read Corrected: public_repo also valid.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Corrected: public_repo also valid.

**Datapoints returned (1):**

- per_issue_comment_timeline - Comment timestamps for time-to-first-response

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/comments#list-issue-comments

**Source URLs:**
- https://docs.github.com/en/rest/issues/comments#list-issue-comments

---

### list-milestones - List milestones

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/milestones`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read Corrected: docs list Issues:read for milestones; researcher hedging removed. public_repo valid.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Corrected: docs list Issues:read for milestones; researcher hedging removed. public_repo valid.

**Datapoints returned (2):**

- milestone_progress - open vs closed issues completion ratio
- milestone_due_vs_close - due_on vs closed_at on-time delivery

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/milestones

**Source URLs:**
- https://docs.github.com/en/rest/issues/milestones

---

### get-milestone - Get a milestone

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/milestones/{milestone_number}`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- single_milestone_progress - Completion counts for one milestone

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/milestones#get-a-milestone

**Source URLs:**
- https://docs.github.com/en/rest/issues/milestones#get-a-milestone

---

### list-repository-labels - List labels for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/labels`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read Corrected: Issues:read is the fine-grained permission; researcher hedging removed.

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Corrected: Issues:read is the fine-grained permission; researcher hedging removed.

**Datapoints returned (1):**

- label_taxonomy - Available labels for classifying issue/PR type/priority/area

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/labels

**Source URLs:**
- https://docs.github.com/en/rest/issues/labels

---

### list-labels-for-issue - List labels for an issue

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/labels`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- issue_labels - Labels on one issue/PR

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/labels#list-labels-for-an-issue

**Source URLs:**
- https://docs.github.com/en/rest/issues/labels#list-labels-for-an-issue

---

### list-assignees - List assignees

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/assignees`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- assignable_users - Set of users assignable in the repo — collaborator roster (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/issues/assignees

**Source URLs:**
- https://docs.github.com/en/rest/issues/assignees

---

### list-issue-reactions - List reactions for an issue

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/reactions`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (2):**

- issue_reaction_counts - Reaction volume/type on an issue — lightweight sentiment/engagement
- issue_reaction_user - Reacting user login (PII)

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-an-issue

**Source URLs:**
- https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-an-issue

---

### list-issue-comment-reactions - List reactions for an issue comment

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- issue_comment_reaction_counts - Reactions on an issue/PR comment

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-an-issue-comment

**Source URLs:**
- https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-an-issue-comment

---

### list-pr-review-comment-reactions - List reactions for a pull request review comment

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Pull requests: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- pr_review_comment_reaction_counts - Reactions on inline PR review comments

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-a-pull-request-review-comment

**Source URLs:**
- https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-a-pull-request-review-comment

---

### list-commit-comment-reactions - List reactions for a commit comment

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/comments/{comment_id}/reactions`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- commit_comment_reaction_counts - Reactions on commit comments

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-a-commit-comment

**Source URLs:**
- https://docs.github.com/en/rest/reactions/reactions#list-reactions-for-a-commit-comment

---

### list-sub-issues - List sub-issues

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/sub_issues`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Issues: read

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- sub_issue_breakdown - Parent/child issue decomposition — work breakdown and completion of sub-tasks

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/issues/sub-issues

**Source URLs:**
- https://docs.github.com/en/rest/issues/sub-issues

---

### graphql-pullrequest-metrics - GraphQL PullRequest review/cycle metrics

**Purpose:** GraphQL query. Selection: repository.pullRequests.nodes { additions deletions changedFiles createdAt closedAt mergedAt mergedBy reviewDecision reviews latestReviews reviewThreads timelineItems totalCommentsCount }

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Pull requests: read; Contents: read Single POST to /graphql; batches PR + reviews + threads + size in one round-trip.

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Single POST to /graphql; batches PR + reviews + threads + size in one round-trip.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (5):**

- pr_review_decision - Aggregate reviewDecision per PR (not in REST)
- resolved_review_thread_ratio - isResolved across reviewThreads
- pr_size_in_list_query - additions/deletions/changedFiles for many PRs in one call
- review_thread_resolver - resolvedBy user per thread (PII)
- stage_cycle_time - timelineItems timestamps for granular cycle-time stages

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/graphql/reference/objects#pullrequest

**Source URLs:**
- https://docs.github.com/en/graphql/reference/objects#pullrequest
- https://docs.github.com/en/graphql/reference/objects#pullrequestreviewthread

---

### list-workflow-runs-repo - List workflow runs for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Public repos readable unauthenticated; private repos need repo scope (classic) or Actions:read (fine-grained). Fine-grained 'Actions: read' confirmed by the shared Actions permission model (artifacts page states it explicitly); the workflow-runs page itself only names the classic repo scope in prose.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| actor | query | no | filter by user who triggered run | - |
| branch | query | no | - | - |
| event | query | no | e.g. push, deployment, release, workflow_dispatch | - |
| status | query | no | status or conclusion, e.g. success, failure, in_progress | - |
| created | query | no | date-time range filter | >=2026-01-01 |
| exclude_pull_requests | query | no | - | - |
| check_suite_id | query | no | - | - |
| head_sha | query | no | - | - |
| per_page | query | no | - | 100 |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Public repos readable unauthenticated; private repos need repo scope (classic) or Actions:read (fine-grained). Fine-grained 'Actions: read' confirmed by the shared Actions permission model (artifacts page states it explicitly); the workflow-runs page itself only names the classic repo scope in prose.

**Datapoints returned (6):**

- deployment_frequency_input - Count of runs of a deploy workflow per time window (filter event/branch/status, group by created_at) = canonical Actions-based deployment frequency signal.
- run_conclusion - conclusion (success/failure/cancelled/...) per run; failure ratio over deploy-workflow runs approximates change-failure-rate.
- run_status - status (queued/in_progress/completed/waiting/requested/pending) — in-flight pipeline state.
- lead_time_input - head_sha + created_at vs the commit author/commit date enables lead-time-for-changes derivation.
- run_attempt_count - run_attempt > 1 indicates re-runs/retries — pipeline flakiness signal.
- triggering_actor - actor/triggering_actor login on the run — who triggered the pipeline. (PII)

**Report / response file fields (11):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `workflow_runs[].id` | integer | - |
| `workflow_runs[].workflow_id` | integer | - |
| `workflow_runs[].status` | string | - |
| `workflow_runs[].conclusion` | string\|null | - |
| `workflow_runs[].event` | string | - |
| `workflow_runs[].run_attempt` | integer | - |
| `workflow_runs[].head_sha` | string | - |
| `workflow_runs[].created_at` | date-time | - |
| `workflow_runs[].run_started_at` | date-time | run_started_at -> updated_at = run duration |
| `workflow_runs[].updated_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs

---

### get-workflow-run - Get a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read repo scope only needed for private repos.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| exclude_pull_requests | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. repo scope only needed for private repos.

**Datapoints returned (2):**

- run_duration_derived - run_started_at -> updated_at yields per-run cycle time.
- run_conclusion - conclusion of a specific run — pass/fail for change-failure-rate numerator.

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `status` | string | - |
| `conclusion` | string\|null | - |
| `run_attempt` | integer | - |
| `run_started_at` | date-time | - |
| `updated_at` | date-time | - |
| `head_sha` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs

---

### get-workflow-run-attempt - Get a workflow run attempt

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Per-attempt detail for retry/recovery analysis.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| attempt_number | path | yes | - | - |
| exclude_pull_requests | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Per-attempt detail for retry/recovery analysis.

**Datapoints returned (2):**

- attempt_timing - run_started_at/updated_at for a specific attempt — recovery/retry duration after a failed attempt.
- attempt_conclusion - conclusion per attempt — distinguishes transient failures resolved by re-run.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `run_attempt` | integer | - |
| `run_started_at` | date-time | - |
| `conclusion` | string\|null | - |
| `status` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs

---

### get-workflow-run-usage - Get workflow run usage (timing)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/timing`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read DEPRECATED — doc states verbatim: 'This endpoint is in the process of closing down.' Endpoint still resolves today but should not be built on. Derive timing from run_started_at/updated_at and job timestamps instead, or use billing/usage endpoints for billable minutes.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. DEPRECATED — doc states verbatim: 'This endpoint is in the process of closing down.' Endpoint still resolves today but should not be built on. Derive timing from run_started_at/updated_at and job timestamps instead, or use billing/usage endpoints for billable minutes.

**Datapoints returned (2):**

- billable_ms_by_os - billable.UBUNTU/MACOS/WINDOWS total_ms — billable minutes per OS for a run.
- run_duration_ms - wall-clock run_duration_ms.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `billable.UBUNTU.total_ms` | integer | - |
| `billable.MACOS.total_ms` | integer | - |
| `billable.WINDOWS.total_ms` | integer | - |
| `run_duration_ms` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs

---

### get-workflow-usage - Get workflow usage (timing)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/timing`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read DEPRECATED — doc states 'This endpoint is in the process of closing down.' Returns aggregate billable_ms by OS for a single workflow. Researcher referenced this in prose but did not catalog it as an endpoint; added.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| workflow_id | path | yes | - | deploy.yml |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. DEPRECATED — doc states 'This endpoint is in the process of closing down.' Returns aggregate billable_ms by OS for a single workflow. Researcher referenced this in prose but did not catalog it as an endpoint; added.

**Datapoints returned (1):**

- workflow_billable_ms_by_os - billable.UBUNTU/MACOS/WINDOWS total_ms aggregated for one workflow — per-pipeline compute cost.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `billable.UBUNTU.total_ms` | integer | - |
| `billable.MACOS.total_ms` | integer | - |
| `billable.WINDOWS.total_ms` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflows

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflows

---

### list-workflow-runs-for-workflow - List workflow runs for a workflow

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read workflow_id accepts numeric id or filename (e.g. deploy.yml). Best for scoping deployment frequency to the specific deploy workflow.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| workflow_id | path | yes | - | deploy.yml |
| actor | query | no | - | - |
| branch | query | no | - | - |
| event | query | no | - | - |
| status | query | no | - | - |
| created | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. workflow_id accepts numeric id or filename (e.g. deploy.yml). Best for scoping deployment frequency to the specific deploy workflow.

**Datapoints returned (3):**

- deploy_workflow_frequency - Runs of the specific deploy workflow per window = deployment frequency without conflating other CI workflows.
- deploy_workflow_failure_rate - Ratio of conclusion=failure to total deploy-workflow runs = change-failure-rate proxy.
- deploy_workflow_lead_time - head_sha + run_started_at vs commit time = lead time for changes.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `workflow_runs[].conclusion` | string\|null | - |
| `workflow_runs[].run_started_at` | date-time | - |
| `workflow_runs[].head_sha` | string | - |
| `workflow_runs[].created_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs

---

### list-repo-workflows - List repository workflows

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/workflows`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Maps workflow names/files to ids; identify the deploy pipeline.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Maps workflow names/files to ids; identify the deploy pipeline.

**Datapoints returned (2):**

- workflow_inventory - Count and names of workflows — CI/CD adoption breadth.
- workflow_state - state field (active/disabled_manually/disabled_inactivity) — automation health.

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `workflows[].id` | integer | - |
| `workflows[].name` | string | - |
| `workflows[].path` | string | - |
| `workflows[].state` | string | - |
| `workflows[].created_at` | date-time | - |
| `workflows[].updated_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflows

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflows

---

### get-workflow - Get a workflow

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read workflow_id accepts numeric id or filename.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| workflow_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. workflow_id accepts numeric id or filename.

**Datapoints returned (1):**

- workflow_state_single - state (active/disabled) of a single workflow.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `id` | integer | - |
| `state` | string | - |
| `created_at` | date-time | - |
| `updated_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflows

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflows

---

### list-jobs-for-workflow-run - List jobs for a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read filter=latest (default) or all to include re-run attempts. Job-level started_at/completed_at give the most precise stage timings. Page only names classic repo scope in prose; fine-grained Actions:read by shared permission model.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| filter | query | no | latest (default) or all | all |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. filter=latest (default) or all to include re-run attempts. Job-level started_at/completed_at give the most precise stage timings. Page only names classic repo scope in prose; fine-grained Actions:read by shared permission model.

**Datapoints returned (5):**

- job_duration - started_at -> completed_at per job = precise build/deploy stage duration; feeds lead-time and pipeline efficiency.
- job_queue_time - created_at -> started_at = runner queue/wait time (bottleneck signal).
- job_conclusion - conclusion per job pinpoints which stage failed.
- step_timings - steps[].started_at/completed_at — per-step granularity.
- runner_attribution - runner_name/runner_group_name/labels — self-hosted vs GitHub-hosted runner usage.

**Report / response file fields (11):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `jobs[].status` | string | - |
| `jobs[].conclusion` | string\|null | - |
| `jobs[].created_at` | date-time | - |
| `jobs[].started_at` | date-time | - |
| `jobs[].completed_at` | date-time | - |
| `jobs[].run_attempt` | integer | - |
| `jobs[].steps[].started_at` | date-time | - |
| `jobs[].steps[].completed_at` | date-time | - |
| `jobs[].runner_name` | string | - |
| `jobs[].labels` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-jobs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-jobs

---

### list-jobs-for-run-attempt - List jobs for a workflow run attempt

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}/jobs`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Jobs scoped to a single attempt — separates retry timings from original run.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| attempt_number | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Jobs scoped to a single attempt — separates retry timings from original run.

**Datapoints returned (2):**

- attempt_job_duration - Per-attempt job started_at/completed_at — time-to-restore when a re-run fixes a broken deploy.
- attempt_job_conclusion - Which jobs failed in a given attempt — recovery analysis.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `jobs[].started_at` | date-time | - |
| `jobs[].completed_at` | date-time | - |
| `jobs[].conclusion` | string\|null | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-jobs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-jobs

---

### get-job - Get a job for a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Single job detail.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| job_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Single job detail.

**Datapoints returned (2):**

- job_duration_single - started_at -> completed_at for one job.
- step_breakdown - steps[] timings for fine-grained stage profiling.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `status` | string | - |
| `conclusion` | string\|null | - |
| `started_at` | date-time | - |
| `completed_at` | date-time | - |
| `steps` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-jobs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-jobs

---

### get-pending-deployments - Get pending deployments for a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/pending_deployments`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read MISSED by researcher. Anyone with read access can call it; repo scope for private. Surfaces the deployment-gate/approval state: which env is waiting, wait timer remaining, required reviewers. Public env protection rules on all plans; private/internal envs need Pro/Team/Enterprise.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED by researcher. Anyone with read access can call it; repo scope for private. Surfaces the deployment-gate/approval state: which env is waiting, wait timer remaining, required reviewers. Public env protection rules on all plans; private/internal envs need Pro/Team/Enterprise.

**Datapoints returned (3):**

- pending_gate_wait_timer - wait_timer + wait_timer_started_at — enforced wait/cool-down before a deploy proceeds (gate latency).
- pending_reviewers - reviewers[] (required approvers) and current_user_can_approve — manual-approval gate awaiting action; feeds deploy-approval lead time.
- pending_environment - environment object the run is blocked on — pipeline waiting state per environment.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `[].environment.name` | string | - |
| `[].wait_timer` | integer | - |
| `[].wait_timer_started_at` | date-time\|null | - |
| `[].current_user_can_approve` | boolean | - |
| `[].reviewers` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs

---

### get-workflow-run-approvals - Get the review history for a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/approvals`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read MISSED by researcher. Returns the environment-approval history (who approved/rejected a gated deployment, when, with comment). Anyone with read access can call it. Private/internal env protection requires Pro/Team/Enterprise.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED by researcher. Returns the environment-approval history (who approved/rejected a gated deployment, when, with comment). Anyone with read access can call it. Private/internal env protection requires Pro/Team/Enterprise.

**Datapoints returned (3):**

- deploy_approval_state - state (approved/rejected/pending) per environment — manual deployment-gate outcome.
- deploy_approval_actor - user.login who approved/rejected the deployment (PII) — governance attribution. (PII)
- deploy_approval_timing - comment + approval event timestamp; gap from pending to approval = approval lead time within delivery flow.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].state` | string | approved\|rejected\|pending |
| `[].user.login` | string | - |
| `[].comment` | string | - |
| `[].environments` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs

---

### list-repo-artifacts - List artifacts for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/artifacts`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Doc explicitly states fine-grained PAT needs 'Actions' read.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| name | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Doc explicitly states fine-grained PAT needs 'Actions' read.

**Datapoints returned (4):**

- artifact_storage_size - size_in_bytes per artifact — Actions storage consumption.
- artifact_count - Number of build artifacts produced — pipeline output/throughput.
- artifact_expiry - expired flag + expires_at — retention/cleanup affecting storage cost.
- artifact_to_run_linkage - workflow_run.head_sha/head_branch links artifact to producing run/commit.

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `artifacts[].size_in_bytes` | integer | - |
| `artifacts[].expired` | boolean | - |
| `artifacts[].created_at` | date-time | - |
| `artifacts[].expires_at` | date-time | - |
| `artifacts[].workflow_run.head_sha` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/artifacts

**Source URLs:**
- https://docs.github.com/en/rest/actions/artifacts

---

### get-repo-cache-usage - Get GitHub Actions cache usage for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/cache/usage`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read MISSED by researcher. Read access to repo; repo scope for private. Actions cache storage is a billable cost input.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED by researcher. Read access to repo; repo scope for private. Actions cache storage is a billable cost input.

**Datapoints returned (2):**

- repo_cache_size - active_caches_size_in_bytes — total Actions cache storage consumed by the repo (billable).
- repo_cache_count - active_caches_count — number of active caches.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `full_name` | string | - |
| `active_caches_size_in_bytes` | integer | - |
| `active_caches_count` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/cache

**Source URLs:**
- https://docs.github.com/en/rest/actions/cache

---

### list-repo-caches - List GitHub Actions caches for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/caches`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read MISSED by researcher. Per-cache size and last-access — cache efficiency + cost granularity.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| ref | query | no | - | - |
| key | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED by researcher. Per-cache size and last-access — cache efficiency + cost granularity.

**Datapoints returned (2):**

- cache_entry_size - actions_caches[].size_in_bytes per cache key — storage cost granularity.
- cache_freshness - actions_caches[].last_accessed_at / created_at — stale-cache detection and hit-recency signal for build reliability.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `actions_caches[].size_in_bytes` | integer | - |
| `actions_caches[].created_at` | date-time | - |
| `actions_caches[].last_accessed_at` | date-time | - |
| `actions_caches[].key` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/cache

**Source URLs:**
- https://docs.github.com/en/rest/actions/cache

---

### get-org-cache-usage - Get GitHub Actions cache usage for an organization

**Request:** `GET https://api.github.com/orgs/{org}/actions/cache/usage`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization administration: read MISSED by researcher. Org-aggregated cache storage cost.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED by researcher. Org-aggregated cache storage cost.

**Datapoints returned (2):**

- org_cache_size - total_active_caches_size_in_bytes — org-wide Actions cache storage (billable).
- org_cache_count - total_active_caches_count — org-wide active cache count.

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `total_active_caches_size_in_bytes` | integer | - |
| `total_active_caches_count` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/cache

**Source URLs:**
- https://docs.github.com/en/rest/actions/cache

---

### get-org-cache-usage-by-repo - List repositories with GitHub Actions cache usage for an organization

**Request:** `GET https://api.github.com/orgs/{org}/actions/cache/usage-by-repository`

**Auth:** bearer - Classic PAT (read:org) or fine-grained PAT

- Scopes: `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization administration: read MISSED by researcher. Per-repo cache breakdown for cost allocation across the org.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. MISSED by researcher. Per-repo cache breakdown for cost allocation across the org.

**Datapoints returned (1):**

- per_repo_cache_size - repository_cache_usages[].active_caches_size_in_bytes per repo — cost allocation.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `repository_cache_usages[].full_name` | string | - |
| `repository_cache_usages[].active_caches_size_in_bytes` | integer | - |
| `repository_cache_usages[].active_caches_count` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/cache

**Source URLs:**
- https://docs.github.com/en/rest/actions/cache

---

### get-org-billing-usage - Get billing usage report for an organization (enhanced billing)

**Request:** `GET https://api.github.com/organizations/{org}/settings/billing/usage`

**Auth:** bearer - Classic PAT (repo, admin:org) or fine-grained PAT

- Scopes: `repo`, `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: (org owner / billing manager role; docs do not name a fine-grained permission) MISSED by researcher (flagged as cross-domain but not cataloged). Authoritative source for Actions billable minutes/storage cost. Requires organization administrator and access to the enhanced billing platform (GHEC orgs migrated to enhanced billing). Filterable to product='Actions'. Replaces the legacy /orgs/{org}/settings/billing/actions minutes endpoint for enhanced-billing customers.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| hour | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans — enhanced billing usage is available on Free/Team/GHEC). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Authoritative source for Actions billable minutes/storage cost. Requires organization administrator and access to the enhanced billing platform (GHEC orgs migrated to enhanced billing). Filterable to product='Actions'. Replaces the legacy /orgs/{org}/settings/billing/actions minutes endpoint for enhanced-billing customers.

**Datapoints returned (3):**

- actions_net_cost - netAmount/grossAmount for product=Actions — actual delivery compute spend.
- actions_quantity - quantity + unitType (e.g. minutes) consumed — usage volume per SKU.
- per_repo_actions_cost - repositoryName breakdown — cost allocation of CI/CD compute by repo.

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].product` | string | - |
| `usageItems[].sku` | string | - |
| `usageItems[].quantity` | number | - |
| `usageItems[].unitType` | string | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].grossAmount` | number | - |
| `usageItems[].repositoryName` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/billing/usage?apiVersion=2026-03-10

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage?apiVersion=2026-03-10

---

### list-deployments - List deployments

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/deployments`

**Auth:** bearer - Classic PAT (repo_deployment, repo) or fine-grained PAT

- Scopes: `repo_deployment`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Deployments: read; Metadata: read repo_deployment is the narrower classic scope that grants deployment access without repo code. The GET page does not name the fine-grained permission in prose, but the fine-grained permissions reference maps these to 'Deployments' read — confidence medium on the exact wording.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| sha | query | no | - | - |
| ref | query | no | - | - |
| task | query | no | - | - |
| environment | query | no | - | production |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. repo_deployment is the narrower classic scope that grants deployment access without repo code. The GET page does not name the fine-grained permission in prose, but the fine-grained permissions reference maps these to 'Deployments' read — confidence medium on the exact wording.

**Datapoints returned (4):**

- deployment_frequency - Count of deployment objects per environment per window (filter environment=production) = most direct DORA deployment frequency source.
- deployment_lead_time_input - sha/ref + created_at vs commit authored time = lead time for changes.
- production_flag - production_environment / environment field isolates prod deploys.
- transient_flag - transient_environment marks ephemeral/preview deploys to exclude from DORA counts.

**Report / response file fields (8):**

| path | type | description |
| --- | --- | --- |
| `[].id` | integer | - |
| `[].sha` | string | - |
| `[].ref` | string | - |
| `[].environment` | string | - |
| `[].production_environment` | boolean | - |
| `[].transient_environment` | boolean | - |
| `[].created_at` | date-time | - |
| `[].updated_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/deployments/deployments

**Source URLs:**
- https://docs.github.com/en/rest/deployments/deployments

---

### get-deployment - Get a deployment

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/deployments/{deployment_id}`

**Auth:** bearer - Classic PAT (repo_deployment, repo) or fine-grained PAT

- Scopes: `repo_deployment`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Deployments: read; Metadata: read Fine-grained 'Deployments: read' per the permissions reference; GET page prose does not name it.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| deployment_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Fine-grained 'Deployments: read' per the permissions reference; GET page prose does not name it.

**Datapoints returned (1):**

- deployment_detail - Single deployment sha/ref/environment/created_at for joining to statuses and commits.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `id` | integer | - |
| `sha` | string | - |
| `environment` | string | - |
| `created_at` | date-time | - |
| `updated_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/deployments/deployments

**Source URLs:**
- https://docs.github.com/en/rest/deployments/deployments

---

### list-deployment-statuses - List deployment statuses

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/deployments/{deployment_id}/statuses`

**Auth:** bearer - Classic PAT (repo_deployment, repo) or fine-grained PAT

- Scopes: `repo_deployment`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Deployments: read; Metadata: read Users with pull (read) access can view. GET page prose only states 'pull access'; fine-grained 'Deployments: read' per permissions reference — confidence medium on wording.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| deployment_id | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Users with pull (read) access can view. GET page prose only states 'pull access'; fine-grained 'Deployments: read' per permissions reference — confidence medium on wording.

**Datapoints returned (4):**

- deploy_outcome_state - state (success/failure/error/inactive/in_progress/queued/pending) — success count = effective deployment frequency.
- change_failure_rate_numerator - Count of statuses with state=failure or error over total deploys = change-failure-rate.
- time_to_restore_input - created_at of a failure status -> created_at of next success on same environment = MTTR.
- deploy_status_creator - creator login who recorded the status (PII). (PII)

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `[].state` | string | error\|failure\|inactive\|pending\|success\|queued\|in_progress |
| `[].environment` | string | - |
| `[].created_at` | date-time | - |
| `[].updated_at` | date-time | - |
| `[].creator.login` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/deployments/statuses

**Source URLs:**
- https://docs.github.com/en/rest/deployments/statuses

---

### get-deployment-status - Get a deployment status

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/deployments/{deployment_id}/statuses/{status_id}`

**Auth:** bearer - Classic PAT (repo_deployment, repo) or fine-grained PAT

- Scopes: `repo_deployment`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Deployments: read; Metadata: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| deployment_id | path | yes | - | - |
| status_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- single_deploy_state - state + created_at for one status event.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `state` | string | - |
| `created_at` | date-time | - |
| `environment` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/deployments/statuses

**Source URLs:**
- https://docs.github.com/en/rest/deployments/statuses

---

### list-environments - List environments

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/environments`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read Anyone with repo read access can call it. Reading only needs Metadata:read / repo scope. MIN-LICENSE CORRECTED: environments are available in PUBLIC repos on ALL plans (incl. Free), but in PRIVATE/INTERNAL repos environments+protection rules require GitHub Pro, Team, or Enterprise — NOT Free. minLicense=team reflects the private-repo gate; on public repos treat as free.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Team or higher. Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Anyone with repo read access can call it. Reading only needs Metadata:read / repo scope. MIN-LICENSE CORRECTED: environments are available in PUBLIC repos on ALL plans (incl. Free), but in PRIVATE/INTERNAL repos environments+protection rules require GitHub Pro, Team, or Enterprise — NOT Free. minLicense=team reflects the private-repo gate; on public repos treat as free.

**Datapoints returned (2):**

- environment_inventory - total_count + names of deployment environments — deployment-target maturity/adoption.
- protection_rules_present - protection_rules (required reviewers, wait timers) + deployment_branch_policy — governance maturity of the pipeline.

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `environments[].id` | integer | - |
| `environments[].name` | string | - |
| `environments[].created_at` | date-time | - |
| `environments[].updated_at` | date-time | - |
| `environments[].protection_rules` | array | - |
| `environments[].deployment_branch_policy` | object\|null | - |

**Plans/tiers:** Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/deployments/environments

**Source URLs:**
- https://docs.github.com/en/rest/deployments/environments

---

### get-environment - Get an environment

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/environments/{environment_name}`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read environment_name must be URL-encoded. MIN-LICENSE CORRECTED: free on public repos; private/internal environments require GitHub Pro, Team, or Enterprise.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| environment_name | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Team or higher. Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. environment_name must be URL-encoded. MIN-LICENSE CORRECTED: free on public repos; private/internal environments require GitHub Pro, Team, or Enterprise.

**Datapoints returned (1):**

- environment_governance - protection_rules + deployment_branch_policy for one environment — gate configuration.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `name` | string | - |
| `protection_rules` | array | - |
| `deployment_branch_policy` | object\|null | - |
| `created_at` | date-time | - |
| `updated_at` | date-time | - |

**Plans/tiers:** Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/deployments/environments

**Source URLs:**
- https://docs.github.com/en/rest/deployments/environments

---

### list-releases - List releases

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/releases`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read; Metadata: read Published releases need Contents:read; listing drafts requires write/push (Contents:write). Public repos readable unauthenticated.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Published releases need Contents:read; listing drafts requires write/push (Contents:write). Public repos readable unauthenticated.

**Datapoints returned (4):**

- release_frequency - Count of releases by published_at per window — release cadence / deployment frequency proxy.
- release_lead_time_input - target_commitish/tag + published_at vs first-commit time = lead time for the release.
- prerelease_ratio - prerelease/draft flags — fraction of stable vs pre-release shipments.
- release_author - author.login who published the release (PII). (PII)

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `[].tag_name` | string | - |
| `[].draft` | boolean | - |
| `[].prerelease` | boolean | - |
| `[].created_at` | date-time | - |
| `[].published_at` | date-time | - |
| `[].target_commitish` | string | - |
| `[].author.login` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/releases/releases

**Source URLs:**
- https://docs.github.com/en/rest/releases/releases

---

### get-latest-release - Get the latest release

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/releases/latest`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read; Metadata: read Returns most recent non-draft, non-prerelease.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Returns most recent non-draft, non-prerelease.

**Datapoints returned (1):**

- current_release_marker - published_at/tag_name of latest stable release — recency of last ship.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `tag_name` | string | - |
| `published_at` | date-time | - |
| `target_commitish` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/releases/releases

**Source URLs:**
- https://docs.github.com/en/rest/releases/releases

---

### get-release-by-tag - Get a release by tag name

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read; Metadata: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| tag | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- release_by_tag - published_at/target_commitish for a specific version tag.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `tag_name` | string | - |
| `published_at` | date-time | - |
| `target_commitish` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/releases/releases

**Source URLs:**
- https://docs.github.com/en/rest/releases/releases

---

### get-release-by-id - Get a release

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/releases/{release_id}`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read; Metadata: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| release_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- release_detail - Full release record (tag, published_at, draft/prerelease) by id.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `tag_name` | string | - |
| `draft` | boolean | - |
| `prerelease` | boolean | - |
| `published_at` | date-time | - |
| `created_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/releases/releases

**Source URLs:**
- https://docs.github.com/en/rest/releases/releases

---

### get-check-run - Get a check run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/check-runs/{check_run_id}`

**Auth:** bearer - Classic PAT (repo (private repos only; public repos need no scope)) or fine-grained PAT

- Scopes: `repo (private repos only; public repos need no scope)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read (mandatory baseline) Docs confirm: 'OAuth app tokens and personal access tokens (classic) need the repo scope to use this endpoint on a private repository.' CORRECTION: 'Checks: read' fine-grained permission is NOT reliably selectable on fine-grained PATs (GitHub-App-only in practice per community discussions 129512/179545). Fine-grained PATs read check-run data via repo read access. GitHub Apps with Checks:read also work.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| check_run_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs confirm: 'OAuth app tokens and personal access tokens (classic) need the repo scope to use this endpoint on a private repository.' CORRECTION: 'Checks: read' fine-grained permission is NOT reliably selectable on fine-grained PATs (GitHub-App-only in practice per community discussions 129512/179545). Fine-grained PATs read check-run data via repo read access. GitHub Apps with Checks:read also work.

**Datapoints returned (4):**

- check_run_status - Lifecycle status: queued, in_progress, completed, waiting, requested, pending.
- check_run_conclusion - Final result for CI pass/fail: success, failure, neutral, cancelled, skipped, timed_out, action_required, stale.
- check_run_duration - started_at to completed_at = per-check execution time.
- check_run_annotations_count - output.annotations_count = number of code annotations emitted by the check.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `status` | string | queued\|in_progress\|completed\|waiting\|requested\|pending |
| `conclusion` | string\|null | success\|failure\|neutral\|cancelled\|skipped\|timed_out\|action_required\|stale |
| `started_at` | date-time\|null | - |
| `completed_at` | date-time\|null | - |
| `output.annotations_count` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

---

### list-check-runs-for-ref - List check runs for a Git reference

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits/{ref}/check-runs`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read Path/method confirmed on /rest/checks/runs. CORRECTION: 'Checks: read' FG permission removed (App-only/not exposed on FG PATs); FG PATs read via repo read access. Truncation: limited to check runs of the 1000 most recent check suites when >1000 suites exist on the ref.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| ref | path | yes | SHA, branch, or tag | main |
| check_name | query | no | - | - |
| status | query | no | queued\|in_progress\|completed | - |
| filter | query | no | latest (default) or all | - |
| app_id | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path/method confirmed on /rest/checks/runs. CORRECTION: 'Checks: read' FG permission removed (App-only/not exposed on FG PATs); FG PATs read via repo read access. Truncation: limited to check runs of the 1000 most recent check suites when >1000 suites exist on the ref.

**Datapoints returned (3):**

- checks_total_count - total_count of check runs on the ref - denominator for CI success rate.
- check_run_conclusion_per_ref - Per-check conclusion across the ref; aggregate success vs failure.
- check_name - Name of each check to break down failure rate by check.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `check_runs[].conclusion` | string\|null | - |
| `check_runs[].status` | string | - |
| `check_runs[].name` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

---

### list-check-runs-in-suite - List check runs in a check suite

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read Path/method confirmed. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| check_suite_id | path | yes | - | - |
| check_name | query | no | - | - |
| status | query | no | - | - |
| filter | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path/method confirmed. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access.

**Datapoints returned (2):**

- suite_checks_total_count - total_count of check runs in the suite.
- suite_member_conclusions - Conclusion of each check in the suite.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `check_runs[].conclusion` | string\|null | - |
| `check_runs[].status` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

---

### list-check-run-annotations - List check run annotations

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/check-runs/{check_run_id}/annotations`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read Path/method confirmed on /rest/checks/runs. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| check_run_id | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path/method confirmed on /rest/checks/runs. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access.

**Datapoints returned (2):**

- annotation_level - notice \| warning \| failure - severity of each annotation.
- annotation_location - path + start_line/end_line where the quality issue was flagged.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].annotation_level` | string\|null | notice\|warning\|failure |
| `[].path` | string | - |
| `[].start_line` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28

---

### get-check-suite - Get a check suite

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/check-suites/{check_suite_id}`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read On /rest/checks/suites. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access. GHES: same path under /api/v3.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| check_suite_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. On /rest/checks/suites. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access. GHES: same path under /api/v3.

**Datapoints returned (4):**

- check_suite_conclusion - Suite rollup conclusion: success, failure, neutral, cancelled, skipped, timed_out, action_required, startup_failure, stale.
- check_suite_status - Suite lifecycle status (queued/in_progress/completed).
- latest_check_runs_count - Number of latest check runs in the suite.
- head_sha - Commit SHA the suite ran against.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `status` | string | - |
| `conclusion` | string\|null | - |
| `head_sha` | string | - |
| `latest_check_runs_count` | integer | - |
| `check_runs_url` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/checks/suites?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/checks/suites?apiVersion=2022-11-28

---

### list-check-suites-for-ref - List check suites for a Git reference

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits/{ref}/check-suites`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Metadata: read On /rest/checks/suites. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| ref | path | yes | - | - |
| app_id | query | no | - | - |
| check_name | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. On /rest/checks/suites. CORRECTION: 'Checks: read' FG permission removed (App-only in practice); FG PATs read via repo read access.

**Datapoints returned (2):**

- suites_total_count - total_count of suites on the ref.
- suite_conclusion_per_ref - Per-suite conclusion to compute overall CI success rate at the ref.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `check_suites[].conclusion` | string\|null | - |
| `check_suites[].head_sha` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/checks/suites?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/checks/suites?apiVersion=2022-11-28

---

### get-combined-commit-status - Get the combined status for a specific reference

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits/{ref}/status`

**Auth:** bearer - Classic PAT (repo:status, repo) or fine-grained PAT

- Scopes: `repo:status`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Commit statuses: read; Metadata: read Path confirmed on /rest/commits/statuses ('Users with pull access can access a combined view'). 'Commit statuses: read' FG permission CONFIRMED on the fine-grained permissions reference page.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| ref | path | yes | SHA, branch, or tag | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/commits/statuses ('Users with pull access can access a combined view'). 'Commit statuses: read' FG permission CONFIRMED on the fine-grained permissions reference page.

**Datapoints returned (3):**

- combined_status_state - Overall state across contexts: failure \| pending \| success.
- status_total_count - total_count of individual statuses in the rollup.
- status_context - context per status (CI service/check name).

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `state` | string | failure\|pending\|success |
| `total_count` | integer | - |
| `sha` | string | - |
| `statuses[].state` | string | - |
| `statuses[].context` | string | - |
| `statuses[].target_url` | string\|null | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/statuses?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/commits/statuses?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens?apiVersion=2022-11-28

---

### list-commit-statuses - List commit statuses for a reference

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/commits/{ref}/statuses`

**Auth:** bearer - Classic PAT (repo:status, repo) or fine-grained PAT

- Scopes: `repo:status`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Commit statuses: read; Metadata: read Confirmed on /rest/commits/statuses. 'Commit statuses: read' FG permission CONFIRMED on permissions reference. Legacy route GET /repos/{owner}/{repo}/statuses/{ref} also documented (same data).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| ref | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Confirmed on /rest/commits/statuses. 'Commit statuses: read' FG permission CONFIRMED on permissions reference. Legacy route GET /repos/{owner}/{repo}/statuses/{ref} also documented (same data).

**Datapoints returned (3):**

- status_state_history - Each status state (error\|failure\|pending\|success) reverse-chron - CI signal timeline per context.
- status_creator - creator (Simple User) who/what posted the status; often a bot/App but can be a user login. (PII)
- status_timing - created_at/updated_at per status for CI latency.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].state` | string | error\|failure\|pending\|success |
| `[].context` | string | - |
| `[].creator` | object\|null | - |
| `[].created_at` | date-time | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/commits/statuses?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/commits/statuses?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens?apiVersion=2022-11-28

---

### list-workflow-runs-for-repo-quality - List workflow runs for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/workflow-runs. 'Actions: read' FG permission CONFIRMED on permissions reference. Truncation: at most 1,000 results when filtered by actor/branch/check_suite_id/created/event/head_sha/status. (CI-quality view of the same endpoint cataloged in delivery-actions-dora.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| actor | query | no | - | - |
| branch | query | no | - | - |
| event | query | no | - | - |
| status | query | no | - | - |
| created | query | no | - | - |
| head_sha | query | no | - | - |
| check_suite_id | query | no | - | - |
| exclude_pull_requests | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/workflow-runs. 'Actions: read' FG permission CONFIRMED on permissions reference. Truncation: at most 1,000 results when filtered by actor/branch/check_suite_id/created/event/head_sha/status. (CI-quality view of the same endpoint cataloged in delivery-actions-dora.)

**Datapoints returned (7):**

- workflow_run_conclusion - conclusion: success\|failure\|neutral\|cancelled\|skipped\|timed_out\|action_required\|stale.
- workflow_run_status - status lifecycle: queued\|in_progress\|completed\|waiting\|requested\|pending.
- workflow_run_attempt - run_attempt - number of re-runs; high attempts indicate flaky CI.
- workflow_run_duration - run_started_at to updated_at = CI duration.
- workflow_run_event - event trigger (push, pull_request, schedule).
- workflow_run_branch - head_branch the run executed against.
- workflow_run_actor - actor / triggering_actor login who triggered the run. (PII)

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `workflow_runs[].conclusion` | string\|null | - |
| `workflow_runs[].status` | string | - |
| `workflow_runs[].run_attempt` | integer | - |
| `workflow_runs[].run_started_at` | date-time | - |
| `workflow_runs[].head_branch` | string | - |
| `workflow_runs[].event` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens?apiVersion=2022-11-28

---

### get-workflow-run-quality - Get a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/workflow-runs. Same schema as list. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| exclude_pull_requests | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/workflow-runs. Same schema as list. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Datapoints returned (2):**

- single_run_conclusion - conclusion of one run (pass/fail).
- single_run_timing - run_started_at/created_at/updated_at for CI duration.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `conclusion` | string\|null | - |
| `status` | string | - |
| `run_attempt` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28

---

### list-workflow-runs-for-workflow-quality - List workflow runs for a workflow

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/workflow-runs. workflow_id accepts numeric id or filename. Same 1,000-result truncation when filtered. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| workflow_id | path | yes | numeric ID or filename | ci.yml |
| status | query | no | - | - |
| branch | query | no | - | - |
| event | query | no | - | - |
| created | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/workflow-runs. workflow_id accepts numeric id or filename. Same 1,000-result truncation when filtered. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Datapoints returned (2):**

- per_workflow_conclusion - conclusion per run within a specific workflow.
- per_workflow_attempt - run_attempt per run to detect flaky reruns in a specific workflow.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `workflow_runs[].conclusion` | string\|null | - |
| `workflow_runs[].run_attempt` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28

---

### get-workflow-run-attempt-quality - Get a workflow run attempt

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/workflow-runs. Per-attempt conclusion supports flaky-rerun analysis. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| attempt_number | path | yes | - | - |
| exclude_pull_requests | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/workflow-runs. Per-attempt conclusion supports flaky-rerun analysis. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Datapoints returned (1):**

- attempt_conclusion - Conclusion of a specific run attempt - distinguishes flaky reruns from genuine failures.

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `conclusion` | string\|null | - |
| `run_attempt` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28

---

### list-jobs-for-workflow-run-quality - List jobs for a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/workflow-jobs ('Anyone with read access...'). 'Actions: read' FG permission CONFIRMED on permissions reference. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| filter | query | no | latest (default) or all | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/workflow-jobs ('Anyone with read access...'). 'Actions: read' FG permission CONFIRMED on permissions reference. (CI-quality view; same endpoint cataloged in delivery-actions-dora.)

**Datapoints returned (4):**

- job_conclusion - Per-job conclusion - identifies which CI job failed.
- job_duration - started_at/completed_at per job for CI stage timing.
- step_conclusion - steps[].conclusion - finest-grained pass/fail per step.
- step_status - steps[].status lifecycle.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `jobs[].conclusion` | string\|null | - |
| `jobs[].status` | string | - |
| `jobs[].steps[].conclusion` | string\|null | - |
| `jobs[].steps[].status` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens?apiVersion=2022-11-28

---

### list-jobs-for-workflow-run-attempt - List jobs for a workflow run attempt

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}/jobs`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/workflow-jobs. Job conclusions per attempt - flaky job detection across reruns. (CI-quality view; jobs-for-attempt also cataloged in delivery-actions-dora as list-jobs-for-run-attempt.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| attempt_number | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/workflow-jobs. Job conclusions per attempt - flaky job detection across reruns. (CI-quality view; jobs-for-attempt also cataloged in delivery-actions-dora as list-jobs-for-run-attempt.)

**Datapoints returned (1):**

- attempt_job_conclusion - Per-job conclusion within a specific attempt; compare across attempts for flakiness.

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `jobs[].conclusion` | string\|null | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28

---

### get-job-for-workflow-run - Get a job for a workflow run

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/workflow-jobs ('Anyone with read access to the repository can use this endpoint'). (CI-quality view; same endpoint cataloged in delivery-actions-dora as get-job.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| job_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/workflow-jobs ('Anyone with read access to the repository can use this endpoint'). (CI-quality view; same endpoint cataloged in delivery-actions-dora as get-job.)

**Datapoints returned (1):**

- single_job_conclusion - Conclusion of one job plus per-step conclusions.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `conclusion` | string\|null | - |
| `status` | string | - |
| `steps[].conclusion` | string\|null | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28

---

### list-artifacts-for-repo - List artifacts for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/artifacts`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/artifacts. 'Actions: read' FG permission CONFIRMED. Metadata readable; content needs download redirect (~1 min expiry). (Test/coverage-artifact view; same endpoint cataloged in delivery-actions-dora as list-repo-artifacts.)

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| name | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/artifacts. 'Actions: read' FG permission CONFIRMED. Metadata readable; content needs download redirect (~1 min expiry). (Test/coverage-artifact view; same endpoint cataloged in delivery-actions-dora as list-repo-artifacts.)

**Datapoints returned (4):**

- artifacts_total_count - total_count of artifacts produced by CI.
- artifact_name - name to identify test/coverage artifacts.
- artifact_size_in_bytes - size_in_bytes - Actions storage billing input.
- artifact_expired - expired flag + expires_at - retention/availability of test evidence.

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `artifacts[].name` | string | - |
| `artifacts[].size_in_bytes` | integer | - |
| `artifacts[].expired` | boolean | - |
| `artifacts[].digest` | string\|null | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens?apiVersion=2022-11-28

---

### list-workflow-run-artifacts - List workflow run artifacts

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/artifacts. Artifacts scoped to one run.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| run_id | path | yes | - | - |
| name | query | no | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/artifacts. Artifacts scoped to one run.

**Datapoints returned (2):**

- run_artifacts_total_count - total_count of artifacts produced by a specific run.
- run_artifact_metadata - name/size/expired per artifact for that run.

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `artifacts[].name` | string | - |
| `artifacts[].size_in_bytes` | integer | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28

---

### get-artifact - Get an artifact

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/actions/artifacts/{artifact_id}`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Actions: read; Metadata: read Path confirmed on /rest/actions/artifacts. digest field confirmed present in response schema.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| artifact_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Path confirmed on /rest/actions/artifacts. digest field confirmed present in response schema.

**Datapoints returned (1):**

- single_artifact_metadata - name, size_in_bytes, expired, created_at, expires_at, digest of one artifact.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `name` | string | - |
| `size_in_bytes` | integer | - |
| `expired` | boolean | - |
| `digest` | string\|null | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28

**Source URLs:**
- https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28

---

### graphql-commit-status-check-rollup - Commit.statusCheckRollup (GraphQL)

**Purpose:** GraphQL query. Selection: repository.object(... on Commit).statusCheckRollup.state

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (repo (private repos only)) or fine-grained PAT

- Scopes: `repo (private repos only)`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Metadata: read; Commit statuses: read ADDED (researcher flagged as a gap but did not catalog). GraphQL Commit.statusCheckRollup merges BOTH legacy Status contexts AND Checks API runs into ONE rollup state, fetchable alongside PR/commit data in one query. REST cannot return the merged rollup in a single call. verified=false: exact GraphQL object/field schema NOT confirmed against /en/graphql/reference/objects this session - confirm Commit/StatusCheckRollup object pages before relying on it.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| query | body | yes | GraphQL query selecting repository.object(oid:).statusCheckRollup.state | - |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. ADDED (researcher flagged as a gap but did not catalog). GraphQL Commit.statusCheckRollup merges BOTH legacy Status contexts AND Checks API runs into ONE rollup state, fetchable alongside PR/commit data in one query. REST cannot return the merged rollup in a single call. verified=false: exact GraphQL object/field schema NOT confirmed against /en/graphql/reference/objects this session - confirm Commit/StatusCheckRollup object pages before relying on it.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (1):**

- status_check_rollup_state - Single combined CI pass/fail state per commit merging statuses + checks.

**Report / response file fields (1):**

| path | type | description |
| --- | --- | --- |
| `data.repository.object.statusCheckRollup.state` | enum | ERROR\|EXPECTED\|FAILURE\|PENDING\|SUCCESS (unconfirmed this session) |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/graphql/reference/objects

---

### list-code-scanning-alerts-repo - List code scanning alerts for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/alerts`

**Auth:** bearer - Classic PAT (security_events, repo, public_repo) or fine-grained PAT

- Scopes: `security_events`, `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read Docs verbatim: 'security_events or repos scope to use this endpoint with private or public repositories, or the public_repo scope to use this endpoint with only public repositories.' Repo doc page does not print a fine-grained permission table value; the catalog permission is code_scanning_alerts:read.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| tool_name | query | no | - | - |
| tool_guid | query | no | - | - |
| state | query | no | - | open |
| severity | query | no | - | high |
| ref | query | no | - | - |
| pr | query | no | - | - |
| sort | query | no | - | - |
| direction | query | no | - | - |
| per_page | query | no | - | - |
| before | query | no | - | - |
| after | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs verbatim: 'security_events or repos scope to use this endpoint with private or public repositories, or the public_repo scope to use this endpoint with only public repositories.' Repo doc page does not print a fine-grained permission table value; the catalog permission is code_scanning_alerts:read.

**Datapoints returned (4):**

- Open code scanning alerts - Count of open SAST/CodeQL alerts by severity and rule
- Code scanning alert MTTR - created_at vs fixed_at across alerts
- Dismissed alerts and reasons - false positive / won't fix / used in tests dismissals
- Alert dismisser identity - dismissed_by.login of who dismissed an alert (PII)

**Report / response file fields (10):**

| path | type | description |
| --- | --- | --- |
| `[].number` | integer | - |
| `[].state` | string | - |
| `[].rule.security_severity_level` | string | - |
| `[].rule.id` | string | - |
| `[].tool.name` | string | - |
| `[].fixed_at` | string | - |
| `[].dismissed_by.login` | string | PII |
| `[].dismissed_reason` | string | - |
| `[].most_recent_instance.location` | object | - |
| `[].created_at` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning
- https://docs.github.com/en/code-security/code-scanning/troubleshooting-code-scanning/advanced-security-must-be-enabled

---

### get-code-scanning-alert-repo - Get a code scanning alert

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}`

**Auth:** bearer - Classic PAT (security_events, repo, public_repo) or fine-grained PAT

- Scopes: `security_events`, `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| alert_number | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Single alert detail - Full detail of one code scanning alert

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `state` | string | - |
| `rule.security_severity_level` | string | - |
| `most_recent_instance.commit_sha` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### list-code-scanning-alert-instances - List instances of a code scanning alert

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}/instances`

**Auth:** bearer - Classic PAT (security_events, repo, public_repo) or fine-grained PAT

- Scopes: `security_events`, `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| alert_number | path | yes | - | - |
| ref | query | no | - | - |
| pr | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Alert instances per branch - Where (refs/locations) an alert recurs

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].ref` | string | - |
| `[].state` | string | - |
| `[].location.path` | string | - |
| `[].classifications` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### get-code-scanning-alert-autofix - Get the status of a code scanning autofix

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}/autofix`

**Auth:** bearer - Classic PAT (security_events, repo) or fine-grained PAT

- Scopes: `security_events`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: write Reading autofix status is documented on the code-scanning page; permission table not printed per-endpoint.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| alert_number | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Reading autofix status is documented on the code-scanning page; permission table not printed per-endpoint.

**Datapoints returned (1):**

- Autofix availability - Whether an AI-suggested fix exists for a code scanning alert (adoption/quality signal)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `status` | string | pending/success/error/outdated |
| `description` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### list-code-scanning-analyses - List code scanning analyses for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/analyses`

**Auth:** bearer - Classic PAT (security_events, repo, public_repo) or fine-grained PAT

- Scopes: `security_events`, `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| tool_name | query | no | - | - |
| ref | query | no | - | - |
| sarif_id | query | no | - | - |
| pr | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (3):**

- Scan frequency / cadence - How often code scanning runs (analysis timestamps per ref)
- Results count per analysis - results_count and rules_count trend
- Scan reliability - error field indicates failed/partial analyses

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `[].results_count` | integer | - |
| `[].rules_count` | integer | - |
| `[].created_at` | string | - |
| `[].tool.name` | string | - |
| `[].commit_sha` | string | - |
| `[].error` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### get-code-scanning-analysis - Get a code scanning analysis for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}`

**Auth:** bearer - Classic PAT (security_events, repo) or fine-grained PAT

- Scopes: `security_events`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| analysis_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Single analysis detail - Detail of one analysis run incl. results/rules count

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `results_count` | integer | - |
| `rules_count` | integer | - |
| `deletable` | boolean | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### get-code-scanning-default-setup - Get code scanning default setup configuration

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/default-setup`

**Auth:** bearer - Classic PAT (repo, security_events) or fine-grained PAT

- Scopes: `repo`, `security_events`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Code scanning enablement - Whether CodeQL default setup is configured and which languages

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `state` | string | configured / not-configured |
| `languages` | array | - |
| `query_suite` | string | - |
| `schedule` | string | - |
| `updated_at` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### list-codeql-databases - List CodeQL databases for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/codeql/databases`

**Auth:** bearer - Classic PAT (security_events, repo) or fine-grained PAT

- Scopes: `security_events`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- CodeQL language coverage - Which languages have an analyzable CodeQL database and when last built

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].language` | string | - |
| `[].created_at` | string | - |
| `[].commit_oid` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### get-code-scanning-sarif-status - Get information about a SARIF upload

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/code-scanning/sarifs/{sarif_id}`

**Auth:** bearer - Classic PAT (security_events, repo) or fine-grained PAT

- Scopes: `security_events`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| sarif_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- SARIF ingest reliability - Whether an uploaded SARIF was processed successfully

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `processing_status` | string | pending/complete/failed |
| `errors` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### list-code-scanning-alerts-org - List code scanning alerts for an organization

**Request:** `GET https://api.github.com/orgs/{org}/code-scanning/alerts`

**Auth:** bearer - Classic PAT (security_events, repo, public_repo) or fine-grained PAT

- Scopes: `security_events`, `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Code scanning alerts: read Docs verbatim scope wording matches repo endpoint (security_events or repo, or public_repo for public only). Must be org owner or security manager.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| tool_name | query | no | - | - |
| state | query | no | - | - |
| severity | query | no | - | - |
| sort | query | no | - | - |
| per_page | query | no | - | - |
| before | query | no | - | - |
| after | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs verbatim scope wording matches repo endpoint (security_events or repo, or public_repo for public only). Must be org owner or security manager.

**Datapoints returned (2):**

- Org-wide open code scanning alerts - Aggregate count/severity of SAST alerts across org repos (default branch)
- Per-repo alert distribution - Which repos carry the most/highest-severity alerts

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].repository.full_name` | string | - |
| `[].state` | string | - |
| `[].rule.security_severity_level` | string | - |
| `[].most_recent_instance.ref` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/rest/code-scanning/code-scanning

---

### list-code-scanning-alerts-enterprise - List code scanning alerts for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/code-scanning/alerts`

**Auth:** bearer - Classic PAT (security_events, repo)

- Scopes: `security_events`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Caller must be enterprise member. Doc page does not print a fine-grained permission for this endpoint; classic PAT in practice.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| tool_name | query | no | - | - |
| state | query | no | - | - |
| sort | query | no | - | - |
| direction | query | no | - | - |
| per_page | query | no | - | - |
| before | query | no | - | - |
| after | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Caller must be enterprise member. Doc page does not print a fine-grained permission for this endpoint; classic PAT in practice.

**Datapoints returned (1):**

- Enterprise-wide code scanning alerts - Cross-org SAST alert rollup

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].repository.full_name` | string | - |
| `[].state` | string | - |
| `[].rule.security_severity_level` | string | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/code-scanning/code-scanning

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/code-scanning/code-scanning

---

### list-secret-scanning-alerts-repo - List secret scanning alerts for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/secret-scanning/alerts`

**Auth:** bearer - Classic PAT (repo, security_events, public_repo) or fine-grained PAT

- Scopes: `repo`, `security_events`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Secret scanning alerts: read Docs: 'authenticated user must be an administrator for the repository or for the organization that owns the repository'.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| state | query | no | - | open |
| secret_type | query | no | - | - |
| resolution | query | no | - | - |
| validity | query | no | - | - |
| is_publicly_leaked | query | no | - | - |
| is_multi_repo | query | no | - | - |
| sort | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs: 'authenticated user must be an administrator for the repository or for the organization that owns the repository'.

**Datapoints returned (4):**

- Open secret scanning alerts - Leaked credentials by type and validity (active secrets highest risk)
- Push protection bypasses - Alerts where push protection was bypassed
- Bypass / resolution actor - Login of who bypassed or resolved (PII)
- Secret remediation time - created_at vs resolved_at

**Report / response file fields (9):**

| path | type | description |
| --- | --- | --- |
| `[].state` | string | - |
| `[].secret_type` | string | - |
| `[].validity` | string | - |
| `[].resolution` | string | - |
| `[].push_protection_bypassed` | boolean | - |
| `[].push_protection_bypassed_by.login` | string | PII |
| `[].resolved_by.login` | string | PII |
| `[].created_at` | string | - |
| `[].resolved_at` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/secret-scanning/secret-scanning

**Source URLs:**
- https://docs.github.com/en/rest/secret-scanning/secret-scanning

---

### get-secret-scanning-alert - Get a secret scanning alert

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}`

**Auth:** bearer - Classic PAT (repo, security_events, public_repo) or fine-grained PAT

- Scopes: `repo`, `security_events`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Secret scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| alert_number | path | yes | - | - |
| hide_secret | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Single secret alert detail - Full detail incl. validity and push-protection bypass

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `state` | string | - |
| `validity` | string | - |
| `push_protection_bypassed` | boolean | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/secret-scanning/secret-scanning

**Source URLs:**
- https://docs.github.com/en/rest/secret-scanning/secret-scanning

---

### list-secret-scanning-alert-locations - List locations for a secret scanning alert

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}/locations`

**Auth:** bearer - Classic PAT (repo, security_events, public_repo) or fine-grained PAT

- Scopes: `repo`, `security_events`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Secret scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| alert_number | path | yes | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Secret exposure locations - Where a leaked secret appears (commits, issues, PRs, discussions)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `[].type` | string | - |
| `[].details` | object | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/secret-scanning/secret-scanning

**Source URLs:**
- https://docs.github.com/en/rest/secret-scanning/secret-scanning

---

### get-secret-scanning-scan-history - Get secret scanning scan history for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/secret-scanning/scan-history`

**Auth:** bearer - Classic PAT (repo, security_events) or fine-grained PAT

- Scopes: `repo`, `security_events`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Secret scanning alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Advanced Security add-on (Code Security / Secret Protection) for private/internal repos. Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Secret scan coverage history - Whether/when incremental, backfill, pattern-update scans ran

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `incremental_scans` | array | - |
| `pattern_update_scans` | array | - |
| `backfill_scans` | array | - |

**Plans/tiers:** Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/secret-scanning/secret-scanning

**Source URLs:**
- https://docs.github.com/en/rest/secret-scanning/secret-scanning

---

### list-secret-scanning-alerts-org - List secret scanning alerts for an organization

**Request:** `GET https://api.github.com/orgs/{org}/secret-scanning/alerts`

**Auth:** bearer - Classic PAT (repo, security_events, public_repo) or fine-grained PAT

- Scopes: `repo`, `security_events`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Secret scanning alerts: read Docs: 'must be an administrator or security manager for the organization'.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| state | query | no | - | - |
| validity | query | no | - | - |
| is_publicly_leaked | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs: 'must be an administrator or security manager for the organization'.

**Datapoints returned (2):**

- Org-wide leaked secrets - Aggregate secret alerts by type/validity
- Org push protection bypass rate - Share of alerts where push protection bypassed

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `[].repository.full_name` | string | - |
| `[].secret_type` | string | - |
| `[].validity` | string | - |
| `[].push_protection_bypassed` | boolean | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/secret-scanning/secret-scanning

**Source URLs:**
- https://docs.github.com/en/rest/secret-scanning/secret-scanning

---

### list-secret-scanning-alerts-enterprise - List secret scanning alerts for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/secret-scanning/alerts`

**Auth:** bearer - Classic PAT (repo, security_events)

- Scopes: `repo`, `security_events`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enterprise member; doc page does not print a fine-grained permission for this endpoint.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| state | query | no | - | - |
| validity | query | no | - | - |
| per_page | query | no | - | - |
| before | query | no | - | - |
| after | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enterprise member; doc page does not print a fine-grained permission for this endpoint.

**Datapoints returned (1):**

- Enterprise-wide leaked secrets - Cross-org secret scanning rollup

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].repository.full_name` | string | - |
| `[].secret_type` | string | - |
| `[].validity` | string | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/secret-scanning/secret-scanning

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/secret-scanning/secret-scanning

---

### list-dependabot-alerts-repo - List Dependabot alerts for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/dependabot/alerts`

**Auth:** bearer - Classic PAT (security_events, public_repo) or fine-grained PAT

- Scopes: `security_events`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Dependabot alerts: read Docs: 'security_events scope (or public_repo for public repos only)'. Catalog fine-grained permission is dependabot_alerts:read; page does not print the slug.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| state | query | no | - | - |
| severity | query | no | - | - |
| ecosystem | query | no | - | - |
| package | query | no | - | - |
| manifest | query | no | - | - |
| scope | query | no | - | - |
| epss_percentage | query | no | - | - |
| sort | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs: 'security_events scope (or public_repo for public repos only)'. Catalog fine-grained permission is dependabot_alerts:read; page does not print the slug.

**Datapoints returned (4):**

- Open Dependabot vulnerability alerts - Vulnerable deps by severity, ecosystem, CVSS, EPSS
- Vulnerable dependency remediation time - created_at vs fixed_at
- Runtime vs dev vulnerability split - dependency.scope runtime vs dev
- Alert dismisser identity - dismissed_by.login (PII)

**Report / response file fields (10):**

| path | type | description |
| --- | --- | --- |
| `[].state` | string | - |
| `[].security_advisory.ghsa_id` | string | - |
| `[].security_advisory.cve_id` | string | - |
| `[].security_advisory.severity` | string | - |
| `[].security_advisory.cvss.score` | number | - |
| `[].security_vulnerability.package.name` | string | - |
| `[].dependency.scope` | string | - |
| `[].dismissed_by.login` | string | PII |
| `[].auto_dismissed_at` | string | - |
| `[].fixed_at` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/dependabot/alerts

**Source URLs:**
- https://docs.github.com/en/rest/dependabot/alerts

---

### get-dependabot-alert-repo - Get a Dependabot alert

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/dependabot/alerts/{alert_number}`

**Auth:** bearer - Classic PAT (security_events, public_repo) or fine-grained PAT

- Scopes: `security_events`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Dependabot alerts: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| alert_number | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Single Dependabot alert detail - Full advisory + patched version for one alert

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `security_advisory.ghsa_id` | string | - |
| `state` | string | - |
| `security_vulnerability.first_patched_version` | object | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/dependabot/alerts

**Source URLs:**
- https://docs.github.com/en/rest/dependabot/alerts

---

### list-dependabot-alerts-org - List Dependabot alerts for an organization

**Request:** `GET https://api.github.com/orgs/{org}/dependabot/alerts`

**Auth:** bearer - Classic PAT (security_events, public_repo) or fine-grained PAT

- Scopes: `security_events`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Dependabot alerts: read Docs: 'must be an owner or security manager for the organization'.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| state | query | no | - | - |
| severity | query | no | - | - |
| ecosystem | query | no | - | - |
| scope | query | no | - | - |
| runtime_risk | query | no | critical-resource, internet-exposed, sensitive-data, lateral-movement | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs: 'must be an owner or security manager for the organization'.

**Datapoints returned (2):**

- Org-wide vulnerable dependencies - Aggregate Dependabot alerts by severity/ecosystem
- Runtime risk classification - runtime_risk surfaces internet-exposed / sensitive-data risk

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].repository.full_name` | string | - |
| `[].security_advisory.severity` | string | - |
| `[].state` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/dependabot/alerts

**Source URLs:**
- https://docs.github.com/en/rest/dependabot/alerts

---

### list-dependabot-alerts-enterprise - List Dependabot alerts for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/dependabot/alerts`

**Auth:** bearer - Classic PAT (repo, security_events)

- Scopes: `repo`, `security_events`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Doc page does not print a fine-grained permission for this endpoint.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| state | query | no | - | - |
| severity | query | no | - | - |
| ecosystem | query | no | - | - |
| per_page | query | no | - | - |
| before | query | no | - | - |
| after | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Doc page does not print a fine-grained permission for this endpoint.

**Datapoints returned (1):**

- Enterprise-wide vulnerable dependencies - Cross-org Dependabot alert rollup

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].repository.full_name` | string | - |
| `[].security_advisory.severity` | string | - |
| `[].state` | string | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/dependabot/alerts

**Source URLs:**
- https://docs.github.com/en/rest/dependabot/alerts

---

### export-sbom - Export SBOM for a repository

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/dependency-graph/sbom`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read Scopes not printed on the SBOM doc page; recorded from access-requirement (read access to repo).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Scopes not printed on the SBOM doc page; recorded from access-requirement (read access to repo).

**Datapoints returned (2):**

- Dependency inventory (SBOM) - Full list of deps with versions and declared licenses
- License composition - Declared/concluded licenses across deps for compliance

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `sbom.packages` | array | - |
| `sbom.creationInfo.created` | string | - |
| `sbom.relationships` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/rest/dependency-graph/sboms

**Source URLs:**
- https://docs.github.com/en/rest/dependency-graph/sboms

---

### dependency-review-compare - Get dependency review (diff between two commits)

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/dependency-graph/compare/{basehead}`

**Auth:** bearer - Classic PAT (repo, public_repo) or fine-grained PAT

- Scopes: `repo`, `public_repo`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Contents: read Token scopes not enumerated on doc page; Contents:read for fine-grained PAT.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| basehead | path | yes | - | main...feature |
| name | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Token scopes not enumerated on doc page; Contents:read for fine-grained PAT.

**Datapoints returned (3):**

- Dependency changes introduced by a PR - Added/removed deps between base and head
- Vulnerabilities introduced in a diff - New vulnerable deps a change would add
- License changes in a diff - License of added/removed deps

**Report / response file fields (7):**

| path | type | description |
| --- | --- | --- |
| `[].change_type` | string | - |
| `[].ecosystem` | string | - |
| `[].name` | string | - |
| `[].version` | string | - |
| `[].license` | string | - |
| `[].scope` | string | - |
| `[].vulnerabilities` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server, Advanced Security

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/dependency-graph/dependency-review

**Source URLs:**
- https://docs.github.com/en/rest/dependency-graph/dependency-review

---

### list-repo-security-advisories - List repository security advisories

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/security-advisories`

**Auth:** bearer - Classic PAT (repo, repository_advisories:read) or fine-grained PAT

- Scopes: `repo`, `repository_advisories:read`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Repository security advisories: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | path | yes | - | - |
| repo | path | yes | - | - |
| state | query | no | - | - |
| sort | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (2):**

- Repository security advisories - Self-published advisories with severity, CVSS, CWE
- Advisory disclosure flow - state tracks remediation lifecycle

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `[].ghsa_id` | string | - |
| `[].cve_id` | string | - |
| `[].severity` | string | - |
| `[].state` | string | - |
| `[].cvss_severities` | object | - |
| `[].cwes` | array | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/security-advisories/repository-advisories

**Source URLs:**
- https://docs.github.com/en/rest/security-advisories/repository-advisories

---

### get-repo-security-advisory - Get a repository security advisory

**Request:** `GET https://api.github.com/repos/{owner}/{repo}/security-advisories/{ghsa_id}`

**Auth:** bearer - Classic PAT (repo, repository_advisories:read) or fine-grained PAT

- Scopes: `repo`, `repository_advisories:read`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Repository security advisories: read

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| ghsa_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits.

**Datapoints returned (1):**

- Single repo advisory detail - Full advisory incl. credits, CVSS, CWE

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `ghsa_id` | string | - |
| `severity` | string | - |
| `cvss_severities` | object | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/security-advisories/repository-advisories

**Source URLs:**
- https://docs.github.com/en/rest/security-advisories/repository-advisories

---

### list-org-security-advisories - List organization repository security advisories

**Request:** `GET https://api.github.com/orgs/{org}/security-advisories`

**Auth:** bearer - Classic PAT (repo, repository_advisories:read) or fine-grained PAT

- Scopes: `repo`, `repository_advisories:read`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Repository security advisories: read Caller must be org owner or security manager.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| state | query | no | - | - |
| sort | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Caller must be org owner or security manager.

**Datapoints returned (1):**

- Org-wide self-published advisories - Advisory count/severity/state across org repos

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `[].ghsa_id` | string | - |
| `[].severity` | string | - |
| `[].state` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/security-advisories/repository-advisories

**Source URLs:**
- https://docs.github.com/en/rest/security-advisories/repository-advisories

---

### list-global-advisories - List global security advisories (GitHub Advisory Database)

**Request:** `GET https://api.github.com/advisories`

**Auth:** bearer - PAT / token
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: No auth required; authenticating raises rate limits.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| type | query | no | - | - |
| ecosystem | query | no | - | - |
| severity | query | no | - | - |
| cwes | query | no | - | - |
| cve_id | query | no | - | - |
| affects | query | no | - | - |
| epss_percentage | query | no | - | - |
| published | query | no | - | - |
| sort | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: global. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. No auth required; authenticating raises rate limits.

**Datapoints returned (1):**

- Global advisory lookup - Query the advisory DB to enrich alerts (CVSS, EPSS, CWE)

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `[].ghsa_id` | string | - |
| `[].cve_id` | string | - |
| `[].severity` | string | - |
| `[].epss.percentage` | number | - |
| `[].cvss_severities` | object | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/security-advisories/global-advisories

**Source URLs:**
- https://docs.github.com/en/rest/security-advisories/global-advisories

---

### get-global-advisory - Get a global security advisory

**Request:** `GET https://api.github.com/advisories/{ghsa_id}`

**Auth:** bearer - PAT / token
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: No auth required.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| ghsa_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: global. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. No auth required.

**Datapoints returned (1):**

- Single global advisory detail - Authoritative advisory record incl. EPSS, CVSS, patched versions

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `ghsa_id` | string | - |
| `epss.percentile` | number | - |
| `cvss_severities` | object | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/security-advisories/global-advisories

**Source URLs:**
- https://docs.github.com/en/rest/security-advisories/global-advisories

---

### get-org-audit-log - Get the audit log for an organization

**Request:** `GET https://api.github.com/orgs/{org}/audit-log`

**Auth:** bearer - Classic PAT (read:audit_log, admin:org) or fine-grained PAT

- Scopes: `read:audit_log`, `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Organization administration: read CORRECTED: docs confirm this endpoint DOES work with GitHub App user tokens, GitHub App installation tokens, and fine-grained PATs; fine-grained PAT needs 'Administration' organization permissions (read). Classic PAT needs read:audit_log. Researcher wrongly claimed fine-grained PAT unsupported.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| phrase | query | no | - | - |
| include | query | no | web, git, or all (default web) | all |
| order | query | no | - | - |
| before | query | no | - | - |
| after | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. CORRECTED: docs confirm this endpoint DOES work with GitHub App user tokens, GitHub App installation tokens, and fine-grained PATs; fine-grained PAT needs 'Administration' organization permissions (read). Classic PAT needs read:audit_log. Researcher wrongly claimed fine-grained PAT unsupported.

**Datapoints returned (3):**

- Org security/governance events - Audit trail of config changes, access grants, repo create/delete
- Actor activity - Who performed which action and when (PII)
- Git access events - clone/fetch/push events when include=git/all (PII)

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `[].action` | string | - |
| `[].actor` | string | PII |
| `[].@timestamp` | integer | - |
| `[].org` | string | - |
| `[].repo` | string | - |
| `[].actor_location` | object | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/orgs/orgs

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/orgs/orgs
- https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/using-the-audit-log-api-for-your-enterprise

---

### get-enterprise-audit-log - Get the audit log for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/audit-log`

**Auth:** bearer - Classic PAT (read:audit_log on GHEC; admin:enterprise on GHES)

- Scopes: `read:audit_log`, `admin:enterprise`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: GHEC: classic PAT with read:audit_log (fine-grained PATs/GitHub Apps not supported for the enterprise endpoint, unlike the org endpoint). GitHub Enterprise Server (3.8-3.20) also serves this endpoint at the same /enterprises/{enterprise}/audit-log path from base https://HOST/api/v3 using the admin:enterprise scope.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| phrase | query | no | - | - |
| include | query | no | - | all |
| order | query | no | - | - |
| before | query | no | - | - |
| after | query | no | - | - |
| per_page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud, or GitHub Enterprise Server (documented 3.8-3.20) — not on Free/Team. Scope level: enterprise. GHEC uses base https://api.github.com with classic PAT scope read:audit_log; GHES serves the same /enterprises/{enterprise}/audit-log path from base https://HOST/api/v3 with the admin:enterprise scope. GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. On GHEC, fine-grained PATs/GitHub Apps are not supported for the enterprise endpoint (unlike the org endpoint).

**Datapoints returned (3):**

- Enterprise audit events - Enterprise-wide governance/security audit trail
- Enterprise actor activity - Who did what across the enterprise (PII)
- Enterprise git events - git clone/push/fetch events when include=git/all (PII)

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `[].action` | string | - |
| `[].actor` | string | PII |
| `[].@timestamp` | integer | - |
| `[].org` | string | - |
| `[].repo` | string | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-server@3.20/rest/enterprise-admin/audit-log

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/audit-log
- https://docs.github.com/en/enterprise-server@3.20/rest/enterprise-admin/audit-log

---

### org-billing-usage-report - Get billing usage report for an organization (enhanced billing platform)

**Request:** `GET https://api.github.com/organizations/{org}/settings/billing/usage`

**Auth:** bearer - Classic PAT (repo (classic PAT). Tutorial states the billing usage endpoints do NOT support fine-grained PATs; use a classic PAT.) or fine-grained PAT

- Scopes: `repo (classic PAT). Tutorial states the billing usage endpoints do NOT support fine-grained PATs; use a classic PAT.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Note: the fine-grained permissions reference page maps this endpoint to org Administration:read via X-Accepted-GitHub-Permissions, but the official automate-usage-reporting tutorial explicitly says fine-grained PATs are NOT supported and to use a classic PAT. Treat classic PAT as the supported path. Caller must be an organization owner. Enhanced billing platform only. Last 24 months of data.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | Organization login/name | - |
| year | query | no | - | 2026 |
| month | query | no | - | 5 |
| day | query | no | - | 15 |
| hour | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Caller must be an organization owner. Enhanced billing platform only. Last 24 months of data.

**Datapoints returned (6):**

- metered net spend by product/SKU - Per-line-item billed amount: product (actions, packages, storage, copilot, codespaces, etc.), SKU, quantity, unitType, pricePerUnit, grossAmount, discountAmount, netAmount
- Actions minutes spend - usageItems rows where product=actions give minutes quantity and netAmount per runner SKU/OS
- Packages GB spend - usageItems rows where product=packages (data transfer GB)
- Shared storage GB-day spend - usageItems rows where product=storage (GB-days)
- Codespaces spend - usageItems rows where product=codespaces
- spend attributed to repository - repositoryName on each usage item enables per-repo cost allocation

**Report / response file fields (11):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].date` | string | - |
| `usageItems[].product` | string | - |
| `usageItems[].sku` | string | - |
| `usageItems[].quantity` | number | - |
| `usageItems[].unitType` | string | - |
| `usageItems[].pricePerUnit` | number | - |
| `usageItems[].grossAmount` | number | - |
| `usageItems[].discountAmount` | number | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].organizationName` | string | - |
| `usageItems[].repositoryName` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage
- https://docs.github.com/en/billing/tutorials/automate-usage-reporting

---

### org-billing-usage-summary - Get billing usage summary for an organization (public preview)

**Request:** `GET https://api.github.com/organizations/{org}/settings/billing/usage/summary`

**Auth:** bearer - Classic PAT (repo (classic PAT). Billing usage endpoints do not support fine-grained PATs per the tutorial.)

- Scopes: `repo (classic PAT). Billing usage endpoints do not support fine-grained PATs per the tutorial.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Org owner. Public preview, subject to change. Enhanced billing platform only. Last 24 months.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| repository | query | no | - | - |
| product | query | no | - | - |
| sku | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Org owner. Public preview, subject to change. Enhanced billing platform only. Last 24 months.

**Datapoints returned (1):**

- aggregated net spend (gross/discount/net) - Pre-aggregated usage with grossQuantity, grossAmount, discountQuantity, discountAmount, netQuantity, netAmount per product/SKU

**Report / response file fields (9):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].product` | string | - |
| `usageItems[].sku` | string | - |
| `usageItems[].unitType` | string | - |
| `usageItems[].grossQuantity` | number | - |
| `usageItems[].grossAmount` | number | - |
| `usageItems[].discountQuantity` | number | - |
| `usageItems[].discountAmount` | number | - |
| `usageItems[].netQuantity` | number | - |
| `usageItems[].netAmount` | number | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage

---

### org-ai-credit-usage - Get billing AI credit usage report for an organization

**Request:** `GET https://api.github.com/organizations/{org}/settings/billing/ai_credit/usage`

**Auth:** bearer - Classic PAT (repo (classic PAT). Fine-grained PATs not supported for billing usage endpoints.)

- Scopes: `repo (classic PAT). Fine-grained PATs not supported for billing usage endpoints.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Org administrator. Last 24 months only. Metered AI credit (GitHub Models / Copilot credit) spend.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| user | query | no | - | - |
| model | query | no | - | - |
| product | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Org administrator. Last 24 months only. Metered AI credit (GitHub Models / Copilot credit) spend.

**Datapoints returned (1):**

- AI credit spend by model - Metered AI credit consumption (netAmount) by model/product; cost line item, not a Copilot adoption metric (PII)

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].model` | string | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].netQuantity` | number | - |
| `user` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage

---

### org-premium-request-usage - Get billing premium request usage report for an organization

**Request:** `GET https://api.github.com/organizations/{org}/settings/billing/premium_request/usage`

**Auth:** bearer - Classic PAT (repo (classic PAT). Fine-grained PATs not supported for billing usage endpoints.)

- Scopes: `repo (classic PAT). Fine-grained PATs not supported for billing usage endpoints.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Org administrator. Last 24 months. Copilot premium-request overage spend line.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| user | query | no | - | - |
| model | query | no | - | - |
| product | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Org administrator. Last 24 months. Copilot premium-request overage spend line.

**Datapoints returned (1):**

- premium request overage spend - Metered premium-request netAmount per model (PII)

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].model` | string | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].netQuantity` | number | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage

---

### user-billing-usage-report - Get billing usage report for a user (enhanced billing platform)

**Request:** `GET https://api.github.com/users/{username}/settings/billing/usage`

**Auth:** bearer - Classic PAT (classic PAT for own account. Fine-grained PATs not supported for billing usage.)

- Scopes: `classic PAT for own account. Fine-grained PATs not supported for billing usage.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Personal account on enhanced billing platform; read only your own usage. Last 24 months.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| username | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Personal account on enhanced billing platform; read only your own usage. Last 24 months.

**Datapoints returned (1):**

- personal account metered spend - Per-line-item net spend for a personal account (Actions/Packages/Storage/Codespaces/Copilot) (PII)

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].product` | string | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].quantity` | number | - |
| `usageItems[].repositoryName` | string | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage

---

### user-billing-usage-summary - Get billing usage summary for a user (public preview)

**Request:** `GET https://api.github.com/users/{username}/settings/billing/usage/summary`

**Auth:** bearer - Classic PAT (classic PAT for own account. Fine-grained PATs not supported for billing usage.)

- Scopes: `classic PAT for own account. Fine-grained PATs not supported for billing usage.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Personal account, enhanced platform, public preview. Own usage only.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| username | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| repository | query | no | - | - |
| product | query | no | - | - |
| sku | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Personal account, enhanced platform, public preview. Own usage only.

**Datapoints returned (1):**

- aggregated personal net spend - Pre-aggregated gross/discount/net per product/SKU for a personal account (PII)

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].product` | string | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].netQuantity` | number | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage

---

### user-ai-credit-usage - Get billing AI credit usage report for a user

**Request:** `GET https://api.github.com/users/{username}/settings/billing/ai_credit/usage`

**Auth:** bearer - Classic PAT (classic PAT for own account. Fine-grained PATs not supported for billing usage.)

- Scopes: `classic PAT for own account. Fine-grained PATs not supported for billing usage.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Personal account, enhanced platform. Own usage only. Last 24 months.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| username | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| model | query | no | - | - |
| product | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Personal account, enhanced platform. Own usage only. Last 24 months.

**Datapoints returned (1):**

- personal AI credit spend - Metered AI credit netAmount by model for a personal account (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].model` | string | - |
| `usageItems[].netAmount` | number | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage

---

### user-premium-request-usage - Get billing premium request usage report for a user

**Request:** `GET https://api.github.com/users/{username}/settings/billing/premium_request/usage`

**Auth:** bearer - Classic PAT (classic PAT for own account. Fine-grained PATs not supported for billing usage.)

- Scopes: `classic PAT for own account. Fine-grained PATs not supported for billing usage.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Personal account, enhanced platform. Own usage only. Last 24 months.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| username | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| model | query | no | - | - |
| product | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Personal account, enhanced platform. Own usage only. Last 24 months.

**Datapoints returned (1):**

- personal premium request spend - Metered premium-request netAmount by model for a personal account (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].model` | string | - |
| `usageItems[].netAmount` | number | - |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/rest/billing/usage

---

### enterprise-billing-usage-report - Get billing usage report for an enterprise (usage by cost center)

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/usage`

**Auth:** bearer - Classic PAT (read:enterprise (classic PAT). Fine-grained PATs not supported for billing usage endpoints.)

- Scopes: `read:enterprise (classic PAT). Fine-grained PATs not supported for billing usage endpoints.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enterprise administrator or billing manager. Enhanced billing platform only. By default returns usage NOT assigned to a cost center; filter via cost_center_id ('none' targets unassociated usage).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| hour | query | no | - | - |
| cost_center_id | query | no | - | - |
| organization | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enterprise administrator or billing manager. Enhanced billing platform only. By default returns usage NOT assigned to a cost center; filter via cost_center_id ('none' targets unassociated usage).

**Datapoints returned (3):**

- enterprise-wide net spend by product/SKU - Same usageItems shape as org report, aggregated across member orgs
- spend by cost center / business unit - FinOps showback/chargeback via cost_center_id
- spend by member organization - organizationName on each item allocates spend across orgs

**Report / response file fields (11):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].date` | string | - |
| `usageItems[].product` | string | - |
| `usageItems[].sku` | string | - |
| `usageItems[].quantity` | number | - |
| `usageItems[].unitType` | string | - |
| `usageItems[].pricePerUnit` | number | - |
| `usageItems[].grossAmount` | number | - |
| `usageItems[].discountAmount` | number | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].organizationName` | string | - |
| `usageItems[].repositoryName` | string | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage
- https://docs.github.com/en/billing/tutorials/automate-usage-reporting

---

### enterprise-billing-usage-summary - Get billing usage summary for an enterprise (public preview)

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/usage/summary`

**Auth:** bearer - Classic PAT (read:enterprise (classic PAT). Fine-grained PATs not supported.)

- Scopes: `read:enterprise (classic PAT). Fine-grained PATs not supported.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enterprise admin or billing manager. Public preview. This is the endpoint the official automate-usage-reporting tutorial demonstrates.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| cost_center_id | query | no | - | - |
| organization | query | no | - | - |
| product | query | no | - | - |
| sku | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enterprise admin or billing manager. Public preview. This is the endpoint the official automate-usage-reporting tutorial demonstrates.

**Datapoints returned (1):**

- aggregated enterprise net spend - Pre-aggregated gross/discount/net amounts per product/SKU across the enterprise

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].product` | string | - |
| `usageItems[].sku` | string | - |
| `usageItems[].netAmount` | number | - |
| `usageItems[].grossAmount` | number | - |
| `usageItems[].netQuantity` | number | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage
- https://docs.github.com/en/billing/tutorials/automate-usage-reporting

---

### enterprise-ai-credit-usage - Get billing AI credit usage report for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/ai_credit/usage`

**Auth:** bearer - Classic PAT (read:enterprise (classic PAT). Fine-grained PATs not supported.)

- Scopes: `read:enterprise (classic PAT). Fine-grained PATs not supported.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enterprise admin or billing manager. Last 24 months. Metered AI credit spend across the enterprise.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| cost_center_id | query | no | - | - |
| organization | query | no | - | - |
| user | query | no | - | - |
| model | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enterprise admin or billing manager. Last 24 months. Metered AI credit spend across the enterprise.

**Datapoints returned (1):**

- enterprise AI credit spend by model/org - Metered AI credit netAmount across the enterprise, breakable by org/user/model (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].model` | string | - |
| `usageItems[].netAmount` | number | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage

---

### enterprise-premium-request-usage - Get billing premium request usage report for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/premium_request/usage`

**Auth:** bearer - Classic PAT (read:enterprise (classic PAT). Fine-grained PATs not supported.)

- Scopes: `read:enterprise (classic PAT). Fine-grained PATs not supported.`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enterprise admin or billing manager. Last 24 months. Copilot premium-request overage spend across the enterprise.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| year | query | no | - | - |
| month | query | no | - | - |
| day | query | no | - | - |
| cost_center_id | query | no | - | - |
| organization | query | no | - | - |
| user | query | no | - | - |
| model | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enterprise admin or billing manager. Last 24 months. Copilot premium-request overage spend across the enterprise.

**Datapoints returned (1):**

- enterprise premium request overage spend - Metered premium-request netAmount per model across the enterprise (PII)

**Report / response file fields (2):**

| path | type | description |
| --- | --- | --- |
| `usageItems[].model` | string | - |
| `usageItems[].netAmount` | number | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/billing/usage

---

### ghas-active-committers-org - Get GitHub Advanced Security active committers for an organization

**Request:** `GET https://api.github.com/orgs/{org}/settings/billing/advanced-security`

**Auth:** bearer - Classic PAT (repo (classic PAT); caller must be an org owner) or fine-grained PAT

- Scopes: `repo (classic PAT); caller must be an org owner`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Administration: read (organization permissions) Confirmed on current GHEC billing reference and GHES 3.14: fine-grained 'Administration' org permission at read level. Counts each committer login once across repos. advanced_security_product can scope to code_security or secret_protection.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| advanced_security_product | query | no | code_security \| secret_protection | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Advanced Security add-on (Code Security / Secret Protection) for private/internal repos. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Confirmed on current GHEC billing reference and GHES 3.14: fine-grained 'Administration' org permission at read level. Counts each committer login once across repos. advanced_security_product can scope to code_security or secret_protection.

**Datapoints returned (3):**

- GHAS active committers (billable seats) - total_advanced_security_committers = distinct billable committer seats; maximum_/purchased_ give entitlement
- GHAS committer breakdown per repo - repositories[].advanced_security_committers and per-user breakdown (login, last pushed date/email) (PII)
- GHAS seat utilization - purchased vs total committers indicates over/under provisioning

**Report / response file fields (9):**

| path | type | description |
| --- | --- | --- |
| `total_advanced_security_committers` | integer | - |
| `total_count` | integer | - |
| `maximum_advanced_security_committers` | integer | - |
| `purchased_advanced_security_committers` | integer | - |
| `repositories[].name` | string | - |
| `repositories[].advanced_security_committers` | integer | - |
| `repositories[].advanced_security_committers_breakdown[].user_login` | string | - |
| `repositories[].advanced_security_committers_breakdown[].last_pushed_date` | string | - |
| `repositories[].advanced_security_committers_breakdown[].last_pushed_email` | string | - |

**Plans/tiers:** Advanced Security

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/billing/billing

**Source URLs:**
- https://docs.github.com/en/rest/billing/billing
- https://docs.github.com/en/enterprise-server@3.14/rest/billing/billing

---

### ghas-active-committers-enterprise - Get GitHub Advanced Security active committers for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/advanced-security`

**Auth:** bearer - Classic PAT (read:enterprise)

- Scopes: `read:enterprise`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enterprise admin. Listed on the enterprise-admin/license reference page alongside consumed-licenses. Aggregates GHAS committers across member orgs.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| advanced_security_product | query | no | code_security \| secret_protection | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Advanced Security add-on (Code Security / Secret Protection) for private/internal repos. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enterprise admin. Listed on the enterprise-admin/license reference page alongside consumed-licenses. Aggregates GHAS committers across member orgs.

**Datapoints returned (2):**

- enterprise GHAS active committers - total_advanced_security_committers across the enterprise; headline GHAS billing number
- per-repo GHAS committers across orgs - repositories[] breakdown rolled up enterprise-wide (PII)

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `total_advanced_security_committers` | integer | - |
| `total_count` | integer | - |
| `repositories[].name` | string | - |
| `repositories[].advanced_security_committers` | integer | - |

**Plans/tiers:** Advanced Security

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/license

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/license

---

### enterprise-consumed-licenses - List enterprise consumed licenses (seats)

**Request:** `GET https://api.github.com/enterprises/{enterprise}/consumed-licenses`

**Auth:** bearer - Classic PAT (read:enterprise)

- Scopes: `read:enterprise`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Docs: OAuth app tokens and classic PATs need the read:enterprise scope. Enterprise admin.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Docs: OAuth app tokens and classic PATs need the read:enterprise scope. Enterprise admin.

**Datapoints returned (2):**

- seats consumed vs purchased - total_seats_consumed vs total_seats_purchased = license utilization / over-provisioning signal
- per-user license assignment - users[] with github_com_login, enterprise roles, license consumption flags (PII)

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `total_seats_consumed` | integer | - |
| `total_seats_purchased` | integer | - |
| `users[].github_com_login` | string | - |
| `users[].github_com_enterprise_roles` | array | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/license

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/license

---

### enterprise-license-sync-status - Get a license sync status (GHES connected to GHEC)

**Request:** `GET https://api.github.com/enterprises/{enterprise}/license-sync-status`

**Auth:** bearer - Classic PAT (read:enterprise)

- Scopes: `read:enterprise`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enterprise admin. Reports sync status of GHES server instances reporting license usage to GHEC.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enterprise admin. Reports sync status of GHES server instances reporting license usage to GHEC.

**Datapoints returned (1):**

- license sync freshness - server_instances[].last_sync indicates whether seat/usage data feeding billing is current

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `server_instances[].server_id` | string | - |
| `server_instances[].hostname` | string | - |
| `server_instances[].last_sync` | string | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/license

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/license

---

### enterprise-cost-centers-list - List cost centers for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/cost-centers`

**Auth:** bearer - Classic PAT (read:enterprise (enterprise owner / billing manager / org owner))

- Scopes: `read:enterprise (enterprise owner / billing manager / org owner)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Cost centers map resources (orgs/repos/users) to business units for chargeback; enhanced billing platform feature.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Cost centers map resources (orgs/repos/users) to business units for chargeback; enhanced billing platform feature.

**Datapoints returned (1):**

- cost center inventory - id, name, state (active/deleted), azure_subscription, resources[] (type + name) — the dimensions for FinOps chargeback

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `costCenters[].id` | string | - |
| `costCenters[].name` | string | - |
| `costCenters[].state` | string | - |
| `costCenters[].azure_subscription` | string\|null | - |
| `costCenters[].resources[].type` | string | - |
| `costCenters[].resources[].name` | string | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/cost-centers

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/billing/cost-centers

---

### enterprise-cost-center-get - Get a cost center by ID for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/cost-centers/{cost_center_id}`

**Auth:** bearer - Classic PAT (read:enterprise (enterprise owner / billing manager / org owner))

- Scopes: `read:enterprise (enterprise owner / billing manager / org owner)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Returns the resources assigned to a single cost center.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |
| cost_center_id | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Returns the resources assigned to a single cost center.

**Datapoints returned (1):**

- cost center resource membership - Which orgs/repos/users roll up to this business unit for chargeback (PII)

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `id` | string | - |
| `name` | string | - |
| `state` | string | - |
| `resources[].type` | string | - |
| `resources[].name` | string | - |

**Plans/tiers:** Enterprise Cloud

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/cost-centers

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/billing/cost-centers

---

### enterprise-budgets-list - List budgets for an enterprise

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/budgets`

**Auth:** bearer - Classic PAT (read:enterprise (enterprise owner / billing manager))

- Scopes: `read:enterprise (enterprise owner / billing manager)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Enhanced billing platform budgets feature. GET endpoints are read-only; POST/PATCH/DELETE manage budgets. Carries budget config plus current spend-against-budget signal.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Enhanced billing platform budgets feature. GET endpoints are read-only; POST/PATCH/DELETE manage budgets. Carries budget config plus current spend-against-budget signal.

**Datapoints returned (1):**

- budget thresholds and current spend - Configured budget amount, target (org/repo/cost-center/product), and tracked spend used for budget-vs-actual alerting

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `budgets[].id` | string | - |
| `budgets[].targetType` | string | - |
| `budgets[].budgetType` | string | - |

**Plans/tiers:** Enterprise Cloud

**Live check:** status 200; verified 2026-06-04; account: enterprise: cybage / org: ALMCybage (owner: pradeepborse); note: Live-verified 2xx against ALMCybage / cybage.

**Verification:** verified: path, datapoints; confidence: medium; source: https://docs.github.com/en/enterprise-cloud@latest/rest/billing/enhanced-billing

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/rest/billing/enhanced-billing

---

### org-codespaces-list - List Codespaces for the organization (billable ownership)

**Request:** `GET https://api.github.com/orgs/{org}/codespaces`

**Auth:** bearer - Classic PAT (admin:org) or fine-grained PAT

- Scopes: `admin:org`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Codespaces: read (organization) Caller must be an org admin. Closest org-level Codespaces cost/usage signal: enumerates active codespaces and billable_owner. Dollar spend itself comes through the enhanced usage report (product=codespaces).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |
| per_page | query | no | - | - |
| page | query | no | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Team or higher. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Caller must be an org admin. Closest org-level Codespaces cost/usage signal: enumerates active codespaces and billable_owner. Dollar spend itself comes through the enhanced usage report (product=codespaces).

**Datapoints returned (3):**

- active codespaces count - total_count of running/stored codespaces billed to the org
- billable owner per codespace - codespaces[].billable_owner identifies who the org is paying for (PII)
- codespace machine/state - machine type, state, last_used_at help estimate idle storage vs active compute spend

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `total_count` | integer | - |
| `codespaces[].billable_owner` | object | - |
| `codespaces[].machine` | object | - |
| `codespaces[].state` | string | - |
| `codespaces[].last_used_at` | string | - |

**Plans/tiers:** Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/rest/codespaces/organizations

**Source URLs:**
- https://docs.github.com/en/rest/codespaces/organizations

---

### org-actions-billing-legacy - Get GitHub Actions billing for an organization (LEGACY billing platform / GHES)

> DEPRECATED

**Request:** `GET https://api.github.com/orgs/{org}/settings/billing/actions`

**Auth:** bearer - Classic PAT (repo (classic PAT, org admin)) or fine-grained PAT

- Scopes: `repo (classic PAT, org admin)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Administration: read (organization) — where the endpoint still appears LEGACY: removed from the current GitHub.com REST reference and from the current fine-grained-permissions reference (migrated accounts use the enhanced usage report). Persists for accounts still on the legacy billing platform and on GHES (api/v3). Could not confirm on a current docs.github.com page; downgraded to verified=false.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Team or higher. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. LEGACY billing endpoint — removed from current GitHub.com REST reference; use the enhanced usage report (/settings/billing/usage) on migrated accounts. Persists on the legacy billing platform and GHES. LEGACY: removed from the current GitHub.com REST reference and from the current fine-grained-permissions reference (migrated accounts use the enhanced usage report). Persists for accounts still on the legacy billing platform and on GHES (api/v3). Could not confirm on a current docs.github.com page; downgraded to verified=false.

**Datapoints returned (1):**

- org Actions minutes by OS - total_minutes_used, total_paid_minutes_used, included_minutes, minutes_used_breakdown UBUNTU/MACOS/WINDOWS

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `total_minutes_used` | integer | - |
| `total_paid_minutes_used` | integer | - |
| `included_minutes` | integer | - |
| `minutes_used_breakdown` | object | - |

**Plans/tiers:** Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/actions/concepts/billing-and-usage

**Source URLs:**
- https://docs.github.com/en/actions/concepts/billing-and-usage

**Deprecated:** yes

---

### org-packages-billing-legacy - Get GitHub Packages billing for an organization (LEGACY / GHES)

> DEPRECATED

**Request:** `GET https://api.github.com/orgs/{org}/settings/billing/packages`

**Auth:** bearer - Classic PAT (repo (org admin))

- Scopes: `repo (org admin)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: LEGACY / GHES only; removed from current GitHub.com reference and fine-grained-permissions page. Unverified on a current page.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Team or higher. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. LEGACY billing endpoint — removed from current GitHub.com REST reference; use the enhanced usage report (/settings/billing/usage) on migrated accounts. Persists on the legacy billing platform and GHES. LEGACY / GHES only; removed from current GitHub.com reference and fine-grained-permissions page. Unverified on a current page.

**Datapoints returned (1):**

- org Packages bandwidth GB - total_gigabytes_bandwidth_used, total_paid_gigabytes_bandwidth_used, included_gigabytes_bandwidth

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `total_gigabytes_bandwidth_used` | integer | - |
| `total_paid_gigabytes_bandwidth_used` | integer | - |
| `included_gigabytes_bandwidth` | integer | - |

**Plans/tiers:** Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/actions/concepts/billing-and-usage

**Source URLs:**
- https://docs.github.com/en/actions/concepts/billing-and-usage

**Deprecated:** yes

---

### org-shared-storage-billing-legacy - Get shared storage billing for an organization (LEGACY / GHES)

> DEPRECATED

**Request:** `GET https://api.github.com/orgs/{org}/settings/billing/shared-storage`

**Auth:** bearer - Classic PAT (repo (org admin))

- Scopes: `repo (org admin)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: LEGACY / GHES only; removed from current GitHub.com reference and fine-grained-permissions page. Unverified on a current page.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| org | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Team or higher. Scope level: org. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. LEGACY billing endpoint — removed from current GitHub.com REST reference; use the enhanced usage report (/settings/billing/usage) on migrated accounts. Persists on the legacy billing platform and GHES. LEGACY / GHES only; removed from current GitHub.com reference and fine-grained-permissions page. Unverified on a current page.

**Datapoints returned (1):**

- org shared storage GB-days - days_left_in_billing_cycle, estimated_paid_storage_for_month, estimated_storage_for_month

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `days_left_in_billing_cycle` | integer | - |
| `estimated_paid_storage_for_month` | number | - |
| `estimated_storage_for_month` | number | - |

**Plans/tiers:** Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/actions/concepts/billing-and-usage

**Source URLs:**
- https://docs.github.com/en/actions/concepts/billing-and-usage

**Deprecated:** yes

---

### enterprise-actions-billing-legacy - Get GitHub Actions billing for an enterprise (LEGACY billing platform)

> DEPRECATED

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/actions`

**Auth:** bearer - Classic PAT (read:enterprise (classic PAT; enterprise admin)) or fine-grained PAT

- Scopes: `read:enterprise (classic PAT; enterprise admin)`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: Fine-grained: Enterprise administration: write (where it still appears for legacy-platform accounts) LEGACY: available to enterprise customers still on the legacy billing platform; also present in GHES. Removed from the current GHEC enterprise-admin/billing reference (now only shows advanced-security). Search-confirmed the path/shape but not on a current rendered reference page; verified=false.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. LEGACY billing endpoint — removed from current GitHub.com REST reference; use the enhanced usage report (/settings/billing/usage) on migrated accounts. Persists on the legacy billing platform and GHES. LEGACY: available to enterprise customers still on the legacy billing platform; also present in GHES. Removed from the current GHEC enterprise-admin/billing reference (now only shows advanced-security). Search-confirmed the path/shape but not on a current rendered reference page; verified=false.

**Datapoints returned (1):**

- Actions minutes used by OS - total_minutes_used, total_paid_minutes_used, included_minutes, minutes_used_breakdown UBUNTU/MACOS/WINDOWS

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `total_minutes_used` | integer | - |
| `total_paid_minutes_used` | integer | - |
| `included_minutes` | integer | - |
| `minutes_used_breakdown.UBUNTU` | integer | - |
| `minutes_used_breakdown.MACOS` | integer | - |
| `minutes_used_breakdown.WINDOWS` | integer | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/actions/concepts/billing-and-usage

**Source URLs:**
- https://docs.github.com/en/actions/concepts/billing-and-usage

**Deprecated:** yes

---

### enterprise-packages-billing-legacy - Get GitHub Packages billing for an enterprise (LEGACY)

> DEPRECATED

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/packages`

**Auth:** bearer - Classic PAT (read:enterprise)

- Scopes: `read:enterprise`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: LEGACY billing platform / GHES. Enterprise admin. Removed from current GHEC reference; could not render section on a current page. Path/fields inferred by symmetry with the org legacy schema.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. LEGACY billing endpoint — removed from current GitHub.com REST reference; use the enhanced usage report (/settings/billing/usage) on migrated accounts. Persists on the legacy billing platform and GHES. LEGACY billing platform / GHES. Enterprise admin. Removed from current GHEC reference; could not render section on a current page. Path/fields inferred by symmetry with the org legacy schema.

**Datapoints returned (1):**

- Packages bandwidth GB - total_gigabytes_bandwidth_used, total_paid_gigabytes_bandwidth_used, included_gigabytes_bandwidth

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `total_gigabytes_bandwidth_used` | integer | - |
| `total_paid_gigabytes_bandwidth_used` | integer | - |
| `included_gigabytes_bandwidth` | integer | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/actions/concepts/billing-and-usage

**Source URLs:**
- https://docs.github.com/en/actions/concepts/billing-and-usage

**Deprecated:** yes

---

### enterprise-shared-storage-billing-legacy - Get shared storage billing for an enterprise (LEGACY)

> DEPRECATED

**Request:** `GET https://api.github.com/enterprises/{enterprise}/settings/billing/shared-storage`

**Auth:** bearer - Classic PAT (read:enterprise)

- Scopes: `read:enterprise`
- Credential: GitHub PAT (classic or fine-grained) sent as Authorization: Bearer <token>.
- Notes: LEGACY billing platform / GHES. Enterprise admin. Removed from current GHEC reference; section not rendered on a current page. Fields inferred from the legacy schema.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| enterprise | path | yes | - | - |

**Rate limits:** Standard GitHub REST rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GHES uses base https://HOST/api/v3 ; GHEC data-residency tenants use https://api.SUBDOMAIN.ghe.com. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. LEGACY billing endpoint — removed from current GitHub.com REST reference; use the enhanced usage report (/settings/billing/usage) on migrated accounts. Persists on the legacy billing platform and GHES. LEGACY billing platform / GHES. Enterprise admin. Removed from current GHEC reference; section not rendered on a current page. Fields inferred from the legacy schema.

**Datapoints returned (1):**

- shared storage GB-days estimate - days_left_in_billing_cycle, estimated_paid_storage_for_month, estimated_storage_for_month

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `days_left_in_billing_cycle` | integer | - |
| `estimated_paid_storage_for_month` | number | - |
| `estimated_storage_for_month` | number | - |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/actions/concepts/billing-and-usage

**Source URLs:**
- https://docs.github.com/en/actions/concepts/billing-and-usage

**Deprecated:** yes

---

### graphql-user-contributions-collection - User contributionsCollection (totals)

**Purpose:** GraphQL query. Selection: user.contributionsCollection

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (read:user, repo) or fine-grained PAT

- Scopes: `read:user`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Metadata: Read; Issues: Read; Pull requests: Read; Contents: Read Public contributions need no scope (or read:user). Including PRIVATE-repo contributions as detailed totals (vs restrictedContributionsCount) requires token visibility/membership AND the user's profile 'private contributions' setting allowing it. Privacy gate confirmed by GitHub contribution-settings docs.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| login | body | yes | User login passed to top-level user() query | octocat |
| from | body | no | DateTime window start; window max span is 1 year | 2025-01-01T00:00:00Z |
| to | body | no | DateTime window end (<= from + 1 year) | 2025-12-31T00:00:00Z |
| organizationID | body | no | Scope contributions to a single organization | MDEyOk9yZ2FuaXphdGlvbjE= |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Public contributions need no scope (or read:user). Including PRIVATE-repo contributions as detailed totals (vs restrictedContributionsCount) requires token visibility/membership AND the user's profile 'private contributions' setting allowing it. Privacy gate confirmed by GitHub contribution-settings docs.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (6):**

- Commits authored (windowed) - Per-user commit volume over a date range (max 1yr). No REST per-user cross-repo aggregate. (PII)
- Pull requests opened (windowed) - Per-user PR creation count over a window. (PII)
- PR reviews submitted (windowed) - Per-user review participation; core code-review signal. (PII)
- Issues opened (windowed) - Per-user issue creation count. (PII)
- Repositories created (windowed) - New repos a user created in the window. (PII)
- Restricted (private) contribution count - Volume of hidden private contributions without exposing detail. (PII)

**Report / response file fields (11):**

| path | type | description |
| --- | --- | --- |
| `totalCommitContributions` | Int! | Commits authored in the window across all repos |
| `totalPullRequestContributions` | Int! | PRs opened in the window |
| `totalPullRequestReviewContributions` | Int! | PR reviews submitted in the window |
| `totalIssueContributions` | Int! | Issues opened in the window |
| `totalRepositoryContributions` | Int! | New repositories created in the window |
| `restrictedContributionsCount` | Int! | Count of contributions to private/inaccessible repos (privacy gate) |
| `hasAnyContributions` | Boolean! | Whether the user has any contributions ever |
| `hasActivityInThePast` | Boolean! | Whether the user was active before the window |
| `startedAt` | DateTime! | Resolved window start |
| `endedAt` | DateTime! | Resolved window end |
| `totalRepositoriesWithContributedCommits` | Int! | Distinct repos the user committed to |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/graphql/reference/objects
- https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

---

### graphql-contribution-calendar - ContributionCalendar (daily heatmap)

**Purpose:** GraphQL query. Selection: user.contributionsCollection.contributionCalendar

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (read:user, repo) or fine-grained PAT

- Scopes: `read:user`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Metadata: Read Calendar reflects only token-visible contributions; private counted only with access and profile-visibility allowance.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| login | body | yes | User login | octocat |
| from | body | no | Window start (follows contributionsCollection window) | 2025-01-01T00:00:00Z |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. NOT verified against a live reference page this session. Calendar reflects only token-visible contributions; private counted only with access and profile-visibility allowance.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (3):**

- Daily contribution heatmap - Per-day activity intensity; enables streak/cadence/active-days analysis. No REST equivalent. (PII)
- Total contributions (calendar) - Windowed green-squares total. (PII)
- Active days / streak - Derivable from per-day counts. (PII)

**Report / response file fields (5):**

| path | type | description |
| --- | --- | --- |
| `contributionCalendar.totalContributions` | Int! | Sum of contributions on the calendar in the window |
| `contributionCalendar.weeks[].contributionDays[].contributionCount` | Int! | Per-day contribution count |
| `contributionCalendar.weeks[].contributionDays[].date` | Date! | Calendar day |
| `contributionCalendar.weeks[].contributionDays[].weekday` | Int! | 0-6 day index |
| `contributionCalendar.weeks[].contributionDays[].contributionLevel` | ContributionLevel! | Bucketed intensity NONE..FOURTH_QUARTILE |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: medium; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

---

### graphql-contributions-by-repository - ContributionsCollection by-repository breakdowns

**Purpose:** GraphQL query. Selection: user.contributionsCollection.{commit,issue,pullRequest,pullRequestReview}ContributionsByRepository

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (read:user, repo) or fine-grained PAT

- Scopes: `read:user`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Metadata: Read; Contents: Read; Pull requests: Read; Issues: Read maxRepositories arg (commonly default 25 / max 100 — not re-confirmed on a live rendered page this session). Private repos appear only with access.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| login | body | yes | User login | octocat |
| maxRepositories | body | no | Limit on repos returned per breakdown | 100 |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: user. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. NOT verified against a live reference page this session. maxRepositories arg (commonly default 25 / max 100 — not re-confirmed on a live rendered page this session). Private repos appear only with access.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (2):**

- Per-user per-repo commit split - Where a user's commits land, repo by repo, in one call. (PII)
- Per-user per-repo review split - Which repos a user reviews most. (PII)

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `commitContributionsByRepository[].repository.nameWithOwner` | String! | Repo the user committed to |
| `commitContributionsByRepository[].contributions.totalCount` | Int! | Commit count in that repo |
| `pullRequestReviewContributionsByRepository[].contributions.totalCount` | Int! | Reviews per repo |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: medium; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

---

### graphql-search-issuecount - search() aggregate counts (issueCount / repositoryCount / userCount / discussionCount)

**Purpose:** GraphQL query. Selection: search(query, type)

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Metadata: Read Counts honor token visibility. Use first:1 to fetch only *Count fields cheaply. SearchType enum = ISSUE\|REPOSITORY\|USER\|DISCUSSION (no code/wiki types).

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| query | body | yes | Search query string with web-search qualifiers | org:acme is:pr is:merged merged:2025-05-01..2025-05-31 |
| type | body | yes | SearchType enum: ISSUE \| REPOSITORY \| USER \| DISCUSSION | ISSUE |
| first | body | no | Page size; set first:1 when you only need the count | 1 |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: global. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Counts honor token visibility. Use first:1 to fetch only *Count fields cheaply. SearchType enum = ISSUE\|REPOSITORY\|USER\|DISCUSSION (no code/wiki types).

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (5):**

- Merged PR count by window/author/label - search(type:ISSUE,'is:pr is:merged ...').issueCount is an O(1) merged-PR throughput counter sliced by any qualifier.
- Open vs closed issue counts - Two searches give open/closed backlog counts for any repo/org/label.
- Review-requested / draft / stale PR counts - issueCount with qualifiers (review:required, draft:true, updated:<date).
- Repository count by topic/language/org - repositoryCount for inventory/adoption sizing.
- Per-author throughput - author:<login> slices counts per person. (PII)

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `search.issueCount` | Int! | Issues+PRs matching (type:ISSUE). The cheap aggregate counter. |
| `search.repositoryCount` | Int! | Repositories matching (type:REPOSITORY) |
| `search.userCount` | Int! | Users matching (type:USER) |
| `search.discussionCount` | Int! | Discussions matching (type:DISCUSSION) |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions

**Source URLs:**
- https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

---

### graphql-ratelimit - rateLimit (budget introspection)

**Purpose:** GraphQL query. Selection: rateLimit

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - PAT / token
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Any authenticated token. CORRECTION: querying rateLimit DOES count against the limit (running the call is charged); docs recommend using response headers or pre-calculating cost. No 'dryRun' argument is documented on rateLimit.

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: global. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Any authenticated token. CORRECTION: querying rateLimit DOES count against the limit (running the call is charged); docs recommend using response headers or pre-calculating cost. No 'dryRun' argument is documented on rateLimit.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (2):**

- GraphQL budget remaining - Operational metric for ingestion self-throttling: remaining + resetAt.
- Per-query cost / node count - Lets the collector verify it stays under 500k node and 2000 pt/min ceilings.

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `rateLimit.limit` | Int! | Max points/hr for this token (5000 / 10000 / installation-scaled) |
| `rateLimit.cost` | Int! | Points the current query costs (the call is still charged) |
| `rateLimit.remaining` | Int! | Points left this window |
| `rateLimit.used` | Int! | Points consumed this window |
| `rateLimit.resetAt` | DateTime! | When the window resets |
| `rateLimit.nodeCount` | Int! | Nodes the query returns (vs 500k cap) |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** verified: path, datapoints; confidence: high; source: https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api

**Source URLs:**
- https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api

---

### graphql-organization-counts - Organization rollup counts

**Purpose:** GraphQL query. Selection: organization.{membersWithRole,repositories,teams,pendingMembers}

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (read:org, repo) or fine-grained PAT

- Scopes: `read:org`, `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Organization administration: Read; Members: Read; Metadata: Read membersWithRole/pendingMembers require org membership/read:org. Private repos in repositories.totalCount need repo access.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| login | body | yes | Organization login | acme |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: org. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. NOT verified against a live reference page this session. membersWithRole/pendingMembers require org membership/read:org. Private repos in repositories.totalCount need repo access.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (4):**

- Org member count - Denominator for adoption/penetration metrics.
- Pending invitations - Onboarding funnel signal.
- Org repository count - Inventory size.
- Team count - Organizational structure size.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `membersWithRole.totalCount` | Int! | Active members (adoption denominator) |
| `pendingMembers.totalCount` | Int! | Invited-but-not-joined users |
| `repositories.totalCount` | Int! | Repos owned by the org |
| `teams.totalCount` | Int! | Number of teams |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: medium; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects
- https://docs.github.com/en/graphql/guides/migrating-from-rest-to-graphql

---

### graphql-repository-counts - Repository connection totalCounts

**Purpose:** GraphQL query. Selection: repository.{pullRequests,issues,stargazers,forks,watchers,collaborators,releases}

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (repo) or fine-grained PAT

- Scopes: `repo`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: Fine-grained: Metadata: Read; Pull requests: Read; Issues: Read Public repos need no scope. Connections accept states: (e.g. pullRequests(states:MERGED)) for merged/open/closed totalCounts in one query.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| owner | body | yes | Repo owner | acme |
| name | body | yes | Repo name | web |
| states | body | no | Filter on pullRequests/issues (OPEN/CLOSED/MERGED) | MERGED |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: Free (all plans incl. personal/Team/EC/ES). Scope level: repo. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. NOT verified against a live reference page this session. Public repos need no scope. Connections accept states: (e.g. pullRequests(states:MERGED)) for merged/open/closed totalCounts in one query.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (5):**

- Merged/open/closed PR totals per repo - One query yields throughput + WIP via states-filtered connections.
- Open issue backlog - Backlog size as a single totalCount.
- Stars / forks / watchers - Popularity/engagement counters.
- Collaborator count - Repo team size.
- Release count - Shipping cadence proxy.

**Report / response file fields (6):**

| path | type | description |
| --- | --- | --- |
| `pullRequests(states:MERGED).totalCount` | Int! | Merged PR count |
| `issues(states:OPEN).totalCount` | Int! | Open issue backlog |
| `stargazers.totalCount` | Int! | Stars |
| `forks.totalCount` | Int! | Forks |
| `collaborators.totalCount` | Int! | Collaborators |
| `releases.totalCount` | Int! | Release count |

**Plans/tiers:** Free, Team, Enterprise Cloud, Enterprise Server

**Verification:** confidence: medium; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

**Source URLs:**
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects
- https://docs.github.com/en/graphql/guides/migrating-from-rest-to-graphql

---

### graphql-enterprise-rollup - Enterprise rollup (members/orgs/owner info)

**Purpose:** GraphQL query. Selection: enterprise.{members,organizations,ownerInfo}

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (read:enterprise, read:org)

- Scopes: `read:enterprise`, `read:org`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: enterprise() resolves on GHEC AND GHES; null/error on Free/Team. Classic PAT (read:enterprise / admin:enterprise) is the documented auth path; fine-grained PAT support for enterprise-admin GraphQL is NOT documented. ownerInfo fields require enterprise-owner auth. Base URLs: GHES https://HOST/api/graphql; GHEC data residency https://api.SUBDOMAIN.ghe.com/graphql.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| slug | body | yes | Enterprise slug | acme-inc |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. NOT verified against a live reference page this session. enterprise() resolves on GHEC AND GHES; null/error on Free/Team. Classic PAT (read:enterprise / admin:enterprise) is the documented auth path; fine-grained PAT support for enterprise-admin GraphQL is NOT documented. ownerInfo fields require enterprise-owner auth. Base URLs: GHES https://HOST/api/graphql; GHEC data residency https://api.SUBDOMAIN.ghe.com/graphql.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (3):**

- Enterprise member count - Top-level adoption denominator across all orgs.
- Org count in enterprise - Scale of the enterprise.
- Outside collaborator / pending counts - External-access surface at enterprise scope.

**Report / response file fields (4):**

| path | type | description |
| --- | --- | --- |
| `members.totalCount` | Int! | Enterprise-wide member count |
| `organizations.totalCount` | Int! | Number of orgs in the enterprise |
| `ownerInfo.admins.totalCount` | Int! | Enterprise admins |
| `ownerInfo.outsideCollaborators.totalCount` | Int! | Outside collaborators across the enterprise |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** confidence: medium; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/enterprise-cloud@latest/graphql/guides/managing-enterprise-accounts

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/graphql/guides/managing-enterprise-accounts
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

---

### graphql-enterprise-billing-info - EnterpriseBillingInfo (license/storage/bandwidth)

**Purpose:** GraphQL query. Selection: enterprise.billingInfo

**Request:** `POST https://api.github.com/graphql/graphql`

**Auth:** bearer - Classic PAT (read:enterprise, manage_billing:enterprise)

- Scopes: `read:enterprise`, `manage_billing:enterprise`
- Credential: GitHub PAT (classic or fine-grained) sent as a bearer token to the GraphQL endpoint.
- Notes: CORRECTION: billing data requires manage_billing:enterprise (per managing-enterprise-accounts guide), not read:enterprise alone. Requires enterprise-owner auth. Storage/bandwidth fields are GHES-centric; on GHEC billing is increasingly served via REST billing-platform endpoints. Exact scalar types (Int vs Float) of usage/quota fields not re-confirmable on client-rendered dotcom pages.

**Parameters:**

| name | in | required | description | example |
| --- | --- | --- | --- | --- |
| slug | body | yes | Enterprise slug | acme-inc |

**Rate limits:** Standard GitHub GraphQL rate limits (5,000/hr authenticated; secondary limits apply). Audit-log endpoints capped at 1,750 q/h.

**Gotchas:** Min license: GitHub Enterprise Cloud (also recent GHES) — not on Free/Team. Scope level: enterprise. GraphQL: POST a query to https://api.github.com/graphql (GHES: https://HOST/api/graphql). The `path` field holds the GraphQL selection, not a URL path. List endpoints are paginated (per_page max 100; follow Link rel=next). Subject to GitHub REST/GraphQL rate limits. Research confidence: LOW — re-confirm fields before relying on them. NOT verified against a live reference page this session. CORRECTION: billing data requires manage_billing:enterprise (per managing-enterprise-accounts guide), not read:enterprise alone. Requires enterprise-owner auth. Storage/bandwidth fields are GHES-centric; on GHEC billing is increasingly served via REST billing-platform endpoints. Exact scalar types (Int vs Float) of usage/quota fields not re-confirmable on client-rendered dotcom pages.

**Not tested reason:** GraphQL requires a POST body (query) — not fireable from a GET-only try-it console.

**Datapoints returned (3):**

- Seat utilization (used vs available licenses) - totalLicenses minus totalAvailableLicenses gives consumed seats.
- Licensable users count - Eligible population for seat assignment.
- Storage / bandwidth usage vs quota - Packages/LFS storage and transfer vs quota (GHES-centric; field types unverified).

**Report / response file fields (3):**

| path | type | description |
| --- | --- | --- |
| `billingInfo.totalLicenses` | Int! | Total purchased licenses (seats) |
| `billingInfo.totalAvailableLicenses` | Int! | Unused licenses |
| `billingInfo.allLicensableUsersCount` | Int! | Users eligible to consume a license |

**Plans/tiers:** Enterprise Cloud, Enterprise Server

**Verification:** confidence: low; note: Unverified this session — schema/field paths provisional.; source: https://docs.github.com/en/enterprise-cloud@latest/graphql/guides/managing-enterprise-accounts

**Source URLs:**
- https://docs.github.com/en/enterprise-cloud@latest/graphql/guides/managing-enterprise-accounts
- https://docs.github.com/en/enterprise-server@3.15/graphql/reference/objects

---
