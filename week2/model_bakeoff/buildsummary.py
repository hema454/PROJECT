
import csv
from collections import defaultdict


def load_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize(rows: list[dict]) -> None:
    by_model = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)

    print("\n" + "=" * 90)
    print(f"{'MODEL':<40} {'AVG COST':>10} {'AVG LATENCY':>13} {'USABLE':>10}")
    print("=" * 90)

    for model, model_rows in by_model.items():
        costs = [float(r["cost_usd"]) for r in model_rows if r["cost_usd"] not in ("", None)]
        latencies = [float(r["latency_sec"]) for r in model_rows if r["latency_sec"] not in ("", None)]
        usable_count = sum(1 for r in model_rows if r["usable"].strip().upper() == "Y")
        total = len(model_rows)

        avg_cost = sum(costs) / len(costs) if costs else 0.0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        print(f"{model:<40} ${avg_cost:>8.5f} {avg_latency:>11.2f}s {usable_count:>7}/{total}")

    print("\n" + "=" * 90)
    print("FAILURES BY MODEL (prompts marked usable=N)")
    print("=" * 90)
    for model, model_rows in by_model.items():
        failed = [r["prompt_label"] for r in model_rows if r["usable"].strip().upper() == "N"]
        if failed:
            print(f"{model}: FAILED on -> {', '.join(failed)}")
        else:
            print(f"{model}: no failures recorded")


def main():
    all_rows = []
    try:
        all_rows += load_rows("results_openrouter.csv")
    except FileNotFoundError:
        print("results_openrouter.csv not found — run bakeoff_openrouter.py first.")
    try:
        all_rows += load_rows("results_ollama.csv")
    except FileNotFoundError:
        print("results_ollama.csv not found — run bakeoff_ollama.py first.")

    if not all_rows:
        return

    unfilled = [r for r in all_rows if r["usable"].strip() == ""]
    if unfilled:
        print(f"\nWARNING: {len(unfilled)} rows still have a blank 'usable' column.")
        print("Open the CSVs, read the 'answer' column, and fill in Y or N before trusting this summary.\n")

    summarize(all_rows)


if __name__ == "__main__":
    main()