#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
E2E Test for Conversational Requirements Engineering
"""
import asyncio
import aiohttp

BASE_URL = "http://localhost:8000/v1"


async def test_conversation_flow():
    print(">>> E2E Test: Conversational Requirements Engineering <<<\n")
    
    async with aiohttp.ClientSession() as session:
        # 1. Start Conversation
        print("[1] Starting conversation...")
        payload = {"initial_idea": "Build a simple todo app"}
        async with session.post(f"{BASE_URL}/conversation/start", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            data = await resp.json()
            conversation_id = data["conversation_id"]
            print(f"Conversation ID: {conversation_id}")
            print(f"AI Question: {data['first_question'][:200]}...")
        
        # 2. Send User Response
        print("\n[2] Sending user response...")
        payload = {
            "conversation_id": conversation_id,
            "message": "It should be a CLI app with Python. Basic add/remove/list tasks."
        }
        async with session.post(f"{BASE_URL}/conversation/message", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            data = await resp.json()
            print(f"AI Response: {data['ai_response'][:200]}...")
            print(f"Status: {data['status']}")
        
        # 3. Trigger Enhancement
        print("\n[3] Enhancing requirements...")
        payload = {"conversation_id": conversation_id}
        async with session.post(f"{BASE_URL}/conversation/enhance", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            data = await resp.json()
            prd = data["enhanced_prd"]
            print(f"Project Name: {prd['project_name']}")
            print(f"Core Features: {prd['core_features']}")
            print(f"Platform: {prd['platform']}")
        
        # 4. Approve Requirements
        print("\n[4] Approving requirements...")
        payload = {"conversation_id": conversation_id}
        async with session.post(f"{BASE_URL}/conversation/approve", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            data = await resp.json()
            project_id = data["project_id"]
            print(f"Project ID: {project_id}")
            print(f"Status: {data['status']}")
        
        # 5. Get Conversation History
        print("\n[5] Retrieving conversation history...")
        async with session.get(f"{BASE_URL}/conversation/{conversation_id}/history") as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            data = await resp.json()
            print(f"Messages Count: {len(data['messages'])}")
            print(f"Final Status: {data['status']}")
        
        # 6. Start Project with Approved Requirements
        print("\n[6] Starting project with approved requirements...")
        # First hire a team
        await session.post(f"{BASE_URL}/company/hire")
        
        payload = {
            "requirement": "fallback text",  # Should be overridden
            "conversation_id": conversation_id,
            "project_name": "todo_app_test",
            "n_round": 1
        }
        async with session.post(f"{BASE_URL}/company/run", json=payload) as resp:
            if resp.status != 200:
                print(f"ERROR: {await resp.text()}")
                return
            print(f"Project started with conversation_id!")
        
        # Stop project
        await asyncio.sleep(2)
        await session.post(f"{BASE_URL}/company/stop")
        
    print("\n>>> E2E Test PASSED <<<")


if __name__ == "__main__":
    asyncio.run(test_conversation_flow())
