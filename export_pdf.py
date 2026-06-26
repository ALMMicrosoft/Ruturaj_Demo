"""
============================================================================
export_pdf.py  --  ONE generic PDF report generator, reusable by EVERY kpi_NN_*.py.
============================================================================
READ THIS BEFORE RUNNING.

WHAT IT DOES
  It does NOT re-run a KPI or call any API. It reads the JSON envelope that a KPI run
  already wrote to docs/reports/_data/, renders it to HTML, and prints that HTML to a
  PDF with headless Microsoft Edge. Each export writes its OWN timestamped file, so
  nothing is ever overwritten.

HOW TO GENERATE A PDF  (two ways - both work for EVERY KPI, no per-script setup)
  A) Auto-generate during a KPI run: just add --pdf to the KPI command.
       python kpi_39_net_ai_contributed_loc_per_developer_per_sprint.py \
              --start 2026-05-15 --end 2026-05-30 --pdf
     The run writes its JSON, then this exporter produces the PDF automatically.

  B) Generate later from an existing run, with this script directly:
       # latest run of a KPI (pass the module name, with or without .py):
       python export_pdf.py kpi_39_net_ai_contributed_loc_per_developer_per_sprint
       # ...or point at one specific envelope file:
       python export_pdf.py docs/reports/_data/kpi_39_..._20260617-175721.json

REQUIREMENTS
  - Microsoft Edge installed (used headless to render the PDF; NO pip dependency -
    requirements.txt stays just httpx). If Edge isn't found, the HTML is still written
    and a warning is printed - the KPI run itself never fails.
  - A KPI must have been run at least once (so its JSON envelope exists under
    docs/reports/_data/). Running with --pdf does both in one step.

WHERE OUTPUT LANDS
  - Reports : docs/reports/report_<module>__<window>__<timestamp>.{html,pdf}
              (uniquely named per run - nothing is overwritten).
  - Run data: docs/reports/_data/*.json  (written automatically on every KPI run;
              this is what the exporter reads). All of docs/reports/ is gitignored.

WHAT THE PDF CONTAINS
  Shared chrome for every KPI: a header, the Excel definition/how-measured/formula/
  interpretation, and a Result banner (the headline value + unit + direction, with the
  matched interpretation band when it can be derived unambiguously). Then either:
    - the generic body: a "KPI data" table (each datapoint -> its value) + the formula,
      and the raw payloads as an "Underlying data" appendix for verification; OR
    - a KPI's own richer body, if that KPI defines a report_sections() hook (below).

HOW THIS FEATURE IS WIRED (for maintainers)
  - _toolkit.py : every KPI run (run_kpi) writes the JSON envelope to docs/reports/_data/
    and, when --pdf is passed, calls export() here automatically.
  - export_pdf.py (this file) : reads an envelope and renders HTML -> PDF. export() is the
    reusable entry point (used by the CLI here and by _toolkit's auto-export).

ADDING A RICHER TABLE FOR ANOTHER KPI  (optional)
  Define, in that KPI's module, a function:
       def report_sections(envelope) -> list[tuple[str, str]]:  # [(title, html), ...]
  Read the per-(developer/row) data from envelope["datapoints"][0]["raw"] and return
  pre-rendered HTML fragments (see kpi_39 / kpi_54 for a template; reuse the module's
  own _band/formatting helpers so console and PDF agree). Without this hook, the KPI
  still exports fine via the generic layout above.
============================================================================
"""
from __future__ import annotations

import datetime
import html
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPORTS_DIR = HERE / "docs" / "reports"
RUN_DATA_DIR = REPORTS_DIR / "_data"
MAX_ROWS = 200          # cap rows for any one auto-rendered table (huge user-day dumps)
MAX_DEPTH = 6           # recursion guard for pathological nesting

# Headless Edge on Windows -> print HTML to PDF (no extra Python deps needed).
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


# ---------------------------------------------------------------------------
# Loading the run envelope
# ---------------------------------------------------------------------------
def load_envelope(arg: str) -> dict:
    """`arg` is either a path to an envelope .json or a KPI module stem. For a module
    stem (with or without .py) we pick the LATEST artifact in docs/reports/_data/."""
    p = Path(arg)
    if p.suffix == ".json" and p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    stem = arg[:-3] if arg.endswith(".py") else arg
    latest = find_latest_artifact(stem)
    if latest is None:
        raise SystemExit(
            f"No run data found for {stem!r} in {RUN_DATA_DIR}.\n"
            f"Run the KPI first, e.g.  python {stem}.py --start 2026-05-15 --end 2026-05-30")
    return json.loads(latest.read_text(encoding="utf-8"))


def find_latest_artifact(stem: str) -> Path | None:
    """Newest envelope for a KPI module stem. Filenames embed a sortable timestamp
    ({module}__{slug}__{YYYYMMDD-HHMMSS}.json), so the max by name is the latest."""
    matches = sorted(RUN_DATA_DIR.glob(f"{stem}__*.json"))
    return matches[-1] if matches else None


# ---------------------------------------------------------------------------
# Generic JSON -> HTML
# ---------------------------------------------------------------------------
def esc(v) -> str:
    return html.escape(str(v))


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _fmt_scalar(v) -> str:
    if v is None:
        return "<span class='null'>&mdash;</span>"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        if v.is_integer():
            return f"{int(v):,}"
        return f"{v:,.4f}".rstrip("0").rstrip(".")
    return esc(v)


def _is_flat_dict(d) -> bool:
    return isinstance(d, dict) and not any(isinstance(x, (dict, list)) for x in d.values())


def _render_table(rows: list[dict]) -> str:
    """An array of flat dicts -> a table. Columns = ordered union of keys (first-seen).
    Numeric columns are right-aligned. Capped at MAX_ROWS with a truncation footer."""
    cols: list[str] = []
    for r in rows:
        for k in r.keys():
            if k not in cols:
                cols.append(k)
    numeric = {c: all(_is_number(r[c]) for r in rows if c in r and r[c] is not None)
               for c in cols}
    missing = "<span class='null'>&mdash;</span>"
    head = "".join(f"<th class='{'num' if numeric[c] else ''}'>{esc(c)}</th>" for c in cols)
    shown = rows[:MAX_ROWS]
    body_rows = []
    for r in shown:
        cells = []
        for c in cols:
            cls = "num" if numeric[c] else ""
            val = _fmt_scalar(r[c]) if c in r else missing
            cells.append(f"<td class='{cls}'>{val}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    foot = ""
    if len(rows) > MAX_ROWS:
        foot = (f"<tfoot><tr><td colspan='{len(cols)}'>&hellip; "
                f"{len(rows) - MAX_ROWS} more row(s) (truncated)</td></tr></tfoot>")
    return (f"<table class='grid'><thead><tr>{head}</tr></thead>"
            f"<tbody>{''.join(body_rows)}</tbody>{foot}</table>")


def render_value(v, depth: int = 0) -> str:
    """Recursive JSON -> HTML: scalars inline, arrays of flat dicts as tables, scalar
    arrays comma-joined, dicts as key/value tables (recurses, so nested objects nest)."""
    if depth > MAX_DEPTH:
        return f"<pre>{esc(json.dumps(v, default=str))}</pre>"
    if v is None or isinstance(v, (str, int, float, bool)):
        return _fmt_scalar(v)
    if isinstance(v, list):
        if not v:
            return "<em>(empty)</em>"
        if all(_is_flat_dict(x) for x in v):
            return _render_table(v)
        if all(not isinstance(x, (dict, list)) for x in v):
            return ", ".join(_fmt_scalar(x) for x in v)
        return "".join(
            f"<div class='item'><div class='ik'>[{i}]</div>{render_value(x, depth + 1)}</div>"
            for i, x in enumerate(v))
    if isinstance(v, dict):
        rows = "".join(
            f"<tr><td class='k'>{esc(k)}</td><td class='v'>{render_value(val, depth + 1)}</td></tr>"
            for k, val in v.items())
        return f"<table class='kv'>{rows}</table>"
    return esc(v)


# ---------------------------------------------------------------------------
# Interpretation band matching (CONSERVATIVE - abstains rather than guess wrong)
# ---------------------------------------------------------------------------
# Map a numeric result to its interpretation band by parsing the KPI's free-text
# `interpretation` (e.g. "<20%=Poor; 20-30%=Developing; >40%=Excellent"). We only
# return a band when the whole string parses into clean numeric intervals AND the
# value lands in one; otherwise we return None and the PDF just shows the guidance
# text verbatim. We deliberately ABSTAIN on time/frequency units (days, hours,
# per-week/month) where a bare-number compare would be meaningless.
_UNIT_ABSTAIN = ("day", "hour", "week", "month")


def _band_intervals(text: str):
    """Parse 'cond=Label; cond=Label; ...' into [(lo, hi, label), ...] or None.
    cond is one of <N, >N, N+, A-B, or a bare anchor N (anchors are read as
    ascending lower bounds). Returns None if anything is ambiguous/unparseable."""
    low = text.lower()
    if any(u in low for u in _UNIT_ABSTAIN):
        return None
    clauses = [c.strip() for c in text.split(";") if c.strip()]
    if not clauses:
        return None
    parsed, anchors = [], []
    for c in clauses:
        if "=" not in c:
            return None
        cond, label = c.split("=", 1)
        label = re.split(r"\s+-\s+", label.strip())[0].strip()      # drop " - description"
        # keep only digits, separators and the comparison markers
        cond = cond.replace(",", "").replace("%", "")
        cond = re.sub(r"[A-Za-z/ ]+", "", cond).strip()
        try:
            if cond.startswith("<"):
                parsed.append((float("-inf"), float(cond[1:]), label, "<"))
            elif cond.startswith(">"):
                parsed.append((float(cond[1:]), float("inf"), label, ">"))
            elif cond.endswith("+"):
                parsed.append((float(cond[:-1]), float("inf"), label, "+"))
            elif "-" in cond[1:]:                                    # range A-B (not a sign)
                a, b = cond.split("-", 1)
                parsed.append((float(a), float(b), label, "range"))
            else:
                anchors.append((float(cond), label))
                parsed.append(None)
        except ValueError:
            return None
    # Anchor mode: every clause was a bare number -> ascending lower bounds.
    if anchors and all(p is None for p in parsed):
        anchors.sort()
        out = []
        for i, (lo, lbl) in enumerate(anchors):
            hi = anchors[i + 1][0] if i + 1 < len(anchors) else float("inf")
            out.append((lo, hi, lbl, "anchor"))
        return out
    if any(p is None for p in parsed):                              # mixed anchors + ranges
        return None
    return parsed


def _interpretation_band(text, value) -> str | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not text:
        return None
    intervals = _band_intervals(text)
    if not intervals:
        return None
    v = float(value)
    for lo, hi, label, kind in intervals:
        if kind == "<" and v < hi:
            return label
        if kind in (">",) and v > lo:
            return label
        if kind in ("+", "anchor") and lo <= v < hi:
            return label
        if kind == "range" and lo <= v <= hi:
            return label
    return None


# ---------------------------------------------------------------------------
# Report sections (shared chrome + body)
# ---------------------------------------------------------------------------
def build_header(kpi: dict, env: dict) -> str:
    meta = " &middot; ".join(filter(None, [
        f"{esc(kpi.get('index'))} index" if kpi.get("index") else None,
        f"Unit: {esc(kpi.get('unit'))}" if kpi.get("unit") else None,
        f"Cadence: {esc(kpi.get('cadence'))}" if kpi.get("cadence") else None,
        f"Direction: {esc(kpi.get('direction'))}" if kpi.get("direction") else None,
        f"Source: {esc(kpi.get('tools'))}" if kpi.get("tools") else None,
        f"Generated {esc(env.get('generatedAt'))}" if env.get("generatedAt") else None,
    ]))
    proj = f"<div class='meta'>Project: {esc(env.get('project'))}</div>" if env.get("project") else ""
    return (f"<h1>KPI #{esc(kpi.get('num'))} &mdash; {esc(kpi.get('name'))}</h1>"
            f"<div class='meta'>{meta}</div>{proj}")


def build_definition(kpi: dict) -> str:
    bits = [f"{esc(kpi.get('definition'))}"]
    if kpi.get("how_measured"):
        bits.append(f"<b>How measured:</b> {esc(kpi.get('how_measured'))}")
    if kpi.get("formula"):
        bits.append(f"<b>Formula:</b> {esc(kpi.get('formula'))}")
    if kpi.get("interpretation"):
        bits.append(f"<b>Interpretation:</b> {esc(kpi.get('interpretation'))}")
    return "<h2>Definition</h2><div class='def'>" + "<br><br>".join(bits) + "</div>"


def build_result(env: dict) -> str:
    kpi = env.get("kpi", {})
    if env.get("perSprintOnly"):
        return ("<h2>Result</h2><div class='result'>Per-sprint KPI &mdash; reported "
                "sprint-wise. There is no single cross-sprint aggregate by design.</div>")
    if env.get("computable") and env.get("result") is not None:
        value = env.get("result")
        band = _interpretation_band(kpi.get("interpretation"), value)
        band_html = f" &mdash; <b>{esc(band)}</b>" if band else ""
        direction = f" &middot; {esc(kpi.get('direction'))}" if kpi.get("direction") else ""
        return (f"<h2>Result</h2><div class='result'>{esc(kpi.get('name'))} = "
                f"{_fmt_scalar(value)} {esc(kpi.get('unit', ''))}{band_html}"
                f"<span class='rmeta'>{direction}</span></div>")
    return "<h2>Result</h2><div class='result warn'>NOT COMPUTABLE &mdash; an input did not resolve.</div>"


def build_body(env: dict) -> str:
    """Prefer a KPI's own `report_sections(envelope)` hook (richer interpretation
    tables). Otherwise build a MEANINGFUL generic body: a compact 'Formula inputs'
    table (each datapoint -> its value) and the formula, then the underlying raw
    payloads as a clearly-secondary 'Underlying data' section for verification."""
    hook = _hook_sections(env)
    if hook:
        heading, sections = hook
        head_html = f"<h2>{esc(heading)}</h2>" if heading else ""
        return head_html + "".join(
            (f"<h3>{esc(title)}</h3>" if title else "") + frag for title, frag in sections)

    kpi = env.get("kpi", {})
    dps = env.get("datapoints", [])

    # 1) The meaningful data: the inputs the formula consumes, one row per datapoint.
    rows = []
    for dp in dps:
        if dp.get("ok") and dp.get("value") is not None:
            val = _fmt_scalar(dp.get("value"))
        else:
            val = f"<span class='null'>{esc(dp.get('error') or 'no data')}</span>"
        rows.append(f"<tr><td>{esc(dp.get('label'))}</td><td class='num'>{val}</td></tr>")
    inputs = (
        "<h2>KPI data</h2>"
        "<table class='grid'><thead><tr><th>Input</th>"
        "<th class='num'>Value</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>")
    if kpi.get("formula"):
        applied = ""
        nums = [dp.get("value") for dp in dps if dp.get("ok") and dp.get("value") is not None]
        if env.get("computable") and env.get("result") is not None and nums:
            applied = (f" &rarr; {' , '.join(_fmt_scalar(n) for n in nums)} = "
                       f"<b>{_fmt_scalar(env.get('result'))} {esc(kpi.get('unit', ''))}</b>")
        inputs += f"<p class='formula'><b>Formula:</b> {esc(kpi.get('formula'))}{applied}</p>"

    # 2) Verification detail: the raw payloads, demoted below the meaningful summary.
    detail = ["<h2>Underlying data (for verification)</h2>"]
    for dp in dps:
        detail.append(f"<h3>{esc(dp.get('label'))}</h3>")
        if dp.get("source"):
            detail.append(f"<div class='meta'>{esc(dp.get('source'))}</div>")
        if dp.get("raw") is not None:
            detail.append(render_value(dp.get("raw")))
        elif not dp.get("ok"):
            detail.append(f"<div class='result warn'>{esc(dp.get('error') or 'no data')}</div>")
    return inputs + "".join(detail)


def _hook_sections(env: dict):
    """Call the KPI module's optional `report_sections(envelope)` hook, if defined.
    The hook may return either:
      - a list of (title, html)            -> rendered under an "<h2>Per-sprint breakdown</h2>"
      - a dict {"heading": str|None,        -> rendered under "<h2>{heading}</h2>" (or no
                "sections": [(title, html)]}    heading at all when heading is falsy)
    Normalised here to (heading, sections) or None. Import failures fall back to generic."""
    module = env.get("module")
    if not module:
        return None
    try:
        mod = importlib.import_module(module)
        hook = getattr(mod, "report_sections", None)
        if callable(hook):
            ret = hook(env)
            if not ret:
                return None
            if isinstance(ret, dict):
                return (ret.get("heading", "Per-sprint breakdown"), ret.get("sections") or [])
            return ("Per-sprint breakdown", ret)            # legacy list form
    except Exception as e:                       # noqa: BLE001 -- generic body is the fallback
        print(f"(report_sections hook unavailable: {e}; using generic render)", file=sys.stderr)
    return None


CSS = """
  @page { size: A4; margin: 16mm 14mm; }
  * { box-sizing: border-box; }
  body { font: 12px/1.5 -apple-system, Segoe UI, Roboto, Arial, sans-serif; color: #1a1a1a; }
  h1 { font-size: 20px; margin: 0 0 2px; }
  h2 { font-size: 14px; margin: 22px 0 8px; border-bottom: 2px solid #2563eb;
       padding-bottom: 4px; color: #1e3a8a; }
  h3 { font-size: 13px; margin: 16px 0 6px; color:#1e3a8a; }
  .meta { color: #666; font-size: 11px; margin-bottom: 4px; }
  table { border-collapse: collapse; width: 100%; margin: 4px 0 10px; }
  .grid th, .grid td { border: 1px solid #d7dbe0; padding: 4px 8px; }
  .grid th { background:#f1f5f9; text-align:left; font-weight:600; }
  .grid tbody tr:nth-child(even) { background:#fafbfc; }
  .grid tfoot td { border-top: 2px solid #94a3b8; background:#f8fafc; color:#666; }
  .num { text-align: right; font-variant-numeric: tabular-nums; }
  .kv td { padding: 3px 8px; border:1px solid #eef0f3; vertical-align: top; }
  .kv .k { color:#555; width: 230px; }
  .kv .v { font-weight:500; }
  .item { margin: 4px 0 4px 10px; }
  .item .ik { color:#888; font-size:10px; }
  .null { color:#aaa; }
  .def { background:#f8fafc; border:1px solid #e5e7eb; border-radius:6px;
         padding:10px 12px; font-size:11px; color:#333; }
  .result { background:#1e3a8a; color:#fff; font-weight:600; padding:8px 12px;
            border-radius:6px; font-size:13px; }
  .result .rmeta { font-weight:400; opacity:0.8; font-size:11px; }
  .result.warn { background:#b91c1c; }
  .formula { font-size:11px; color:#333; background:#f8fafc; border:1px solid #e5e7eb;
             border-radius:6px; padding:8px 12px; }
  .tag { font-size:10px; padding:1px 7px; border-radius:10px; font-weight:600;
         text-transform:uppercase; }
  .tag-active { background:#dcfce7; color:#166534; }
  .tag-closed { background:#e0e7ff; color:#3730a3; }
  .tag-future { background:#fef3c7; color:#92400e; }
  .foot { margin-top:18px; color:#888; font-size:10px;
          border-top:1px solid #e5e7eb; padding-top:6px; }
"""


def render_html(env: dict) -> str:
    kpi = env.get("kpi", {})
    foot = (f"Generated from run data {esc(env.get('generatedAt'))} &middot; "
            f"module {esc(env.get('module'))} &middot; rendered by export_pdf.py")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>KPI #{esc(kpi.get('num'))} &mdash; {esc(kpi.get('name'))}</title>
<style>{CSS}</style></head><body>
{build_header(kpi, env)}
{build_definition(kpi)}
{build_result(env)}
{build_body(env)}
<div class="foot">{foot}</div>
</body></html>"""


# ---------------------------------------------------------------------------
# Output paths + PDF
# ---------------------------------------------------------------------------
def _window_slug(env: dict) -> str:
    """A filename-safe window tag: sprint name(s) if the run was per-sprint, else the
    window-selecting CLI flags from the recorded argv, else 'run'."""
    names: list[str] = []
    for dp in env.get("datapoints", []):
        raw = dp.get("raw")
        if isinstance(raw, dict):
            for sp in raw.get("perSprint", []) or []:
                if sp.get("name"):
                    names.append(str(sp["name"]))
    if not names:
        argv = env.get("argv", []) or []
        for flag in ("--sprint", "--name", "--start", "--end", "--day", "--source"):
            for i, a in enumerate(argv):
                if a == flag and i + 1 < len(argv):
                    names.append(str(argv[i + 1]))
                elif isinstance(a, str) and a.startswith(flag + "="):
                    names.append(a.split("=", 1)[1])
    raw = "_".join(names) if names else "run"
    return (re.sub(r"[^A-Za-z0-9]+", "_", raw).strip("_") or "run")[:80]


def _unique(path: Path) -> Path:
    """Never clobber: if `path` exists, append _2, _3, ... before the suffix."""
    if not path.exists():
        return path
    n = 2
    while True:
        cand = path.with_name(f"{path.stem}_{n}{path.suffix}")
        if not cand.exists():
            return cand
        n += 1


def _out_paths(env: dict) -> tuple[Path, Path]:
    module = env.get("module") or "kpi"
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    base = f"report_{module}__{_window_slug(env)}__{ts}"
    return (_unique(REPORTS_DIR / f"{base}.html"), _unique(REPORTS_DIR / f"{base}.pdf"))


def _print_pdf(html_path: Path, pdf_path: Path) -> bool:
    edge = next((p for p in EDGE_CANDIDATES if Path(p).exists()), None)
    if not edge:
        print(f"Microsoft Edge not found; HTML written to {html_path} (PDF skipped).",
              file=sys.stderr)
        return False
    subprocess.run(
        [edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", html_path.as_uri()],
        check=True, capture_output=True)
    return True


def export(arg: str) -> tuple[Path, Path | None]:
    """Render one run's envelope (a .json path or a KPI module stem) to HTML + PDF.
    Returns (html_path, pdf_path|None). Reusable both from the CLI and from a KPI run's
    auto-export (_toolkit, on `--pdf`). Each call writes its own timestamped files."""
    env = load_envelope(arg)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    html_path, pdf_path = _out_paths(env)
    html_path.write_text(render_html(env), encoding="utf-8")
    print(f"HTML: {html_path}")
    if _print_pdf(html_path, pdf_path):
        print(f"PDF : {pdf_path}")
        return html_path, pdf_path
    return html_path, None


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        raise SystemExit(
            "Usage: python export_pdf.py <kpi_module_stem | path-to-envelope.json>\n"
            "e.g.   python export_pdf.py kpi_39_net_ai_contributed_loc_per_developer_per_sprint")
    export(args[0])


if __name__ == "__main__":
    main()
