"""Replay one historical SKU-warehouse case across all four horizons through the API and reconcile retained evidence.

Real-source execution is a human-run demonstration, not a research evaluation.
Inventory/advisory outputs are retained, not recomputed from the API response.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from contextlib import AbstractContextManager
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import math
from pathlib import Path
import platform
import random
from typing import Any

from fastapi.testclient import TestClient
import pandas as pd

from src.api.main import create_app
from src.data.validated_handoff import (
    PROJECT_DATA_VERSION,
    ValidatedProjection,
    read_validated_projection,
)
from src.decision_support.retained_cases import (
    DECISION_SUPPORT_MANIFEST_SHA256,
    DECISION_SUPPORT_RECORDS_SHA256,
    load_retained_case_bundle,
)
from src.forecasting.export import (
    DESTINATION,
    ORIGIN,
    RUN_ID,
    TRAINING_START,
    _json,
    _read_bound,
    _receipts,
)
from src.forecasting.paths import REPOSITORY, RepositoryLayout
from src.inventory_risk.forecast_handoff import ForecastHandoff, load_forecast_handoff
from src.inventory_risk.runner import PROVENANCE_SHA256

HISTORY_COLUMNS = ("Date", "SKU_ID", "Warehouse_ID", "Units_Sold")
TARGET_START = "2024-12-03"
HORIZONS = (1, 7, 14, 28)
OUTPUT_DIRECTORY = Path("research-materials/issue-214")
SCHEMA = "issue-214-worked-scenario-v1"


class ScenarioError(ValueError):
    """A failed demonstration stage, without a substitute result."""

    def __init__(self, reason_code: str, message: str):
        super().__init__(message)
        self.reason_code = reason_code


def _require(condition: bool, reason: str, message: str) -> None:
    if not condition:
        raise ScenarioError(reason, message)


def _bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _equal(left: Any, right: Any) -> bool:
    """Preserve JSON type distinctions such as false versus zero."""
    return _bytes(left) == _bytes(right)


def _number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _api_client(repository: Path) -> TestClient:
    return TestClient(create_app(repository=repository))


def _check_history_source(repository: Path, handoff: ForecastHandoff) -> None:
    """Bind the data provenance pin to the producer's hash-bound metadata."""
    layout = RepositoryLayout(repository)
    source = handoff.document["source"]
    payload = layout._owned_path(
        layout.run_directory(RUN_ID) / "run_manifest.json"
    ).read_bytes()
    _require(
        hashlib.sha256(payload).hexdigest() == source["run_manifest_sha256"],
        "source_unverified",
        "Producer manifest differs from the forecast source.",
    )
    manifest = _json(payload)
    bindings = _receipts(layout, manifest["files"])
    metadata = _json(
        _read_bound(
            layout, f"artifacts/forecasting/{RUN_ID}/run_metadata.json", bindings
        )
    )
    _require(
        metadata["validated_provenance_hash"] == PROVENANCE_SHA256,
        "source_unverified",
        "History provenance differs from the producer's source.",
    )


def select_case(bundle: dict[str, Any], seed: str) -> tuple[dict[str, Any], list[str]]:
    """Select a pair by identity from the retained roster, never by exposure outcome."""
    _require(
        isinstance(seed, str) and bool(seed.strip()),
        "invalid_seed",
        "Supply an explicit nonblank seed.",
    )
    pool = [
        case
        for case in bundle["records"]
        if type(case["horizon"]) is int
        and case["horizon"] == 7
        and case["prospective_record"]["analysis_inventory_state_available"] is True
        and case["prospective_record"]["forecast_input_status"] == "available"
        and case["record"]["inventory_risk_evidence"] is not None
    ]
    pool.sort(key=lambda case: case["assessment_id"])
    ids = [case["assessment_id"] for case in pool]
    _require(
        bool(pool) and len(ids) == len(set(ids)),
        "invalid_pool",
        "The eligible pair-selection pool is empty or duplicated.",
    )
    return deepcopy(random.Random(seed).choice(pool)), ids


def build_request(
    case: dict[str, Any], projection: ValidatedProjection
) -> dict[str, Any]:
    """Keep the selected pair's complete pre-origin history; never expose labels."""
    _require(
        projection.provenance_sha256 == PROVENANCE_SHA256
        and projection.scope["start_date"] == TRAINING_START
        and projection.scope["end_date"] == ORIGIN
        and projection.scope["columns"] == list(HISTORY_COLUMNS),
        "source_unverified",
        "History projection identity or scope differs.",
    )
    row = case["prospective_record"]
    _require(
        row["forecast_origin"] == ORIGIN,
        "identity_mismatch",
        "The retained origin differs.",
    )
    frame = projection.frame
    _require(
        set(frame.columns) == set(HISTORY_COLUMNS),
        "invalid_history",
        "Unexpected history columns.",
    )
    frame = frame.loc[
        (frame.SKU_ID == row["SKU_ID"]) & (frame.Warehouse_ID == row["Warehouse_ID"])
    ].copy()
    frame["Date"] = pd.to_datetime(frame.Date, errors="raise")
    frame = frame.sort_values("Date")
    expected = pd.date_range(TRAINING_START, ORIGIN, freq="D")
    _require(
        frame.Date.tolist() == expected.tolist(),
        "invalid_history",
        "History must cover every day from training start through origin exactly once.",
    )
    history = []
    for day, value in zip(frame.Date, frame.Units_Sold, strict=True):
        # .item() preserves strict type checks while accepting pandas/numpy scalars.
        number = value.item() if hasattr(value, "item") else value
        _require(
            type(number) is int and number >= 0,
            "invalid_history",
            "Demand must contain nonnegative whole integer units.",
        )
        history.append({"Date": day.strftime("%Y-%m-%d"), "Units_Sold": number})
    return {
        "SKU_ID": row["SKU_ID"],
        "Warehouse_ID": row["Warehouse_ID"],
        "forecast_origin": ORIGIN,
        "horizon": row["horizon"],
        "input_kind": "supplied_history",
        "history": history,
    }


def reconcile(
    response: dict[str, Any],
    request: dict[str, Any],
    case: dict[str, Any],
    handoff: ForecastHandoff,
) -> None:
    """An exact replay check; no tolerance, fallback or new inventory calculation."""
    horizon = request["horizon"]
    _require(
        type(horizon) is int and horizon in HORIZONS,
        "identity_mismatch",
        "Unsupported horizon.",
    )
    document = handoff.document
    prospective, record = case["prospective_record"], case["record"]
    forecasts = [
        r
        for r in document["forecasts"]
        if all(
            r[k] == request[k]
            for k in ("SKU_ID", "Warehouse_ID", "forecast_origin", "horizon")
        )
    ]
    producers = [r for r in document["producers"] if r["horizon"] == horizon]
    _require(
        len(forecasts) == len(producers) == 1,
        "source_unverified",
        "No unique matching forecast/producer exists.",
    )
    forecast, producer = forecasts[0], producers[0]
    expected = {
        "SKU_ID": request["SKU_ID"],
        "Warehouse_ID": request["Warehouse_ID"],
        "forecast_origin": ORIGIN,
        "horizon": horizon,
        "target_start_date": TARGET_START,
        "target_end_date": (
            date.fromisoformat(ORIGIN) + timedelta(days=horizon)
        ).isoformat(),
        "forecast_type": "next_day" if horizon == 1 else "cumulative_window",
        "model": producer["model"],
        "configuration_id": producer["configuration_id"],
        "model_source_run_id": document["source"]["run_id"],
        "manifest_reference": document["source"]["run_manifest_path"],
        "manifest_sha256": document["source"]["run_manifest_sha256"],
        "inference_schema": "forecast-inference-v1",
        "inference_mode": "request_time",
        "input_kind": "supplied_history",
        "status": "available",
        "producer_designation": "frozen_designated_producer",
        "unavailable_reasons": [],
    }
    for key, value in expected.items():
        _require(
            key in response and _equal(response[key], value),
            "reconciliation_failed",
            f"API field differs: {key}.",
        )
    for key in (
        "SKU_ID",
        "Warehouse_ID",
        "forecast_origin",
        "horizon",
        "target_start_date",
        "target_end_date",
        "model",
        "configuration_id",
    ):
        _require(
            _equal(prospective[key], forecast[key])
            and _equal(forecast[key], expected[key]),
            "reconciliation_failed",
            f"Retained field differs: {key}.",
        )
    for key, value in {
        "sku_id": request["SKU_ID"],
        "warehouse_id": request["Warehouse_ID"],
        "forecast_origin": ORIGIN,
        "forecast_horizon": f"{horizon}-day",
    }.items():
        _require(
            _equal(record[key], value),
            "reconciliation_failed",
            f"Advisory identity differs: {key}.",
        )
    _require(
        forecast["forecast_type"] == expected["forecast_type"]
        and forecast["unit"] == prospective["unit"] == "units",
        "reconciliation_failed",
        "Retained forecast meaning/units differ.",
    )
    for key in ("model_path", "model_hash", "preprocessor_path", "preprocessor_hash"):
        _require(
            _equal(response["provenance"][key], producer["model_reference"][key]),
            "reconciliation_failed",
            f"Producer reference differs: {key}.",
        )
    _require(
        response["provenance"]["input_sha256"]
        == hashlib.sha256(_bytes(request)).hexdigest(),
        "reconciliation_failed",
        "API input digest differs from this history.",
    )
    values = (
        response["forecast_quantity"],
        forecast["prediction"],
        prospective["prediction"],
        record["forecast_demand"],
    )
    _require(
        all(_number(value) for value in values),
        "reconciliation_failed",
        "Forecast quantities must be finite JSON numbers.",
    )
    _require(
        all(value == values[0] for value in values[1:]),
        "reconciliation_failed",
        f"Exact forecast replay differs: API={values[0]!r}; retained={values[1:]!r}. No retained evidence was substituted.",
    )
    _require(
        prospective["source_export_sha256"] == handoff.sha256,
        "source_unverified",
        "Retained projection uses another export.",
    )


def aligned_cases(
    bundle: dict[str, Any], anchor: dict[str, Any]
) -> list[dict[str, Any]]:
    """Require one retained case per horizon for the same selected pair/origin."""
    identity = anchor["prospective_record"]
    cases = []
    for horizon in HORIZONS:
        matches = [
            c
            for c in bundle["records"]
            if type(c["horizon"]) is int
            and c["horizon"] == horizon
            and all(
                _equal(c["prospective_record"][key], identity[key])
                for key in ("SKU_ID", "Warehouse_ID", "forecast_origin")
            )
        ]
        _require(
            len(matches) == 1,
            "identity_mismatch",
            f"No unique same-pair h{horizon} retained case.",
        )
        item = deepcopy(matches[0])
        row, record = item["prospective_record"], item["record"]
        if horizon == 28:
            _require(
                row["downstream_use_status"] == "not_approved_for_downstream_use"
                and row["downstream_use_reason"]
                == "28_day_downstream_use_requires_separate_approval"
                and record["inventory_risk_evidence"] is None
                and record["replenishment_recommendation"] is None,
                "unapproved_inventory",
                "h28 inventory/replenishment evidence must remain unavailable.",
            )
        else:
            _require(
                row["analysis_inventory_state_available"] is True
                and record["inventory_risk_evidence"] is not None,
                "source_unverified",
                f"h{horizon} scenario evidence is unavailable.",
            )
        cases.append(item)
    return cases


def load_observations(
    repository: Path, handoff: ForecastHandoff
) -> tuple[list[dict[str, Any]], str]:
    """Read existing hash-bound final observations; never regenerate outcomes."""
    layout = RepositoryLayout(repository)
    payload = layout._owned_path(
        layout.run_directory(RUN_ID) / "run_manifest.json"
    ).read_bytes()
    _require(
        hashlib.sha256(payload).hexdigest()
        == handoff.document["source"]["run_manifest_sha256"],
        "source_unverified",
        "Observation parent manifest differs.",
    )
    bindings = _receipts(layout, _json(payload)["files"])
    raw = _read_bound(
        layout, f"artifacts/forecasting/{RUN_ID}/observations.json", bindings
    )
    rows = _json(raw)
    _require(
        isinstance(rows, list), "source_unverified", "Observations must be a list."
    )
    return rows, hashlib.sha256(raw).hexdigest()


def retrospective_comparison(
    responses: list[dict[str, Any]], observations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Select four targets from the parsed observation list after forecasting."""
    rows = []
    for response in responses:
        matching = [
            row
            for row in observations
            if all(
                _equal(row[key], response[key])
                for key in ("SKU_ID", "Warehouse_ID", "horizon")
            )
        ]
        _require(
            len(matching) == 1,
            "source_unverified",
            "No unique matching actual-sales total.",
        )
        actual = matching[0]["observed_target"]
        _require(
            _number(actual) and actual >= 0 and actual == int(actual),
            "source_unverified",
            "Actual sales must be nonnegative whole units.",
        )
        error = response["forecast_quantity"] - actual
        rows.append(
            {
                "horizon": response["horizon"],
                "target_start_date": response["target_start_date"],
                "target_end_date": response["target_end_date"],
                "forecast_quantity": response["forecast_quantity"],
                "actual_units_sold": actual,
                "signed_error_prediction_minus_actual": error,
                "absolute_error": abs(error),
                "absolute_percentage_error": None
                if actual == 0
                else abs(error) / actual * 100,
                "percentage_error_unavailable_reason": "actual_sales_zero"
                if actual == 0
                else None,
            }
        )
    return rows


def _output_path(repository: Path, output: Path) -> Path:
    base = repository / OUTPUT_DIRECTORY
    candidate = output if output.is_absolute() else repository / output
    _require(
        base.resolve() == base
        and candidate.resolve().is_relative_to(base)
        and candidate.suffix == ".json",
        "invalid_output",
        "Write a JSON trace under research-materials/issue-214 without symlink redirection.",
    )
    # Resolve each component so even a symlink within the permitted tree is refused.
    for part in (candidate, *candidate.parents):
        if part == repository:
            break
        _require(
            not part.is_symlink(),
            "invalid_output",
            "Output paths cannot contain symlinks.",
        )
    _require(
        not candidate.exists(),
        "output_exists",
        "Refusing to overwrite an existing trace.",
    )
    return candidate


def _environment() -> dict[str, str]:
    result = {"python": platform.python_version()}
    for name in ("pandas", "numpy", "fastapi", "lightgbm", "xgboost"):
        try:
            result[name] = version(name)
        except PackageNotFoundError:
            result[name] = "not_installed"
    return result


def run_scenario(
    *,
    seed: str,
    output: Path,
    repository: Path = REPOSITORY,
    case_loader: Callable[[Path], dict[str, Any]] = load_retained_case_bundle,
    forecast_loader: Callable[[Path], ForecastHandoff] = load_forecast_handoff,
    history_reader: Callable[..., ValidatedProjection] = read_validated_projection,
    client_factory: Callable[[Path], AbstractContextManager[Any]] = _api_client,
    observation_loader: Callable[
        [Path, ForecastHandoff], tuple[list[dict[str, Any]], str]
    ] = load_observations,
) -> dict[str, Any]:
    """Reconcile four API predictions before reading retrospective comparison values."""
    repository = repository.resolve()
    stage = "output_validation"
    try:
        destination = _output_path(repository, output)
        stage = "retained_source"
        bundle = case_loader(repository)
        stage = "case_selection"
        case, ids = select_case(bundle, seed)
        stage = "forecast_source"
        handoff = forecast_loader(repository / DESTINATION)
        stage = "producer_metadata"
        _check_history_source(repository, handoff)
        stage = "history_read"
        projection = history_reader(
            repository=repository,
            data_version=PROJECT_DATA_VERSION,
            columns=HISTORY_COLUMNS,
            start=TRAINING_START,
            end=ORIGIN,
            expected_provenance_sha256=PROVENANCE_SHA256,
        )
        stage = "case_alignment"
        cases = aligned_cases(bundle, case)
        stage = "history_validation"
        requests = [build_request(item, projection) for item in cases]
        responses = []
        stage = "api_startup"
        with client_factory(repository) as client:
            stage = "api_health"
            health = client.get("/health")
            _require(
                health.status_code == 200
                and health.json().get("status") == "ready"
                and all(
                    h in health.json().get("available_horizons", []) for h in HORIZONS
                ),
                "api_unavailable",
                "The saved producer service is unavailable.",
            )
            for request, retained in zip(requests, cases, strict=True):
                stage = "api_forecast"
                exchange = client.post("/forecasts", json=request)
                _require(
                    exchange.status_code == 200,
                    "api_request_failed",
                    f"h{request['horizon']} API returned HTTP {exchange.status_code}; no substitute result.",
                )
                response = exchange.json()
                stage = "reconciliation"
                reconcile(response, request, retained, handoff)
                responses.append(response)
        # Outcomes are read only after every prospective replay has reconciled.
        stage = "retrospective_comparison"
        observations, observation_hash = observation_loader(repository, handoff)
        comparison = retrospective_comparison(responses, observations)
        request = requests[0]
        stage = "trace_serialization"
        trace = {
            "schema": SCHEMA,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "execution": "in_process_TestClient",
            "scope": "four-horizon historical replay consistency with a separate retrospective actual-sales/error comparison; retained inventory/advisory evidence is not recomputed",
            "selection": {
                "seed": seed,
                "algorithm": "random.Random(seed).choice(sorted assessment IDs)",
                "pool": ids,
                "assessment_id": case["assessment_id"],
                "population": "purposive pair-selection roster with available inventory evidence; not representative",
            },
            "history": {
                "count": len(request["history"]),
                "start": TRAINING_START,
                "end": ORIGIN,
                "input_sha256_by_horizon": {
                    str(r["horizon"]): r["provenance"]["input_sha256"]
                    for r in responses
                },
                "validated_provenance_sha256": projection.provenance_sha256,
            },
            "sources": {
                "forecast_export_sha256": handoff.sha256,
                "decision_support_manifest_sha256": DECISION_SUPPORT_MANIFEST_SHA256,
                "decision_support_records_sha256": DECISION_SUPPORT_RECORDS_SHA256,
                "helper_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()
                ).hexdigest(),
            },
            "environment": _environment(),
            "forecast_results": [
                {"horizon": r["horizon"], "api_response": r, "retained_case": c}
                for r, c in zip(responses, cases, strict=True)
            ],
            "retrospective_comparison": {
                "role": "post-forecast explanatory comparison; never a prospective input or uncertainty estimate",
                "observations_sha256": observation_hash,
                "observations_path": f"artifacts/forecasting/{RUN_ID}/observations.json",
                "rows": comparison,
            },
            "unit_basis": "units, from retained export and documented Units_Sold forecast contract; the API has no unit field",
            "current_method_approval": {
                "status": "group_approved",
                "scope": "h1/h7/h14 fixed-origin, fixed-reorder-point, no-receipt scenario",
                "decision_date": "2026-10-12",
                "reported_date": "2026-10-23",
                "reference": "docs/decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record",
            },
            "interpretation_boundary": "Historical method labels are unchanged; h1/h7/h14 scenario approval excludes h28 inventory and does not establish source timing, optimal orders, managerial clearance or business benefit.",
        }
        payload = (
            json.dumps(trace, indent=2, sort_keys=True, allow_nan=False) + "\n"
        ).encode()
    except ScenarioError as exc:
        raise ScenarioError(exc.reason_code, f"[{stage}] {exc}") from exc
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        IndexError,
        OverflowError,
        RuntimeError,
    ) as exc:
        raise ScenarioError(
            "source_unverified",
            f"[{stage}] {type(exc).__name__}: {exc}",
        ) from exc
    created = False
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            created = True
            stream.write(payload)
    except OSError as exc:
        if created:
            try:
                destination.unlink(missing_ok=True)
            except OSError:
                pass  # Preserve the write failure; no success is reported.
        raise ScenarioError(
            "output_write_failed",
            f"[trace_write] Could not create the trace; existing files are never overwritten. {type(exc).__name__}: {exc}",
        ) from exc
    return trace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed",
        required=True,
        help="Choose and record before inspecting forecast/exposure outcomes.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="New JSON file under research-materials/issue-214.",
    )
    args = parser.parse_args(argv)
    try:
        trace = run_scenario(seed=args.seed, output=args.output)
    except ScenarioError as exc:
        parser.exit(1, f"{exc.reason_code}: {exc}\n")
    print(
        f"Reconciled horizons 1/7/14/28 for anchor {trace['selection']['assessment_id']}; trace: {args.output}"
    )
    print(
        "Historical replay only. Inventory/advisory evidence was retained, not recomputed."
    )
    print("Retrospective comparison (actual sales were not forecast inputs):")
    for row in trace["retrospective_comparison"]["rows"]:
        percentage = row["absolute_percentage_error"]
        percentage_text = (
            "unavailable (zero actual sales)"
            if percentage is None
            else f"{percentage:.2f}%"
        )
        print(
            f"h{row['horizon']}: forecast={row['forecast_quantity']:.6f}; "
            f"actual={row['actual_units_sold']:g}; "
            f"absolute_error={row['absolute_error']:.6f}; APE={percentage_text}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
