---
name: update-best-practices
description: "Updates skills with best practices for something in ./skills/skills."
license: MIT
---

# Update best practices

Skill that updates skills with best practices in a process, programming language, framework, library, module...

## Steps

1. Check if the matching best practices skill exists already in (./skills/skills/...).
2. For the given user project (programming language, framework...), find the latest version (unless user specifies a specific version).
3. Browse the internet for best practices for the query. Avoid user-made blogs, prioritize official documentations and specifications.
4. Save results as skill files in this repository (./skills/skills/...). If the skill exists, update it, if it doesn't, create it (format: `<project>-best-practices/`).

## Examples

Input: "create skill with best practices for the latest Python version"
Output: a skill file in ./skills/skills/python-best-practices/SKILL.md with comprehensive list of best practices, for instance:

```md
---
name: python-best-practices
description: "Use when working with Python code."
license: MIT
---

# Python 3.15 best practices

- prioritize `match` statement over conditionals when applicable (https://docs.python.org/3/tutorial/controlflow.html#tut-match):

\```python
case 401 | 403 | 404:
    return "Not allowed"
\```

- use f-strings to format strings (https://docs.python.org/3/reference/lexical_analysis.html#f-strings):
- [more...]
```

## Edge cases

If you are in doubt or encountered some blocker, ask the user question(s) on how to proceed.

## Resources

- the Internet (official documentations and specifications are preferred over something like user posts or blogs)
