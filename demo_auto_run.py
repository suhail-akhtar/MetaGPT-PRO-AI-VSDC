import urllib.request
import urllib.error
import json
import time
import sys
import os

BASE_URL = "http://localhost:8088/v1"

def request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def run_demo():
    print("🚀 STARTING AUTONOMOUS DEMO: 'Snake Game'")
    print("------------------------------------------")
    
    # 1. Start Conversation
    print("1️⃣  Submitting Idea: 'Create a classic Snake Game using Python and Pygame'")
    data = request("POST", "/conversation/start", {"initial_idea": "Create a classic Snake Game using Python and Pygame"})
    if not data: return
    conv_id = data['conversation_id']
    print(f"   AI: {data['first_question'][:60]}...")
    
    # 2. Add Details
    print("\n2️⃣  Providing Details: 'Include a scoreboard, 3 lives system, and increasing difficulty.'")
    data = request("POST", "/conversation/message", {
        "conversation_id": conv_id, 
        "message": "Include a scoreboard, 3 lives system, and increasing difficulty. I am ready to start."
    })
    if not data: return
    print(f"   AI: {data['ai_response'][:60]}...")
    
    # 3. Approve
    print("\n3️⃣  Approving Requirements (Triggering Autonomous Agents)...")
    data = request("POST", "/conversation/approve", {"conversation_id": conv_id})
    if not data: return
    project_id = data['project_id']
    print(f"   ✅ Project Created: {project_id}")
    print("   ⚡ Agents have been dispatched to the backend container.")
    
    # 4. Monitor
    print(f"\n4️⃣  Monitoring Progress for {project_id}...")
    print("   (Agents are writing PRDs, designing system, and coding in the workspace)")
    
    start_time = time.time()
    last_files = set()
    
    # We will monitor for 60 seconds or until user stops
    try:
        while time.time() - start_time < 120:
            # Check status
            status = request("GET", f"/project/{project_id}/status")
            state = "RUNNING" if status and status.get('is_running') else "IDLE"
            
            # Check files via API (using the files endpoint we verified earlier)
            files_resp = request("GET", f"/files/tree?path=projects/{project_id}")
            
            current_files = []
            if files_resp and 'items' in files_resp:
                current_files = [f['name'] for f in files_resp['items']]
                
                # Check for new files
                new_files = set(current_files) - last_files
                if new_files:
                    for f in new_files:
                        print(f"\n   📄 [NEW ARTIFACT]: {f}")
                        if f.endswith('.md'):
                            print(f"      -> Documentation/Plan generated")
                        elif f.endswith('.py'):
                            print(f"      -> Source Code generated")
                    last_files = set(current_files)
            
            print(f"\r   ⏳ Status: {state} | Files Created: {len(current_files)} | Runtime: {int(time.time() - start_time)}s", end="", flush=True)
            time.sleep(2)
            
    except KeyboardInterrupt:
        pass
    
    print("\n\n✅ Demo Loop Complete.")
    print(f"   To view the full output, run: python api_cli.py list")
    print(f"   Then select {project_id}")

if __name__ == "__main__":
    run_demo()
