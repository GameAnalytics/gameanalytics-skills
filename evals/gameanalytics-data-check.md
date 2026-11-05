# gameanalytics-data-check

## Triggers

| Prompt | Expected |
|---|---|
| "We shipped 1.4.0 yesterday, is data coming in?" | this skill |
| "I added the SDK to my new game, is GameAnalytics receiving anything?" | this skill |
| "Is the new build reporting purchases?" | this skill |
| "Help me add the GameAnalytics SDK to Unity" | `gameanalytics-sdk-setup` |
| "Is the event Level_5_Complete arriving?" | this skill, which must say the MCP cannot see design or progression events and point to Live Events |

## Behaviour

1. **Healthy build.** Must: a verdict table with PASS on freshness, data from the game and build; adoption shares as INFO; event types and families compared with the previous build on rates over the same days. Must not: compare a partial day alone; use `get_games` as proof that data arrives.
2. **Misspelled build** (the game sends `v1.4.0`, the user says `1.4.0`). Must: FAIL check 3 as a near-miss and show the string that arrived.
3. **Build never configured** (game data present, no new build string). Must: FAIL check 3 and point to configuring the build before initialise.
4. **Release an hour ago.** Must: WAIT on freshness or on check 6, with when to check again.
5. **Always.** Must: the paragraph on what is not checked (design and progression events, resource events by currency, custom dimensions) with the Live Events steps.
6. **Event volume.** Must: events per player per day from `event_count` divided by DAU, with WARN over 450 and FAIL over 500. Must not: filter `event_count` by build, or subtract the `category` groups from the total to estimate design events.
7. **Old build without purchases.** On a game where one build has users but $0 revenue while another earns, must: FAIL purchases for that build when it is the new one and the floors are met.
