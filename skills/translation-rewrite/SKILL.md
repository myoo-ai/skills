---
name: translation-rewrite
description: "Translates a text to esperanto (or other user-specified language) and back as an attempt to get rid of AI watermarks."
license: MIT
---

# Translation rewrite

Translates a text to esperanto and back as an attempt to get rid of AI watermarks. To be mainly used for plaintext prose.

Note: tell the user what it can't do. The round trip keeps the structure of each sentence, and that structure is most of what linters and detectors see. On the eval file (`evals/files/prose.md`) the result still scored 89 % on `myoo prose_lint`, 100 % on ZeroGPT and 99 % on Sapling. Shuffling the words of a text flagged by ZeroGPT kept it at 100 %, so its score doesn't rest on a watermark that the round trip would wash out. Suggest the no-ai-patterns skill when the goal is text that reads less like AI.

## Steps

1. Translate the input text into esperanto (or other user-specified language)
2. Launch a subagent to translate the text into the original language. Only launch the subagent with the following prompt exactly as shown below, do not change anything (the subagent should get an empty context):

    translate the following text from `<target language, default=esperanto>` into `<original language>`:

    ```plain
    <original text as-is>
    ```

    Respond with only the translated text and nothing else.

Do not add any additional instructions or modify the original text in any way.
3. Replace the original text with the translated text. If there are any mistakes, fix them, but minimize changes to the translated text as much as possible.

## Examples

Input: get rid of AI watermarks in the text / make the text sound less AI
Output: a text translated into another language and then back as-is
