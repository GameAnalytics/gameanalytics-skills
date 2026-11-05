# GameAnalytics skills

Skills that teach your AI assistant to work with [GameAnalytics](https://gameanalytics.com): plan what to track, integrate the SDK, get a first read of your games, check a new build's data, and write a weekly KPI report.

They follow the [Agent Skills](https://agentskills.io) standard, so they work in Claude, Claude Code, Cursor, Codex and other clients that support skills. They run on two GameAnalytics MCP servers.

## Skills

| Skill | What it does | Needs |
|---|---|---|
| `gameanalytics-tracking-plan` | Designs or audits a tracking plan by genre and KPI, with naming rules, and checks it against the daily limits: 15,000 unique design event IDs, 8,000 progression, 4,000 resource, 500 events per player. Writes `gameanalytics/tracking-plan.md` and `.csv` | Documentation MCP |
| `gameanalytics-sdk-setup` | Integrates the SDK into your engine from the live docs, configures it before initialise, generates a typed wrapper for your plan, and gets you to a first event in Realtime | Documentation MCP |
| `gameanalytics-getting-started` | Confirms the connection, checks data availability, lists your games, and gives a health snapshot (DAU, new users, D1 and D7 retention, revenue, ARPDAU) with five suggested next questions | GameAnalytics MCP |
| `gameanalytics-data-check` | After a release, checks that the new build's data is arriving: freshness, the build string, adoption, expected platforms and countries, purchases, ads and sessions against the previous build, and event types, errors and events per player against the 500 limit | GameAnalytics MCP |
| `gameanalytics-weekly-report` | A fixed-structure weekly report: KPIs week on week, top movers by country and platform, anomalies against an 8-week trend, and questions to ask next. Saved as a dated markdown file | GameAnalytics MCP |

## Requirements

- **[GameAnalytics MCP](https://docs.gameanalytics.com/ai-tools/ga-mcp)** at `https://mcp.gameanalytics.com`, for the three data skills. You sign in with your GameAnalytics account. Your organization needs MCP Access or PipelineIQ Pro; [get access](https://www.gameanalytics.com/mcp-server).
- **[GameAnalytics Documentation MCP](https://docs.gameanalytics.com/ai-tools/documentation-mcp)** at `https://mcp.docs.gameanalytics.com`, for the tracking plan and SDK setup skills. Free, no account needed.
- **Python 3.9 or later** where the client runs code. The tracking plan and weekly report skills use small standard-library scripts for their arithmetic; without Python they fall back to documented formulas.

## Install

### Claude Code

```bash
claude plugin marketplace add GameAnalytics/gameanalytics-skills
claude plugin install gameanalytics@gameanalytics
```

The plugin adds the five skills and both MCP servers. Run `/mcp`, select `gameanalytics` and sign in.

### Claude (web, desktop and Cowork)

1. Add the connectors: Settings > Connectors > Add custom connector, name `GameAnalytics`, URL `https://mcp.gameanalytics.com`. Add GameAnalytics Documentation from the connector directory.
2. Download the skill zips from the latest release (or build them with `scripts/package.sh`) and upload each one under Settings > Capabilities > Skills.

### Cursor, Codex and other clients

1. Add both MCP servers: the [GameAnalytics MCP](https://docs.gameanalytics.com/ai-tools/ga-mcp) and [Documentation MCP](https://docs.gameanalytics.com/ai-tools/documentation-mcp) pages give the configuration for each client.
2. Copy the folders under `skills/` into your client's skills folder.

## Try it

- "Which games do I have in GameAnalytics, and how is the biggest one doing?"
- "Plan the analytics events for my match-3 game on Unity."
- "Add the GameAnalytics SDK to this project and implement the plan."
- "We shipped build 1.4.0 yesterday. Is the data coming in?"
- "Write last week's report for Galaxy Quest."

## Privacy

The GameAnalytics MCP is read-only and returns only data your account can already see. What you ask and the numbers it returns are processed by your AI provider under that provider's terms. The data skills write files only where stated: the tracking plan and SDK skills ask before changing your project, and the weekly report saves to `gameanalytics-reports/`.

## What these skills cannot see

The GameAnalytics MCP is built on the Metrics API, which has no event IDs. The skills can count events by type (purchases, ads, ad revenue, resource, errors, sessions), but they cannot see design or progression events, resource events by currency or item, or custom dimensions. For those, they point you to Realtime > Live Events and AnalyticsIQ.

## Contributing

- `shared/` holds the rules several skills need. `scripts/sync-shared.sh` copies each file into the skills whose `SKILL.md` links it, because every skill folder must stand alone. Edit `shared/`, never the copies.
- `scripts/check.sh` validates frontmatter, synced copies, links and the unit tests. Run it before every pull request.
- `evals/` holds the trigger and behaviour cases for each skill. Run the affected ones when a skill changes.
- No em or en dashes in any file; the check enforces it.

## License

[Apache 2.0](LICENSE)
