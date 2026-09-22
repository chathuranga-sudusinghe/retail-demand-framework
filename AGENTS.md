# AGENTS.md

## Purpose

This file defines the repository-wide rules that AI coding agents, including Codex, must follow when working in this project.

The repository is the shared implementation space for the COMP1884 group project:

**A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis**

AI tools are assistants. They must not invent research decisions, bypass the team workflow, or merge work directly into `main`.

---

## 1. Read before doing any work

Before modifying files, the AI agent must read:

1. `README.md`
2. `docs/project-overview.md`
3. `docs/project-boundaries.md`
4. `docs/research-design.md`
5. `docs/dataset.md`
6. `docs/references.md`
7. the relevant decision record under `docs/decisions/`
8. the relevant member overview under `docs/team/`
9. the relevant workflow under `docs/workflows/`
10. the assigned GitHub Issue or task description

If any instruction conflicts, stop and ask the user for clarification.

---

## 2. Branch rule

Never implement work directly on `main`.

Every implementation task must be completed on a feature branch.

Recommended naming:

```text
feature/<short-task-name>
research/<short-research-task>
fix/<short-fix-name>
docs/<short-doc-name>
test/<short-test-name>
```

---

## 3. Pull request rule

Changes must reach `main` through a Pull Request.

The agent must not:

- push implementation directly to `main`;
- merge its own Pull Request;
- bypass required review;
- force-push to `main`;
- delete protected branches;
- disable repository rules.

The normal flow is:

```text
GitHub Issue
    -> task branch
    -> implementation / research work
    -> tests / validation
    -> commit
    -> push branch
    -> Pull Request with "Closes #<issue-number>"
    -> review
    -> approval
    -> merge to main
    -> linked Issue auto-closes
```

If GitHub does not auto-close the linked Issue after merge, verify the Issue state and close it manually as completed.

---

## 4. Research decision rule

The AI agent may implement approved research decisions, but it must not silently create new research decisions.

Examples of decisions that require explicit team or supervisor approval where appropriate:

- changes to the approved analytical unit or aggregation frequency;
- changes to the approved forecasting target definition;
- product/SKU eligibility rules;
- model family selection when not already approved;
- final hypothesis wording;
- demand-regime definitions;
- inventory-risk definitions;
- replenishment formula/rules;
- evaluation metric changes;
- threshold definitions;
- use of source `Demand_Forecast`;
- replacement of the primary dataset.

If such a decision is missing, stop and ask.

---

## 5. Dataset rule

The selected **High-Dimensional Supply Chain Inventory Dataset** must remain local.

Never commit:

```text
*.xlsx
*.xls
*.csv
*.parquet
data/raw/*
data/processed/*
```

except approved small test fixtures.

Do not remove the dataset-protection rules from `.gitignore`.

The dataset is simulated. Do not describe it as observed data from a real operating company.

The project must build its own demand-forecasting models from historical `Units_Sold`.

Current approved forecasting grain from DR-002:

```text
SKU_ID + Warehouse_ID + Date
```

Current forecasting target:

```text
Units_Sold
```

`Stockout_Flag` is zero-variance in the verified dataset and must not be used as a stockout target or validation label.

The source `Demand_Forecast` field must not be used as a normal model target or feature unless an approved, leakage-safe research decision explicitly defines its use.

---

## 6. Reproducibility rule

Shared data preparation and modelling logic must live in source code, not only in notebooks.

Preferred locations:

```text
src/data/
src/forecasting/
src/inventory_risk/
src/visualization/
src/decision_support/
tests/
```

Notebooks may be used for exploration, but important implementation logic must be moved into reusable modules.

---

## 7. Time-series rule

For forecasting tasks:

- preserve chronological order;
- do not use random train/test splitting for the main time-series evaluation;
- avoid future-data leakage;
- generate lag and rolling features using only information available before the prediction point;
- document train/validation/test periods;
- compare advanced models with a simple baseline;
- ensure inventory states or source-generated forecasts are not accidentally used from the future.

---

## 8. Inventory-risk and replenishment rule

Didilani's component receives Chathuranga's forecast output at SKU-warehouse level and combines it with relevant inventory variables such as:

```text
Warehouse_ID
Inventory_Level
Reorder_Point
Supplier_Lead_Time_Days
Order_Quantity
```

`Stockout_Flag` may be retained only as a documented dataset field/limitation; it must not be treated as an observed stockout target or validation label.

Do not invent a replenishment rule silently.

Any risk level, threshold, or recommended replenishment quantity must have:

- a documented definition;
- a justified calculation/rule;
- leakage-safe temporal alignment;
- an evaluation or sensitivity check;
- clear limitations.

A recommendation is decision support, not an automatically executable purchase order.

---

## 9. Member boundaries

### Chathuranga

Primary COMP1884 area:

```text
Model training
Model comparison / selection
Demand forecasting
Forecast evaluation
```

Relevant docs:

```text
docs/team/chathuranga/group-project-overview.md
docs/workflows/demand-forecasting.md
```

### Didilani

Primary COMP1884 area:

```text
Inventory-risk analytics
Replenishment analysis
Visual analytics
Business interpretation
```

Relevant docs:

```text
docs/team/didilani/group-project-overview.md
docs/workflows/inventory-risk-analysis.md
```

### Dewmi

Primary COMP1884 area:

```text
Responsible decision support
Ethical / legal / governance analysis
Transparency and human oversight
```

Relevant docs:

```text
docs/team/dewmi/group-project-overview.md
docs/workflows/responsible-decision-support.md
```

Members may collaborate across boundaries, but ownership changes must be explicit.

---

## 10. COMP1884 repository scope rule

This repository contains the COMP1884 group implementation only.

Keep work in this repository focused on the approved group research question, integrated group product, member COMP1884 responsibilities, shared evidence, and collaboration workflow.

---

## 11. Testing rule

Before proposing a Pull Request:

- run relevant tests;
- add or update tests for new behaviour where practical;
- report any failing tests;
- do not hide test failures;
- do not change tests only to make incorrect code pass.

---

## 12. Commit rule

Use clear commit messages.

Recommended forms:

```text
feat: add demand forecasting baseline
feat: add replenishment risk rules
fix: correct lag feature leakage
docs: record research decision
test: add data validation tests
```

Keep commits focused on one logical change where practical.

---

## 13. Pull Request preparation

Before opening a Pull Request, the agent should provide:

- summary of changes;
- files changed;
- tests run;
- known limitations;
- related GitHub Issue;
- `Closes #<issue-number>` in the PR body;
- any research decision that still needs approval.

The agent must not claim work is complete when required validation has not been run.

---

## 14. Beginner-support rule

Some contributors are new to GitHub and Codex.

When asked for help, explain:

1. what task is being worked on;
2. what file(s) are relevant;
3. what branch should be created;
4. what command should be run next;
5. what should not be changed;
6. how to commit and push;
7. how to open a Pull Request.

Use simple, step-by-step instructions.

---

## 15. Stop conditions

The AI agent must stop and ask for clarification if:

- the task is not linked to the approved project scope;
- the requested change affects research methodology without approval;
- the task conflicts with repository documentation;
- the dataset handling rule would be violated;
- the user asks to bypass branch or Pull Request rules;
- the correct member/component ownership is unclear.

---

## 16. Source of truth

Use this priority order:

```text
1. Explicit current user instruction
2. Approved GitHub Issue / Pull Request discussion
3. docs/decisions/
4. docs/project-boundaries.md
5. docs/research-design.md
6. docs/dataset.md
7. member and workflow documentation
8. README.md
```

When two sources conflict, do not guess. Ask the user.
