"""Operational progress only: no data access, model construction or approval."""
from __future__ import annotations

from datetime import datetime, timezone
import logging
import re
import sys
from pathlib import Path
from time import perf_counter
from typing import Any


class RunProgress:
    """A run-owned logger; root/library loggers and scientific artifacts stay untouched."""

    def __init__(self, directory: Path, run_id: str, *, primary_fits: int,
                 supportive_fits: int, baseline_evaluations: int):
        self.run_id = run_id
        self.total_fits = primary_fits + supportive_fits
        self.total_evaluations = self.total_fits + baseline_evaluations
        self.completed_fits = 0
        self.completed_evaluations = 0
        self.started = perf_counter()
        self.candidate_started = self.started
        self.context: dict[str, Any] = {}
        self.operation = "preflight"
        self.fit_completed = False
        self.candidate_failed = False
        # An unregistered logger avoids persistent global state or duplicate handlers.
        self.logger = logging.Logger(f"forecasting.run.{run_id}", level=logging.INFO)
        self.logger.propagate = False
        handlers: list[logging.Handler] = []
        try:
            handlers.append(logging.StreamHandler(sys.stdout))
            handlers.append(logging.FileHandler(directory / "run.log", mode="x", encoding="utf-8"))
            for handler in handlers:
                handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
                self.logger.addHandler(handler)
            self._emit("run_start", primary_fits=primary_fits, supportive_fits=supportive_fits,
                       baseline_evaluations=baseline_evaluations,
                       planned_fits=self.total_fits, planned_evaluations=self.total_evaluations)
        except BaseException as exc:
            self._close_handlers(handlers, primary_error=exc)
            raise

    def _emit(self, event: str, *, level: int = logging.INFO, **details: Any) -> None:
        progress = 100 * self.completed_evaluations / self.total_evaluations if self.total_evaluations else 0
        fit_progress = 100 * self.completed_fits / self.total_fits if self.total_fits else 0
        fields = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "run_id": self.run_id, "evaluation_stage": "validation", "event": event,
                  "operation": self.operation, "fold": self.context.get("fold_id", "-"),
                  "horizon": self.context.get("horizon", "-"),
                  "evidence_role": self.context.get("evidence_role", "-"),
                  "model": self.context.get("model", "-"),
                  "configuration_id": self.context.get("configuration_id", "-"),
                  "completed_fits": f"{self.completed_fits}/{self.total_fits}",
                  "fit_progress": f"{fit_progress:.2f}%",
                  "completed_evaluations": f"{self.completed_evaluations}/{self.total_evaluations}",
                  "progress": f"{progress:.2f}%", "elapsed_seconds": f"{perf_counter() - self.started:.3f}",
                  **details}
        self.logger.log(level, " ".join(f"{key}={value}" for key, value in fields.items()))

    def phase(self, operation: str) -> None:
        self.context = {}
        self.operation = operation
        self._emit("phase_start")

    def start_candidate(self, keys: dict[str, Any], *, learned: bool) -> None:
        # Explicit allowlist: never pass metadata, arrays, predictions or exception payloads.
        self.context = {key: keys[key] for key in
                        ("fold_id", "horizon", "evidence_role", "model", "configuration_id")}
        self.candidate_started = perf_counter()
        self.fit_completed = False
        self.candidate_failed = False
        self.operation = "estimator_fit" if learned else "baseline_evaluation"
        self._emit("fit_start" if learned else "baseline_start")

    def complete_fit(self) -> None:
        self.completed_fits += 1
        self.fit_completed = True
        self._emit("fit_complete", fit_elapsed_seconds=f"{perf_counter() - self.candidate_started:.3f}")
        self.operation = "prediction_and_metrics"

    def complete_candidate(self, *, learned: bool) -> None:
        self.completed_evaluations += 1
        self._emit("evaluation_complete" if learned else "baseline_complete",
                   candidate_elapsed_seconds=f"{perf_counter() - self.candidate_started:.3f}")
        self.context = {}

    def fail_candidate(self, exc: BaseException) -> None:
        self.candidate_failed = True
        self._emit("fit_failure" if self.operation == "estimator_fit" else "evaluation_failure",
                   level=logging.ERROR, **self._failure_details(exc))

    def _failure_details(self, exc: BaseException) -> dict[str, str]:
        # Known fixed messages are safe; arbitrary library exception text can embed
        # input rows, matrices, paths or secrets. Keep those in existing diagnostics.
        safe_messages = {
            "Validation input differs from the specifically authorised input view.",
            "Historical pair roster does not match native 50-SKU x 5-warehouse coverage.",
            "Pair roster changed between frozen validation folds.",
            "Incomplete candidate-independent validation target population.",
            "Incomplete fixed-origin predictor population.",
            "Prediction population is misaligned or nonfinite.",
            "Fit requires aligned nonempty finite training inputs and labels.",
            "Estimator no longer matches the frozen runtime recipe.",
            "Primary early stopping/callbacks are forbidden.",
            "Effective XGBoost CPU/thread/seed controls differ from the frozen recipe.",
            "Effective LightGBM runtime controls differ from the frozen recipe.",
            "Effective CatBoost runtime controls differ from the frozen recipe.",
            "Metrics require equally sized one-dimensional aligned vectors.",
            "empty_population", "nonfinite_actual", "nonfinite_prediction", "numeric_overflow",
        }
        message = str(exc)
        safe_iteration_counts = re.fullmatch(r"Iteration mismatch: requested [0-9]+, effective [0-9]+\.", message)
        reason = message if message in safe_messages or safe_iteration_counts else (
            f"{type(exc).__name__} during {self.operation}; detailed failure reason in diagnostics.json")
        return {"exception_type": type(exc).__name__, "reason": reason}

    def fail_run(self, exc: BaseException) -> None:
        if self.context and not self.candidate_failed:
            self.fail_candidate(exc)
        self._emit("run_failure", level=logging.ERROR, **self._failure_details(exc))

    def complete_run(self, status: str) -> None:
        self.context = {}
        self.operation = "finalizing" if status == "finalizing_verified" else "completed"
        self._emit("finalization_verified" if status == "finalizing_verified" else "run_complete", status=status,
                   total_elapsed_seconds=f"{perf_counter() - self.started:.3f}")

    def _close_handlers(
        self, handlers: list[logging.Handler], *, primary_error: BaseException | None = None,
    ) -> None:
        errors: list[BaseException] = []
        for handler in handlers:
            for action in (handler.flush, handler.close):
                try:
                    action()
                except BaseException as exc:
                    errors.append(exc)
            self.logger.removeHandler(handler)
        if primary_error is not None:
            for error in errors:
                primary_error.add_note(f"Progress handler cleanup failed: {type(error).__name__}.")
        elif errors:
            for error in errors[1:]:
                errors[0].add_note(f"Additional progress cleanup failure: {type(error).__name__}.")
            raise errors[0]

    def close(self) -> None:
        self._close_handlers(self.logger.handlers[:], primary_error=sys.exception())
