"""tracker lanes -- share, risk, the 80% cut and each item's lane
(proposal 26, C-02; decisions D1-D4).

  tracker lanes LEDGER... [--project DIR] [--json]

For every non-terminal item:

  share  value weight (high 3, medium 2, low 1) x points, over the queue's total
  risk   impact x likelihood; at least 9 when the item routes restricted --
         money, user data, secrets, releases and every common-rules change,
         as the project's risk_paths and risk_always say (tools/tracker/risk.py)

In share order, items are Now until the cumulative share reaches 80%; the
item that crosses the line is Now too (D3). The tail goes by risk (D4):
6 and over Daily, 3-5 Weekly, 1-2 When touched; a tail item with no impact or
likelihood is Unscored, never guessed. Risk 9 and over is alone -- never
bundled -- in whichever lane. An item with no value (after the project's
value_defaults) or no points is listed as unsized and takes no share.

Exit codes: 0 printed, 2 could not read a ledger.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.tracker import ledger as L
from tools.tracker import route as ROUTE

WEIGHT = {"high": 3, "medium": 2, "low": 1}
CUT = 0.80
ALONE = 9


def _tail_lane(risk) -> str:
    if risk is None:
        return "Unscored"
    if risk >= 6:
        return "Daily"
    if risk >= 3:
        return "Weekly"
    return "When touched"


def lanes(queue: list[dict], project) -> dict:
    sized, unsized = [], []
    for order, item in enumerate(queue):
        if item.get("status") in L.TERMINAL_STATUSES:
            continue
        r = ROUTE.route(item, project)
        impact, likelihood = item.get("impact"), item.get("likelihood")
        risk = impact * likelihood if isinstance(impact, int) and isinstance(likelihood, int) else None
        if r["risk"] == "restricted":
            risk = max(risk or 0, ALONE)
        row = {"id": item.get("id"), "title": item.get("title"), "value": r["value"],
               "points": r["points"], "risk": risk, "risk_class": r["risk"],
               "alone": risk is not None and risk >= ALONE, "order": order}
        if r["value"] in WEIGHT and isinstance(r["points"], int):
            row["raw"] = WEIGHT[r["value"]] * r["points"]
            sized.append(row)
        else:
            unsized.append(row)
    total = sum(r["raw"] for r in sized)
    sized.sort(key=lambda r: (-r["raw"], r["order"]))
    before = 0.0
    for r in sized:
        r["share"] = r["raw"] / total if total else 0.0
        r["lane"] = "Now" if before < CUT else _tail_lane(r["risk"])
        before += r["share"]
        r["cumulative"] = before
    for r in sized + unsized:
        r.pop("order", None)
    return {"items": sized, "unsized": unsized, "total": total}


def table(result: dict) -> str:
    lines = [f"{'lane':<13} {'id':<7} {'share':>6} {'cum':>6} {'risk':>4}  title"]
    for r in result["items"]:
        risk = "-" if r["risk"] is None else str(r["risk"])
        alone = " (alone)" if r["alone"] else ""
        lines.append(f"{r['lane']:<13} {r['id']:<7} {r['share']:>6.1%} {r['cumulative']:>6.1%} "
                     f"{risk:>4}  {r['title']}{alone}")
    if result["unsized"]:
        lines.append("unsized: " + ", ".join(u["id"] for u in result["unsized"]))
    return "\n".join(lines)


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="tracker lanes", description=__doc__.splitlines()[0])
    ap.add_argument("ledgers", type=Path, nargs="+")
    ap.add_argument("--project", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    queue: list[dict] = []
    for path in args.ledgers:
        try:
            queue.extend(L.items(L.load(path)))
        except (OSError, ValueError) as exc:
            print(f"tracker lanes: {exc}", file=sys.stderr)
            return 2
    result = lanes(queue, args.project or ROUTE.project_of(args.ledgers[0]))
    print(json.dumps(result, ensure_ascii=False) if args.json else table(result))
    return 0
