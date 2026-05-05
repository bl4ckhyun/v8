---
name: v8-security-triaging
description: Guides the initial analysis and impact assessment of a V8 security report, strictly excluding implementation or fixing.
---

# Skill: V8 Security Triaging

Use this skill to perform the initial analysis and impact assessment of a V8
security vulnerability report.

## Core Mandates

- **Technical Skepticism:** Treat all reporter claims (e.g., "OOB write", "RCE",
  "Silent Write") as **hypotheses**, not facts. Your primary job is empirical
  verification.
- **Sandbox Bypasses vs. Regular Bugs:**
  - **Sandbox Bypass:** Reports that start with in-sandbox memory corruption
    (using `--sandbox-testing` or the Sandbox API). These are strictly governed
    by the V8 Sandbox threat model.
  - **Regular Bug:** Vulnerabilities that do not require an initial in-sandbox
    write primitive.
- **Scope Limitation:** This skill is strictly for **triaging and impact
  analysis**. It does NOT include implementing a fix or creating a CL. Fixing is
  a separate task that must be explicitly requested by the user after triage is
  complete.
- **No External Actions without Approval:** NEVER upload a CL, post a comment,
  or modify issue metadata on Buganizer or Gerrit without explicit user approval
  of the exact content and action. This includes `git cl upload`.
- **Official Documentation:** Always refer to
  [triaging.md](../../../docs/security/triaging.md) for the definitive rules on
  labeling and classification.
- **Buganizer First:** Use the Buganizer MCP (`render_issue`) as the primary
  source of truth for report details.
- **Verification Required:** Never classify a bug based solely on the report.
  Exhaustive technical verification via `v8-poc-classification` is mandatory.
  The foundation of the entire triage process is a successful local reproduction
  or a definitive explanation for the lack thereof.
- **ClusterFuzz Check:** Check the issue's comments for indications that the
  crash has already been uploaded to ClusterFuzz (e.g., comments from
  `cluster-fuzz-googleplex@system.gserviceaccount.com`). If not uploaded,
  provide the user with manual upload instructions.

## Workflow

### 1. Information Gathering

Fetch the report details from Buganizer.

- Tool: `mcp_Buganizer_render_issue(issueId="<id>")`
- **Access Issues:** If the tool is missing, fails, or returns no results
  (likely due to access restrictions):
  - Ask the user to install the Buganizer MCP extension.
  - Ask the user to grant access to the `google.com` account for the specific
    issue.
- **Critical Analysis:** Read the report carefully but treat all claims as
  hypotheses. Identify specific impact claims (e.g., "OOB write", "RCE") that
  need empirical verification.
- **Attachment Check:** Check if the reporter mentions specific files (e.g.,
  "poc.html", "crash.log") that are NOT present in the issue's attachments list.
  If any are missing, **MUST** include a request for these files in the final
  triage update, as the issue may be non-actionable without them.

### 2. Technical Verification & Classification

Invoke the `v8-poc-classification` skill to perform the technical deep-dive.

- **Exhaustive Verification:** Follow the workflow in `v8-poc-classification` to
  reproduce the issue, verify impact claims (e.g., Read vs. Write), and check
  for safe-termination traps.
- **Mandatory Non-ASan Build:** Ensure the issue is checked on a standard
  **Release build without ASan** as part of the classification process.
- **Reference Classification Rules:** Use the **Classification & Impact
  Assessment** section in `v8-poc-classification` to determine the final
  Buganizer labels and security impact.

### 3. Reporting Findings

Draft a concise summary of your analysis for the user.

- **Formatting Requirement:** Use a **bulleted list** format for the main points
  (Status, Classification, Rationale, etc.) and ensure there are **double line
  breaks** between each list item for optimal rendering in Buganizer.
- **Content:**
  - **Mandatory First Sentence:** Every update MUST start with: "This analysis
    is AI-generated using the `v8-security-triaging` skill (Conversation ID:
    `<id>`)." Use the current session ID (found in the workspace path or
    environment) for `<id>`.
  - **Status:** Reproduced / Not Reproduced (include exact build and flags
    used).
  - **Classification:** Vulnerability / Bug / Not a Bug (Intended Behavior).
    - **Note:** If a logical bug is verified but cannot be escalated to a crash
      or memory corruption in a **Release build**, classify it as a **Bug**.
  - **Local Reproduction Findings:** Summarize the **Verified Impact** (e.g.,
    confirmed OOB write). If the bug is purely logical and caught by runtime
    protections (like `ref.cast` or bounds checks) without crashing, state this
    clearly. Include a **GDB Backtrace** snippet if it supports the
    classification.
  - **Rationale:** Explain the technical conclusion. For sandbox bypasses,
    explicitly state if it violates the threat model.
  - **Security Impact:** Provide the label and a short explanation. Skip or
    simplify the CVSS vector unless specifically requested.
  - **Reproduction:** Provide the exact `d8` command and flags used to reproduce
    the issue locally, and summarize the observed result (e.g., "Script output
    confirmed stale load").
  - **Proposed Owner:** Propose a suitable owner based on recent commits to
    affected files.
  - **ClusterFuzz Upload Info (User Only):** If a real crash or memory
    corruption is confirmed and it has NOT yet been uploaded to ClusterFuzz,
    provide all necessary details for a manual upload (repro file, job name,
    issue ID, and flags) to the user. Explicitly advise the user to perform the
    upload.
- **Action:** Present the draft analysis and (if applicable) the ClusterFuzz
  upload info to the user for approval. Clarify that the ClusterFuzz info is for
  the user's manual action and will NOT be posted to Buganizer.
- **Post Update:** Use `mcp_Buganizer_add_buganizer_comment` to post ONLY the
  approved analysis message if available; otherwise, ask the user to post it.
