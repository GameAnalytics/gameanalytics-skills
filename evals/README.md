# Evals

One file per skill. Each has trigger cases (does the description pick the right skill) and behaviour cases (does the run follow the skill). Run them by hand in a fresh session with the plugin installed, against a GameAnalytics account that has at least one game with 8 or more weeks of data.

A case passes when every "must" holds and no "must not" happens. Record results in the pull request that changes a skill, so a description change is checked against the trigger cases before it ships.

- [gameanalytics-getting-started](gameanalytics-getting-started.md)
- [gameanalytics-data-check](gameanalytics-data-check.md)
- [gameanalytics-weekly-report](gameanalytics-weekly-report.md)
- [gameanalytics-tracking-plan](gameanalytics-tracking-plan.md)
- [gameanalytics-sdk-setup](gameanalytics-sdk-setup.md)
