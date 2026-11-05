# gameanalytics-getting-started

## Triggers

| Prompt | Expected |
|---|---|
| "I just connected GameAnalytics, what can you see?" | this skill |
| "Which games do I have in GameAnalytics?" | this skill |
| "How is my game doing?" | this skill |
| "What was D7 retention for Galaxy Quest last week on iOS?" | no skill needed: a direct query |
| "Write me last week's report for Galaxy Quest" | `gameanalytics-weekly-report` |
| "Show me top advertised puzzle games in the US" | not this plugin (Ad Insights) |

## Behaviour

1. **Not connected** (GameAnalytics MCP removed). Must: give the setup steps for the user's client and stop. Must not: show any number.
2. **Org without MCP Access** (403). Must: name MCP Access or PipelineIQ Pro and the get-access page. Must not: retry in a loop.
3. **Normal run.** Must: state the latest complete day and that today is partial; list studios and games with 7-day active users; build the snapshot for the 7 complete days against the 7 before; label the D1 and D7 install windows; end with exactly five numbered questions. Must not: call `conversion` or `retention_retro`; use today's partial data; suggest a question about design events.
4. **Accuracy.** For the chosen game and the same dates, DAU, new users, D1, D7, IAP revenue and ARPDAU match AnalyticsIQ.
5. **Thin game** (under 30 paying users a day). Must: mark money metrics thin; include the cumulative revenue question.
