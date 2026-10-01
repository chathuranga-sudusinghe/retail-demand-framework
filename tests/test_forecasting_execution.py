"""Current CSV input compatibility; synthetic files only."""
from unittest.mock import Mock

import pytest

from src.forecasting import execution


@pytest.mark.parametrize("header", ["Date,SKU_ID,Warehouse_ID,Units_Sold,Units_Sold", "Date,SKU_ID,Units_Sold"])
def test_required_headers_must_be_unique(tmp_path, header):
    path = tmp_path / "synthetic.csv"
    path.write_text(header + "\n")
    with pytest.raises(execution.ExecutionBlocked, match="exactly once"):
        execution.load_dataset(path)


def test_csv_loader_preserves_text_ids_and_excludes_source_fields(tmp_path):
    path = tmp_path / "synthetic.csv"
    path.write_text("Date,SKU_ID,Warehouse_ID,Units_Sold,Demand_Forecast\n2024-01-01,001,02,5,999\n")
    data = execution.load_dataset(path)
    assert data.SKU_ID.iloc[0] == "001" and data.Warehouse_ID.iloc[0] == "02"
    assert "Demand_Forecast" not in data


def test_csv_header_parser_error_is_wrapped_before_pandas_loading(tmp_path, monkeypatch):
    path = tmp_path / "synthetic.csv"
    path.write_text("x" * (execution.csv.field_size_limit() + 1) + "\n")
    loader = Mock(side_effect=AssertionError("Malformed header must fail before data loading."))
    monkeypatch.setattr(execution.pd, "read_csv", loader)
    with pytest.raises(execution.ExecutionBlocked, match="CSV could not be loaded") as caught:
        execution.load_dataset(path)
    assert isinstance(caught.value.__cause__, execution.csv.Error)
    loader.assert_not_called()
