#!/usr/bin/env python3
"""
KPI viewer server -- a tiny LOCAL runner behind the HTML generator (index.html).

WHY A SERVER? A browser cannot safely call GitHub / Jira / Anthropic with your
tokens (CORS blocks Jira/Anthropic, and tokens must never sit in a static page).
This stdlib server reuses the SAME verified kpi_*.py scripts -- their fetch() and
extract() -- and returns, per datapoint, the request, the COMPLETE raw JSON, the
extracted value, and the JSON path(s) used. index.html renders + highlights that.

The console scripts are UNCHANGED: `python kpi_NN_*.py` still prints the trace.
This server is an additional, optional way to view the same thing in a browser.

Run:  python server.py            # opens http://localhost:8000
      python server.py 8090       # custom port
"""
from __future__ import annotations

import asyncio
import importlib
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


def kpi_modules() -> list[str]:
    return sorted(p.stem for p in HERE.glob("kpi_*.py"))


def get_module(modname: str, reload: bool = False):
    mod = importlib.import_module(modname)
    return importlib.reload(mod) if reload else mod


def list_kpis() -> list[dict]:
    out = []
    for modname in kpi_modules():
        try:
            k = get_module(modname).KPI
        except Exception:
            continue
        out.append({
            "id": modname, "num": k.get("num"), "name": k.get("name"),
            "index": k.get("index"), "formula": k.get("formula"), "unit": k.get("unit"),
            "tools": k.get("tools"), "definition": k.get("definition"), "plain": k.get("plain"),
            "how_measured": k.get("how_measured"), "interpretation": k.get("interpretation"),
            "cadence": k.get("cadence"), "direction": k.get("direction"),
        })
    out.sort(key=lambda x: (x["num"] is None, x["num"]))
    return out


def project_name() -> str | None:
    try:
        from _toolkit import project_name as pn
        return pn()
    except Exception:
        return None


async def _run(mod) -> dict:
    KPI, DPS, compute = mod.KPI, mod.DATAPOINTS, mod.compute
    dps, values = [], []
    async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
        client._kpi_log = []   # the toolkit transport appends every real API exchange here
        for dp in DPS:
            entry = {
                "label": dp.label, "description": getattr(dp, "description", ""),
                "example": getattr(dp, "example", ""), "source": dp.source,
                "plain": getattr(dp, "plain", ""),
                "paths": list(getattr(dp, "paths", []) or []),
                "steps": list(getattr(dp, "steps", []) or []),
                "availability": getattr(dp, "availability", "live"),
            }
            if entry["availability"] != "live" or not dp.fetch or not dp.extract:
                entry.update(ok=False, value=None, status=None, request=None, raw=None,
                             api_calls=[],
                             error=getattr(dp, "reason", None) or "not a live datapoint")
                dps.append(entry); values.append(None); continue
            mark = len(client._kpi_log)   # every exchange after this belongs to THIS datapoint
            try:
                call = await dp.fetch(client)
                val = dp.extract(call.raw) if call.ok else None
                entry.update(
                    ok=bool(call.ok and val is not None), value=val, status=call.status,
                    request={"method": call.method, "url": call.url,
                             "headers": call.headers, "note": call.note},
                    raw=call.raw, error=None if call.ok else f"HTTP {call.status}",
                )
                values.append(val)
            except Exception as e:                      # noqa: BLE001
                entry.update(ok=False, value=None, status=None, request=None, raw=None, error=str(e))
                values.append(None)
            entry["api_calls"] = client._kpi_log[mark:]   # the real upstream responses
            dps.append(entry)
    computable = len(values) > 0 and all(v is not None for v in values)
    result, err = None, None
    if computable:
        try:
            result = compute(*values)
        except Exception as e:                          # noqa: BLE001
            err = str(e)
    return {"kpi": KPI, "datapoints": dps,
            "computable": bool(computable and result is not None),
            "result": result, "error": err}


def run_kpi_json(modname: str) -> dict:
    # reload so per-module caches (e.g. the retention cohort cache) reset each run
    return asyncio.run(_run(get_module(modname, reload=True)))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                return self._send(200, (HERE / "index.html").read_text(encoding="utf-8"), "text/html")
            except FileNotFoundError:
                return self._send(500, json.dumps({"error": "index.html not found"}))
        if self.path == "/api/project":
            return self._send(200, json.dumps({"project": project_name()}))
        if self.path == "/api/kpis":
            return self._send(200, json.dumps(list_kpis()))
        return self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path.startswith("/api/run/"):
            modname = self.path[len("/api/run/"):]
            if modname not in kpi_modules():
                return self._send(404, json.dumps({"error": f"unknown kpi {modname}"}))
            try:
                return self._send(200, json.dumps(run_kpi_json(modname), default=str))
            except Exception as e:                       # noqa: BLE001
                return self._send(500, json.dumps({"error": str(e)}))
        return self._send(404, json.dumps({"error": "not found"}))

    def log_message(self, *a):                           # keep the console quiet
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"KPI viewer running at {url}   (Ctrl+C to stop)")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
