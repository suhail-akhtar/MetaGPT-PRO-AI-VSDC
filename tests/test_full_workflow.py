#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Full E2E Test: Scientific Calculator with Conversation + Sprint/Backlog
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000/v1"


async def test_scientific_calculator():
    print("=" * 60)
    print("E2E TEST: Scientific Calculator with Full Workflow")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # ==========================================
        # PHASE 1: CONVERSATION
        # ==========================================
        print("\n>>> PHASE 1: CONVERSATION <<<\n")
        
        # 1. Start Conversation
        print("[1] Starting conversation with AI Product Manager...")
        payload = {
            "initial_idea": "Build a Scientific Calculator like Windows 10 in HTML + JavaScript with full functionalities including trigonometric functions, logarithms, powers, memory functions, and history"
        }
        async with session.post(f"{BASE_URL}/conversation/start", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            data = await resp.json()
            conversation_id = data["conversation_id"]
            print(f"   Conversation ID: {conversation_id}")
            print(f"   AI Question: {data['first_question'][:150]}...")
        
        # 2. Send clarification
        print("\n[2] Clarifying requirements...")
        payload = {
            "conversation_id": conversation_id,
            "message": """It should be a web-based scientific calculator with:
- Basic operations: +, -, *, /, %, parentheses
- Scientific functions: sin, cos, tan, log, ln, sqrt, power, factorial
- Memory functions: MC, MR, M+, M-
- History panel showing previous calculations
- Degree/Radian toggle for trig functions
- Dark theme similar to Windows 10 calculator
- Keyboard input support
- Responsive design"""
        }
        async with session.post(f"{BASE_URL}/conversation/message", json=payload) as resp:
            data = await resp.json()
            print(f"   AI Response: {data['ai_response'][:150]}...")
            print(f"   Status: {data['status']}")
        
        # 3. Enhance requirements
        print("\n[3] Enhancing requirements...")
        payload = {"conversation_id": conversation_id}
        async with session.post(f"{BASE_URL}/conversation/enhance", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                prd = data["enhanced_prd"]
                print(f"   Project Name: {prd.get('project_name', 'N/A')}")
                print(f"   Core Features: {len(prd.get('core_features', []))} features")
                print(f"   User Stories: {len(prd.get('user_stories', []))} stories")
                print(f"   Platform: {prd.get('platform', 'N/A')}")
        
        # 4. Approve requirements
        print("\n[4] Approving requirements...")
        payload = {"conversation_id": conversation_id}
        async with session.post(f"{BASE_URL}/conversation/approve", json=payload) as resp:
            data = await resp.json()
            project_id = data["project_id"]
            print(f"   Project ID: {project_id}")
            print(f"   Status: {data['status']}")
        
        # 5. Get conversation history
        print("\n[5] Getting conversation history...")
        async with session.get(f"{BASE_URL}/conversation/{conversation_id}/history") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Total Messages: {len(data['messages'])}")
                print(f"   Final Status: {data['status']}")
        
        # ==========================================
        # PHASE 2: PROJECT START WITH SPRINTS
        # ==========================================
        print("\n>>> PHASE 2: PROJECT + SPRINTS <<<\n")
        
        # 6. Hire team
        print("[6] Hiring team...")
        await session.post(f"{BASE_URL}/company/hire")
        print("   Team hired!")
        
        # 7. Start project with conversation_id
        print("\n[7] Starting project (triggers task breakdown + sprints)...")
        project_name = "scientific_calculator"
        payload = {
            "requirement": "fallback",
            "conversation_id": conversation_id,
            "project_name": project_name,
            "n_round": 1
        }
        async with session.post(f"{BASE_URL}/company/run", json=payload) as resp:
            if resp.status != 200:
                print(f"   ERROR: {await resp.text()}")
            else:
                print("   Project started!")
        
        # Wait for task breakdown to complete
        print("\n[8] Waiting for task breakdown generation (15s)...")
        await asyncio.sleep(15)
        
        # ==========================================
        # PHASE 3: SPRINT & BOARD INSPECTION
        # ==========================================
        print("\n>>> PHASE 3: SPRINT & BOARD INSPECTION <<<\n")
        
        # 9. Get sprints
        print("[9] Getting sprints...")
        async with session.get(f"{BASE_URL}/project/{project_name}/sprints") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Total Sprints: {data.get('total_sprints', 0)}")
                print(f"   Current Sprint: {data.get('current_sprint', 'N/A')}")
                for s in data.get('sprints', [])[:3]:
                    print(f"   - {s.get('name', 'Sprint')}: {len(s.get('tasks', []))} tasks")
            else:
                print(f"   Response: {resp.status}")
        
        # 10. Get backlog
        print("\n[10] Getting backlog...")
        async with session.get(f"{BASE_URL}/project/{project_name}/backlog") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Stories: {len(data.get('stories', []))}")
                print(f"   Total Points: {data.get('total_points', 0)}")
            else:
                print(f"   Response: {resp.status}")
        
        # 11. Get board
        print("\n[11] Getting Kanban board...")
        async with session.get(f"{BASE_URL}/project/{project_name}/board") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Todo: {len(data.get('todo', []))} tasks")
                print(f"   In Progress: {len(data.get('in_progress', []))} tasks")
                print(f"   Done: {len(data.get('done', []))} tasks")
                print(f"   Blocked: {len(data.get('blocked', []))} tasks")
            else:
                print(f"   Response: {resp.status}")
        
        # 12. Get metrics
        print("\n[12] Getting metrics...")
        async with session.get(f"{BASE_URL}/project/{project_name}/metrics") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Progress: {data.get('progress_percent', 0)}%")
                print(f"   Points Completed: {data.get('points_completed', 0)}")
                print(f"   Points Remaining: {data.get('points_remaining', 0)}")
                print(f"   Blocked: {data.get('blocked_count', 0)}")
            else:
                print(f"   Response: {resp.status}")
        
        # 13. Move a task
        print("\n[13] Testing task move...")
        async with session.get(f"{BASE_URL}/project/{project_name}/board") as resp:
            if resp.status == 200:
                data = await resp.json()
                todo_tasks = data.get('todo', [])
                if todo_tasks:
                    task = todo_tasks[0]
                    task_id = task.get('id') if isinstance(task, dict) else task
                    print(f"   Moving task {task_id} to in_progress...")
                    move_payload = {"task_id": task_id, "new_status": "in_progress"}
                    async with session.post(f"{BASE_URL}/project/{project_name}/task/move", json=move_payload) as move_resp:
                        if move_resp.status == 200:
                            move_data = await move_resp.json()
                            print(f"   Result: {move_data.get('message', 'Moved')}")
                        else:
                            print(f"   Move failed: {await move_resp.text()}")
        
        # 14. Stop project
        print("\n[14] Stopping project...")
        await session.post(f"{BASE_URL}/company/stop")
        print("   Project stopped.")
        
    print("\n" + "=" * 60)
    print("E2E TEST COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_scientific_calculator())
