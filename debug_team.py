import json
from pathlib import Path

file_path = Path(r"e:\github_repos\MetaGPT-Pro\workspace\storage\team\team.json")
if not file_path.exists():
    print("No team.json found")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Inspect roles and their memory/todo
roles = data.get('roles', {})
print(f"Roles found: {list(roles.keys())}")

for name, role_data in roles.items():
    print(f"\n--- Role: {name} ---")
    # Check memory
    history = role_data.get('rc', {}).get('memory', {}).get('storage', [])
    print(f"Memory count: {len(history)}")
    if history:
        last_msg = history[-1]
        print(f"Last message content preview: {str(last_msg.get('content'))[:100]}...")
        print(f"Last message sent_from: {last_msg.get('sent_from')}")
        print(f"Last message send_to: {last_msg.get('send_to')}")
    
    # Check todo
    print(f"Todo: {role_data.get('rc', {}).get('todo')}")
    
    # Check working memory if any specific field exists
    # And check if there is a 'planner' or 'plans'
    planner = role_data.get('planner', {})
    if planner:
        tasks = planner.get('plan', {}).get('tasks', [])
        print(f"Plan Tasks: {len(tasks)}")
        for t in tasks:
            print(f"  - Task {t.get('task_id')}: {t.get('instruction')[:50]}... [Assignee: {t.get('assignee')}, Status: {t.get('is_finished')}]")

