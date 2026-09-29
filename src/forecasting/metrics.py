"""Frozen DR-006 metrics; unavailable results carry explicit JSON-safe status."""
from __future__ import annotations

from math import fsum, isfinite, sqrt
from typing import Any

import numpy as np

METRIC_NAMES = ("wape", "mae", "rmse", "bias")


def forecasting_metrics(actual: Any, prediction: Any) -> dict[str, Any]:
    """Score raw, aligned vectors. WAPE is a ratio; Bias is prediction - actual.

    No clipping, rounding, epsilon or partial-population scoring is performed.
    Empty/nonfinite vectors and numeric overflow remain diagnostic failures.
    """
    y, p = np.asarray(actual, dtype=float), np.asarray(prediction, dtype=float)
    if y.ndim != 1 or p.ndim != 1 or y.shape != p.shape:
        raise ValueError("Metrics require equally sized one-dimensional aligned vectors.")
    result: dict[str, Any] = {
        "n_predictions": len(y), **dict.fromkeys(METRIC_NAMES),
        "wape_denominator": None, "metric_status": "valid", "failure_reason": None,
    }
    reason = None
    if not len(y):
        reason = "empty_population"
    elif not np.isfinite(y).all():
        reason = "nonfinite_actual"
    elif not np.isfinite(p).all():
        reason = "nonfinite_prediction"
    if reason:
        return {**result, "metric_status": "failed", "failure_reason": reason}
    try:
        errors = [float(pi) - float(yi) for yi, pi in zip(y, p, strict=True)]
        absolute = fsum(abs(e) for e in errors)
        denominator = fsum(abs(float(yi)) for yi in y)
        values = {
            "wape": absolute / denominator if denominator else None,
            "mae": absolute / len(y),
            "rmse": sqrt(fsum(e * e for e in errors) / len(y)),
            "bias": fsum(errors) / len(y), "wape_denominator": denominator,
        }
        if not all(v is None or isfinite(v) for v in values.values()):
            raise OverflowError
    except (OverflowError, ValueError):
        return {**result, "metric_status": "failed", "failure_reason": "numeric_overflow"}
    result.update(values)
    if denominator == 0:
        result.update(metric_status="undefined_zero_actual_total",
                      failure_reason="WAPE denominator is zero.")
    return result


def four_fold_means(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Exactly folds 1..4, arithmetic means only; never pool or weight scores."""
    if any(r.get("evaluation_stage", "validation") != "validation" for r in records):
        raise ValueError("Final evidence cannot enter validation summaries.")
    ids = [r["fold_id"] for r in records]
    if len(ids) != len(set(ids)) or any(type(i) is not int or i not in (1, 2, 3, 4)
                                        for i in ids):
        raise ValueError("Duplicate or unapproved fold identity.")
    valid = [r for r in records if r["metric_status"] == "valid"
             and all(r.get(m) is not None and isfinite(r[m]) for m in METRIC_NAMES)]
    result = {
        "expected_fold_count": 4, "valid_fold_count": len(valid),
        "n_predictions": sum(r["n_predictions"] for r in records),
        **{f"mean_{m}": None for m in METRIC_NAMES},
        "metric_status": "unavailable", "failure_reason": "Incomplete or invalid four-fold evidence.",
    }
    if set(ids) == {1, 2, 3, 4} and len(valid) == 4:
        ordered = sorted(valid, key=lambda r: r["fold_id"])
        result.update({f"mean_{m}": fsum(r[m] / 4 for r in ordered) for m in METRIC_NAMES})
        result.update(metric_status="valid", failure_reason=None)
    return result
