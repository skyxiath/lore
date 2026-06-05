# Lore — North Star

> The thesis, in one place, kept current. Grounded in verified research (see [research/](research/)). Last updated 2026-06-05.

## The one sentence

**Lore takes genuinely raw lifestyle-camera footage — POV/action-cam, smart glasses, and interval capture — plus a music track and a text instruction, and produces a short, music-synced, narratively coherent edit, by adding the one stage every prior system skips: a joint audio+visual *worthiness gate* that decides what is even worth keeping in 90%-dead-time footage.**

## Why now, and why this is not already solved

Automatic music-synced editing just had its strongest result — **CutClaw** ([arXiv:2603.29664](https://arxiv.org/abs/2603.29664)) — and it works well. But it is benchmarked on **5 feature-length films + 5 long-duration vlogs**: *already-edited, professionally-shot footage*. That single fact is Lore's whole reason to exist (full teardown: [research/cutclaw.md](research/cutclaw.md)):

- Running PySceneDetect on a finished film **recovers the human editor's cuts** — the hardest part of raw capture (finding where meaningful units begin and end in one continuous take) is handed to it for free.
- Every shot is pre-selected by pros, so CutClaw has **no upstream worthiness-selection gate** — its `Q_vis` term never has to reject dead time, because there is none. (It does post-hoc perceptual QA, but never "is this hour worth keeping.")
- Its narrative spine is an **on-screen protagonist** (identity injection "a man"→"Joker", Protagonist Presence Ratio, Semantic Identity Verification) — and in POV/glasses footage the subject is *behind the camera*. Three load-bearing components have nothing to grip.

Lore's regime is the inverse: one continuous take or auto-triggered interval clips, no editorial cuts, ~90% dead time, no on-screen protagonist, often no clean dialogue. **CutClaw's headline capability — "hours-long *raw* footage editing" — is structurally untested in exactly the regime that name implies.** The clean motivating experiment is to run CutClaw as-is on raw POV/glasses footage and show it break: PySceneDetect finds no real units, the protagonist gate misfires, `Q_vis` has no garbage to reject against. We *show* the gap rather than argue it.

## What Lore keeps, guts, and adds

| | Decision | Why |
|---|---|---|
| **KEEP** | Music-as-skeleton; keypoint/beat+downbeat grid; `Q_sync`; AV-Harmony; the Playwriter→Editor→Reviewer agent structure | This is CutClaw's *validated core* — removing audio is its single biggest ablation hit (AV-Harmony 86.5→77.2). Beat tracking is essentially solved ([allin1](https://github.com/mir-aidj/all-in-one), [Beat This!](https://github.com/CPJKU/beat_this)); we adopt, not rebuild. |
| **GUT** | Protagonist machinery: Identity Injection, Protagonist Presence Ratio, Semantic Identity Verification | The wearer is behind the camera. Nothing to track. Replace with an **activity / place / attention** anchor. |
| **REPLACE** | PySceneDetect shot boundaries | Raw footage has no editorial cuts. Replace with **event/activity segmentation**: IMU/gaze/optical-flow/SLAM change-points → a video-LLM semantic pass. For interval footage the 9-min gaps are *free* segment boundaries. |
| **ADD (the contribution)** | A joint **audio+visual worthiness gate** upstream of the Playwriter, including a **dialogue-content** channel | The missing stage. CutClaw never needed it; commercial tools do it shallowly. This is where "what a good human editor keeps" lives. |
| **PROMOTE** | Footage's own (diegetic) audio + capture **metadata** (timestamps/GPS/IMU) from throwaway to first-class selection + planning signals | The impact, the cheer, the laughter, the wind-drop, and *where/when/what-activity* are exactly what mark a keepable moment. |

## What Lore is NOT (the reviewer rebuttals, pre-answered)

- **"Isn't this just Apple Memories / Google Photos / GoPro Quik?"** Those optimize *pleasantness* over mostly-shootable input, select via shallow heuristics (aesthetics, faces, sensor metadata), don't follow a free-text instruction, don't reason about dialogue, and don't handle a 90%-dead-time interval regime. GoPro Quik proves *sensor metadata can drive selection* — but it's sensor-only with zero semantics and no story planner. (See [research/music-edit-landscape.md](research/music-edit-landscape.md).)
- **"Isn't this just CutClaw?"** We keep its sync spine and gut the half that assumes a pre-edited film with an on-screen protagonist. Different input regime, different (added) front end.
- **The honest one — "Hasn't someone done instruction + dialogue + beat-sync already?"** Closest prior art is the **Prompt-Driven Agentic Video Editing System** ([arXiv:2509.16811](https://arxiv.org/abs/2509.16811), 2025): instruction-conditioned selection from multi-hour footage + narrative-relevant *speech* scoring + a Librosa beat-alignment agent that even aborts beat-sync to protect important narration. **This means Lore's claim is NOT "first to score dialogue for editing."** Lore's defensible contribution is the *distinctive combination + regime*: (a) the truly-raw, 90%-dead-time **POV/glasses/interval** regime nobody evaluates in; (b) **capture-metadata × semantics fusion** (IMU/GPS/gaze as a worthiness + narrative prior); (c) **downbeat/structure-aware** timing; (d) a **protagonist-free activity/place/attention** narrative anchor; (e) the **joint acoustic-recurrence + dialogue-content** worthiness gate as one unit. We cite 2509.16811 as the nearest neighbor and differentiate on regime and signal fusion, not on a "first ever" claim.

## The contributions, stated honestly

> **Primary claim = composition** (decided 2026-06-05, [open-questions.md](open-questions.md) Q1). #1 is the headline; #2 is the enabling front end, built good-enough rather than over-invested.

1. **A protagonist-free narrative spine for raw footage** *(headline)* — the Playwriter re-anchored on activity/place/time/attention, with capture metadata as the arc backbone and 9-minute interval gaps treated as deliberate ellipses absorbed by the music structure. Metadata-as-narrative-arc (not just clustering/indexing) appears to be an open gap. **This — not "we also compose" — is what separates Lore from CutClaw and [2509.16811](https://arxiv.org/abs/2509.16811). Lead with the anchor.**
2. **A worthiness gate for dead-time-dominated raw footage** *(enabling front end)* — query-free, audio-aware (acoustic *and* dialogue-content), metadata-grounded. No existing benchmark scores edit-worthiness on this regime; the closest query-free audio-visual highlight detector ([Islam et al., WACV 2025](https://arxiv.org/abs/2407.13933)) uses audio only as generic *acoustic recurrence* — and notably its audio-only stream **beats** visual-only, which directly motivates fusing audio in. Without it the composer gets garbage; with it, composition becomes possible.
3. **An evaluation suite for this regime** — keeping AV-Harmony/beat-F1, *discarding* TVSum/SumMe F1 (provably near-random per [Otani et al. CVPR 2019](https://arxiv.org/abs/1903.11328); use Kendall's τ/Spearman vs a random baseline), and a Bradley-Terry pairwise human study for **Human-Likeness** backstopped by an MLLM-judge proxy ([VideoScore](https://arxiv.org/abs/2406.15252), ~0.77 Spearman w/ humans).
4. *(Stretch / possible separate artifact)* **A dataset** pairing raw lifestyle footage with human-editor ground-truth edits — none is public, and it gates honest evaluation.

## Flagship demo

**The interval "day recap."** A day or trip captured 1-min-every-10-min, compressed to a ~45s music-synced film. It exercises everything (metadata-driven arc, music sync, worthiness selection), sidesteps CutClaw's hardest deconstruction problem (the gaps pre-segment the footage), and is a thing people genuinely want that nothing automates well. Build toward this as the headline result.

## The biggest risks (don't hand-wave these)

1. **Defining the protagonist-free anchor concretely.** "Protagonist presence" is crisp; "activity/place/attention coherence" is fuzzy. If we don't pin it down, the Playwriter has nothing firm to plan against. **Conceptual crux — nail early.**
2. **Evaluation / ground truth.** No public raw-footage→human-edit dataset exists, and even human agreement on "importance" is low (τ≈0.18). The eval design is itself a deliverable and the most likely thing to sink the project if hand-waved.
3. **Novelty positioning vs [arXiv:2509.16811](https://arxiv.org/abs/2509.16811).** Must be cited and cleanly differentiated on regime + fusion, not ignored.
4. **Data sourcing.** 24h of genuinely-raw POV/glasses/interval footage with usable content is painful to get. Ego4D / Aria Everyday Activities / Nymeria are the realistic starting pools.

## Read next

- [plan/architecture.md](plan/architecture.md) — the redesigned pipeline, component by component, with concrete models/tools.
- [plan/project-plan.md](plan/project-plan.md) — milestones, build order, the "break CutClaw" experiment, the eval plan.
- [open-questions.md](open-questions.md) — unresolved forks with trade-offs.
- [research/](research/) — six verified dossiers backing every claim above.
