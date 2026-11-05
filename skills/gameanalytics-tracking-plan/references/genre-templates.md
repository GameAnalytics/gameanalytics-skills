# Genre templates

Starting points, not finished plans. Every genre also gets the base set. Cut anything that does not serve a decision the team named.

Placeholders follow the plan CSV format: `{name}` in the ID, values listed separately. Numbers in brackets are typical sends per player per day, for the budget.

## Base set (every game)

| Type | Event | Serves |
|---|---|---|
| session | Automatic session start and end [8] | DAU, retention, session length |
| error | Automatic on Unity, iOS, Android; manual elsewhere [1] | Stability by build |
| design | `tutorial:{step}:complete`, one value per step [1] | Tutorial funnel; put seconds on the step in `value` |
| design | `settings:{setting}:{state}` for a few settings that matter (sound, notifications) [0.2] | Feature use |
| custom dimension | Player segment, such as `player_type` = new, returning, payer | Segment any KPI |

Business events for every real-money purchase, and ad events for every ad shown, whenever the game has IAP or ads.

## Hyper-casual

Decisions: does the core loop retain, where do players drop, how many ads per session before churn.

| Type | Event | Notes |
|---|---|---|
| progression | `{status}:Level{level}` with status Start, Fail, Complete [20] | Cap `level` at the designed count; endless levels reuse a cycle number, not a counter |
| ad | interstitial and rewarded_video: `show`, `failed_show`, `reward_received` [6] | Placement in `ad_placement`, such as `level_end` |
| design | `ad:{placement}:offered` [3] | Rewarded ad offers that were not taken |

## Puzzle and match-3

Decisions: level difficulty, booster economy, which offers sell.

| Type | Event | Notes |
|---|---|---|
| progression | `{status}:Episode{episode}:Level{level}` [15] | `score` on Complete; the attempt number is automatic |
| resource | `{flow}:{currency}:{item_type}:{item_id}` with Coins, Lives; item types booster, reward, shop, life [8] | `item_id` is the booster or reward kind, never a level number |
| design | `booster:{booster}:used` [3] | Moves left or level tier in `value`, not in the ID |
| business | `{item_type}:{item_id}` with item types coins_pack, bundle, pass [0.05] | |

## Idle and simulation

Decisions: progression speed, offline earnings, prestige timing.

| Type | Event | Notes |
|---|---|---|
| progression | `Complete:Prestige{tier}` [0.3] | Prestige or era resets as tiers |
| resource | Soft and hard currency sources and sinks by system (`upgrade`, `offline`, `manager`) [10] | Group upgrades by system, never one item ID per upgrade level |
| design | `offline:collect:{multiplier}` with multiplier x1, x2 [1] | Hours offline in `value` |
| design | `upgrade:{system}:purchased` [15] | Upgrade level in `value` |

## RPG and midcore

Decisions: early progression, gacha and gear economy, which content holds players.

| Type | Event | Notes |
|---|---|---|
| progression | `{status}:Chapter{chapter}:Stage{stage}` [10] | |
| resource | Gold, Gems, Energy, by source (quest, battle, shop, gacha) and sink (upgrade, summon, refill) [12] | Item ID is a category such as `hero_upgrade`, never a hero ID |
| design | `gacha:{banner_type}:{rarity}` [2] | Banner type (standard, limited), not each banner's name |
| design | `hero:levelup:{rarity}` [5] | Level reached in `value` |
| design | `pvp:{mode}:{outcome}` [3] | |

## Strategy and 4X

Decisions: onboarding, alliance join rate, build queue friction.

| Type | Event | Notes |
|---|---|---|
| progression | `Complete:HQ{level}` [0.5] | Headquarters or main building level as the backbone |
| resource | Resources by source (gather, quest, raid) and sink (build, train, research) [10] | |
| design | `alliance:{action}` with join, leave, help [1] | |
| design | `speedup:{queue}:used` [3] | Minutes skipped in `value` |

## Shooter and action

Decisions: match outcomes, weapon balance, mode popularity.

| Type | Event | Notes |
|---|---|---|
| design | `match:{mode}:{outcome}` [4] | Kills or score in `value`, map in a custom field if needed |
| design | `loadout:{weapon_class}:selected` [4] | Weapon class, not each weapon skin |
| progression | `{status}:Season{season}:Tier{tier}` for a battle pass [1] | Cap tiers at the pass length |
| business | Battle pass and bundle purchases [0.05] | |

## Casino and social casino

Decisions: coin balance health, which machines retain, bonus economy.

| Type | Event | Notes |
|---|---|---|
| resource | Coins by source (bonus, purchase, win) and sink (bet) [30] | Bet size never in the ID; send the amount |
| design | `machine:{machine_group}:spin` [aggregate per session, 4] | Aggregate spins per session with the count in `value`; per-spin events break the per-player limit |
| design | `bonus:{bonus_type}:collected` [3] | |

## Sports and racing

Decisions: event participation, car or team upgrades, career progression.

| Type | Event | Notes |
|---|---|---|
| progression | `{status}:Career{season}:Event{event}` [8] | |
| design | `race:{mode}:{result}` [5] | Position or time in `value` |
| resource | Cash and premium currency by source and sink, item type upgrade, tuning, car [8] | |

## Hybrid-casual

Combine the hyper-casual loop with a light meta: add a resource event for the meta currency, a design event for the meta upgrade (`meta:{system}:upgrade`), and business events for no-ads and bundle purchases. Watch per-player volume: hybrid games often send level and ad events at hyper-casual rates on top of meta events.
