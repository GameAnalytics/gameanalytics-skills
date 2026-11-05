# Changelog

## 0.1.0

First release.

- `gameanalytics-tracking-plan`: genre and KPI tracking plans, checked against GameAnalytics ID formats and daily limits by `check_plan.py`.
- `gameanalytics-sdk-setup`: SDK integration from the live docs, configure before initialise, a typed wrapper per plan, first event in Realtime.
- `gameanalytics-getting-started`: connection, data availability, games, a health snapshot and five next questions.
- `gameanalytics-data-check`: verdicts on data from a new build or game.
- `gameanalytics-weekly-report`: a fixed-structure weekly KPI report with movers and trend anomalies from `weekly_stats.py`, saved with a JSON sidecar.
- The plugin connects the GameAnalytics MCP server and the GameAnalytics Documentation MCP.
