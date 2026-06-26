"""
============================================================================
KPI #08 - AI Code Acceptance Rate - Utilization index   (Source: GitHub Copilot)
============================================================================
VERIFY THIS SCRIPT AGAINST THE EXCEL MASTER SHEET ROW FOR KPI #8.

From the Excel master (5_Index_AI_SDLC_KPI_v4 / KPIs.xlsx), row num=8:
  Definition    : % of AI-generated suggestions (inline completions and
                  generated blocks) that developers accept without
                  modification, measuring suggestion quality and developer
                  trust.
  How measured  : Count accepted suggestions divided by total suggestions
                  shown x 100. Track separately: single-line completions vs
                  multi-line block suggestions.
  Formula       : (Accepted AI suggestions / Total AI suggestions shown) x 100
  Unit          : %        Cadence: Weekly       Direction: higher-better
  Interpretation: <20%=Poor - wrong model or prompt quality issues;
                  20-30%=Developing; 30-35%=Industry average;
                  >40%=Excellent - high model-developer alignment

HOW THIS SCRIPT COMPUTES IT (read top to bottom, then run it):
  Accepted suggestions = total accepted code suggestions across the latest 7-day
                         window, summed across totals_by_feature while excluding
                         agent_edit, plan_mode, and custom_mode.
                         (Defensively filtered out of totals_by_feature,
                         totals_by_language_feature, and totals_by_model_feature).
  Suggestions shown    = total suggestions GENERATED across the same 7-day
                         window, summed across totals_by_feature (used as a proxy
                         for suggestions shown), excluding agent_edit, plan_mode,
                         and custom_mode.
                          NOTE: As per official docs, agent_edit (and edits from
                          custom agents) writes changes directly into files and may not
                          populate suggestion-style fields or user_initiated_interaction_count,
                          so they are excluded. Other agentic modes like plan_mode
                          are also excluded for the same reason.
  Result               = Accepted / Shown * 100.

  Both numbers are extracted from the latest 7 days of the org 28-day report
  returned by the GitHub Copilot API. The script calculates a weekly blended rate,
  presenting a feature-wise checklist breakdown showing included vs excluded categories.

RUN:
  python kpi_08_ai_code_acceptance_rate.py          # trimmed raw payloads
  python kpi_08_ai_code_acceptance_rate.py --raw    # full raw payloads
(Needs tools.github-copilot.githubKey + .org in your .secrets/project.json.)
============================================================================
"""
from _toolkit import Datapoint, cfg, gh_report, run_kpi

# The tool id whose credentials this KPI reads from .secrets/project.json.
TOOL = "github-copilot"

# --- The KPI definition, copied verbatim from the Excel sheet so a developer can
#     diff the printed header against the spreadsheet row. ASCII-only for printing
#     (the Excel "x 100" multiplication sign and the "<20%=Poor -" em dash are
#     rendered with plain ASCII "x" and "-" so the trace prints on any console). --
KPI = {
    "num": 8,
    "name": "AI Code Acceptance Rate",
    "index": "Utilization",
    "definition": "% of AI-generated suggestions (inline completions and generated "
                  "blocks) that developers accept without modification, measuring "
                  "suggestion quality and developer trust.",
    "how_measured": "Count accepted suggestions divided by total suggestions shown "
                    "x 100. Track separately: single-line completions vs multi-line "
                    "block suggestions.",
    "formula": "(Accepted AI suggestions / Total AI suggestions shown) x 100",
    "unit": "%",
    "cadence": "Weekly",
    "direction": "higher-better",
    "interpretation": "<20%=Poor - wrong model or prompt quality issues; "
                      "20-30%=Developing; 30-35%=Industry average; "
                      ">40%=Excellent - high model-developer alignment",
    "tools": "GitHub Copilot",
    "plain": "Out of every AI code suggestion Copilot produced, what share did "
             "developers keep. High = Copilot's suggestions are good enough that "
             "developers trust and accept them; low = they mostly ignore or rewrite "
             "what Copilot suggests.",
    # How the formula combines the datapoint values, step by step. Each step is
    # self-contained so a brand-new developer needs no code to follow it.
    "steps": [
        "Take Accepted suggestions: the total count of AI code suggestions developers "
        "kept, added up over the latest 7-day window (sliced from the 28-day report "
        "returned by the GitHub Copilot org metrics API).",
        "Take Suggestions shown: the total count of AI code suggestions Copilot "
        "generated over the same 7-day window. This is a PROXY (a documented "
        "stand-in) for 'suggestions shown' because the API has no exact 'shown' field.",
        "Divide Accepted suggestions by Suggestions shown. This gives a fraction "
        "between 0 and 1 -- the share of generated suggestions developers accepted.",
        "Multiply that fraction by 100 to turn it into a percentage (e.g. 0.35 -> 35%).",
    ],
}


# ===========================================================================
# SHARED FETCH - the org 28-day metrics report (both datapoints read from it)
# ===========================================================================
# Both the numerator (accepted) and the denominator (shown) live in the SAME
# report, so we fetch it once and let each extractor pull its own field. This
# mirrors the executive Copilot route, which builds suggestionsAccepted and
# suggestionsGenerated from a single fetchReport(...organization-28-day/latest).
async def fetch_org_28day_report(client):
    token = cfg(TOOL, "githubKey")
    org = cfg(TOOL, "org")
    if not token:
        raise RuntimeError("Set tools.github-copilot.githubKey in .secrets/project.json")
    if not org:
        raise RuntimeError("Set tools.github-copilot.org in .secrets/project.json")
    return await gh_report(
        client,
        f"/orgs/{org}/copilot/metrics/reports/organization-28-day/latest",
        token=token,
    )


_LATEST_RAW_REPORT = None

EXCLUDED_FEATURES = {
    "agent_edit",
    "chat_panel_plan_mode",
    "chat_panel_custom_mode"
}


def _get_last_7_days(raw):
    if not isinstance(raw, dict):
        return []
    day_totals = raw.get("day_totals")
    if not isinstance(day_totals, list):
        return []
    valid_days = []
    for d in day_totals:
        if isinstance(d, dict) and isinstance(d.get("day"), str):
            # Defensively exclude the features from all three key breakdowns in the payload:
            # 1. totals_by_feature
            if isinstance(d.get("totals_by_feature"), list):
                d["totals_by_feature"] = [
                    feat for feat in d["totals_by_feature"]
                    if isinstance(feat, dict) and feat.get("feature") not in EXCLUDED_FEATURES
                ]
            # 2. totals_by_language_feature
            if isinstance(d.get("totals_by_language_feature"), list):
                d["totals_by_language_feature"] = [
                    feat for feat in d["totals_by_language_feature"]
                    if isinstance(feat, dict) and feat.get("feature") not in EXCLUDED_FEATURES
                ]
            # 3. totals_by_model_feature
            if isinstance(d.get("totals_by_model_feature"), list):
                d["totals_by_model_feature"] = [
                    feat for feat in d["totals_by_model_feature"]
                    if isinstance(feat, dict) and feat.get("feature") not in EXCLUDED_FEATURES
                ]
            valid_days.append(d)
    # Sort ascending by date string
    valid_days.sort(key=lambda x: x["day"])
    return valid_days[-7:]



# ===========================================================================
# DATAPOINT 1 of 2 - "Accepted suggestions" (the formula's numerator)
# ===========================================================================
async def fetch_accepted_suggestions(client):
    return await fetch_org_28day_report(client)


def extract_accepted_suggestions(raw):
    global _LATEST_RAW_REPORT
    _LATEST_RAW_REPORT = raw
    if not isinstance(raw, dict):
        return None
    last_7 = _get_last_7_days(raw)
    total = 0.0
    seen = False
    for d in last_7:
        totals_by_feature = d.get("totals_by_feature")
        if not isinstance(totals_by_feature, list):
            continue
        for feat in totals_by_feature:
            if isinstance(feat, dict):
                name = feat.get("feature")
                if isinstance(name, str) and name not in EXCLUDED_FEATURES:
                    v = feat.get("code_acceptance_activity_count", 0)
                    if isinstance(v, (int, float)):
                        total += v
                        seen = True
    return total if seen else 0.0


# ===========================================================================
# DATAPOINT 2 of 2 - "Suggestions shown" (the formula's denominator)
# ===========================================================================
async def fetch_shown_suggestions(client):
    return await fetch_org_28day_report(client)


def extract_shown_suggestions(raw):
    if not isinstance(raw, dict):
        return None
    last_7 = _get_last_7_days(raw)
    total = 0.0
    seen = False
    for d in last_7:
        totals_by_feature = d.get("totals_by_feature")
        if not isinstance(totals_by_feature, list):
            continue
        for feat in totals_by_feature:
            if isinstance(feat, dict):
                name = feat.get("feature")
                if isinstance(name, str) and name not in EXCLUDED_FEATURES:
                    v = feat.get("code_generation_activity_count", 0)
                    if isinstance(v, (int, float)):
                        total += v
                        seen = True
    return total if seen else 0.0


# ===========================================================================
# THE FORMULA - (Accepted AI suggestions / Total AI suggestions shown) x 100
# ===========================================================================
# Arguments arrive in the same order as DATAPOINTS below.
def compute(accepted_suggestions, shown_suggestions):
    if accepted_suggestions is None or shown_suggestions is None:
        return None

    if _LATEST_RAW_REPORT:
        last_7 = _get_last_7_days(_LATEST_RAW_REPORT)
        
        feature_sums = {
            "Code Completions": {"suggested": 0, "accepted": 0},
            "Copilot Chat": {"suggested": 0, "accepted": 0},
            "Ask Mode": {"suggested": 0, "accepted": 0},
            "Edit Mode": {"suggested": 0, "accepted": 0},
            "Agent Mode": {"suggested": 0, "accepted": 0},
            "Plan Mode": {"suggested": 0, "accepted": 0},
            "Custom Agents (via Configure Custom Agents)": {"suggested": 0, "accepted": 0},
            "GitHub Copilot CLI": {"suggested": 0, "accepted": 0},
        }
        
        for d in last_7:
            totals_by_feature = d.get("totals_by_feature")
            if not isinstance(totals_by_feature, list):
                continue
            for feat in totals_by_feature:
                if not isinstance(feat, dict):
                    continue
                name = feat.get("feature")
                if not isinstance(name, str):
                    continue
                gen = feat.get("code_generation_activity_count", 0)
                acc = feat.get("code_acceptance_activity_count", 0)
                
                gen_val = gen if isinstance(gen, (int, float)) else 0
                acc_val = acc if isinstance(acc, (int, float)) else 0
                
                if name == "code_completion":
                    category = "Code Completions"
                elif name == "chat_panel_ask_mode":
                    category = "Ask Mode"
                elif name == "agent_edit":
                    category = "Edit Mode"
                elif name == "chat_panel_agent_mode":
                    category = "Agent Mode"
                elif name == "chat_panel_plan_mode":
                    category = "Plan Mode"
                elif name == "chat_panel_custom_mode":
                    category = "Custom Agents (via Configure Custom Agents)"
                elif name == "copilot_cli":
                    category = "GitHub Copilot CLI"
                elif name in ("chat_inline", "chat_panel_unknown_mode") or name.startswith("chat"):
                    category = "Copilot Chat"
                else:
                    category = "Copilot Chat"
                
                feature_sums[category]["suggested"] += gen_val
                feature_sums[category]["accepted"] += acc_val
        
        start_day = last_7[0]["day"] if last_7 else "N/A"
        end_day = last_7[-1]["day"] if last_7 else "N/A"
        
        print("\n" + "=" * 74)
        print(f"Weekly Feature-wise Breakdown ({start_day} to {end_day}):")
        print("-" * 74)
        total_suggested_incl = 0
        total_accepted_incl = 0
        
        excluded_displays = {
            "Edit Mode", "Plan Mode", 
            "Custom Agents (via Configure Custom Agents)"
        }
        
        # Print Included Features first
        for display_name, stats in feature_sums.items():
            if display_name not in excluded_displays:
                s = stats["suggested"]
                a = stats["accepted"]
                total_suggested_incl += s
                total_accepted_incl += a
                rate = (a / s * 100) if s > 0 else 0.0
                print(f"  ✅ {display_name:<45}: Suggested = {s:<4} | Accepted = {a:<4} | Rate = {rate:.4f}%")
        
        # Print Excluded Features second
        for display_name in feature_sums:
            if display_name in excluded_displays:
                print(f"  ❌ {display_name:<45}: [EXCLUDED - Writes directly to files, not in suggestion metrics per official docs]")
        
        overall_rate_incl = (total_accepted_incl / total_suggested_incl * 100) if total_suggested_incl > 0 else 0.0
        print("-" * 74)
        print(f"  📊 Overall (Included Features)                  : Suggested = {total_suggested_incl:<4} | Accepted = {total_accepted_incl:<4} | Rate = {overall_rate_incl:.4f}%")
        print(f"  Formula                                         : (Accepted = {total_accepted_incl} / Suggested = {total_suggested_incl}) * 100 = {overall_rate_incl:.4f}%")
        print("=" * 74 + "\n")

    if not shown_suggestions:        # guard divide-by-zero (no suggestions shown => rate is 0.0%)
        return 0.0
    return accepted_suggestions / shown_suggestions * 100


# The inputs the runner fetches, extracts, and feeds to compute() in this order.
DATAPOINTS = [
    Datapoint(
        label="Accepted suggestions (weekly total)",
        description="The total number of AI code suggestions developers accepted, summed "
                    "across the most recent 7 days. Note: As per official docs, agent_edit (and custom "
                    "agent edits) writes changes directly into files and may not populate standard "
                    "suggestion-style fields (like code_acceptance_activity_count), so they are excluded. "
                    "Other agentic modes like plan_mode are also excluded for the same reason.",
        example="e.g. summing day_totals[].code_acceptance_activity_count (excluding edit/plan/custom mode features) "
                "across the latest 7-day window gave 6, so Accepted = 6.",
        plain="How many AI code suggestions developers kept (accepted) over the last 7 days (excluding edit/plan/custom modes).",
        source="GET /orgs/{org}/copilot/metrics/reports/organization-28-day/latest "
               "-> follow download_links[0] -> gunzip -> "
               "sum(last_7_days(day_totals[].totals_by_feature[].code_acceptance_activity_count (filtered)))",
        paths=[
            "day_totals[].totals_by_feature[].code_acceptance_activity_count",
            "day_totals[].totals_by_language_feature[].code_acceptance_activity_count",
            "day_totals[].totals_by_model_feature[].code_acceptance_activity_count",
        ],
        steps=[
            "Call the GitHub Copilot org 28-day metrics report endpoint.",
            "Decompress and parse the JSON report file.",
            "Sort the day_totals array and take the latest 7 days.",
            "Sum the code_acceptance_activity_count across these 7 days, excluding agent_edit, plan_mode, and custom_mode.",
        ],
        fetch=fetch_accepted_suggestions,
        extract=extract_accepted_suggestions,
    ),
    Datapoint(
        label="Suggestions shown (weekly total; code_generation proxy)",
        description="The total number of AI suggestions generated (used as a proxy for shown), "
                    "summed across the latest 7 days. Note: As per official docs, agent_edit (and custom "
                    "agent edits) do not populate standard suggestion-style fields (like code_generation_activity_count), "
                    "so they are excluded. Other agentic modes like plan_mode are also excluded for the same reason.",
        example="e.g. summing day_totals[].code_generation_activity_count (excluding edit/plan/custom mode features) "
                "across the latest 7-day window gave 93, so Shown = 93.",
        plain="How many AI code suggestions Copilot generated over the last 7 days (excluding edit/plan/custom modes).",
        source="GET /orgs/{org}/copilot/metrics/reports/organization-28-day/latest "
               "-> follow download_links[0] -> gunzip -> "
               "sum(last_7_days(day_totals[].totals_by_feature[].code_generation_activity_count (filtered)))",
        paths=[
            "day_totals[].totals_by_feature[].code_generation_activity_count",
            "day_totals[].totals_by_language_feature[].code_generation_activity_count",
            "day_totals[].totals_by_model_feature[].code_generation_activity_count",
        ],
        steps=[
            "Use the same decompressed and parsed JSON report file.",
            "Sort the day_totals array and take the latest 7 days.",
            "Sum the code_generation_activity_count across these 7 days, excluding agent_edit, plan_mode, and custom_mode.",
        ],
        fetch=fetch_shown_suggestions,
        extract=extract_shown_suggestions,
    ),
]


if __name__ == "__main__":
    run_kpi(KPI, DATAPOINTS, compute)

