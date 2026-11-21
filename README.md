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

This repository's skills follows a modified version of [agentskills' evaluating skills guide](https://agentskills.io/skill-creation/evaluating-skills). The evaluation tests can be found in `<skill dir>/evals/evals.json` for each skill.

The process is as follows:

1. Every skill has recorded sample output of what the result should look like after using the skill.
2. When evaluating a skill, we run the agent harness 2 times:
    - with the skills that need to be tested
    - without any skills (to test if the skill is needed at all or if without the skills the agent achieves acceptable outcomes)
3. An independent ["skill grader"](./.agents/skills/skill-grader) model reviews the outputs and reports the deltas between the real and expected versions, in a single comprehensive report.

## Releasing myoo-ai/skills

Installed plugins only update when the version in `plugin.json` and `.claude-plugin/marketplace.json` goes up, regardless of whether `main` upgraded. Ask the agent to [release](./.agents/skills/release).
