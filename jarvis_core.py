"""
Core improved Jarvis entrypoint. This provides an interactive loop that uses planner + executor + memory + vault.
Run: python jarvis_core.py
"""
import os
from planner import create_plan
from executor import execute_plan
import semantic_memory as sm
import vault_manager as vm


def interactive():
    print("JARVIS CORE - interactive mode")
    while True:
        try:
            user = input("Ty: ")
            if not user:
                continue
            if user.lower() in ('exit','quit'):
                break
            # store task
            sm.save_memory('task', 'last', user)
            plan = create_plan(user)
            print('\nPlan:')
            for s in plan:
                print(f"- [{s.get('id')}] {s.get('action')} - {s.get('description','')}")
            confirm = input('\nWykonac plan? (tak/nie) > ')
            if confirm.strip().lower() not in ('tak','t','y','yes'):
                print('Anulowano')
                continue
            results = execute_plan(plan)
            print('\nWyniki:')
            for r in results:
                print(r)
            sm.save_memory('task_result', 'last_result', str(results))
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    interactive()
