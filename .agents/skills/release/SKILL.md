---
name: release
description: "Bumps the myoo-skills plugin version, commits it, tags vX.Y.Z and publishes a GitHub release. Use when the user asks to release, publish, ship, bump the version, or push skill changes out to installed plugins."
license: MIT
compatibility: "Requires git, jq and an authenticated gh CLI"
---

# Release

Publishes a new version of the `myoo-skills` plugin. Plugin managers (omp `marketplace.autoUpdate: auto`, `claude plugin update`, ...) only reinstall when the version in the catalog is a newer semver than the installed one, so changes pushed to `main` without a version bump never reach users.

The version lives in two files and must stay identical:

- `plugin.json`: `.version`
- `.claude-plugin/marketplace.json`: `.plugins[] | select(.name == "myoo-skills") | .version`

## Steps

1. Run `git fetch --tags origin` and check the repository state:
    - current branch is `main`, and `git status --porcelain` is empty
    - `git rev-list --count HEAD..origin/main` is `0`; otherwise `git pull --rebase` first
2. Read both versions and stop if they differ:

    ```bash
    jq -r .version plugin.json
    jq -r '.plugins[] | select(.name == "myoo-skills") | .version' .claude-plugin/marketplace.json
    ```

3. Find the previous release: `prev=$(git describe --tags --abbrev=0 --match 'v*')`. No tag means this is the first release.
4. Collect the changes since the previous release:

    ```bash
    git log --no-merges --format='- %s' "$prev"..HEAD
    git diff --name-status "$prev" HEAD -- skills rules
    ```

    For the first release, run `git log` without the range and diff against the empty tree: `git diff --name-status "$(git hash-object -t tree /dev/null)" HEAD -- skills rules`. Stop if nothing changed since the previous tag.
5. Pick the bump. Use the user's version or level if given, else infer it from step 4:
    - major: a skill or rule was removed or renamed, or a skill's behavior changed incompatibly
    - minor: a skill or rule was added
    - patch: anything else (wording, fixes, evals, docs)
6. Set the new version `X.Y.Z` in both files, changing only the version fields. Re-run the step 2 commands; both must print `X.Y.Z`, and `jq empty plugin.json .claude-plugin/marketplace.json` must succeed.
7. Commit only those two files: `git commit -m "release vX.Y.Z" -- plugin.json .claude-plugin/marketplace.json`.
8. Tag: `git tag -a vX.Y.Z -m "vX.Y.Z"`.
9. Push branch and tag in one step: `git push --atomic origin main vX.Y.Z`.
10. Write release notes to a temp file: one line per added, changed and removed skill or rule from step 4, then the commit subjects. Publish them with `gh release create vX.Y.Z --verify-tag --title vX.Y.Z --notes-file <file>`.
11. Report the version change (`old -> new`), the release URL from `gh release view vX.Y.Z --json url --jq .url`, and that omp installs with `marketplace.autoUpdate: auto` pick it up on their next startup once their cached catalog is older than 24h (`omp plugin marketplace update myoo-skills && omp plugin upgrade` to get it now).

## Examples

Input: "release the new skill"
Output: `skills/osint/` was added since `v0.1.0`, so the agent bumps both manifests to `0.2.0`, commits `release v0.2.0`, pushes `main` and tag `v0.2.0`, and publishes a GitHub release with notes such as:

```md
- added `osint`
- changed `no-ai-patterns`: evals added

- add osint skill
- no-ai-patterns: add evals
```

Input: "bump to 1.0.0"
Output: same flow with version `1.0.0`, regardless of the inferred level.

## Edge cases

- Uncommitted or unpushed unrelated work: ask whether to commit it first; never fold it into the release commit.
- New version not greater than the current one: stop and ask. Plugin managers ignore downgrades and equal versions.
- Tag `vX.Y.Z` already exists locally or on `origin`: stop and ask; never move or delete a published tag.
- Pre-release requested (`X.Y.Z-rc.1`): add `--prerelease` to `gh release create`, and warn the user that omp auto-update still installs it, because `0.2.0-rc.1` is newer semver than `0.1.0`.
- `gh` missing or unauthenticated: the pushed tag is still the release. Give the user the `gh release create` command to run.
- Push rejected: the atomic push published nothing. Run `git pull --rebase` (stop and ask on conflicts in the manifests), recreate the unpublished tag on the rebased commit with `git tag -d vX.Y.Z && git tag -a vX.Y.Z -m "vX.Y.Z"`, and push again.
