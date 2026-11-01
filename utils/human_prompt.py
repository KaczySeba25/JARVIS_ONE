"""Human prompt utilities: unify CLI-based human-in-the-loop interactions.

ask_human(prompt) will show prompt, record response to semantic_memory and return it.
"""
import semantic_memory as sm


def ask_human(prompt):
    print("\n--- HUMAN INPUT REQUIRED ---")
    print(prompt)
    resp = input("Twoja odpowiedz: ")
    try:
        sm.save_memory('human_input', 'last', f"{prompt} -> {resp}")
    except Exception:
        pass
    return resp
