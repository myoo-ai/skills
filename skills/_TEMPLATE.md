---
# https://agentskills.io/specification

# equals the directory name, a-z, 0-9, single hyphens, max 64 chars.
name: skills
# one-line description, double-quoted, max 1024 chars
description: "Does X to Y. Use when the user asks to ..., mentions ..., or works with ...."
license: MIT
# env requirements, max 500 chars
# compatibility: "Requires git and jq"
# allowed-tools: Bash(git:*) Bash(jq:*) Read
---

# Skill Title

One or two sentences on the outcome this skill produces.

## Steps

1. Imperative, concrete step. Name the action, not a harness tool: "search the repo", not "use Grep tool".
2. Next step.

## Examples

Input: what the user asks.
Output: what the agent produces.

## Edge cases

- Situation: what to do instead.

## Resources

All paths are relative to this skill's directory. Keep references one level deep and keep this file under 500 lines.

- [references/REFERENCE.md](references/REFERENCE.md): read when ...
- `scripts/example.sh`: run to ...
