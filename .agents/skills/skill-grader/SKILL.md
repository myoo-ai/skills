---
name: skill-grader
description: "Used when evaluating/grading skills, writing or fixing their evals, or as regression test for skills."
license: MIT
---

# Skill grader

Grades this repository's skills with `myoo-eval` (github.com/myoo-ai/eval), and writes or fixes their evals. The suite lives in `evals/`: `evals/eval.yml` holds the settings, `evals/<skill>/<case>/` the task cases and `evals/triggers/` the trigger cases. [references/writing-evals.md](references/writing-evals.md) describes the case format, the graders and how to check a case. Read it before you add or change a case.

## Grading a skill

1. Run `myoo-eval check evals` and fix every error. Its warnings name skills with fewer than 5 task cases (a verdict per skill needs 5), skills without a trigger case and cases skipped on this machine because a command they require is missing. If the graded skill has a coverage warning, write the missing cases first (see below) or tell the user that the report will give no verdict for it.
2. Run the skill's cases and the trigger cases: `myoo-eval run evals --case '<skill>/*,triggers/*'`. Each case runs in every installed harness on Sonnet 5.5, with the plugin installed and without any skills, 3 times each, and a run that fails its graders gets the retry prompt, up to 3 tries. Add `--harness omp` or `--runs 1` only when the user asks for a quick check. Add `-v` to watch what each agent does. To grade an edit to the skill against the committed version, use `--arm with,ref:HEAD`. `--judge <harness>` picks the harness for the judge graders.
3. Read the report it prints (also in `evals/results/latest/report.md`). Then read the transcripts of the failed runs with `myoo-eval show latest --failed`, because a grader can pass or fail for the wrong reason.
4. Share an in-chat summary with the user on how the skill performed:
   - Overview: the verdict per harness (helps, hurts, equivalent or inconclusive) in 1-3 sentences
   - Metrics from the report's tables: pass rate on the first try and after the last, tries, tokens in and out, cost and time with and without the skill
   - Triggers: whether the skill loaded when it should, and false loads on near-miss cases
   - Suggestions for improvement: what would objectively improve the skill, from the failed graders and the transcripts. Name the cases whose graders never vary, as they cannot tell the arms apart.
   - Diff (if applicable, see below)
5. To compare 2 runs, such as before and after an edit to the skill, use `myoo-eval report <new results dir> --compare <old results dir>`.

## Writing and fixing evals

1. Read the skill and its rules file (`rules/<skill>.md`, when there is one), then its existing cases, so a new case covers a rule or a scenario they do not.
2. Write the case as [references/writing-evals.md](references/writing-evals.md) describes. The prompt reads the way a user asks, without the rules the skill teaches. Hidden tests and fixtures go in the case's `eval/` directory, and the graders check what the skill teaches and what the user asked for.
3. Run `myoo-eval verify <skill>/<case>`. It runs the graders that need no agent on the untouched workspace, and at least one outcome grader must fail there.
4. Write a good solution in a scratch directory outside the repository, then run `myoo-eval verify <skill>/<case> <dir>`. Every grader must pass. Fix the grader when a good solution fails it, and delete the scratch directory afterwards.
5. Run `myoo-eval check evals` again, then one real run of the new case (`myoo-eval run evals --case '<skill>/<case>' --runs 1 -v`) and read `myoo-eval show latest` to see that the graders that need an agent work too.

When a grader in an existing case turns out wrong, fix it the same way and re-grade the stored runs with `myoo-eval grade latest`, which costs no agent runs. For cases with more than 1 try, `grade` warns about runs that stopped on a pass that the new graders turn into a fail. Run those cases again.

## Diffing outputs

Each run keeps the workspace it started from and the one it left in `evals/results/<timestamp>/runs/<skill>/<case>/<harness>/<arm>/<n>/`, as `original/` and `modified/`, with the changes between them in `diff.patch` next to them. `latest` points at the newest results directory.

- What the agent changed: read `diff.patch`.
- Output against the expected one, for cases with an `expected.md`: `git diff --no-index evals/<skill>/<case>/expected.md evals/results/latest/runs/<skill>/<case>/<harness>/<arm>/<n>/modified/<file>`
- The same file in 2 arms: `git diff --no-index <run dir of arm none>/modified/<file> <run dir of arm with>/modified/<file>`
- PDFs: `scripts/pdf-diff/main.py <old PDF path> <new PDF path> -o /tmp/<old name>-<new name>.diff.pdf`, and present the result to the user.

## Examples

Input: grade skill "myskill"
Output: a report on how skill `myskill` performed, with suggestions for improving it

Input: add evals for skill "myskill"
Output: new cases in `evals/myskill/`, each checked with `myoo-eval verify` on the untouched workspace and on a good solution

## References

- [references/writing-evals.md](references/writing-evals.md) describes the case format and how to check a case
- `scripts/pdf-diff/main.py <old PDF path> <new PDF path> -o <output diff PDF path>`: computes a diff between 2 PDF files and outputs the results as a new PDF file with side by side git-like comparison
