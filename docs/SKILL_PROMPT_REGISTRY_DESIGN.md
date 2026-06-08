# Skill Prompt Registry Design

**Status: design only. Not implemented.**

This document describes future `SkillRegistry` and `PromptTemplateRegistry`
concepts for `workflow-harness`. It is a design target only. It does not
implement any registry, schema, planner behavior, runtime behavior, prompt
execution, broker/sandbox behavior, or execution path.

## Trust Boundary

- Planner may propose desired skills and prompt intent, but cannot authorize
  them.
- Compiler remains the sole authority boundary.
- Arbitrary planner prompts must not become executable prompts.
- Prompt templates are versioned, reviewed artifacts.
- Skills are versioned, reviewed artifacts.

## Capability Boundary

- A skill does not automatically imply tool access.
- Tool access remains explicit per node/capability envelope.
- Skill access remains explicit per node/capability envelope.
- Prompt-template access remains explicit per node/capability envelope.

## Future Registry Intent

Future skills must declare allowed inputs, allowed outputs, model policy, prompt
template, and tool policy.

Future prompt templates must declare allowed variables, output schema,
version/hash, and forbidden content such as credentials or approval decisions.

Future skill execution must be broker/sandbox mediated if it uses LLM/subagent
execution.

## Credential and Authority Limits

- No credentials in planner output, prompt templates, compiled artifacts, logs,
  summaries, or capability envelopes.
- No approval carryover.
- No authority subsumption.

## Conceptual Skill Example

The following example is conceptual only. It is **not** an executable schema,
not an implemented artifact, and not a runtime contract.

```json
{
  "skill_id": "innovation_opportunity_generator",
  "skill_version": "v1",
  "skill_type": "llm_subagent",
  "prompt_template_id": "innovation_opportunity_generator_prompt_v1",
  "allowed_inputs": ["ProgramContext.json", "RetrievedContext.json"],
  "allowed_outputs": ["InnovationIdeaCandidates.json"],
  "model_policy": {
    "allowed_model_family": "approved_internal_llm",
    "temperature_max": 0.3
  },
  "tool_policy": "none"
}
```

## Conceptual Prompt Template Example

The following example is conceptual only. It is **not** an executable schema,
not an implemented artifact, and not a prompt execution surface.

```json
{
  "prompt_template_id": "innovation_opportunity_generator_prompt_v1",
  "version": "v1",
  "allowed_variables": ["program_context", "retrieved_context", "rubric"],
  "output_schema": "InnovationIdeaCandidates.schema.json",
  "forbidden_content": ["credentials", "approval_decisions", "hidden_policy"]
}
```

## Non-Goals

This document does not enable LLM planning, dynamic skills, prompt execution,
tools, connectors, MCP/network access, sandbox/broker behavior, or real execution.
