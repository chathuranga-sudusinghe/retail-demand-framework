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

## Inventory-risk evaluation evidence

Chathuranga manually ran the constructed-origin evaluation on 23 October 2026 and authorised its four output files for shared GitHub review. These are unchanged copies of `research-materials/inventory-risk/issue-164/evaluation-v1/`, totalling 8,481,777 bytes.

| File | What to review |
|---|---|
| [report.md](inventory-risk/issue-164/evaluation-v1/report.md) | Start here: the per-horizon counts, proxy metrics, denominators and scenario limitations. |
| [prospective.json](inventory-risk/issue-164/evaluation-v1/prospective.json) | The 1,000-key handoff; inventory exposure is available only for horizons 1/7/14. H=28 remains gated. No realised targets or retrospective metrics. |
| [evaluation.json](inventory-risk/issue-164/evaluation-v1/evaluation.json) | The 750 retrospective cases and three horizon summaries, kept separate from prospective inputs. |
| [manifest.json](inventory-risk/issue-164/evaluation-v1/manifest.json) | Original output hashes, source bindings, snapshot basis, operator, timestamp and implementation hashes. |

Each horizon has 239 paired forecast comparisons and 11 scenario-at/below-threshold cases. These results use hypothetical starting inventory, a fixed reorder point and no receipts; they do not establish actual stockout accuracy or real-retailer effectiveness. The [protocol's retained-run record](../docs/research/inventory-risk-evaluation-protocol.md#123-retained-human-run-evidence) records the execution and identity-check scope. These files support review. #164/#168 were closed as delivered evidence milestones through PR #175, not as proof of complete consumer/prototype acceptance. [DR-012 group approval](../docs/decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) is recorded separately under #177; the original files retain their historical proposed-status metadata.

## Decision-support review evidence

Chathuranga authorised the limited [Issue #168](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/168) snapshot below for GitHub sharing on 23 October 2026. The four files are unchanged copies from `research-materials/decision-support/issue-168-json/`, totalling 209,854 bytes. All members can inspect them here without receiving separate copies or running the preparation command.

| File | What to review |
|---|---|
| [records.md](decision-support/issue-168-json/records.md) | Start here: the 20 populated forecast-only records F01–F20, with identity, horizon meaning, assumptions, limitations and explicit unavailable evidence. |
| [records.json](decision-support/issue-168-json/records.json) | The same records in machine-readable form, linked to the exact forecast source. |
| [review.json](decision-support/issue-168-json/review.json) | The eight checks per record: 24 human-confirmed outcomes for F01–F03; the remaining 136 checks for F04–F20 are blank. |
| [manifest.json](decision-support/issue-168-json/manifest.json) | The unchanged preparation receipt, including source and record hashes, original generator hashes, operator and preparation time. |

The manifest's assessment-status text and blank-template hash describe initial preparation; they do not describe the later partial checklist. Its code hashes identify the historical generator, not today's source. This historical forecast-only snapshot remains separate from the inventory-linked bundle below and has no complete assessment summary. Publication alone does not establish peer approval. #168 was subsequently closed through PR #175 for its delivered evidence milestone; the completed inventory-linked assessment below remains separate from this historical forecast-only snapshot. The [evaluation document](../docs/research/responsible-decision-support-evaluation.md) records the mapping, findings and presentation requirements. The [storage policy](../docs/artifact-storage-policy.md) limits sharing to the named review bundles. Actual preparation and summarisation continue to use ignored local directories; tracked copies support inspection without changing the command-line interface.

### Inventory-linked records

Chathuranga prepared this separate bundle on 23 October 2026 using the inventory evaluation above, then confirmed its assessment and manually generated the summaries. The six shared files now total 390,436 bytes. The source records and preparation manifest remain unchanged; the editable checklist contains the confirmed human outcomes, and both summary files are unchanged copies of his generated outputs.

| File | What to review |
|---|---|
| [records.md](decision-support/issue-168-inventory-v1/records.md) | Start here: 20 populated records, including inventory evidence for the 15 selected 1/7/14-day cases. |
| [records.json](decision-support/issue-168-inventory-v1/records.json) | The same records with exact inventory/source bindings; five h=28 cases retain gated inventory fields. |
| [review.json](decision-support/issue-168-inventory-v1/review.json) | All 160 record-level outcomes confirmed by Chathuranga, assessed on 23 October 2026; case-specific evidence/reasons and all identities are retained. |
| [manifest.json](decision-support/issue-168-inventory-v1/manifest.json) | Original preparation receipt and bindings for the records, readable copy and initial blank checklist. |
| [summary.md](decision-support/issue-168-inventory-v1/summary.md) | Human-run summary: 20 assessed records, 160 checks, per-criterion counts and explicit met-proportion denominators. |
| [summary.json](decision-support/issue-168-inventory-v1/summary.json) | The same summary in machine-readable form, binding the completed checklist and original record hashes. |

The historical F01–F03 outcomes above were not transferred to these changed records. Chathuranga reviewed and explicitly confirmed the separate 20-record assessment draft; Codex transcribed those confirmed outcomes into both the local and tracked checklists, with assessor `Chathuranga` and date `2026-10-23`. The completed checklist SHA-256 is `91585207e718ada57aa29ffad782eb513638a62d0a98ae8a5a36b3fea1978fa7`; the source records and manifest's initial-template hash remain unchanged. The preparation manifest's blank-assessment status remains a historical receipt, not the current checklist status. Chathuranga then manually ran the summarizer; its outputs retain all unavailable cases in the applicable denominators and report no overall cross-criterion score. This is an individual record-level assessment; prototype visibility, component acceptance and independent peer review remain separate. The generator and summarizer still operate on local working directories under `research-materials/`. For local use, copy the complete bundle into a fresh ignored directory, keeping filenames and bytes unchanged. The inventory consumer requires its four-file evaluation bundle together because it checks the adjacent manifest and companion hashes; do not overwrite existing local evidence.

## Descriptive evidence

- [Demand EDA](demand-eda.md) and its figures: historical descriptive analysis, including full-year exposure; not a feature-selection experiment or current protocol.
- [Temporal demand and inventory-alignment profile](temporal-demand-profile.md): native-grain, demand-condition and inventory-context evidence; no approved inventory-risk outcome is implied.

No EDA, profiling or metrics are regenerated during documentation maintenance. Earlier unavailable/removed experiment evidence must not be described as retained or relabelled as the revised study's baseline.

## Storage and review

Machine evidence and sole run_manifest.json completion authority are local under artifacts/forecasting/<run_id>/. Models/state/replay inputs are local under models/forecasting/<run_id>/. Canonical trackable comparisons are reports/forecasting/<run_id>/comparison.md. Temporary reports use reports/forecasting/drafts/; historical originals referenced by completed receipts remain unchanged. [Storage policy](../docs/artifact-storage-policy.md) defines exact retention/version contracts.

A completion manifest and generated scores establish execution evidence, not human acceptance of interpretation. Chathuranga owns forecasting conclusions; component owners review claims affecting their area. The consolidated final report is the human-reviewed final forecasting interpretation; this review does not establish lecturer approval, group-wide downstream approval or completion of the API, inventory-risk or responsible decision-support components. Optional supplementary reviewed reports/figures must link exact run/stage/evidence identities, actual review references and limitations; they should not duplicate the canonical result report.

Any report must distinguish validation means from final fixed-origin metrics, primary/supportive/baseline roles, provenance/completion/review status, unavailable values and prior outcome exposure. Do not invent unexecuted results, statistical significance, a universal model winner or inventory effectiveness. Preserve dataset protections. Contribution/review follows [CONTRIBUTING](../CONTRIBUTING.md); material milestones belong in [research progress](../docs/research-progress.md).
