# Weekly report template

Every report uses these seven sections, in this order, with these headings. Keep a section and write "None this week." rather than dropping it.

```markdown
# <Game name>: weekly report <YYYY>-W<ww>

<Monday d Mon> to <Sunday d Mon YYYY> (UTC), compared with <previous Monday> to <previous Sunday>. Data processed up to <interval end, UTC>. Generated <generation time, UTC>.

## Summary

<Two or three sentences. The largest movements and the flagged anomalies, as facts with numbers. No causes, no advice.>

## KPIs

<The script's KPI table, unchanged.>

## Top movers

<The script's movers tables for country and platform, unchanged. "None this week." if no slice moved apart from the game-wide trend.>

## Anomalies

<The script's anomaly list, unchanged, then one line: "Method: each KPI's week compared with a linear trend over the previous 7 weeks; flagged when z is 2 or more and the deviation is 10% or more, or z is 4 or more and the deviation is 3% or more. For daily alerts, use Anomaly Detection in AnalyticsIQ.">

## Questions worth asking next

1. <Three to five questions, each tied to a finding above and answerable with the GameAnalytics MCP.>

## Data notes

- <Thin metrics, metrics not available and why, failed calls, a week moved because the latest was incomplete.>
- Design, progression and resource events are not part of this report: the Metrics API does not include them.
```

## Writing the questions

- Tie each to a row: a flagged KPI, a mover, a thin metric.
- Make each one a query the MCP can answer: a metric, a breakdown, a period. For example: "How does D1 retention for installs from 25 to 31 Oct split by platform and country?"
- A KPI flagged two weeks running gets a question about its trend over 8 weeks.
- No questions about design events, progression events or custom dimensions.

## Summary examples

- Good: "DAU averaged 14,020, up 42% on last week and well above its 7-week trend; the rise is concentrated on iOS (+80%). ARPDAU fell 28% to $0.051, so IAP revenue rose only 3%."
- Bad: "The new update drove a big DAU spike but hurt monetization." It states causes the data does not show.
