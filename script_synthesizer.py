"""Script synthesizer: ask model to write a small Playwright script for a step and return script text.

This is the novel capability: Jarvis can synthesize automation scripts (Playwright/Python)
on-demand, save them to a sandbox, and attempt to run them. Scripts are audited and saved.
"""
from model_router import ModelRouter

router = ModelRouter()

PROMPT = '''Generate a Playwright Python script that performs the following step.
Return ONLY the script content (no explanations). Step: {step}
'''


def synthesize(step_text):
    messages = [
        {"role": "system", "content": "You are a safe code generator. Produce only Python Playwright scripts."},
        {"role": "user", "content": PROMPT.format(step=step_text)}
    ]
    script = router.ask(messages)
    return script
