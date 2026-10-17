"""Planner: turn a high-level task into an ordered plan of steps using an LLM.

The planner asks the model_router for a plan in a simple JSON format. The executor
will interpret and run the steps.
"""
import json
from model_router import ModelRouter

router = ModelRouter()

PLAN_PROMPT = '''You are a planner that converts a user's task into a JSON list of steps.
Each step must have: id, action, tool (optional), args (dict), human (bool) indicating whether human input is required,
and description.
Return only valid JSON. Task: {task}
'''


def create_plan(task_text):
    messages = [
        {"role": "system", "content": "You are a planner that produces deterministic step lists for automation."},
        {"role": "user", "content": PLAN_PROMPT.format(task=task_text)}
    ]
    resp = router.ask(messages)
    # try to parse JSON from response
    try:
        obj = json.loads(resp)
        return obj
    except Exception:
        # fallback: try to extract JSON substring
        import re
        m = re.search(r"(\{.*\}|\[.*\])", resp, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    # last-resort: wrap plain text as one-step plan
    return [{"id": "1", "action": "note", "description": task_text, "human": False, "args": {}}]
