# Research Evidence Index

This directory holds lightweight inspectable numerical snapshots, descriptive reports and approved figures. [Final evaluation](../docs/forecasting-final-evaluation.md) is the canonical current forecasting interpretation and conclusion; generated reports retain the wording/status captured when they were rendered.

## Dataset provenance

The research uses Ziya's published [High-Dimensional Supply Chain Inventory Dataset](https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset), downloaded from Kaggle. The source records were simulated by the publisher; the project team did not generate a replacement research dataset. References to simulated data in retained reports describe the published source's provenance. Synthetic test fixtures and API demonstration inputs are separately labelled examples.

## Forecasting evidence

| Role | Exact retained run | Tracked numerical source |
|---|---|---|
| Four-fold chronological validation | validation-20261002-01 | [Validation comparison](forecasting/validation-20261002-01/comparison.md) |
| Reserved fixed-origin final/test evaluation | final-20261003-02 | [Final comparison](forecasting/final-20261003-02/comparison.md) |

Chathuranga confirms both retained runs completed and integrity verification passed. This index performs no fresh bundle verification. Both comparisons are immutable generated evidence: old pending/finalizing/blocked wording inside them is historical, not current project status. Current decisions remain in [DR-014](../docs/decisions/DR-014-forecasting-selection-and-final-refit.md), and current findings/review status in the final report. No final-result-driven reselection is allowed.

## Descriptive evidence

- [Demand EDA](demand-eda.md) and its figures: historical descriptive analysis, including full-year exposure; not a feature-selection experiment or current protocol.
- [Temporal demand and inventory-alignment profile](temporal-demand-profile.md): native-grain, demand-condition and inventory-context evidence; no approved inventory-risk outcome is implied.

No EDA, profiling or metrics are regenerated during documentation maintenance. Earlier unavailable/removed experiment evidence must not be described as retained or relabelled as the revised study's baseline.

## Storage and review

Machine evidence and sole run_manifest.json completion authority are local under artifacts/forecasting/<run_id>/. Models/state/replay inputs are local under models/forecasting/<run_id>/. Canonical trackable comparisons are reports/forecasting/<run_id>/comparison.md. Temporary reports use reports/forecasting/drafts/; historical originals referenced by completed receipts remain unchanged. [Storage policy](../docs/artifact-storage-policy.md) defines exact retention/version contracts.

A completion manifest and generated scores establish execution evidence, not human acceptance of interpretation. Chathuranga owns forecasting conclusions; component owners review claims affecting their area. The consolidated final report is the human-reviewed final forecasting interpretation; this review does not establish lecturer approval, group-wide downstream approval or completion of the API, inventory-risk or responsible decision-support components. Optional supplementary reviewed reports/figures must link exact run/stage/evidence identities, actual review references and limitations; they should not duplicate the canonical result report.

Any report must distinguish validation means from final fixed-origin metrics, primary/supportive/baseline roles, provenance/completion/review status, unavailable values and prior outcome exposure. Do not invent unexecuted results, statistical significance, a universal model winner or inventory effectiveness. Preserve dataset protections. Contribution/review follows [CONTRIBUTING](../CONTRIBUTING.md); material milestones belong in [research progress](../docs/research-progress.md).
