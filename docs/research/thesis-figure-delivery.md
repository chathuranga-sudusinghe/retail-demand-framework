# Thesis and presentation figure delivery

Related: #201, #179 and #182; existing PR #211.

On 5 November 2026, Chathuranga approved the six revised core figures and the
two additional forecasting/transparency figures in the project working chat.
This explicitly extends this figure-delivery task beyond #201's inventory-only
selection. It does not add a research method, change permanent member ownership,
approve interpretations or complete component/code review.

Chathuranga separately instructed removal of the entire original V11 delivery
directory, including its PNGs and archives. That ignored directory was removed;
the retained forecasts, inventory evaluation, assessments and worked trace were
not changed. The default delivery now contains exactly eight PNGs, rather than
hundreds of case-table pages. The unused table-rendering module and its dedicated
tests were subsequently removed at Chathuranga's request. The active exporter,
source validation and current figure tests remain in use.

## Purpose and selection

| Output | Question and visual form |
|---|---|
| `fig01_coverage_eligibility` | Which records support the analysis? Compact population/eligibility table, including explicit h28 gating. |
| `fig02_proxy_crossings` | What did forecast crossings capture/miss? Three confusion matrices and four existing denominator-labelled rates. |
| `fig03_population_margins` | Where are retained margins relative to zero? Three evaluation-only scatter panels with common scales, confusion markers and the existing worked case highlighted. |
| `fig04_worked_forecast` | What did the illustrative case forecast? Four-horizon forecast/actual bars and exact target-window/producer context. |
| `fig05_worked_margins` | How did forecast error affect the inventory interpretation? Paired h1/h7/h14 margins, retaining the h14 missed proxy crossing. |
| `fig06_evidence_status` | What exists, is approved, unknown or deferred? Compact availability and historical/current approval tables. |
| `fig07_transparency_checks` | What do existing human record checks show? Counts of met, not met and not assessable for eight criteria. |
| `fig08_forecasting_comparison` | How do frozen models compare? All seven models at each horizon, preserving primary/supportive/baseline roles and producer designation. |

Every PNG has a matching SVG and JSON evidence sidecar. Sidecars retain full-precision plotted values, original statuses, case identities
and source hashes/pointers. Full assumptions and reasons remain in the unchanged
referenced evidence; the complete forecast export is not copied into reports.
The margin sidecar is the complete case index: match a panel's horizon and
confusion-cell marker to its retained cases. Overlapping points are not distinct
visible observations; the graph is an overview, not a replacement for the index.
Didilani must review this overview/index approach against the case-identity
requirement in the [visual specification](inventory-risk-visual-evidence.md).

The figures use a 6.3-inch thesis width, minimum 8-point text, explicit units,
zero-based magnitude bars, shared comparison scales and redundant colour/marker
or hatch encodings. Inspect at the intended insertion size; do not shrink a
whole figure until labels become unreadable. PNGs are 300 DPI; use SVG where the
document editor supports it. Retain captions from the sidecars/manifest.

## Inputs and identity

- Existing validated inventory-view loader and its manifest-bound prospective,
  evaluation and report files, plus the registered forecast export.
- `research-materials/issue-214/worked-scenario-v1.json`, pinned to the SHA-256
  recorded in `docs/worked-example-scenario.md`.
- `reports/decision-support/issue-168-inventory-v1/summary.json` and
  `reports/forecasting/final-20261003-02/comparison.md`, pinned to their existing
  bytes in `src/visualization/thesis_evidence.py`.

The additional pins identify the retained snapshots selected for this delivery;
they do not establish independent review. Do not refresh a pin to accommodate a
mismatch. The exporter rejects mismatches before creating its output directory,
checks cross-source bindings, and copies stored metrics instead of recomputing
research results. No models, datasets, inference, API replay or evaluation
producers are executed. Axis limits and display rounding are presentation only.

The generation manifest records source/code SHA-256, repository HEAD, whether
the working tree was clean, renderer versions, dimensions, purposes, captions
and output hashes. A manifest is written only after all eight exports succeed
and source/code bytes are rechecked. A partial failed directory must not be used
as a completed bundle; preserve diagnostics for inspection.

## Human rendering command

Run from the existing repository root in the reviewed project environment:

```bash
.venv/bin/python -m src.visualization.render_issue_201_views \
  --output-directory reports/figures/final-thesis-figures
```

The responsible human reviews this command and manually executes it. It reads
only retained evidence and writes eight PNGs, eight SVGs, eight JSON sidecars,
`manifest.json` and a preview/caption `README.md` under trackable
`reports/figures/final-thesis-figures/`. Chathuranga explicitly chose one stable
final folder rather than numbered output directories. Rerunning the same command
updates the generated bundle in place; no new version folders are needed.

Rendering and source checks finish in an automatically cleaned temporary staging
folder before existing outputs are touched. Replacement is permitted only for an
intact exporter-owned bundle with matching manifest hashes and exactly its known
files. Unrelated files and manually changed outputs cause a refusal rather than
silent deletion. A failed render leaves the previous final bundle unchanged.
The completion manifest is published last. Its schema version describes the JSON
format and does not version the destination folder.

### Recovery after interrupted publication

Staging protects the previous bundle from rendering/source-check failures.
Publication itself replaces files individually and is not an atomic directory
swap. If interrupted during replacement, the final folder has no completion
manifest and is deliberately refused on the next run. Do not treat it as a
completed bundle or add a replacement manifest by hand.

Before recovery, inspect the exact directory and Git state:

```bash
ls -la reports/figures/final-thesis-figures/
git status --short -- reports/figures/final-thesis-figures/
```

Confirm it contains only this exporter's eight `fig01`–`fig08` PNG/SVG/JSON sets,
README and possibly a manifest. Preserve any unrelated/manual work first; if
uncertain, stop and inspect rather than delete. The following human-run command
removes this generated figure folder only. Retained forecasts, inventory sources,
assessment evidence, code and documentation are outside its scope. If figures
were committed, check for unique uncommitted changes before removal.

Once the contents are confirmed disposable, recover in the same stable folder:

```bash
rm -r -- reports/figures/final-thesis-figures/
.venv/bin/python -m src.visualization.render_issue_201_views
```

This is a manual recovery instruction, not automatic cleanup permission. Code
checks cover interrupted publication, missing-manifest refusal and clean
regeneration on disposable synthetic fixtures. Complete this documentation and
the other approved fixes before committing; do not defer recovery work to a
later implementation task.

## Interpretation and acceptance

Keep current DR-012 approval visible separately from immutable historical
`proposed_for_group_approval` labels. Method approval covers h1/h7/h14 only.
The [reconciled C1 scope](../research-design.md#164-human-decisions-and-c1-closeout-record)
defers h28 inventory use, numerical replenishment, overstock, uncertainty and
automatic review rules. Unknown source timing remains disclosed. Scenario
crossings are not observed stockouts, negative margins are not verified physical
negative stock, and forecasts do not create executable purchase orders.

Actual sales, proxy counts and retrospective margins are labelled evaluation
only. The worked case is illustrative, not population-representative; retain its
underprediction and h14 false negative. The final forecasting comparison is one
origin with prior validation/EDA exposure, not a universal ranking or grounds for
reselection. Transparency checks are a purposive 20-record assessment, not a
usability experiment, managerial-review clearance or decision-quality evidence.

Synthetic tests can check contracts, displayed values, exclusions, scale bounds,
export lifecycle and text clipping. They do not establish actual rendered
readability or scientific correctness. After human generation, inspect all eight
real outputs, grayscale distinguishability and intended thesis/slide placement.
Record exact source revision, bundle identity and any remaining findings.

Didilani reviews inventory interpretation/D2, Dewmi reviews responsible
presentation/W2 and her transparency component, Chathuranga reviews forecast
meaning and model comparisons, and Tinosh supports technical review. Reuse valid
prior reviews only within their recorded scope. Another human must approve code
before merge; author self-review and synthetic tests are not substitutes.

## Implementation validation record

### W2 clarification follow-up — 7 November 2026

[Dewmi's conditional W2 findings and the existing explanations](responsible-decision-support-evaluation.md#w2-findings-received--7-november-2026)
are recorded in the existing responsible-use handoff. Figure 05's renderer now
expands TN/FN and explains them in terms of forecast and retrospective proxy
crossings. The table columns accommodate the full names; no retained values,
confusion classifications or other figures' rendering logic change.

Chathuranga manually regenerated the eight-figure bundle into the same stable
directory on 7 November 2026. The manifest SHA-256 is
`e95cbd33e5b708f3fe21458f570ecbcaafe81c1df5b9e3a1266dcb9d7f2f3ad1`;
it records generation HEAD `8edd436d3d41c05db83549d62b32f3cc41b8ff09`
with uncommitted changes. A subsequent local byte check matched all 24 output
hashes, README, four renderer files and eight named source files. This is a local
manifest match, not independent provenance verification. Codex inspected the
actual Figure 05 PNG: expanded labels fit the table, with the h14 missed proxy
crossing and physical-stock caveat retained. Give Dewmi the committed revision
and this manifest identity for her affected-view recheck; final W2 acceptance
remains pending.

Validation on `fix/issue-182-figure-clarity`: 45 synthetic tests passed across
`test_thesis_figures.py`, `test_render_issue_201_views.py` and
`test_inventory_views.py`. The new checks cover expanded TN/FN meanings and
table-cell text bounds. Ruff, format checks, MyPy for the four active
visualization modules and `git diff --check` passed. These are implementation
checks, separate from Dewmi's final presentation acceptance. After regeneration,
plain `git diff --check` reports Matplotlib-generated trailing whitespace inside
SVG path data. Source/document checks excluding generated SVGs pass; generated
SVG bytes and the matching manifest hashes are preserved.

Checks during implementation on 5 November 2026, branch
`feature/issue-201-inventory-views`, HEAD
`15d114a5ad73f42f7caf65b4ca49e8dc1efd9355` with uncommitted changes:

- Four targeted synthetic visualization test files: 57 tests passed. Coverage
  includes retained-source rejection, gate-only h28 trace handling, exact plotted
  values, null exclusions, common scales, font/cell bounds, caveat overlap,
  eight-file export, output restrictions and PNG/SVG failure cleanup. Subsequent
  checks also cover rerendering the same folder, preserving existing outputs on
  render failure, and refusing unrelated or manually changed files.
- Scoped Ruff lint/format and MyPy checks passed for the visualization modules;
  test files were linted/formatted. `git diff --check` passed.
- All eight retained display projections passed read-only identity/contract
  loading. No figures were constructed from those retained inputs.
- All eight synthetic-only temporary previews were inspected; the margin
  annotation/footer and worked-case legend/table spacing were corrected. These
  synthetic previews are not deliverable research figures or research evidence.
- The narrow command `.venv/bin/python -m src.data.verify_checksums --profile dewmi`
  matched the forecast export, 1/1 files, none missing/changed. Reference revision
  and HEAD were both the full SHA above; reference SHA-256 was
  `381ed9607a9e3ec155ee3754d699d62873bfbff18f5e1f4edc31c407267ed7cc`.
  Independent review and tracked-content comparison were not supplied; this is
  a provisional local match. Other files are outside that profile's coverage.

At the initial implementation checkpoint, retained-data PNG generation was not
performed. Chathuranga subsequently manually generated the first eight-figure candidate
on 5 November 2026. Read-only inspection matched
24/24 output hashes, 8/8 source hashes and 4/4 renderer-code hashes against its
manifest, SHA-256
`72dfa38b539de2b61c317ca5692150a99d1a5bb6da022c0c283f6b140775ccc0`.
All eight PNGs were inspected, and their Git visibility was confirmed. These are
local manifest identity checks, not independent scientific or component review.

Chathuranga approved two subsequent presentation corrections: move the population
margin worked-case labels to the empty upper-left panel area with pointers, and
replace irregular forecasting percentage ticks with regular shared intervals.
The corrections passed the same 57 targeted synthetic tests, scoped Ruff/format
and MyPy checks. Regression checks cover pointers above the zero reference and
regular, common percentage ticks; synthetic previews were inspected. Plotted
values, identities and methods are unchanged. Chathuranga then explicitly
requested removal of the uncommitted numbered output folders. They were removed;
the stable final output was subsequently generated as recorded below. The hash
above identifies the earlier inspected candidate, not the current final bundle.

Generate or refresh the corrected figures in the stable final folder:

```bash
.venv/bin/python -m src.visualization.render_issue_201_views \
  --output-directory reports/figures/final-thesis-figures
```

Chathuranga manually generated the corrected eight-figure bundle in
`reports/figures/final-thesis-figures/` on 5 November 2026. Its manifest SHA-256 is
`72e7445fa3940b1fab7c096f9d420140e8e9888d3ddda1c707282ab9a841c05c`.
Read-only checks matched 24/24 output files, 8/8 source files, 4/4 renderer-code
files and the README hash. All eight PNGs are 300 DPI and trackable. The bundle
records HEAD `15d114a5ad73f42f7caf65b4ca49e8dc1efd9355` with uncommitted changes.
The corrected population-margin pointers and regular percentage ticks were
inspected in the actual PNGs. Prior inspection of the six unchanged figure
layouts remains applicable; no additional broad audit or research execution was
performed. The rejected numbered folders are absent.

These are local identity and technical visual checks, not independent reference
provenance or component acceptance. Grayscale review, intended thesis/slide
placement and human component/code acceptance remain pending. The full repository
test suite was not run; no training, inference, replay or research evaluation was
executed by Codex.

## Engineering handoff

### Approved Claude-review corrections — 5 November 2026

Chathuranga approved D1–D4, the focused regression improvements and the index
update before commit. Hatched transparency counts now have opaque white label
backgrounds. Forecasting ticks use fewer regular shared intervals (0/20/40/60%
for the retained comparison). Both margin figures state the physical-stock
limitation; the worked-case retrospective legend explicitly says evaluation only.
The recovery procedure above is documented and exercised before commit, rather
than deferred to a later task. Optional colour/CLI refactoring was not included.
Chathuranga subsequently requested removal of the unused legacy renderer; that
cleanup is recorded below separately from the approved readability fixes.

After these changes, 75 targeted synthetic tests passed across the visualization
and retained-case suites, with scoped Ruff, formatting, MyPy and diff checks
passing. Four affected synthetic previews were inspected. A read-only comparison
also matched all 750 figure-03 case-index values/source pointers to retained
evaluation rows. Chathuranga subsequently regenerated all eight PNGs in the same
stable folder. The latest manifest SHA-256 is
`7bad51be654104108c9ece9c4c0ef00d442182cc35f6f686c0a9179c9ace366b`.
All 24 output hashes, eight source hashes, four code hashes and the README hash
matched. The four affected actual PNGs were inspected: hatch labels, tick spacing,
margin caveats and evaluation-only wording are visible and readable. Temporary
grayscale copies of all eight existing PNGs were inspected at 756 pixels wide
(6.3-inch width at 120 screen pixels/inch); markers, hatches, labels and quantities
remained distinguishable. Original delivered PNGs were not modified by this QA.
This is screen-based technical inspection, not actual printer/projector testing,
final slide/document placement, D2 or W2. No fitting, inference, scenario replay
or research evaluation ran.

### Completed runtime checks and remaining human reviews

**Legacy cleanup — 5 November 2026:** At Chathuranga's request, the unused
`src/visualization/inventory_rendering.py` and its dedicated
`tests/test_inventory_rendering.py` were removed after checking repository
references. The active CLI already used `thesis_figures.py`; no production
consumer of the old renderer remained. Its unrelated-directory protection check
was preserved in `tests/test_render_issue_201_views.py`, and obsolete CI paths
were removed. The source loader/builders and their tests remain active.

The current four-file synthetic selection (inventory views, thesis figures,
exporter lifecycle and retained cases) passed 59 tests. The earlier 75-test
record above is historical and included the retired rendering tests. Scoped
Ruff/format, MyPy for the four remaining visualization modules and diff checks
passed. All 24 delivered output hashes and four active renderer-code hashes
still matched the reviewed manifest; no PNG regeneration or research run was
needed. This cleanup is a separate uncommitted follow-up to `77e7771` until the
human commits it; it does not alter source evidence or component-review status.

The API setup guide, integration readiness register and group report now link
the implemented figure delivery and distinguish it from pending acceptance.
The installed API inventory copy matched all four tracked source files byte for
byte; the retained records hash also matched its preparation manifest. Existing
accepted #203 request-time checks are reused for their unchanged scope.

The human figure rerun and technical readability/grayscale checks are recorded
above. Chathuranga also completed the [retained-route walkthrough](../forecast-inference-api.md#human-observed-retained-route-walkthrough--5-november-2026):
startup completed; roster/F01/F04 returned HTTP 200; F99 returned HTTP 404
`unknown_case`. His screenshot and pasted response establish these observations.
A separate read-only follow-up matched all 20 roster record objects and F01/F04
to the retained records, checked horizons and F04 gating, and verified F99. These
GET requests do not run inference. The API guide records source/revision scope,
executor/date, screenshot identity and the distinction from semantic acceptance.
B14's exact-export producer review (Chathuranga), consumer review (Didilani) and
technical representation review (Tinosh) remain human decisions, separate from
the file matches. D2, W2 and human code peer review must be recorded before the
relevant completion/merge decision. No existing scoped approval is repeated or
silently upgraded.

Next action: inspect the generated eight outputs at their intended insertion
size and arrange the scoped component and code reviews. Regeneration is needed
only if an approved change is made. The PNG/SVG/JSON bundle is trackable without `.gitignore`
changes. Keep any unrelated local modifications out of staging.

After the outputs and changes have been reviewed, a suggested focused commit is
`feat: add thesis-ready result figures`. Suggested commands, not executed:

```bash
git add .github/workflows/ci-quality.yml \
  docs/artifact-storage-policy.md \
  docs/forecast-inference-api.md docs/integration-contract-readiness.md \
  docs/group-report.md \
  docs/research/inventory-risk-visual-evidence.md \
  docs/research/thesis-figure-delivery.md reports/README.md \
  src/visualization/render_issue_201_views.py \
  src/visualization/thesis_evidence.py src/visualization/thesis_figures.py \
  tests/test_render_issue_201_views.py tests/test_thesis_figures.py \
  reports/figures/final-thesis-figures/
git diff --cached --stat
git commit -m "feat: add thesis-ready result figures"
```

Use existing PR #211 after an explicitly authorised human push; a second PR is
not proposed. Its scope/description and review must reflect the added figures,
preserve Didilani's authorship/contributions and link #201/#179/#182 accurately.
No commit, push, merge, branch change or GitHub message was performed here.
