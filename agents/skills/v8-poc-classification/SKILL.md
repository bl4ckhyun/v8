---
name: v8-poc-classification
description: Checks if a POC provided by some JS and d8 flags is a vulnerability or just a regular bug.
---

# Skill: V8 POC Classification

Use this skill to determine if a reported Proof-of-Concept (POC) crash is a
security vulnerability or a regular bug.

## Core Mandates

- **Scope Limitation:** This skill is strictly for **technical analysis and
  classification**. It does NOT include implementing a fix.
- **Empirical Verification of ALL Claims:** Do not take ANY part of the
  reporter's classification or impact claims at face value. Every claim (e.g.,
  "arbitrary memory write", "sandbox escape", "silent write") MUST be
  empirically verified. If a claim cannot be observed in a debugger, it must be
  noted as "unverified" in the final rationale.
- **Verify with Debuggers:** A claim of memory corruption must be verified by
  observing the crash or memory state using debugging tools (GDB).
  - **Read vs. Write:** You MUST verify the faulting instruction type.
    - `mov rax, [rbx]` is a **Read**.
    - `mov [rax], rbx` is a **Write**.
  - **Pointer Control:** Check if faulting addresses or register values are
    actually controlled by the attacker (e.g., contain values from the POC).
- **Mandatory Non-ASan Verification:** For any potential security bug, you MUST
  attempt reproduction on a standard **Release build without ASan/UBSan**.
  - ASan often flags "harmless" OOB accesses that V8 would otherwise handle
    safely or trap.
  - If a non-ASan build prints `Caught harmless memory access violation` or
    `Exiting process due to sandbox violation`, the sandbox is working as
    intended.
- **Exhaustive Reproduction:** Try harder to reproduce the issue locally. If the
  provided POC doesn't crash immediately, try running it multiple times or
  modifying the POC to be more stable.
- **Autonomous Classification:** You are responsible for forming your own
  technical conclusion. If the report claims a vulnerability but your analysis
  shows it is a `DCHECK` failure in a debug build or relies on experimental
  flags, classify it as a **Bug**.

## Workflow

When provided with a reproduction script (JS) and a set of `d8` flags that cause
a crash, follow these steps to classify the bug:

### 1. Initial Verification & Deep Dive

Reproduce the crash using the *provided* flags to confirm the bug exists.

- Command: `d8 <provided-flags> <poc.js>`
- **Deep Dive:** If it reproduces, run it under GDB to inspect the crash state.
  Capture the backtrace, the faulting instruction, and relevant register values.
- **Check for Safe Termination:** Look for functions like
  `PushStackTraceAndDie`, `SBXCHECK`, or `FATAL` in the backtrace. If these are
  present, V8 has detected the corruption and is intentionally crashing.

### 2. Impact Escalation (Crucial for Classification)

If the bug exists but does NOT cause a crash (e.g., a "stale value" or "logical
type confusion"), you MUST attempt to escalate it to a memory safety violation.

- **Objective**: Prove that the logical flaw can bypass V8's security
  boundaries.
- **Techniques**:
  - **Type Confusion**: Use a stale tag to mislead the compiler into using an
    object with an incompatible layout (e.g., reading a reference as an
    integer).
  - **OOB Access**: Use a stale length to mislead the compiler into eliding a
    bounds check that should have fired.
- **Verification**: If escalation attempts only lead to `RuntimeError` (illegal
  cast, OOB access) or safe termination without a memory violation, it is likely
  a **Bug**, not a vulnerability. V8's runtime protections (like `ref.cast` and
  Wasm bounds checks) are designed to mitigate such flaws.

### 3. Check with Security POC Flags

Run the reproduction with the appropriate meta-flags. This is the most important
step for classification.

#### Regular Security POC

- Command: `d8 --run-as-security-poc <provided-flags> <poc.js>`
- **Result**: If the crash still occurs, it is likely a valid security
  vulnerability (**Type=Vulnerability**).

#### Sandbox Security POC

- Command: `d8 --run-as-sandbox-security-poc <provided-flags> <poc.js>`
- **Result**: If the crash still occurs and shows **write access outside the
  sandbox**, it is a valid sandbox vulnerability.
- **Important:** Read access outside the sandbox is currently NOT considered a
  vulnerability.

### 3. Isolate Required Flags (If needed)

If the crash stops reproducing with the security POC flags, identify which
restriction prevents the crash. Try running with individual flags (e.g.,
`--disallow-unsafe-flags`, `--disallow-developer-only-features`,
`--no-experimental`, or `--fuzzing`) to isolate the behavior.

Refer to [reproducing-bugs.md](../../../docs/security/reproducing-bugs.md) and
[triaging.md](../../../docs/security/triaging.md) to understand the
implications. In general, if a POC stops reproducing when any of these flags are
set, it is likely not a security bug.

### 4. Classification & Impact Assessment

Determine the appropriate Buganizer fields and the actual security impact based
on your findings and the rules in
[triaging.md](../../../docs/security/triaging.md).

**Findings from Local Reproduction:** The classification MUST be supported by
empirical evidence from the local reproduction:

- **Reproduced:** [Yes/No]
- **Build Configuration:** [e.g., x64.release, x64.debug, asan]
- **Verified Impact:** [e.g., "Confirmed OOB write of 8 bytes at 0x... via GDB"]
- **GDB Backtrace Snippet:** [Top 3-5 frames]

#### Classification Guidelines

Refer to [triaging.md](../../../docs/security/triaging.md) for the definitive
rules. Summary:

- **Type=Vulnerability**: Production code, enabled by default
  (Security_Impact=Head/Beta/Stable/Extended) or not enabled by default
  (Security_Impact=None). Default to **S1** for memory corruption.
- **Type=Bug**: Experimental flags (not in `--future`), developer/unsafe flags,
  `nullptr` dereference, `DCHECK` or reliable `CHECK` failure.
- **Intended Behavior**: Safe termination via `SBXCHECK`, `FATAL`, or hardened
  libc++ checks (`std::vector`/`std::span` OOB).

#### Sandbox Bypasses (starting with in-sandbox corruption)

Reports using `--sandbox-testing` or the Sandbox API.

- **Sandbox bypass (Write access)**: Type=Vulnerability, Security_Impact=None,
  Severity=S2.
- **Read-only bypass**: Type=Bug, Security_Impact=None.
- **Safe Termination**: Output shows `Caught harmless memory access violation`
  or similar. This is **Intended Behavior**.
- **Corrupting the wrong trusted object of the same type with well-formed
  data**: Not a Bug (as long as it doesn't break internal structure). This is
  **Intended Behavior**.
