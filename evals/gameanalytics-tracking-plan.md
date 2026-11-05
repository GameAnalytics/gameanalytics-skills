# gameanalytics-tracking-plan

## Triggers

| Prompt | Expected |
|---|---|
| "Plan the analytics events for my match-3 game" | this skill |
| "Review our event naming, we keep hitting the design event limit" | this skill (audit) |
| "What should I track for a hyper-casual game?" | this skill |
| "Install the GameAnalytics SDK in Godot" | `gameanalytics-sdk-setup` |

## Behaviour

1. **New plan.** Must: one interview message; fetch the limits and event type pages through the Documentation MCP; use progression for levels and resource for currency; write `gameanalytics/tracking-plan.csv` and `.md` after asking; run `check_plan.py` and show a passing budget table. Must not: put a score, timestamp, price or user ID in an ID.
2. **Over budget.** Ask for one design event per item for 400 items across 50 levels. Must: the checker fails; the skill restructures (item rarity, progression events) until it passes.
3. **Audit.** Point it at code with `NewDesignEvent("kill:" + enemyId + ":" + x + ":" + y)`. Must: identify the dynamic parts and propose grouped IDs with coordinates in custom fields.
4. **No Documentation MCP.** Must: give the connection steps; may continue from the bundled event rules but must say they were not checked against the live docs.
