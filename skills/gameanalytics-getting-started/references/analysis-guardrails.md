# Analysis guardrails

Rules for any number this skill reports. They exist because the most common ways an AI answer about game data goes wrong are a partial period, a tiny sample and an invented cause.

## Periods

- Use complete UTC days only. State the exact dates of every period.
- Compare equal-length periods. Week with week, 7 days with 7 days.
- Label retention with its install-day window, which differs from the activity window.

## Volume floors

Below these, a rate is noise. Show the number, mark it **thin**, and never flag it as a change or an anomaly.

| Metric family | Floor (daily average in the period) |
|---|---|
| User counts and engagement (DAU, sessions, session length) | 100 active users |
| Retention | 200 new users |
| Money (revenue, ARPDAU, ARPPU, conversion) | 30 paying users |
| Ad revenue and impressions | 100 active users |

For a breakdown (a country, a platform, a build), apply the same floors to the slice, and skip any slice under 2% of the game's total for that metric.

## Arithmetic

- Do arithmetic with code when the client can run it, not mentally.
- Round only for display: integers for counts, two decimals for USD (three for per-user amounts under $1, such as ARPDAU), one decimal for percentages and percentage points.
- A change in a rate is reported in percentage points (pp), not percent. D1 going from 30% to 27% is -3.0 pp.
- Divide by zero means "not available", never 0% or infinity.

## Language

- Describe, do not explain. "Revenue fell 18% week on week, mostly in the US" is fine. "Revenue fell because of the update" is not, unless the user supplied that fact.
- Never say nothing happened elsewhere: say what was checked.
- Name every number's source call and period when the user asks how it was computed.
- If a call failed or a metric is unavailable, say so in one line in the data notes. Never estimate a missing number.
