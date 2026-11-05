# gameanalytics-sdk-setup

## Triggers

| Prompt | Expected |
|---|---|
| "Add GameAnalytics to my Unity project" | this skill |
| "Implement our tracking plan" | this skill |
| "GameAnalytics init fails on Android" | this skill (repair) |
| "Is data from build 1.4.0 arriving?" | `gameanalytics-data-check` |

## Behaviour

1. **Blank Unity project with a plan.** Must: detect Unity; fetch the Unity setup, configuration and event tracking pages; propose the changes and wait for a yes; configure build, currencies, item types and custom dimensions from the CSV before initialise; generate a wrapper with one method per planned event; explain Live Events and the device build. Must not: ask for the secret key in chat; invent SDK methods.
2. **Blank JavaScript project.** Same, with the npm install from the docs. Must: a first event visible in Live Events.
3. **Existing integration with configure after init.** Must: treat it as a repair and move the configure calls before initialise.
4. **Engine with no SDK.** Must: point to the Collection API and say the integration belongs on a server.
5. **End to end.** Tracking plan, then this skill, then `gameanalytics-data-check` an hour later, on a blank Unity project and a blank JavaScript project. Pass: events in Live Events and PASS on data check checks 1 to 3.
