# Agent Instructions

This repository hosts **Oracle**, a local-first gaming and streaming copilot. Follow these guidelines when modifying files in this repo:

- Prioritize stability and clarity over experimental features.
- Keep the architecture split between the **Thought Engine** (LLM + decision logic) and the **Functional Core** (Discord, OBS, overlay, config).
- Default LLM usage must remain local-only; cloud backends are opt-in.
- Never hardcode secrets (Discord tokens, OBS passwords, etc.). Use configuration files or environment variables.
- Maintain developer-facing docs (README, TASKS) so setup steps stay clear for new contributors.

This AGENTS file applies to the entire repository unless a more specific AGENTS.md exists deeper in the tree.
