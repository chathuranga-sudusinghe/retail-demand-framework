# Decision-support records — Issue #168

20 purposive decision-support records; inventory evidence is conditional on its recorded snapshot basis; missing inventory/replenishment evidence remains explicit; h=28 downstream use gated

Source export SHA-256: `c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863`.

These are prepared records, not completed transparency assessments. Enter the eight criterion outcomes per record in [review.json](review.json).

Use applicability `yes` or `no`; for applicable checks use `met`, `not met` or `not assessable`. Supply evidence for met checks and reasons for other outcomes/non-applicability, plus the assessor and ISO date.

## F01

```json
{
  "assessment_id": "F01",
  "horizon": 1,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-03 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F01",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"next_day\", \"horizon\": 1, \"target_end_date\": \"2024-12-03\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 13.638668942391519,
    "forecast_horizon": "1-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_1\", \"Warehouse_ID\": \"WH_1\", \"configuration_id\": \"GBM018\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 1, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 227.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 213.36133105760848,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_1",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_1"
  }
}
```

## F02

```json
{
  "assessment_id": "F02",
  "horizon": 7,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-09 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F02",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 7, \"target_end_date\": \"2024-12-09\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 89.08327726179623,
    "forecast_horizon": "7-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_1\", \"Warehouse_ID\": \"WH_1\", \"configuration_id\": \"GBM011\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 7, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 227.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 137.91672273820376,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_1",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_1"
  }
}
```

## F03

```json
{
  "assessment_id": "F03",
  "horizon": 14,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-16 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F03",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 14, \"target_end_date\": \"2024-12-16\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 170.942626953125,
    "forecast_horizon": "14-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_1\", \"Warehouse_ID\": \"WH_1\", \"configuration_id\": \"GBM022\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 14, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 227.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 56.057373046875,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_1",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_1"
  }
}
```

## F04

```json
{
  "assessment_id": "F04",
  "horizon": 28,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-30 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F04",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 28, \"target_end_date\": \"2024-12-30\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 343.1779479980469,
    "forecast_horizon": "28-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_1\", \"Warehouse_ID\": \"WH_1\", \"configuration_id\": \"GBM003\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 28, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": null,
    "inventory_risk_provenance": null,
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "28-day case is in forecast-transparency scope only; inventory interpretation and review triggers remain gated.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_1",
    "unavailable_fields": {
      "inventory_risk_evidence": "28_day_downstream_use_requires_separate_approval",
      "inventory_risk_provenance": "28_day_downstream_use_requires_separate_approval",
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_1"
  }
}
```

## F05

```json
{
  "assessment_id": "F05",
  "horizon": 1,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-03 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F05",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"next_day\", \"horizon\": 1, \"target_end_date\": \"2024-12-03\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 11.189844763125892,
    "forecast_horizon": "1-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_5\", \"Warehouse_ID\": \"WH_2\", \"configuration_id\": \"GBM018\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 1, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 77.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 65.81015523687411,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_5",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_2"
  }
}
```

## F06

```json
{
  "assessment_id": "F06",
  "horizon": 7,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-09 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F06",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 7, \"target_end_date\": \"2024-12-09\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 78.59810591959317,
    "forecast_horizon": "7-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_5\", \"Warehouse_ID\": \"WH_2\", \"configuration_id\": \"GBM011\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 7, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 77.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": -1.5981059195931664,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_5",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_2"
  }
}
```

## F07

```json
{
  "assessment_id": "F07",
  "horizon": 14,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-16 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F07",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 14, \"target_end_date\": \"2024-12-16\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 152.30743408203125,
    "forecast_horizon": "14-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_5\", \"Warehouse_ID\": \"WH_2\", \"configuration_id\": \"GBM022\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 14, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 77.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": -75.30743408203125,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_5",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_2"
  }
}
```

## F08

```json
{
  "assessment_id": "F08",
  "horizon": 28,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-30 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F08",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 28, \"target_end_date\": \"2024-12-30\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 303.52630615234375,
    "forecast_horizon": "28-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_5\", \"Warehouse_ID\": \"WH_2\", \"configuration_id\": \"GBM003\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 28, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": null,
    "inventory_risk_provenance": null,
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "28-day case is in forecast-transparency scope only; inventory interpretation and review triggers remain gated.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_5",
    "unavailable_fields": {
      "inventory_risk_evidence": "28_day_downstream_use_requires_separate_approval",
      "inventory_risk_provenance": "28_day_downstream_use_requires_separate_approval",
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_2"
  }
}
```

## F09

```json
{
  "assessment_id": "F09",
  "horizon": 1,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-03 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F09",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"next_day\", \"horizon\": 1, \"target_end_date\": \"2024-12-03\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 13.911101904309598,
    "forecast_horizon": "1-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_10\", \"Warehouse_ID\": \"WH_3\", \"configuration_id\": \"GBM018\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 1, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 194.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 180.0888980956904,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_10",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_3"
  }
}
```

## F10

```json
{
  "assessment_id": "F10",
  "horizon": 7,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-09 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F10",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 7, \"target_end_date\": \"2024-12-09\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 91.93821340571549,
    "forecast_horizon": "7-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_10\", \"Warehouse_ID\": \"WH_3\", \"configuration_id\": \"GBM011\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 7, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 194.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 102.06178659428451,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_10",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_3"
  }
}
```

## F11

```json
{
  "assessment_id": "F11",
  "horizon": 14,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-16 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F11",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 14, \"target_end_date\": \"2024-12-16\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 167.450439453125,
    "forecast_horizon": "14-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_10\", \"Warehouse_ID\": \"WH_3\", \"configuration_id\": \"GBM022\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 14, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 194.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 26.549560546875,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_10",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_3"
  }
}
```

## F12

```json
{
  "assessment_id": "F12",
  "horizon": 28,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-30 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F12",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 28, \"target_end_date\": \"2024-12-30\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 317.7198791503906,
    "forecast_horizon": "28-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_10\", \"Warehouse_ID\": \"WH_3\", \"configuration_id\": \"GBM003\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 28, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": null,
    "inventory_risk_provenance": null,
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "28-day case is in forecast-transparency scope only; inventory interpretation and review triggers remain gated.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_10",
    "unavailable_fields": {
      "inventory_risk_evidence": "28_day_downstream_use_requires_separate_approval",
      "inventory_risk_provenance": "28_day_downstream_use_requires_separate_approval",
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_3"
  }
}
```

## F13

```json
{
  "assessment_id": "F13",
  "horizon": 1,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-03 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F13",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"next_day\", \"horizon\": 1, \"target_end_date\": \"2024-12-03\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 13.517109918099667,
    "forecast_horizon": "1-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_15\", \"Warehouse_ID\": \"WH_4\", \"configuration_id\": \"GBM018\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 1, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 105.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 91.48289008190034,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_15",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_4"
  }
}
```

## F14

```json
{
  "assessment_id": "F14",
  "horizon": 7,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-09 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F14",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 7, \"target_end_date\": \"2024-12-09\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 88.79312754329506,
    "forecast_horizon": "7-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_15\", \"Warehouse_ID\": \"WH_4\", \"configuration_id\": \"GBM011\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 7, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 105.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 16.206872456704943,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_15",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_4"
  }
}
```

## F15

```json
{
  "assessment_id": "F15",
  "horizon": 14,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-16 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F15",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 14, \"target_end_date\": \"2024-12-16\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 168.23077392578125,
    "forecast_horizon": "14-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_15\", \"Warehouse_ID\": \"WH_4\", \"configuration_id\": \"GBM022\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 14, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 105.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": -63.23077392578125,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_15",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_4"
  }
}
```

## F16

```json
{
  "assessment_id": "F16",
  "horizon": 28,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-30 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F16",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 28, \"target_end_date\": \"2024-12-30\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 339.2133483886719,
    "forecast_horizon": "28-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_15\", \"Warehouse_ID\": \"WH_4\", \"configuration_id\": \"GBM003\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 28, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": null,
    "inventory_risk_provenance": null,
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "28-day case is in forecast-transparency scope only; inventory interpretation and review triggers remain gated.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_15",
    "unavailable_fields": {
      "inventory_risk_evidence": "28_day_downstream_use_requires_separate_approval",
      "inventory_risk_provenance": "28_day_downstream_use_requires_separate_approval",
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_4"
  }
}
```

## F17

```json
{
  "assessment_id": "F17",
  "horizon": 1,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-03 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F17",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"next_day\", \"horizon\": 1, \"target_end_date\": \"2024-12-03\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 12.310227868534884,
    "forecast_horizon": "1-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_20\", \"Warehouse_ID\": \"WH_5\", \"configuration_id\": \"GBM018\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 1, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 200.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 187.6897721314651,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_20",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_5"
  }
}
```

## F18

```json
{
  "assessment_id": "F18",
  "horizon": 7,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-09 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F18",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 7, \"target_end_date\": \"2024-12-09\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 88.82577723956054,
    "forecast_horizon": "7-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_20\", \"Warehouse_ID\": \"WH_5\", \"configuration_id\": \"GBM011\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 7, \"model\": \"lightgbm\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 200.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 111.17422276043946,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_20",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_5"
  }
}
```

## F19

```json
{
  "assessment_id": "F19",
  "horizon": 14,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-16 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F19",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 14, \"target_end_date\": \"2024-12-16\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 161.19580078125,
    "forecast_horizon": "14-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_20\", \"Warehouse_ID\": \"WH_5\", \"configuration_id\": \"GBM022\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 14, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": {
      "forecast_exposure_state": "no_forecast_crossing",
      "forecast_input_reason": "",
      "forecast_input_status": "available",
      "inventory_basis": "constructed_origin_scenario",
      "inventory_buffer": 200.0,
      "methodology_status": "proposed_for_group_approval",
      "origin_exposure_state": "scenario_initially_above_threshold",
      "origin_snapshot_status": "unknown",
      "predicted_margin": 38.80419921875,
      "snapshot_assumption": "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    },
    "inventory_risk_provenance": "{\"dataset_provenance_sha256\": \"35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f\", \"manifest_sha256\": \"5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9\", \"operator\": \"Chathuranga\", \"prospective_sha256\": \"5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4\", \"source\": {\"forecast_export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}, \"mapping_version\": \"issue-164-168-v1\", \"snapshot_basis\": \"Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.\", \"snapshot_policy\": \"constructed-origin\"}}",
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_20",
    "unavailable_fields": {
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_5"
  }
}
```

## F20

```json
{
  "assessment_id": "F20",
  "horizon": 28,
  "record": {
    "assumptions": [
      "Target interval 2024-12-03 through 2024-12-30 is inclusive.",
      "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
      "Reorder_Point is held fixed for the proposed scenario.",
      "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
      "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
      "Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory."
    ],
    "component_provenance": {
      "decision_support": "responsible_decision_support",
      "forecast": "forecasting",
      "inventory_risk": "inventory_risk"
    },
    "evidence": [
      "Assessment ID: F20",
      "Mapping version: issue-164-168-v1",
      "{\"forecast_type\": \"cumulative_window\", \"horizon\": 28, \"target_end_date\": \"2024-12-30\", \"target_start_date\": \"2024-12-03\", \"uncertainty\": {\"reason\": \"no_agreed_method\", \"status\": \"unavailable\"}, \"unit\": \"units\"}",
      "Retained export SHA-256: c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863",
      "Inventory prospective SHA-256: 5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4"
    ],
    "forecast_demand": 306.3371276855469,
    "forecast_horizon": "28-day",
    "forecast_origin": "2024-12-02",
    "forecast_provenance": "{\"SKU_ID\": \"SKU_20\", \"Warehouse_ID\": \"WH_5\", \"configuration_id\": \"GBM003\", \"export_schema\": \"issue-132-forecast-export-v1\", \"export_sha256\": \"c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863\", \"forecast_origin\": \"2024-12-02\", \"forecast_status\": \"available\", \"horizon\": 28, \"model\": \"xgboost\", \"producer_status\": \"designated_producer\", \"source\": {\"evaluation_stage\": \"final_evaluation\", \"integrity_result\": {\"baseline_evaluations\": 8, \"evaluations\": 28, \"learned_refits\": 20, \"models_replayed\": 20, \"predictions\": 7000, \"status\": \"passed\"}, \"prediction_receipt_sha256\": \"853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692\", \"run_id\": \"final-20261003-02\", \"run_manifest_path\": \"artifacts/forecasting/final-20261003-02/run_manifest.json\", \"run_manifest_sha256\": \"adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43\", \"source_schema\": \"issue-130-final-v1\"}}",
    "human_review_reasons": [
      "Human review has not yet been assessed."
    ],
    "human_review_status": "not_assessed",
    "inventory_risk_evidence": null,
    "inventory_risk_provenance": null,
    "limitations": [
      "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
      "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
      "Limited purposive selection of 20 forecasts; not statistically representative.",
      "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff.",
      "The final interval had December 3\u201316 prior validation exposure and full-year exploratory exposure.",
      "Record contents alone do not establish visibility/readability in a rendered prototype.",
      "28-day case is in forecast-transparency scope only; inventory interpretation and review triggers remain gated.",
      "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
      "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
      "Source Demand_Forecast is a reference field, not the project forecast input.",
      "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
      "Negative scenario balances are not verified physical negative inventory.",
      "Snapshot within-day semantics remain unresolved and are not inferred here.",
      "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
      "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
      "Constructed starting balances are hypothetical; source origin availability is not established by this scenario."
    ],
    "management_consideration": "Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
    "replenishment_recommendation": null,
    "sku_id": "SKU_20",
    "unavailable_fields": {
      "inventory_risk_evidence": "28_day_downstream_use_requires_separate_approval",
      "inventory_risk_provenance": "28_day_downstream_use_requires_separate_approval",
      "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
      "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded."
    },
    "uncertainty_or_error": null,
    "warehouse_id": "WH_5"
  }
}
```
