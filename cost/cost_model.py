"""Monthly cost estimate for the AWS 3-tier reference architecture.

Reads unit prices (pricing.json) and usage scenarios (scenarios.json) and
prints a line-by-line monthly estimate as a Markdown table, most expensive
first. Prices are entered by hand; re-check them in the AWS Pricing
Calculator before relying on the result.
"""

import argparse
import json
from pathlib import Path

HOURS_PER_MONTH = 730  # AWS's own convention: 24 h x 365 days / 12 months
HERE = Path(__file__).resolve().parent


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def line_cost(price: dict, quantity: float) -> float:
    """Monthly cost of one line item. Hourly prices are scaled to a full month."""
    if quantity < 0:
        raise ValueError("quantity cannot be negative")
    hours = HOURS_PER_MONTH if price["unit"] == "hour" else 1
    return price["usd"] * quantity * hours


def estimate(scenario: dict, prices: dict):
    """Return ([(item, monthly_usd), ...], total_usd) for one scenario."""
    lines = []
    for entry in scenario["items"]:
        key = entry["price"]
        if key not in prices:
            raise KeyError(f"no price defined for '{key}'")
        lines.append((entry["item"], line_cost(prices[key], entry["quantity"])))
    return lines, sum(cost for _, cost in lines)


def as_markdown(name: str, lines, total: float) -> str:
    rows = [f"| {name} | USD / month | Share |", "|---|---:|---:|"]
    for item, cost in sorted(lines, key=lambda line: line[1], reverse=True):
        rows.append(f"| {item} | {cost:,.2f} | {cost / total:.0%} |")
    rows.append(f"| **Total** | **{total:,.2f}** | 100% |")
    return "\n".join(rows)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--scenario", default="all", help="scenario name, or 'all' (default)")
    p.add_argument("--prices", default=str(HERE / "pricing.json"))
    p.add_argument("--scenarios", default=str(HERE / "scenarios.json"))
    args = p.parse_args(argv)

    prices = load_json(args.prices)["prices"]
    scenarios = load_json(args.scenarios)
    names = list(scenarios) if args.scenario == "all" else [args.scenario]

    for name in names:
        lines, total = estimate(scenarios[name], prices)
        print(f"### {name}: {scenarios[name]['description']}\n")
        print(as_markdown(name, lines, total))
        print()


if __name__ == "__main__":
    main()
