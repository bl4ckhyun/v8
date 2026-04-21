---
name: writing_skills_rule
trigger: agents/**/*
---

# Best Practices for Writing Skills and Rules in `agents/`

This rule applies to any addition or modification to the `agents/` directory. When creating new skills or rules, adhere to the following best practices.

## 1. Rules vs. Skills: When to Use Which

*   **Use a Rule** when you need to enforce high-level constraints, workflow mandates, role restrictions, or high-level directives. Rules are usually "always on" or triggered by specific situations (e.g., debugging). They restrict behavior or mandate specific orchestration.
*   **Use a Skill** when you need to provide a specific technical guide, procedure explanation, or reference implementation for a focused task. Skills provide step-by-step instructions or reference material for a specific domain (e.g., porting a class, using a tool).

## 2. Tone and Style: Be Positive Instead of Negative

*   **Focus on what the agent *should* do** rather than what it *should not* do. Positive instructions are more effective for AI models.
*   **If you must specify a negative constraint** (what not to do), ensure you immediately provide a clear alternative action or guidance on what to do instead.

## 3. Structure and Clarity

*   **Structural Clarity**: Use clear hierarchy, headers, and bullet points. If defining complex prompts, consider using XML-style tags to separate different parts (e.g., context, instructions, constraints).
*   **Precision**: Be specific about the "What" and "How". Break down complex tasks into sequential steps.
*   **Skill & Tool Descriptions**: Treat skill and tool descriptions like professional API documentation. Specify the purpose, when to use it, parameters, and expected outcomes.

## 4. Examples

*   **High-Quality Examples**: Provide few-shot examples of both input and desired output to guide the agent, especially for complex formatting or reasoning steps.

**Example: Positive Framing**
*   *Bad (Negative)*: "Do not use Python 2."
*   *Good (Positive)*: "Always use Python 3 for new scripts."

**Example: Rule vs. Skill**
*   *Rule*: `always_use_bazel.md` (Mandates that the agent must use `bazel build` instead of `make`).
*   *Skill*: `how_to_add_bazel_target.md` (Provides step-by-step instructions on writing a BUILD file).
