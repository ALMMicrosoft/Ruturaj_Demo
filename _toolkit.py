"""
_toolkit.py  --  the ONLY shared helper a KPI verification script needs.

It is deliberately tiny and app-independent (just `httpx` + the standard
library). It holds the generic plumbing every script repeats:

  * load the project's credentials from a config file (server-side, gitignored),
  * make an authenticated GitHub / Jira GET,
  * follow a GitHub "report" download link and gunzip it,
  * pretty-print the full verification trace so a developer can check a KPI,
    line by line, against its definition in the Excel master sheet.

Everything KPI-SPECIFIC (which endpoints, what to extract, the formula) lives
INLINE in each kpis script -- so one file tells the whole story for one KPI.

---------------------------------------------------------------------------
SETUP (each developer does this once)
---------------------------------------------------------------------------
  pip install httpx
  copy project.config.example.json  ->  .secrets/project.json   and fill it in
    (or point the env var KPILAB_CONFIG at an existing project.json)

RUN a KPI script:
  python kpi_01_active_ai_tool_adoption_rate.py          # trimmed raw payloads
  python kpi_01_active_ai_tool_adoption_rate.py --raw     # full raw payloads
---------------------------------------------------------------------------
"""
from __future__ import annotations

import asyncio
import base64
import datetime
import gzip
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

import httpx

# Make stdout UTF-8 so the trace prints cleanly on any console (Windows cp1252
# would otherwise mojibake separators and choke on non-ASCII in raw payloads).
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

# ===========================================================================
# 1. CONFIG  --  where credentials come from (never hard-coded in a script)
# ===========================================================================
# The config file shape (see project.config.example.json):
#   { "project": "...", "tools": { "<toolId>": { "<field>": "<value>", ... } } }
# Tokens live ONLY in this gitignored file and are read at run time.

def _config_path() -> Path:
    env = os.environ.get("KPILAB_CONFIG")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent / ".secrets" / "project.json"


def load_config() -> dict:
    p = _config_path()
    if not p.exists():
        raise SystemExit(
            f"No config found at {p}.\n"
            "Copy project.config.example.json to .secrets/project.json and fill it "
            "in, or set the KPILAB_CONFIG environment variable to your project.json."
        )
    data = json.loads(p.read_text("utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("tools"), dict):
        raise SystemExit(f"Config at {p} is malformed (need a top-level 'tools' object).")
    return data


def cfg(tool_id: str, key: str) -> str:
    """One credential/identifier for a tool, trimmed; '' if absent."""
    v = load_config().get("tools", {}).get(tool_id, {}).get(key)
    return v.strip() if isinstance(v, str) else ""


def project_name() -> str:
    return load_config().get("project") or "(unnamed project)"


# ===========================================================================
# 2. A single upstream call result -- carries the request preview + raw payload
# ===========================================================================
@dataclass
class Call:
    method: str
    url: str
    headers: dict[str, str]          # Authorization is redacted
    status: int | None = None
    raw: Any = None                  # parsed upstream payload (after following links)
    note: str | None = None          # e.g. "followed a signed download link + gunzipped"

    @property
    def ok(self) -> bool:
        return self.status is not None and 200 <= self.status < 300


def _redact(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers.items():
        out[k] = "***redacted***" if k.lower() == "authorization" else v
    return out


def _record(client, method, url, status, headers, response, note=None):
    """If the client carries a `_kpi_log` list, append this real API exchange to it.
    The HTML viewer shows these as the actual raw responses per datapoint. Console
    runs don't set `_kpi_log`, so this is a no-op there."""
    log = getattr(client, "_kpi_log", None)
    if isinstance(log, list):
        log.append({"method": method, "url": url, "status": status,
                    "headers": headers, "response": response, "note": note})


# ===========================================================================
# 3. GITHUB transport  (GitHub Copilot + GitHub REST share this)
# ===========================================================================
GITHUB = "https://api.github.com"


async def gh_get(client: httpx.AsyncClient, path: str, *, token: str,
                 api_version: str) -> Call:
    """An authenticated GitHub GET. `path` begins with '/'. Returns parsed JSON."""
    url = f"{GITHUB}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": api_version,
    }
    r = await client.get(url, headers=headers)
    try:
        body = r.json()
    except Exception:
        body = None
    _record(client, "GET", url, r.status_code, _redact(headers), body)
    return Call("GET", url, _redact(headers), r.status_code, body)


async def _follow_link(client: httpx.AsyncClient, link: str) -> Any:
    """Follow a signed download link; gunzip if gzipped; parse JSON or JSONL."""
    r = await client.get(link)
    buf = r.content
    if len(buf) >= 2 and buf[0] == 0x1F and buf[1] == 0x8B:        # gzip magic bytes
        buf = gzip.decompress(buf)
    text = buf.decode("utf-8", "replace")
    try:
        parsed: Any = json.loads(text)                             # single JSON document
    except Exception:
        parsed = []                                                # JSONL: one object per line
        for line in text.splitlines():
            line = line.strip()
            if line:
                try:
                    parsed.append(json.loads(line))
                except Exception:
                    pass
    # signed links carry a short-lived token in the query string -> drop it.
    _record(client, "GET", link.split("?")[0] + "  (signed download link)",
            r.status_code, {}, parsed,
            note="followed download_links[0]; gunzipped + parsed report file")
    return parsed


async def gh_report(client: httpx.AsyncClient, path: str, *, token: str,
                    api_version: str = "2026-03-10") -> Call:
    """A GitHub Copilot 'reports' call (2-stage).

    The report endpoint returns signed `download_links`; the real data is the
    (often gzipped) file behind the first link. `raw` is that parsed file -- i.e.
    exactly what the value is extracted from.
    """
    res = await gh_get(client, path, token=token, api_version=api_version)
    if not res.ok:
        return res
    body = res.raw if isinstance(res.raw, dict) else {}
    links = body.get("download_links")
    first = links[0] if isinstance(links, list) and links else None
    if not isinstance(first, str):
        return res
    res.raw = await _follow_link(client, first)
    res.note = ("report endpoint returned signed download_links; followed the first "
                "link and parsed the (gzipped) report file -- shown as raw below")
    return res


# ===========================================================================
# 4. JIRA transport  (Jira Cloud REST -- HTTP Basic email:apiToken)
# ===========================================================================
async def jira_get(client: httpx.AsyncClient, path: str, *, email: str,
                   token: str, site: str) -> Call:
    """An authenticated Jira Cloud GET. `site` like 'your-site.atlassian.net'."""
    base = f"https://{site}"
    url = f"{base}{path}"
    basic = base64.b64encode(f"{email}:{token}".encode()).decode()
    headers = {"Accept": "application/json", "Authorization": f"Basic {basic}"}
    r = await client.get(url, headers=headers)
    try:
        body = r.json()
    except Exception:
        body = None
    _record(client, "GET", url, r.status_code, _redact(headers), body)
    return Call("GET", url, _redact(headers), r.status_code, body)


# ===========================================================================
# 4b. CLAUDE / ANTHROPIC transport  (Admin API -- x-api-key: sk-ant-admin...)
# ===========================================================================
async def claude_get(client: httpx.AsyncClient, path: str, *, admin_key: str,
                     anthropic_version: str = "2023-06-01",
                     params: dict | None = None) -> Call:
    """An authenticated Anthropic Admin API GET (usage / cost / Claude Code
    analytics). `path` begins with '/', e.g. '/v1/organizations/usage_report/messages'.
    Auth is the org admin key via the x-api-key header (NOT Bearer)."""
    url = f"https://api.anthropic.com{path}"
    headers = {
        "x-api-key": admin_key,
        "anthropic-version": anthropic_version,
        "content-type": "application/json",
    }
    r = await client.get(url, headers=headers, params=params)
    try:
        body = r.json()
    except Exception:
        body = None
    _record(client, "GET", str(r.request.url), r.status_code, _redact_kv(headers), body)
    return Call("GET", str(r.request.url), _redact_kv(headers), r.status_code, body)


def _redact_kv(headers: dict[str, str]) -> dict[str, str]:
    """Redact the Anthropic key (x-api-key) as well as Authorization."""
    out: dict[str, str] = {}
    for k, v in headers.items():
        out[k] = "***redacted***" if k.lower() in ("authorization", "x-api-key") else v
    return out


# ===========================================================================
# 5. A KPI input datapoint  --  one number the formula consumes
# ===========================================================================
@dataclass
class Datapoint:
    label: str
    # `source` is a plain-English description of WHERE the value comes from and
    # HOW it is derived -- the first thing a developer reads to verify it.
    source: str
    # `description` = plain-English WHAT this datapoint is (its meaning in the
    # formula). `example` = a grounded "e.g. ..." showing a real value, so a
    # developer can sanity-check the number against a concrete case.
    description: str = ""
    example: str = ""
    # `plain` = a one-line plain-English summary a brand-new developer grasps at a
    # glance (no jargon). The `steps` below give the granular detail; together they
    # must let a fresher understand the value WITHOUT reading the code.
    plain: str = ""
    # `paths` = the JSON path(s) in the raw response this datapoint reads, in dot
    # notation with `[]` for an array wildcard (e.g. "seat_breakdown.total",
    # "day_totals[].weekly_active_users"). The HTML viewer highlights exactly
    # these nodes in the formatted JSON. Console output ignores this field.
    paths: list[str] = field(default_factory=list)
    # `steps` = the calculation logic, step by step, in plain English: how this
    # datapoint's value is derived from the raw response (the call, the field(s)
    # read, the aggregation). Printed on the console and shown in the HTML viewer.
    steps: list[str] = field(default_factory=list)
    # `fetch` performs the real upstream call(s); `extract` pulls the number from
    # the raw payload. Splitting them is what makes the value verifiable: the
    # trace shows the raw response right next to the extracted number.
    fetch: Callable[[httpx.AsyncClient], Awaitable[Call]] | None = None
    extract: Callable[[Any], float | None] | None = None
    availability: str = "live"        # live | pending | unavailable
    reason: str | None = None         # why pending/unavailable


# ===========================================================================
# 6. THE RUNNER  --  prints the full, human-checkable verification trace
# ===========================================================================
def _trim(value: Any, full: bool, limit: int = 1500) -> str:
    text = json.dumps(value, indent=2, ensure_ascii=False)
    if full or len(text) <= limit:
        return text
    return text[:limit] + f"\n... [{len(text) - limit} more chars -- run with --raw for full payload]"


def run_kpi(kpi: dict, datapoints: list[Datapoint],
            compute: Callable[..., float | None]) -> None:
    """Entry point for every script's `__main__`. Runs the KPI live and prints:
    the Excel definition, each datapoint's request + raw response + extracted
    value, then the formula substituted with the live numbers and the result."""
    full = "--raw" in sys.argv
    asyncio.run(_run_kpi(kpi, datapoints, compute, full))


async def _run_kpi(kpi: dict, datapoints: list[Datapoint],
                   compute: Callable[..., float | None], full: bool) -> None:
    line = "=" * 74
    print(line)
    print(f"KPI #{kpi.get('num')} · {kpi.get('name')} · {kpi.get('index')} index")
    print("-" * 74)
    if kpi.get("plain"):
        print(f"  IN SHORT      : {kpi.get('plain')}")
    print("These fields must match the Excel master sheet row for this KPI:")
    print(f"  DEFINITION    : {kpi.get('definition')}")
    print(f"  HOW MEASURED  : {kpi.get('how_measured')}")
    print(f"  FORMULA       : {kpi.get('formula')}")
    print(f"  UNIT          : {kpi.get('unit')}   CADENCE: {kpi.get('cadence')}"
          + (f"   DIRECTION: {kpi.get('direction')}" if kpi.get('direction') else ""))
    if kpi.get("interpretation"):
        print(f"  INTERPRETATION: {kpi.get('interpretation')}")
    print(f"  SOURCE TOOLS  : {kpi.get('tools')}")
    print(f"  PROJECT       : {project_name()}")
    print(line)

    values: list[float | None] = []
    records: list[dict] = []   # per-datapoint rows for the report envelope (label/value/ok/raw)
    async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
        for i, dp in enumerate(datapoints, 1):
            print(f"\n[{i}] {dp.label}   ({dp.availability})")
            if dp.plain:
                print(f"    in short: {dp.plain}")
            if dp.description:
                print(f"    what   : {dp.description}")
            print(f"    source : {dp.source}")
            if dp.example:
                print(f"    e.g.   : {dp.example}")
            if dp.steps:
                print("    logic  : how this value is calculated, step by step:")
                for n, step in enumerate(dp.steps, 1):
                    print(f"             {n}. {step}")
            if dp.availability != "live" or dp.fetch is None or dp.extract is None:
                reason = dp.reason or "no live source wired"
                print(f"    BLOCKED: {reason}")
                values.append(None)
                records.append({"label": dp.label, "source": dp.source, "value": None,
                                "ok": False, "error": reason, "raw": None})
                continue
            try:
                call = await dp.fetch(client)
            except Exception as e:           # noqa: BLE001 -- surface any failure plainly
                print(f"    ERROR  : {e}")
                values.append(None)
                records.append({"label": dp.label, "source": dp.source, "value": None,
                                "ok": False, "error": str(e), "raw": None})
                continue
            print(f"    request: {call.method} {call.url}")
            print(f"    headers: {call.headers}")
            if call.note:
                print(f"    note   : {call.note}")
            print(f"    status : {call.status}")
            print(f"    raw    :\n{_indent(_trim(call.raw, full))}")
            value = dp.extract(call.raw) if call.ok else None
            print(f"    -> EXTRACTED: {value}")
            values.append(value)
            records.append({"label": dp.label, "source": dp.source, "value": value,
                            "ok": bool(call.ok), "error": None if call.ok else f"HTTP {call.status}",
                            "raw": call.raw})

    print("\n" + "-" * 74)
    print("HOW THIS KPI IS CALCULATED (step by step):")
    for i, (dp, v) in enumerate(zip(datapoints, values), 1):
        print(f"  {i}. {dp.label} = {_fmt(v)}")
    print(f"  {len(values) + 1}. Apply the formula: {kpi.get('formula')}")
    for step in kpi.get("steps", []):
        print(f"       - {step}")
    computable = bool(values and all(v is not None for v in values))
    result = compute(*values) if computable else None
    if computable:
        print(f"  => RESULT = {_fmt(result)} {kpi.get('unit', '')}".rstrip())
        print("\nCheck the RESULT and every step above against the Excel definition.")
    else:
        print("  => NOT COMPUTABLE -- at least one datapoint did not resolve (see above).")
        print("     This shows exactly which input is missing/blocked.")
    print(line)

    _write_envelope(kpi, records, result, computable)


def _write_envelope(kpi: dict, datapoint_records: list[dict],
                    result: float | None, computable: bool) -> None:
    """Write the run envelope to docs/reports/_data/ (read by export_pdf.py). On
    `--pdf`, also render HTML + PDF. Never raises -- reporting must not break a run."""
    try:
        here = Path(__file__).resolve().parent
        module = Path(sys.argv[0]).stem or "kpi"
        data_dir = here / "docs" / "reports" / "_data"
        data_dir.mkdir(parents=True, exist_ok=True)
        env = {
            "module": module,
            "project": project_name(),
            "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "argv": sys.argv[1:],
            "kpi": kpi,
            "computable": computable,
            "result": result,
            "datapoints": datapoint_records,
        }
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = data_dir / f"{module}__{ts}.json"
        path.write_text(json.dumps(env, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(f"\n  [report] envelope -> {path}")
        if "--pdf" in sys.argv:
            import export_pdf
            export_pdf.export(str(path))
    except Exception as e:                   # noqa: BLE001 -- reporting must never break the run
        print(f"  (report/PDF step skipped: {e})")


def _indent(text: str, pad: str = "             ") -> str:
    return "\n".join(pad + ln for ln in text.splitlines())


def _fmt(v: float | None) -> str:
    if v is None:
        return "None"
    return str(int(v)) if float(v).is_integer() else f"{v:.4f}"
