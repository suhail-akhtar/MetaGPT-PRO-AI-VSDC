import json
from pathlib import Path

file_path = Path(r"e:\github_repos\MetaGPT-Pro\workspace\storage\team\team.json")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

roles = data['env']['roles']

for name, role_data in roles.items():
    print(f"\n--- Role: {name} ({role_data.get('profile')}) ---")
    print(f"Use Fixed SOP: {role_data.get('use_fixed_sop')}")
    
    # Check memory
    # Memory structure might be 'history' -> 'storage' based on BaseEnv? 
    # Or Role has 'rc' -> 'memory'
    rc = role_data.get('rc', {})
    memory = rc.get('memory', {}).get('storage', [])
    print(f"Memory count: {len(memory)}")
    if memory:
        last_msg = memory[-1]
        content = last_msg.get('content')
        if isinstance(content, str):
            print(f"Last message content preview: {content[:100]}...")
        else:
            print(f"Last message content type: {type(content)}")
        print(f"Last message sent_from: {last_msg.get('sent_from')}")
        print(f"Last message send_to: {last_msg.get('send_to')}")
    
    # Check Plan if it exists (for RoleZero based roles)
    planner = role_data.get('planner', {})
    if planner:
        plan = planner.get('plan', {})
        tasks = plan.get('tasks', [])
        print(f"Plan Tasks: {len(tasks)}")
        for t in tasks:
            print(f"  - Task {t.get('task_id')}: {t.get('instruction')[:50]}... [Assignee: {t.get('assignee')}, Status: {t.get('is_finished')}]")
            
    # Check Todo
    print(f"Todo: {rc.get('todo')}")
