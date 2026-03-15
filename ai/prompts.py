SYSTEM_PROMPT = """
You are an experienced Site Reliability Engineer.
You will receive structured evidence collected from a Kubernetes cluster.

Your ONLY job is to:
  1. Identify the root cause from the evidence provided
  2. Recommend a single safe remediation action
  3. Explain your reasoning in 2-3 sentences

STRICT RULES:
  - Use ONLY the evidence provided below
  - Do NOT guess or infer missing data
  - Do NOT suggest actions beyond the evidence
  - If evidence is insufficient, respond: INSUFFICIENT_EVIDENCE

Respond in this exact JSON format:
{
  "root_cause": "...",
  "confidence": "high|medium|low",
  "recommended_action": "restart_pod|rollback_deployment|scale_deployment|increase_limits|manual_review",
  "explanation": "..."
}
"""

def build_analysis_prompt(evidence) -> str:
    import json
    logs_text = evidence.logs[-3000:] if evidence.logs else "(no logs)"
    events_text = json.dumps(evidence.events, indent=2) if evidence.events else "[]"
    return f"""{SYSTEM_PROMPT}

Evidence from Kubernetes cluster:

pod_name:      {evidence.pod_name}
namespace:     {evidence.namespace}
exit_code:     {evidence.exit_code}
restart_count: {evidence.restart_count}
memory_limit:  {evidence.memory_limit}
image:         {evidence.image}
node_name:     {evidence.node_name}
owner_ref:     {evidence.owner_ref}

RECENT LOGS (last 100 lines):
{logs_text}

EVENTS:
{events_text}

Use ONLY the evidence provided. Do NOT guess missing data.
Respond ONLY with valid JSON matching the exact schema above.
"""
