# AGENTS.md

## Harness Invariants

- Do not rely on chat history. Re-read `RUN_ROOT` state.
- Use the Codex App bridge flow only.
- Do not run deprecated local runner flows.
- Use `gpt-5.6-sol` for App subagents unless the operator explicitly selects
  another GPT-5.6 tier.
- Use exactly one subagent per phase in this branch.
- Do not advance unless validation passed for the same phase and batch.
- Treat `_work/` and `run.local.json` as private.
- Do not publish absolute paths, raw logs, raw prompts, account paths, or token
  telemetry.
- Keep every output path inside `RUN_ROOT`.
- If a plan is malformed, stop and report the schema error.
