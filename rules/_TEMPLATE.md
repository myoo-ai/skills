---
# there is no widely accepted standard for AI harness rules at the moment

# 1. Always on:
# alwaysApply: true
# applyTo: "**"
#
# 2. Agent decides from the description (fyi Claude Code has no equivalent and loads it always):
# description: "Conventions for X. Read before doing Y."
# alwaysApply: false
#
# 3. Scoped to certain filepaths (`globs` == `paths` == `applyTo`, just in different harnesses so we need to duplicate it :/)
# description: "Conventions for X files."
# globs: "src/**/*.ts"
# paths: ["src/**/*.ts"]
# applyTo: "src/**/*.ts"
# alwaysApply: false
---

# Rule title

- One imperative rule per bullet. Add the reason when it isn't obvious
- Name actions, not harness tools, e.g. "run the tests", not "use the Bash tool"
