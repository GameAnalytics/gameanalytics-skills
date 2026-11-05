# Event rules and limits

What the GameAnalytics SDKs and Collection API accept. Always re-check a rule against the live docs (`docs_search`, `docs_fetch`) before writing code: these pages change.

Sources:
- [Event types (Collection API)](https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/api/event-types)
- [Event tracking and cardinality limits](https://docs.gameanalytics.com/event-tracking-and-integrations/data-retention-and-limits/event-tracking-and-cardinality-limits)
- [Design](https://docs.gameanalytics.com/events-metrics-and-filtering/event-types/design-events), [Progression](https://docs.gameanalytics.com/events-metrics-and-filtering/event-types/progression-events), [Resource](https://docs.gameanalytics.com/events-metrics-and-filtering/event-types/resource-events), [Business](https://docs.gameanalytics.com/events-metrics-and-filtering/event-types/business-events), [Ad](https://docs.gameanalytics.com/events-metrics-and-filtering/event-types/ad-events) events
- [Custom dimensions](https://docs.gameanalytics.com/event-tracking-and-integrations/advanced-tracking/custom-dimensions), [Custom event fields](https://docs.gameanalytics.com/event-tracking-and-integrations/advanced-tracking/custom-event-fields)
- [Plan your SDK implementation](https://docs.gameanalytics.com/getting-started/plan-your-sdk-implementation)

## Limits

| Limit | Value | Plan to stay under |
|---|---|---|
| Events per active user per day | 500 | 450 |
| Unique design event IDs per game per day | 15,000 | 13,500 |
| Unique progression event IDs per game per day | 8,000 | 7,200 |
| Unique resource event IDs per game per day | 4,000 | 3,600 |

Over a cardinality limit, events are still collected but their identifiers become `null`. Metrics built on them become wrong in AnalyticsIQ and through the Metrics API; Data Warehouse and Data Export keep the full payload. Alerts appear under Game Overview > Integrations.

## Event types

Prefer the prescriptive types: they fill GameAnalytics dashboards with no setup. Use design events only for what no other type covers.

| Type | Use for | ID format |
|---|---|---|
| Session (`user`, `session_end`) | Sessions | Sent automatically by the SDK |
| Error | Crashes and exceptions | Severity `debug`, `info`, `warning`, `error`, `critical`. Message up to 8,192 characters. At most 10 per game launch. Sent automatically by the Unity, iOS and Android SDKs |
| Business | Real-money purchases | `itemType:itemId`, each part 1 to 64 characters. Amount is an integer in cents; currency is an ISO 4217 code such as `USD`. Receipt validation works on iOS and Android |
| Ad | Ad shows, clicks, failures, rewards | `ad_type`: `video`, `rewarded_video`, `playable`, `interstitial`, `offer_wall`, `banner`. `ad_action`: `clicked`, `show`, `failed_show`, `reward_received`. `ad_sdk_name` lowercase, no spaces or underscores. `ad_placement` up to 64 characters |
| Progression | Levels, worlds, missions, tutorial steps | `Start`, `Fail` or `Complete`, then 1 to 3 tiers: `Complete:World01:Level05`. Optional integer `score`; attempt number is sent on Fail and Complete |
| Resource | Virtual currency earned and spent | `Source` or `Sink`, then currency, item type, item ID: `Sink:Gems:Boost:DoubleXP`. Currency matches `[A-Za-z]{1,64}`. The amount is positive; the SDK signs it |
| Design | Everything else: feature use, UI, choices, tutorial branches | 1 to 5 parts joined by `:`, e.g. `shop:open:main_menu`. Optional float `value` |

**Characters.** Each design, progression, business and resource part is 1 to 64 characters from `A-Z a-z 0-9`, space, and `- _ . ( ) ! ?`.

**Register before initialize.** Resource currencies and item types, and custom dimension values, must be configured in the SDK before it initialises. Anything not registered is rejected. Plan for at most 20 currencies and 20 item types: the docs give 20 on the engine pages and 50 currencies on the resource events page, so 20 is the safe number.

## Custom dimensions and fields

- **Custom dimensions** `custom_01`, `custom_02`, `custom_03`: segment users (for example player type or difficulty). At most 20 values each, registered before init, each value up to 32 characters. Values persist across sessions until reset. They do not apply to design events.
- **Custom event fields**: up to 50 key-value pairs on an event. Visible only in Data Warehouse and Data Export, not in the AnalyticsIQ UI or the Metrics API. Use them for high-cardinality detail such as coordinates.
- **Build**: up to 32 characters. Set it with the SDK's configure-build call before init so every event carries it.

## Naming rules

1. Structure design IDs as `category:subcategory:outcome`, lowest cardinality on the left.
2. Never put a dynamic value in an ID: no user IDs, timestamps, coordinates, scores, prices, durations, random seeds or generated content IDs. Put numbers in `value` (design), `score` (progression) or `amount` (resource), and detail in custom fields.
3. Enumerate every part's allowed values. If you cannot list them, the part is unbounded and will break the cardinality limit.
4. Use one casing style and stick to it. `shop:open` and `Shop:Open` count as two IDs.
5. Group large sets: item rarity rather than item name, area rather than coordinates, `ugc_video` rather than each upload.
6. Use progression events for levels rather than `level:5:complete` design events.
