# Collaboration Workflow

## Goal

This document defines the official contribution workflow for the COMP1884 group project.

The objective is to keep the repository safe, reviewable, reproducible, and understandable for contributors who are new to GitHub.

---

## 1. Workflow overview

```text
Project documentation
        |
        v
GitHub Issue
        |
        v
Assigned contributor
        |
        v
Update local main
        |
        v
Create task branch
        |
        v
Work with ChatGPT / Codex if needed
        |
        v
Run tests / validation
        |
        v
Commit
        |
        v
Push feature branch
        |
        v
Open Pull Request with "Closes #<issue-number>"
        |
        v
Review and required approval
        |
        v
Merge to main
        |
        v
Linked Issue auto-closes
        |
        v
Verify Issue state and pull latest main locally
```

---

## 2. Main branch

`main` is the integration branch.

It should contain only work that has passed the agreed review process.

Normal contributors must not use `main` as a development branch.

---

## 3. Task branches

Every Issue gets its own branch.

Recommended prefixes include:

```text
feature/
research/
docs/
fix/
test/
refactor/
```

Examples:

```text
feature/shared-data-validation
research/temporal-demand-profile
feature/forecasting-baseline
feature/inventory-risk-baseline
feature/responsible-decision-view
docs/update-research-design
```

Do not reuse one long-lived branch for unrelated Issues.

---

## 4. Issue-first rule

Implementation should normally begin from a GitHub Issue.

An Issue should explain:

- problem / goal;
- owner;
- expected files or component;
- acceptance criteria;
- dependencies;
- research decisions already approved;
- definition of done.

AI tools should implement the Issue, not invent a different task.

---

## 5. Pull Request rule

Every implementation branch must be reviewed through a Pull Request.

The Pull Request should include:

- `Closes #<issue-number>` so the linked Issue auto-closes when merged to `main`;
- summary;
- files changed;
- tests/validation;
- screenshots or outputs where relevant;
- known limitations;
- any unresolved research question.

---

## 6. Review responsibilities

### Chathuranga
Acts as project coordinator and primary integration reviewer.

### Didilani
Reviews work relevant to inventory-risk analytics, interpretation, and shared integration when requested.

### Dewmi
Reviews work relevant to responsible decision support, governance, transparency, and shared integration when requested.

Cross-review is encouraged because this is one integrated group project.

---

## 7. AI-assisted contribution model

The team may use ChatGPT and Codex.

The recommended model is:

```text
Human reads / understands Issue
        |
        v
AI explains task
        |
        v
Human confirms plan
        |
        v
AI helps implement
        |
        v
Human checks output
        |
        v
Tests
        |
        v
Pull Request
        |
        v
Human review
```

AI output is not automatically accepted as correct.

---

## 8. What AI is allowed to do

AI may:

- explain repository documentation;
- explain assigned Issues;
- suggest branch names;
- edit code on a feature branch;
- write tests;
- explain errors;
- prepare commit messages;
- help prepare Pull Request descriptions;
- explain review feedback;
- make approved documentation changes.

---

## 9. What AI must not decide alone

AI must not silently decide:

- research hypotheses;
- changes to the approved target variable definition;
- data cleaning policy;
- changes to the approved analytical unit / aggregation frequency;
- inventory-risk meaning;
- model evaluation policy;
- scope changes;
- member/component boundaries.

These are project/research decisions.

---

## 10. Example member workflow

Example for Didilani:

```bash
git checkout main
git pull origin main
git checkout -b feature/inventory-risk-baseline
```

She then works only on the assigned Issue, commits, and pushes:

```bash
git add .
git commit -m "feat: add inventory risk baseline"
git push -u origin feature/inventory-risk-baseline
```

Then she opens a Pull Request to `main` and includes:

```text
Closes #<issue-number>
```

When the PR is merged to `main`, GitHub should automatically close the linked Issue. The Issue state must still be verified after merge.

The same process applies to all members.

---

## 11. Merge discipline

Do not:

- force push to `main`;
- merge without required approval;
- push dataset files;
- merge failing work simply to keep moving;
- combine unrelated changes in one Pull Request.

---

## 12. Conflict resolution

If a feature branch is behind `main`, update it carefully before merge.

A beginner should ask for help rather than guessing through a merge conflict.

The priority is preserving correct work, not completing the merge quickly.
