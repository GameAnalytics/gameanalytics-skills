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

1. **Healthy build.** Must: a verdict table with PASS on freshness, game and build; adoption shares as INFO; event families compared with the previous build on rates over the same days. Must not: compare a partial day alone.
2. **Misspelled build** (the game sends `v1.4.0`, the user says `1.4.0`). Must: FAIL check 3 as a near-miss and show the string that arrived.
3. **Build never configured** (game data present, no new build string). Must: FAIL check 3 and point to configuring the build before initialise.
4. **Release an hour ago.** Must: WAIT on freshness or on check 6, with when to check again.
5. **Always.** Must: the paragraph on what is not checked (design, progression, resource events, custom dimensions) with the Live Events steps.
