# Next questions bank

Each question is answerable with the GameAnalytics MCP tools. Replace `<game>`, the dates and the bracketed values before showing it.

## Selection rules

1. Take signal questions first, in the order the signals appear below, at most one per signal.
2. Fill the remaining places from the baseline list, in order.
3. Exactly five questions.
4. At least one asks for a breakdown by country, platform or build.
5. At most one hands off to another skill.
6. Never suggest a question about design events, progression events, resource events or custom dimensions: the MCP cannot answer them.
7. Skip a question whose metric was marked thin in the snapshot, except the low-volume question, which exists for that case.

## Signal questions

| Signal in the snapshot | Question |
|---|---|
| DAU changed by 10% or more | Which countries and platforms account for the change in DAU for `<game>` between `<previous>` and `<current>`? |
| New users changed by 15% or more | Which install sources (`install_publisher`) and countries drove the change in new users for `<game>`? |
| D1 changed by 2 pp or more, or D7 by 1 pp or more | How does D1 retention differ by country and platform for `<game>` installs from `<D1 window>`? |
| IAP revenue changed by 15% or more | Is the revenue change for `<game>` driven by the number of paying users or by spend per paying user (ARPPU)? |
| Money metrics thin (under 30 paying users a day) | What is cumulative revenue per user at day 7 and day 14 since install for `<game>`, by platform? |
| Ad revenue present | How does ad revenue per active user split by ad network and ad format for `<game>` over `<current>`? |
| IAP revenue and ad revenue both 0 | Are purchases and ads being tracked for `<game>`? (hands off to `gameanalytics-data-check`) |
| More than one build active in the current period | How do D1 retention and sessions per user compare between build `<newest>` and build `<previous>`? |
| An `ab_id` is active | How do D1 retention and ARPDAU compare between the variants of A/B test `<ab_id>`? |
| Data starts less than 30 days ago | How is D1 retention moving for each daily install cohort of `<game>` since `<first date>`? |

## Baseline questions

1. Which five countries bring the most active users and revenue to `<game>` over `<current>`?
2. How do D1 and D7 retention compare between iOS and Android for `<game>`?
3. How have DAU and revenue moved week by week over the last 8 weeks for `<game>`? (hands off to `gameanalytics-weekly-report`)
4. How have sessions per user and average session length moved over the last 4 weeks for `<game>`?
5. What share of `<game>`'s active users are paying users, by country?
