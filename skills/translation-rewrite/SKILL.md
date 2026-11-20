---
name: translation-rewrite
description: "Translates a text to esperanto and back as an attempt to get rid of AI watermarks."
license: MIT
---

# Translation rewrite

Translates a text to esperanto and back as an attempt to get rid of AI watermarks. To be mainly used for plaintext prose.

## Steps

1. Translate the input text into esperanto
2. Launch a subagent to translate the text into the original language. Only launch the subagent with the following prompt exactly as shown below, do not change anything:

    translate the following text from esperanto to `<original language>`:

    ```plain
    <original text as-is>
    ```

    Respond with only the translated text and nothing else.

Do not add any additional instructions or modify the original text in any way.
3. Replace the original text with the translated text. If there are any mistakes, fix them, but minimize changes to the translated text as much as possible.

## Examples

Input: what the user asks.
Output: what the agent produces.

## Edge cases

- Situation: what to do instead.

## Resources

All paths are relative to this skill's directory. Keep references one level deep and keep this file under 500 lines.

- [references/REFERENCE.md](references/REFERENCE.md): read when ...
- `scripts/example.sh`: run to ...
