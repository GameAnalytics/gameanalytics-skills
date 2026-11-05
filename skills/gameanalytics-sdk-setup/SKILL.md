---
name: gameanalytics-sdk-setup
description: Integrates the GameAnalytics SDK into a game project (Unity, Unreal, Godot, Roblox, Flutter, GameMaker, Android, iOS, JavaScript and others) from the live GameAnalytics docs, configures build, currencies, item types and custom dimensions before initialise, wires the events of a tracking plan through one typed wrapper, and walks the user to a first event in Realtime. Use when someone wants to add, install, integrate, initialise or fix the GameAnalytics SDK in their game, or to implement a GameAnalytics tracking plan in code.
---

# GameAnalytics: SDK setup

Get the SDK into the user's project the way the current docs describe, and stop when a first event shows in GameAnalytics. Code comes from the docs on every run, never from memory: SDK versions and install methods change.

Read before editing anything:
- [references/engine-detection.md](references/engine-detection.md): how to detect the engine, which page to fetch, the order of SDK calls, where keys come from
- [references/event-rules.md](references/event-rules.md): event formats and limits the wrapper must respect
- [references/mcp-connection.md](references/mcp-connection.md): how to connect the Documentation MCP if it is missing

This skill needs the GameAnalytics Documentation MCP (`docs_search`, `docs_fetch`). Without it, give the setup steps from the connection reference and stop.

## Step 1: Detect

1. Detect the engine from the project files, using the table in the engine reference. If the files are ambiguous, ask.
2. Look for an existing integration: search for `GameAnalytics` in code, package manifests and settings. If one exists, this is a repair: check the version and the order of calls rather than installing again.
3. Look for `gameanalytics/tracking-plan.csv`. If it exists, it is the source of truth for event IDs, currencies, item types and custom dimensions. If not, offer `gameanalytics-tracking-plan` first, or set up the SDK with sessions and errors only.

## Step 2: Fetch the docs

`docs_fetch` the engine's setup page, then its configuration and event tracking pages. Take from them, verbatim: the install method and current version, the configure and initialise calls, and the event methods. If the docs and the engine reference disagree, the docs win.

## Step 3: Propose, then change

Tell the user, in one message, what will change: the package or plugin to add, the files to create or edit, and where initialise will run. Wait for a yes before touching the project. Never run a package install or edit project settings without it.

## Step 4: Install and initialise

1. Install the SDK as the docs describe.
2. Add the configure calls before initialise, in the order from the engine reference: build, user ID if used, resource currencies and item types from the plan, custom dimension values from the plan.
3. Initialise with the game key and secret key read from the engine's settings or the project's config. Ask the user to enter the keys themselves (Game Settings in GameAnalytics); do not ask for them in chat.
4. In development builds only, turn on info and verbose logging.

## Step 5: The wrapper

Generate one small analytics module in the project's language with one method per planned event, for example `Analytics.LevelComplete(world, level, score)` or `Analytics.ShopOpened(source)`. Each method:

- builds the event ID from the plan's template,
- accepts placeholder values only from the plan's list (an enum or constants where the language has them),
- passes numbers in `value`, `score` or `amount`, never in the ID,
- calls the SDK method the docs give for that event type.

Then add calls to the wrapper at the triggers the plan names, only where the trigger is unambiguous in the code. List the triggers you could not place for the user to wire.

## Step 6: First event

Tell the user how to see it:

1. Make a device build (the Unity editor does not run the native SDK) with logging on, and play for a minute.
2. Open GameAnalytics > the game > Realtime > Live Events. Events typically appear within 30 seconds; filter by build to see only this build.
3. If nothing appears, check the device log for the SDK's init line and errors, and compare the game key with Game Settings.

Then offer `gameanalytics-data-check` for about an hour later, when the aggregated metrics include the build.

## Rules

- Change only what the user approved. Keep edits small and in the project's style.
- Never invent an SDK method or option. If the docs do not show it, say so.
- A deprecated or legacy page in the docs is not a reason to use it; prefer the engine's current setup page.
- Business events: amounts are integers in cents and currencies are ISO 4217 codes. Ad events: `ad_sdk_name` is lowercase with no spaces or underscores. Check the wrapper against [references/event-rules.md](references/event-rules.md).
