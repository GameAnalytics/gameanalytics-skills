# Connecting to GameAnalytics

Two MCP servers. The skills only work with these two.

| Server | URL | Auth | Tools |
|---|---|---|---|
| GameAnalytics MCP | `https://mcp.gameanalytics.com` | Sign in with a GameAnalytics account (OAuth) | `get_games`, `get_studios`, `get_dimensions`, `get_dimension_values`, `get_interval`, `get_supported_metrics`, `query_metric`, `query_retention`, `query_cumulative` |
| GameAnalytics Documentation MCP | `https://mcp.docs.gameanalytics.com` | None | `docs_search`, `docs_fetch` |

Tool names may carry a client prefix, such as `mcp__gameanalytics__get_interval`. Match on the part after the last separator.

## Which server is connected

- **GameAnalytics MCP connected:** `get_interval` and `query_metric` are available.
- **Only `fetch_*` tools are available** (`fetch_user_unique`, `fetch_revenue` and so on): that is the self-hosted GA-MCP server, which these skills do not support. Give the setup steps below for the hosted server.
- **Neither:** give the setup steps below and stop. Never guess numbers.

## Connection probe

Call `get_interval` with no arguments. It is cheap and touches the account.

| Result | Meaning | Say to the user |
|---|---|---|
| An interval such as `2025-11-01T00:00:00.000Z/2026-11-05T09:00:00.000Z` | Connected, data exists | Report the earliest and latest dates. The latest day is partial. |
| "No data available" (HTTP 204) | Connected, the account has no game data yet | Integrate the SDK first (`gameanalytics-sdk-setup`), then check again. |
| Authentication error (401) | The sign-in expired or was revoked | Disconnect and reconnect the GameAnalytics server in the AI tool to sign in again. |
| `403` | The organization has neither MCP Access nor PipelineIQ Pro | Get access on the [GameAnalytics MCP server page](https://www.gameanalytics.com/mcp-server). Retrying will not help. |

## Setup

Full instructions: [GameAnalytics MCP](https://docs.gameanalytics.com/ai-tools/ga-mcp) and [Documentation MCP](https://docs.gameanalytics.com/ai-tools/documentation-mcp).

- **Claude (web and desktop):** Settings > Connectors > Add custom connector, name `GameAnalytics`, URL `https://mcp.gameanalytics.com`, then Connect. The Documentation MCP is in the connector directory as GameAnalytics Documentation.
- **Claude Code:** installing this plugin adds both servers. Without the plugin:

  ```bash
  claude mcp add --transport http gameanalytics https://mcp.gameanalytics.com
  claude mcp add --transport http gameanalytics-docs https://mcp.docs.gameanalytics.com
  ```

  Then run `/mcp`, select `gameanalytics` and authenticate.
- **Codex:** `codex mcp add gameanalytics --url https://mcp.gameanalytics.com`, then `codex mcp login gameanalytics`. Docs: `codex mcp add --url https://mcp.docs.gameanalytics.com gameanalytics-docs`.
- **Cursor:** in `~/.cursor/mcp.json` or a project's `.cursor/mcp.json`:

  ```json
  {
    "mcpServers": {
      "GameAnalytics": { "url": "https://mcp.gameanalytics.com" },
      "gameanalytics-docs": { "type": "http", "url": "https://mcp.docs.gameanalytics.com" }
    }
  }
  ```

The GameAnalytics MCP reads every organization, studio and game the signed-in account can see. It is read-only.

## Calling conventions

- Dates are `YYYY-MM-DD` in UTC. `end_date` is inclusive: the server queries up to `23:59:59` of that day.
- `game_ids` takes game IDs as strings. Get them from `get_games`, never from a name.
- `filters` is a flat object, AND-ed: `{"platform": "ios"}` or `{"country_code": ["US", "CA"]}`.
- `query_type`: `timeseries` (default), `group` with one `dimension`, or `split` with exactly two `dimensions`.
- With `granularity: "day"`, one request covers at most 31 days. Split longer ranges into chunks of 31 days or fewer.
- `query_retention` and `query_cumulative` take a single `game_id`.

## Calls to avoid

These request shapes do not match the Metrics API specification and are likely to fail. Use the workaround.

| Avoid | Use instead |
|---|---|
| `query_metric` with `conversion` | `paying_users / user_unique` over the same days |
| `query_metric` with `conversion_ft` | `converting_users / user_unique` |
| `query_retention` with `retention_retro` | `retention_ahead` |
| `query_retention` with `returning_users` | `retention_count` |

If a call fails anyway, say which call failed and carry on without that number. Never fill the gap with an estimate.
