"""The worthiness gate (pipeline stage 3) — Lore's enabling contribution.

Decides what is worth keeping in 90%-dead-time footage, by fusing four signals:
acoustic salience, visual salience, dialogue-content importance, and a metadata
prior. Prunes the event set BEFORE the planner reads it. This is the stage CutClaw
never needed (films have no dead time). Ref: research/highlight-detection.md,
research/audio-highlight.md.
"""
from .gate import WorthinessScore, score_and_prune  # noqa: F401
from .dialogue import score_dialogue_importance      # noqa: F401
