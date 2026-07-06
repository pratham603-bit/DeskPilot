# DeskPilot Threat Model (STRIDE)

This lightweight threat model analyzes the security posture of the DeskPilot agent using the STRIDE methodology.

## Spoofing (Impersonating a user or component)
**Threat**: A malicious local user or process injects fake context pretending to be a valid user preference.
**Mitigation**: The `preferences.json` and `tasks.db` files are stored locally in the `data/` directory with restricted file system permissions. There is no external authentication layer because DeskPilot is designed as a single-user local tool, but it assumes the host OS is securing access to the `DeskPilot` folder.

## Tampering (Modifying data or code)
**Threat**: A malicious prompt injection could try to tell Gemini to delete all tasks, modify the agent's code, or corrupt the database.
**Mitigation**: The system prompt explicitly instructs Gemini to "NEVER fabricate task or schedule data". Furthermore, the tools provided to the LLM (like `add_task`, `complete_task`) only allow append-only or specific status updates. There is no `delete_all_tasks` tool exposed to the agent.

## Repudiation (Denying an action occurred)
**Threat**: The agent performs an action (e.g., adding a random task) and the user cannot verify why it happened.
**Mitigation**: All tool executions are strictly appended to `data/audit.log` with the timestamp, tool name, arguments, and result. This ensures complete traceability of all agent actions.

## Information Disclosure (Exposing sensitive data)
**Threat**: Tasks, schedule events, or documents passed to `summarize_document` are leaked to unauthorized parties.
**Mitigation**: Local data (`tasks.db`, `preferences.json`) never leaves the machine. The only external API called is the Gemini API. We rely on Google's API privacy guarantees (API data is not used for model training for paid/enterprise tiers, though users should be cautious with highly sensitive data on free tiers).

## Denial of Service (Impacting availability)
**Threat**: A complex prompt causes the agent to get stuck in an infinite tool-calling loop, consuming all local CPU or API quota.
**Mitigation**: The tool-calling loop relies on the standard `google-generativeai` package loop handling. In future iterations, a hard limit on the number of consecutive tool calls per turn should be enforced.

## Elevation of Privilege (Gaining unauthorized capabilities)
**Threat**: The agent uses prompt injection to execute arbitrary shell commands.
**Mitigation**: DeskPilot operates in a restricted environment. It is only provided with specific, narrowly-scoped tools (SQLite operations and summarization). It does not have access to a generic `run_shell_command` tool.
