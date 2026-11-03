"""Synthetic checks for the Issue #203 consumer-evidence helper.

No saved model, artifact or research run is used: a deterministic in-memory
fake implements the documented request-time HTTP contract, and recorded
exchanges are mutated to prove each requirement outcome is derived from an
actual assertion rather than written as a constant.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import hashlib
import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Any

import pytest

import capture_consumer_evidence as cce

SKU = "SKU_SYN_A"
WAREHOUSE = "WH_SYN_1"
ORIGIN = date(2025, 1, 28)
VALUES = [
    11,
    12,
    14,
    15,
    17,
    16,
    13,
    12,
    13,
    15,
    16,
    18,
    17,
    14,
    13,
    14,
    16,
    17,
    19,
    18,
    15,
    13,
    14,
    16,
    17,
    20,
    18,
    15,
]
REQUEST_FIELDS = {
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "input_kind",
    "history",
}
LIMITATIONS = [
    "Synthetic demo input is illustrative supplied history.",
    "Multi-day quantities are cumulative totals, not daily paths.",
    "28-day forecast availability does not approve downstream inventory use.",
]
FIXED_NOW = datetime(2026, 10, 28, 4, 0, tzinfo=UTC)


def synthetic_example(horizon: int) -> dict[str, Any]:
    return {
        "SKU_ID": SKU,
        "Warehouse_ID": WAREHOUSE,
        "forecast_origin": ORIGIN.isoformat(),
        "horizon": horizon,
        "input_kind": "synthetic_demo",
        "history": cce.dated_history(ORIGIN, VALUES),
    }


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class FakeResponse:
    status_code: int
    payload: Any

    def json(self) -> Any:
        return copy.deepcopy(self.payload)


def _domain_error(reason: str) -> FakeResponse:
    return FakeResponse(422, {"detail": {"reason_code": reason, "message": reason}})


def fake_forecast(request: dict[str, Any]) -> FakeResponse:
    """Deterministic stand-in for POST /forecasts following the documented contract."""
    extras = sorted(set(request) - REQUEST_FIELDS)
    if extras:
        return FakeResponse(
            422,
            {
                "detail": [
                    {
                        "type": "extra_forbidden",
                        "loc": ["body", field],
                        "msg": "Extra inputs are not permitted",
                    }
                    for field in extras
                ]
            },
        )
    horizon = request["horizon"]
    if horizon not in cce.PRODUCERS:
        return _domain_error("unsupported_horizon")
    if request["SKU_ID"] != SKU:
        return _domain_error("unknown_sku")
    if request["Warehouse_ID"] != WAREHOUSE:
        return _domain_error("unknown_warehouse")
    origin = date.fromisoformat(request["forecast_origin"])
    if origin < cce.SAVED_MODEL_BOUNDARY:
        return _domain_error("invalid_origin")
    dates = sorted(date.fromisoformat(row["Date"]) for row in request["history"])
    if dates[-1] > origin:
        return _domain_error("future_history")
    if any((later - earlier).days != 1 for earlier, later in pairwise(dates)):
        return _domain_error("invalid_history")
    if dates[-1] != origin:
        return _domain_error("incomplete_history")
    model, config = cce.PRODUCERS[horizon]
    base = f"{cce.MODEL_ROOT}/{model}/h{horizon}/{config}"
    history = sorted(request["history"], key=lambda row: row["Date"])
    return FakeResponse(
        200,
        {
            "inference_schema": "forecast-inference-v1",
            "inference_mode": "request_time",
            "input_kind": request["input_kind"],
            "model_source_run_id": cce.SOURCE_RUN_ID,
            "manifest_reference": cce.MANIFEST_REFERENCE,
            "manifest_sha256": _digest("manifest"),
            "SKU_ID": request["SKU_ID"],
            "Warehouse_ID": request["Warehouse_ID"],
            "forecast_origin": request["forecast_origin"],
            "horizon": horizon,
            "target_start_date": (origin + timedelta(days=1)).isoformat(),
            "target_end_date": (origin + timedelta(days=horizon)).isoformat(),
            "forecast_type": "next_day" if horizon == 1 else "cumulative_window",
            "forecast_quantity": sum(row["Units_Sold"] for row in history[-7:])
            * horizon
            / 7,
            "model": model,
            "configuration_id": config,
            "producer_designation": "frozen_designated_producer",
            "provenance": {
                "model_path": f"{base}/model.txt",
                "model_hash": _digest(f"model-{horizon}"),
                "preprocessor_path": f"{base}/state.json",
                "preprocessor_hash": _digest(f"preprocessor-{horizon}"),
                "input_sha256": _digest(json.dumps(request, sort_keys=True)),
            },
            "status": "available",
            "unavailable_reasons": [],
            "assumptions": [
                "Forecast uses only the supplied history through forecast_origin."
            ],
            "limitations": list(LIMITATIONS),
        },
    )


class FakeClient:
    def __init__(self) -> None:
        self.gets: list[str] = []
        self.posts: list[dict[str, Any]] = []

    def get(self, url: str) -> FakeResponse:
        self.gets.append(url)
        return FakeResponse(
            200,
            {
                "status": "ready",
                "available_horizons": [1, 7, 14, 28],
                "unavailable_reasons": [],
            },
        )

    def post(self, url: str, *, json: Any) -> FakeResponse:
        assert url == "/forecasts"
        self.posts.append(copy.deepcopy(json))
        return fake_forecast(copy.deepcopy(json))


@pytest.fixture
def examples_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "examples" / "forecast-api"
    directory.mkdir(parents=True)
    for horizon in cce.HORIZONS:
        (directory / f"forecast-{horizon}-day.json").write_text(
            json.dumps(synthetic_example(horizon), indent=2) + "\n", encoding="utf-8"
        )
    return directory


@pytest.fixture
def record(examples_dir: Path) -> dict[str, Any]:
    return cce.collect_exchanges(FakeClient(), examples_dir)


def failed_requirements(rec: dict[str, Any]) -> set[str]:
    outcomes = cce.derive_outcomes(cce.evaluate_record(rec))
    return {
        name for name, outcome in outcomes.items() if outcome["outcome"] == "FAILED"
    }


def body(rec: dict[str, Any], horizon: int) -> dict[str, Any]:
    entry = next(e for e in rec["examples"] if e["horizon"] == horizon)
    result: dict[str, Any] = entry["body"]
    return result


def rejection(rec: dict[str, Any], case: str) -> dict[str, Any]:
    result: dict[str, Any] = next(r for r in rec["rejections"] if r["case"] == case)
    return result


# --------------------------------------------------------------------------
# Derivation of outcomes
# --------------------------------------------------------------------------


def test_synthetic_capture_derives_every_requirement_from_checks(
    examples_dir: Path,
) -> None:
    client = FakeClient()
    rec = cce.collect_exchanges(client, examples_dir)
    evidence = cce.build_evidence(rec, {"title": "synthetic"})

    assert evidence["overall_outcome"] == "PASSED"
    assert set(evidence["requirement_outcomes"]) == set(cce.REQUIREMENTS)
    for outcome in evidence["requirement_outcomes"].values():
        assert outcome["outcome"] == "PASSED"
        assert outcome["checks_total"] > 0
        assert outcome["checks_failed"] == []
    # health + 4 horizons + repeat + changed history + 10 rejection requests
    assert client.gets == ["/health"]
    assert [p["horizon"] for p in client.posts[:4]] == [1, 7, 14, 28]
    assert len(client.posts) == 4 + 1 + 1 + 10
    assert {r["case"] for r in rec["rejections"]} == {
        "unknown_sku",
        "unknown_warehouse",
        "unsupported_horizon",
        "invalid_origin",
        "future_history",
        "incomplete_history",
        "invalid_history",
        "extra_observed_target",
        "extra_Demand_Forecast",
        "extra_Inventory_Level",
    }


def test_requirements_without_checks_are_failed_not_assumed() -> None:
    outcomes = cce.derive_outcomes([])
    assert {o["outcome"] for o in outcomes.values()} == {"FAILED"}
    assert cce.overall_outcome(outcomes) == "FAILED"
    assert cce.overall_outcome({}) == "FAILED"


def _set(horizon: int, key: str, value: Any) -> Callable[[dict[str, Any]], None]:
    def mutate(rec: dict[str, Any]) -> None:
        body(rec, horizon)[key] = value

    return mutate


def _set_provenance(
    horizon: int, key: str, value: Any
) -> Callable[[dict[str, Any]], None]:
    def mutate(rec: dict[str, Any]) -> None:
        body(rec, horizon)["provenance"][key] = value

    return mutate


def _rename_model_hash(rec: dict[str, Any]) -> None:
    provenance = body(rec, 7)["provenance"]
    provenance["model_sha256"] = provenance.pop("model_hash")


def _drop_h28_limitation(rec: dict[str, Any]) -> None:
    body(rec, 28)["limitations"] = LIMITATIONS[:2]


def _health_unavailable(rec: dict[str, Any]) -> None:
    rec["health"]["body"]["status"] = "unavailable"


def _example_file_changed(rec: dict[str, Any]) -> None:
    rec["examples"][2]["file_sha256_after"] = "0" * 64


def _missing_h14(rec: dict[str, Any]) -> None:
    rec["examples"] = [e for e in rec["examples"] if e["horizon"] != 14]


def _changed_history_ignored(rec: dict[str, Any]) -> None:
    rec["changed_history"]["body"]["provenance"]["input_sha256"] = body(rec, 1)[
        "provenance"
    ]["input_sha256"]


def _changed_history_wrong_increment(rec: dict[str, Any]) -> None:
    rec["changed_history"]["request"]["history"][-1]["Units_Sold"] += 1


def _changed_history_other_producer(rec: dict[str, Any]) -> None:
    rec["changed_history"]["body"]["configuration_id"] = "GBM001"


def _repeat_hash_differs(rec: dict[str, Any]) -> None:
    rec["repeat_request"]["body"]["provenance"]["input_sha256"] = "f" * 64


def _unknown_sku_accepted(rec: dict[str, Any]) -> None:
    entry = rejection(rec, "unknown_sku")
    entry["http_status"] = 200
    entry["body"] = copy.deepcopy(body(rec, 1))


def _wrong_reason(rec: dict[str, Any]) -> None:
    rejection(rec, "future_history")["body"]["detail"]["reason_code"] = (
        "incomplete_history"
    )


def _extra_field_accepted(rec: dict[str, Any]) -> None:
    entry = rejection(rec, "extra_observed_target")
    entry["http_status"] = 200
    entry["body"] = copy.deepcopy(body(rec, 1))


def _rejection_leaks_quantity(rec: dict[str, Any]) -> None:
    rejection(rec, "invalid_origin")["body"]["detail"]["forecast_quantity"] = 0.0


def _rejection_request_tampered(rec: dict[str, Any]) -> None:
    rejection(rec, "invalid_history")["request"] = synthetic_example(1)


def _unsupported_horizon_accepted(rec: dict[str, Any]) -> None:
    rejection(rec, "unsupported_horizon")["http_status"] = 200


@pytest.mark.parametrize(
    "mutate,expected_failed",
    [
        (_set(7, "Warehouse_ID", "WH_SYN_2"), {"AS-01"}),
        (_set(7, "target_start_date", ORIGIN.isoformat()), {"AS-02", "AS-03"}),
        (
            _set(14, "target_end_date", (ORIGIN + timedelta(days=13)).isoformat()),
            {"AS-03"},
        ),
        (
            _set(1, "forecast_type", "cumulative_window"),
            {"AS-04", "RT-CHANGED-HISTORY"},
        ),
        (_set(7, "horizon", "7"), {"AS-04"}),
        (_drop_h28_limitation, {"AS-04"}),
        (_set(14, "producer_designation", "candidate"), {"AS-05"}),
        (_set(28, "configuration_id", "GBM001"), {"AS-05"}),
        (_rename_model_hash, {"AS-05"}),
        (
            _set_provenance(1, "preprocessor_hash", "abc"),
            {"AS-05", "RT-CHANGED-HISTORY"},
        ),
        (_set_provenance(7, "model_path", "models/other/model.txt"), {"AS-05"}),
        (_set(7, "observed_target", 15), {"AS-06"}),
        (_set_provenance(14, "Inventory_Level", 40), {"AS-05", "AS-06"}),
        (_set(1, "inference_mode", "retained"), {"AS-06"}),
        (_set(7, "status", "unavailable"), {"RT-CONTRACT"}),
        (_set(7, "forecast_quantity", "90.06"), {"RT-CONTRACT"}),
        (_health_unavailable, {"RT-CONTRACT"}),
        (_example_file_changed, {"RT-CONTRACT"}),
        (
            _missing_h14,
            {"AS-01", "AS-02", "AS-03", "AS-04", "AS-05", "AS-06", "RT-CONTRACT"},
        ),
        (_changed_history_ignored, {"AS-05", "RT-CHANGED-HISTORY"}),
        (_changed_history_wrong_increment, {"RT-CHANGED-HISTORY"}),
        (_changed_history_other_producer, {"RT-CHANGED-HISTORY"}),
        (_repeat_hash_differs, {"AS-05", "RT-CHANGED-HISTORY"}),
        (_unknown_sku_accepted, {"AS-01", "RT-REJECTIONS"}),
        (_unsupported_horizon_accepted, {"AS-04", "RT-REJECTIONS"}),
        (_wrong_reason, {"RT-REJECTIONS"}),
        (_extra_field_accepted, {"AS-06", "RT-REJECTIONS"}),
        (_rejection_leaks_quantity, {"RT-REJECTIONS"}),
        (_rejection_request_tampered, {"RT-REJECTIONS"}),
    ],
)
def test_each_violation_fails_exactly_its_requirements(
    record: dict[str, Any],
    mutate: Callable[[dict[str, Any]], None],
    expected_failed: set[str],
) -> None:
    assert failed_requirements(record) == set()
    mutate(record)
    assert failed_requirements(record) == expected_failed
    evidence = cce.build_evidence(record, {})
    assert evidence["overall_outcome"] == "FAILED"


def test_unchanged_quantity_after_changed_history_is_informational(
    record: dict[str, Any],
) -> None:
    record["changed_history"]["body"]["forecast_quantity"] = body(record, 1)[
        "forecast_quantity"
    ]
    assert failed_requirements(record) == set()
    observations = cce.derive_observations(record)
    assert observations["changed_history_forecast_quantity_changed"] is False


def test_rejection_requests_are_built_in_memory_from_the_valid_example() -> None:
    base = synthetic_example(1)
    original = copy.deepcopy(base)
    cases = {case.case_id: case.payload for case in cce.build_rejection_cases(base)}
    assert base == original

    def dates(payload: dict[str, Any]) -> list[date]:
        return sorted(date.fromisoformat(row["Date"]) for row in payload["history"])

    invalid_origin = cases["invalid_origin"]
    assert (
        date.fromisoformat(invalid_origin["forecast_origin"]) < cce.SAVED_MODEL_BOUNDARY
    )
    assert dates(invalid_origin)[-1] == date.fromisoformat(
        invalid_origin["forecast_origin"]
    )
    assert dates(cases["future_history"])[-1] == ORIGIN + timedelta(days=1)
    assert (
        cases["incomplete_history"]["forecast_origin"]
        == (ORIGIN + timedelta(days=1)).isoformat()
    )
    assert dates(cases["incomplete_history"])[-1] == ORIGIN

    gapped = dates(cases["invalid_history"])
    assert len(gapped) == len(VALUES) and gapped[-1] == ORIGIN
    assert len(set(gapped)) == len(gapped)
    assert max((b - a).days for a, b in pairwise(gapped)) == 2
    assert sum((b - a).days != 1 for a, b in pairwise(gapped)) == 1

    changed = cce.build_changed_history_request(base)
    assert (
        changed["history"][-1]["Units_Sold"]
        == VALUES[-1] + cce.CHANGED_HISTORY_INCREMENT
    )
    assert changed["history"][:-1] == base["history"][:-1]
    assert base == original


# --------------------------------------------------------------------------
# Evidence preservation
# --------------------------------------------------------------------------


def test_exclusive_write_never_overwrites_existing_evidence(tmp_path: Path) -> None:
    target = tmp_path / "issue-203" / "consumer-evidence.json"
    target.parent.mkdir()
    target.write_bytes(b'{"existing": true}\n')
    with pytest.raises(FileExistsError):
        cce.write_evidence_exclusive(target, b'{"replacement": true}\n')
    assert target.read_bytes() == b'{"existing": true}\n'


def test_written_hash_matches_lf_bytes_on_disk(tmp_path: Path) -> None:
    data = cce.serialise_evidence({"a": [1, 2], "b": "text"})
    assert b"\r\n" not in data and data.endswith(b"\n")
    target = tmp_path / "new" / "evidence.json"
    digest = cce.write_evidence_exclusive(target, data)
    assert digest == hashlib.sha256(target.read_bytes()).hexdigest()
    assert target.read_bytes() == data


@contextlib.contextmanager
def _fake_factory(client: Any) -> Iterator[Any]:
    yield client


def _clean_git(_: Path) -> cce.GitState:
    return cce.GitState("a" * 40, True)


def _run_main(
    argv: list[str],
    client: Any = None,
    git: Callable[[Path], cce.GitState] = _clean_git,
) -> int:
    def factory() -> Any:
        if client is None:
            raise AssertionError("the API must not be contacted")
        return _fake_factory(client)

    return cce.main(
        argv, client_factory=factory, git_reader=git, clock=lambda: FIXED_NOW
    )


def test_main_refuses_existing_output_before_contacting_api(
    tmp_path: Path, examples_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "consumer-evidence.json"
    output.write_bytes(b"original evidence\n")
    code = _run_main(["--output", str(output), "--examples-dir", str(examples_dir)])
    assert code == 2
    assert output.read_bytes() == b"original evidence\n"


def test_main_refuses_dirty_tree(
    tmp_path: Path, examples_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "out.json"
    code = _run_main(
        ["--output", str(output), "--examples-dir", str(examples_dir)],
        git=lambda _: cce.GitState("a" * 40, False),
    )
    assert code == 2 and not output.exists()


def test_main_dry_run_and_failed_capture_write_nothing(
    tmp_path: Path, examples_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "out.json"
    args = ["--output", str(output), "--examples-dir", str(examples_dir)]
    assert _run_main([*args, "--dry-run"], FakeClient()) == 0
    assert not output.exists()

    class WrongWindowClient(FakeClient):
        def post(self, url: str, *, json: Any) -> FakeResponse:
            response = super().post(url, json=json)
            if response.status_code == 200 and response.payload["horizon"] == 7:
                response.payload["target_end_date"] = "2025-02-05"
            return response

    assert _run_main(args, WrongWindowClient()) == 1
    assert not output.exists()


def test_capture_verify_and_documentation_values_agree(
    tmp_path: Path, examples_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    previous = tmp_path / cce.PREVIOUS_CAPTURE
    previous.parent.mkdir(parents=True)
    previous.write_bytes(b'{"legacy": "h7 only"}\r\n')
    output = tmp_path / "research-materials" / "issue-203" / "consumer-evidence-v2.json"

    assert (
        _run_main(
            ["--output", str(output), "--examples-dir", str(examples_dir)], FakeClient()
        )
        == 0
    )
    assert previous.read_bytes() == b'{"legacy": "h7 only"}\r\n'

    evidence = json.loads(output.read_text(encoding="utf-8"))
    assert evidence["metadata"]["capture_timestamp_utc"] == "2026-10-28T04:00:00+00:00"
    assert evidence["metadata"]["capture_date_asia_colombo"] == "2026-10-28"
    assert (
        evidence["metadata"]["previous_capture"]["sha256_local_bytes"]
        == hashlib.sha256(previous.read_bytes()).hexdigest()
    )

    digest, _, problems = cce.verify_evidence_file(output)
    assert problems == []
    assert digest == hashlib.sha256(output.read_bytes()).hexdigest()

    doc = tmp_path / "doc.md"
    doc.write_text(
        "Captured {{CAPTURE_DATE}} ({{CAPTURE_TIMESTAMP_UTC}}); "
        "SHA-256 `{{EVIDENCE_SHA256}}`.\n",
        encoding="utf-8",
    )
    assert cce.main(["--verify", str(output), "--fill-docs", str(doc)]) == 0
    assert doc.read_text(encoding="utf-8") == (
        f"Captured 28 October 2026 (2026-10-28T04:00:00+00:00); SHA-256 `{digest}`.\n"
    )


def test_verify_rejects_hand_edited_evidence(
    tmp_path: Path, examples_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "evidence.json"
    assert (
        _run_main(
            ["--output", str(output), "--examples-dir", str(examples_dir)], FakeClient()
        )
        == 0
    )
    evidence = json.loads(output.read_text(encoding="utf-8"))

    edited_response = copy.deepcopy(evidence)
    edited_response["exchanges"]["examples"][1]["body"]["target_end_date"] = (
        "2025-02-05"
    )
    path_a = tmp_path / "edited-response.json"
    path_a.write_bytes(cce.serialise_evidence(edited_response))
    _, _, problems = cce.verify_evidence_file(path_a)
    assert any("re-derived" in problem for problem in problems)

    edited_outcome = copy.deepcopy(evidence)
    edited_outcome["checks"][0]["passed"] = False
    path_b = tmp_path / "edited-outcome.json"
    path_b.write_bytes(cce.serialise_evidence(edited_outcome))
    _, _, problems = cce.verify_evidence_file(path_b)
    assert any("stored checks differ" in problem for problem in problems)

    crlf = tmp_path / "crlf.json"
    crlf.write_bytes(output.read_bytes().replace(b"\n", b"\r\n"))
    _, _, problems = cce.verify_evidence_file(crlf)
    assert any("CRLF" in problem for problem in problems)


def test_fill_placeholders_rejects_unknown_tokens() -> None:
    with pytest.raises(KeyError):
        cce.fill_placeholders(
            "{{EVIDENCE_SHA256}} {{TYPO_KEY}}", {"EVIDENCE_SHA256": "x"}
        )


def test_helper_imports_app_from_the_repository_package() -> None:
    tree = ast.parse(Path(cce.__file__).read_text(encoding="utf-8"))
    modules = {
        node.module: {alias.name for alias in node.names}
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "app" in modules.get("src.api.main", set())
    assert "api.main" not in modules
