# Contributing Guide

Work from an assigned Issue on a dedicated task branch in the existing repository. Keep the change reviewable, preserve unrelated work and obtain human review before acceptance. Branch commands and PR-opening/merging instructions below are for humans to perform; AI assistants must not perform those actions. Other permitted Git operations still require explicit user authorization before an AI agent performs them.

## 1. One-time setup

You need repository access, Git, Python **3.12.3**, and the existing local repository. In WSL, keep the repository and its virtual environment on the Linux filesystem. Do not create a sibling copy or another worktree.

From the repository root, after approval to prepare your environment:

~~~bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
~~~

Confirm the exact Python patch version; a 3.12 interpreter is not automatically 3.12.3. Dependencies are pinned. Obtain the [dataset](docs/dataset.md) locally under data/raw/ only when your task requires it. The repository does not distribute it. Environment setup and data possession do not authorize preparation or experiments.

## 2. Reading order and responsibility

Read [README](README.md), [AGENTS](AGENTS.md), [overview](docs/project-overview.md), [boundaries](docs/project-boundaries.md), [research design](docs/research-design.md), [dataset](docs/dataset.md), [references](docs/references.md), relevant [decisions](docs/decisions/README.md), your member overview/workflow, and the assigned Issue before implementation.

| Member | Overview | Workflow / review responsibility |
|---|---|---|
| Chathuranga | [Research Team Lead & Forecasting](docs/team/chathuranga/group-project-overview.md) | [Forecasting](docs/workflows/demand-forecasting.md); forecasting meaning and shared API architecture/integration review |
| Didilani | [Inventory Risk & Replenishment](docs/team/didilani/group-project-overview.md) | [Inventory risk](docs/workflows/inventory-risk-analysis.md); rules, analytical meaning and business interpretation |
| Dewmi | [Responsible Decision Support](docs/team/dewmi/group-project-overview.md) | [Responsible support](docs/workflows/responsible-decision-support.md); semantics, governance and human oversight |
| Tinosh | [System Integration & Prototype](docs/team/tinosh/group-project-overview.md) | [Integration](docs/workflows/system-integration-and-prototype.md); adapters, delivery schemas, technical visuals and integration tests |

Code changes require review and approval by at least one other human team member before merging into main; human reviewers may use AI assistance, but must inspect the changes and make their own approval decision. Self-review or AI review alone does not satisfy this requirement. Cross-component review is encouraged where relevant. Technical implementation does not transfer analytical ownership. Missing/conflicting research decisions must be referred to their human owner, not resolved silently by AI.

## 3. Issue and branch workflow

An Issue should name the problem, owner, expected component/files, acceptance criteria, dependencies, approved research decisions and definition of done. Implement that scope. An AI assistant may draft or suggest an Issue, but must explain the proposal and obtain explicit user permission for that specific Issue before creating it on GitHub. A perceived need for an Issue or approval for a different Issue is not permission to create one.

Begin with read-only inspection:

~~~bash
git status --short --branch
git branch --show-current
~~~

Reuse an existing matching task branch. Never implement on main or reuse one branch for unrelated Issues. Determine whether synchronization is needed before proposing it; do not blindly pull or switch with unrelated modifications. A human creates any new task branch; AI assistants provide the exact command and wait for the branch to exist rather than creating it themselves. Branch names may use feature/, research/, fix/, docs/, test/ or refactor/ naming. For example, the human runs:

~~~bash
git checkout -b feature/inventory-risk-baseline
~~~

The normal sequence is Issue -> branch -> scoped work -> checks -> human review -> commit/push -> Pull Request -> required review/approval -> merge to main. No step grants standing authorization for later Git actions. Do not reset, stash, discard, force-push or resolve conflicts by overwriting another contributor's work.

## 4. Implementation, tests and AI assistance

Ask Codex to explain the Issue, relevant files, existing branch, expected outputs, prohibited changes and safe checks before unfamiliar work. Understand and review its output; AI-generated text/code is not automatically accepted evidence or a research decision.

Use reusable src/ modules and repository tools. Run targeted checks first. MyPy configuration is in [mypy.ini](mypy.ini); Ruff and pytest commands follow the [quality](.github/workflows/ci-quality.yml) and [test](.github/workflows/ci-tests.yml) definitions. Some model tests include small native fits, so inspect test scope when fitting is prohibited. Never hide failures or alter tests merely to make wrong behavior pass.

Actual training, tuning, validation, final evaluation, large analysis and real data preparation require explicit human authorization for the particular operation. The responsible component member reviews the run within the approved scope and manually starts it in their own terminal. Chathuranga handles forecasting; Didilani may run her approved inventory-risk work. Shared preparation and cross-component work require review by the relevant members and a named human executor; decisions requiring group agreement, including DR-012 approval, remain team decisions. AI assistants prepare code, explain commands and hand them to the member; research execution remains human under [AGENTS §17](AGENTS.md#17-experiment-execution-responsibility). A passing synthetic test, documentation merge or protocol approval does not authorize a research run. Preserve chronological order, fixed features, exact scope and reserved-outcome safeguards.

## 5. Evidence and progress handoff

Use [applied MLOps](docs/workflows/applied-mlops.md) for reproducibility/review controls, [storage policy](docs/artifact-storage-policy.md) for retention and [report index](reports/README.md) for findings. Link exact run IDs, stage, evidence, completion/review status, limitations and the actual approving references. Generated metrics and logs are not human approval.

Update [research progress](docs/research-progress.md) after material milestones, discussions, blockers or decisions; the contributor closest to the work drafts the entry and the component owner checks claims. Detailed decisions belong in Decision Records and meetings in their own records. Retain failed/incomplete evidence and never regenerate unavailable history as if it were original evidence.

## 6. Commit, push and Pull Request

First review status/diff and ensure only intended files changed, data/secrets are untracked and checks pass. Stage explicit reviewed files. These are examples for a human-approved next step:

~~~bash
git add <reviewed-file-paths>
git commit -m "<type>: <short summary>"
git push -u origin <task-branch>
~~~

The human contributor opens a Pull Request with base main and the task branch as head; AI assistants may prepare its title, description and instructions but must not open or merge it. Complete the [template](.github/PULL_REQUEST_TEMPLATE.md), including summary, files, tests/results, evidence where relevant, limitations, unresolved decisions and **Closes #<issue-number>**. For code changes, request review from at least one human team member other than the author of the changes and record their review and approval on the PR. AI tools may assist the human reviewer with inspection and findings, but the reviewer must assess the changes and decide whether to approve. Self-review, AI review alone and passing checks do not replace human peer review. Substantive code changes after approval require renewed review and approval of those changes. Once that review is complete, review blockers are resolved and required checks pass, either the human task/PR author or the human reviewer may merge, subject to repository permissions and protections. Do not merge unreviewed or failing work for convenience. Branch creation and PR opening/merging remain human-only under [AGENTS](AGENTS.md).

## 7. Review feedback and conflicts

Address review feedback on the **same task branch**; a new branch is not needed. Explain changes, rerun relevant checks and commit/push only after authorization. The existing Pull Request updates automatically.

If behind main, inspect the divergence before choosing synchronization. Ask for help with unfamiliar conflicts. Preserve both contributors' intended behavior and resolve against the approved contracts, not whichever side is quickest. Do not use blind reset/checkout conflict choices or unapproved merge/rebase.

After an approved merge, verify that GitHub closed the linked Issue; if not, a human-authorized follow-up should close it as completed. Synchronize local main only when needed and approved. Branch deletion also requires authorization. Start the next unrelated Issue on its own branch.

## 8. Beginner mistakes and when to ask for help

Avoid typing a GitHub URL alone as a shell command, developing on main, committing dataset files or secrets, copying code you cannot explain, mixing unrelated work, ignoring failing tests, and treating source Demand_Forecast as the project's forecast. Preserve .gitignore protections for raw/processed data, artifacts and models.

Ask for help when repository access fails, the current branch is unclear, a merge conflict appears, dataset files appear in status, an Issue's output is unclear, or a proposed change affects research methodology. Human review is the final control point; unresolved rules are not permission to invent a default.
