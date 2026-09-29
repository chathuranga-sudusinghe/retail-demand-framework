# Forecasting runner — Gate 2 implementation

Issue #52 implements the frozen validation contract in [protocol.md](protocol.md).
Gate 2 code and test evidence require human review at Gate 3. Neither this
document nor the runner grants Gate 4 execution approval. No approval manifest
for a project experiment is supplied. Final estimator/preprocessing fitting and
evaluation remain blocked at Gate 6.

## Components

| File | Responsibility |
|---|---|
| `src/forecasting/models.py` | Construct the five learned estimators from accepted configuration interfaces; enforce CPU, seed, threads, no stopping callbacks and exact fitted iteration counts; capture native defaults. |
| `src/forecasting/baselines.py` | Check the latest complete historical week and apply all four approved Naive/Seasonal Naive formulas. |
| `src/forecasting/metrics.py` | Raw-prediction WAPE/MAE/RMSE/Bias, explicit undefined/failure status and arithmetic means across exactly four folds. |
| `src/forecasting/evaluation.py` | Isolate authorised dates, join historical predictors and labels by native keys, record exclusions and prepare one fixed-origin vector/complete outcome per historical pair. |
| `src/forecasting/selection.py` | Require all 24 complete primary configurations, retain exact configuration/model ties separately by horizon, and keep supportive/baseline evidence outside RQ2 selection. |
| `src/forecasting/artifacts.py` | Exact v2 CSV column order, deterministic record order, atomic JSON/CSV writes and exclusive run directories. |
| `src/forecasting/progress.py` | Run-owned standard logging handlers for terminal progress and `run.log`; no model/data access or execution authority. |
| `src/forecasting/reporting.py` | Read-only human-review Markdown from persisted CSV/JSON metrics, selections and metadata. |
| `src/forecasting/metadata.py` | Validate a human-supplied run scope bound to the reviewed source/protocol/input; capture environment and build fingerprints without hashing final-period outcomes. |
| `src/forecasting/experiment.py` | Sequential orchestration, complete-fold preflight, failure diagnostics and seven required artifacts. Final-stage entry always raises `ExecutionBlocked`. |

Accepted feature, target, fold, preprocessing and canonical-grid modules are
reused unchanged. No research decision, feature, grid or evaluation date changes.

## Tests and safe local checks

Use the existing WSL virtual environment:

```bash
source .venv/bin/activate
python -m pytest -q
ruff check src/forecasting tests/test_forecasting_models_metrics_baselines.py tests/test_forecasting_evaluation.py tests/test_forecasting_experiment.py tests/test_forecasting_observability.py
python -m mypy src/forecasting --explicit-package-bases --disable-error-code import-untyped
git diff --check
```

The new tests create small in-memory synthetic panels and temporary artifacts.
The complete 1,152-fit primary plan is exercised with mocked estimators; the
32 supportive fits are also mocked. Separate library smoke tests fit controlled
random arrays with 200 rows, preserving frozen 100/300 boosting budgets and
the fixed supportive settings. They verify API compatibility, effective counts
and JSON-safe defaults, not research performance. Tests never read the project
dataset or invoke an authorised real experiment. Temporary mock outputs are
implementation diagnostics and must not become model-comparison evidence.

## Later validation execution interface — not authorised now

Only after human Gate 3 acceptance and specific Gate 4 authorisation may the
owner use the reviewed command shape:

```text
python -m src.forecasting.experiment --input <local-csv> --run-id <unique-run-id> --authorization <human-reviewed-manifest.json>
```

The manifest maps to `ValidationAuthorization` in `metadata.py`. It requires:

- the exact run ID, `evaluation_stage="validation"`, schema/protocol versions
  and full protocol byte hash;
- reviewed source hashes, including source/tests, requirements, AGENTS.md,
  the feature contract and relevant Decision Records;
- the fingerprint of the ordered four-column validation view, restricted to
  January 1–December 2 **before demand/key validation or fingerprinting**;
- protocol, full-implementation acceptance and specific-run human references;
- an explicit `validation_run_authorized=true` declaration and `worker_count=1`;
- ordered subsets of primary/supportive models and horizons; both simple
  baselines must have either explicit execution references or exclusion reasons.

The manifest contains `scope.primary_models`, `scope.supportive_models`,
`scope.horizons`, `scope.baselines`, `scope.baseline_exclusions` and
`scope.baseline_approval_references`. The last two use ordered `[model, reason]`
or `[model, reference]` pairs. It cannot add configurations, folds or horizons.
Every in-scope primary model/horizon still uses all 24 configurations and all
four folds. Approval references are local audit records supplied by the human;
they are not cryptographic authentication and cannot be generated by the runner.

Calling `run_validation` without that record fails before accessing inputs or
constructing estimators. The command checks it before reading the CSV. Native
50-SKU × 5-warehouse historical coverage is required by the real entry; pure
preparation helpers also support synthetic unit-test panels. All four folds
are prepared and checked before the first fit. Later folds may use previously
observed validation dates as historical training data, as the frozen schedule
requires. No final-period observation enters validation fingerprints or fitting.

## Outputs and diagnostics

Successful runs write the seven protocol artifacts under the ignored local
`outputs/revised-forecasting/<run_id>/` directory. Existing run IDs fail instead
of overwriting outputs. No raw/full dataset copy or model binary is saved.
Failed runs retain metadata, completed records and `diagnostics.json`; no
partial run is used for automatic selection. There is no retry or resume policy.

An authorised run also creates `run.log` in that same directory. Run-owned Python
logging handlers write the same operational events to standard output and the
file, without changing root/library logging. The initial event declares primary
fits, supportive fits and baseline evaluations separately. Fit start/completion,
candidate completion and failure events identify the run, validation stage,
fold, horizon, role, model and configuration. Counts and percentages distinguish
completed learned fits from completed evaluations (baselines never count as
fits). Elapsed times use a monotonic clock; completion reports total runtime.
Handlers close on success, failure or interruption. Logging setup occurs only
after authorisation and exclusive run-directory creation, never on import.

Logs allow only operational identifiers and counts, with no rows, matrices,
predictions, credentials or model internals. Known fixed failure messages are
logged directly. Arbitrary exception payloads are omitted because libraries can
embed input data or sensitive values; logs instead identify the exception type,
failing operation and existing `diagnostics.json` evidence. The operational log
is additional to the seven scientific artifacts and their unchanged manifest.

The complete native defaults are captured after fitting: XGBoost booster
configuration, LightGBM's native parameter block (tree data discarded), and
CatBoost's `get_all_params()`. Requested/effective tree counts must agree.
LightGBM can naturally stop with fewer trees when no further splits are possible;
that is an explicit failed fit under this protocol, even without early stopping.
The runner does not modify frozen parameters or manufacture trees to avoid it.

XGBoost's inherited `missing=np.nan` API sentinel is encoded as JSON null with
`unavailable_parameter_values.missing="library_nan_sentinel"`. Numerical input
matrices remain complete; prediction/metric NaN or infinity remains invalid.
Undefined WAPE uses `undefined_zero_actual_total`; it cannot establish a leader.
Zero observations remain numerical zero. No prediction clipping is performed.

Representation records identify the exact model/fold/horizon/training population
and link shared primary vocabularies. Selected effective API parameters are
retained by fold, since fitted native defaults can be data-dependent. Selection
and freeze references remain pending/null until separate human review. The
comparison is generated after saving `run_metadata.json`,
`selected_configurations.json`, `configuration_summary.csv` and
`fold_metrics.csv`. It copies stored values without calculating metrics or
differences. Its run summary records provenance, authorised scope, model roles
and blocked final status. Compact selected-configuration and primary WAPE
matrices precede separate 1/7/14/28-day sections with primary means, four-fold
WAPE comparisons, all tied primary configurations' fold metrics, separate
supportive/baseline tables, ties and limitations. Administrative representatives
are labelled; incomplete or unauthorised evidence remains explicitly unavailable.
No cross-horizon winner, statistical test or stability threshold is calculated.

The artifact manifest hashes every other artifact's full bytes. Its own
`run_metadata.json` hash is null with status `self_reference`: a file cannot
contain its own full-byte digest. Diagnostics have their own paths. Source and
authorised input hashes are independent of this self-reference limitation.

Final evaluation always remains inaccessible through this implementation,
including its CLI stage flag. Gate 6 must separately approve and implement the
final estimator/category/scaler reuse-versus-refit policy; no fold-4 reuse or
all-history refit is assumed. Future reporting must disclose both earlier
December 3–16 validation exposure and full-year EDA exposure.
