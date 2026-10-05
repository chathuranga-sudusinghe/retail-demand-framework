"""Deterministic prospective projection of the retained Issue #132 evidence.

Only JSON identities and byte hashes are checked. Models, outcomes and research
metrics are never loaded or recalculated. See docs/forecast-api-contract.md.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any

from src.forecasting.paths import REPOSITORY, RepositoryLayout

RUN_ID = "final-20261003-02"
EXPORT_SCHEMA = "issue-132-forecast-export-v1"
SOURCE_SCHEMA = "issue-130-final-v1"
ORIGIN = "2024-12-02"
TRAINING_START = "2024-01-01"
PRODUCERS = (
    (1, "lightgbm", "GBM018"),
    (7, "lightgbm", "GBM011"),
    (14, "xgboost", "GBM022"),
    (28, "xgboost", "GBM003"),
)
DESTINATION = f"data/processed/forecasting/handoffs/{RUN_ID}/{EXPORT_SCHEMA}.json"
RECORD_SOURCE_FIELDS = (
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
    "prediction",
    "model",
    "configuration_id",
)
REFERENCE_NAMES = ("model", "descriptor", "preprocessor", "origin_features")
INTEGRITY_FIELDS = {
    "status",
    "evaluations",
    "learned_refits",
    "baseline_evaluations",
    "predictions",
    "models_replayed",
}


@dataclass(frozen=True)
class _SourceAnchor:
    """Independently reviewed pins; synthetic tests substitute only this anchor."""

    manifest_sha256: str
    receipt_sha256: str
    series_count: int
    sku_count: int
    warehouse_count: int


_VERIFIED_SOURCE = _SourceAnchor(
    "adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43",
    "853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692",
    250,
    50,
    5,
)


class ForecastExportError(ValueError):
    """No usable prospective export; callers must not substitute forecasts."""

    reason_code = "source_unverified"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ForecastExportError(message)


def _digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


def _json(data: bytes) -> Any:
    # Do not import final_authorization.read_json: its dependency graph imports
    # scientific verification/model code. Keep this parser standard-library only.
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            _require(key not in result, "Duplicate JSON field.")
            result[key] = value
        return result

    def invalid_constant(value: str) -> Any:
        raise ForecastExportError("Non-finite JSON constant: " + value)

    return json.loads(data, object_pairs_hook=unique, parse_constant=invalid_constant)


def _receipts(layout: RepositoryLayout, rows: Any) -> dict[str, dict[str, str]]:
    _require(isinstance(rows, list), "File bindings must be a list.")
    result: dict[str, dict[str, str]] = {}
    roots = {
        "artifacts": f"artifacts/forecasting/{RUN_ID}",
        "models": f"models/forecasting/{RUN_ID}",
        "reports": f"reports/forecasting/{RUN_ID}",
    }
    for row in rows:
        _require(
            isinstance(row, dict) and set(row) == {"path", "owner", "sha256"},
            "Malformed file binding.",
        )
        relative, owner = row["path"], row["owner"]
        _require(
            isinstance(relative, str)
            and isinstance(owner, str)
            and owner in roots
            and _digest(row["sha256"]),
            "Invalid file path, owner or hash.",
        )
        reference = PurePosixPath(relative)
        _require(
            not reference.is_absolute()
            and ".." not in reference.parts
            and "\\" not in relative
            and reference.as_posix() == relative,
            "Invalid repository-relative file path.",
        )
        # Historical final reports may retain their original drafts receipt.
        allowed = [PurePosixPath(roots[owner])]
        if owner == "reports":
            allowed.append(PurePosixPath(f"reports/forecasting/drafts/{RUN_ID}"))
        _require(
            any(
                reference.is_relative_to(root) and reference != root for root in allowed
            ),
            "File binding crosses its owner or run.",
        )
        layout._owned_path(layout.repository_path(relative))
        _require(relative not in result, "Duplicate file binding.")
        result[relative] = row
    return result


def _read_bound(
    layout: RepositoryLayout, relative: str, bindings: dict[str, dict[str, str]]
) -> bytes:
    _require(relative in bindings, "Missing required file binding: " + relative)
    data = layout._owned_path(layout.repository_path(relative)).read_bytes()
    _require(
        hashlib.sha256(data).hexdigest() == bindings[relative]["sha256"],
        "Source file hash differs: " + relative,
    )
    return data


def _identity(row: dict[str, Any]) -> tuple[str, int, str]:
    horizon, model, configuration = (
        row["horizon"],
        row["model"],
        row["configuration_id"],
    )
    _require(
        type(horizon) is int and horizon in (1, 7, 14, 28),
        "Unsupported evidence horizon.",
    )
    _require(
        isinstance(model, str)
        and bool(model)
        and isinstance(configuration, str)
        and bool(configuration),
        "Malformed producer identity.",
    )
    return model, horizon, configuration


def _timing(row: dict[str, Any]) -> None:
    _require(
        row["run_id"] == RUN_ID and row["evaluation_stage"] == "final_evaluation",
        "Run or evaluation stage differs.",
    )
    _require(
        row["training_start"] == TRAINING_START
        and row["training_end"] == ORIGIN
        and row["forecast_origin"] == ORIGIN,
        "Training window or forecast origin differs.",
    )
    horizon = _identity(row)[1]
    start = (date.fromisoformat(ORIGIN) + timedelta(days=1)).isoformat()
    end = (date.fromisoformat(ORIGIN) + timedelta(days=horizon)).isoformat()
    _require(
        row["target_start_date"] == start and row["target_end_date"] == end,
        "Target interval differs from origin + 1 through origin + horizon.",
    )


def _forecast_type(horizon: int) -> str:
    return "next_day" if horizon == 1 else "cumulative_window"


def _producer_reference(
    layout: RepositoryLayout,
    candidate: dict[str, Any],
    bindings: dict[str, dict[str, str]],
    sealed: dict[str, dict[str, str]],
) -> dict[str, str]:
    artifact = candidate["model_artifact"]
    _require(
        isinstance(artifact, dict) and _identity(artifact) == _identity(candidate),
        "Producer model reference identity differs.",
    )
    model, horizon, configuration = _identity(candidate)
    prefix = f"models/forecasting/{RUN_ID}/final/{model}/h{horizon}/{configuration}"
    filenames = {
        "model": "model.txt" if model == "lightgbm" else "model.ubj",
        "descriptor": "descriptor.json",
        "preprocessor": "state.json",
        "origin_features": "origin_features.json",
    }
    result = {}
    for name in REFERENCE_NAMES:
        relative, digest = artifact[name + "_path"], artifact[name + "_hash"]
        _require(
            relative == f"{prefix}/{filenames[name]}" and _digest(digest),
            "Producer reference path or hash differs.",
        )
        _require(
            relative in bindings
            and bindings[relative]["owner"] == "models"
            and bindings[relative]["sha256"] == digest
            and sealed.get(relative) == bindings[relative],
            "Producer reference is not bound to manifest and receipt.",
        )
        # Read native models and JSON descriptors/states as bytes only.
        with layout._owned_path(layout.repository_path(relative)).open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        _require(actual == digest, "Producer reference bytes changed.")
        result[name + "_path"], result[name + "_hash"] = relative, digest
    return result


def _build_export(layout: RepositoryLayout, anchor: _SourceAnchor) -> dict[str, Any]:
    directory = layout.run_directory(RUN_ID)
    manifest_path = directory / "run_manifest.json"
    manifest_bytes = layout._owned_path(manifest_path).read_bytes()
    _require(
        hashlib.sha256(manifest_bytes).hexdigest() == anchor.manifest_sha256,
        "Independently pinned manifest hash differs.",
    )
    manifest = _json(manifest_bytes)
    _require(
        isinstance(manifest, dict)
        and manifest["manifest_version"] == 2
        and type(manifest["manifest_version"]) is int
        and manifest["run_id"] == RUN_ID
        and manifest["schema_version"] == SOURCE_SCHEMA
        and manifest["evaluation_stage"] == "final_evaluation"
        and manifest["final_status"] == "verified_completed",
        "Final completion identity or status differs.",
    )
    bindings = _receipts(layout, manifest["files"])
    prefix = f"artifacts/forecasting/{RUN_ID}"
    values = {
        name: _read_bound(layout, f"{prefix}/{name}", bindings)
        for name in (
            "run_metadata.json",
            "prediction_receipt.json",
            "candidates.json",
            "predictions.json",
        )
    }
    _require(
        hashlib.sha256(values["prediction_receipt.json"]).hexdigest()
        == anchor.receipt_sha256,
        "Independently pinned prediction receipt hash differs.",
    )
    metadata, receipt, candidates, predictions = (
        _json(values[name])
        for name in (
            "run_metadata.json",
            "prediction_receipt.json",
            "candidates.json",
            "predictions.json",
        )
    )
    _require(
        isinstance(metadata, dict)
        and isinstance(receipt, dict)
        and isinstance(candidates, list)
        and isinstance(predictions, list),
        "Malformed final source documents.",
    )
    _require(
        metadata["run_id"] == RUN_ID
        and metadata["schema_version"] == SOURCE_SCHEMA
        and metadata["evaluation_stage"] == "final_evaluation"
        and metadata["run_status"] == "verified_completed"
        and metadata["completed_at_utc"] == manifest["completed_at_utc"]
        and isinstance(manifest["completed_at_utc"], str)
        and bool(manifest["completed_at_utc"])
        and metadata["prediction_receipt_hash"] == anchor.receipt_sha256,
        "Metadata and completion manifest differ.",
    )
    expected_integrity = {
        "status": "passed",
        "evaluations": 28,
        "learned_refits": 20,
        "baseline_evaluations": 8,
        "predictions": 28 * anchor.series_count,
        "models_replayed": 20,
    }
    integrity = manifest["integrity_result"]
    _require(
        isinstance(integrity, dict)
        and set(integrity) == INTEGRITY_FIELDS
        and integrity == metadata["integrity_result"] == expected_integrity
        and all(type(integrity[k]) is int for k in INTEGRITY_FIELDS - {"status"}),
        "Recorded integrity result is absent, failed or inconsistent.",
    )
    temporal = metadata["temporal_policy"]
    _require(
        temporal
        == {
            "training_start": TRAINING_START,
            "training_end": ORIGIN,
            "forecast_origin": ORIGIN,
            "target_start_date": "2024-12-03",
            "outcome_window_end": "2024-12-30",
        },
        "Retained temporal policy differs.",
    )
    mapping = [
        {"horizon": h, "model": m, "configuration_id": c} for h, m, c in PRODUCERS
    ]
    _require(
        metadata["producer_mapping"] == mapping
        and all(type(r["horizon"]) is int for r in metadata["producer_mapping"]),
        "Frozen designated producer mapping differs.",
    )
    raw_roster = metadata["pair_roster"]
    _require(
        isinstance(raw_roster, list)
        and all(
            isinstance(p, list)
            and len(p) == 2
            and all(isinstance(v, str) and bool(v) for v in p)
            for p in raw_roster
        ),
        "Malformed SKU/warehouse roster.",
    )
    roster = [tuple(p) for p in raw_roster]
    _require(
        len(roster) == anchor.series_count and sorted(set(roster)) == roster,
        "SKU/warehouse roster is incomplete, duplicated or unordered.",
    )
    roster_set = set(roster)
    skus, warehouses = {p[0] for p in roster}, {p[1] for p in roster}
    _require(
        len(skus) == anchor.sku_count
        and len(warehouses) == anchor.warehouse_count
        and roster_set == {(s, w) for s in skus for w in warehouses},
        "SKU/warehouse population differs from the approved complete grid.",
    )
    scope = metadata["scope"]
    _require(
        isinstance(scope, list)
        and scope == metadata["candidates"]
        and len(scope) == 28,
        "Final candidate scope differs.",
    )
    scope_keys = {_identity(c) for c in scope}
    _require(
        len(scope_keys) == 28 and len(candidates) == 28,
        "Duplicate or incomplete final candidates.",
    )
    _require(
        receipt["receipt_version"] == 1
        and type(receipt["receipt_version"]) is int
        and receipt["run_id"] == RUN_ID
        and receipt["evaluation_stage"] == "final_evaluation"
        and type(receipt["candidate_count"]) is int
        and receipt["candidate_count"] == 28
        and type(receipt["prediction_count"]) is int
        and receipt["prediction_count"] == 28 * anchor.series_count,
        "Prediction receipt identity or population differs.",
    )
    sealed = _receipts(layout, receipt["files"])
    _require(
        all(bindings.get(p) == r for p, r in sealed.items()),
        "Prediction receipt and completion bindings differ.",
    )
    for name in ("candidates.json", "predictions.json"):
        relative = f"{prefix}/{name}"
        _require(
            sealed.get(relative) == bindings[relative],
            "Missing sealed prediction/candidate binding.",
        )
    indexed = {}
    for candidate in candidates:
        _require(isinstance(candidate, dict), "Malformed final candidate.")
        _timing(candidate)
        key = _identity(candidate)
        _require(
            key in scope_keys
            and key not in indexed
            and candidate["candidate_status"] == "completed",
            "Candidate is unavailable, duplicated or outside declared scope.",
        )
        indexed[key] = candidate
    designated = {(m, h, c) for h, m, c in PRODUCERS}
    _require(
        designated <= indexed.keys(),
        "Missing designated producer; no substitute is permitted.",
    )
    producer_rows = []
    for horizon, model, configuration in PRODUCERS:
        candidate = indexed[model, horizon, configuration]
        _require(
            candidate["evidence_role"] == "primary"
            and candidate["canonical_config_id"] == configuration,
            "Designated producer identity differs.",
        )
        producer_rows.append(
            {
                "horizon": horizon,
                "model": model,
                "configuration_id": configuration,
                "forecast_type": _forecast_type(horizon),
                "model_reference": _producer_reference(
                    layout, candidate, bindings, sealed
                ),
            }
        )
    records, seen = [], set()
    for row in predictions:
        _require(isinstance(row, dict), "Malformed prediction record.")
        _timing(row)
        key = _identity(row)
        _require(key in indexed, "Prediction has no declared candidate.")
        pair = row["SKU_ID"], row["Warehouse_ID"]
        _require(
            all(isinstance(v, str) for v in pair) and pair in roster_set,
            "Prediction SKU/warehouse identity is outside the declared roster.",
        )
        identity = (*key, *pair)
        _require(
            identity not in seen, "Duplicate forecast identity within candidate rows."
        )
        seen.add(identity)
        quantity = row["prediction"]
        _require(
            type(quantity) in (int, float) and math.isfinite(quantity),
            "Prediction quantity is missing, malformed or non-finite.",
        )
        if key in designated:
            _require(
                row["evidence_role"] == "primary"
                and row["canonical_config_id"] == key[2],
                "Prediction designated producer identity differs.",
            )
            record = {k: row[k] for k in RECORD_SOURCE_FIELDS}
            record.update(
                forecast_type=_forecast_type(row["horizon"]),
                unit="units",
                producer_status="designated_producer",
                forecast_status="available",
                uncertainty={"status": "unavailable", "reason": "no_agreed_method"},
            )
            records.append(record)
    expected = {(*key, *pair) for key in scope_keys for pair in roster}
    _require(
        seen == expected and len(records) == 4 * anchor.series_count,
        "Incomplete forecast population; no partial export is permitted.",
    )
    records.sort(key=lambda r: (r["horizon"], r["SKU_ID"], r["Warehouse_ID"]))
    return {
        "export_schema": EXPORT_SCHEMA,
        "source": {
            "run_id": RUN_ID,
            "evaluation_stage": "final_evaluation",
            "source_schema": SOURCE_SCHEMA,
            "run_manifest_path": manifest_path.relative_to(layout.root).as_posix(),
            "run_manifest_sha256": anchor.manifest_sha256,
            "prediction_receipt_sha256": anchor.receipt_sha256,
            "integrity_result": dict(integrity),
        },
        "forecast_origin": ORIGIN,
        "training_start": TRAINING_START,
        "training_end": ORIGIN,
        "producers": producer_rows,
        "series_count": anchor.series_count,
        "record_count": len(records),
        "forecasts": records,
    }


def build_forecast_export(repository: Path = REPOSITORY) -> dict[str, Any]:
    """Check only the pinned retained source and return the prospective document.

    Does not write files. Invalid/unavailable source raises ForecastExportError
    with reason_code='source_unverified'; there is no zero or alternate-run fallback.
    """
    try:
        return _build_export(RepositoryLayout(repository), _VERIFIED_SOURCE)
    except ForecastExportError:
        raise
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OverflowError,
    ) as exc:
        raise ForecastExportError(
            "Required forecasting evidence is missing or malformed."
        ) from exc


def write_forecast_export(repository: Path = REPOSITORY) -> dict[str, str]:
    """Write exclusively to the approved ignored destination; return its SHA-256.

    Invoke on the real bundle only after specific owner authorization. No hash
    sidecar is created: the reviewed hash belongs in the contract/API configuration.
    """
    document = build_forecast_export(repository)
    data = (
        json.dumps(
            document, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")
    layout = RepositoryLayout(repository)
    destination = layout._owned_path(layout.repository_path(DESTINATION))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, prefix=".forecast-export-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # An exclusive hard link publishes complete bytes without replacing any file.
        os.link(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink()
    return {"path": DESTINATION, "sha256": hashlib.sha256(data).hexdigest()}


def main() -> None:
    """Owner-run CLI; imports and --help never read retained evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    args = parser.parse_args()
    try:
        result = write_forecast_export(args.repository)
    except (ForecastExportError, OSError, ValueError) as exc:
        parser.exit(1, f"Forecast export failed: {exc}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
