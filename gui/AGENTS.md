# AGENTS.md

## Harness Invariants

- Do not rely on chat history. Re-read `RUN_ROOT` state.
- Use the ChatGPT desktop app bridge flow only.
- On Windows, use the native Windows agent and PowerShell. Do not require WSL,
  Bash, or `.sh` scripts.
- Use the Python executable available to the active agent (`python` on native
  Windows, normally `python3` on macOS/Linux).
- Do not run deprecated local runner flows.
- Use `gpt-5.6-sol` for App subagents unless the operator explicitly selects
  another GPT-5.6 tier.
- Use exactly one subagent per phase in this branch.
- Do not advance unless validation passed for the same phase and batch.
- Treat `_work/` and `run.local.json` as private.
- Do not publish absolute paths, raw logs, raw prompts, account paths, or token
  telemetry.
- Keep every output path inside `RUN_ROOT`.
- If a plan is malformed, repair the current phase output and rerun validation.
