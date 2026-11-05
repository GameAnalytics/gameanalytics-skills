# Tracking plan: <game>

Version <n>, <date>. Engine: <engine>. Platforms: <platforms>. Business model: <model>.

## Decisions this plan serves

| Decision | KPI | Where to read it |
|---|---|---|
| <Is level 12 too hard?> | <Fail rate per level> | <AnalyticsIQ Funnels on progression events> |

## Assumptions to confirm

- <Sessions per player per day, peak DAU, anything taken from the genre template>

## Events

| Type | Event ID | Values | Trigger | KPI | value / score / amount | Per player per day |
|---|---|---|---|---|---|---|
| progression | `{status}:World{world}:Level{level}` | status = Start, Fail, Complete; world = 1 to 5; level = 1 to 20 | Level start and end | Level funnel | Score on Complete | 12 |

`tracking-plan.csv` next to this file is the source of truth for implementation.

## Budget

<The budget table printed by check_plan.py.>

## Register before initialize

- Build: <how the build string is set, for example the version name>
- Resource currencies: <list>
- Resource item types: <list>
- Custom dimension 01 <name>: <values>

## Custom event fields

- <Detail kept out of IDs, analysed in Data Warehouse or Data Export, at most 50 fields per event>

## Open questions

- <Anything the team must decide before implementation>
