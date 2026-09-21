# Member Onboarding Guide

## Purpose

This guide is for contributors who are new to GitHub, branches, Pull Requests, ChatGPT, or Codex.

You do not need to understand all of GitHub before starting. Follow the workflow one step at a time.

---

## 1. One-time setup

You need:

- access to the private GitHub repository;
- Git installed;
- a local clone of the repository;
- access to ChatGPT / Codex if you plan to use them;
- the UCI Online Retail dataset stored locally under `data/raw/`.

---

## 2. Confirm the repository

Repository:

```text
chathuranga-sudusinghe/retail-demand-framework
```

Do not create a separate copy unless the group explicitly decides to do so.

---

## 3. Understand your project documents

Before starting a task, read your own files.

### Chathuranga

```text
docs/team/chathuranga/group-project-overview.md
docs/team/chathuranga/individual-project-overview.md
```

### Didilani

```text
docs/team/didilani/group-project-overview.md
docs/team/didilani/individual-project-overview.md
```

### Dewmi

```text
docs/team/dewmi/group-project-overview.md
docs/team/dewmi/individual-project-overview.md
```

Remember:

```text
group-project-overview.md
= work for COMP1884

individual-project-overview.md
= future COMP1885 direction only
```

---

## 4. Start every task from latest main

Run:

```bash
git checkout main
git pull origin main
```

Do not start a new task from an old feature branch.

---

## 5. Create your branch

Example:

```bash
git checkout -b feature/my-task-name
```

Do not make development changes directly on `main`.

---

## 6. Use Codex as a guide first

If you are unsure what the Issue means, use:

```text
Read AGENTS.md and my relevant project documents.

I am working on GitHub Issue #<number>.

Do not change files yet.

Explain:
1. what I need to do,
2. what files are relevant,
3. what branch name I should use,
4. what output is expected,
5. what I should not change,
6. what tests or checks I should run.
```

Only ask it to implement after you understand the explanation.

---

## 7. Check before committing

Run:

```bash
git status
```

Make sure:

- you are on your feature branch;
- only expected files changed;
- the dataset is not being tracked;
- no secret or password is included.

---

## 8. Commit and push

Example:

```bash
git add .
git commit -m "feat: add assigned task"
git push -u origin feature/my-task-name
```

---

## 9. Open a Pull Request

On GitHub:

```text
Pull requests
-> New pull request
-> base: main
-> compare: your feature branch
```

Complete the Pull Request template.

Do not merge your own work before the required review.

---

## 10. If review asks for changes

Do not create a new branch.

Stay on the same feature branch, make the requested changes, then:

```bash
git add .
git commit -m "fix: address review feedback"
git push
```

The Pull Request updates automatically.

---

## 11. After merge

Run:

```bash
git checkout main
git pull origin main
```

Then start the next Issue on a new branch.

---

## 12. Common mistakes to avoid

Do not:

- type the GitHub URL by itself in a terminal and expect it to clone;
- work directly on `main`;
- upload the Excel dataset to GitHub;
- reuse one branch for many different tasks;
- let AI change research decisions without approval;
- ignore failing tests;
- copy code you cannot explain.

---

## 13. When to ask for help

Ask immediately if:

- Git shows a permission error;
- the repository will not clone;
- you are unsure which branch you are on;
- you see a merge conflict;
- Codex wants to change research methodology;
- the dataset appears in `git status`;
- you do not understand the expected output of an Issue.
