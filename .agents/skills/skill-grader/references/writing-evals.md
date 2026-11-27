# Writing evals

The evals run with `myoo-eval` (github.com/myoo-ai/eval). This file holds what you need to add or change cases without the tool's own docs.

## Layout

```plain
evals/eval.yml                    # suite settings, shared by every case
evals/<skill>/<case>/case.yml     # one task case
evals/<skill>/<case>/prompt.md    # optional, the prompt when it is long
evals/<skill>/<case>/workspace/   # copied in as the agent's working directory
evals/<skill>/<case>/eval/        # hidden from the agent, read by run graders as ../eval
evals/<skill>/<case>/expected.md  # optional, a good answer for humans, never read by graders
evals/triggers/<case>/case.yml    # one trigger case
evals/results/                    # run results, gitignored
```

Never put eval files inside `skills/`: the agent must not find the expected answers.

## A task case

```yaml
description: adds a bounded concurrent checksum function with tests
skills: [go-best-practices] # the skills this case is about
prompt: |
  Add a concurrent variant of Sum to filesum.go: ...
setup: go mod download # optional, runs in the sandbox before the agent
requires: [go] # commands the case needs, its runs are skipped where they are missing
tries: 3 # default 3, a failed try gets the retry prompt in the same session
timeout: 10m # per try
max_tokens: 400000 # optional, tokens in and out per try
max_changed_lines: 200 # optional, added and removed lines of the final diff
graders:
  - name: hidden test passes
    run: cp ../eval/zz_grader_test.go . && go test -run TestGrader .
    timeout: 3m
  - name: uses WaitGroup.Go
    regex: '\.Go\(func'
    in: file:filesum.go
  - name: no WaitGroup.Add
    regex: '\.Add\(1\)'
    in: file:filesum.go
    not: true
  - name: skill loaded
    skill: go-best-practices
```

### The prompt

Write it the way a user asks, with what a user would know: the request, the files, the versions they run ("go.mod says go 1.27", "PHP 8.5"), the behaviour they need and their constraints. Leave the skill's rules out. A prompt that names the API or the steps the skill teaches makes both arms pass, and the case then measures the prompt, not the skill. Graders may check what the skill teaches, as long as it is what the user wants. They must not depend on a choice the prompt leaves open, such as a file name it never gives.

### Graders

Each grader sets one kind. `weight` (default 1), `dimension` (`outcome`, the default and the only one that decides the verdict, or `safety`, `process`, `trigger`) and `arms` are optional.

| Kind       | Passes when                                                                           |
| ---------- | ------------------------------------------------------------------------------------- |
| `regex`    | the pattern matches the target (`in`, default the final reply)                        |
| `contains` | the target contains the text                                                          |
| `file`     | the workspace file exists and matches `match`, or `exists: false`, or `changed: true` |
| `run`      | the shell command exits 0                                                             |
| `judge`    | a judge model's majority vote says the criterion holds                                |
| `skill`    | the agent loaded the skill (scored only in arms that install it)                      |
| `tool`     | tool calls with a matching name whose input matches `match`                           |
| `command`  | calls of a stubbed command whose arguments and stdin match `match`                    |
| `order`    | steps (`tool`, `command` or `skill`, each with an optional `match`) happen in order   |
| `changes`  | every changed workspace path matches one of the listed globs                          |

`regex`, `contains`, `tool` and `command` count matches. They need at least 1, `min` and `max` set other bounds and `not: true` means none. `exclude` drops matches that also match it.

Targets for `in`: `final`, `transcript`, `tools`, `commands`, `network`, `diff` (the unified diff from the original to the final workspace) and `file:<path>`. A judge without `in` reads the final reply plus the diff. A judge must quote the evidence for a pass. For a mistake the agent must not make, describe the mistake and set `not: true`.

### Run graders

Each run grader starts in a fresh sandbox without network, with its working directory in `modified/`:

| Path          | Holds                                            |
| ------------- | ------------------------------------------------ |
| `.`           | the final workspace                              |
| `../original` | the workspace as the agent got it, after `setup` |
| `../eval`     | a copy of the case's `eval/` directory           |

`ORIGINAL_DIR`, `MODIFIED_DIR` and `EVAL_DIR` hold the same paths. Put hidden tests and fixtures in `eval/` as files, not as heredocs in `case.yml`, and copy them in where the toolchain needs them (`cp ../eval/test_hidden.py tests/`). Compare against `../original` instead of hardcoding a number measured on the input, for example a word count within 25 % of the original's:

```sh
n=$(wc -w < prose.md); o=$(wc -w < ../original/prose.md); test $((n * 4)) -ge $((o * 3)) && test $((n * 4)) -le $((o * 5))
```

The sandbox PATH holds the system directories and the `sandbox.path` entries of `eval.yml`. A toolchain installed elsewhere goes there, and a case that needs it lists it under `requires`.

## A trigger case

```yaml
kind: trigger
expect: [ticket, prose] # one skill, a list that must all load, or none
acceptable: [support] # may also load without failing
query: implicit # free label, implicit, explicit or near_miss
prompt: Draft a reply to ticket 4711 in our house style.
```

Write positive cases the way a user would phrase the request without naming the skill. Write `expect: none` cases for requests that sound close but belong to no skill, and for each pair of skills that `myoo-eval check` lists as overlapping.

## Checking a new case

1. `myoo-eval check evals` must report no errors. Its coverage warnings name skills with fewer than 5 task cases (a verdict per skill needs 5) or no trigger case.
2. `myoo-eval verify <skill>/<case>` runs the graders that need no agent on the untouched workspace. Every outcome grader that checks the result must fail there, or the case passes when the agent does nothing. A grader that errs instead of grading, such as one with an invalid pattern, fails verification. A case whose `requires` commands are missing here cannot be verified on this machine.
3. Write a good solution in a scratch directory (a full copy of the workspace with your changes) and run `myoo-eval verify <skill>/<case> <dir>`. Every grader must pass. A grader that fails a good solution is wrong.
4. Add `--judge <harness>` to `verify` to also run the judge graders, which costs model requests.
5. Run the case once for real when it is new: `myoo-eval run evals --case '<skill>/<case>' --runs 1`, then read `myoo-eval show latest` to see that the graders pass and fail for the right reasons.
