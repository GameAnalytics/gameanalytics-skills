# Engines: detection and docs

Detect the engine from the project, then fetch its pages. The setup page is the URL below; fetch the configuration and event tracking pages with `docs_search` "<engine> configuration" and "<engine> event tracking", or from the links on the setup page.

All URLs start with `https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/`.

| Engine | Detect by | Setup page | Notes |
|---|---|---|---|
| Unity | `ProjectSettings/ProjectVersion.txt`, `Assets/`, `Packages/manifest.json` | `game-engine-sdks/unity` | Install through the package manager (OpenUPM scoped registry) or the `.unitypackage`. Keys, build, currencies, item types and custom dimension values live in the GameAnalytics Settings object; a GameAnalytics GameObject goes in the first scene. Native validation does not run in the editor |
| Unreal | `*.uproject`, `Source/*.Build.cs` | `game-engine-sdks/unreal` | Plugin from Fab or GitHub; enable it in the `.uproject` and add the module to `Build.cs` |
| Godot 4 | `project.godot` | `game-engine-sdks/godot` | GDExtension; enable the plugin in Project Settings |
| Roblox | `default.project.json` (Rojo), `wally.toml`, `.rbxl` or `.rbxlx` | `game-engine-sdks/roblox` | Rojo with Wally, or the Creator Store module. Server-side initialise |
| Flutter | `pubspec.yaml` with a `flutter` section | `game-engine-sdks/flutter` | `flutter pub add`; the web target also needs a script tag |
| GameMaker | `*.yyp` | `game-engine-sdks/gamemaker` | Extension from the marketplace or GitHub |
| Android (native) | `build.gradle` or `build.gradle.kts` with an Android plugin, no engine above | `platform-sdks/android` | Maven repository plus dependency; initialise with the activity |
| iOS (native) | `*.xcodeproj` or `Package.swift`, `Podfile`, no engine above | `platform-sdks/ios` | Swift Package Manager or CocoaPods. Show the App Tracking Transparency prompt before initialise if the app uses it |
| JavaScript / HTML5 | `package.json` with a web game framework (Phaser, PixiJS, Three.js, Babylon.js) or a plain `index.html` game | `open-source-sdks/javascript` | `npm install gameanalytics` or the script snippet |
| C++ | `CMakeLists.txt` without an engine | `open-source-sdks/cpp` | |
| C# (.NET, non-Unity) | `*.csproj` without Unity | `open-source-sdks/c-sharp` | |

Not listed, or not sure: run `docs_search` with the engine name. If GameAnalytics has no SDK for it, the [Collection API](https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/api/setup) accepts events over HTTPS, signed with HMAC SHA-256 using the game's secret key. Treat that as a server-side integration and say so: a secret key must not ship in a web page's source.

## Order of calls, on every engine

1. Optional: enable info and verbose logging (development builds only).
2. Configure the build string.
3. Configure the custom user ID, if the game uses one.
4. Configure available resource currencies and item types.
5. Configure available custom dimension values (01, 02, 03).
6. Initialise with the game key and secret key.
7. Send events, only after initialise.

Configure calls after initialise are ignored or make initialise fail. If the plan uses custom dimensions, set the active value before initialise too, so it attaches to the first session.

## Where keys come from

Game key and secret key: GameAnalytics > the game's Game Settings. They are per game. The user enters them in the engine's settings or a config file the build reads. Do not ask for them in chat and do not hardcode them in a file you are about to show. Every client SDK ships the secret key inside the game, which is expected for GameAnalytics; still keep it out of public repositories when possible.
