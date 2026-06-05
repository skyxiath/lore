# Lore — Working Guidelines

How we work on this project. Read this before adding research, planning, or writing.

## 1. Lead with the load-bearing point

The single most important fact about CutClaw — that **it edits already-edited films, not raw footage** — got buried across four conversation turns before it surfaced, and that wasted real time. Don't do that.

- State the conclusion first, then support it. One sentence that changes the decision goes at the top, not in a sub-clause.
- If a finding undercuts or reframes the whole project, it is the headline. Promote it.
- No hedging soup. If something is true, say it plainly; if it's uncertain, say *that* plainly and move on.

## 2. Primary sources only; the founding conversation is unreliable

This project began from a pasted chat transcript the user explicitly flagged as **not reliable**. Treat it as a source of *questions*, never *answers*.

- Every load-bearing claim (CutClaw internals, leaderboard numbers, "X uses audio", "no system does Y") is verified against the paper, the repo, the leaderboard, or the dataset card — not from memory or summary.
- Research dossiers carry inline citations and a `## Sources` list. A claim without a source is marked as inference.
- We re-verify surprising or numeric claims a second time (the research workflow has an adversarial verify pass for this reason).

## 3. Know exactly what we keep vs. gut from CutClaw

Lore is **not** "CutClaw but more audio-aware." It is CutClaw's *music-sync spine* applied to the regime CutClaw's benchmark never tested, with two structural changes.

- **KEEP:** music-as-skeleton, the keypoint grid, `Q_sync`, the Playwriter→Editor→Reviewer agent structure, AV-Harmony as a metric. This is the validated core (removing it is CutClaw's biggest ablation hit).
- **GUT:** the protagonist machinery (Identity Injection, Protagonist Presence Ratio `R_prot`, Semantic Identity Verification). The wearer is behind the camera; there is nothing to track.
- **ADD:** (a) a joint audio+visual **highlight-worthiness gate** upstream of the Playwriter — the stage CutClaw never needed because films have no dead time; (b) **event/activity segmentation** to replace PySceneDetect (raw footage has no editorial cuts); (c) an **activity/place/time/attention** narrative anchor to replace the protagonist anchor.

When proposing anything, say which bucket it's in. Avoid drift into "redesign the whole thing."

## 4. Scope to a real project, not a research lab-year

This is a Stanford course/research project with finite time and compute. Every avenue gets tagged by effort and risk.

- Prefer contributions that yield a **clean ablation** ("+component → metric up") — these de-risk the deliverable.
- The motivating experiment is cheap and devastating: **run CutClaw as-is on raw POV/glasses footage and show it breaks** (protagonist gate misfires, PySceneDetect finds nothing real, `Q_vis` has no bad footage to reject against). Show the gap; don't argue it.
- Ambitious ideas (free audio/video decoupling, J/L-cuts) are scoped or shelved, not deleted — they live in `open-questions.md`.

## 5. Evaluation is a first-class deliverable, not an afterthought

The dimension the user actually cares about — "would a good human editor have made this?" — is the hardest to measure and the most likely to sink the project if hand-waved.

- AV-Harmony transfers from CutClaw (we keep the external music beat). Reuse it.
- The selection stage needs its own metric (highlight precision / rank-correlation, mindful of the Otani et al. critique that summarization F1 can be near-random).
- "Human-likeness" → a rigorous pairwise human study, with an MLLM-judge proxy for fast iteration. Design this early.

## 6. Workspace hygiene

- `NORTH_STAR.md` = the thesis, kept short and current. `research/` = verified dossiers, one topic per file. `plan/` = architecture + milestones. `open-questions.md` = unresolved decisions with the trade-offs.
- Memory (`~/.claude/.../memory/`) holds durable, non-obvious facts and user/process feedback — not things derivable from these docs.
- Update files in place; don't fork near-duplicates. Link between docs so the workspace reads as one connected thing.
