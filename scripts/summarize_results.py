#!/usr/bin/env python3
"""Summarise k6 summary-export files and resource samples as markdown tables.

Usage:
    python3 scripts/summarize_results.py results/exp-01-baseline [more dirs ...]

Runs of one configuration are grouped by file name (<config>-r<N>.json). For
every metric the table shows the mean over repetitions and the min-max range.
"""

import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RUN_FILE = re.compile(r"^(?P<config>.+)-r(?P<rep>\d+)\.json$")


def metric(data: dict, name: str, stat: str):
    """Read one statistic; works for flat and nested ("values") k6 exports."""
    entry = data.get("metrics", {}).get(name, {})
    entry = entry.get("values", entry)
    return entry.get(stat)


def failed_rate(data: dict):
    rate = metric(data, "http_req_failed", "rate")
    if rate is None:
        rate = metric(data, "http_req_failed", "value")
    return rate


def fmt(values: list[float], digits: int = 1) -> str:
    values = [v for v in values if v is not None]
    if not values:
        return "-"
    mean = statistics.mean(values)
    if len(values) == 1 or min(values) == max(values):
        return f"{mean:.{digits}f}"
    return f"{mean:.{digits}f} ({min(values):.{digits}f}-{max(values):.{digits}f})"


def parse_resources(path: Path) -> dict[str, dict[str, list[float]]]:
    """Return {pod_prefix: {"cpu": [...], "mem": [...]}} from a samples file."""
    pods: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"cpu": [], "mem": []}
    )
    for line in path.read_text().splitlines():
        _, _, rest = line.partition(" ")
        for segment in rest.split(";"):
            parts = segment.split()
            if len(parts) != 3:
                continue
            name, cpu, mem = parts
            if not (cpu.endswith("m") and mem.endswith("Mi")):
                continue
            prefix = name.split("-")[0]
            pods[prefix]["cpu"].append(float(cpu[:-1]))
            pods[prefix]["mem"].append(float(mem[:-2]))
    return pods


def summarise(directory: Path) -> None:
    runs: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(directory.glob("*.json")):
        match = RUN_FILE.match(path.name)
        if match:
            runs[match["config"]].append(path)

    if not runs:
        print(f"_no k6 summary files in {directory}_\n")
        return

    print(f"### {directory}\n")
    header = ["Config", "Runs", "Avg ms", "P95 ms", "P99 ms", "Max ms"]
    header += ["Req/s", "Failed %", "Tokens/s"]
    print("| " + " | ".join(header) + " |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    resource_rows = []
    for config, files in runs.items():
        data = [json.loads(f.read_text()) for f in files]
        failed = [failed_rate(d) for d in data]
        failed = [None if v is None else v * 100 for v in failed]
        print(
            f"| {config} | {len(files)} "
            f"| {fmt([metric(d, 'http_req_duration', 'avg') for d in data], 2)} "
            f"| {fmt([metric(d, 'http_req_duration', 'p(95)') for d in data], 2)} "
            f"| {fmt([metric(d, 'http_req_duration', 'p(99)') for d in data], 2)} "
            f"| {fmt([metric(d, 'http_req_duration', 'max') for d in data], 1)} "
            f"| {fmt([metric(d, 'http_reqs', 'rate') for d in data], 2)} "
            f"| {fmt(failed, 2)} "
            f"| {fmt([metric(d, 'llm_tokens_per_second', 'avg') for d in data], 2)} |"
        )

        per_pod: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: {"cpu": [], "mem": []}
        )
        for f in files:
            res = f.with_name(f.stem + ".resources.txt")
            if res.exists():
                for pod, series in parse_resources(res).items():
                    per_pod[pod]["cpu"].append(statistics.mean(series["cpu"]))
                    per_pod[pod]["mem"].append(statistics.mean(series["mem"]))
        for pod, series in sorted(per_pod.items()):
            cpu, mem = fmt(series["cpu"], 0), fmt(series["mem"], 0)
            resource_rows.append(f"| {config} | {pod} | {cpu} | {mem} |")

    if resource_rows:
        print("\n| Config | Pod | CPU m (mean of run means) | Memory Mi |")
        print("| --- | --- | --- | --- |")
        print("\n".join(resource_rows))
    print()


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        summarise(Path(arg))


if __name__ == "__main__":
    main()
