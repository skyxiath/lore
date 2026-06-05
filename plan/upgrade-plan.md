# Upgrade Plan — prototype → final version

> Branch `final-version`. Goal: upgrade every prototype stand-in into the real architecture from [architecture.md](architecture.md), closing the gaps in [../notes/status-vs-plan.md](../notes/status-vs-plan.md). The prototype (main branch, commit `69ada12`) proved the end-to-end shape; this branch makes each part real.

## The mapping: what each part is now → what it becomes

| # | Part | Prototype now (main) | Final version (this branch) | Approach |
|---|---|---|---|---|
| 1 | **Composition spine** | minimal composer: chronological sort + center-trim + even beat grid | **CutClaw's real agent spine** (Playwriter→Editor→Reviewer), re-anchored, running on Modal | `modal_app.py`: build the image, route 3 LLM endpoints to OpenAI, feed it our selected clips; debug the first run |
| 2 | **Playwriter (narrative arc)** — *headline* | none (clips just sorted by time) | activity/place/time **arc** + **instruction-following** + gaps-as-ellipsis | re-anchor CutClaw's Screenwriter prompts on activity/place; OR an LLM planner over worthiness+metadata emitting an ordered, narrated shot plan |
| 3 | **Worthiness gate** | MLLM (gpt-4o-mini) vision + dialogue scorer | + real **audio-event features** (PANNs/BEATs/CLAP), + **metadata fusion** (IMU/GPS/motion), + optional learned/recurrence head | add an audio-feature extractor stage; fuse signals; ablate each (Kendall-τ) |
| 4 | **Event segmentation** | sidestepped (1 interval clip = 1 event) | real **change-point cascade** for continuous footage (IMU/gaze/optical-flow → video-LLM → aggregate) | needed for non-interval sources; build the cascade |
| 5 | **Music deconstruction** | librosa beats only | **downbeats + structure** (allin1/madmom) → cut density tracks the song (sparse verse, dense drop) | adopt allin1; structure-aware slot allocation |
| 6 | **Editor (trim)** | center-trim to slot length | pick the **salient sub-segment** (motion/attention) + **motion-on-beat** | optical-flow / VLM sub-clip scoring; align motion peaks to beats |
| 7 | **Reviewer** | none | coherence + quality gate with backtracking | CutClaw's Reviewer (re-anchored to activity/place) or a Lore check |
| 8 | **Metadata** | filename timestamps only | **GPMF / Aria** sensor ingestion (GPS, IMU, gaze) | parse telemetry → feed gate (#3) + arc (#2) |
| 9 | **Evaluation suite** | none | **Kendall-τ** worthiness vs labels, **AV-Harmony**, MLLM-judge + **pairwise human study** | build the harness; measure every upgrade above |

## Dependencies & suggested sequence

- **#9 (eval) is the measuring stick** — building even a light version first means every later upgrade gets a before/after number (the plan called eval first-class; it's at zero).
- **#1 (Modal CutClaw spine)** is the biggest single piece and what Modal was provisioned for; it also subsumes #2/#6/#7 if CutClaw's re-anchored agents are used instead of a Lore-native composer. **Key fork:** do we make the final composer *CutClaw's actual spine* (run on Modal) or an *upgraded Lore-native composer*? This decides whether #2/#6/#7 are "re-anchor CutClaw" or "build our own."
- **#3 (worthiness)** and **#8 (metadata)** pair together and improve selection regardless of which composer wins.
- **#5 (downbeats)** is a localized, high-visible-impact upgrade.
- **#4 (segmentation)** only matters once we target continuous (non-interval) footage.

## The fork to settle first
**Final composer = CutClaw's real spine (Modal) vs. upgraded Lore-native composer?**
- *CutClaw spine:* matches the original thesis ("keep CutClaw's spine"), gives the agentic Playwriter/Editor/Reviewer for free, but is an infra/debug lift (image build, model routing) and less controllable.
- *Lore-native:* full control, no Modal/heavy-deps, faster iteration, but we reimplement the agent intelligence (arc planning, smart trimming).
- *Hybrid:* keep Lore's front end (gate + metadata arc + selection), feed CutClaw's spine on Modal for the actual edit. Most faithful to the thesis.

Once settled, sequence falls out. Default proposal: **light eval harness (#9) → settle the composer fork → CutClaw-on-Modal (#1) → worthiness+metadata (#3,#8) → downbeats (#5) → segmentation (#4).**
