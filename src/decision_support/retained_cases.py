"""Read-only access to the retained Issue #168 decision-support cases.

This adapter joins the existing 20 decision-support records to validated
prospective inputs. It never prepares records or reads retrospective results.
"""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
from pathlib import Path
from typing import Any

from src.decision_support.assessment import PAIRS, load_inventory_evidence
from src.decision_support.records import DecisionSupportRecord
from src.forecasting.export import DESTINATION
from src.forecasting.paths import REPOSITORY
from src.inventory_risk.forecast_handoff import (
    MAPPING_VERSION,
    ForecastHandoff,
    load_forecast_handoff,
)
from src.inventory_risk.runner import PROSPECTIVE_FIELDS

DECISION_SUPPORT_DIRECTORY = Path("reports/decision-support/issue-168-inventory-v1")
INVENTORY_PROSPECTIVE_PATH = Path(
    "research-materials/inventory-risk/issue-164/evaluation-v1/prospective.json"
)
# Pins come from the reviewed, Git-tracked Issue #168 retained bundle. A bundle
# revision requires review of these bytes and the corresponding source bindings.
DECISION_SUPPORT_MANIFEST_SHA256 = (
    "92fe7ee2308344b5efd5f3593564ed2c86260f7bf89f8a611e2d2f87d94e638a"
)
DECISION_SUPPORT_RECORDS_SHA256 = (
    "dc029ba66c07009202f17643a3565f550e7ac2aa7c23ac411ea15f964c91937a"
)
HORIZONS = (1, 7, 14, 28)

_MANIFEST_FIELDS = {
    "assessment_status",
    "code_sha256",
    "initial_review_template_sha256",
    "mapping_version",
    "operator",
    "prepared_at",
    "records_markdown_sha256",
    "records_sha256",
    "review_schema",
    "source_export_sha256",
}
_RECORD_FIELDS = set(DecisionSupportRecord.__dataclass_fields__)
_COMMON_PROSPECTIVE_FIELDS = (
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
    "prediction",
    "unit",
    "model",
    "configuration_id",
    "run_id",
    "evaluation_stage",
    "evidence_role",
    "source_export_sha256",
    "source_provenance",
    "forecast_input_status",
    "forecast_input_reason",
    "downstream_use_status",
    "downstream_use_reason",
    "methodology_status",
    "method_assumptions",
    "method_limitations",
)
_INVENTORY_PROSPECTIVE_FIELDS = (
    "Date",
    "Inventory_Level",
    "Reorder_Point",
    "origin_snapshot_available",
    "origin_snapshot_status",
    "origin_snapshot_reason",
    "inventory_state_available",
    "inventory_basis",
    "snapshot_assumption",
    "scenario_inventory_state_available",
    "analysis_inventory_state_available",
    "origin_exposure_state",
    "forecast_exposure_state",
    "inventory_buffer",
    "predicted_margin",
)
_RECORD_INVENTORY_FIELDS = (
    "inventory_basis",
    "snapshot_assumption",
    "origin_snapshot_status",
    "origin_exposure_state",
    "forecast_exposure_state",
    "inventory_buffer",
    "predicted_margin",
    "forecast_input_status",
    "forecast_input_reason",
    "methodology_status",
)
_EXPECTED_PROSPECTIVE_FIELDS = set(
    (*_COMMON_PROSPECTIVE_FIELDS, *_INVENTORY_PROSPECTIVE_FIELDS)
)
if _EXPECTED_PROSPECTIVE_FIELDS != set(PROSPECTIVE_FIELDS):
    raise RuntimeError("Retained-case projection differs from the inventory contract.")
_MANIFEST_CODE_KEYS = {
    "src/decision_support/assessment.py",
    "src/decision_support/records.py",
    "src/inventory_risk/forecast_handoff.py",
}


class RetainedCaseSourceError(ValueError):
    """A retained source is missing, changed or inconsistent."""

    reason_code = "source_unverified"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RetainedCaseSourceError(message)


def _reject_constant(value: str) -> None:
    raise RetainedCaseSourceError(
        f"Non-finite JSON constant is not permitted: {value}."
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"Duplicate JSON property: {key}.")
        result[key] = value
    return result


def _json_document(payload: bytes, label: str) -> dict[str, Any]:
    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetainedCaseSourceError(f"Invalid {label} JSON.") from exc
    _require(isinstance(document, dict), f"{label} must be a JSON object.")
    return document


def _is_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _same_json_value(left: Any, right: Any) -> bool:
    """Compare JSON types as well as values (e.g. false is not zero)."""
    try:
        return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(
            right, sort_keys=True, allow_nan=False
        )
    except (TypeError, ValueError):
        return False


def _forecast_index(
    forecast_document: dict[str, Any],
) -> dict[tuple[Any, ...], dict[str, Any]]:
    forecasts = forecast_document["forecasts"]
    indexed = {
        (
            row["SKU_ID"],
            row["Warehouse_ID"],
            row["forecast_origin"],
            row["horizon"],
        ): row
        for row in forecasts
    }
    _require(len(indexed) == len(forecasts), "Forecast identity is not unique.")
    return indexed


def _validate_manifest(manifest: dict[str, Any], handoff: ForecastHandoff) -> None:
    _require(
        set(manifest) == _MANIFEST_FIELDS,
        "Decision-support manifest fields differ.",
    )
    _require(
        manifest["mapping_version"] == MAPPING_VERSION,
        "Decision-support mapping version differs.",
    )
    _require(
        manifest["source_export_sha256"] == handoff.sha256,
        "Decision-support manifest is bound to another forecast export.",
    )
    _require(
        manifest["review_schema"] in {"issue-168-review-v1", "issue-168-review-v2"},
        "Unsupported decision-support review schema.",
    )
    for name in (
        "initial_review_template_sha256",
        "records_markdown_sha256",
        "records_sha256",
    ):
        _require(_is_digest(manifest[name]), f"Invalid manifest digest: {name}.")
    _require(
        isinstance(manifest["code_sha256"], dict)
        and set(manifest["code_sha256"]) == _MANIFEST_CODE_KEYS
        and all(_is_digest(value) for value in manifest["code_sha256"].values()),
        "Invalid preparation-code digest mapping.",
    )
    for name in ("assessment_status", "operator", "prepared_at"):
        _require(
            isinstance(manifest[name], str) and bool(manifest[name].strip()),
            f"Invalid decision-support manifest value: {name}.",
        )


def _expected_roster() -> list[tuple[str, str, int, str]]:
    return [
        (sku, warehouse, horizon, f"F{index:02d}")
        for index, (sku, warehouse, horizon) in enumerate(
            ((sku, warehouse, h) for sku, warehouse in PAIRS for h in HORIZONS),
            start=1,
        )
    ]


def _projection(row: dict[str, Any], horizon: int) -> dict[str, Any]:
    names: tuple[str, ...] = _COMMON_PROSPECTIVE_FIELDS
    if horizon in (1, 7, 14):
        names = (*names, *_INVENTORY_PROSPECTIVE_FIELDS)
    return {name: row[name] for name in names}


def _validate_record_join(
    wrapper: dict[str, Any],
    *,
    expected: tuple[str, str, int, str],
    handoff: ForecastHandoff,
    forecast_document: dict[str, Any],
    forecasts: dict[tuple[Any, ...], dict[str, Any]],
    inventory_rows: dict[tuple[Any, ...], dict[str, Any]],
    inventory_provenance: dict[str, Any],
) -> dict[str, Any]:
    sku, warehouse, horizon, assessment_id = expected
    _require(
        isinstance(wrapper, dict)
        and set(wrapper) == {"assessment_id", "horizon", "record"}
        and wrapper["assessment_id"] == assessment_id
        and type(wrapper["horizon"]) is int
        and wrapper["horizon"] == horizon,
        f"Decision-support wrapper differs for {assessment_id}.",
    )
    record = wrapper["record"]
    _require(
        isinstance(record, dict) and set(record) == _RECORD_FIELDS,
        f"Decision-support record fields differ for {assessment_id}.",
    )
    try:
        DecisionSupportRecord(**record)
    except (TypeError, ValueError) as exc:
        raise RetainedCaseSourceError(
            f"Invalid decision-support record {assessment_id}."
        ) from exc

    key = sku, warehouse, forecast_document["forecast_origin"], horizon
    _require(key in forecasts, f"Forecast case is missing for {assessment_id}.")
    forecast = forecasts[key]
    _require(
        record["sku_id"] == sku
        and record["warehouse_id"] == warehouse
        and record["forecast_origin"] == forecast["forecast_origin"]
        and record["forecast_horizon"] == f"{horizon}-day"
        and type(record["forecast_demand"]) is type(forecast["prediction"])
        and record["forecast_demand"] == forecast["prediction"],
        f"Nested forecast identity differs for {assessment_id}.",
    )
    try:
        forecast_provenance = _json_document(
            record["forecast_provenance"].encode("utf-8"),
            f"forecast provenance for {assessment_id}",
        )
    except (AttributeError, TypeError) as exc:
        raise RetainedCaseSourceError(
            f"Invalid forecast provenance for {assessment_id}."
        ) from exc
    expected_provenance = {
        "export_sha256": handoff.sha256,
        "export_schema": forecast_document["export_schema"],
        "source": forecast_document["source"],
        "SKU_ID": sku,
        "Warehouse_ID": warehouse,
        "forecast_origin": forecast["forecast_origin"],
        "horizon": horizon,
        "model": forecast["model"],
        "configuration_id": forecast["configuration_id"],
        "producer_status": forecast["producer_status"],
        "forecast_status": forecast["forecast_status"],
    }
    _require(
        _same_json_value(forecast_provenance, expected_provenance),
        f"Forecast provenance differs for {assessment_id}.",
    )

    if horizon == 28:
        _require(
            key in inventory_rows,
            f"Inventory case is missing for {assessment_id}.",
        )
        gated_row = inventory_rows[key]
        _require(
            record["inventory_risk_evidence"] is None
            and record["inventory_risk_provenance"] is None
            and "28_day_downstream_use_requires_separate_approval"
            in record["unavailable_fields"].get("inventory_risk_evidence", "")
            and gated_row["SKU_ID"] == sku
            and gated_row["Warehouse_ID"] == warehouse
            and gated_row["forecast_origin"] == forecast["forecast_origin"]
            and gated_row["horizon"] == horizon
            and gated_row["source_export_sha256"] == handoff.sha256
            and gated_row["downstream_use_status"]
            == "not_approved_for_downstream_use"
            and gated_row["downstream_use_reason"]
            == "28_day_downstream_use_requires_separate_approval",
            "The h28 inventory gate is not preserved.",
        )
        return {"assessment_id": assessment_id, "horizon": horizon, "record": record}

    _require(key in inventory_rows, f"Inventory case is missing for {assessment_id}.")
    source_row = inventory_rows[key]
    _require(
        source_row["source_export_sha256"] == handoff.sha256
        and source_row["SKU_ID"] == sku
        and source_row["Warehouse_ID"] == warehouse
        and source_row["forecast_origin"] == forecast["forecast_origin"]
        and source_row["horizon"] == horizon,
        f"Inventory identity differs for {assessment_id}.",
    )
    inventory_available = source_row["analysis_inventory_state_available"] is True
    if inventory_available:
        expected_inventory = {
            name: source_row[name] for name in _RECORD_INVENTORY_FIELDS
        }
        _require(
            _same_json_value(record["inventory_risk_evidence"], expected_inventory)
            and record["inventory_risk_provenance"]
            == json.dumps(inventory_provenance, sort_keys=True),
            f"Decision-support inventory evidence differs for {assessment_id}.",
        )
    else:
        _require(
            record["inventory_risk_evidence"] is None
            and bool(record["unavailable_fields"].get("inventory_risk_evidence")),
            f"Unavailable inventory evidence lacks its reason for {assessment_id}.",
        )
    return {"assessment_id": assessment_id, "horizon": horizon, "record": record}


def load_retained_case_bundle(
    repository: Path = REPOSITORY,
    *,
    forecast_loader: Callable[..., ForecastHandoff] = load_forecast_handoff,
    inventory_loader: Callable[..., dict[str, Any]] = load_inventory_evidence,
) -> dict[str, Any]:
    """Load and validate the existing retained 20-case bundle without writing.

    ``evaluation.json`` and ``review.json`` are never opened here. The existing
    inventory loader may hash its bound retrospective companion as opaque bytes.
    """
    repository = repository.resolve()
    forecast_path = repository / DESTINATION
    inventory_path = repository / INVENTORY_PROSPECTIVE_PATH
    record_directory = repository / DECISION_SUPPORT_DIRECTORY
    try:
        handoff = forecast_loader(forecast_path)
        inventory = inventory_loader(inventory_path, handoff)
        return load_decision_support_records(
            record_directory,
            handoff=handoff,
            inventory_evidence=inventory,
        )
    except RetainedCaseSourceError:
        raise
    except (
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        IndexError,
    ) as exc:
        raise RetainedCaseSourceError(
            "A retained decision-support source is unavailable or unverified."
        ) from exc


def load_decision_support_records(
    directory: Path,
    *,
    handoff: ForecastHandoff,
    inventory_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Validate the decision-support manifest and create prospective joins."""
    try:
        manifest_bytes = (directory / "manifest.json").read_bytes()
        records_bytes = (directory / "records.json").read_bytes()
    except OSError as exc:
        raise RetainedCaseSourceError(
            "Decision-support source is unavailable."
        ) from exc
    _require(
        hashlib.sha256(manifest_bytes).hexdigest() == DECISION_SUPPORT_MANIFEST_SHA256,
        "Decision-support manifest hash differs from the reviewed retained bundle.",
    )
    _require(
        hashlib.sha256(records_bytes).hexdigest() == DECISION_SUPPORT_RECORDS_SHA256,
        "Decision-support records hash differs from the reviewed retained bundle.",
    )
    manifest = _json_document(manifest_bytes, "decision-support manifest")
    _validate_manifest(manifest, handoff)
    _require(
        hashlib.sha256(records_bytes).hexdigest() == manifest["records_sha256"],
        "Decision-support records do not match their manifest hash.",
    )
    bundle = _json_document(records_bytes, "decision-support records")
    _require(
        set(bundle) == {"mapping_version", "source", "scope", "records"}
        and bundle["mapping_version"]
        == manifest["mapping_version"]
        == MAPPING_VERSION,
        "Decision-support records envelope differs from the manifest.",
    )
    _require(
        isinstance(bundle["records"], list) and len(bundle["records"]) == 20,
        "Decision-support roster must contain exactly 20 cases.",
    )
    _require(
        isinstance(bundle["scope"], str) and bool(bundle["scope"].strip()),
        "Decision-support scope is missing.",
    )

    forecast_document = handoff.document
    expected_source = {
        "export_sha256": handoff.sha256,
        "export_schema": forecast_document["export_schema"],
        **forecast_document["source"],
        "inventory_evidence": inventory_evidence["provenance"],
    }
    _require(
        _same_json_value(bundle["source"], expected_source),
        "Decision-support source provenance differs from validated inputs.",
    )
    forecasts = _forecast_index(forecast_document)
    inventory_rows = inventory_evidence["rows"]
    roster = _expected_roster()
    cases = [
        _validate_record_join(
            wrapper,
            expected=expected,
            handoff=handoff,
            forecast_document=forecast_document,
            forecasts=forecasts,
            inventory_rows=inventory_rows,
            inventory_provenance=inventory_evidence["provenance"],
        )
        for wrapper, expected in zip(bundle["records"], roster, strict=True)
    ]
    for case in cases:
        key = (
            case["record"]["sku_id"],
            case["record"]["warehouse_id"],
            case["record"]["forecast_origin"],
            case["horizon"],
        )
        source_row = inventory_rows[key]
        case["prospective_record"] = _projection(source_row, case["horizon"])

    return {
        "mapping_version": bundle["mapping_version"],
        "source": bundle["source"],
        "scope": bundle["scope"],
        "records": cases,
    }
