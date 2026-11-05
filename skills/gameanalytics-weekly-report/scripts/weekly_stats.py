#!/usr/bin/env python3
"""Weekly KPI statistics for the gameanalytics-weekly-report skill.

Reads GameAnalytics MCP query results (raw responses or {date: value} maps) and
prints week-on-week changes, trend anomalies and top movers as JSON or markdown.
Standard library only. See references/anomaly-method.md for the input format.
"""

import argparse
import datetime as dt
import json
import math
import sys

FIELDS = {
    "user_unique": "user_unique",
    "new_users": "new_users",
    "revenue": "sum",
    "ilrd_revenue": "sum",
    "paying_users": "paying_users",
    "session_unique": "session_unique",
    "session_length": "mean",
    "wau": "user_unique",
    "arppu": "arppu",
    "d1": "retention",
    "d7": "retention",
}

FLOORS = {"users": 100, "retention": 200, "money": 30}
SLICE_MIN_SHARE = 0.02
SLICE_MIN_COUNT = 100
ECHO_BAND = 0.05
TOP_MOVERS = 3

KPIS = [
    ("wau", "WAU", "count", "users"),
    ("dau", "DAU (average)", "count", "users"),
    ("new_users", "New users", "count", "users"),
    ("d1", "D1 retention", "rate", "retention"),
    ("d7", "D7 retention", "rate", "retention"),
    ("revenue", "IAP revenue", "money", "money"),
    ("ad_revenue", "Ad revenue", "money", "users"),
    ("arpdau", "ARPDAU", "per_user", "money"),
    ("arppu", "ARPPU", "money", "money"),
    ("conversion", "Conversion", "rate", "money"),
    ("sessions_per_user", "Sessions per user", "ratio", "users"),
    ("session_length", "Avg session length", "seconds", "users"),
]

BREAKDOWN_FIELDS = {"user_unique": "user_unique", "new_users": "new_users", "revenue": "sum"}
BREAKDOWN_LABELS = {"user_unique": "Active users", "new_users": "New users", "revenue": "IAP revenue"}
DIMENSION_LABELS = {"country_code": "country", "platform": "platform"}


def parse_date(value):
    return dt.date.fromisoformat(str(value)[:10])


def day_range(start, days):
    return [start + dt.timedelta(days=i) for i in range(days)]


def _rows(obj):
    """Flatten tool results into rows of {timestamp, result} or {timestamp, event}.

    The MCP returns three shapes: single-game timeseries as {"visualisation": {"items": [{date, value}]}},
    group and multi-game queries as {"result": [{timestamp, result}]}, split queries as {"result": [{timestamp, event}]}.
    """
    if isinstance(obj, dict):
        vis = obj.get("visualisation")
        if isinstance(vis, dict) and isinstance(vis.get("items"), list):
            return [{"timestamp": i["date"], "value": i.get("value")} for i in vis["items"]]
        if isinstance(obj.get("result"), list):
            return obj["result"]
        return []
    if isinstance(obj, list):
        rows = []
        for item in obj:
            if isinstance(item, dict) and "timestamp" in item:
                rows.append(item)
            elif isinstance(item, dict) and "date" in item:
                rows.append({"timestamp": item["date"], "value": item.get("value")})
            else:
                rows.extend(_rows(item))
        return rows
    return []


def _is_date_map(obj):
    return isinstance(obj, dict) and not ({"result", "visualisation"} & set(obj))


def normalize_series(obj, field):
    """Return {date: float} from a {date: value} map, [{date, value}] rows or raw tool results."""
    if obj is None:
        return {}
    if _is_date_map(obj):
        return {parse_date(k): float(v) for k, v in obj.items() if v is not None}
    out = {}
    for row in _rows(obj):
        if "value" in row:
            value = row["value"]
        else:
            payload = row.get("result") if isinstance(row.get("result"), dict) else row.get("event")
            value = payload.get(field) if isinstance(payload, dict) else None
        if value is not None:
            out[parse_date(row["timestamp"])] = float(value)
    return out


def normalize_breakdown(obj, dimension, field, this_start, prev_start):
    """Return ({value: this_week}, {value: prev_week}) from {"this", "prev"} maps or raw group responses."""
    if isinstance(obj, dict) and "this" in obj and "prev" in obj:
        return ({k: float(v) for k, v in obj["this"].items()},
                {k: float(v) for k, v in obj["prev"].items()})
    weeks = {this_start: {}, prev_start: {}}
    for row in _rows(obj):
        day = parse_date(row["timestamp"])
        bucket = this_start if this_start <= day < this_start + dt.timedelta(days=7) else (
            prev_start if prev_start <= day < this_start else None)
        if bucket is None:
            continue
        items = row.get("result") if isinstance(row.get("result"), list) else [row.get("event")]
        for item in items:
            if not isinstance(item, dict):
                continue
            key = item.get(dimension)
            if key is None or item.get(field) is None:
                continue
            key = str(key)
            weeks[bucket][key] = weeks[bucket].get(key, 0.0) + float(item[field])
    return weeks[this_start], weeks[prev_start]


def _sum_window(series, days):
    vals = [series.get(d) for d in days]
    if any(v is None for v in vals):
        return None
    return sum(vals)


def _div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def weekly_values(data, week_start, weeks=8):
    """Return {kpi: [value for week -7 .. 0]} and {family: [floor basis per week]}."""
    daily = {k: normalize_series(v, FIELDS.get(k, k)) for k, v in data.get("daily", {}).items()}
    weekly = {k: normalize_series(v, FIELDS.get(k, k)) for k, v in data.get("weekly", {}).items()}
    retention = {k: normalize_series(v, FIELDS.get(k, k)) for k, v in data.get("retention", {}).items()}
    for key, series in retention.items():
        if series and max(series.values()) > 1:
            retention[key] = {d: v / 100 for d, v in series.items()}
    dau, new, rev, ilrd = (daily.get(k, {}) for k in ("user_unique", "new_users", "revenue", "ilrd_revenue"))
    payers, sessions, length = (daily.get(k, {}) for k in ("paying_users", "session_unique", "session_length"))

    values = {key: [] for key, *_ in KPIS}
    basis = {"users": [], "money": [], "retention_d1": [], "retention_d7": []}
    windows = {"d1": None, "d7": None}
    for k in range(-(weeks - 1), 1):
        start = week_start + dt.timedelta(days=7 * k)
        days = day_range(start, 7)
        dau_sum = _sum_window(dau, days)
        rev_sum = _sum_window(rev, days)
        pay_sum = _sum_window(payers, days)
        sess_sum = _sum_window(sessions, days)
        length_weighted = None
        if sess_sum and all(length.get(d) is not None and sessions.get(d) is not None for d in days):
            length_weighted = sum(length[d] * sessions[d] for d in days)

        values["wau"].append(weekly.get("wau", {}).get(start))
        values["dau"].append(_div(dau_sum, 7))
        values["new_users"].append(_sum_window(new, days))
        values["revenue"].append(rev_sum)
        values["ad_revenue"].append(_sum_window(ilrd, days))
        values["arpdau"].append(_div(rev_sum, dau_sum))
        values["arppu"].append(weekly.get("arppu", {}).get(start))
        values["conversion"].append(_div(pay_sum, dau_sum))
        values["sessions_per_user"].append(_div(sess_sum, dau_sum))
        values["session_length"].append(_div(length_weighted, sess_sum))
        basis["users"].append(_div(dau_sum, 7))
        basis["money"].append(_div(pay_sum, 7))

        for key, shift in (("d1", 1), ("d7", 7)):
            cohort = day_range(start - dt.timedelta(days=shift), 7)
            weights = _sum_window(new, cohort)
            rates = [retention.get(key, {}).get(d) for d in cohort]
            if weights and all(r is not None for r in rates):
                values[key].append(sum(rates[i] * new[d] for i, d in enumerate(cohort)) / weights)
            else:
                values[key].append(None)
            basis[f"retention_{key}"].append(_div(weights, 7))
            if k == 0:
                windows[key] = (cohort[0].isoformat(), cohort[-1].isoformat())
    return values, basis, windows


def linear_trend(ys):
    """Fit y = a + b*x on x = 0..n-1; return (prediction at x = n, residual standard deviation)."""
    n = len(ys)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    ssr = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    sd = math.sqrt(ssr / (n - 2)) if n > 2 else 0.0
    return a + b * n, sd


def detect_anomaly(series, thin):
    """Weekly-trend z-score on the prior weeks; falls back to a 20% week-on-week rule."""
    actual = series[-1]
    prior = [v for v in series[:-1] if v is not None]
    result = {"method": None, "expected": None, "z": None, "deviation_pct": None,
              "flagged": False, "direction": None}
    if actual is None:
        return result
    if len(prior) >= 4:
        expected, sd = linear_trend(prior)
        if sd > 0 and expected != 0:
            z = (actual - expected) / sd
            dev = (actual - expected) / abs(expected)
            result.update(method="trend-z", expected=expected, z=z, deviation_pct=dev)
            result["flagged"] = (abs(z) >= 2 and abs(dev) >= 0.10) or (abs(z) >= 4 and abs(dev) >= 0.03)
    if result["method"] is None:
        prev = series[-2] if len(series) > 1 else None
        if prev:
            dev = (actual - prev) / abs(prev)
            result.update(method="wow-20", expected=prev, deviation_pct=dev, flagged=abs(dev) >= 0.20)
    if thin:
        result["flagged"] = False
    if result["deviation_pct"] is not None:
        result["direction"] = "up" if result["deviation_pct"] > 0 else "down"
    return result


def floor_family(key, family):
    if family == "retention":
        return f"retention_{key}"
    return family


def compute_kpis(data, previous=None):
    week_start = parse_date(data["week_start"])
    values, basis, windows = weekly_values(data, week_start)
    prev_flags = {}
    if previous:
        for item in previous.get("kpis", []):
            if item.get("anomaly", {}).get("flagged"):
                prev_flags[item["key"]] = item["anomaly"].get("direction")
    out = []
    for key, label, unit, family in KPIS:
        series = values[key]
        this, prev = series[-1], series[-2]
        if key == "ad_revenue" and not any(series):
            continue
        fam = floor_family(key, family)
        floor_value = basis[fam][-1]
        floor_key = "retention" if family == "retention" else family
        thin = floor_value is not None and floor_value < FLOORS[floor_key]
        change_abs = None if this is None or prev is None else this - prev
        change_pct = _div(change_abs, abs(prev) if prev else None)
        anomaly = detect_anomaly(series, thin)
        anomaly["repeat"] = bool(anomaly["flagged"] and prev_flags.get(key) == anomaly["direction"])
        item = {
            "key": key, "label": label, "unit": unit, "this": this, "prev": prev,
            "change_abs": change_abs, "change_pct": change_pct, "thin": thin,
            "history": series, "anomaly": anomaly,
        }
        if key in windows and windows[key]:
            item["cohort_window"] = windows[key]
        out.append(item)
    return out


def compute_movers(data):
    week_start = parse_date(data["week_start"])
    prev_start = week_start - dt.timedelta(days=7)
    movers = {}
    for dimension, metrics in data.get("breakdowns", {}).items():
        movers[dimension] = {}
        for metric, raw in metrics.items():
            field = BREAKDOWN_FIELDS.get(metric, metric)
            this, prev = normalize_breakdown(raw, dimension, field, week_start, prev_start)
            movers[dimension][metric] = rank_movers(this, prev, count_metric=metric != "revenue")
    return movers


def rank_movers(this, prev, count_metric=True):
    total_this, total_prev = sum(this.values()), sum(prev.values())
    total_pct = _div(total_this - total_prev, total_prev)
    rows = []
    for key in set(this) | set(prev):
        t, p = this.get(key, 0.0), prev.get(key, 0.0)
        share = max(_div(t, total_this) or 0.0, _div(p, total_prev) or 0.0)
        if share < SLICE_MIN_SHARE:
            continue
        if count_metric and max(t, p) < SLICE_MIN_COUNT:
            continue
        pct = _div(t - p, p)
        if pct is not None and total_pct is not None and abs(pct - total_pct) < ECHO_BAND:
            continue
        expected = p * (1 + total_pct) if total_pct is not None else p
        rows.append({"value": key, "this": t, "prev": p, "change_abs": t - p,
                     "change_pct": pct, "vs_trend": t - expected, "share": share})
    up = sorted((r for r in rows if r["vs_trend"] > 0), key=lambda r: -r["vs_trend"])[:TOP_MOVERS]
    down = sorted((r for r in rows if r["vs_trend"] < 0), key=lambda r: r["vs_trend"])[:TOP_MOVERS]
    return {"total_this": total_this, "total_prev": total_prev, "total_change_pct": total_pct,
            "up": up, "down": down}


def build_report(data, previous=None):
    week_start = parse_date(data["week_start"])
    if week_start.weekday() != 0:
        raise ValueError(f"week_start {week_start} is not a Monday")
    iso = week_start.isocalendar()
    notes = []
    kpis = compute_kpis(data, previous)
    for item in kpis:
        if item["this"] is None:
            notes.append(f"{item['label']}: no complete data for the report week.")
        elif item["thin"]:
            notes.append(f"{item['label']}: below the volume floor, shown but not flagged.")
    return {
        "game": data.get("game"),
        "week": {
            "iso": f"{iso[0]}-W{iso[1]:02d}",
            "start": week_start.isoformat(),
            "end": (week_start + dt.timedelta(days=6)).isoformat(),
            "prev_start": (week_start - dt.timedelta(days=7)).isoformat(),
            "prev_end": (week_start - dt.timedelta(days=1)).isoformat(),
        },
        "kpis": kpis,
        "movers": compute_movers(data),
        "notes": notes,
    }


def fmt_value(value, unit):
    if value is None:
        return "n/a"
    if unit == "count":
        return f"{value:,.0f}"
    if unit == "money":
        return f"${value:,.2f}"
    if unit == "per_user":
        return f"${value:,.3f}" if abs(value) < 1 else f"${value:,.2f}"
    if unit == "rate":
        return f"{value * 100:.1f}%"
    if unit == "seconds":
        return f"{value / 60:.1f} min"
    return f"{value:,.2f}"


def fmt_change(item):
    if item["change_abs"] is None:
        return "n/a"
    if item["unit"] == "rate":
        return f"{item['change_abs'] * 100:+.1f} pp"
    if item["change_pct"] is None:
        return "n/a"
    return f"{item['change_pct'] * 100:+.1f}%"


def fmt_flag(item):
    if item["thin"]:
        return "thin"
    a = item["anomaly"]
    if not a["flagged"]:
        return ""
    return f"anomaly ({a['direction']}{', repeat' if a['repeat'] else ''})"


def to_markdown(report):
    lines = ["| KPI | This week | Last week | Change | Flag |", "|---|---|---|---|---|"]
    for item in report["kpis"]:
        label = item["label"]
        if item.get("cohort_window"):
            start, end = item["cohort_window"]
            label += f" (installs {start} to {end})"
        lines.append(f"| {label} | {fmt_value(item['this'], item['unit'])} | "
                     f"{fmt_value(item['prev'], item['unit'])} | {fmt_change(item)} | {fmt_flag(item)} |")

    lines += ["", "Movers (change beyond the game-wide trend):", ""]
    any_mover = False
    for dimension, metrics in report["movers"].items():
        for metric, m in metrics.items():
            rows = m["up"] + m["down"]
            if not rows:
                continue
            any_mover = True
            unit = "money" if metric == "revenue" else "count"
            total = "n/a" if m["total_change_pct"] is None else f"{m['total_change_pct'] * 100:+.1f}%"
            dim_label = DIMENSION_LABELS.get(dimension, dimension)
            lines += [f"{BREAKDOWN_LABELS.get(metric, metric)} by {dim_label} (game total {total})", "",
                      f"| {dim_label.capitalize()} | This week | Last week | Change | Vs game trend |",
                      "|---|---|---|---|---|"]
            for r in rows:
                pct = "new" if r["change_pct"] is None else f"{r['change_pct'] * 100:+.1f}%"
                vs = fmt_value(abs(r["vs_trend"]), unit)
                sign = "+" if r["vs_trend"] > 0 else "-"
                lines.append(f"| {r['value']} | {fmt_value(r['this'], unit)} | {fmt_value(r['prev'], unit)} | "
                             f"{pct} | {sign}{vs} |")
            lines.append("")
    if not any_mover:
        lines.append("No country or platform moved apart from the game-wide trend.")

    flagged = [i for i in report["kpis"] if i["anomaly"]["flagged"]]
    lines += ["", "Anomalies:", ""]
    if not flagged:
        lines.append("None flagged.")
    for item in flagged:
        a = item["anomaly"]
        if a["method"] == "trend-z":
            detail = (f"{fmt_value(item['this'], item['unit'])} against a trend of "
                      f"{fmt_value(a['expected'], item['unit'])} ({a['deviation_pct'] * 100:+.1f}%, z = {a['z']:.1f})")
        else:
            detail = (f"{fmt_value(item['this'], item['unit'])} against "
                      f"{fmt_value(a['expected'], item['unit'])} last week ({a['deviation_pct'] * 100:+.1f}%)")
        repeat = " Flagged last week too." if a["repeat"] else ""
        lines.append(f"- {item['label']}: {detail}.{repeat}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="JSON file with week_start, daily, weekly, retention and breakdowns")
    parser.add_argument("--previous", help="last week's JSON output, to mark repeated anomalies")
    parser.add_argument("--markdown", action="store_true", help="print markdown tables instead of JSON")
    parser.add_argument("--out", help="also write the JSON output to this file (the report sidecar)")
    args = parser.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    previous = None
    if args.previous:
        try:
            with open(args.previous, encoding="utf-8") as f:
                previous = json.load(f)
        except FileNotFoundError:
            print(f"note: previous report {args.previous} not found", file=sys.stderr)
    report = build_report(data, previous)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    print(to_markdown(report) if args.markdown else json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
