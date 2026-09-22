# Contributing Guide

## 1. Purpose

This guide explains how group members should contribute to the `retail-demand-framework` repository.

The repository is shared by:

- Chathuranga Indrajith Sudusinghe
- Didilani Prasadika Weerawickrama Pathinayaka
- Haputhanthrige Dewmi Pramodya

All members have write access, but normal work must still follow the branch and Pull Request workflow.

---

## 2. Golden rule

**Do not work directly on `main`.**

Every task should follow:

```text
Issue
-> branch
-> work
-> commit
-> push
-> Pull Request with "Closes #<issue-number>"
-> review
-> merge
-> Issue auto-closes
```

---

## 3. Before starting work

Always update your local `main` branch first:

```bash
git checkout main
git pull origin main
```

Then read the GitHub Issue assigned to you.

Also read:

```text
README.md
AGENTS.md
docs/project-boundaries.md
your group-project-overview.md
the relevant workflow document
```

---

## 4. Create a feature branch

Create the branch from the updated `main`.

Example:

```bash
git checkout -b feature/inventory-risk-baseline
```

Recommended branch prefixes:

```text
feature/
research/
fix/
docs/
test/
refactor/
```

Examples:

```text
feature/data-cleaning-baseline
feature/time-series-features
feature/inventory-risk-baseline
research/temporal-demand-profile
docs/update-research-design
fix/cancellation-filter
```

---

## 5. Work only on your task

Do not make unrelated changes in the same branch.

If you notice another problem:

1. finish the current task;
2. create a separate GitHub Issue;
3. create a separate branch for that work.

This keeps Pull Requests easy to review.

---

## 6. Dataset handling

The source dataset remains local.

Place it under:

```text
data/raw/
```

Do not commit the dataset.

Before pushing, check:

```bash
git status
```

The raw dataset should not appear as a tracked file.

---

## 7. Commit your work

Check changes:

```bash
git status
```

Stage selected changes:

```bash
git add .
```

Commit:

```bash
git commit -m "feat: add inventory risk baseline"
```

Use a short and clear message.

---

## 8. Push your branch

First push:

```bash
git push -u origin feature/inventory-risk-baseline
```

Later pushes on the same branch:

```bash
git push
```

---

## 9. Open a Pull Request

On GitHub:

1. open the repository;
2. click **Pull requests**;
3. click **New pull request**;
4. set base branch to `main`;
5. select your feature branch as the compare branch;
6. complete the Pull Request template;
7. link and auto-close the relevant Issue by adding `Closes #<issue-number>` to the PR description;
8. request review;
9. do not merge until review requirements are satisfied.

---

## 10. Review process

The normal review process is:

```text
Contributor opens PR
        |
        v
Reviewer checks code / docs / tests
        |
        +--> changes requested -> contributor updates branch
        |
        v
Approval
        |
        v
Merge to main
```

Do not bypass review for convenience.

---

## 11. After a Pull Request is merged

Update your local `main`:

```bash
git checkout main
git pull origin main
```

Delete the old local branch when it is no longer needed:

```bash
git branch -d feature/inventory-risk-baseline
```

Verify that the PR's linked Issue was automatically closed. If it was not, close it manually as completed.

Then start the next Issue from the updated `main`.

---

## 12. Working with Codex / ChatGPT

You may use ChatGPT and Codex to help with this project.

Before asking Codex to implement anything, ask it to read:

```text
AGENTS.md
README.md
docs/project-boundaries.md
your group-project-overview.md
the relevant workflow file
the assigned GitHub Issue
```

A good first prompt is:

```text
Read AGENTS.md and the project documentation relevant to my assigned task.

I am working on GitHub Issue #<number>.

First explain:
1. what this task requires,
2. which files are relevant,
3. which feature branch I should create,
4. what I must not change.

Do not modify files yet.
```

Only after you understand the plan should you ask the agent to implement.

---

## 13. Research decisions

Do not let an AI tool silently decide important research methodology.

Examples requiring explicit discussion:

- changes to the approved target definition;
- changes to the approved analytical unit / aggregation frequency;
- return/cancellation treatment;
- demand-regime definition;
- risk-proxy definition;
- hypothesis changes;
- evaluation metrics;
- model comparison rules.

Record important decisions in:

```text
docs/decisions/
```

---

## 14. Need help?

If you are unsure what to do:

1. do not push random changes;
2. do not edit `main`;
3. ask in the group;
4. ask ChatGPT/Codex to explain the task using the repository documentation;
5. open or update a GitHub Issue when necessary.
