# Local file verification

Related: [Issue #169](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/169).
This guide checks file identity against shared references. It does not approve
research, consumer acceptance, inventory timing or a new experiment.

## Choose the reference first

Use this guide, the verifier and [2026-10-06.json](2026-10-06.json) from a
human-reviewed repository revision. Obtain the expected full Git commit SHA
independently from the reviewed GitHub PR/commit or the human sender.
A hash copied from the same untrusted file does not establish its identity.
GitHub hosts the reference metadata; datasets, models and ZIPs remain local.

The reference records the original 6 October member-package hashes and payload
hashes, the raw-source CSV/receipt identities, and retained run-manifest anchors.
The CSV hash comes from its existing acquisition receipt. The receipt file's own
hash was first registered from the retained local file for #169, rather than
being independently corroborated by an earlier receipt-hash record.
It is prepared for human review under #169. Publishing a hash does not change any
existing acceptance or approval status. The package source commit is historical
provenance, not a requirement to reset a member's current checkout.

## Member commands

Open PowerShell on Windows, or Terminal on macOS/Linux/WSL, in your existing
retail-demand-framework repository root. Use the project's Python 3.12.3;
Python 3.10 or later is supported. The verifier needs Git on PATH and uses only
the Python standard library; no model dependencies are needed.
Use your configured project interpreter if applicable: `.\.venv\Scripts\python.exe`
on Windows or `.venv/bin/python` on macOS/Linux/WSL.

Set reviewed_commit to an independently obtained full SHA containing these
verification files; the historical package-source commit is not that revision.
Run only your assigned member command.

**Windows PowerShell:**

~~~powershell
$reviewed_commit = "FULL_40_CHARACTER_REVIEWED_COMMIT_SHA"

# Dewmi: the installed forecast export (1 file)
python -m src.data.verify_checksums --profile dewmi --tracked-ref "$reviewed_commit"

# Didilani: installed export and validated dataset bundle (5 files)
python -m src.data.verify_checksums --profile didilani --tracked-ref "$reviewed_commit"

# Tinosh: installed saved-model bundles and metadata (20 files)
python -m src.data.verify_checksums --profile tinosh --tracked-ref "$reviewed_commit"
~~~

If your Windows installation uses the Python launcher, replace python with py -3.
Check that the selected interpreter meets the minimum version.

**macOS/Linux/WSL (Bash or Zsh):**

~~~bash
reviewed_commit="FULL_40_CHARACTER_REVIEWED_COMMIT_SHA"

# Dewmi: the installed forecast export (1 file)
python3 -m src.data.verify_checksums --profile dewmi --tracked-ref "$reviewed_commit"

# Didilani: installed export and validated dataset bundle (5 files)
python3 -m src.data.verify_checksums --profile didilani --tracked-ref "$reviewed_commit"

# Tinosh: installed saved-model bundles and metadata (20 files)
python3 -m src.data.verify_checksums --profile tinosh --tracked-ref "$reviewed_commit"
~~~

Later multiline examples use Bash syntax. In PowerShell, put the command on one
line and use your Windows interpreter.

Output identifies the exact reference SHA-256, repository HEAD and matched
reference revision. With --tracked-ref, the reference must match that commit
before any payload is checked. Each selected file must then print OK, followed
by Files matched: N/N.
Exit code 0 means every selected file matched; 1 means a content check failed;
2 means a reference, argument or setup error prevented verification. Missing files
fail; they are not skipped. Send the full output, command and reference commit to
the sender. Commands run without --tracked-ref are provisional: exit 0 then
means only that payload bytes match the supplied local reference. A warning is
printed if that reference is untracked or differs from HEAD; even a HEAD match
does not independently establish human review. Do not treat a provisional match
as verification against the sender's reviewed reference.

If the reference file is not present in the supplied reviewed commit, or its
bytes differ, a reviewed-commit check fails. Provisional checks can help review
byte identity, but cannot be presented as a completed trusted handoff check.

These commands check the actual installed repository paths. Keep original ZIPs
and extracted package folders under the ignored research-materials/ directory.
Keep HANDOFF/ inside that extracted folder; it does not belong at the repository
root. ZIP files elsewhere are not automatically Git-ignored.
To check the extracted package itself, run sha256sum -c HANDOFF/SHA256SUMS from
that extracted folder, as described in the original handoff.

Optionally check the original member ZIP as well. Replace the example absolute
archive path with the file's actual location:

~~~bash
python3 -m src.data.verify_checksums --profile didilani \
  --tracked-ref "$reviewed_commit" \
  --archive /absolute/path/to/research-materials/didilani-handoff-final-20261003-02.zip
~~~

Windows PowerShell equivalent (replace the path with your actual ZIP location):

~~~powershell
python -m src.data.verify_checksums --profile didilani --tracked-ref "$reviewed_commit" --archive "C:\path\to\retail-demand-framework\research-materials\didilani-handoff-final-20261003-02.zip"
~~~

The archive is checked in addition to the installed payload. A renamed archive
can match by content. This option is only available for a named member profile.

## Recover an existing Windows reference checkout

[.gitattributes](../../.gitattributes) keeps docs/checksums/2026-10-06.json
as LF on checkout. Without this rule, core.autocrlf=true can produce a CRLF
working copy whose bytes differ from the committed reference, even though Git
considers the text unchanged. The verifier correctly rejects those bytes.

Adding or pulling the attributes rule does not necessarily rewrite an existing
CRLF copy. Use this one-file recovery only for a confirmed line-ending issue in
the checksum reference, after a human has reviewed the rule and approved updating
to a revision containing it. Do not apply it to data, models, ZIPs or other
mismatching payloads.

1. From the repository root, inspect the local state and effective rule:

   ~~~text
   git status --short --branch
   git diff HEAD -- docs/checksums/2026-10-06.json
   git check-attr text eol -- docs/checksums/2026-10-06.json
   git ls-files --eol -- docs/checksums/2026-10-06.json
   ~~~

   Stop and contact the sender if there are local edits, a substantive reference
   difference, or uncertainty about the reviewed revision. The effective attributes
   must report text: set and eol: lf. In the last command, i/lf w/crlf together
   with attr/text eol=lf identifies the LF-in-Git/CRLF-in-working-copy condition.
   An empty Git diff can coexist with those CRLF bytes. If it reports w/lf, the
   working copy already has LF; stop and contact the sender about the mismatch.
   For other states, including mixed line endings, contact the sender before recovery.

2. Using your file manager, create a new, uniquely named backup folder under
   research-materials/, for example `research-materials/checksum-recovery-<unique-name>/`.
   **Move only** docs/checksums/2026-10-06.json into that folder, keeping its
   filename. Preserve the backup; do not overwrite any earlier backup. The original
   reference path must now be absent. This preserves the exact previous bytes.

3. Restore that missing reference from the current reviewed checkout. This command
   requires Git 2.23 or later and works in PowerShell and macOS/Linux/WSL terminals:

   ~~~text
   git restore --source=HEAD --worktree -- docs/checksums/2026-10-06.json
   ~~~

   Git recreates the file using the LF rule. A restore without first moving the
   existing file may leave its old bytes unchanged. No reference hashes or payloads
   are regenerated, and the backup remains local under ignored research-materials/.

4. Rerun your member command with the independently supplied full reviewed commit
   for the updated repository version. A previous revision may fail the tracked
   comparison because this fix changes tracked files. Do not replace the supplied
   revision with HEAD merely to make a check pass. Send the complete output,
   including the reference revision, SHA-256, HEAD, matched counts and any errors.
   If verification still fails, preserve both copies and contact the sender.

## Tracked source, configuration and documentation

Git supplies the versioned reference for all tracked content, including source,
tests, dependencies, configuration, AGENTS.md and methodology documents. This
avoids a checksum file hashing itself or becoming stale on every source edit.

After independently obtaining a reviewed full commit SHA, replace the placeholder:

~~~bash
python3 -m src.data.verify_checksums --tracked-only \
  --tracked-ref FULL_40_CHARACTER_REVIEWED_COMMIT_SHA
~~~

Or check tracked content and a member's payload together:

~~~bash
python3 -m src.data.verify_checksums --profile didilani \
  --tracked-ref FULL_40_CHARACTER_REVIEWED_COMMIT_SHA
~~~

--root must be the Git repository top-level directory. Tracked checks stop if
any index entries have assume-unchanged or skip-worktree flags, because these can
hide working-tree changes from git diff. The verifier does not clear these flags.
A tracked mismatch stops the combined check before the artifact references are
used. The comparison includes staged/unstaged tracked additions, modifications and
deletions relative to the supplied commit. It compares Git content, so configured
line-ending normalization can make Git-equivalent files have different physical
bytes. It does not claim SHA-256 equality of every tracked working-tree file.

Untracked files are reported outside this comparison; ignored files are covered
only when explicitly inventoried in a selected profile/bundle. An OK tracked result
does not mean there are no extra local files. Do not reset, stash, discard changes,
pull or switch branches automatically to make a check pass.

The independently trusted verifier/reference must be inspected before execution.
Checking a program using that same untrusted program is not a trust bootstrap.

## Other retained project artifacts

Available lightweight profiles:

| Profile | Files checked |
|---|---|
| source | Original source CSV and its acquisition receipt: 2 files |
| validated | Validated Parquet, schema, audit and provenance: 4 files |
| anchors | Validation/final completion manifests only: 2 files |
| all | Union of the profiles, deduplicated: 28 files |

~~~bash
python3 -m src.data.verify_checksums --profile source --tracked-ref "$reviewed_commit"
python3 -m src.data.verify_checksums --profile validated --tracked-ref "$reviewed_commit"
python3 -m src.data.verify_checksums --profile anchors --tracked-ref "$reviewed_commit"
python3 -m src.data.verify_checksums --profile all --tracked-ref "$reviewed_commit"
~~~

all means all registered profile files. It does not scan every file in the
repository or verify all models from the research study. Members should use their
own profile; they are not expected to possess other members' files or the source CSV.

For someone retaining a complete research bundle, the optional bundle checks first
verify the independently pinned completion-manifest bytes, then read its existing
inventory. They do not rewrite or regenerate that manifest:

~~~bash
python3 -m src.data.verify_checksums --bundle final --tracked-ref "$reviewed_commit"
python3 -m src.data.verify_checksums --bundle validation --tracked-ref "$reviewed_commit"
~~~

The original final inventory has 93 entries; validation has 2,537 entries. Each
command also checks its completion manifest. These can read substantial data from
disk; explain the scope and obtain human direction before a large full-bundle scan.
They are not part of an ordinary member check. A member-specific derivative subset
will correctly report missing files if checked as a complete research bundle.

All checks read bytes and metadata only. They never deserialize model/dataset
payloads, start the API, train, run inference, replay predictions, calculate
research metrics or repeat scientific verification. Byte matching does not establish
scientific correctness, origin availability, consumer acceptance or run approval.

## Coverage and updates

The initial profiles cover the supplied member payload, raw/validated source
references and completed validation/final anchors. Full-bundle inventories extend
coverage to their listed models, preprocessing, predictions, outcomes, metrics,
logs and retained snapshots, without copying bulk inventories into Git.

Other ignored files, the failed first final run, university/private materials,
scratch files, caches and virtual environments are not registered by this initial
reference. Do not describe them as verified. Credentials and secrets must not be
published or inventoried here.

To add another important artifact/version:
1. Identify the exact retained path, owner, version and existing trustworthy receipt
   or manifest. Preserve historical bytes and approval attribution.
2. Verify its reference provenance with the responsible human. Record identity
   separately from review/acceptance. Never derive a new expected hash from a
   mismatching recipient file merely to make it pass.
3. Add a versioned reference/profile or a pinned existing bundle anchor and document
   its scope and command. Keep original versioned references unchanged. For a new
   checksum-reference JSON filename, add its explicit text eol=lf rule to
   .gitattributes in the same reviewed change and test its checkout behavior.
4. Run focused synthetic verifier tests and inspect the new metadata. Submit only
   lightweight references/code/docs through the human PR/review workflow.

The optional bytes fields in the JSON are informational metadata; SHA-256 is
the identity check. They are not separate size validations.

On MISSING, ERROR or MISMATCH, retain the output and contact the sender/relevant owner.
Do not overwrite files, refresh expected hashes or retrain to repair an identity
failure.

## AI assistant instructions

Read the repository [AGENTS.md](../../AGENTS.md) and use the member's narrowest
applicable profile before relying on supplied artifacts. Report the reference
revision, reference SHA-256, repository HEAD, command, coverage, matched counts
and failures. Distinguish reviewed-reference checks from provisional local matches. If no profile covers a
required file, say it is unverified and request the correct reference; do not
silently expand scans or invent acceptance. Use an independently reviewed commit
for tracked-content comparison when required.

Use the existing [storage policy](../artifact-storage-policy.md) and
[MLOps workflow](../workflows/applied-mlops.md). This guide changes no research,
retention, execution, component-ownership or Git-approval rule.
