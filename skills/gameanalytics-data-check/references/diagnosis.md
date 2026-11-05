# Diagnosis: symptom, likely cause, fix

Look up each FAIL and WARN here. Fetch the engine's SDK page with `docs_fetch` when a fix needs exact code; the [SDKs overview](https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/sdks-overview) links every engine.

First step for any data problem: enable the SDK's info and verbose logs, run a device build, and watch Realtime > Live Events in GameAnalytics. The Unity editor does not run the native SDK, so editor play mode proves nothing.

## The game is missing (check 2)

| Likely cause | Fix |
|---|---|
| The game key and secret key belong to another game, or were swapped | Copy both from the game's Game Settings in GameAnalytics and compare with the values in the build |
| The SDK never initialises | Confirm the initialize call runs on startup; look for the SDK's init log line |
| Only editor or simulator builds were run | Install a device build |
| A configure call runs after initialize and init fails | Move every configure call (build, currencies, item types, custom dimension values, user ID) before initialize |
| The device blocks the request | Test on another network; check for a firewall or proxy |

## The build is missing or misspelled (check 3)

| Likely cause | Fix |
|---|---|
| The build is configured after initialize | Call the SDK's configure-build method (or set the build in the Unity Settings object for each platform) before initialize |
| The build string differs from the one expected | Use the exact string that arrived, or fix the build setting; GameAnalytics treats `1.4.0`, `v1.4.0` and `1.4.0 ` as different builds |
| The build string is longer than 32 characters | Shorten it; longer values are cut |
| Builds from different platforms use different strings | Decide on one scheme per release, for example `1.4.0` everywhere |

## Adoption looks wrong (check 4)

| Symptom | Likely cause |
|---|---|
| Few users on the new build, many new installs on it | A phased rollout or slow store updates. Normal. |
| New installs keep arriving on the old build after 48 hours | The store still serves the old binary to some regions or devices, or the new binary does not set the build |

## Expected values are missing (check 5)

| Missing | Likely cause | Fix |
|---|---|---|
| A platform | The SDK is not included or not initialised in that platform's build target | Check the platform-specific setup on the engine's SDK page |
| A soft-launch country | No installs yet from that store region, or the store listing is not live there | Check store availability; recheck after a day |
| An unexpected country above 2% | Test devices, VPNs or a store region opened by mistake | Filter test users out in analysis; check store availability |
| An A/B test (`ab_id`) | Users are not enrolled yet, or the remote config ready callback is not awaited | Check the A/B test is running and the SDK fetches remote configs before reading them |
| An ad network (`ad_sdk_name`) | Ad event calls are missing for that network, or `ad_sdk_name` is not lowercase without spaces or underscores | Add ad events in the mediation callbacks; fix the name |
| An ILRD network | Impression-level ad revenue is not enabled for that mediation SDK | Enable the ILRD integration on the engine's ad revenue page |
| An attribution source (`install_publisher`) | The attribution integration is not connected, or the source only records on install day | Check the attribution setup; look at new users only |

## Event families dropped (check 6)

| Family | Likely cause | Fix |
|---|---|---|
| Purchases | The business event call was removed or moved; `amount` sent as a float instead of integer cents; `currency` not an ISO 4217 code | Restore the call after a successful purchase, amount in cents, currency like `USD` |
| Ads | Ad event calls missing from the new mediation callbacks | Re-add `show`, `clicked`, `failed_show` and `reward_received` calls |
| Ad revenue | ILRD integration removed or the mediation SDK updated | Re-enable the ILRD integration for the new mediation SDK version |
| Sessions | Session start or end no longer sent, for example after app lifecycle changes, or users drop out early | Check the SDK's session handling; compare session length to rule out a real gameplay change |
| Errors | The new build crashes or logs more errors | Read the error messages in AnalyticsIQ Health > Errors, filtered to the build |
