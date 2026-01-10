#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
E2E Test for Agent Collaboration Layer (Phase 3)
"""
import asyncio
import aiohttp

BASE_URL = "http://localhost:8000/v1"


async def test_agent_collaboration():
    print("=" * 60)
    print("E2E TEST: Agent Collaboration Layer")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Send message from Bob to Alice
        print("\n[1] Bob sends design approval request to Alice...")
        payload = {
            "from_agent": "Bob",
            "to_agent": "Alice",
            "content": "Design complete for Calculator module. Please review and approve.",
            "message_type": "approval_request",
            "requires_response": True,
            "context": {"module": "calculator", "sprint": 1}
        }
        async with session.post(f"{BASE_URL}/agents/message", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                msg_id = data["message_id"]
                thread_id = data["thread_id"]
                print(f"   Message ID: {msg_id}")
                print(f"   Thread ID: {thread_id}")
            else:
                print(f"   ERROR: {await resp.text()}")
                return
        
        # 2. Get Alice's inbox
        print("\n[2] Checking Alice's inbox...")
        async with session.get(f"{BASE_URL}/agents/Alice/inbox") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Unread: {data['unread']}")
                print(f"   Total: {len(data['messages'])}")
        
        # 3. Alice responds
        print("\n[3] Alice responds with question...")
        payload = {
            "from_agent": "Alice",
            "to_agent": "Bob",
            "content": "Does the calculator need scientific functions?",
            "message_type": "question"
        }
        async with session.post(f"{BASE_URL}/agents/message", json=payload) as resp:
            data = await resp.json()
            print(f"   Message sent: {data['message_id']}")
        
        # 4. Bob answers
        print("\n[4] Bob answers...")
        payload = {
            "from_agent": "Bob",
            "to_agent": "Alice",
            "content": "Yes, basic trig functions (sin, cos, tan) and logarithms.",
            "message_type": "answer"
        }
        async with session.post(f"{BASE_URL}/agents/message", json=payload) as resp:
            data = await resp.json()
            print(f"   Message sent: {data['message_id']}")
        
        # 5. Alice approves
        print("\n[5] Alice approves...")
        payload = {
            "message_id": msg_id,
            "approved": True,
            "notes": "Design approved. Proceed with implementation."
        }
        async with session.post(f"{BASE_URL}/agents/approve", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Status: {data['status']}")
                print(f"   Workflow resumed: {data['workflow_resumed']}")
            else:
                print(f"   Response: {resp.status}")
        
        # 6. Get all conversations
        print("\n[6] Getting all conversations...")
        async with session.get(f"{BASE_URL}/agents/conversations") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Total threads: {len(data['threads'])}")
                print(f"   Active: {data['active_count']}")
        
        # 7. Client injects message
        print("\n[7] Client sends mid-project question...")
        payload = {
            "from_agent": "Client",
            "to_agent": "Alice",
            "content": "Can we add a dark mode toggle to the calculator?",
            "message_type": "client_message",
            "context": {"inject_at": "current_sprint"}
        }
        async with session.post(f"{BASE_URL}/agents/message", json=payload) as resp:
            data = await resp.json()
            print(f"   Client message sent: {data['message_id']}")
        
        # 8. Get pending approvals
        print("\n[8] Getting pending approvals...")
        async with session.get(f"{BASE_URL}/agents/pending") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Pending: {data['pending_count']}")
        
    print("\n" + "=" * 60)
    print("E2E TEST COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_agent_collaboration())
