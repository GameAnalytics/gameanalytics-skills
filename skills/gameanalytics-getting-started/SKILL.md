---
name: gameanalytics-getting-started
description: Connects to GameAnalytics, confirms access and data availability, lists the user's studios and games, and produces a first health snapshot of one game (DAU, new users, D1 and D7 retention, revenue, ARPDAU) for the last 7 complete days against the 7 before, ending with five suggested next questions. Use when someone starts using GameAnalytics through an AI assistant, asks which games they have in GameAnalytics, or asks how their game is doing without naming a specific metric or period.
---

# GameAnalytics: getting started

Take a new user from "is this connected?" to a first, trustworthy read of one game, then hand them five good questions to ask next. The skill only reads data.

Read before the first call:
- [references/mcp-connection.md](references/mcp-connection.md): servers, the connection probe, calling conventions, calls to avoid
- [references/metrics.md](references/metrics.md): which call answers which KPI, units, periods
- [references/analysis-guardrails.md](references/analysis-guardrails.md): volume floors, arithmetic, language

## Step 1: Confirm the connection

Call `get_interval`. Follow the result table in the connection reference. On anything other than an interval, tell the user what it means and how to fix it, and stop.

## Step 2: Data availability

From the interval, report the earliest and latest dates with data. Set:

- `T` = the date part of the interval end (today in UTC, still filling)
- `L` = `T - 1`, the last complete day

Say plainly that `T` is partial and everything below ends at `L`.

## Step 3: Studios and games

1. `get_studios` and `get_games` with `start_date = L - 29`, `end_date = L`.
2. Rank the games: `query_metric` with `metric: "user_unique"`, all game IDs (up to 100), `start_date = L - 6`, `end_date = L`, `granularity: "all"`, `query_type: "group"`, `dimension: "game_id"`. This is unique users over 7 days.
3. Show a table: studio, game, game ID, 7-day active users. Show the top 20 when there are more, and say how many there are in total.
4. Ask which game to look at. If the user already named one, or does not answer, take the game with the most active users and say so.

A game missing from `get_games` had no activity in the last 30 days. If the user expected it, suggest `gameanalytics-data-check`.

## Step 4: Health snapshot

Periods, all inclusive:

| Name | Days |
|---|---|
| Current | `L - 6` to `L` |
| Previous | `L - 13` to `L - 7` |
| D1 current / previous install days | `L - 7` to `L - 1` / `L - 14` to `L - 8` |
| D7 current / previous install days | `L - 13` to `L - 7` / `L - 20` to `L - 14` |

Calls for the chosen game (`game_ids: [id]`, `granularity: "day"`):

1. `user_unique`, `L - 13` to `L`
2. `new_users`, `L - 20` to `L` (also the retention weights)
3. `revenue`, `L - 13` to `L`
4. `paying_users`, `L - 13` to `L` (for the money floor)
5. `ilrd_revenue`, `L - 13` to `L`
6. `query_retention`, `metric: "retention_ahead"`, `game_id`, `days_ahead: 1`, `L - 14` to `L - 1`
7. `query_retention`, `metric: "retention_ahead"`, `game_id`, `days_ahead: 7`, `L - 20` to `L - 7`
8. For the next questions: `get_dimension_values` for `build` and for `ab_id`, `games: [id]`, `L - 6` to `L`

Compute, with code when the client can run it:

| KPI | Formula per period |
|---|---|
| DAU | mean of daily `user_unique` |
| New users | sum of daily `new_users` |
| D1, D7 retention | `sum(retention_d * new_users_d) / sum(new_users_d)` over the install days |
| IAP revenue | sum of daily `sum` |
| Ad revenue | sum of daily `sum`; leave the row out when both periods are 0 |
| ARPDAU | IAP revenue / sum of daily DAU |

Change: percent for counts and money, percentage points for retention. Apply the volume floors and mark thin values.

Present it like this:

```markdown
**Galaxy Quest**, last 7 complete days (29 Oct to 4 Nov 2026, UTC) against the 7 before

| KPI | Last 7 days | Previous 7 days | Change |
|---|---|---|---|
| DAU (average) | 12,340 | 11,980 | +3.0% |
| New users | 8,410 | 9,020 | -6.8% |
| D1 retention (installs 28 Oct to 3 Nov) | 31.2% | 30.1% | +1.1 pp |
| D7 retention (installs 22 to 28 Oct) | 8.4% | 8.9% | -0.5 pp |
| IAP revenue | $4,210.55 | $3,980.10 | +5.8% |
| ARPDAU | $0.049 | $0.047 | +3.4% |
```

Follow the table with at most three short observations, describing rather than explaining. Then one line on what this snapshot cannot see: design and progression events (see the metrics reference).

## Step 5: Five suggested next questions

Pick exactly five from [references/next-questions.md](references/next-questions.md), following its selection rules. Fill in the game name and real dates so each one can be asked as written. Number them 1 to 5.

## Rules

- Never show a number that did not come from a call in this session.
- If a call fails, show "not available" in that row and say which call failed in one line. Do not stop the snapshot for one missing metric.
- Do not compare the partial day `T` with anything.
- Keep the whole answer short enough to read in a minute: the games table, the snapshot, the observations, the five questions.
