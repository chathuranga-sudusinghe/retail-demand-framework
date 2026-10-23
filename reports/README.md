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

## Decision-support review evidence

Chathuranga authorised the limited [Issue #168](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/168) snapshot below for GitHub sharing on 23 October 2026. The four files are unchanged copies from `research-materials/decision-support/issue-168-json/`, totalling 209,854 bytes. All members can inspect them here without receiving separate copies or running the preparation command.

| File | What to review |
|---|---|
| [records.md](decision-support/issue-168-json/records.md) | Start here: the 20 populated forecast-only records F01–F20, with identity, horizon meaning, assumptions, limitations and explicit unavailable evidence. |
| [records.json](decision-support/issue-168-json/records.json) | The same records in machine-readable form, linked to the exact forecast source. |
| [review.json](decision-support/issue-168-json/review.json) | The eight checks per record: 24 human-confirmed outcomes for F01–F03; the remaining 136 checks for F04–F20 are blank. |
| [manifest.json](decision-support/issue-168-json/manifest.json) | The unchanged preparation receipt, including source and record hashes, original generator hashes, operator and preparation time. |

The manifest's assessment-status text and blank-template hash describe initial preparation; they do not describe the later partial checklist. Its code hashes identify the historical generator, not today's source. This snapshot is available for human review; publishing it does not establish peer approval or complete Issue #168. No complete assessment summary exists yet. The [evaluation document](../docs/research/responsible-decision-support-evaluation.md) records the mapping, partial findings and presentation requirements. The [storage policy](../docs/artifact-storage-policy.md) limits this exception to the four named files. Actual preparation and summarisation continue to use ignored local directories; these tracked copies support inspection without changing the command-line interface.

## Descriptive evidence

- [Demand EDA](demand-eda.md) and its figures: historical descriptive analysis, including full-year exposure; not a feature-selection experiment or current protocol.
- [Temporal demand and inventory-alignment profile](temporal-demand-profile.md): native-grain, demand-condition and inventory-context evidence; no approved inventory-risk outcome is implied.

No EDA, profiling or metrics are regenerated during documentation maintenance. Earlier unavailable/removed experiment evidence must not be described as retained or relabelled as the revised study's baseline.

## Storage and review

Machine evidence and sole run_manifest.json completion authority are local under artifacts/forecasting/<run_id>/. Models/state/replay inputs are local under models/forecasting/<run_id>/. Canonical trackable comparisons are reports/forecasting/<run_id>/comparison.md. Temporary reports use reports/forecasting/drafts/; historical originals referenced by completed receipts remain unchanged. [Storage policy](../docs/artifact-storage-policy.md) defines exact retention/version contracts.

A completion manifest and generated scores establish execution evidence, not human acceptance of interpretation. Chathuranga owns forecasting conclusions; component owners review claims affecting their area. The consolidated final report is the human-reviewed final forecasting interpretation; this review does not establish lecturer approval, group-wide downstream approval or completion of the API, inventory-risk or responsible decision-support components. Optional supplementary reviewed reports/figures must link exact run/stage/evidence identities, actual review references and limitations; they should not duplicate the canonical result report.

Any report must distinguish validation means from final fixed-origin metrics, primary/supportive/baseline roles, provenance/completion/review status, unavailable values and prior outcome exposure. Do not invent unexecuted results, statistical significance, a universal model winner or inventory effectiveness. Preserve dataset protections. Contribution/review follows [CONTRIBUTING](../CONTRIBUTING.md); material milestones belong in [research progress](../docs/research-progress.md).
