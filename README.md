<!-- markdownlint-disable no-inline-html -->
# myoo-skills

<h1 align="center"><samp>
μ&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
&nbsp;\&nbsp;&nbsp;&nbsp;&nbsp;<br>
&nbsp;&nbsp;🐄💨
</samp></h1>

Main repository for [μ-skills](https://github.com/myoo-ai/skills).

See <https://github.com/myoo-ai> for the whats and whys.

## Quickstart

### Generic

Just ask the AI agent in your harness to install these skills for you:

```prompt
Can you install these skills globally for the current AI harness that I am using?
https://github.com/myoo-ai/skills

If the current harness supports it, make it auto-update.
```

### omp

```bash
omp plugin marketplace add myoo-ai/skills
omp plugin install myoo-skills@myoo-skills
```

updating:

```bash
omp plugin marketplace update myoo-skills
omp plugin upgrade myoo-skills@myoo-skills
```

auto-updating:

```bash
omp config set marketplace.autoUpdate auto
```

There is also a skill for omp to update the harness settings and to recomend (AKA settings and skills that noone bothers to check/change but are actually quite good), after installing invoke it with:

```prompt
Use the improve-harness skill to give recommendations how should the settings of the current harness be improved.
```

### claude code

```bash
claude plugin marketplace add myoo-ai/skills
claude plugin install myoo-skills@myoo-skills
```

updating:

```bash
claude plugin marketplace update myoo-skills
claude plugin update myoo-skills@myoo-skills
```

### codex

```bash
codex plugin marketplace add myoo-ai/skills
codex plugin add myoo-skills@myoo-skills
```

updating:

```bash
# also reinstalls installed plugins from the marketplace
codex plugin marketplace upgrade myoo-skills
```

### github copilot cli

```bash
copilot plugin marketplace add myoo-ai/skills
copilot plugin install myoo-skills@myoo-skills
```

updating:

```bash
copilot plugin marketplace update myoo-skills
copilot plugin update myoo-skills
```

### cursor, gemini cli, opencode, and others

Skills only, via the [skills CLI](https://skills.sh):

```bash
npx skills add myoo-ai/skills
```

updating:

```bash
npx skills update
```

## Evaluating agent outputs

The evals of this repository's skills run with [myoo-eval](https://github.com/myoo-ai/eval). The suite lives in [`evals/`](./evals): `evals/eval.yml` holds the settings, `evals/<skill>/<case>/case.yml` the task cases and `evals/triggers/` the cases that check which skill a request loads. Hidden tests and expected files for the graders sit in the case's `eval/` directory, which the agent never sees.

The process is as follows:

1. Every task case gives the agent a request and a workspace, and graders check the result: files, commands, `myoo prose_lint` and toolchain runs, and a judge model where no command can decide. A run that fails its graders gets up to 3 tries in the same session.
2. Every case runs in Claude Code and omp on Sonnet 5.5, inside a sandbox, in 2 arms:
   - with the plugin installed
   - without any skills (to test if the skill is needed at all or if without the skills the agent achieves acceptable outcomes)
3. The report compares the arms per harness, gives a verdict on whether the skills improve the outcome, and lists what each arm cost.

```bash
myoo-eval check evals                              # validate the cases without running an agent
myoo-eval run evals --case 'go-best-practices/*'   # run some cases
myoo-eval show latest                              # transcripts and grades of the last run
```

Ask the agent to [grade a skill](./.agents/skills/skill-grader) for a summary of the latest results with suggestions.

## Releasing myoo-ai/skills

Installed plugins only update when the version in `plugin.json` and `.claude-plugin/marketplace.json` goes up, regardless of whether `main` upgraded. Ask the agent to [release](./.agents/skills/release).
