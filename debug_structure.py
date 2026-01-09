import json
from pathlib import Path

file_path = Path(r"e:\github_repos\MetaGPT-Pro\workspace\storage\team\team.json")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Top level keys: {list(data.keys())}")
if 'env' in data:
    print(f"Env keys: {list(data['env'].keys())}")
    if 'roles' in data['env']:
         print(f"Env Roles found: {list(data['env']['roles'].keys())}")
