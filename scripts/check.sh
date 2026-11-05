#!/usr/bin/env bash
# Repo checks: skill frontmatter, synced shared references, links, banned dashes, JSON manifests, unit tests.
set -uo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
fail=0
err() { echo "FAIL: $*"; fail=1; }

for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json .mcp.json; do
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null || err "$f is not valid JSON"
done

for skill_md in skills/*/SKILL.md; do
  dir="$(dirname "$skill_md")"
  folder="$(basename "$dir")"
  python3 - "$skill_md" "$folder" <<'PY' || fail=1
import re, sys
path, folder = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    print(f"FAIL: {path} has no frontmatter"); sys.exit(1)
fm = {}
for line in m.group(1).splitlines():
    if ":" in line and not line.startswith(" "):
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
ok = True
name = fm.get("name", "")
desc = fm.get("description", "")
if name != folder:
    print(f"FAIL: {path} name '{name}' does not match folder '{folder}'"); ok = False
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
    print(f"FAIL: {path} name '{name}' is not lowercase-hyphenated within 64 characters"); ok = False
if not desc or len(desc) > 1024:
    print(f"FAIL: {path} description is empty or over 1024 characters ({len(desc)})"); ok = False
if ": " in desc or desc.startswith(("'", '"', "[", "{", ">", "|")):
    print(f"FAIL: {path} description must be a plain one-line YAML scalar with no ': '"); ok = False
if "Use when" not in desc and "Use this when" not in desc:
    print(f"FAIL: {path} description does not say when to use the skill"); ok = False
body_lines = text.count("\n")
if body_lines > 500:
    print(f"FAIL: {path} is {body_lines} lines; keep SKILL.md under 500 and move detail to references/"); ok = False
sys.exit(0 if ok else 1)
PY

  for shared in shared/*.md; do
    name="$(basename "$shared")"
    copy="$dir/references/$name"
    if grep -q "references/$name" "$skill_md"; then
      [ -f "$copy" ] || { err "$copy missing; run scripts/sync-shared.sh"; continue; }
      cmp -s "$shared" "$copy" || err "$copy differs from $shared; run scripts/sync-shared.sh"
    fi
  done

  for ref in $(grep -oE '\((references|scripts|assets)/[^)#]+\)' "$skill_md" | tr -d '()' | sort -u); do
    [ -e "$dir/$ref" ] || err "$skill_md links $ref, which does not exist"
  done
done

for md in $(find . -name "*.md" -not -path "./.git/*"); do
  for ref in $(grep -oE '\]\([^)#:]+\.(md|py|csv|json)\)' "$md" | sed -E 's/^\]\(//; s/\)$//' | sort -u); do
    [ -e "$(dirname "$md")/$ref" ] || err "$md links $ref, which does not exist"
  done
done

dash_hits="$(grep -rnI $'\xe2\x80\x94\|\xe2\x80\x93' --exclude-dir=.git . || true)"
[ -z "$dash_hits" ] || { echo "$dash_hits"; err "em or en dashes found"; }

python3 -m unittest discover -s tests -q 2>&1 | tail -3
[ "${PIPESTATUS[0]}" -eq 0 ] || err "unit tests failed"

if [ "$fail" -eq 0 ]; then echo "OK: all checks passed"; else exit 1; fi
