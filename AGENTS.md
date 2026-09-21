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
6. the relevant member overview under `docs/team/`
7. the relevant workflow under `docs/workflows/`
8. the assigned GitHub Issue or task description

If any instruction conflicts, stop and ask the user for clarification.

---

## 2. Branch rule

Never implement work directly on `main`.

Every implementation task must be completed on a feature branch.

Recommended naming:

```text
feature/<short-task-name>
fix/<short-fix-name>
docs/<short-doc-name>
test/<short-test-name>
```

Examples:

```text
feature/data-cleaning-baseline
feature/inventory-risk-baseline
docs/update-research-design
test/data-validation
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
    -> feature branch
    -> implementation
    -> tests / validation
    -> commit
    -> push branch
    -> Pull Request
    -> review
    -> approval
    -> merge to main
```

---

## 4. Research decision rule

The AI agent may implement approved research decisions, but it must not silently create new research decisions.

Examples of decisions that require explicit team or supervisor approval:

- daily vs weekly demand aggregation;
- treatment of returns and cancellations;
- target definition;
- product eligibility rules;
- model family selection when not already approved;
- final hypothesis wording;
- demand-regime definitions;
- inventory-risk proxy definitions;
- evaluation metric changes;
- threshold definitions;
- changes to the group/individual project boundary.

If such a decision is missing, stop and ask.

---

## 5. Dataset rule

The UCI Online Retail dataset must remain local.

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

Do not invent values for missing data.

Do not silently convert returns or negative quantities into normal sales.

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

Notebooks may be used for exploration, but important production logic must be moved into reusable modules.

---

## 7. Time-series rule

For forecasting tasks:

- preserve chronological order;
- do not use random train/test splitting for the main time-series evaluation;
- avoid future-data leakage;
- generate lag and rolling features using only information available before the prediction point;
- document train/validation/test periods;
- compare advanced models with a simple baseline.

---

## 8. Inventory-risk rule

The source dataset does not contain true inventory state such as on-hand stock, safety stock, reorder points, or supplier lead time.

Therefore, do not describe derived outputs as observed historical stockouts or overstock events unless additional valid data are introduced.

Use terms such as:

```text
inventory-risk proxy
stockout-pressure indicator
overstock-pressure indicator
slow-moving-risk indicator
```

when appropriate.

---

## 9. Member boundaries

### Chathuranga
Primary COMP1884 area:

```text
Time-series demand forecasting
Model evaluation
Forecast error / bias / uncertainty
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

## 10. COMP1884 vs COMP1885 rule

This repository contains the COMP1884 group implementation.

The COMP1885 individual-project documents in `docs/team/*/individual-project-overview.md` are planning overviews only.

Do not implement the full COMP1885 projects inside this repository unless the team explicitly changes that decision.

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
feat: add weekly demand aggregation
fix: correct lag feature leakage
docs: clarify inventory risk proxy rules
test: add data validation tests
refactor: separate cleaning and aggregation logic
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
