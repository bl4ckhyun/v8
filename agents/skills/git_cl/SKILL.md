---
name: git_cl
description: "Conventions for git cl commit messages in V8."
---

# Skill: Git CL Conventions

Use this skill to ensure correct formatting of commits and CLs in V8.

## Commit Message Format

-   **Title**: The title MUST follow the format `[component] Title`.
    -   **CORRECT**: `[compiler] Fix crash in loop unroller`
    -   **INCORRECT**: `[compiler]: Fix crash in loop unroller` (Do NOT use a colon after the component).
-   **Description**: Provide a clear explanation of the "why" and "what". Wrap lines at 72 characters.
-   **Tags**: All tag-like lines (e.g., `TAG=`, `BUG=`, `CONV=`) must be at the very bottom of the CL description.
    -   Always include `TAG=agy` for agent-generated changes.

## CL Description Guidelines

-   **Formatting**: CL descriptions should always be formatted and wrapped at 72 columns.
-   **Focus on Content & Effects**: The description should reflect the **contents** and **effects** of the changes, not the process or historical steps taken to get there.
-   **Highlight Important Details**: Focus on the rationale ('why') and key non-obvious design decisions.
-   **Conciseness**: Keep descriptions focused and avoid unnecessary wordiness.
-   **Keep Description Up-to-Date**: Always update the CL description to accurately reflect the *entire* set of changes in the CL. **NEVER** append multiple CL descriptions into one; rewrite or integrate them into a cohesive summary.
-   **Bug Lines**: When listing multiple bugs, do not put more than 4 or 5 bugs on a single line (Gerrit stops rendering them as links). If you have more, add a second `Bug:` line.
-   **Preserve Change-Id**: **ALWAYS** keep the `Change-Id` line when updating the CL description.

## Git Command Usage

-   **Avoid Interactive Prompts**: Always run commands non-interactively to prevent hanging. Use `git --no-pager` or `PAGER=cat` for commands with long output (e.g., `git branch`, `git log`, `git cl desc`). Bypass editors by prefixing with `EDITOR=true` (e.g., `EDITOR=true git commit --amend`). For `git cl upload`, avoid the deprecated `-m` flag; use `-t` and `--commit-description=+` instead.
-   **Always Format**: Always run `git cl format` before creating a commit or uploading a CL to ensure your code adheres to the style guide.
-   **Avoid Interactive Editors**: When committing, amending, or uploading (e.g., `git cl upload`), if there is a risk of an editor opening, prefix the command with `EDITOR=cat` (e.g., `EDITOR=cat git cl upload`) to force non-interactive behavior.
-   **Updating CL Description**: To update the CL description on Gerrit from your local commit message (e.g., after amending to add bugs), use `git cl upload --commit-description=+`. This avoids interactive prompts and forces the description to sync with your local HEAD commit.
-   **Timeout for Stuck Commands**: If a git command (like `checkout`, `commit`, `upload`) does not show progress within a reasonable time (e.g., 1 minute), kill the task immediately and retry with a better setup or report to the user. Do not let it run indefinitely.
-   **Check Status & Alerts**: Always run `git cl status` after uploading or when checking the state of a CL to identify failing checks or try jobs. Suggest addressing these alerts to the user.
-   **Branching & Checkouts (AVOID POLLUTION)**: When creating a new worktree or branch (e.g., `git worktree add -b branch_name path origin/main`), **always explicitly specify `origin/main`** as the base commit. If you do not specify the base, `git` defaults to the current `HEAD`, which may contain unrelated experimental or local commits. This will cause unrelated code to be accidentally merged into your CL.
-   **Verify Before Uploading**: Before running `git cl upload`, you MUST verify exactly what you are uploading. Run `git log origin/main..HEAD` or `git diff --name-only origin/main..HEAD`. If you see commits or files that are not part of your specific task (e.g., "a bunch of code" you didn't write), **DO NOT UPLOAD**. You are on the wrong baseline. Reset your branch to `origin/main` and cherry-pick only your intended commits.
-   **Branching for Unrelated Changes**: If you have changes that are unrelated to the current branch's purpose or active CL, **NEVER** upload them to the same CL or commit them to the same branch. You MUST create a new branch for these changes.
-   **Base New Branches on Clean Upstream**: When creating a new branch for a clean set of changes or to fix a CL, always base it on a clean upstream (e.g., `origin/main`). Do not simply run `git checkout -b new-branch` from your current branch unless you are sure it is clean.
-   **Verify Process CLs**: For CLs intended to contain ONLY process/documentation changes (like skill updates), always verify that no code files (e.g., `.cc`, `.h`, `.js`, `.py`) are modified before uploading. Use `git diff --name-only origin/main` to check.
-   **Fetching Latest Patchset of a CL**: Use `git cl patch <CL_NUMBER>` to fetch and checkout the latest patchset of a CL.
