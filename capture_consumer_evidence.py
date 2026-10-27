"""Issue #203 helper: capture request-time consumer evidence from a running local API.

Run from the repository root while the API is running on 127.0.0.1:8000:

    .venv/bin/python capture_consumer_evidence.py --output research-materials/issue-203/consumer-evidence.json

Standard library only. It sends the four existing example files unchanged, plus
a few in-memory negative/changed requests, and checks the AS-01..AS-06 invariants
on what the API actually returned. It writes no repository file except the
evidence JSON under the ignored research-materials/ folder, and never trains,
evaluates or rewrites anything. The PASS/FAIL lines are technical checks only;
the acceptance decision stays with the human reviewer.

This helper is a local tool. Do not commit it unless the team asks for it.
"""

from __future__ import annotations

import argparse
import copy
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from importlib import metadata
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
EXPECTED_PRODUCERS = {
    1: ("lightgbm", "GBM018", "next_day"),
    7: ("lightgbm", "GBM011", "cumulative_window"),
    14: ("xgboost", "GBM022", "cumulative_window"),
    28: ("xgboost", "GBM003", "cumulative_window"),
}
RUN_ID = "final-20261003-02"
PROVENANCE_KEYS = {
    "model_path",
    "model_hash",
    "preprocessor_path",
    "preprocessor_hash",
    "input_sha256",
}
RETROSPECTIVE_KEYS = {
    "observed_target",
    "actual",
    "error",
    "abs_error",
    "wape",
    "mae",
    "rmse",
    "bias",
    "Demand_Forecast",
    "Inventory_Level",
}
PACKAGES = (
    "fastapi",
    "pydantic",
    "uvicorn",
    "numpy",
    "pandas",
    "scikit-learn",
    "lightgbm",
    "xgboost",
    "threadpoolctl",
)


def call(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"{}")


def canonical_input_sha256(payload: dict) -> str:
    """Recompute the API's input hash independently (same canonical form)."""
    history = sorted(payload["history"], key=lambda row: row["Date"])
    canonical = {
        "SKU_ID": payload["SKU_ID"],
        "Warehouse_ID": payload["Warehouse_ID"],
        "forecast_origin": payload["forecast_origin"],
        "horizon": payload["horizon"],
        "input_kind": payload.get("input_kind", "supplied_history"),
        "history": [
            {"Date": row["Date"], "Units_Sold": row["Units_Sold"]} for row in history
        ],
    }
    return hashlib.sha256(
        json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def all_keys(value) -> set[str]:
    if isinstance(value, dict):
        found = set(value)
        for item in value.values():
            found |= all_keys(item)
        return found
    if isinstance(value, list):
        return set().union(*(all_keys(item) for item in value)) if value else set()
    return set()


def check_success(payload: dict, status: int, body: dict) -> list[tuple[str, bool]]:
    horizon = payload["horizon"]
    origin = date.fromisoformat(payload["forecast_origin"])
    model, configuration, forecast_type = EXPECTED_PRODUCERS[horizon]
    start = date.fromisoformat(body.get("target_start_date", "1900-01-01"))
    end = date.fromisoformat(body.get("target_end_date", "1900-01-01"))
    quantity = body.get("forecast_quantity")
    provenance = body.get("provenance", {})
    return [
        ("HTTP 200", status == 200),
        (
            "AS-01 identity echoed unchanged",
            (body.get("SKU_ID"), body.get("Warehouse_ID"))
            == (payload["SKU_ID"], payload["Warehouse_ID"]),
        ),
        (
            "AS-02 origin kept; target start = origin + 1 (not the origin)",
            body.get("forecast_origin") == payload["forecast_origin"]
            and start == origin + timedelta(days=1)
            and start != origin,
        ),
        (
            "AS-03 inclusive window: end = origin + h, exactly h days",
            end == origin + timedelta(days=horizon) and (end - start).days + 1 == horizon,
        ),
        (
            "AS-04 horizon and forecast_type preserved",
            body.get("horizon") == horizon and body.get("forecast_type") == forecast_type,
        ),
        (
            "AS-04 28-day downstream limitation present",
            any("28-day" in text for text in body.get("limitations", [])),
        ),
        (
            "AS-05 designated producer and source run",
            (body.get("model"), body.get("configuration_id")) == (model, configuration)
            and body.get("model_source_run_id") == RUN_ID
            and body.get("producer_designation") == "frozen_designated_producer"
            and body.get("manifest_reference")
            == f"artifacts/forecasting/{RUN_ID}/run_manifest.json",
        ),
        (
            "AS-05 model/preprocessor/input provenance present",
            set(provenance) == PROVENANCE_KEYS,
        ),
        (
            "AS-05 input_sha256 matches independent recomputation",
            provenance.get("input_sha256") == canonical_input_sha256(payload),
        ),
        (
            "AS-06 no retrospective or inventory fields in response",
            not (all_keys(body) & RETROSPECTIVE_KEYS),
        ),
        (
            "request_time mode, available, no unavailable reasons",
            body.get("inference_mode") == "request_time"
            and body.get("status") == "available"
            and body.get("unavailable_reasons") == [],
        ),
        (
            "finite raw quantity",
            isinstance(quantity, (int, float)) and math.isfinite(quantity),
        ),
    ]


def run_git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        return f"unavailable: {error}"


def environment(example_paths: list[Path]) -> dict:
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "git_head": run_git("rev-parse", "HEAD"),
        "git_branch": run_git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_status_porcelain": run_git("status", "--porcelain"),
        "package_versions": versions,
        "example_file_sha256": {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in example_paths
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    root = (Path.cwd() / "research-materials").resolve()
    if not output.is_relative_to(root) or output == root:
        parser.exit(1, "Write evidence inside the ignored research-materials/ folder.\n")
    if output.exists():
        parser.exit(1, f"Evidence file already exists: {output}\n")

    paths = [
        Path(f"examples/forecast-api/forecast-{h}-day.json") for h in EXPECTED_PRODUCERS
    ]
    evidence: dict = {"environment": environment(paths), "requests": []}
    failures = 0

    status, body = call("GET", "/health")
    health_ok = status == 200 and body == {
        "status": "ready",
        "available_horizons": [1, 7, 14, 28],
        "unavailable_reasons": [],
    }
    evidence["health"] = {"status": status, "body": body, "ok": health_ok}
    print(f"{'PASS' if health_ok else 'FAIL'}  GET /health -> {status} {body}")
    failures += not health_ok

    originals = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        originals[payload["horizon"]] = payload
        status, body = call("POST", "/forecasts", payload)
        checks = check_success(payload, status, body)
        evidence["requests"].append(
            {
                "name": path.name,
                "status": status,
                "response": body,
                "checks": dict(checks),
            }
        )
        print(f"\n{path.name}: HTTP {status}, quantity={body.get('forecast_quantity')}")
        for label, ok in checks:
            print(f"  {'PASS' if ok else 'FAIL'}  {label}")
            failures += not ok

    # Changed history: same request with one supplied value increased in memory.
    changed = copy.deepcopy(originals[1])
    changed["history"][-1]["Units_Sold"] += 5
    status, body = call("POST", "/forecasts", changed)
    original_hash = evidence["requests"][0]["response"].get("provenance", {}).get(
        "input_sha256"
    )
    ok = (
        status == 200
        and body.get("provenance", {}).get("input_sha256")
        == canonical_input_sha256(changed)
        != original_hash
    )
    evidence["changed_history"] = {"status": status, "response": body, "ok": ok}
    print(
        f"\n{'PASS' if ok else 'FAIL'}  changed history -> new input_sha256; "
        f"quantity={body.get('forecast_quantity')}"
    )
    failures += not ok

    # Negative cases built in memory from the 7-day example; files are not changed.
    base = originals[7]
    negatives = []

    def variant(name, expected_status, expected_reason, change):
        payload = copy.deepcopy(base)
        change(payload)
        negatives.append((name, expected_status, expected_reason, payload))

    variant("unknown SKU", 422, "unknown_sku", lambda p: p.update(SKU_ID="SKU_UNKNOWN"))
    variant(
        "unknown warehouse",
        422,
        "unknown_warehouse",
        lambda p: p.update(Warehouse_ID="WH_UNKNOWN"),
    )
    variant("unsupported horizon 3", 422, "unsupported_horizon", lambda p: p.update(horizon=3))
    variant(
        "origin before saved-model boundary",
        422,
        "invalid_origin",
        lambda p: p.update(forecast_origin="2024-12-01"),
    )
    variant(
        "history after origin",
        422,
        "future_history",
        lambda p: p.update(forecast_origin="2025-01-27"),
    )
    variant(
        "extra observed_target field rejected",
        422,
        None,
        lambda p: p.update(observed_target=99),
    )
    variant("boolean horizon rejected", 422, None, lambda p: p.update(horizon=True))
    evidence["negative_requests"] = []
    print()
    for name, expected_status, expected_reason, payload in negatives:
        status, body = call("POST", "/forecasts", payload)
        detail = body.get("detail")
        reason = detail.get("reason_code") if isinstance(detail, dict) else None
        ok = (
            status == expected_status
            and (expected_reason is None or reason == expected_reason)
            and "forecast_quantity" not in json.dumps(body)
        )
        evidence["negative_requests"].append(
            {"name": name, "status": status, "reason_code": reason, "ok": ok}
        )
        print(f"{'PASS' if ok else 'FAIL'}  {name} -> {status} {reason or ''}")
        failures += not ok

    evidence["technical_failures"] = failures
    evidence["note"] = (
        "Technical checks only. Acceptance is the human reviewer's recorded decision."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(evidence, stream, indent=2, sort_keys=True)
        stream.write("\n")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"\nTechnical failures: {failures}")
    print(f"Evidence written to {output}")
    print(f"Evidence SHA-256: {digest}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
