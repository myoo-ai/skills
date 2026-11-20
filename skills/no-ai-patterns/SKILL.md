---
name: no-ai-patterns
description: "Use everytime the user requires the output (codebase or other forms of work) as it would be delivered to them to not be sloppy or for it to look more human/less AI"
license: MIT
---
<!-- markdownlint-disable code-block-style -->

# No AI patterns

This is the main skill that holds many subskills to minimize AI patterns/slop in non-temporary outputs (mostly codebase, however can be used on other things too). Does not apply to temporary work (helper scripts, temporary analyses, etc.), unless otherwise specified by the user.

This is the main skill to apply everytime the user wants the output to be less sloppy or AI. On frequent use, ask the user if you should add a rule to the current agent harness to use this skill everytime for the current project.

## Steps

You can use this as a TODO:

1. Check `which myoo`. If it IS available:
    1. Lint the prose with `myoo prose_lint`, send plaintext in stdin. If it's code, use `myoo code_lint .` instead to recursively lint current directory.
    2. Fix the violations that these commands produced using the recommendations or your best judgement. Sometimes, it is acceptable to ignore a few violations (but no more than 10 % of all violations, if there are at least 10 violations in total). If using `myoo code_lint`, you can ignore violations by adding a comment above the affected line with the content `myoo-ignore: <rule_id>`, for example: `// myoo-ignore: comments-in-file-header` (or `myoo-ignore-file: comments-in-file-header` anywhere in the file)
2. If `myoo-cli` is not available, proceed with dispatching the subagents in the next step. Ask the user if you should install it globally for the current machine/user according to instructions in [myoo-ai/cli](https://github.com/myoo-ai/cli)'s README. This question should not pause the subagents from their review. If the harness doesn't support this or you are unsure, suggest it at the very end of the turn.
3. Dispatch parallel subagents using the prompts below. They will provide insights beyond what `myoo-ai/cli` scripts can offer.
4. After the review process is done, you may fix all of the violations yourself, or dispatch additional agents as necessary.
5. Once the fixes are in, rerun the linters and dispatch the [fix-pass subagent](#fix-pass-subagent) on the diff of the fixes.

### Subagent

Dispatch multiple parallel subagents. Each subagent gets a slice of the rules as divided in [Rules list](#rules-list).

For each subagent, dispatch the following prompt, replacing placeholders as necessary:

    You are taking the role of a human senior reviewer. You will review the output of an AI agent. The output in question might refer to a file, document, prose, media or codebase, and is located here: <insert location of the project here>

    Assume the following rules:

    ```plain
    <see "### Rules list" in this skill>
    ```

    Most of the rules assume software code as the input. Therefore, if a rule is not applicable to the current input, you may skip flagging it.

    Your final report will only consist of the following message and nothing else. It will be plaintext only, and it will follow exactly this format:

    ```txt
    #<nth violation> <path>:<line>:<col from>-<col to>
    OR
    #<nth violation> <path>:<line>:<col from>-<line to>.<col to> - <rule ID like above>: <description exactly like above> (note: <your optional, additional notes, max. 40 characters)
    ```

    Method:
    1. Create a temporary file to append violations to, for instance `/tmp/myoo-patterns_<nth agent>.txt`
    2. Read through every file in the input that can contain violations
      - For plaintext prose, browse entire text and assess whether there is a violation on current line range
      - For codebases, browse through all code files
    3. For every found violation, append it to the file and move on
    4. At end, just report the output of the final violations file

    examples:

    ```
    #1 web/src/components/content/markdown.test.ts:1:1-2.48 - ai-comment
    ```

The subagent comes back with findings that you will fix, along with the `myoo prose_lint`/`myoo code_lint` findings (if `myoo-ai/cli` is available).

### Rules list

These rules can't be verified by `myoo code_lint` and `myoo prose_lint` alone.

#### Generic prose subagent

Always dispatch, applies to all inputs: docs, READMEs, commit messages, PR descriptions, UI copy. It does not apply to chat deliverables or temporary/repl scripts.

```rules
generic-over-specific: a specific fact is replaced by generic praise or an abstraction that could describe any project ("a powerful, flexible tool for managing your data"). state the concrete fact (number, name, behavior) or delete the sentence.
unquantified-claim: a performance, quality or security claim comes with no measurement or reference ("significantly improves performance"). give the number and how it was measured, or drop the claim.
claims-not-in-change: a commit message, PR description or summary claims changes, tests or verification that the diff doesn't contain ("added comprehensive tests" with no test file touched). describe only what the diff does and what was actually run.
changelog-bullets: a commit message or PR body lists every edited file or obvious edit as bullets instead of saying why. write an imperative subject and a short body with the reason and any non-obvious consequence.
vague-attribution: an opinion is attributed to unnamed authorities ("experts agree", "many users report"). name the source or state it as the author's view.
contrast-with-strawman: a mid-sentence "rather than X", "instead of X" or "unlike X" contrasts with an alternative nobody proposed. state the point directly.
nominal-style: actions are turned into nouns or trailing participle chains ("performs validation of the input, enabling detection of errors"). use the verb and split the sentence.
formulaic-outline: the document follows a stock skeleton (Overview, Key Features, Benefits, Challenges, Future Work, Conclusion) whatever the content. keep only the sections the reader needs.
restating-summary: a paragraph or section ends by restating what it just said, in any wording. delete the recap.
over-structure: short content is split into headings, tables or label lists it doesn't need (a five-sentence PR description with Summary, Changes, Testing and Impact headings). write it as plain paragraphs.
elegant-variation: the same thing goes by rotating synonyms ("the tool", "the utility", "the CLI"). pick one term and keep it, since readers assume different names mean different things.
punctuation-substitution: an em dash, semicolon or colon was swapped for a comma splice, " - " or ", so" while the sentence stayed one long AI sentence. split it into separate sentences or restructure it.
```

#### Code and comments subagent

Only dispatch it when input is software code. Give it read access to the whole repository. The reuse and convention rules compare the change with the code around it.

```rules
mirror-docstring: every member, private and trivial ones included, gets a doc comment whose params and return lines repeat the signature. keep doc comments for public API and for behavior, units, side effects and errors a reader can't see.
stale-comment: a comment, doc comment or log text disagrees with the code next to it (wrong count, old name, removed parameter, a fallback that no longer exists). fix or delete the comment.
hedging-comment: a comment hedges without a reason ("just in case", "to be safe", "should work"). name the case being guarded against, or remove the guard (see impossible-guard).
impossible-guard: a null, undefined, type or empty check on a value that the types or the preceding code already guarantee. delete the check and trust the invariant, validate only at system boundaries.
dead-fallback: a fallback value, default branch or alternate path that can't run (`?? default` on a required field, a silent `default:` on an exhaustive enum, "try the new API, else the old one" where the old one is gone). remove it, or make the impossible case fail loudly.
catch-without-purpose: a try/catch that can't catch anything, catch-log-rethrow at every layer, or a broad catch that turns all failures into one generic message. let the error propagate, or catch the specific error where the code does something different.
speculative-abstraction: an interface, base class, factory, strategy, registry, plugin hook or generic parameter with a single implementation and no second use in sight. use the concrete type, and extract when the second case arrives.
pass-through-wrapper: a function, method or class that only forwards to another call and adds no name, contract or policy. call the target directly.
config-for-one-value: options, flags, env vars, constructor params or constants for values no caller ever changes. inline the value, and add the option when someone needs it.
parallel-implementation: new code re-implements something the codebase already has (helper, type, client, validation, formatting) under another name or shape. reuse or extend the existing one.
leftover-old-path: the change keeps replaced code alive (compatibility shims, aliases, re-exports, `_v2` or `legacy` twins, flags that are always on, unused params, uncalled functions). delete the old path and migrate every caller, unless an external consumer needs it, and then say who.
convention-drift: naming, error handling, logging, file layout, test style or library choice differs from what the surrounding code does. follow the local convention.
generic-name: a name says nothing about the domain (`utils`, `helpers`, `common`, `manager`, `data`, `processData`, `handleClick2`). name it after what it holds or does.
scope-creep: the diff has changes the task didn't ask for (unrelated refactors, renames, reformatting, dependency bumps). revert them or split them into a separate change.
unrequested-artifact: the change adds files nobody asked for (summary or implementation markdown, example scripts, ad-hoc test scripts in the root, `*.bak` copies, READMEs that only list file names). delete them.
unconditional-success: a success message, `success: true` result or "all checks passed" output is printed whatever happened. report the actual outcome, or print nothing on success.
log-narration: info-level logs for every step ("Starting X...", "Done with X"), or logging and rethrowing the same error. log once where the error is handled, and keep step traces at debug level or drop them.
mock-tautology: a test asserts what its mock was told to return, or only that mocks were called in order, so it passes whatever the code does. test observable behavior through the real collaborator or a fake that has behavior.
test-restates-implementation: expected values are computed with the same formula as the code (`expect(tax(100)).toBe(100 * TAX_RATE)`), or tests pin private helpers and incidental structure. use known literal expectations and test through the public behavior.
test-gaming: code or tests were bent to make tests pass (special-cased test inputs, `if (env === "test")` branches, loosened or deleted assertions, skipped failing tests, try/catch around assertions). fix the code so the original assertion holds.
```

#### Fix-pass subagent

Dispatch it after violations were fixed, on the diff of the fix pass only. It checks that the fixes solved the problem instead of dodging the rule.

```rules
arbitrary-split: a long-function or deep-nesting violation was "fixed" by cutting the body into sequential chunks (helpers called once with many pass-through params, closures turned into a class) without a meaningful boundary. split only at a named concept, or keep the function.
rule-dodge: code was rewritten just enough to stop a rule from matching while keeping the problem (a non-null assertion hidden behind an assert helper everywhere, `unwrap()` turned into `expect("")`, a duplicated block made unequal by renaming one variable, lines joined to shrink a function). fix the underlying issue the rule describes.
score-gaming: comments were seeded with TODOs, questions, first person, contractions or "we/will/if" wording, or words were swapped mechanically ("its" to "the", "every" to "all"), to lower the "(likely) AI patterns" score. revert the swaps, and write comments only where a reason is needed, in whatever wording reads best.
lost-reason: a fix deleted a comment that explained why (a constraint, a gotcha, a non-obvious invariant) instead of rewording it. put the reason back in plain words.
meaning-drift: a reworded comment or doc now says something different from the original or from the code (a flipped negation, a dropped condition, "when" turned into "if" where it meant time). restore the original meaning.
code-touched-in-comment-pass: a pass that should only change comments changed code (a deleted line next to a removed comment, a broken comment opener, changed indentation that matters). restore the code, and compare the code with comments stripped before and after.
```

## Examples

Input: make it less sloppy/AI; make it human
Output: new output according to this skill + a table with summary of all fixed violations. if any were ignored or skipped, report them in separate section
