import urllib.request
import urllib.parse
import json
import time
import sys

BASE_URL = "http://localhost:8088/v1"

def request(method, endpoint, data=None):
    url = BASE_URL + endpoint
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.data = json_data
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"Request failed: {e}")
        print(e.read().decode('utf-8'))
        return None

def main():
    print("🚀 STARTING DEEP INTEGRATION DEMO")
    print("---------------------------------")
    
    # 1. Start Conversation
    print("1️⃣  Starting Conversation...")
    idea = (
        "Build a simple Flappy Bird clone using Python and Pygame. "
        "Requirements: 1. Bird jumps on spacebar. 2. Pipes move left. 3. Collision ends game. 4. Score counts passed pipes. "
        "No menu, no sound, no settings. Just the core gameplay loop. "
        "Do not ask clarifying questions, just write the PRD and code."
    )
    data = request("POST", "/conversation/start", {"initial_idea": idea})
    if not data: return
    conv_id = data['conversation_id']
    print(f"   Project ID: {conv_id}")
    
    # 2. Approve Immediately (Trigger Execution)
    print("\n2️⃣  Approving Requirements...")
    data = request("POST", "/conversation/approve", {"conversation_id": conv_id})
    if not data: return
    proj_id = data['project_id']
    print(f"   Project Created: {proj_id}")
    
    # 3. Monitor for PRD Pause
    print(f"\n3️⃣  Monitoring {proj_id} for PRD Generation (Expect Pause)...")
    paused = False
    for i in range(60):
        # We can't easily check 'paused' status via API without the edit, 
        # so we will check if it goes IDLE quickly (meaning it hit the break)
        status = request("GET", f"/project/{proj_id}/status")
        print(f"   [{i}s] Status: {status.get('status')} | Running: {status.get('is_running')}")
        
        if status.get('status') == 'idle' and i > 5:
            # It went idle. In the old version, this meant it finished or crashed.
            # In the new version, it means it paused (because PRD takes ~1 round).
            print("   ⚠️  System went IDLE. Checking if it was a Pause...")
            paused = True
            break
        
        time.sleep(2)
        
    if not paused:
        print("❌  Timed out waiting for pause.")
        return

    print("\n4️⃣  System Paused! Simulating User Review...")
    time.sleep(2)
    
    # 4. Resume
    print(f"\n5️⃣  Approving PRD (Resuming Check)...")
    data = request("POST", f"/project/{proj_id}/resume", {})
    if data:
        print(f"   ✅  Resume Signal Sent: {data}")
    
    # 5. Monitor for Code Generation
    print(f"\n6️⃣  Monitoring for Code Generation...")
    for i in range(60):
        status = request("GET", f"/project/{proj_id}/status")
        print(f"   [{i}s] Status: {status.get('status')}")
        
        # Check files
        files = request("GET", f"/files/tree?path=projects/{proj_id}")
        if files and 'children' in files:
            file_names = [f['name'] for f in files['children']]
            print(f"   Files: {shorten(file_names)}")
            if "docs" in file_names and "resources" in file_names:
                print("   ✅  Docs generated.")
            # If we see python files or subfolders with code, success
        
        if status.get('status') == 'idle':
            print("   ℹ️  System Idle (Cycle Complete)")
            break
            
        time.sleep(2)

def shorten(lst):
    return [x[:10] for x in lst]

if __name__ == "__main__":
    main()
