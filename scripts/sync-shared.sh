#!/usr/bin/env bash
# Copies each shared/<file>.md into every skill whose SKILL.md links references/<file>.md.
# Skills must stay self-contained (Agent Skills standard), so shared rules are copied, not linked.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

for skill_md in skills/*/SKILL.md; do
  skill_dir="$(dirname "$skill_md")"
  for shared in shared/*.md; do
    name="$(basename "$shared")"
    if grep -q "references/$name" "$skill_md"; then
      mkdir -p "$skill_dir/references"
      cp "$shared" "$skill_dir/references/$name"
      echo "synced $name -> $skill_dir/references/"
    elif [ -f "$skill_dir/references/$name" ]; then
      rm "$skill_dir/references/$name"
      echo "removed unused $skill_dir/references/$name"
    fi
  done
done
