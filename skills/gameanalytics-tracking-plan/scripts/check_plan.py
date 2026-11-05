#!/usr/bin/env python3
"""Validate a GameAnalytics tracking plan CSV against ID formats and daily limits.

Usage: check_plan.py tracking-plan.csv [--markdown]
Exits 1 when the plan has an error or breaks a hard limit. See references/naming-and-budget.md.
"""

import argparse
import csv
import json
import math
import re
import sys

PART_RE = re.compile(r"^[A-Za-z0-9 \-_.()!?]{1,64}$")
CURRENCY_RE = re.compile(r"^[A-Za-z]{1,64}$")
PLACEHOLDER_RE = re.compile(r"\{([A-Za-z0-9_]+)\}")
DYNAMIC_RE = re.compile(
    r"(^|_)(user|uid|userid|player_id|device|timestamp|time|date|uuid|guid|session_id|score|price|amount|"
    r"coord|coords|pos|position|x|y|z|seed|damage|duration|ms|seconds)($|_)",
    re.I,
)

CARDINALITY = {"design": (13500, 15000), "progression": (7200, 8000), "resource": (3600, 4000)}
EVENTS_PER_USER = (450, 500)
MAX_CURRENCIES = 20
MAX_ITEM_TYPES = 20
MAX_DIMENSION_VALUES = 20
MAX_DIMENSION_VALUE_LEN = 32
TYPES = {"design", "progression", "resource", "business", "ad", "error", "session",
         "custom_dimension_01", "custom_dimension_02", "custom_dimension_03"}
ENUMERATE_LIMIT = 200000


def parse_values(text):
    """Parse 'a=x|y; b=1..20' into {'a': ['x', 'y'], 'b': ['1', ..., '20']}."""
    out = {}
    for chunk in (text or "").split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError(f"values entry '{chunk}' is not name=values")
        name, raw = (s.strip() for s in chunk.split("=", 1))
        m = re.fullmatch(r"(\d+)\.\.(\d+)", raw)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            out[name] = [str(i) for i in range(lo, hi + 1)]
        else:
            out[name] = [v.strip() for v in raw.split("|") if v.strip()]
    return out


def expansions(template, values):
    names = PLACEHOLDER_RE.findall(template)
    count = math.prod(len(values.get(n, [])) for n in names) if names else 1
    return names, count


def sample_ids(template, values, names, count):
    """Yield every expanded ID when small; otherwise the first and last value of each placeholder."""
    if not names:
        yield template
        return
    if count <= ENUMERATE_LIMIT:
        combos = [[]]
        for n in names:
            combos = [c + [v] for c in combos for v in values[n]]
    else:
        combos = [[values[n][0] for n in names], [values[n][-1] for n in names]]
    for combo in combos:
        out = template
        for n, v in zip(names, combo):
            out = out.replace("{" + n + "}", v, 1)
        yield out


def check_row(row, line, problems, inventory):
    etype = (row.get("event_type") or "").strip().lower()
    template = (row.get("event_id") or "").strip()
    errors, warnings = problems["errors"], problems["warnings"]
    where = f"line {line} ({template or etype})"

    if etype not in TYPES:
        errors.append(f"{where}: unknown event_type '{etype}'")
        return 0
    try:
        values = parse_values(row.get("values"))
    except ValueError as exc:
        errors.append(f"{where}: {exc}")
        return 0

    per_user = (row.get("per_user_per_day") or "").strip()
    if etype not in {"custom_dimension_01", "custom_dimension_02", "custom_dimension_03"}:
        try:
            inventory["per_user"] += float(per_user or 0)
        except ValueError:
            errors.append(f"{where}: per_user_per_day '{per_user}' is not a number")

    if etype.startswith("custom_dimension"):
        dim_values = values.get("values", [])
        if not dim_values:
            errors.append(f"{where}: list the dimension's values as values=a|b|c")
        if len(dim_values) > MAX_DIMENSION_VALUES:
            errors.append(f"{where}: {len(dim_values)} values; a custom dimension allows {MAX_DIMENSION_VALUES}")
        for v in dim_values:
            if len(v) > MAX_DIMENSION_VALUE_LEN:
                errors.append(f"{where}: value '{v}' is over {MAX_DIMENSION_VALUE_LEN} characters")
        if etype in inventory["dimensions"]:
            errors.append(f"{where}: {etype} is defined twice")
        inventory["dimensions"].add(etype)
        return 0

    if etype in {"ad", "error", "session"}:
        return 0

    names, count = expansions(template, values)
    for n in names:
        if n not in values or not values[n]:
            errors.append(f"{where}: placeholder {{{n}}} has no values, so it is unbounded")
            return 0
        if DYNAMIC_RE.search(n):
            errors.append(f"{where}: placeholder {{{n}}} looks like a dynamic value; "
                          "put numbers in value, score or amount, and detail in custom fields")
    for n in values:
        if n not in names:
            warnings.append(f"{where}: values define '{n}', which the event_id does not use")

    parts = template.split(":")
    if etype == "design" and not 1 <= len(parts) <= 5:
        errors.append(f"{where}: a design event_id has 1 to 5 parts; this has {len(parts)}")
    if etype == "progression" and not 2 <= len(parts) <= 4:
        errors.append(f"{where}: a progression event_id is Start, Fail or Complete plus 1 to 3 tiers")
    if etype == "resource" and len(parts) != 4:
        errors.append(f"{where}: a resource event_id is Source|Sink:currency:itemType:itemId")
    if etype == "business" and len(parts) != 2:
        errors.append(f"{where}: a business event_id is itemType:itemId")

    seen_bad = set()
    for event_id in sample_ids(template, values, names, count):
        id_parts = event_id.split(":")
        for part in id_parts:
            if not PART_RE.match(part) and part not in seen_bad:
                seen_bad.add(part)
                errors.append(f"{where}: part '{part}' must be 1 to 64 of A-Z a-z 0-9 space - _ . ( ) ! ?")
        if etype == "progression" and id_parts[0] not in {"Start", "Fail", "Complete"}:
            if id_parts[0] not in seen_bad:
                seen_bad.add(id_parts[0])
                errors.append(f"{where}: progression must start with Start, Fail or Complete, not '{id_parts[0]}'")
        if etype == "resource" and len(id_parts) == 4:
            flow, currency, item_type = id_parts[0], id_parts[1], id_parts[2]
            if flow not in {"Source", "Sink"} and flow not in seen_bad:
                seen_bad.add(flow)
                errors.append(f"{where}: resource flow must be Source or Sink, not '{flow}'")
            if not CURRENCY_RE.match(currency) and currency not in seen_bad:
                seen_bad.add(currency)
                errors.append(f"{where}: currency '{currency}' must be letters only")
            inventory["currencies"].add(currency)
            inventory["item_types"].add(item_type)
        for part in id_parts:
            inventory["casing"].setdefault((etype, part.lower()), set()).add(part)

    if template in inventory["templates"]:
        warnings.append(f"{where}: the same event_id is defined twice")
    inventory["templates"].add(template)
    inventory["cardinality"][etype] = inventory["cardinality"].get(etype, 0) + count
    return count


def check_plan(rows):
    problems = {"errors": [], "warnings": []}
    inventory = {"per_user": 0.0, "currencies": set(), "item_types": set(), "dimensions": set(),
                 "templates": set(), "cardinality": {}, "casing": {}}
    for line, row in rows:
        check_row(row, line, problems, inventory)

    if len(inventory["currencies"]) > MAX_CURRENCIES:
        problems["errors"].append(f"{len(inventory['currencies'])} resource currencies; plan for at most {MAX_CURRENCIES}")
    if len(inventory["item_types"]) > MAX_ITEM_TYPES:
        problems["errors"].append(f"{len(inventory['item_types'])} resource item types; plan for at most {MAX_ITEM_TYPES}")
    for variants in inventory["casing"].values():
        if len(variants) > 1:
            problems["warnings"].append(f"inconsistent casing: {', '.join(sorted(variants))} count as different IDs")

    budget = []
    for etype, (soft, hard) in CARDINALITY.items():
        used = inventory["cardinality"].get(etype, 0)
        status = "over limit" if used > hard else "over safe line" if used > soft else "ok"
        budget.append({"limit": f"{etype} IDs per day", "planned": used, "safe_line": soft, "limit_value": hard,
                       "status": status})
    soft, hard = EVENTS_PER_USER
    used = inventory["per_user"]
    status = "over limit" if used > hard else "over safe line" if used > soft else "ok"
    budget.append({"limit": "events per user per day", "planned": used, "safe_line": soft, "limit_value": hard,
                   "status": status})
    for row in budget:
        if row["status"] == "over limit":
            problems["errors"].append(f"{row['limit']}: {row['planned']:,.0f} breaks the limit of {row['limit_value']:,}")
        elif row["status"] == "over safe line":
            problems["warnings"].append(f"{row['limit']}: {row['planned']:,.0f} is over the safe line of {row['safe_line']:,}")

    return {
        "ok": not problems["errors"],
        "errors": problems["errors"],
        "warnings": problems["warnings"],
        "budget": budget,
        "currencies": sorted(inventory["currencies"]),
        "item_types": sorted(inventory["item_types"]),
    }


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = {"event_type", "event_id", "values", "per_user_per_day"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"CSV is missing columns: {', '.join(sorted(missing))}")
        return [(i + 2, row) for i, row in enumerate(reader)]


def to_markdown(result):
    lines = ["| Limit | Planned | Safe line | Limit | Status |", "|---|---|---|---|---|"]
    for row in result["budget"]:
        lines.append(f"| {row['limit']} | {row['planned']:,.0f} | {row['safe_line']:,} | {row['limit_value']:,} | {row['status']} |")
    lines.append("")
    lines.append(f"Resource currencies ({len(result['currencies'])}): {', '.join(result['currencies']) or 'none'}")
    lines.append(f"Resource item types ({len(result['item_types'])}): {', '.join(result['item_types']) or 'none'}")
    for title, key in (("Errors", "errors"), ("Warnings", "warnings")):
        lines += ["", f"{title}:"]
        lines += [f"- {p}" for p in result[key]] or ["- none"]
    lines += ["", "Result: " + ("PASS" if result["ok"] else "FAIL")]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)
    result = check_plan(read_rows(args.csv))
    print(to_markdown(result) if args.markdown else json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
