# Project Setup and Dataset Handoff

**Discussion date:** 21 September 2026
**Time:** 8:30–10:00 PM; end confirmed by Chathuranga on 16 November 2026
**Format:** Microsoft Teams, with WhatsApp setup and follow-up
**Prepared:** 5 November 2026, retrospectively from the WhatsApp export
**Purpose:** Resolve local development setup and distribute the selected dataset.
**Minutes taken by:** Didilani Pathinayaka (confirmed 16 November 2026)
**Apologies:** None; all three active members attended, according to Chathuranga.

## Participation and evidence

**Clarification recorded 16 November:** Chathuranga confirms participation by himself, Didilani and Dewmi, the three active members, with Didilani taking minutes. Tinosh had not yet joined. The earlier export-only record could identify Chathuranga and Dewmi but could not establish the full attendance list. That evidence gap is now supplemented by his account; the unmapped contact identifier is not independently assigned to a person. The invitation is M0070; Chathuranga reported the meeting open for screen sharing at 8:26 PM (M0076), and Dewmi asked to rejoin at 9:41 PM (M0088–M0090).

References follow the [discussion log conventions](2026-09-13-to-2026-11-05-whatsapp-discussions.md#source-and-reading-conventions). Meeting links and contact identifiers are omitted.

## Topics and follow-up

- Python 3.12, virtual environments and dependency installation were explained for different operating systems (M0065–M0069).
- Repository-root, environment activation and repository synchronisation problems received troubleshooting support (M0074–M0092).
- UCI data was shared in the morning. In the evening, Chathuranga shared `supply_chain_dataset1.csv`, gave local `data/raw/` extraction/storage instructions and supplied the Kaggle source (M0063–M0064; M0093–M0102).
- Dewmi acknowledged the dataset instructions at 10:54 PM (M0101), after the confirmed 10:00 PM meeting end. This follow-up alone does not establish successful installation or byte identity.

## Decisions and scope

[DR-001](../decisions/DR-001-dataset-selection.md) records the dataset choice. This note documents communication and setup support, not a new forecasting or inventory method. The selected source contains publisher-simulated records.

## Actions and blockers at the time

| Action | Owner addressed | Timing | Recorded status |
|---|---|---|---|
| Prepare Python environment/dependencies | Members receiving setup guidance | Before project work; no separate deadline established | Instructions supplied; completion not independently established |
| Resolve repository paths and activation | Chathuranga with affected members | Setup/follow-up | Troubleshooting exchanged; not every resolution recorded |
| Store selected dataset locally | Receiving members | Following handoff | File/instructions shared; Dewmi acknowledged |

Environment and repository-path confusion were evident blockers. Chathuranga clarified on 16 November that the group generally arranged future meetings according to progress and bottlenecks while continuing WhatsApp coordination; no next formal date was fixed at this meeting close. These historical statuses do not describe current installation readiness.
