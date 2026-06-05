"""Dialogue-content channel — score the narrative importance of WHAT WAS SAID.

The differentiated signal: existing highlight detectors hear *sound* (PANNs =
AudioSet sound-event tagging), not *words*. Lore scores spoken content for story
importance, conditioned on the instruction.

NEAREST PRIOR WORK — must cite, do NOT claim "first": the Prompt-Driven Agentic
Video Editing System (arXiv 2509.16811, 2025) already does instruction-conditioned
selection + dialogue/speech-act scoring + beat-alignment that aborts to protect
narration. Lore differentiates on regime (raw POV/glasses/interval) + metadata x
semantics fusion, NOT on being first. (related-work-prompt-driven-agentic-editing)

Note also: CutClaw's Screenwriter already has 'hook dialogue' selection
(Screenwriter_scene_short.select_hook_dialogue) — reuse/learn from it.
"""
from __future__ import annotations


def score_dialogue_importance(
    transcript_segments: list[dict],
    instruction: str = "",
    *,
    llm=None,
) -> dict[int, float]:
    """Map transcript-segment index -> narrative-importance score in [0,1].

    `transcript_segments`: WhisperX output (word/segment timestamps + text [+ speaker]).
    Open risk (open-questions.md Q8): does this survive noisy, unscripted lifestyle
    ASR (wind, crosstalk, disfluencies) vs. the clean meeting/screenplay text the
    importance-scoring literature assumes? Validate on real WhisperX output. M2.
    """
    raise NotImplementedError("Dialogue importance lands in M2; see plan/project-plan.md")
