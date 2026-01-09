#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
E2E Test for Sprint/Backlog System (Phase 2)
"""
import asyncio
import aiohttp

BASE_URL = "http://localhost:8000/v1"


async def test_sprint_backlog_system():
    print(">>> E2E Test: Sprint/Backlog System <<<\n")
    
    async with aiohttp.ClientSession() as session:
        # 1. Start a conversation and approve requirements
        print("[1] Starting conversation...")
        payload = {"initial_idea": "Build a calculator app with +, -, *, / operations"}
        async with session.post(f"{BASE_URL}/conversation/start", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            data = await resp.json()
            conversation_id = data["conversation_id"]
            print(f"Conversation ID: {conversation_id}")
        
        # Send clarification
        print("\n[2] Clarifying requirements...")
        payload = {
            "conversation_id": conversation_id,
            "message": "CLI-based Python app. Support basic arithmetic."
        }
        async with session.post(f"{BASE_URL}/conversation/message", json=payload) as resp:
            await resp.json()
        
        # Approve
        print("\n[3] Approving requirements...")
        payload = {"conversation_id": conversation_id}
        async with session.post(f"{BASE_URL}/conversation/approve", json=payload) as resp:
            data = await resp.json()
            print(f"Project ID: {data['project_id']}")
        
        # Hire team first
        await session.post(f"{BASE_URL}/company/hire")
        
        # Start project with approved requirements
        print("\n[4] Starting project (triggers task breakdown)...")
        project_id = f"calc_app_test"
        payload = {
            "requirement": "fallback",
            "conversation_id": conversation_id,
            "project_name": project_id,
            "n_round": 1
        }
        async with session.post(f"{BASE_URL}/company/run", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR starting project: {await resp.text()}")
                return
            print("Project started!")
        
        # Wait for task breakdown to complete
        await asyncio.sleep(10)
        
        # 5. Get sprints
        print("\n[5] Getting sprints...")
        async with session.get(f"{BASE_URL}/project/{project_id}/sprints") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"Total Sprints: {data.get('total_sprints', 0)}")
                print(f"Current Sprint: {data.get('current_sprint', 1)}")
            else:
                print(f"Sprints not ready: {await resp.text()}")
        
        # 6. Get backlog
        print("\n[6] Getting backlog...")
        async with session.get(f"{BASE_URL}/project/{project_id}/backlog") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"Stories: {len(data.get('stories', []))}")
                print(f"Total Points: {data.get('total_points', 0)}")
            else:
                print(f"Backlog not ready: {await resp.text()}")
        
        # 7. Get board
        print("\n[7] Getting Kanban board...")
        async with session.get(f"{BASE_URL}/project/{project_id}/board") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"Todo: {len(data.get('todo', []))} tasks")
                print(f"In Progress: {len(data.get('in_progress', []))} tasks")
                print(f"Done: {len(data.get('done', []))} tasks")
            else:
                print(f"Board not ready: {await resp.text()}")
        
        # 8. Get metrics
        print("\n[8] Getting metrics...")
        async with session.get(f"{BASE_URL}/project/{project_id}/metrics") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"Progress: {data.get('progress_percent', 0)}%")
                print(f"Points Remaining: {data.get('points_remaining', 0)}")
            else:
                print(f"Metrics not ready: {await resp.text()}")
        
        # 9. Move a task
        print("\n[9] Moving task to in_progress...")
        async with session.get(f"{BASE_URL}/project/{project_id}/board") as resp:
            if resp.status == 200:
                data = await resp.json()
                todo_tasks = data.get('todo', [])
                if todo_tasks:
                    task_id = todo_tasks[0]['id']
                    move_payload = {"task_id": task_id, "new_status": "in_progress"}
                    async with session.post(f"{BASE_URL}/project/{project_id}/task/move", json=move_payload) as move_resp:
                        if move_resp.status == 200:
                            print(f"Task {task_id} moved to in_progress")
                        else:
                            print(f"Move failed: {await move_resp.text()}")
        
        # Stop project
        await session.post(f"{BASE_URL}/company/stop")
        
    print("\n>>> E2E Test COMPLETED <<<")


if __name__ == "__main__":
    asyncio.run(test_sprint_backlog_system())
