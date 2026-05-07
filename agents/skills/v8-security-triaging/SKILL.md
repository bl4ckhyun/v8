---
name: v8-security-triaging
description: Guides the initial analysis and impact assessment of a V8 security report, strictly excluding implementation or fixing.
---

# Skill: V8 Security Triaging

Use this skill to orchestrate the initial analysis and impact assessment of a V8
security vulnerability report.

## Core Mandates

- **Strategic Orchestration:** You are the **Orchestrator**. Your goal is to
  manage specialized subagents to verify reporter claims empirically while
  keeping your own context lean.
- **Technical Skepticism:** Treat all reporter claims (e.g., "OOB write", "RCE",
  "Silent Write") as **hypotheses**, not facts. Your primary job is empirical
  verification.
- **Scope Limitation:** This skill is strictly for **triaging and impact
  analysis**. It does NOT include implementing a fix or creating a CL. Fixing is
  a separate task that must be explicitly requested by the user after triage is
  complete.
- **No External Actions without Approval:** NEVER upload a CL, post a comment,
  or modify issue metadata on Buganizer or Gerrit without explicit user approval
  of the exact content and action.
- **Buganizer First:** Use the Buganizer MCP (`render_issue`) as the primary
  source of truth. Use `render_issue_with_external` if content is redacted.
- **Sandbox Bypasses vs. Regular Bugs**:
  - **Sandbox Bypass**: Reports that start with in-sandbox memory corruption
    (using `--sandbox-testing` or the Sandbox API). These are strictly governed
    by the V8 Sandbox threat model.
  - **Regular Bug**: Vulnerabilities that do not require an initial in-sandbox
    write primitive.
- **Environmental Awareness**: During information gathering, identify if the
  crash involves **specialized execution modes** (e.g., REPL mode,
  `DebugEvaluate`, or experimental features) that might have different security
  properties.
- **Attachment Access**: Only attempt to retrieve attachment content (e.g.,
  `poc.js`) using the Buganizer MCP tools. If the tools fail, **MUST** ask the
  user to provide the content manually. Do not speculatively search for
  restricted attachments.
- **ClusterFuzz Check**: Check the issue's comments for indications that the
  crash has already been uploaded to ClusterFuzz. If not uploaded, provide the
  user with manual upload instructions in Step 5.
- **Exhaustive Verification:** Never classify a bug based solely on the report.
  Exhaustive technical verification via `v8-poc-classification` is mandatory.
- **Official Documentation:** Always refer to
  [triaging.md](../../../docs/security/triaging.md) for the definitive rules on
  labeling and classification.

## Strategic Orchestration Guidelines

When executing a triage task, delegate tactical steps to subagents:

- **Researcher**: Fetching report details, identifying experts
  (`find_experts_for_file`), and locating Buganizer components.
- **Builder**: Setting up the environment (`git checkout`) and building specific
  variants (Release, ASan, non-ASan).
- **Tester**: Baseline reproduction across multiple configurations and security
  boundary checks.
- **Generalist**: POC minimization, flag bisection, and "healing" POCs
  (replacing natives with standard JS).
- **Debugger**: Interactive crash analysis in GDB to verify primitives and
  attacker control.

## Workflow

### 1. Phase: Intake (Researcher)

Delegate to **Researcher** to gather all necessary data.

- **Action**: Fetch report details using `mcp_Buganizer_render_issue`.
- **Extraction**: Identify the POC script, required `d8` flags, and the
  reporter's environment (commit hash/version). Identify the **introduction
  commit (regression range)** by analyzing the history of affected files or
  using the reporter's claims.
- **Attachment Check**: Check if the reporter mentions specific files (e.g.,
  "poc.html", "crash.log") that are NOT present in the issue's attachments list.
  If any are missing, **MUST** include a request for these files in the final
  update.
- **Mapping**: Identify affected source files and find top experts using
  `mcp_pndMcp_find_experts_for_file`.
- **Component Discovery**: Identify the most specific Buganizer component for
  the affected subsystem (e.g., `Blink > JavaScript > Maglev`) using
  `mcp_Buganizer_list_components`.

### 2. Phase: Exhaustive Reproduction (Tester/Builder/Generalist)

Reproduction is the critical first gate. You MUST confirm the issue exists
before proceeding. Delegate technical deep-dives to `v8-poc-classification`.

- **Baseline**: Delegate to **Tester** to reproduce with the reporter's exact
  flags and revision.
- **Escalation**: If initial attempt fails, delegate to **Builder** and
  **Tester** to try:
  - Different build variants (Release, Debug, ASan).
  - Current `origin/main` (HEAD).
- **Healing (Initial)**: If it still fails, delegate to **Generalist** to
  analyze the POC for stability or environmental dependencies (e.g., memory
  limits).
- **Exit**: If reproduction fails after exhaustive attempts across all
  configurations, stop and ask the user for clarification.

### 3. Phase: Security Boundary Verification (Tester/Generalist)

Determine if the bug is a security vulnerability or a regular bug. Utilize
`v8-poc-classification` for detailed investigation loops.

- **Boundary Check**: Delegate to **Tester** to run the POC with
  `reporter_flags + --run-as-[sandbox]-security-poc`.
  - **Note**: The meta-flag MUST be specified *in addition to* the existing
    flags.
- **Investigation Loop**: If the crash **stops** reproducing with the security
  flag:
  1. **Analyze**: Delegate to **Generalist** to identify why. Is it a forbidden
     flag, a developer-only feature, or natives syntax?
  2. **Heal**: Delegate to **Generalist** to attempt "healing" the POC. Replace
     forbidden syntax (e.g., `%OptimizeFunctionOnNextCall`) with standard JS
     logic (e.g., a hot loop) while maintaining the bug trigger.
  3. **Conclude**: If it cannot be healed or still fails, explain technically
     why the report is invalid.

### 4. Phase: Impact Determination & Minimization (Debugger/Generalist)

Technical proof of the vulnerability's impact. Use `v8-poc-classification` to
verify primitives and attacker control.

- **Crash/Corruption Priority**: Delegate to **Generalist** to attempt to make
  the POC either **crash** (SEGV, Abort) or **demonstrate clear memory
  corruption** (e.g., via non-overwritten side effects, type confusion detected
  in JS).
- **Verification**: Delegate to **Tester** to run the POC on a **Standard
  Release build (non-ASan)** and **ASan build**.
- **Minimization**: Delegate to **Generalist** to reduce the POC and flags to
  the smallest possible set that still reproduces the security violation.
- **Deep Dive**: Delegate to **Debugger** to capture the crash in GDB and
  verify:
  - **Primitive**: Is it a Read or Write?
  - **Control**: Does the faulting address or register contain data from the
    POC?
  - **Traps**: Is this a safe termination (e.g., `SBXCHECK`)?

### 5. Phase: Reporting Findings

Draft a concise synthesis based on verified subagent findings.

- **Mandatory First Sentence**: "This analysis is AI-generated using the
  `v8-security-triaging` skill (Conversation ID: `<id>`)." (Use
  `INVOKER_INFO_SESSION_ID`).
- **Formatting Requirement**: Use a **bulleted list** format for the main points
  (Status, Classification, Rationale, etc.) and ensure there are **double line
  breaks** between each list item for optimal rendering in Buganizer.
- **Content:**
  - **Classification**: Vulnerability / Bug / Not a Bug (Intended Behavior).

  - **Security Impact**: Provide the label (e.g., `Security_Impact-Head`) and a
    short explanation. Skip or simplify the CVSS vector unless requested.

  - **Proposed Severity**: Provide the proposed severity (e.g., `S1`) based on
    [triaging.md](../../../docs/security/triaging.md) and Chromium guidelines.

  - **Introduced In / Regression Range**: Provide the commit or version where
    the vulnerability was introduced, if identifiable.

  - **Rationale**: Explain the technical conclusion. For sandbox bypasses,
    explicitly state if it violates the threat model.

  - **Local Reproduction Findings**: Follow the structure and mandatory fields
    defined in the **Classification Guidelines** of `v8-poc-classification`.
    Ensure all technical data (Status, Reproduction command, Result, Build,
    Verified Impact, and GDB Backtrace) is included here.

  - **Proposed Owner**: Based on expert discovery. Include a very short (half
    sentence) explanation for the choice (e.g., "author of affected code",
    "primary maintainer of subsystem").

  - **Proposed Component**: Propose the most specific Buganizer component
    possible (e.g., `Parser`, `Maglev`, `Turbofan`) if the current component is
    the top-level V8 engine component or is otherwise incorrect. Include the
    component path and ID.

  - **ClusterFuzz Upload Info (User Only)**: If a real crash or memory
    corruption is confirmed and it has NOT yet been uploaded to ClusterFuzz,
    provide all necessary details for a manual upload (repro file, job name,
    issue ID, and flags) to the user. Explicitly advise the user to perform the
    upload.
- **Action**: Present the draft analysis and (if applicable) the ClusterFuzz
  upload info to the user for approval. Clarify that the ClusterFuzz info is for
  the user's manual action and will NOT be posted to Buganizer.
- **Post Update**: Use `mcp_Buganizer_add_buganizer_comment` to post ONLY the
  approved analysis message if available; otherwise, ask the user to post it.
