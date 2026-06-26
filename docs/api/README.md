# API Endpoint Reference

The complete, verified API surface for the four tools in scope — **every** endpoint
the research identified, not just the ones the KPI scripts call. Use these to
confirm that a datapoint's `source` (method, path, field) in a `kpi_*.py` script is
real, and to discover endpoints for KPIs not yet scripted.

Extracted from the verified catalog (originally `genai-tracker/lib/catalog/*.ts`);
this bundle is now self-sufficient.

| Tool | Reference | Endpoints |
|------|-----------|-----------|
| GitHub Copilot | [`github-copilot.md`](github-copilot.md) | 20 |
| GitHub | [`github.md`](github.md) | 192 |
| Jira (Cloud) | [`jira.md`](jira.md) | 93 |
| Claude (Anthropic) | [`claude.md`](claude.md) | 30 |
| **Total** | | **335** |

Each tool reference contains: the tool blurb + plans/tiers table + feasibility
verdict; an overview table of all endpoints; and, per endpoint, the purpose,
request line, auth, headers, parameters, response shape, returned datapoints,
report-file fields (for GitHub Copilot download-link reports), example
request/response, required plans, rate limits, and live-check status.

See also [`../FEASIBILITY.md`](../FEASIBILITY.md) for which KPIs these endpoints can
actually feed (computable / pending / blocked + reasons).
