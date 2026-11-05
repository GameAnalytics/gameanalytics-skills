# Plan CSV, placeholders and the budget

## CSV columns

| Column | Required | Content |
|---|---|---|
| `event_type` | yes | `design`, `progression`, `resource`, `business`, `ad`, `error`, `session`, `custom_dimension_01`, `custom_dimension_02`, `custom_dimension_03` |
| `event_id` | yes | The ID template. Placeholders in braces: `shop:open:{source}`, `{status}:World{world}:Level{level}`. For a custom dimension, its name. For `ad`, `error` and `session`, a short label |
| `values` | yes | Allowed values per placeholder, `;`-separated, values split by a pipe: `source=main_menu\|level_end; level=1..50`. `a..b` is an integer range. For a custom dimension: `values=new\|returning\|payer` |
| `trigger` | | What in the game sends it |
| `kpi` | | The decision or KPI it serves |
| `value_meaning` | | What goes in `value` (design), `score` (progression) or `amount` (resource, business) |
| `per_user_per_day` | yes | Average sends per active player per day. Count each status of a progression row, both start and end of sessions, every ad action |
| `notes` | | Anything the implementer needs |

The sample in [../assets/tracking-plan-template.csv](../assets/tracking-plan-template.csv) passes the checker.

## Placeholders

- Every placeholder needs a closed list or range of values. A placeholder whose values you cannot list is a dynamic value: move it out of the ID.
- Name placeholders after what they hold (`source`, `world`, `rarity`). Names like `user`, `timestamp`, `score`, `price`, `x` are rejected as dynamic.
- Progression templates start with the status: `{status}:...` with `status=Start|Fail|Complete`, or one fixed status.
- Resource templates have four parts: `{flow}:{currency}:{item_type}:{item_id}` with `flow=Source|Sink`.
- In the CSV, quote a `values` cell only if it contains a comma. Every currency and item type must be registered in the SDK before init.

## Budget

The checker computes the worst case, assuming every combination is sent on the same day:

- **Unique IDs per type per day** = sum over rows of the product of each placeholder's value count. `{status}:World{world}:Level{level}` with 3 statuses, 5 worlds and 20 levels is 300.
- **Events per player per day** = sum of `per_user_per_day` over all rows.
- **Currencies and item types** = distinct values across resource rows; at most 20 each.
- **Custom dimension values**: at most 20 per dimension, each up to 32 characters.

Plan to stay under the safe line: 13,500 design, 7,200 progression and 3,600 resource IDs, and 450 events per player. That leaves room for content added after launch.

## Getting back under budget

| Problem | Fix |
|---|---|
| A part enumerates items, levels or content | Group it: rarity instead of item, chapter instead of level, a type instead of a UGC ID |
| Levels tracked as design events | Use progression events |
| Two placeholders multiply | Split into two events, or drop the less useful part |
| A number in the ID (score, time, damage) | Put it in `value` or `score` |
| A per-frame or per-tap event | Aggregate per session or per level and send once, with the count in `value` |
| Detail needed only for deep analysis (coordinates, loadouts) | Custom event fields, analysed in Data Warehouse or Data Export |
