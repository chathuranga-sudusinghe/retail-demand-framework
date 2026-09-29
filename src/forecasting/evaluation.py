"""Historical label intersection and fixed-origin preparation; no model fitting."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from typing import Any, cast

import numpy as np
import pandas as pd

from src.forecasting.baselines import baseline_history
from src.forecasting.configuration import PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.features import (
    KEY_COLUMNS, SERIES_COLUMNS, build_features, build_origin_features,
    feature_eligibility, prepare_demand,
)
from src.forecasting.preprocessing import (
    ForecastPreprocessor, fit_preprocessor, fit_primary_preprocessors,
)
from src.forecasting.targets import FORECAST_HORIZONS, build_horizon_targets
from src.forecasting.validation import VALIDATION_FOLDS, ValidationFold, split_fold


class PreflightError(ValueError):
    """A failed population carries diagnostics rather than repaired/dropped rows."""

    def __init__(self, message: str, diagnostics: list[dict[str, Any]] | None = None):
        super().__init__(message)
        self.diagnostics = diagnostics or []


def frame_hash(frame: pd.DataFrame) -> str:
    """Fingerprint an already scoped, ordered view; no raw file is hashed."""
    canonical = frame.copy()
    # A missing final-period value can change the original whole column's dtype.
    # Equivalent authorised numerical values must hash identically regardless.
    for column in canonical.select_dtypes(include="number").columns:
        canonical[column] = canonical[column].astype(float)
    digest = sha256(json.dumps(list(canonical.columns), separators=(",", ":")).encode())
    digest.update(pd.util.hash_pandas_object(canonical, index=False).to_numpy(dtype=np.uint64).tobytes())
    return digest.hexdigest()


def validation_view(data: pd.DataFrame, *, fold_number: int | None = None) -> pd.DataFrame:
    """Read dates to isolate authorised rows BEFORE demand/key validation or hashing.

    A fold view ends at its own outcome end; the run view ends December 2.
    Excluded future quantities, keys, duplicates and gaps never affect this view.
    Dates must be valid calendar keys so the isolation itself is unambiguous.
    """
    if not data.columns.is_unique or "Date" not in data:
        raise ValueError("Unique columns and Date are required.")
    if pd.api.types.is_numeric_dtype(data.Date.dtype):
        raise ValueError("Date must contain calendar dates.")
    dates = pd.to_datetime(data.Date, format="%Y-%m-%d", errors="raise")
    if dates.isna().any() or dates.dt.tz is not None or dates.ne(dates.dt.normalize()).any():
        raise ValueError("Date must be nonmissing timezone-naive calendar days.")
    if fold_number is not None and (type(fold_number) is not int or fold_number not in (1, 2, 3, 4)):
        raise ValueError("Only the four frozen validation folds are supported.")
    end = VALIDATION_FOLDS[(fold_number or 4) - 1].validation.end
    mask = dates.between(pd.Timestamp("2024-01-01"), pd.Timestamp(end))
    scoped = data.loc[mask].copy()
    scoped["Date"] = dates.loc[mask]
    return prepare_demand(scoped, require_daily=False)


def require_native_roster(training: pd.DataFrame) -> None:
    """Check documented native 50 x 5 coverage using historical identities only."""
    skus, warehouses = sorted(training.SKU_ID.unique()), sorted(training.Warehouse_ID.unique())
    pairs = set(training.loc[:, list(SERIES_COLUMNS)].itertuples(index=False, name=None))
    if len(skus) != 50 or len(warehouses) != 5 or pairs != set(product(skus, warehouses)):
        raise PreflightError("Historical pair roster does not match native 50-SKU x 5-warehouse coverage.")


@dataclass(frozen=True)
class PreparedHorizon:
    horizon: int
    features: pd.DataFrame
    labels: np.ndarray
    observed_targets: np.ndarray
    preprocessors: dict[str, ForecastPreprocessor]
    training_population_hash: str
    eligibility_records: list[dict[str, Any]]


@dataclass(frozen=True)
class PreparedFold:
    fold: ValidationFold
    origin_features: pd.DataFrame
    baseline_evidence: pd.DataFrame
    horizons: dict[int, PreparedHorizon]
    pair_key_hash: str
    input_view_hash: str


def prepare_fold(
    data: pd.DataFrame, fold_number: int, *, horizons: tuple[int, ...] = FORECAST_HORIZONS,
) -> PreparedFold:
    """Pure preparation usable with small synthetic panels; never runs estimators.

    The production entry additionally requires native coverage and a run approval.
    Strict fold coverage is retained. Every historical training pair must have a
    complete origin, all four targets, baseline history and known fitted categories.
    """
    if (not horizons or tuple(h for h in FORECAST_HORIZONS if h in horizons) != horizons
            or any(type(h) is not int for h in horizons)):
        raise ValueError("horizons must be an ordered unique subset of 1, 7, 14, 28.")
    scoped = validation_view(data, fold_number=fold_number)
    try:
        training, outcomes = split_fold(scoped, fold_number)
    except ValueError as exc:
        raise PreflightError(str(exc), [{"fold_id": fold_number,
                                        "input_view_hash": frame_hash(scoped),
                                        "failure_reason": str(exc)}]) from exc
    fold = VALIDATION_FOLDS[fold_number - 1]
    origin = build_origin_features(training, origin=fold.training.end)
    roster = training.loc[:, list(SERIES_COLUMNS)].drop_duplicates().reset_index(drop=True)
    origin_keys = origin.loc[:, list(SERIES_COLUMNS)].reset_index(drop=True)
    if not origin_keys.equals(roster) or not feature_eligibility(origin).all():
        bad = origin.loc[~feature_eligibility(origin), list(SERIES_COLUMNS)]
        raise PreflightError("Incomplete fixed-origin predictor population.", cast(list[dict[str, Any]], bad.to_dict("records")))
    history = baseline_history(training, origin=fold.training.end)
    if not history.loc[:, list(SERIES_COLUMNS)].equals(roster):
        raise PreflightError("Baseline population differs from the training roster.")
    historical_features = build_features(training)
    historical_targets = build_horizon_targets(
        training, window_start=fold.training.start, window_end=fold.training.end,
    )
    # Explicit one-to-one key joins, never positional assumptions between utilities.
    aligned = historical_features.loc[:, list(KEY_COLUMNS)].merge(
        historical_targets, on=list(KEY_COLUMNS), how="left", validate="one_to_one", sort=False,
    )
    if len(aligned) != len(historical_features):
        raise PreflightError("Historical feature/label key population mismatch.")
    observed = build_horizon_targets(
        outcomes, window_start=fold.validation.start, window_end=fold.validation.end,
    )
    observed = origin.loc[:, list(KEY_COLUMNS)].merge(
        observed, on=list(KEY_COLUMNS), how="left", validate="one_to_one", sort=False,
    )
    if observed.loc[:, [f"target_{h}_day" for h in horizons]].isna().any().any():
        bad = observed.loc[observed.isna().any(axis=1), list(KEY_COLUMNS)]
        raise PreflightError("Incomplete candidate-independent validation target population.",
                             cast(list[dict[str, Any]], bad.to_dict("records")))
    feature_mask = feature_eligibility(historical_features)
    pair_hash = frame_hash(roster)
    input_hash = frame_hash(scoped)
    prepared_horizons = {}
    for horizon in horizons:
        column = f"target_{horizon}_day"
        boundary = (aligned.Date + pd.Timedelta(days=horizon - 1)).le(pd.Timestamp(fold.training.end))
        label_mask = aligned[column].notna() & boundary
        accepted = feature_mask & label_mask
        features = historical_features.loc[accepted].reset_index(drop=True)
        labels = aligned.loc[accepted, column].to_numpy(dtype=float)
        reasons = {
            "incomplete_predictor_history": ~feature_mask,
            "target_after_training_cutoff": ~boundary,
            "missing_observed_training_target": boundary & aligned[column].isna(),
        }
        diagnostics = []
        for pair in roster.itertuples(index=False, name=None):
            mask = aligned.SKU_ID.eq(pair[0]) & aligned.Warehouse_ID.eq(pair[1])
            exclusions = {name: int((mask & condition).sum()) for name, condition in reasons.items()}
            overlaps = [name for name, condition in reasons.items()
                        if any(name != other and (mask & condition & other_mask).any()
                               for other, other_mask in reasons.items())]
            diagnostics.append({
                "fold_id": fold.number, "horizon": horizon,
                "SKU_ID": pair[0], "Warehouse_ID": pair[1],
                "raw_row_count": int(mask.sum()),
                "feature_eligible_count": int((mask & feature_mask).sum()),
                "label_eligible_count": int((mask & label_mask).sum()),
                "training_row_count": int((mask & accepted).sum()),
                "expected_origin_count": 1, "scored_origin_count": 0,
                "exclusion_counts": exclusions, "overlapping_reasons": overlaps,
                "pair_key_hash": pair_hash, "input_view_hash": input_hash,
            })
        if features.empty:
            raise PreflightError("No intersected eligible training population.", diagnostics)
        primary = fit_primary_preprocessors(features, training_end=fold.training.end, horizon=horizon)
        states: dict[str, ForecastPreprocessor] = {name: state for name, state in primary.items()}
        for model in SUPPORTIVE_MODELS:
            states[model] = fit_preprocessor(features, model, training_end=fold.training.end, horizon=horizon)
        try:
            reference = primary["xgboost"].transform(origin)
            for primary_model in PRIMARY_MODELS:
                pd.testing.assert_frame_equal(reference, primary[primary_model].transform(origin))
            for state in states.values():
                if state.training_row_count != len(features):
                    raise PreflightError("Preprocessing changed the intersected fitting population.")
                state.transform(origin)  # Unknown categories fail before ANY candidate fit.
        except ValueError as exc:
            raise PreflightError(str(exc), diagnostics) from exc
        population = features.loc[:, list(KEY_COLUMNS)].copy()
        population[column] = labels
        prepared_horizons[horizon] = PreparedHorizon(
            horizon, features, labels, observed[column].to_numpy(dtype=float), states,
            frame_hash(population), diagnostics,
        )
    return PreparedFold(fold, origin, history, prepared_horizons, pair_hash, input_hash)
