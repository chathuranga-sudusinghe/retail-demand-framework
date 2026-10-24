"""Read-only joined view of the 20 retained Issue #168 research cases (Issue #183).

Each case presents one fixed-origin chain:

    retained forecast -> linked inventory scenario -> decision-support record

This module only joins and presents evidence that the existing, hash-bound
loaders have already verified. It does not run models, recalculate inventory
exposure, assess transparency, assign review outcomes or create orders. It is
separate from request-time inference (``POST /forecasts``).

Record contents come unchanged from ``build_review_records`` so that
responsible decision-support semantics stay owned by that module.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import os
from pathlib import Path
from typing import Any

from src.decision_support.assessment import (
    PAIRS,
    build_review_records,
    load_inventory_evidence,
)
from src.decision_support.records import DecisionSupportRecord
from src.forecasting.export import DESTINATION
from src.forecasting.paths import REPOSITORY
from src.inventory_risk.forecast_handoff import (
    MAPPING_VERSION,
    ForecastHandoff,
    load_forecast_handoff,
)

CASE_SCHEMA = "issue-183-retained-case-v1"
EVIDENCE_MODE = "fixed_origin_retained_research"
HORIZONS = (1, 7, 14, 28)
GATED_HORIZONS = frozenset({28})
FORECAST_EXPORT_ENV = "RDF_RETAINED_FORECAST_EXPORT"
INVENTORY_PROSPECTIVE_ENV = "RDF_RETAINED_INVENTORY_PROSPECTIVE"
ADVISORY_NOTICE = (
    "Retained fixed-origin research evidence for human consideration only. "
    "It is not a live forecast, an approved purchase instruction or a completed "
    "transparency assessment; human-review status is shown exactly as recorded."
)
_FORECAST_FIELDS = (
    "target_start_date",
    "target_end_date",
    "forecast_type",
    "unit",
    "prediction",
    "model",
    "configuration_id",
    "producer_status",
    "forecast_status",
    "uncertainty",
)
_RECORD_FIELDS = frozenset(f.name for f in fields(DecisionSupportRecord))


class CaseSourceUnavailable(Exception):
    """The retained sources are absent or failed verification."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _inventory_stage(
    horizon: int, record: dict[str, Any], provenance: dict[str, Any]
) -> dict[str, Any]:
    """Describe the inventory step without creating or repairing evidence."""
    evidence = record["inventory_risk_evidence"]
    reason = record["unavailable_fields"].get("inventory_risk_evidence")
    if horizon in GATED_HORIZONS:
        _require(
            evidence is None and bool(reason),
            "A gated 28-day case must not carry inventory scenario evidence.",
        )
        return {
            "status": "gated",
            "reason": reason,
            "evidence": None,
            "provenance": None,
        }
    if evidence is None:
        _require(bool(reason), "Unavailable inventory evidence needs a reason.")
        return {
            "status": "unavailable",
            "reason": reason,
            "evidence": None,
            "provenance": None,
        }
    return {
        "status": "available",
        "reason": None,
        "evidence": evidence,
        "provenance": provenance,
    }


@dataclass(frozen=True)
class RetainedCaseCatalog:
    """Immutable JSON text per case; every read returns a fresh copy."""

    source: str
    cases: tuple[tuple[str, str], ...]
    keys: tuple[tuple[tuple[str, str, str, int], str], ...]

    def ids(self) -> list[str]:
        return [assessment_id for assessment_id, _ in self.cases]

    def get(self, assessment_id: str) -> dict[str, Any] | None:
        for candidate, payload in self.cases:
            if candidate == assessment_id:
                return json.loads(payload)
        return None

    def find(
        self, sku_id: str, warehouse_id: str, forecast_origin: str, horizon: int
    ) -> dict[str, Any] | None:
        wanted = (sku_id, warehouse_id, forecast_origin, horizon)
        for key, assessment_id in self.keys:
            if key == wanted:
                return self.get(assessment_id)
        return None

    def summaries(self) -> list[dict[str, Any]]:
        result = []
        for assessment_id in self.ids():
            case = self.get(assessment_id)
            assert case is not None
            result.append(
                {
                    "assessment_id": assessment_id,
                    "SKU_ID": case["SKU_ID"],
                    "Warehouse_ID": case["Warehouse_ID"],
                    "forecast_origin": case["forecast_origin"],
                    "horizon": case["horizon"],
                    "inventory_status": case["inventory_scenario"]["status"],
                    "human_review_status": case["decision_support_record"][
                        "human_review_status"
                    ],
                }
            )
        return result

    def source_document(self) -> dict[str, Any]:
        return json.loads(self.source)


def build_catalog(
    handoff: ForecastHandoff, inventory_evidence: dict[str, Any]
) -> RetainedCaseCatalog:
    """Join the verified forecast export, inventory evidence and the 20 records."""
    _require(
        inventory_evidence is not None,
        "Linked inventory evidence is required for the joined prototype slice.",
    )
    bundle = build_review_records(handoff, inventory_evidence)
    document = handoff.document
    forecasts = {
        (row["SKU_ID"], row["Warehouse_ID"], row["horizon"]): row
        for row in document["forecasts"]
    }
    expected = [(sku, wh, h) for sku, wh in PAIRS for h in HORIZONS]
    _require(
        len(bundle["records"]) == len(expected) == 20,
        "The retained roster must contain exactly 20 cases.",
    )
    cases: list[tuple[str, str]] = []
    keys: list[tuple[tuple[str, str, str, int], str]] = []
    for position, (case, (sku, warehouse, horizon)) in enumerate(
        zip(bundle["records"], expected, strict=True), start=1
    ):
        record = case["record"]
        assessment_id = case["assessment_id"]
        _require(
            assessment_id == f"F{position:02d}"
            and case["horizon"] == horizon
            and record["sku_id"] == sku
            and record["warehouse_id"] == warehouse
            and record["forecast_horizon"] == f"{horizon}-day",
            f"Record identity differs from the retained roster: {assessment_id}",
        )
        _require(
            set(record) == _RECORD_FIELDS,
            "Decision-support record fields differ from DecisionSupportRecord.",
        )
        row = forecasts[(sku, warehouse, horizon)]
        _require(
            record["forecast_origin"] == row["forecast_origin"]
            and record["forecast_demand"] == row["prediction"],
            f"Record forecast differs from the retained export: {assessment_id}",
        )
        view = {
            "case_schema": CASE_SCHEMA,
            "evidence_mode": EVIDENCE_MODE,
            "mapping_version": bundle["mapping_version"],
            "assessment_id": assessment_id,
            "SKU_ID": sku,
            "Warehouse_ID": warehouse,
            "forecast_origin": row["forecast_origin"],
            "horizon": horizon,
            "forecast": {
                **{name: row[name] for name in _FORECAST_FIELDS},
                "provenance": json.loads(record["forecast_provenance"]),
            },
            "inventory_scenario": _inventory_stage(
                horizon, record, inventory_evidence["provenance"]
            ),
            "decision_support_record": record,
            "advisory_notice": ADVISORY_NOTICE,
        }
        # allow_nan=False rejects any non-finite value instead of hiding it.
        cases.append((assessment_id, json.dumps(view, sort_keys=True, allow_nan=False)))
        keys.append(((sku, warehouse, row["forecast_origin"], horizon), assessment_id))
    source = {
        "mapping_version": MAPPING_VERSION,
        "scope": bundle["scope"],
        "source": bundle["source"],
    }
    return RetainedCaseCatalog(
        source=json.dumps(source, sort_keys=True, allow_nan=False),
        cases=tuple(cases),
        keys=tuple(keys),
    )


def load_catalog(
    forecast_export: Path, inventory_prospective: Path
) -> RetainedCaseCatalog:
    """Verify both retained sources with the existing loaders, then join them."""
    try:
        handoff = load_forecast_handoff(forecast_export)
        inventory = load_inventory_evidence(inventory_prospective, handoff)
        return build_catalog(handoff, inventory)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise CaseSourceUnavailable("source_unverified", str(error)) from error


def load_default_catalog(repository: Path = REPOSITORY) -> RetainedCaseCatalog:
    """Read locally configured paths; nothing is guessed or generated."""
    inventory = os.environ.get(INVENTORY_PROSPECTIVE_ENV, "").strip()
    if not inventory:
        raise CaseSourceUnavailable(
            "inventory_evidence_unconfigured",
            f"Set {INVENTORY_PROSPECTIVE_ENV} to the hash-bound prospective.json.",
        )
    export = os.environ.get(FORECAST_EXPORT_ENV, "").strip()
    return load_catalog(
        Path(export) if export else repository / DESTINATION, Path(inventory)
    )
