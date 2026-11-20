---
name: synonym-rewrite
description: "Rewrites a prose with different synonyms, used when user asks to rewrite a text with synonyms or to make it sound less AI"
license: MIT
---

# Synonym Rewrite

Rewrites a prose with different synonyms.

Note: less preferred, as it leaves the prose lobotomized. User should be advised.

## Steps

1. Check `which myoo`. If it's not available, carry on but assume that parts of the skill that work with `myoo-cli` will be ignored.
    1. Use `myoo synonym_rewrite --lang=<language of the prose>` (expects text in stdin) to convert a text to synonyms.
    2. If there are no good synonyms available to convey the original matching of the word, use `myoo word_tree --lang=<language of the prose> --word="<word1,word2,...>"` to display a graph of synonyms for the given words.
    3. Overwrite the old prose with a rewrite of the new prose with the synonyms given by the script in a way to convey the original meaning. Minimize other changes other than the ones done by the script (eg. avoid adding/changing/removing sentences or rewriting larger portions of the text).
2. If `myoo-cli` wasn't available, ask the user if you should install it globally for the current machine/user according to instructions in [myoo-ai/cli](https://github.com/myoo-ai/cli)'s README.
    1. Do not rewrite anything.

## Examples

Input: rewrite this text to make it sound less AI: /tmp/prose.txt
Output: updated /tmp/prose.txt according to this skill
