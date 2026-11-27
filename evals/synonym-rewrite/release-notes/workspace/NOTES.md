# Release notes: Stackpin 3.1

## Overview

Stackpin 3.1 is a significant update that brings powerful new capabilities to dependency pinning. This release focuses on improving reliability, enhancing performance and streamlining the overall developer experience. Every team that manages multiple services will benefit from these improvements.

## New features

Stackpin now supports lockfile verification in continuous integration. The new `stackpin verify` command compares the current lockfile against the recorded checksums and fails the build when a package has changed unexpectedly. This ensures that every deployment uses exactly the dependencies that were reviewed.

```sh
stackpin verify --lockfile stackpin.lock --strict
```

Additionally, the resolver is now considerably faster. Large monorepos with hundreds of packages will notice a dramatic reduction in resolution time. Detailed benchmarks are available in the [performance report](https://stackpin.dev/blog/resolver-3-1).

## Important changes

The configuration format has been updated to provide greater flexibility. Existing projects should migrate their settings by running the following command:

```sh
stackpin migrate-config --from 2 --to 3 ./stackpin.toml
```

Projects that skip this step will continue to work, but they will receive a deprecation warning on every run. Support for the old format will be removed in the next major release.

## Getting help

If you encounter any problems during the upgrade, please consult the [migration guide](https://stackpin.dev/docs/migrate-3) or open an issue on [GitHub](https://github.com/stackpin/stackpin/issues). Our maintainers are committed to helping every user complete the transition smoothly.
