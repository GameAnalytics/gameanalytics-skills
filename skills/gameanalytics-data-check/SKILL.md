---
name: gameanalytics-data-check
description: Checks through the GameAnalytics MCP that data from a newly shipped build or a newly integrated game is arriving correctly (data freshness, the game appearing, the build string present, adoption of the new build, expected platforms, countries, A/B tests and ad networks present, purchases, ads and sessions compared with the previous build, and event types, errors and events per player across the game), and returns a PASS, WARN, FAIL or WAIT verdict per check with fixes. Use when someone has released a new build or version, integrated the GameAnalytics SDK into a new game, or asks whether their data is coming in.
---

# GameAnalytics: data arrival check

After a release, answer one question fast: is the new build's data arriving the way it should? Each check ends in a verdict with evidence and a next step. The skill only reads data.

Read before the first call:
- [references/mcp-connection.md](references/mcp-connection.md): servers, the connection probe, calling conventions
- [references/metrics.md](references/metrics.md): calls, response shapes, what the data cannot show
- [references/analysis-guardrails.md](references/analysis-guardrails.md): volume floors and language
- [references/event-rules.md](references/event-rules.md): build string and event format rules, for diagnosing a FAIL
- [references/diagnosis.md](references/diagnosis.md): symptom, likely cause and fix for every FAIL and WARN

## Inputs

Ask for anything missing in one message:

- **Game**: name or ID. Resolve names with `get_games`; never guess an ID.
- **Build string** exactly as set in the SDK, for example `1.4.0`.
- **Release time** in UTC. If unknown, use the first day the build appears and say so.
- **New game or new build of an existing game.**
- Optional expectations: platforms, soft-launch countries, an A/B test, ad networks, attribution source.

Set `R` = release date, `T` = the date part of the `get_interval` end (today, partial), `L` = `T - 1`. Presence checks run over `R` to `T`, since partial data still proves arrival.

## Checks

Run them in order. A FAIL on checks 1 to 3 stops the run: later checks would only repeat it.

| # | Check | Calls | Verdict |
|---|---|---|---|
| 1 | **Freshness** | `get_interval` | WAIT if its end is before the release time: data is processed hourly, so check again in about an hour. Otherwise PASS. |
| 2 | **Data from the game** | `query_metric` `event_count`, `game_ids: [id]`, `granularity: "all"`, `R` to `T` | PASS above 0. FAIL at 0: no event has reached GameAnalytics since release. `get_games` lists a game whether or not it sends data, so it cannot answer this. |
| 3 | **Build present** | `get_dimension_values`, `dimension: "build"`, `games: [id]`, `R` to `T`, `limit: 1000` | PASS on an exact match. FAIL on a near-miss (different case, spaces, a `v` prefix, cut at 32 characters) or on no match; list the builds that did arrive. |
| 4 | **Adoption** | `query_metric` `user_unique`, `granularity: "all"`, `query_type: "group"`, `dimension: "build"`, `R` to `T`; and `new_users` grouped by `first_build` | INFO: the new build's share of active users and of new installs. A low share during a phased store rollout is normal. WARN if there are new installs but none on the new build after 48 hours. |
| 5 | **Expected values** | One `query_metric` per expectation with `filters: {"build": "<build>"}`, `query_type: "group"`: `user_unique` by `platform` and by `country_code`; `user_unique` by `ab_id` and `ab_variant_id`; `ad_impressions_count` by `ad_sdk_name`; `ilrd_revenue` by `ilrd_network_name`; `new_users` by `install_publisher` | PASS when every expected value is present. FAIL for a missing expected platform. WARN for anything else missing. With no expectations given, list the platforms and top countries as INFO and ask whether they match. |
| 6 | **New build vs the previous build** | See below | PASS, WARN or FAIL per family. |
| 7 | **Game-wide event health since release** | See below | PASS, WARN or FAIL per item. |

Checks 6 and 7 use complete days only, `R` to `L`. With none yet, mark them WAIT.

### Check 6: new build vs the previous build

The previous build is the one with the most active users from `R - 7` to `R - 1`. Query each metric over `R` to `L` with `granularity: "all"`, `query_type: "group"`, `dimension: "build"`, which returns every build in one call, and compare the two builds:

| Family | Rate for each build | FAIL when | WARN when |
|---|---|---|---|
| Purchases | `revenue` (`sum`) / `user_unique` | The previous build averaged 30 or more paying users a day, the new build has 100 or more active users a day, and the new build's revenue is 0 | The rate fell by more than half |
| Ads | `ad_impressions_count` / `user_unique` | The previous build had impressions and the new build has none, at 100 or more active users a day | The rate fell by more than half |
| Ad revenue | `ilrd_revenue` (`sum`) / `user_unique` | The same as Ads | The rate fell by more than half |
| Sessions | `sessions_per_user` | | It fell by more than 30% |

If the new build is under the floor (100 active users a day), report the rates as **thin** and the verdict as WAIT: it is too early to tell.

### Check 7: game-wide event health since release

`event_count` cannot be filtered, grouped or split by `build`: it returns 0 or nothing. So event types, errors and volume are compared for the whole game, the days `R` to `L` against the same number of days before `R`, each divided by the sum of daily `user_unique`. A problem in a build used by 20% of players shows as a change of 20% or less here, so read it next to check 4.

| Item | Call | FAIL when | WARN when |
|---|---|---|---|
| Event types | `event_count`, `query_type: "group"`, `dimension: "category"` | A type sent before release (`business`, `ads`, `impression`, `resource`, `error`) is absent after it | A type's rate per player fell by more than half |
| Errors | `event_count`, `query_type: "group"`, `dimension: "severity"`; add `error` and `critical` | | The rate per player at least doubled |
| Event volume | `event_count`, `granularity: "day"`, divided by daily `user_unique` | Over 500 events per player per day: the collection limit | Over 450 per player per day |

The `category` and `severity` groupings cover only the core event types and do not add up to the `event_count` total. Never subtract them to estimate design or progression events.

## Output

```markdown
**Data check: Galaxy Quest, build 1.4.0**, released 3 Nov 2026 14:00 UTC; data processed up to 5 Nov 2026 09:00 UTC

| # | Check | Verdict | Evidence | Next step |
|---|---|---|---|---|
| 1 | Freshness | PASS | Data up to 5 Nov 09:00 UTC | |
| 3 | Build present | PASS | `1.4.0` seen from 3 Nov | |
| 4 | Adoption | INFO | 38% of active users, 61% of new installs | |
| 6 | Purchases | FAIL | $0 from 4,120 users on 1.4.0; $0.041 per user on 1.3.2 | Check the business event call ... |
```

After the table:

1. The FAILs and WARNs first, each with the fix from [references/diagnosis.md](references/diagnosis.md).
2. Always this paragraph, adapted: "Not checked here: design and progression events, resource events by currency or item, and custom dimensions are not in the Metrics API. Open Realtime > Live Events in GameAnalytics, filter Build to `<build>`, and confirm those events appear. Live Events shows the last 50 events, typically within 30 seconds of sending."
3. When the run had a WAIT, say when to run it again.

## Rules

- A metric that returns 0 for the new build is evidence only when the comparison build shows the same metric above 0 over the same days.
- Never call a build broken from a partial day alone.
- State evidence as numbers with their dates, not adjectives.
