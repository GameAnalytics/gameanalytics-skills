---
name: gameanalytics-tracking-plan
description: Designs or audits a GameAnalytics tracking plan for a game, by genre and by the KPIs the team cares about, choosing the right event type for each question, applying naming rules, and checking the plan against the daily limits (15,000 unique design event IDs, 8,000 progression, 4,000 resource, 500 events per user) before writing a tracking-plan.md and a tracking-plan.csv data dictionary into the project. Use when someone wants to plan, review or clean up analytics events, an event taxonomy or event naming for a game that uses or will use GameAnalytics.
---

# GameAnalytics: tracking plan

Turn "what do we want to know about our game" into a short list of events that answer it, named so they stay inside GameAnalytics limits. The output is a plan the team reviews and `gameanalytics-sdk-setup` implements.

Read before drafting:
- [references/event-rules.md](references/event-rules.md): event types, ID formats, limits, naming rules
- [references/naming-and-budget.md](references/naming-and-budget.md): the CSV format, placeholders and how the budget is computed
- [references/genre-templates.md](references/genre-templates.md): starting points per genre

This skill needs the GameAnalytics Documentation MCP (`docs_search`, `docs_fetch`). It does not need a GameAnalytics account.

## Step 1: Interview

Ask in one message, and skip what the project or the user already answered:

1. Genre and sub-genre, with one sentence on the core loop.
2. Business model: in-app purchases, ads, both, or premium.
3. Engine and platforms.
4. The three to five decisions the team wants data for (for example "is level 12 too hard", "which offer sells", "do rewarded ads hurt retention"). These become the KPIs.
5. Live-ops features: A/B tests, remote configs, events, battle pass.
6. Expected sessions per player per day and expected peak DAU, rough is fine.
7. An existing plan or existing tracking code to audit, if there is one.

If the user wants a plan straight away, use the genre template's defaults and list the assumptions at the top of the plan.

## Step 2: Check the rules are current

Run `docs_search` for "event tracking and cardinality limits" and for the event types the plan will use, and `docs_fetch` the top pages. If anything differs from the event rules reference, follow the live docs and say what changed.

## Step 3: Draft

Start from the genre template, then cut it to what serves the user's decisions. Fewer events, used well, beat full coverage.

Pick the event type in this order: the automatic events (sessions, errors), then business for purchases, ad for ads, progression for levels and stages, resource for virtual currency, and design only for what is left. Use custom dimensions for player segments that apply to every event (at most 3, 20 values each).

For every event, write: the type, the ID template with placeholders, the allowed values of each placeholder, what triggers it, which KPI it serves, what goes in `value`, `score` or `amount`, and how often an average player sends it per day.

Auditing existing code instead: search the project for the SDK's event calls (for example `GameAnalytics.NewDesignEvent`, `addDesignEvent`, `NewProgressionEvent`), list the IDs found, and convert them into the CSV before checking.

## Step 4: Check the budget

Write the CSV (format in the naming and budget reference) to `gameanalytics/tracking-plan.csv` in the project, then run:

```bash
python3 <skill dir>/scripts/check_plan.py gameanalytics/tracking-plan.csv --markdown
```

It validates every ID and computes the worst case: unique IDs per day for each type, events per player per day, currencies, item types and custom dimension values. On any error or "over safe line", revise the plan (merge values, move detail into `value` or custom fields, drop low-value events) and run it again. Never hand over a plan that fails the check.

If the client cannot run Python, compute the budget by hand as the naming and budget reference describes, and say so in the plan.

## Step 5: Write the plan

Write `gameanalytics/tracking-plan.md` from [assets/tracking-plan-template.md](assets/tracking-plan-template.md): the decisions and KPIs, the event table, the budget table from the script, what goes in custom dimensions and custom fields, and the open questions. Keep the CSV next to it as the source of truth: `gameanalytics-sdk-setup` reads it.

Ask before creating the `gameanalytics/` folder, and before overwriting an existing plan.

## Step 6: Hand off

Summarize in chat: the number of events by type, the budget headroom, and the assumptions to confirm. Then offer `gameanalytics-sdk-setup` to implement it. After launch, point to Game Overview > Integrations in GameAnalytics, where limit alerts appear, and to `gameanalytics-data-check` for the first build.

## Rules

- No dynamic values in IDs, ever. The checker rejects placeholder names that look like one; do not rename a placeholder to get past it.
- Do not plan analysis the Metrics API cannot do and promise it through the MCP: design and progression events are analysed in AnalyticsIQ (Explore, Funnels), not through the GameAnalytics MCP.
- Do not invent SDK method names in the plan. Name event types, not code; the SDK setup skill fetches the code from the docs.
