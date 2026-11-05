# gameanalytics-weekly-report

## Triggers

| Prompt | Expected |
|---|---|
| "Weekly report for Galaxy Quest" | this skill |
| "How did my game do last week compared with the week before?" | this skill |
| "Set up a Monday report for all my games" | this skill, plus how to schedule it |
| "What's my DAU today?" | no skill needed: a direct query |

## Behaviour

1. **Normal run.** Must: the last complete ISO week; all seven template sections in order; the script's tables unchanged; the method line under Anomalies; three to five questions tied to findings; the report and the JSON sidecar saved under `gameanalytics-reports/<game-slug>/`. Must not: any number not from a call; any cause stated as fact.
2. **Second week.** Run again for the following week. Must: pass the previous sidecar; mark a KPI flagged both weeks as a repeat.
3. **Week not complete** (run on a Sunday). Must: use the week before and say why.
4. **No code execution.** Must: compute by the documented formulas and add the data note.
5. **Known incident week** (a week with a real outage or feature launch). Must: flag the affected KPI; must not flag KPIs under their floors.
6. **Chunking.** Must: no `day` request longer than 31 days.
