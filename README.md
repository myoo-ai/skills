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

There is also a skill for omp to update the harness settings and to recomend (AKA settings and skills that noone bothers to check/change but are actually quite good), after installing invoke it with:

```prompt
Use /skill:myoo-improve-omp to suggest how to edit my harness' settings.
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
