"""Executor: execute plans produced by the planner.

Supports actions:
- web_research : calls skills.web_research
- run_skill    : calls skills.<name>.run(args)
- playwright_script : runs a playwright script generated to sandbox
- human_prompt : asks user for input via utils.human_prompt
- save_credentials : uses vault_manager to save sensitive info
- note : store a note in semantic_memory

Executor is conservative: it will not bypass human prompts automatically.
"""
import importlib
import os
import json
from utils.human_prompt import ask_human
import semantic_memory as sm
import vault_manager as vm

def _call_skill(name, arg):
    try:
        module = importlib.import_module(f"skills.{name}")
        importlib.reload(module)
        if hasattr(module, 'run'):
            return module.run(arg if arg is not None else "")
        return f"Skill {name} has no run()"
    except Exception as e:
        return f"Skill error: {e}"


def _run_playwright(script_text, script_name="auto_script"):
    # write script to sandbox and attempt to run it with playwright if available
    sandbox = os.path.join(".sandbox", "playwright")
    os.makedirs(sandbox, exist_ok=True)
    path = os.path.join(sandbox, f"{script_name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(script_text)
    # try to execute via playwright if installed
    try:
        import subprocess
        # run in a separate process; user should ensure playwright installed
        p = subprocess.run(["python", path], capture_output=True, text=True, timeout=300)
        return p.stdout + "\n" + p.stderr
    except Exception as e:
        return f"Could not run playwright script: {e}\nScript saved to: {path}"


def execute_plan(plan):
    results = []
    for step in plan:
        action = step.get('action')
        args = step.get('args', {}) or {}
        desc = step.get('description', '')
        human = step.get('human', False)
        sid = step.get('id', '')
        results.append({"id": sid, "start": True, "action": action})

        if human:
            # ask human
            prompt = desc or args.get('prompt', 'Proszę o interwencję')
            answer = ask_human(prompt)
            results[-1]['result'] = answer
            continue

        if action == 'web_research':
            kw = args.get('query') or desc
            try:
                from skills import web_research
                r = web_research.run(kw)
                results[-1]['result'] = r
            except Exception as e:
                results[-1]['result'] = f"web_research error: {e}"
            continue

        if action == 'run_skill':
            name = args.get('skill')
            arg = args.get('arg', '')
            r = _call_skill(name, arg)
            results[-1]['result'] = r
            continue

        if action == 'playwright_script':
            script = args.get('script')
            name = args.get('name', 'auto')
            r = _run_playwright(script, name)
            results[-1]['result'] = r
            continue

        if action == 'save_credentials':
            name = args.get('name')
            cred = args.get('credentials')
            vm.save_credentials(name, cred)
            results[-1]['result'] = f"saved credentials {name}"
            continue

        if action == 'note':
            sm.save_memory('note', sid or 'note', desc)
            results[-1]['result'] = 'noted'
            continue

        results[-1]['result'] = f"Unknown action: {action}"
    return results
