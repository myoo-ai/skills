---
name: ui-design
description: "Use everytime the task requires designing an user interface or a webpage."
license: MIT
---
<!-- markdownlint-disable code-block-style -->

# UI Design

This is the main skill for UI design. Use it everytime you are designing a web page or user interface.

## Steps

1. Read the rules and best practices of this skill
2. Design the user interface with accordance to this skill

### Rules

- no bullet points or emdashes or semicolons as separators between text or text-like elements
- do not overexplain what's obvious in the UI, instead assume that the user is familiar with the concepts already and intuitively knows what a certain element does
  - for problem/domain-specific functionality, prefer adding a tooltip or a "hint" element that display a tooltip, further explaining what an element in the UI does
  - in general, the UI should use icons to signalize the functionality to the user, instead of text
  - examples:
    - bad: "Click any symbol to copy it", and then also showing the copy sheets icon
    - good: when hovering an element, show a "Click to copy" tooltip, or just use a copy button with 2 paper sheets as icon
- use monospace text sparingly, mostly only in places that signify computer code or otherwise mechanic/copyable instructions
- do NOT use UTF-8 emojis or symbols for icons. Instead, prefer SVG or PNGs. check if your harness has a tool to generate images, if yes use it to generate the icons. alternatively, find some free-to-use/good-license icons on the Internet or create some icons with the tools available to you
- do not use borders or outlines that are stacked and nested multiple levels deep
  - examples:
    - bad: a section on the page that has a border, with table inside that is bordered, with bordered section element inside it which has a codeblock that is styled with an outline
    - good: try to minimize the borders somehow by using a different layout or styles. if you are unsure, suggest some options to the user after implementing the features in the first pass/turn and try to get feedback from them
- no left-padded/zero-padded numbers that signalize chronology/ordering of items or sections. The chronology should either be intuitive, or you should use a different style (eg. no zero-padded numbers, just numbers)
- symbol or emoji + solid background != avatar or logo. Generate a better image or make it clear that the avatar/logo is a placeholder. If they're supposed to be randomized user avatars, you can style them better, eg. use different font, add some pattern in the background, etc.
- no thin borders that are barely visible. either there is a border or there isn't, having a border or outline that's barely visible doesn't do anything
- watch the paddings/margins! There are many cases where the elements have inconsistent spacing between them, which makes the sections not separated correctly or gives the design a bad look. If you are unsure and the tools are available to you, screenshot the result with sufficient resolution (as in, one where you can make up the elements but not spend a lot of tokens), so that you may tweak the paddings/margins appropriately.
- also refer to `no-ai-patterns` skill for the prose in the UI (in short, ensure `myoo prose_lint` passes)

## Examples

Input: create a modern static website about greek letter μ
Output: an artifact with a modern static website about greek letter μ, following the rules and best practices in this skill
