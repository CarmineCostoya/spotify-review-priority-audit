# Interruption and resume recording guide

## What the recording must prove

The assignment asks for checkpoint snapshots showing saved work, an interruption, and then new completed work
after resume without paying to relabel IDs that were already complete under unchanged settings. The official
run already contains this evidence:

- `grading/checkpoint_before.json`: 9,309 completed IDs saved before interruption
- `grading/checkpoint_after.json`: 100,000 completed IDs after recovery
- `grading/calls.jsonl`: initial and resume call records
- `outputs/runs/final-100000/recovery.md`: the written recovery narrative

The verification command below reads those real artifacts. It makes no model calls, uses no API key, and does
not modify the official run.

## Before recording

1. Close `.env`, API billing pages, password managers, messages, and unrelated browser tabs.
2. Open a terminal at the repository root and increase the terminal font size.
3. Open the public GitHub README and live dashboard in two browser tabs.
4. Use a screen recorder with microphone audio. On macOS, QuickTime Player's **New Screen Recording** is enough.
5. Record only the terminal and the two assignment tabs. Do not record the whole desktop if notifications or
   private information could appear.

Recommended length: 3 to 4 minutes.

### Silent caption option

If recording without a microphone, open `docs/recording_captions.html` in a browser. It contains seven
full-screen caption cards. Use the left and right arrow keys to move between them, switching to the terminal or
dashboard whenever the corresponding evidence should be shown.

## Commands to copy before starting

Run each command separately while recording:

```bash
clear
git status --short
python3 scripts/verify_resume_evidence.py
nl -ba src/spotify_audit/pipeline.py | sed -n '42,90p'
sed -n '1,80p' outputs/runs/final-100000/recovery.md
```

Expected verifier result:

```text
Completed before interruption:       9,309
Completed after recovery:            100,000
Newly completed after resume:        90,691
Previously completed IDs resubmitted:         0
FINAL RESULT: PASS
```

The 90,691 newly completed IDs include direct model classifications and valid exact-text cache reuse. Therefore,
that number is larger than the number of unique IDs sent to resumed model enrichment.

## One-take speaking script

### 0:00 - 0:25: Introduction

> This is the interruption and resume demonstration for my Spotify review priority audit. The professor updated
> the required scope to 100,000 reviews. This repository contains the completed official run, its saved
> checkpoints, and the complete call log.

Show the GitHub README briefly, including the final result and submission links.

### 0:25 - 1:30: Verify the saved checkpoints

Run:

```bash
python3 scripts/verify_resume_evidence.py
```

Say:

> Before the interruption, the checkpoint contained 9,309 completed review IDs. After resuming and recovery,
> the final checkpoint contained 100,000. The resume therefore added 90,691 completed IDs. The verifier also
> compares the pre-interruption IDs with every review ID in resume enrichment calls. The overlap is zero, so no
> already completed ID was paid for and enriched again.

Pause long enough for the `FINAL RESULT: PASS` line to be readable.

### 1:30 - 2:25: Show the resume mechanism

Run:

```bash
nl -ba src/spotify_audit/pipeline.py | sed -n '42,90p'
```

Say:

> At startup, the pipeline loads saved records by review ID. In resume mode it writes those completed IDs into
> the before checkpoint. While reading the source CSV, it skips an ID that already has a valid completed record.
> Pending reviews are the only ones sent to enrichment. Exact duplicate text can reuse a saved result only when
> the label configuration is unchanged, and the new ID keeps direct cache-source provenance.

Point to the completed-ID check, the `continue`, and the label-configuration comparison.

### 2:25 - 3:05: Show the recovery record

Run:

```bash
sed -n '1,80p' outputs/runs/final-100000/recovery.md
```

Say:

> The official run was interrupted after 9,309 completions and resumed with five bounded workers. Failed batches
> were retried with smaller batch sizes until all 100,000 reviews were complete, with zero unresolved records.
> The complete call log preserves initial, resume, failure, and recovery attempts.

### 3:05 - 3:35: Show the result

Open the live dashboard and say:

> The recovered results feed the deterministic ranking and the deployed database-backed dashboard. The final
> recommendation is to prioritize general playback reliability. The dashboard and repository are public and
> linked from the README.

### Closing sentence

> This demonstrates saved progress, a real interrupted run, new completed work after resume, and zero
> re-enrichment of IDs that were already complete.

## After recording

1. Watch the entire video once. Confirm the terminal output is readable and no secrets or notifications appear.
2. Upload it somewhere the grader can open without requesting access, such as an unlisted YouTube video or a
   public view-only Drive link.
3. Test the recording URL in a private browser window.
4. Add the URL to the README under a short **Interruption/resume recording** heading.
5. Commit and push the README update, then test the GitHub link while signed out.
