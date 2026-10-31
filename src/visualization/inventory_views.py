"""Read and project retained inventory evidence for four approved views.

This module consumes retained files only. It does not prepare inventory inputs,
run an evaluation, produce charts, or expose retrospective values through the
prospective projections.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

from src.forecasting.export import DESTINATION as FORECAST_EXPORT_PATH
from src.forecasting.paths import REPOSITORY
from src.inventory_risk.forecast_handoff import (
    ForecastHandoff,
    load_forecast_handoff,
)
from src.inventory_risk.input_preparation import EVALUABLE_HORIZONS
from src.inventory_risk.runner import (
    PROSPECTIVE_FIELDS,
    PROSPECTIVE_SCHEMA,
    PROVENANCE_SHA256,
    RUN_SCHEMA,
    validate_prospective_state,
)

INVENTORY_EVIDENCE_DIRECTORY = Path("reports/inventory-risk/issue-164/evaluation-v1")
EVALUATION_FILE_NAMES = frozenset({"prospective.json", "evaluation.json", "report.md"})
PROSPECTIVE_HORIZONS = (1, 7, 14)
RETROSPECTIVE_PROXY_LABEL = (
    "Retrospective threshold-crossing proxy based on Units_Sold; not observed stockout."
)

IDENTITY_FIELDS = ("SKU_ID", "Warehouse_ID", "forecast_origin", "horizon")
TARGET_FIELDS = ("target_start_date", "target_end_date")
_FORECAST_COPY_FIELDS = (
    "prediction",
    "unit",
    "model",
    "configuration_id",
    *TARGET_FIELDS,
)
_FORECAST_EXPORT_SOURCE_FIELDS = (
    "forecast_status",
    "producer_status",
)
_GROUP_FIELDS = (
    "inventory_basis",
    "run_id",
    "evaluation_stage",
    "evidence_role",
    "model",
    "configuration_id",
    "horizon",
    "forecast_origin",
    "canonical_config_id",
    "fold_id",
    "target_start_date",
    "target_end_date",
    "selection_status",
    "representation_id",
    "methodology_status",
)
_COVERAGE_COUNT_FIELDS = (
    "origin_known_at_or_below_count",
    "scenario_at_or_below_count",
    "initially_above_threshold_count",
    "evaluable_paired_case_count",
    "unavailable_case_count",
    "forecast_unavailable_or_gated_count",
    "retrospective_unavailable_or_gated_count",
)
_CONFUSION_COUNT_FIELDS = ("N", "TP", "TN", "FP", "FN")
_METRIC_FIELDS = (
    "event_prevalence",
    "missed_crossing_rate",
    "false_alert_rate",
    "agreement",
    "precision",
    "recall",
    "balanced_accuracy",
)
_EVALUATION_REQUIRED_FIELDS = frozenset(
    {
        *IDENTITY_FIELDS,
        *TARGET_FIELDS,
        "prediction",
        "unit",
        "model",
        "configuration_id",
        "run_id",
        "evaluation_stage",
        "evidence_role",
        "source_export_sha256",
        "source_provenance",
        "forecast_status",
        "producer_status",
        "prediction_status",
        "eligibility_status",
        "forecast_input_status",
        "forecast_input_reason",
        "retrospective_input_status",
        "retrospective_input_reason",
        "target_status",
        "target_unavailable_reason",
        "evaluation_unavailable_reasons",
        "origin_exposure_state",
        "forecast_exposure_state",
        "retrospective_exposure_state",
        "comparison_case",
        "confusion_cell",
        "inventory_basis",
        "inventory_buffer",
        "predicted_margin",
        "retrospective_margin",
        "methodology_status",
        "method_assumptions",
        "method_limitations",
        "observed_target",
    }
)


class InventoryViewSourceError(ValueError):
    """A retained visual-evidence source is absent, changed, or inconsistent."""

    reason_code = "source_unverified"


@dataclass(frozen=True)
class InventoryViewEvidence:
    """Validated retained files, with prospective and retrospective documents apart."""

    manifest: dict[str, Any]
    prospective: dict[str, Any]
    evaluation: dict[str, Any]
    forecasts: tuple[dict[str, Any], ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryViewSourceError(message)


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        _require(key not in value, f"Duplicate JSON property: {key}.")
        value[key] = item
    return value


def _invalid_constant(value: str) -> None:
    raise InventoryViewSourceError(
        f"Non-finite JSON constant is not permitted: {value}."
    )


def _json_document(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_object,
            parse_constant=_invalid_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InventoryViewSourceError(f"Invalid {label} JSON.") from exc
    _require(isinstance(value, dict), f"{label} must be a JSON object.")
    return value


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _same_json(left: Any, right: Any) -> bool:
    try:
        return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(
            right, sort_keys=True, allow_nan=False
        )
    except (TypeError, ValueError):
        return False


def _case_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(row[name] for name in IDENTITY_FIELDS)


def _finite_json_number(value: Any) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def load_inventory_view_evidence(
    repository: Path = REPOSITORY,
    *,
    forecast_loader: Callable[[Path], ForecastHandoff] = load_forecast_handoff,
) -> InventoryViewEvidence:
    """Validate and load the tracked Issue-164 evidence without generating results.

    The Issue-164 runner's existing validator is reused for prospective row
    semantics. Its loader is intentionally restricted to ignored
    ``research-materials/`` inputs, so this reader verifies the tracked review
    copy against its own manifest before parsing it.
    """
    repository = repository.resolve()
    directory = repository / INVENTORY_EVIDENCE_DIRECTORY
    try:
        manifest_bytes = (directory / "manifest.json").read_bytes()
        manifest = _json_document(manifest_bytes, "inventory evidence manifest")
        _require(
            manifest.get("schema") == RUN_SCHEMA,
            "Unsupported inventory evidence manifest schema.",
        )
        file_hashes = manifest.get("files")
        _require(
            isinstance(file_hashes, dict) and set(file_hashes) == EVALUATION_FILE_NAMES,
            "Inventory evidence manifest file list differs.",
        )
        payloads: dict[str, bytes] = {}
        for name, expected_hash in file_hashes.items():
            _require(_is_digest(expected_hash), f"Invalid manifest digest for {name}.")
            payload = (directory / name).read_bytes()
            _require(
                hashlib.sha256(payload).hexdigest() == expected_hash,
                f"Inventory evidence hash differs: {name}.",
            )
            payloads[name] = payload

        handoff = forecast_loader(repository / FORECAST_EXPORT_PATH)
        forecast_document = handoff.document
        source = manifest.get("source")
        _require(isinstance(source, dict), "Inventory evidence source is missing.")
        _require(
            manifest.get("dataset_provenance_sha256") == PROVENANCE_SHA256,
            "Inventory dataset provenance differs from the retained contract.",
        )
        _require(
            source.get("forecast_export_sha256") == handoff.sha256
            and source.get("forecast_source") == forecast_document.get("source"),
            "Inventory evidence is bound to a different forecast export.",
        )

        prospective = _json_document(payloads["prospective.json"], "prospective")
        evaluation = _json_document(payloads["evaluation.json"], "evaluation")
        _require(
            set(prospective) == {"schema", "source", "scope", "records"}
            and prospective.get("schema") == PROSPECTIVE_SCHEMA
            and prospective.get("source") == source,
            "Prospective inventory envelope differs from its manifest.",
        )
        _require(
            set(evaluation) == {"schema", "source", "scope", "cases", "summary"}
            and evaluation.get("schema") == RUN_SCHEMA
            and evaluation.get("source") == source,
            "Retrospective evaluation envelope differs from its manifest.",
        )
        _require(
            isinstance(source.get("mapping_version"), str)
            and source.get("mapping_version")
            and source.get("snapshot_policy")
            in {"unknown", "source-confirmed", "constructed-origin"}
            and isinstance(source.get("snapshot_basis"), str)
            and bool(source["snapshot_basis"].strip()),
            "Inventory evidence policy or basis is invalid.",
        )

        prospective_records = prospective.get("records")
        export_rows = forecast_document.get("forecasts")
        _require(
            isinstance(prospective_records, list)
            and len(prospective_records) == 1000
            and isinstance(export_rows, list)
            and len(export_rows) == 1000,
            "The retained prospective population must contain 1000 forecast keys.",
        )
        export_by_key = {_case_key(row): row for row in export_rows}
        _require(
            len(export_by_key) == len(export_rows),
            "Forecast export identity is not unique.",
        )
        prospective_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row in prospective_records:
            _require(
                isinstance(row, dict) and set(row) == set(PROSPECTIVE_FIELDS),
                "Prospective record fields differ from the retained contract.",
            )
            key = _case_key(row)
            _require(
                key not in prospective_by_key and key in export_by_key,
                "Prospective inventory identity is unknown or duplicated.",
            )
            forecast = export_by_key[key]
            for name in _FORECAST_COPY_FIELDS:
                _require(
                    _same_json(row[name], forecast[name]),
                    f"Prospective forecast field differs: {name}.",
                )
            _require(
                row["source_export_sha256"] == handoff.sha256
                and row["source_provenance"]
                == json.dumps(forecast_document["source"], sort_keys=True),
                "Prospective forecast provenance differs from the validated export.",
            )
            try:
                validate_prospective_state(row, source)
            except (TypeError, ValueError, KeyError) as exc:
                raise InventoryViewSourceError(
                    "Prospective inventory state failed source validation."
                ) from exc
            prospective_by_key[key] = row
        _require(
            set(prospective_by_key) == set(export_by_key),
            "Prospective inventory keys do not match the forecast population.",
        )

        evaluation_cases = evaluation.get("cases")
        evaluation_summary = evaluation.get("summary")
        expected_evaluation_keys = {
            key for key in export_by_key if key[3] in EVALUABLE_HORIZONS
        }
        _require(
            isinstance(evaluation_cases, list)
            and len(evaluation_cases) == len(expected_evaluation_keys)
            and isinstance(evaluation_summary, list)
            and len(evaluation_summary) == len(EVALUABLE_HORIZONS),
            "Retrospective evaluation population or summaries differ.",
        )
        evaluation_keys: set[tuple[Any, ...]] = set()
        for row in evaluation_cases:
            _require(
                isinstance(row, dict) and _EVALUATION_REQUIRED_FIELDS <= set(row),
                "Retrospective evaluation case is missing required fields.",
            )
            key = _case_key(row)
            _require(
                key[3] in EVALUABLE_HORIZONS
                and key not in evaluation_keys
                and key in prospective_by_key,
                "Retrospective evaluation contains an unknown, duplicate, or gated key.",
            )
            prospective_row = prospective_by_key[key]
            for name in (
                *TARGET_FIELDS,
                "prediction",
                "unit",
                "model",
                "configuration_id",
            ):
                _require(
                    _same_json(row[name], prospective_row[name]),
                    f"Retrospective case identity/value differs: {name}.",
                )
            _require(
                row["source_export_sha256"] == handoff.sha256,
                "Retrospective case is bound to a different forecast export.",
            )
            _require(
                row["source_provenance"]
                == json.dumps(forecast_document["source"], sort_keys=True)
                and row["forecast_status"] == export_by_key[key]["forecast_status"]
                and row["producer_status"] == export_by_key[key]["producer_status"],
                "Retrospective forecast provenance differs from the validated export.",
            )
            evaluation_keys.add(key)
        _require(
            evaluation_keys == expected_evaluation_keys,
            "Retrospective cases do not match the approved evaluation horizons.",
        )

        summary_horizons: set[int] = set()
        for row in evaluation_summary:
            _require(
                isinstance(row, dict)
                and set(_CONFUSION_COUNT_FIELDS + _COVERAGE_COUNT_FIELDS) <= set(row)
                and set(_METRIC_FIELDS) <= set(row),
                "Retrospective summary is missing existing counts or metrics.",
            )
            horizon = row.get("horizon")
            _require(
                type(horizon) is int
                and horizon in EVALUABLE_HORIZONS
                and horizon not in summary_horizons,
                "Retrospective summary has an unexpected or duplicate horizon.",
            )
            _require(
                all(
                    type(row[name]) is int
                    for name in _CONFUSION_COUNT_FIELDS + _COVERAGE_COUNT_FIELDS
                ),
                "Retrospective summary counts must remain integers.",
            )
            for name in _METRIC_FIELDS:
                value, status = row[name], row.get(f"{name}_status")
                _require(
                    (value is None or _finite_json_number(value))
                    and isinstance(status, str)
                    and bool(status),
                    f"Retrospective metric status/value is invalid: {name}.",
                )
            summary_horizons.add(horizon)
        _require(
            summary_horizons == set(EVALUABLE_HORIZONS),
            "Retrospective summaries must remain separate for h1, h7, and h14.",
        )
        return InventoryViewEvidence(
            manifest=manifest,
            prospective=prospective,
            evaluation=evaluation,
            forecasts=tuple(export_rows),
        )
    except InventoryViewSourceError:
        raise
    except (
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
    ) as exc:
        raise InventoryViewSourceError(
            "A retained inventory view source is unavailable or unverified."
        ) from exc


def _projection(row: Mapping[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {name: row[name] for name in fields}


def _prospective_identity_and_gate(row: Mapping[str, Any]) -> dict[str, Any]:
    return _projection(
        row,
        (
            *IDENTITY_FIELDS,
            *TARGET_FIELDS,
            "downstream_use_status",
            "downstream_use_reason",
        ),
    )


def _prospective_view_row(row: dict[str, Any]) -> dict[str, Any]:
    if row["horizon"] == 28:
        return _prospective_identity_and_gate(row)
    return _projection(
        row,
        (
            *IDENTITY_FIELDS,
            *TARGET_FIELDS,
            "prediction",
            "unit",
            "model",
            "configuration_id",
            "run_id",
            "evaluation_stage",
            "evidence_role",
            "source_export_sha256",
            "source_provenance",
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
            "forecast_input_status",
            "forecast_input_reason",
            "downstream_use_status",
            "downstream_use_reason",
            "methodology_status",
            "method_assumptions",
            "method_limitations",
        ),
    )


def _evaluation_case_context(row: dict[str, Any]) -> dict[str, Any]:
    return _projection(
        row,
        (
            *IDENTITY_FIELDS,
            *TARGET_FIELDS,
            "inventory_basis",
            "run_id",
            "evaluation_stage",
            "evidence_role",
            "model",
            "configuration_id",
            "canonical_config_id",
            "methodology_status",
        ),
    )


def build_exposure_coverage(evidence: InventoryViewEvidence) -> dict[str, Any]:
    """Build prospective exposure rows and a separate evaluation coverage section."""
    coverage_fields = (
        *_GROUP_FIELDS,
        *_CONFUSION_COUNT_FIELDS,
        *_COVERAGE_COUNT_FIELDS,
    )
    evaluation_status_fields = (
        *IDENTITY_FIELDS,
        "comparison_case",
        "retrospective_exposure_state",
        "retrospective_input_status",
        "retrospective_input_reason",
        "target_status",
        "target_unavailable_reason",
        "evaluation_unavailable_reasons",
    )
    return {
        "source": evidence.prospective["source"],
        "horizon_population": [
            {
                "forecast_origin": origin,
                "horizon": horizon,
                "horizon_forecast_population_count": sum(
                    row["forecast_origin"] == origin and row["horizon"] == horizon
                    for row in evidence.prospective["records"]
                ),
            }
            for origin, horizon in sorted(
                {
                    (row["forecast_origin"], row["horizon"])
                    for row in evidence.prospective["records"]
                }
            )
        ],
        "prospective_records": [
            _prospective_view_row(row) for row in evidence.prospective["records"]
        ],
        "evaluation_only": {
            "summary": [
                _projection(row, tuple(name for name in coverage_fields if name in row))
                for row in evidence.evaluation["summary"]
            ],
            "cases": [
                _projection(row, evaluation_status_fields)
                for row in evidence.evaluation["cases"]
            ],
        },
    }


def _metric_denominator(row: Mapping[str, Any], name: str) -> int | str:
    if name in {"event_prevalence", "agreement"}:
        return row["N"]
    if name in {"missed_crossing_rate", "recall"}:
        return row["TP"] + row["FN"]
    if name == "false_alert_rate":
        return row["FP"] + row["TN"]
    if name == "precision":
        return row["TP"] + row["FP"]
    return f"positive={row['TP'] + row['FN']}; negative={row['TN'] + row['FP']}"


def build_proxy_crossing_comparison(evidence: InventoryViewEvidence) -> dict[str, Any]:
    """Build evaluation-only proxy comparisons, never observed-stockout claims."""
    summaries: list[dict[str, Any]] = []
    for source_row in evidence.evaluation["summary"]:
        row = dict(source_row)
        summaries.append(
            {
                "group": _projection(
                    row,
                    tuple(name for name in _GROUP_FIELDS if name in row),
                ),
                "counts": _projection(
                    row, _CONFUSION_COUNT_FIELDS + _COVERAGE_COUNT_FIELDS
                ),
                "metrics": {
                    name: {
                        "value": row[name],
                        "denominator": _metric_denominator(row, name),
                        "status": row[f"{name}_status"],
                    }
                    for name in _METRIC_FIELDS
                },
            }
        )
    case_fields = (
        *IDENTITY_FIELDS,
        *TARGET_FIELDS,
        "comparison_case",
        "confusion_cell",
        "origin_exposure_state",
        "forecast_exposure_state",
        "retrospective_exposure_state",
        "forecast_input_status",
        "forecast_input_reason",
        "retrospective_input_status",
        "retrospective_input_reason",
        "target_status",
        "target_unavailable_reason",
        "evaluation_unavailable_reasons",
        "run_id",
        "evaluation_stage",
        "evidence_role",
        "model",
        "configuration_id",
        "source_export_sha256",
        "source_provenance",
        "methodology_status",
        "method_assumptions",
        "method_limitations",
    )
    return {
        "label": RETROSPECTIVE_PROXY_LABEL,
        "source": evidence.evaluation["source"],
        "summaries": summaries,
        "cases": [
            _projection(row, case_fields) for row in evidence.evaluation["cases"]
        ],
    }


def build_margin_comparison(evidence: InventoryViewEvidence) -> dict[str, Any]:
    """Keep prospective forecast margins separate from retrospective margins."""
    prospective_fields = (
        *IDENTITY_FIELDS,
        *TARGET_FIELDS,
        "inventory_basis",
        "inventory_buffer",
        "predicted_margin",
        "origin_exposure_state",
        "forecast_exposure_state",
        "origin_snapshot_status",
        "origin_snapshot_reason",
        "forecast_input_status",
        "forecast_input_reason",
        "run_id",
        "evaluation_stage",
        "evidence_role",
        "model",
        "configuration_id",
        "source_export_sha256",
        "source_provenance",
        "methodology_status",
        "method_assumptions",
        "method_limitations",
    )
    evaluation_fields = (
        *IDENTITY_FIELDS,
        *TARGET_FIELDS,
        "inventory_basis",
        "inventory_buffer",
        "retrospective_margin",
        "origin_exposure_state",
        "retrospective_exposure_state",
        "retrospective_input_status",
        "retrospective_input_reason",
        "target_status",
        "target_unavailable_reason",
        "evaluation_unavailable_reasons",
        "run_id",
        "evaluation_stage",
        "evidence_role",
        "model",
        "configuration_id",
        "source_export_sha256",
        "source_provenance",
        "methodology_status",
        "method_assumptions",
        "method_limitations",
    )
    return {
        "reference_value": 0,
        "reference_meaning": "Existing reorder-reference boundary; no tolerance band.",
        "prospective": {
            "records": [
                _projection(row, prospective_fields)
                for row in evidence.prospective["records"]
                if row["horizon"] in PROSPECTIVE_HORIZONS
            ]
        },
        "evaluation_only": {
            "records": [
                _projection(row, evaluation_fields)
                for row in evidence.evaluation["cases"]
            ]
        },
    }


def _availability_record(
    row: dict[str, Any], forecast: Mapping[str, Any]
) -> dict[str, Any]:
    if row["horizon"] == 28:
        return _prospective_identity_and_gate(row)
    return {
        **_projection(
            row,
            (
                *IDENTITY_FIELDS,
                *TARGET_FIELDS,
                "prediction",
                "unit",
                "model",
                "configuration_id",
                "run_id",
                "evaluation_stage",
                "evidence_role",
                "source_export_sha256",
                "source_provenance",
                "origin_snapshot_available",
                "origin_snapshot_status",
                "origin_snapshot_reason",
                "inventory_state_available",
                "inventory_basis",
                "snapshot_assumption",
                "scenario_inventory_state_available",
                "analysis_inventory_state_available",
                "forecast_input_status",
                "forecast_input_reason",
                "downstream_use_status",
                "downstream_use_reason",
                "methodology_status",
                "method_assumptions",
                "method_limitations",
            ),
        ),
        **_projection(forecast, _FORECAST_EXPORT_SOURCE_FIELDS),
    }


def build_availability_provenance(evidence: InventoryViewEvidence) -> dict[str, Any]:
    """Build distinct prospective and evaluation-only evidence-status matrices."""
    evaluation_fields = (
        *IDENTITY_FIELDS,
        "forecast_status",
        "producer_status",
        "prediction_status",
        "eligibility_status",
        "forecast_input_status",
        "forecast_input_reason",
        "retrospective_input_status",
        "retrospective_input_reason",
        "target_status",
        "target_unavailable_reason",
        "evaluation_unavailable_reasons",
        "run_id",
        "evaluation_stage",
        "evidence_role",
        "model",
        "configuration_id",
        "source_export_sha256",
        "source_provenance",
        "methodology_status",
        "method_assumptions",
        "method_limitations",
    )
    forecast_by_key = {_case_key(row): row for row in evidence.forecasts}
    return {
        "source": evidence.prospective["source"],
        "dataset_provenance_sha256": evidence.manifest["dataset_provenance_sha256"],
        "prospective": {
            "records": [
                _availability_record(row, forecast_by_key[_case_key(row)])
                for row in evidence.prospective["records"]
            ]
        },
        "evaluation_only": {
            "records": [
                _projection(row, evaluation_fields)
                for row in evidence.evaluation["cases"]
            ]
        },
    }
