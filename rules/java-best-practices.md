---
description: "Java code follows the java-best-practices skill. Load it before changing .java, pom.xml or build.gradle files."
globs: ["**/*.java", "**/pom.xml", "**/build.gradle", "**/build.gradle.kts"]
paths: ["**/*.java", "**/pom.xml", "**/build.gradle", "**/build.gradle.kts"]
applyTo: "**/*.java,**/pom.xml,**/build.gradle,**/build.gradle.kts"
alwaysApply: false
# omp: remind once per session, right after the first edit of a matching file
condition: ["**/*.java", "**/pom.xml", "**/build.gradle", "**/build.gradle.kts"]
interruptMode: never
repeatMode: once
---

# Java best practices

- Load the `java-best-practices` skill before writing or changing Java code, and follow it
- If Java code was already changed without it, load it now and re-check those changes against it
