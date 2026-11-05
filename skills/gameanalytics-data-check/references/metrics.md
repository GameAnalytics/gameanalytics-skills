# Metrics: what to call and how to read it

Definitions follow the [GameAnalytics metrics reference](https://docs.gameanalytics.com/events-metrics-and-filtering/metrics). All days are UTC.

## KPI to call

| KPI | Call | Read field | Notes |
|---|---|---|---|
| DAU | `query_metric` `user_unique`, `granularity: "day"` | `user_unique` | Unique users per day |
| WAU | `query_metric` `user_unique`, `granularity: "week"` | `user_unique` | Unique users per ISO week (Monday start). Not the sum of DAU |
| New users | `query_metric` `new_users` | `new_users` | Users seen for the first time |
| D1, D7 retention | `query_retention` `retention_ahead`, `days_ahead: 1` or `7` | `retention` | A fraction per install day (0.21 = 21%). Same as the GameAnalytics UI |
| IAP revenue | `query_metric` `revenue` | `sum` | USD. `sum_cents` is the same amount in cents |
| Ad revenue | `query_metric` `ilrd_revenue` | `sum` | USD, impression-level ad revenue. Separate from IAP revenue |
| ARPDAU | `query_metric` `arpu`, `granularity: "day"` | `arpu` | IAP revenue per daily active user, USD. `total_revenue` in the same row is in cents |
| ARPPU | `query_metric` `arppu` | `arppu` | IAP revenue per paying user in the period, USD |
| Paying users | `query_metric` `paying_users` | `paying_users` | Users who purchased in the period |
| Conversion | `paying_users / user_unique` over the same days and granularity | | Do not call `conversion` (see the connection reference) |
| Sessions | `query_metric` `session_unique` | `session_unique` | |
| Sessions per user | `query_metric` `sessions_per_user` | `sessions_per_user` | Also returns `session_unique` and `user_unique` |
| Session length | `query_metric` `session_length` | `mean` | Seconds per session. `sum` is total seconds |
| Events received | `query_metric` `event_count` | | All event types together. No breakdown by event ID |
| Ad impressions | `query_metric` `ad_impressions_count` | | Needs ad events |

Call `get_supported_metrics` when a question needs a metric not listed here.

## Response shapes

- `timeseries`: `{"result": [{"timestamp": "2026-10-26T00:00:00.000Z", "result": {"user_unique": 1234}}]}`, one row per period.
- `group`: `{"result": [{"timestamp": ..., "result": [{"country_code": "US", "user_unique": 400}, ...]}]}`.
- A period with no data comes back as `0`, not as an error. Zero can mean "nothing happened" or "nothing was sent". Say which you cannot tell apart.

## Periods

- **Complete days only.** The latest day in `get_interval` is still filling. The last complete day is the day before the date part of the interval's end, unless the end is exactly midnight.
- **Equal lengths.** Compare 7 days with 7 days, a week with a week. Never compare a partial month with a full one.
- **31 days per `day` request.** Chunk longer ranges.
- **Retention matures late.** A D1 value exists only for install days at least 1 complete day before the last complete day; D7 needs 7. So the D7 window for "last week" is the 7 install days ending 7 days before the last complete day. Always print the install-day window next to a retention number.
- **Weighting.** To combine daily rates into one number for a period, weight them: ARPDAU over a week is total revenue divided by the sum of daily DAU; retention over a cohort window is weighted by `new_users` per install day. Never average daily percentages without weights.

## What this data cannot answer

The Metrics API behind the GameAnalytics MCP has no event IDs. It cannot show:

- Design events or progression events by name, for example whether `Level_5_Complete` is arriving.
- Resource events (sources and sinks) by currency or item.
- Custom dimensions 01, 02, 03 and custom event fields.

Point to where the user can see them instead:

- **Realtime > Live Events** in GameAnalytics shows the last 50 events, filterable by event type, build and user ID. New events appear within about 30 seconds.
- **Explore**, **Funnels** and **Engagement** in AnalyticsIQ, for design and progression analysis.
- **Data Warehouse** and **Data Export** in PipelineIQ keep full event payloads, including custom fields.

Design and progression events are available in AnalyticsIQ for 3 months ([data retention](https://docs.gameanalytics.com/event-tracking-and-integrations/data-retention-and-limits/data-retention-practices)).
