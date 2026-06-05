"""The activity/place/attention narrative anchor — R1, the conceptual crux.

CutClaw anchors narrative on a tracked on-screen protagonist (Identity Injection,
Protagonist Presence Ratio R_prot, Semantic Identity Verification). The wearer is
behind the camera, so Lore replaces ALL of it with:

  • Playwriter (Screenwriter_scene_short.Screenwriter): plan the arc over a
    place -> activity -> time progression built from event attributes + capture
    metadata; for 'interval', justify each ~9-min gap as an ellipsis by a
    place/activity change and let the music structure absorb it.
  • Editor (core.fine_grained_shot_trimming): replace the R_prot term with
    S_activity (activity/attention salience: gaze fixation, head stabilization,
    subject-of-action). Optionally add S_motion-on-beat (land a visual motion
    peak on a musical beat — the action-footage cut feel).
  • Reviewer (Reviewer.Review_timeline): replace Semantic Identity Verification
    with an activity/place coherence + attention check; KEEP temporal/structural
    integrity + perceptual quality.

GUARDRAIL (open-questions.md Q1): the contribution is the ANCHOR, not "we also
compose". Spec the anchor precisely here BEFORE coding M4 — "activity coherence",
"legal place transition", and the attention score must be concrete.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ActivityPlaceAnchor:
    """The narrative spine that replaces the protagonist. To be pinned down in M4.

    These fields are the spec stubs for R1 — fill with concrete definitions:
    """
    activity_sequence: list[str]          # the planned activity progression
    place_transitions: list[tuple[str, str]]  # (from_place, to_place) deemed legal
    # attention_fn(event) -> [0,1]: gaze fixation / head stabilization / motion
    # coherence_fn(a, b) -> [0,1]: activity+place continuity between adjacent shots


def patch_for_pov_regime(cutclaw_config_overrides: dict) -> dict:
    """Return prompt/scoring patch directives for the re-anchored spine.

    Most GUT decisions are already config toggles (see LoreConfig.cutclaw_overrides:
    MAIN_CHARACTER_NAME='', ENABLE_FACE_QUALITY_CHECK=False,
    ENABLE_TRIM_SHOT_CHARACTER_ANALYSIS=False). What remains is prompt-level:
    re-anchor src/prompt.py's Screenwriter/Editor/Reviewer prompts on
    activity/place/time. Implemented in M4.
    """
    raise NotImplementedError("Compose re-anchor lands in M4; see plan/project-plan.md")
