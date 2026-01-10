#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MetaGPT-PRO API CLI Client
Use this tool to interact with the backend API directly, bypassing the frontend.
"""
import sys
import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8088/v1"

def print_ai(msg):
    print(f"\n\033[92m[AI PM]:\033[0m {msg}\n")

def print_sys(msg):
    print(f"\033[93m[SYSTEM]:\033[0m {msg}")

def _request(method, endpoint, data=None):
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
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        try:
            err_body = e.read().decode('utf-8')
            print(f"Server response: {err_body}")
        except:
            pass
        raise
    except urllib.error.URLError as e:
        print(f"Connection Failed: {e.reason}")
        raise

def start_conversation():
    print("\n=== MetaGPT-PRO CLI Project Creator ===\n")
    idea = input("Enter your project idea: ").strip()
    if not idea:
        return

    try:
        data = _request("POST", "/conversation/start", {"initial_idea": idea})
        
        conv_id = data["conversation_id"]
        print_sys(f"Conversation started (ID: {conv_id})")
        print_ai(data["message"])
        
        conversation_loop(conv_id)
        
    except Exception:
        pass

def conversation_loop(conv_id):
    while True:
        user_input = input("\033[94m[You]:\033[0m ").strip()
        if not user_input:
            continue
            
        if user_input.lower() in ["exit", "quit"]:
            break

        if user_input.lower() == "/approve":
            approve_project(conv_id)
            break

        try:
            data = _request("POST", "/conversation/message", {
                "conversation_id": conv_id,
                "content": user_input
            })
            
            print_ai(data["message"])
            
            if data.get("require_approval"):
                print_sys("The requirements seem complete. Type '/approve' to start the project.")
                
        except Exception:
            pass

def approve_project(conv_id):
    print_sys("Approving requirements...")
    try:
        data = _request("POST", "/conversation/approve", {"conversation_id": conv_id})
        
        project_id = data["project_id"]
        print_sys(f"Project Approved! ID: {project_id}")
        print_sys("Development started in background.")
        
        monitor_project(project_id)
        
    except Exception:
        pass

def monitor_project(project_id):
    print("\n=== Monitoring Project Status (Ctrl+C to stop) ===\n")
    try:
        while True:
            try:
                stats = _request("GET", f"/project/{project_id}/status")
                status = "RUNNING" if stats.get("is_running") else "IDLE"
                print(f"\rProject Status: {status} | Agent Activity: Check Docker Logs", end="", flush=True)
            except:
                print(f"\rStatus Check Failed", end="", flush=True)
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped monitoring.")


def select_project():
    try:
        projects = _request("GET", "/projects")
        if not projects:
            print("No projects found.")
            return

        print("\n=== Select a Project ===")
        for i, p in enumerate(projects):
            status_icon = "🟢" if p['status'] == 'active' else "⚪"
            print(f"{i+1}. {status_icon} {p['name']} ({p['id']})")
        
        choice = input("\nEnter number (or 0 to cancel): ").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(projects):
            return
            
        selected = projects[int(choice)-1]
        project_menu(selected['id'], selected['name'])
        
    except Exception as e:
        print(f"Error fetching projects: {e}")

def project_menu(project_id, project_name):
    while True:
        print(f"\n=== Managing: {project_name} ({project_id}) ===")
        print("1. View Status")
        print("2. Chat with Team (PM)")
        print("3. View Board Tasks")
        print("4. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            try:
                stats = _request("GET", f"/project/{project_id}/status")
                status = "RUNNING" if stats.get("is_running") else "IDLE"
                print(f"\nProject Status: {status}")
                if status == "RUNNING":
                    print("Tip: Check Docker logs for detailed agent activity.")
            except:
                print("Failed to get status.")
        
        elif choice == "2":
            # Resume conversation logic
            # We need to find the conversation ID for this project. 
            # For now, we assume convention project_id = "proj_" + conv_id
            # So conv_id = "conv_" + project_id.replace("proj_", "")
            # This is a bit hacky but fits the current ID generation logic.
            conv_id = project_id.replace("proj_", "conv_")
            print_sys(f"Entering chat for {project_id}...")
            conversation_loop(conv_id)
            
        elif choice == "3":
            try:
                board = _request("GET", f"/project/{project_id}/board")
                print("\n--- Project Board ---")
                cols = ["todo", "in_progress", "review", "testing", "done"]
                for col in cols:
                    tasks = board.get(col, [])
                    print(f"\n[{col.upper()}]: {len(tasks)} tasks")
                    for t in tasks:
                        # Task object might be detailed or just ID depending on API
                        title = t.get('title', 'Untitled') if isinstance(t, dict) else t
                        print(f"  - {title}")
            except:
                print("Failed to fetch board.")
                
        elif choice == "4":
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        # ... (keep existing list logic if needed, or redirect to menu)
        pass
        
    while True:
        print("\n=== MetaGPT-PRO CLI ===\n")
        print("1. Create New Project")
        print("2. Manage Existing Project")
        print("3. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            start_conversation()
        elif choice == "2":
            select_project()
        elif choice == "3":
            break

