---
name: gameanalytics-weekly-report
description: Writes a fixed-structure weekly KPI report for one GameAnalytics game from the GameAnalytics MCP (WAU, DAU, new users, D1 and D7 retention, revenue, ARPDAU, ARPPU, conversion, sessions), with week-on-week changes, top movers by country and platform, anomalies flagged against an 8-week trend, and questions worth asking next, saved as a dated markdown file. Use when someone asks for a weekly report, a week-on-week KPI summary, or how their game did last week.
---

# GameAnalytics: weekly report

One report per game per ISO week, always in the same structure, so weeks can be compared side by side. The skill reads data and writes two files: the report and a JSON sidecar.

Read before the first call:
- [references/mcp-connection.md](references/mcp-connection.md): servers, the connection probe, calling conventions, calls to avoid
- [references/metrics.md](references/metrics.md): which call answers which KPI, units, periods
- [references/analysis-guardrails.md](references/analysis-guardrails.md): volume floors, arithmetic, language
- [references/report-template.md](references/report-template.md): the exact report structure
- [references/anomaly-method.md](references/anomaly-method.md): the input format for the script, and the formulas

## Step 1: Game and week

1. Run the connection probe (`get_interval`). Stop on anything but an interval.
2. Resolve the game with `get_games`. One game per report; for several games, write one report each.
3. The report week is the last complete ISO week, Monday to Sunday UTC, unless the user names another. Let `W` be its Monday. The week is complete only if the interval end is on or after `W + 7` (the next Monday). Otherwise use the week before and say why.

## Step 2: Fetch

All calls use the game's ID. Day ranges are inclusive and stay within 31 days per request.

| Data | Call | Ranges |
|---|---|---|
| `user_unique`, `revenue`, `ilrd_revenue`, `paying_users`, `session_unique`, `session_length` | `query_metric`, `granularity: "day"` | `W-49` to `W-22`, and `W-21` to `W+6` |
| `new_users` | `query_metric`, `granularity: "day"` | `W-56` to `W-36`, `W-35` to `W-15`, and `W-14` to `W+6` |
| D1 retention | `query_retention`, `retention_ahead`, `days_ahead: 1` | `W-50` to `W-23`, and `W-22` to `W+5` |
| D7 retention | `query_retention`, `retention_ahead`, `days_ahead: 7` | `W-56` to `W-29`, and `W-28` to `W-1` |
| WAU (`user_unique`) and `arppu` | `query_metric`, `granularity: "week"` | `W-49` to `W+6` |
| Breakdowns: `user_unique`, `new_users`, `revenue` by `country_code`, and by `platform` | `query_metric`, `granularity: "week"`, `query_type: "group"`, `limit: 250` | `W-7` to `W+6` |

That is 27 calls. Run independent calls in parallel when the client allows it.

## Step 3: Compute

Write the results to a working file in the format given in [references/anomaly-method.md](references/anomaly-method.md), then run:

```bash
python3 <skill dir>/scripts/weekly_stats.py input.json --previous <last week's sidecar> --out <this week's sidecar> --markdown
```

The script prints the KPI table, the movers tables and the anomaly list, and writes the sidecar. Leave out `--previous` when there is no earlier report for the game.

If the client cannot run Python, compute by hand with the formulas in the anomaly method reference, and add a data note saying the numbers were computed without the script.

## Step 4: Write the report

Follow [references/report-template.md](references/report-template.md) exactly: the same sections, in the same order, every week. Use the script's tables as they are. Write the summary, the next questions and the data notes yourself, under the guardrails.

Save the report and the sidecar:

- `gameanalytics-reports/<game-slug>/<YYYY>-W<ww>.md`
- `gameanalytics-reports/<game-slug>/<YYYY>-W<ww>.json`

`<game-slug>` is the game name in lowercase with hyphens. Write relative to the current project folder, or wherever the user keeps reports. Before computing, look for the previous week's sidecar in the same folder and pass it as `--previous`.

Show the full report in the reply too, and give the file path.

## Rules

- Never mix this week's partial day into any number.
- Every flagged anomaly comes from the script's method, or the documented fallback. Do not flag by eye.
- Movers are descriptive. Write "iOS DAU rose 80% against a 40% game-wide rise", never a reason, unless the user gave one.
- If the user wants this every week, explain that it can be scheduled (for example with Claude Code's `/schedule` or a scheduled task in Claude Cowork) and that each run reads the previous sidecar.
