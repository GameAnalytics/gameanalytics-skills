# Script input and the anomaly method

## Input for `weekly_stats.py`

One JSON file. Every series accepts any of these forms, so tool results can be saved with as little reshaping as possible:

- a map of date to value: `{"2026-10-26": 1234, "2026-10-27": 1250}` (the most compact; prefer it)
- rows: `[{"date": "2026-10-26", "value": 1234}]`
- the tool result as returned, or a list of them for chunked ranges. All three shapes in the metrics reference are read: the single-game `visualisation` items, `result` rows and `event` rows.

```json
{
  "game": {"id": "12345", "name": "Galaxy Quest"},
  "week_start": "2026-10-26",
  "daily": {
    "user_unique": {"2026-08-31": 980},
    "new_users": {},
    "revenue": {},
    "ilrd_revenue": {},
    "paying_users": {},
    "session_unique": {},
    "session_length": {}
  },
  "weekly": {
    "wau": {"2026-09-07": 5400},
    "arppu": {}
  },
  "retention": {
    "d1": {"2026-09-06": 0.31},
    "d7": {}
  },
  "breakdowns": {
    "country_code": {
      "user_unique": {"this": {"US": 4100, "DE": 900}, "prev": {"US": 3500, "DE": 950}},
      "new_users": {},
      "revenue": {}
    },
    "platform": {}
  }
}
```

- `week_start` is the report week's Monday.
- Daily values are the read fields in the metrics reference: `sum` for `revenue` and `ilrd_revenue`, `mean` for `session_length` (seconds), the metric's own name otherwise.
- Retention is keyed by install day, as a fraction (`0.31`). Percentages are detected and converted.
- Weekly series are keyed by the week's Monday.
- Breakdowns are `{"this": {...}, "prev": {...}}` maps of dimension value to weekly total, or the raw `group` result with two weekly rows.
- Missing days make that week's value `n/a`. They are never filled.

## Weekly values

For each of the 8 weeks (the report week and the 7 before it):

| KPI | Value |
|---|---|
| DAU | mean of the 7 daily `user_unique` |
| New users, IAP revenue, ad revenue | sum of the 7 days |
| ARPDAU | IAP revenue / sum of daily DAU |
| Conversion | sum of daily paying users / sum of daily DAU |
| Sessions per user | sum of daily sessions / sum of daily DAU |
| Session length | sum of (daily mean length x daily sessions) / sum of daily sessions |
| D1 retention | for install days `Monday - 1` to `Sunday - 1`: sum(rate x new users) / sum(new users) |
| D7 retention | the same, for install days `Monday - 7` to `Sunday - 7` |
| WAU, ARPPU | the weekly value as returned |

## Change

- Counts, money and ratios: `(this - last) / last`, as a percentage.
- Retention and conversion: `this - last`, in percentage points.

## Anomaly

For each KPI:

1. Take the 7 prior weekly values (at least 4 must exist) and fit a straight line `y = a + b*x`, with `x = 0..6`.
2. Expected value: `a + b*7`. Residual standard deviation: `sqrt(sum of squared residuals / (n - 2))`.
3. `z = (this week - expected) / sd`, and deviation `= (this week - expected) / |expected|`.
4. Flag when `|z| >= 2` and `|deviation| >= 10%`, or `|z| >= 4` and `|deviation| >= 3%`.
5. Fallback when there are fewer than 4 prior weeks, or the deviation is 0: flag only a week-on-week change of 20% or more.
6. Never flag a KPI under its volume floor (see the guardrails). The report week's floor basis is: DAU for user metrics and ad revenue, paying users a day for money metrics, and new users a day in the cohort window for retention.
7. When last week's sidecar flagged the same KPI in the same direction, mark it as a repeat.

## Movers

For each breakdown (country, platform) and metric (active users, new users, IAP revenue):

1. Game-wide change: `g = (total this - total last) / total last`.
2. Drop a slice under 2% of the total in both weeks. For counts, also drop a slice under 100 in both weeks.
3. Drop a slice whose own change is within 5 percentage points of `g`: it only echoes the game-wide move.
4. For each remaining slice: `vs trend = this - last x (1 + g)`.
5. List the 3 largest positive and the 3 largest negative `vs trend` values.
