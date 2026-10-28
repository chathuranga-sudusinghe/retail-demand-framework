"""Capture and verify Issue #203 request-time forecast consumer evidence.

Run from the repository root with the configured environment, for example:

    .venv/bin/python capture_consumer_evidence.py \
        --output research-materials/issue-203/consumer-evidence-v2.json
    .venv/bin/python capture_consumer_evidence.py \
        --verify research-materials/issue-203/consumer-evidence-v2.json

Capture first records every request/response exchange (health, the four
synthetic horizon examples, a repeat request, the changed-history request and
the rejection-boundary requests). Each requirement outcome (AS-01 to AS-06,
plus the request-time contract, changed-history and rejection groups) is then
derived from assertions on those recorded exchanges; no outcome is written as
a constant. ``--verify`` re-derives the outcomes from the stored exchanges.

Evidence files are created exclusively: an existing file is never overwritten.

Scope: technical request-time consumer verification only. The evidence is not
formal forecast-producer approval and not independently reviewed source
verification; both remain pending under #179.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol

from fastapi.testclient import TestClient

from src.api.main import app

EVIDENCE_SCHEMA = "issue-203-consumer-evidence-v2"
DEFAULT_OUTPUT = Path("research-materials/issue-203/consumer-evidence-v2.json")
PREVIOUS_CAPTURE = Path("research-materials/issue-203/consumer-evidence.json")
DEFAULT_EXAMPLES_DIR = Path("examples/forecast-api")

HORIZONS: tuple[int, ...] = (1, 7, 14, 28)
SOURCE_RUN_ID = "final-20261003-02"
MANIFEST_REFERENCE = f"artifacts/forecasting/{SOURCE_RUN_ID}/run_manifest.json"
MODEL_ROOT = f"models/forecasting/{SOURCE_RUN_ID}/final"
SAVED_MODEL_BOUNDARY = date(2024, 12, 2)
PRODUCERS: dict[int, tuple[str, str]] = {
    1: ("lightgbm", "GBM018"),
    7: ("lightgbm", "GBM011"),
    14: ("xgboost", "GBM022"),
    28: ("xgboost", "GBM003"),
}
CHANGED_HISTORY_INCREMENT = 5
COLOMBO = timezone(timedelta(hours=5, minutes=30), "Asia/Colombo")

# Explicit response allowlist, identical to the ForecastResponse schema
# asserted in tests/test_forecast_api.py.
RESPONSE_FIELDS = frozenset(
    {
        "inference_schema",
        "inference_mode",
        "input_kind",
        "model_source_run_id",
        "manifest_reference",
        "manifest_sha256",
        "SKU_ID",
        "Warehouse_ID",
        "forecast_origin",
        "horizon",
        "target_start_date",
        "target_end_date",
        "forecast_type",
        "forecast_quantity",
        "model",
        "configuration_id",
        "producer_designation",
        "provenance",
        "status",
        "unavailable_reasons",
        "assumptions",
        "limitations",
    }
)
# Provenance key names as served by src/api/main.py.
PROVENANCE_FIELDS = frozenset(
    {
        "model_path",
        "model_hash",
        "preprocessor_path",
        "preprocessor_hash",
        "input_sha256",
    }
)
PROVENANCE_HASH_FIELDS = ("model_hash", "preprocessor_hash", "input_sha256")
# Retrospective, inventory and evaluation keys that must never appear (at any
# depth) in a request-time response. Compared case-insensitively.
FORBIDDEN_RESPONSE_KEYS = frozenset(
    key.lower()
    for key in (
        "observed_target",
        "Demand_Forecast",
        "Inventory_Level",
        "Reorder_Point",
        "Stockout_Flag",
        "Order_Quantity",
        "Supplier_Lead_Time_Days",
        "Units_Sold",
        "retrospective_margin",
        "predicted_margin",
        "exposure_state",
        "target_1_day",
        "target_7_day",
        "target_14_day",
        "target_28_day",
        "wape",
        "mae",
        "rmse",
        "bias",
        "error",
        "signed_error",
        "absolute_error",
    )
)
STABLE_CHANGED_HISTORY_FIELDS = (
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
    "forecast_type",
    "model",
    "configuration_id",
    "producer_designation",
    "model_source_run_id",
    "manifest_sha256",
)
STABLE_CHANGED_HISTORY_PROVENANCE = (
    "model_path",
    "model_hash",
    "preprocessor_path",
    "preprocessor_hash",
)

REQUIREMENTS: dict[str, str] = {
    "AS-01": "Identity echoed unchanged; unknown SKU/warehouse rejected explicitly",
    "AS-02": "Origin kept; target_start_date = origin + 1",
    "AS-03": "Inclusive window: target_end_date = origin + h, exactly h days",
    "AS-04": (
        "Horizon and forecast_type preserved; cumulative and 28-day limitation "
        "wording; unsupported horizon rejected"
    ),
    "AS-05": "Designated producer, saved model/preprocessor and input provenance",
    "AS-06": (
        "Exact response allowlist; no retrospective or inventory fields; such "
        "request fields rejected"
    ),
    "RT-CONTRACT": "Health ready; HTTP 200, available, finite quantity; files intact",
    "RT-CHANGED-HISTORY": (
        "Final-day Units_Sold +5 yields a new input_sha256 with the same producer"
    ),
    "RT-REJECTIONS": "HTTP 422 rejection boundaries without a substitute quantity",
}
AS_REQUIREMENTS = ("AS-01", "AS-02", "AS-03", "AS-04", "AS-05", "AS-06")
SCOPE_STATEMENTS = (
    "Technical request-time consumer verification under #203 only.",
    "Not formal forecast-producer approval; that remains pending under #179.",
    "Not independently reviewed source verification; that remains pending under #179.",
    "Synthetic demonstration inputs; no accuracy, research or inventory-use claim.",
)
_SHA256 = re.compile(r"[0-9a-f]{64}")
_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


class ResponseLike(Protocol):
    status_code: int

    def json(self) -> Any: ...


class ClientLike(Protocol):
    def get(self, url: str) -> ResponseLike: ...

    def post(self, url: str, *, json: Any) -> ResponseLike: ...


ClientFactory = Callable[[], AbstractContextManager[ClientLike]]


@dataclass(frozen=True)
class Check:
    check_id: str
    requirements: tuple[str, ...]
    description: str
    passed: bool
    observed: Any = None

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.check_id,
            "requirements": list(self.requirements),
            "description": self.description,
            "passed": self.passed,
            "observed": self.observed,
        }


@dataclass(frozen=True)
class RejectionCase:
    case_id: str
    requirements: tuple[str, ...]
    kind: str  # "domain" (reason_code expected) or "extra_field"
    expected: str
    description: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class GitState:
    revision: str
    clean: bool | None


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or len(value) != 10:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def find_forbidden_keys(obj: Any, path: str = "") -> list[str]:
    """Return every key path (any depth) whose name is a forbidden key."""
    found: list[str] = []
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_path = f"{path}.{key}" if path else str(key)
            if str(key).lower() in FORBIDDEN_RESPONSE_KEYS:
                found.append(key_path)
            found.extend(find_forbidden_keys(value, key_path))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            found.extend(find_forbidden_keys(item, f"{path}[{index}]"))
    return found


def contains_key(obj: Any, name: str) -> bool:
    if isinstance(obj, Mapping):
        return name in obj or any(contains_key(v, name) for v in obj.values())
    if isinstance(obj, list):
        return any(contains_key(item, name) for item in obj)
    return False


def dated_history(end: date, values: Sequence[int]) -> list[dict[str, Any]]:
    """Consecutive daily rows ending at ``end`` (inclusive)."""
    start = end - timedelta(days=len(values) - 1)
    return [
        {"Date": (start + timedelta(days=i)).isoformat(), "Units_Sold": value}
        for i, value in enumerate(values)
    ]


def _sorted_history(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        (dict(row) for row in payload["history"]), key=lambda row: str(row["Date"])
    )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


# --------------------------------------------------------------------------
# Request construction (in memory only; example files are never rewritten)
# --------------------------------------------------------------------------


def build_changed_history_request(base: Mapping[str, Any]) -> dict[str, Any]:
    """Copy ``base`` and add CHANGED_HISTORY_INCREMENT to the final day's Units_Sold."""
    payload = copy.deepcopy(dict(base))
    final_date = max(str(row["Date"]) for row in payload["history"])
    for row in payload["history"]:
        if str(row["Date"]) == final_date:
            row["Units_Sold"] += CHANGED_HISTORY_INCREMENT
    return payload


def build_rejection_cases(base: Mapping[str, Any]) -> list[RejectionCase]:
    """Derive every negative request from the valid 1-day example."""
    history = _sorted_history(base)
    values = [int(row["Units_Sold"]) for row in history]
    origin = date.fromisoformat(str(base["forecast_origin"]))

    def variant(**changes: Any) -> dict[str, Any]:
        payload = copy.deepcopy(dict(base))
        payload.update(changes)
        return payload

    before_boundary = SAVED_MODEL_BOUNDARY - timedelta(days=1)
    # One extra leading day, then drop a middle day: same row count, still ends
    # at the origin, but contains exactly one gap.
    padded = dated_history(origin, [values[0], *values])
    gapped = padded[: len(padded) // 2] + padded[len(padded) // 2 + 1 :]
    future_row = {
        "Date": (origin + timedelta(days=1)).isoformat(),
        "Units_Sold": values[-1],
    }

    rejections = ("RT-REJECTIONS",)
    return [
        RejectionCase(
            "unknown_sku",
            ("AS-01", *rejections),
            "domain",
            "unknown_sku",
            "SKU_ID unknown to the saved models",
            variant(SKU_ID="SKU_SYN_UNKNOWN"),
        ),
        RejectionCase(
            "unknown_warehouse",
            ("AS-01", *rejections),
            "domain",
            "unknown_warehouse",
            "Warehouse_ID unknown to the saved models",
            variant(Warehouse_ID="WH_SYN_UNKNOWN"),
        ),
        RejectionCase(
            "unsupported_horizon",
            ("AS-04", *rejections),
            "domain",
            "unsupported_horizon",
            "Integer horizon 3 is not one of 1/7/14/28",
            variant(horizon=3),
        ),
        RejectionCase(
            "invalid_origin",
            rejections,
            "domain",
            "invalid_origin",
            f"Origin {before_boundary.isoformat()} precedes the saved-model boundary",
            variant(
                forecast_origin=before_boundary.isoformat(),
                history=dated_history(before_boundary, values),
            ),
        ),
        RejectionCase(
            "future_history",
            rejections,
            "domain",
            "future_history",
            "History contains a day after the forecast origin",
            variant(history=[*history, future_row]),
        ),
        RejectionCase(
            "incomplete_history",
            rejections,
            "domain",
            "incomplete_history",
            "History ends one day before the forecast origin",
            variant(forecast_origin=(origin + timedelta(days=1)).isoformat()),
        ),
        RejectionCase(
            "invalid_history",
            rejections,
            "domain",
            "invalid_history",
            "History ends at the origin but has one missing day",
            variant(history=gapped),
        ),
        RejectionCase(
            "extra_observed_target",
            ("AS-06", *rejections),
            "extra_field",
            "observed_target",
            "Retrospective observed_target supplied as a request field",
            variant(observed_target=100),
        ),
        RejectionCase(
            "extra_Demand_Forecast",
            ("AS-06", *rejections),
            "extra_field",
            "Demand_Forecast",
            "Source Demand_Forecast supplied as a request field",
            variant(Demand_Forecast=100),
        ),
        RejectionCase(
            "extra_Inventory_Level",
            ("AS-06", *rejections),
            "extra_field",
            "Inventory_Level",
            "Inventory variable supplied as a request field",
            variant(Inventory_Level=100),
        ),
    ]


# --------------------------------------------------------------------------
# Collection: record raw exchanges only (no judgement here)
# --------------------------------------------------------------------------


def _response_body(response: ResponseLike) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _post(client: ClientLike, payload: Mapping[str, Any]) -> dict[str, Any]:
    request = copy.deepcopy(dict(payload))
    response = client.post("/forecasts", json=copy.deepcopy(request))
    return {
        "request": request,
        "http_status": response.status_code,
        "body": _response_body(response),
    }


def collect_exchanges(client: ClientLike, examples_dir: Path) -> dict[str, Any]:
    health = client.get("/health")
    record: dict[str, Any] = {
        "health": {"http_status": health.status_code, "body": _response_body(health)}
    }

    examples: list[dict[str, Any]] = []
    for horizon in HORIZONS:
        path = examples_dir / f"forecast-{horizon}-day.json"
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError(f"{path} does not contain a JSON object")
        exchange = _post(client, payload)
        examples.append(
            {
                "horizon": horizon,
                "file": path.as_posix(),
                "file_sha256_before": sha256_bytes(raw),
                **exchange,
            }
        )
    record["examples"] = examples

    base = examples[0]["request"]
    record["repeat_request"] = {"base_horizon": 1, **_post(client, base)}
    record["changed_history"] = {
        "base_horizon": 1,
        "units_sold_increment": CHANGED_HISTORY_INCREMENT,
        **_post(client, build_changed_history_request(base)),
    }
    record["rejections"] = [
        {"case": case.case_id, **_post(client, case.payload)}
        for case in build_rejection_cases(base)
    ]

    for entry in examples:
        entry["file_sha256_after"] = sha256_bytes(Path(entry["file"]).read_bytes())
    return record


# --------------------------------------------------------------------------
# Evaluation: derive checks from recorded exchanges
# --------------------------------------------------------------------------


def evaluate_health(health: Any) -> list[Check]:
    entry = _dict(health)
    body = _dict(entry.get("body"))
    ok = (
        entry.get("http_status") == 200
        and body.get("status") == "ready"
        and body.get("available_horizons") == list(HORIZONS)
        and body.get("unavailable_reasons") == []
    )
    return [
        Check(
            "health.ready",
            ("RT-CONTRACT",),
            "GET /health is HTTP 200 and ready for horizons [1, 7, 14, 28] "
            "with no unavailable reasons",
            ok,
            {"http_status": entry.get("http_status"), "body": entry.get("body")},
        )
    ]


def evaluate_forecast_exchange(horizon: int, entry: Mapping[str, Any]) -> list[Check]:
    request = _dict(entry.get("request"))
    status = entry.get("http_status")
    raw_body = entry.get("body")
    body = _dict(raw_body)
    provenance = _dict(body.get("provenance"))
    origin = parse_date(request.get("forecast_origin"))
    start = parse_date(body.get("target_start_date"))
    end = parse_date(body.get("target_end_date"))
    expected_model, expected_config = PRODUCERS[horizon]
    expected_prefix = f"{MODEL_ROOT}/{expected_model}/h{horizon}/{expected_config}/"
    limitations = body.get("limitations")
    limitation_text = (
        " ".join(item for item in limitations if isinstance(item, str)).lower()
        if isinstance(limitations, list)
        else ""
    )
    p = f"h{horizon}"
    checks: list[Check] = []

    def add(
        suffix: str,
        requirements: tuple[str, ...],
        description: str,
        passed: bool,
        observed: Any,
    ) -> None:
        checks.append(
            Check(f"{p}.{suffix}", requirements, description, bool(passed), observed)
        )

    # Request-time contract
    add(
        "example_file_unchanged",
        ("RT-CONTRACT",),
        "Example file bytes identical before and after capture",
        is_sha256(entry.get("file_sha256_before"))
        and entry.get("file_sha256_before") == entry.get("file_sha256_after"),
        {
            "before": entry.get("file_sha256_before"),
            "after": entry.get("file_sha256_after"),
        },
    )
    add(
        "request_horizon",
        ("RT-CONTRACT",),
        f"Example request asks for horizon {horizon}",
        request.get("horizon") == horizon
        and not isinstance(request.get("horizon"), bool),
        request.get("horizon"),
    )
    add(
        "http_200",
        ("RT-CONTRACT",),
        "HTTP 200 with a JSON object body",
        status == 200 and isinstance(raw_body, dict),
        status,
    )
    add(
        "available",
        ("RT-CONTRACT",),
        "status 'available' and empty unavailable_reasons",
        body.get("status") == "available" and body.get("unavailable_reasons") == [],
        {
            "status": body.get("status"),
            "unavailable_reasons": body.get("unavailable_reasons"),
        },
    )
    add(
        "inference_schema",
        ("RT-CONTRACT",),
        "inference_schema is forecast-inference-v1",
        body.get("inference_schema") == "forecast-inference-v1",
        body.get("inference_schema"),
    )
    add(
        "input_kind_echo",
        ("RT-CONTRACT",),
        "input_kind echoed from the request",
        body.get("input_kind") == request.get("input_kind", "supplied_history"),
        body.get("input_kind"),
    )
    add(
        "quantity_finite",
        ("RT-CONTRACT",),
        "forecast_quantity is a finite JSON number",
        is_finite_number(body.get("forecast_quantity")),
        body.get("forecast_quantity"),
    )

    # AS-01 identity
    add(
        "identity_echo",
        ("AS-01",),
        "SKU_ID and Warehouse_ID echoed unchanged",
        isinstance(request.get("SKU_ID"), str)
        and body.get("SKU_ID") == request.get("SKU_ID")
        and body.get("Warehouse_ID") == request.get("Warehouse_ID"),
        {"SKU_ID": body.get("SKU_ID"), "Warehouse_ID": body.get("Warehouse_ID")},
    )

    # AS-02 origin vs target start
    add(
        "origin_echo",
        ("AS-02",),
        "forecast_origin echoed unchanged",
        origin is not None
        and body.get("forecast_origin") == request.get("forecast_origin"),
        body.get("forecast_origin"),
    )
    add(
        "target_start",
        ("AS-02",),
        "target_start_date = forecast_origin + 1 day",
        origin is not None and start == origin + timedelta(days=1),
        body.get("target_start_date"),
    )

    # AS-03 inclusive window
    add(
        "target_end",
        ("AS-03",),
        f"target_end_date = forecast_origin + {horizon} days",
        origin is not None and end == origin + timedelta(days=horizon),
        body.get("target_end_date"),
    )
    add(
        "window_length",
        ("AS-03",),
        f"Inclusive window covers exactly {horizon} day(s)",
        start is not None and end is not None and (end - start).days + 1 == horizon,
        None if start is None or end is None else (end - start).days + 1,
    )

    # AS-04 horizon meaning
    expected_type = "next_day" if horizon == 1 else "cumulative_window"
    add(
        "horizon_echo",
        ("AS-04",),
        "horizon echoed as the same JSON integer",
        type(body.get("horizon")) is int and body.get("horizon") == horizon,
        body.get("horizon"),
    )
    add(
        "forecast_type",
        ("AS-04",),
        f"forecast_type is {expected_type}",
        body.get("forecast_type") == expected_type,
        body.get("forecast_type"),
    )
    if horizon > 1:
        add(
            "cumulative_limitation",
            ("AS-04",),
            "Limitations state multi-day quantities are cumulative, not daily paths",
            "cumulative" in limitation_text and "daily path" in limitation_text,
            limitations,
        )
    if horizon == 28:
        add(
            "h28_limitation",
            ("AS-04",),
            "Limitations state 28-day availability does not approve "
            "downstream inventory use",
            "28-day" in limitation_text
            and "does not approve downstream inventory use" in limitation_text,
            limitations,
        )

    # AS-05 provenance
    add(
        "producer_designation",
        ("AS-05",),
        "producer_designation is frozen_designated_producer",
        body.get("producer_designation") == "frozen_designated_producer",
        body.get("producer_designation"),
    )
    add(
        "producer_mapping",
        ("AS-05",),
        f"Designated producer {expected_model} {expected_config}",
        body.get("model") == expected_model
        and body.get("configuration_id") == expected_config,
        {"model": body.get("model"), "configuration_id": body.get("configuration_id")},
    )
    add(
        "source_run",
        ("AS-05",),
        f"Source run {SOURCE_RUN_ID} and its run manifest reference",
        body.get("model_source_run_id") == SOURCE_RUN_ID
        and body.get("manifest_reference") == MANIFEST_REFERENCE,
        {
            "model_source_run_id": body.get("model_source_run_id"),
            "manifest_reference": body.get("manifest_reference"),
        },
    )
    add(
        "manifest_sha256",
        ("AS-05",),
        "manifest_sha256 is a SHA-256 hex digest",
        is_sha256(body.get("manifest_sha256")),
        body.get("manifest_sha256"),
    )
    add(
        "provenance_keys",
        ("AS-05",),
        "provenance keys are exactly " + ", ".join(sorted(PROVENANCE_FIELDS)),
        isinstance(body.get("provenance"), dict)
        and set(provenance) == PROVENANCE_FIELDS,
        sorted(provenance),
    )
    add(
        "provenance_hashes",
        ("AS-05",),
        "model_hash, preprocessor_hash and input_sha256 are SHA-256 hex digests",
        all(is_sha256(provenance.get(key)) for key in PROVENANCE_HASH_FIELDS),
        {key: provenance.get(key) for key in PROVENANCE_HASH_FIELDS},
    )
    add(
        "provenance_paths",
        ("AS-05",),
        f"Model and preprocessor paths are under {expected_prefix}",
        all(
            isinstance(provenance.get(key), str)
            and str(provenance.get(key)).startswith(expected_prefix)
            for key in ("model_path", "preprocessor_path")
        ),
        {key: provenance.get(key) for key in ("model_path", "preprocessor_path")},
    )

    # AS-06 prospective-only response
    add(
        "response_allowlist",
        ("AS-06",),
        "Response keys exactly match the ForecastResponse allowlist",
        isinstance(raw_body, dict) and set(body) == RESPONSE_FIELDS,
        {
            "unexpected": sorted(set(body) - RESPONSE_FIELDS),
            "missing": sorted(RESPONSE_FIELDS - set(body)),
        },
    )
    forbidden = find_forbidden_keys(raw_body)
    add(
        "no_retrospective_or_inventory_keys",
        ("AS-06",),
        "No retrospective, inventory or metric keys at any depth",
        not forbidden,
        forbidden,
    )
    add(
        "inference_mode",
        ("AS-06",),
        "inference_mode is request_time",
        body.get("inference_mode") == "request_time",
        body.get("inference_mode"),
    )
    return checks


def evaluate_cross_horizon(examples: Mapping[int, Mapping[str, Any]]) -> list[Check]:
    bodies = [_dict(examples[h].get("body")) for h in HORIZONS if h in examples]
    horizons = sorted(
        int(b["horizon"]) for b in bodies if type(b.get("horizon")) is int
    )
    input_hashes = [_dict(b.get("provenance")).get("input_sha256") for b in bodies]
    model_hashes = [_dict(b.get("provenance")).get("model_hash") for b in bodies]
    manifests = {b.get("manifest_sha256") for b in bodies}

    def distinct(values: list[Any]) -> bool:
        return (
            len(values) == len(HORIZONS)
            and all(is_sha256(v) for v in values)
            and len(set(values)) == len(values)
        )

    return [
        Check(
            "cross.four_horizon_records",
            ("AS-04",),
            "Four separate responses, one per horizon 1/7/14/28",
            horizons == list(HORIZONS),
            horizons,
        ),
        Check(
            "cross.distinct_input_sha256",
            ("AS-05",),
            "input_sha256 differs across the four requests "
            "(horizon is part of the input)",
            distinct(input_hashes),
            input_hashes,
        ),
        Check(
            "cross.distinct_model_hash",
            ("AS-05",),
            "Each horizon is served by a distinct saved model file",
            distinct(model_hashes),
            model_hashes,
        ),
        Check(
            "cross.single_manifest",
            ("AS-05",),
            "All four responses cite the same run manifest hash",
            len(bodies) == len(HORIZONS)
            and len(manifests) == 1
            and all(is_sha256(m) for m in manifests),
            sorted(str(m) for m in manifests),
        ),
    ]


def evaluate_repeat(base: Mapping[str, Any] | None, repeat: Any) -> list[Check]:
    base_entry = _dict(base)
    entry = _dict(repeat)
    base_hash = _dict(_dict(base_entry.get("body")).get("provenance")).get(
        "input_sha256"
    )
    repeat_hash = _dict(_dict(entry.get("body")).get("provenance")).get("input_sha256")
    requirements = ("AS-05", "RT-CHANGED-HISTORY")
    return [
        Check(
            "repeat.request_identical",
            requirements,
            "Repeat request is byte-for-byte the 1-day example request",
            bool(base_entry) and entry.get("request") == base_entry.get("request"),
            None,
        ),
        Check(
            "repeat.http_200",
            requirements,
            "Repeat request returns HTTP 200",
            entry.get("http_status") == 200,
            entry.get("http_status"),
        ),
        Check(
            "repeat.same_input_sha256",
            requirements,
            "Identical input yields an identical input_sha256 "
            "(control for the changed-history check)",
            is_sha256(base_hash) and repeat_hash == base_hash,
            {"base": base_hash, "repeat": repeat_hash},
        ),
    ]


def evaluate_changed_history(
    base: Mapping[str, Any] | None, changed: Any
) -> list[Check]:
    base_entry = _dict(base)
    entry = _dict(changed)
    base_body = _dict(base_entry.get("body"))
    body = _dict(entry.get("body"))
    base_prov = _dict(base_body.get("provenance"))
    prov = _dict(body.get("provenance"))
    expected_request = (
        build_changed_history_request(base_entry["request"])
        if isinstance(base_entry.get("request"), dict)
        and "history" in base_entry["request"]
        else None
    )
    differing = [
        field
        for field in STABLE_CHANGED_HISTORY_FIELDS
        if body.get(field) != base_body.get(field)
    ] + [
        f"provenance.{field}"
        for field in STABLE_CHANGED_HISTORY_PROVENANCE
        if prov.get(field) != base_prov.get(field)
    ]
    req = ("RT-CHANGED-HISTORY",)
    return [
        Check(
            "changed_history.request_mutation",
            req,
            "Request equals the 1-day example with final-day Units_Sold "
            f"+{CHANGED_HISTORY_INCREMENT} only",
            expected_request is not None and entry.get("request") == expected_request,
            None,
        ),
        Check(
            "changed_history.http_200",
            req,
            "Changed-history request returns HTTP 200",
            entry.get("http_status") == 200 and body.get("status") == "available",
            entry.get("http_status"),
        ),
        Check(
            "changed_history.input_sha256_changed",
            ("AS-05", *req),
            "input_sha256 is a new SHA-256 digest that differs from the "
            "original request",
            is_sha256(prov.get("input_sha256"))
            and is_sha256(base_prov.get("input_sha256"))
            and prov.get("input_sha256") != base_prov.get("input_sha256"),
            {
                "original": base_prov.get("input_sha256"),
                "changed": prov.get("input_sha256"),
            },
        ),
        Check(
            "changed_history.same_producer_and_window",
            req,
            "Identity, origin, window, producer and saved model/preprocessor "
            "provenance unchanged",
            bool(body) and bool(base_body) and not differing,
            differing,
        ),
        Check(
            "changed_history.quantity_finite",
            req,
            "Changed-history forecast_quantity is a finite number",
            is_finite_number(body.get("forecast_quantity")),
            body.get("forecast_quantity"),
        ),
        Check(
            "changed_history.response_allowlist",
            req,
            "Changed-history response keys match the allowlist",
            set(body) == RESPONSE_FIELDS,
            sorted(set(body) ^ RESPONSE_FIELDS),
        ),
    ]


def _rejection_matches(case: RejectionCase, status: Any, body: Any) -> tuple[bool, Any]:
    detail = _dict(body).get("detail")
    if case.kind == "domain":
        reason = _dict(detail).get("reason_code")
        return status == 422 and reason == case.expected, {
            "http_status": status,
            "reason_code": reason,
        }
    errors = detail if isinstance(detail, list) else []
    matched = any(
        isinstance(err, dict)
        and err.get("type") == "extra_forbidden"
        and isinstance(err.get("loc"), list)
        and bool(err["loc"])
        and err["loc"][-1] == case.expected
        for err in errors
    )
    return status == 422 and matched, {"http_status": status, "detail": detail}


def evaluate_rejections(base: Mapping[str, Any] | None, rejections: Any) -> list[Check]:
    base_request = _dict(base).get("request")
    if not isinstance(base_request, dict) or "history" not in base_request:
        return [
            Check(
                "rejections.base_available",
                ("AS-01", "AS-04", "AS-06", "RT-REJECTIONS"),
                "Valid 1-day example available to derive rejection requests",
                False,
                None,
            )
        ]
    recorded = {
        entry.get("case"): entry
        for entry in (rejections if isinstance(rejections, list) else [])
        if isinstance(entry, dict)
    }
    checks: list[Check] = []
    for case in build_rejection_cases(base_request):
        entry = _dict(recorded.get(case.case_id))
        checks.append(
            Check(
                f"reject.{case.case_id}.request",
                case.requirements,
                f"Recorded request matches specification: {case.description}",
                entry.get("request") == case.payload,
                None,
            )
        )
        matched, observed = _rejection_matches(
            case, entry.get("http_status"), entry.get("body")
        )
        expectation = (
            f"HTTP 422 reason_code {case.expected}"
            if case.kind == "domain"
            else f"HTTP 422 extra_forbidden for {case.expected}"
        )
        checks.append(
            Check(
                f"reject.{case.case_id}.outcome",
                case.requirements,
                f"{expectation} with no substitute forecast_quantity",
                bool(entry)
                and matched
                and not contains_key(entry.get("body"), "forecast_quantity"),
                observed,
            )
        )
    return checks


def evaluate_record(record: Mapping[str, Any]) -> list[Check]:
    checks = evaluate_health(record.get("health"))
    examples: dict[int, Mapping[str, Any]] = {}
    for entry in record.get("examples") or []:
        if isinstance(entry, dict) and entry.get("horizon") in HORIZONS:
            examples[int(entry["horizon"])] = entry
    for horizon in HORIZONS:
        if horizon in examples:
            checks.extend(evaluate_forecast_exchange(horizon, examples[horizon]))
        else:
            checks.append(
                Check(
                    f"h{horizon}.present",
                    (*AS_REQUIREMENTS, "RT-CONTRACT"),
                    f"Exchange for forecast-{horizon}-day.json recorded",
                    False,
                    None,
                )
            )
    checks.extend(evaluate_cross_horizon(examples))
    checks.extend(evaluate_repeat(examples.get(1), record.get("repeat_request")))
    checks.extend(
        evaluate_changed_history(examples.get(1), record.get("changed_history"))
    )
    checks.extend(evaluate_rejections(examples.get(1), record.get("rejections")))
    return checks


def derive_outcomes(checks: Sequence[Check]) -> dict[str, dict[str, Any]]:
    """PASSED only when a requirement has at least one check and none failed."""
    outcomes: dict[str, dict[str, Any]] = {}
    for requirement, title in REQUIREMENTS.items():
        related = [c for c in checks if requirement in c.requirements]
        failed = [c.check_id for c in related if not c.passed]
        outcomes[requirement] = {
            "title": title,
            "outcome": "PASSED" if related and not failed else "FAILED",
            "checks_total": len(related),
            "checks_failed": failed,
        }
    return outcomes


def overall_outcome(outcomes: Mapping[str, Mapping[str, Any]]) -> str:
    passed = set(outcomes) == set(REQUIREMENTS) and all(
        o.get("outcome") == "PASSED" for o in outcomes.values()
    )
    return "PASSED" if passed else "FAILED"


def derive_observations(record: Mapping[str, Any]) -> dict[str, Any]:
    examples = [e for e in record.get("examples") or [] if isinstance(e, dict)]
    base = next((e for e in examples if e.get("horizon") == 1), {})
    original = _dict(base.get("body")).get("forecast_quantity")
    changed = _dict(_dict(record.get("changed_history")).get("body")).get(
        "forecast_quantity"
    )
    return {
        "changed_history_forecast_quantity": {"original": original, "changed": changed},
        "changed_history_forecast_quantity_changed": (
            original != changed
            if is_finite_number(original) and is_finite_number(changed)
            else None
        ),
        "note": (
            "Informational only. Tree models can return the same quantity for "
            "different inputs, so an unchanged quantity is not a failure; the "
            "pass/fail signal is the changed input_sha256 against the "
            "identical-request control."
        ),
    }


# --------------------------------------------------------------------------
# Evidence assembly, exclusive writing and verification
# --------------------------------------------------------------------------


def build_evidence(
    record: Mapping[str, Any], metadata: Mapping[str, Any]
) -> dict[str, Any]:
    checks = evaluate_record(record)
    outcomes = derive_outcomes(checks)
    return {
        "evidence_schema": EVIDENCE_SCHEMA,
        "metadata": dict(metadata),
        "requirement_outcomes": outcomes,
        "overall_outcome": overall_outcome(outcomes),
        "observations": derive_observations(record),
        "checks": [check.to_json() for check in checks],
        "exchanges": dict(record),
    }


def serialise_evidence(evidence: Mapping[str, Any]) -> bytes:
    """UTF-8, LF line endings on every platform, trailing newline."""
    text = json.dumps(evidence, indent=2, ensure_ascii=False, allow_nan=False)
    return (text + "\n").encode("utf-8")


def write_evidence_exclusive(path: Path, data: bytes) -> str:
    """Create ``path`` exclusively in binary mode; never overwrite.

    Raises FileExistsError if the file already exists. Returns the SHA-256 of
    the bytes actually on disk.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
    written = path.read_bytes()
    if written != data:
        raise OSError(f"{path}: bytes on disk differ from the serialised evidence")
    return sha256_bytes(written)


def verify_evidence_file(path: Path) -> tuple[str, dict[str, Any], list[str]]:
    """Re-derive all outcomes from the stored exchanges; never modifies the file."""
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    problems: list[str] = []
    try:
        evidence = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return digest, {}, [f"not valid UTF-8 JSON: {exc}"]
    if (
        not isinstance(evidence, dict)
        or evidence.get("evidence_schema") != EVIDENCE_SCHEMA
    ):
        return digest, _dict(evidence), [f"evidence_schema is not {EVIDENCE_SCHEMA}"]
    if b"\r\n" in raw:
        problems.append(
            "file contains CRLF line endings; the committed bytes must be LF"
        )
    checks = evaluate_record(_dict(evidence.get("exchanges")))
    outcomes = derive_outcomes(checks)
    if [c.to_json() for c in checks] != evidence.get("checks"):
        problems.append(
            "stored checks differ from checks re-derived from the stored exchanges"
        )
    if outcomes != evidence.get("requirement_outcomes"):
        problems.append("stored requirement_outcomes differ from re-derived outcomes")
    if overall_outcome(outcomes) != "PASSED":
        failed = [r for r, o in outcomes.items() if o["outcome"] != "PASSED"]
        problems.append("re-derived outcomes not all PASSED: " + ", ".join(failed))
    if evidence.get("overall_outcome") != overall_outcome(outcomes):
        problems.append("stored overall_outcome differs from the re-derived outcome")
    return digest, evidence, problems


def documentation_values(
    path: Path, digest: str, evidence: Mapping[str, Any]
) -> dict[str, str]:
    meta = _dict(evidence.get("metadata"))
    colombo_date = date.fromisoformat(str(meta["capture_date_asia_colombo"]))
    return {
        "EVIDENCE_PATH": path.as_posix(),
        "EVIDENCE_SHA256": digest,
        "CAPTURE_TIMESTAMP_UTC": str(meta["capture_timestamp_utc"]),
        "CAPTURE_DATE": f"{colombo_date.day} {colombo_date:%B %Y}",
        "API_REVISION": str(meta["api_revision"]),
        "PYTHON_VERSION": str(meta["python_version"]),
        "PLATFORM": str(meta["platform"]),
    }


def fill_placeholders(text: str, values: Mapping[str, str]) -> str:
    """Replace ``{{KEY}}`` tokens; fail on any unknown token."""
    unknown = sorted({m.group(1) for m in _PLACEHOLDER.finditer(text)} - set(values))
    if unknown:
        raise KeyError("unknown placeholders: " + ", ".join(unknown))
    return _PLACEHOLDER.sub(lambda m: values[m.group(1)], text)


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------


def read_git_state(cwd: Path) -> GitState:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return GitState("unknown", None)
    return GitState(revision, status.strip() == "")


def _default_client_factory() -> AbstractContextManager[ClientLike]:
    # The context manager runs the application lifespan, so the saved
    # producers are loaded exactly as in the served application.
    return TestClient(app)


def capture_metadata(
    *,
    reviewer: str,
    argv: Sequence[str],
    git: GitState,
    captured_at: datetime,
    output: Path,
) -> dict[str, Any]:
    previous: dict[str, Any] | None = None
    if PREVIOUS_CAPTURE.exists() and PREVIOUS_CAPTURE.resolve() != output.resolve():
        previous = {
            "path": PREVIOUS_CAPTURE.as_posix(),
            "sha256_local_bytes": sha256_bytes(PREVIOUS_CAPTURE.read_bytes()),
            "status": (
                "Preserved unchanged and superseded: h7-only capture whose "
                "AS-01 to AS-06 values were written as constants rather than "
                "derived from checks."
            ),
        }
    return {
        "title": "Issue #203 request-time forecast consumer verification evidence",
        "related_issue": "#203",
        "pending_under": (
            "#179 (formal producer approval; independently reviewed source "
            "verification)"
        ),
        "capture_timestamp_utc": captured_at.astimezone(UTC).isoformat(
            timespec="seconds"
        ),
        "capture_date_asia_colombo": captured_at.astimezone(COLOMBO).date().isoformat(),
        "api_revision": git.revision,
        "working_tree_clean": git.clean,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "execution": (
            "In-process fastapi.testclient.TestClient(src.api.main.app) with the "
            "application lifespan; saved producers loaded from local artifacts "
            "at startup."
        ),
        "capture_command": " ".join(["python capture_consumer_evidence.py", *argv]),
        "reviewer": reviewer,
        "previous_capture": previous,
        "scope": list(SCOPE_STATEMENTS),
    }


def format_outcomes(evidence: Mapping[str, Any]) -> str:
    lines = []
    for requirement, outcome in _dict(evidence.get("requirement_outcomes")).items():
        total = outcome["checks_total"]
        passed = total - len(outcome["checks_failed"])
        lines.append(
            f"  {requirement:<20} {outcome['outcome']:<7} ({passed}/{total} checks)"
        )
        for check_id in outcome["checks_failed"]:
            lines.append(f"      failed: {check_id}")
    lines.append(f"  OVERALL              {evidence.get('overall_outcome')}")
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0] if __doc__ else None
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"new evidence file to create (default: {DEFAULT_OUTPUT.as_posix()}); "
        "an existing file is never overwritten",
    )
    parser.add_argument("--examples-dir", type=Path, default=DEFAULT_EXAMPLES_DIR)
    parser.add_argument("--reviewer", default="Tinosh")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="permit capture from a working tree with uncommitted tracked changes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run and evaluate every check but write nothing",
    )
    parser.add_argument(
        "--verify",
        type=Path,
        metavar="EVIDENCE",
        help="re-derive outcomes from an existing evidence file (read-only)",
    )
    parser.add_argument(
        "--fill-docs",
        type=Path,
        nargs="+",
        metavar="MARKDOWN",
        default=[],
        help="with --verify: replace {{PLACEHOLDER}} tokens in these files",
    )
    return parser


def _verify_command(args: argparse.Namespace) -> int:
    path: Path = args.verify
    if not path.is_file():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2
    digest, evidence, problems = verify_evidence_file(path)
    print(f"Evidence: {path.as_posix()}\nSHA-256:  {digest}")
    if evidence.get("evidence_schema") == EVIDENCE_SCHEMA:
        print(format_outcomes(evidence))
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1
    values = documentation_values(path, digest, evidence)
    print("\nDocumentation values:")
    for key, value in values.items():
        print(f"  {{{{{key}}}}} = {value}")
    filled: list[tuple[Path, bytes]] = []
    for doc in args.fill_docs:
        try:
            filled.append(
                (
                    doc,
                    fill_placeholders(doc.read_bytes().decode("utf-8"), values).encode(
                        "utf-8"
                    ),
                )
            )
        except KeyError as exc:
            print(f"error: {doc}: {exc}", file=sys.stderr)
            return 1
    for doc, data in filled:  # write only after every document filled cleanly
        doc.write_bytes(data)
        print(f"Filled placeholders in {doc.as_posix()}")
    return 0


def _capture_command(
    args: argparse.Namespace,
    argv: Sequence[str],
    client_factory: ClientFactory,
    git_reader: Callable[[Path], GitState],
    clock: Callable[[], datetime],
) -> int:
    output: Path = args.output
    if output.exists():
        print(
            f"error: {output} already exists; refusing to overwrite existing evidence. "
            "Choose a new --output path or use --verify.",
            file=sys.stderr,
        )
        return 2
    if not args.examples_dir.is_dir():
        print(
            f"error: {args.examples_dir} not found; run from the repository root",
            file=sys.stderr,
        )
        return 2
    git = git_reader(Path.cwd())
    if git.clean is not True and not args.allow_dirty:
        print(
            "error: working tree has uncommitted tracked changes or git is "
            "unavailable; commit first so api_revision identifies the tested "
            "source (or pass --allow-dirty)",
            file=sys.stderr,
        )
        return 2

    captured_at = clock()
    with client_factory() as client:
        record = collect_exchanges(client, args.examples_dir)
    metadata = capture_metadata(
        reviewer=args.reviewer,
        argv=argv,
        git=git,
        captured_at=captured_at,
        output=output,
    )
    evidence = build_evidence(record, metadata)
    print(format_outcomes(evidence))
    if evidence["overall_outcome"] != "PASSED":
        print(
            "error: one or more checks failed; no evidence file written",
            file=sys.stderr,
        )
        return 1
    if args.dry_run:
        print("Dry run: all checks passed; no evidence file written.")
        return 0
    data = serialise_evidence(evidence)
    try:
        digest = write_evidence_exclusive(output, data)
    except FileExistsError:
        print(
            f"error: {output} was created concurrently; not overwritten",
            file=sys.stderr,
        )
        return 2
    print(f"\nEvidence written: {output.as_posix()}\nSHA-256: {digest}")
    for key, value in documentation_values(output, digest, evidence).items():
        print(f"  {{{{{key}}}}} = {value}")
    return 0


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: ClientFactory | None = None,
    git_reader: Callable[[Path], GitState] = read_git_state,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = _parser().parse_args(arguments)
    if args.verify is not None:
        return _verify_command(args)
    if args.fill_docs:
        print("error: --fill-docs requires --verify", file=sys.stderr)
        return 2
    return _capture_command(
        args, arguments, client_factory or _default_client_factory, git_reader, clock
    )


if __name__ == "__main__":
    raise SystemExit(main())
