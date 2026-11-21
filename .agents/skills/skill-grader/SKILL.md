---
name: skill-grader
description: "Used when evaluating/grading skills, or as regression test for skills."
license: MIT
---

# Skill grader

Use this skill when evaluating or grading skills, or as regession test for skills.

## Steps

1. Check if the skill definition has an `evals/` folder. If yes, the `evals.json` file should contain test cases.
2. Launch subagents with clean context in a way that you can monitor the following metrics: total output tokens, total time taken to perform the task. The dispatched subagents are:
    - One with the skill loaded
    - One with no skills
3. After testing is done, compare outputs of the expected and the 2 real ouputs.
4. Share a comprehensive in-chat summary with the user on how the skills performed. In general, this should contain the following information:
    - Overview (1-3 sentences about whether the skill performs better or worse)
    - Metrics (total output tokens and time taken between the 2 skills in a table)
    - Suggestions for improvement (what would objectively improve the skill, from both metrics perspective and the quality of the outputs)
    - Diff (if applicable, see below)
5. If requested by the user, diff the current output against expected. For PDFs, run `scripts/pdf-diff/main.py <old PDF path> <new PDF path> -o /tmp/<old name>-<new name>.diff.pdf` and present it to user. For plaintext, you can use git style diffs.

## Examples

Input: grade skill "myskill"
Output: a comprehensive evaluation report of skill `myskill`

## References

- `scripts/pdf-diff/main.py <old PDF path> <new PDF path> -o <output diff PDF path>`: computed a diff between two PDF files and outputs the results as a new PDF file with side by side git-like comparison
