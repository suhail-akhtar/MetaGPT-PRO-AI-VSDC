#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
E2E Test for Document Versioning (Phase 5)
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000/v1"
PROJECT_ID = "test_version_project"


async def test_versioning():
    print("=" * 60)
    print("E2E TEST: Document Versioning & History")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Create first version of PRD
        print("\n[1] Creating PRD v1...")
        content1 = json.dumps({
            "title": "Calculator App",
            "features": ["addition", "subtraction"],
            "user_stories": ["As a user, I want to add numbers"]
        })
        async with session.post(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/snapshot",
            params={
                "doc_id": "main_prd",
                "content": content1,
                "changed_by": "Alice",
                "reason": "Initial PRD creation"
            }
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Version: {data['version']}")
            else:
                print(f"   ERROR: {await resp.text()}")
                return
        
        # 2. Create second version with changes
        print("\n[2] Creating PRD v2 with new feature...")
        content2 = json.dumps({
            "title": "Calculator App",
            "features": ["addition", "subtraction", "multiplication"],
            "user_stories": [
                "As a user, I want to add numbers",
                "As a user, I want to multiply numbers"
            ]
        })
        async with session.post(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/snapshot",
            params={
                "doc_id": "main_prd",
                "content": content2,
                "changed_by": "Client",
                "reason": "Added multiplication feature"
            }
        ) as resp:
            data = await resp.json()
            print(f"   Version: {data['version']}")
        
        # 3. Create third version
        print("\n[3] Creating PRD v3 with division...")
        content3 = json.dumps({
            "title": "Calculator App Pro",
            "features": ["addition", "subtraction", "multiplication", "division"],
            "user_stories": [
                "As a user, I want to add numbers",
                "As a user, I want to multiply numbers",
                "As a user, I want to divide numbers"
            ]
        })
        async with session.post(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/snapshot",
            params={
                "doc_id": "main_prd",
                "content": content3,
                "changed_by": "Alice",
                "reason": "Added division and renamed app"
            }
        ) as resp:
            data = await resp.json()
            print(f"   Version: {data['version']}")
        
        # 4. Get version list
        print("\n[4] Getting version list...")
        async with session.get(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/versions",
            params={"doc_id": "main_prd"}
        ) as resp:
            data = await resp.json()
            print(f"   Versions: {data['versions']}")
            print(f"   Current: {data['current']}")
            print(f"   Total: {data['total']}")
        
        # 5. Get specific version
        print("\n[5] Getting v2 details...")
        async with session.get(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/version/2",
            params={"doc_id": "main_prd"}
        ) as resp:
            data = await resp.json()
            print(f"   Version: {data['version']}")
            print(f"   Changed by: {data['changed_by']}")
            print(f"   Reason: {data['change_reason']}")
        
        # 6. Compare v1 vs v3
        print("\n[6] Comparing v1 vs v3...")
        async with session.get(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/diff",
            params={"doc_id": "main_prd", "v1": 1, "v2": 3}
        ) as resp:
            data = await resp.json()
            print(f"   Summary: {data['summary']}")
            print(f"   Added: {len(data['added'])}")
            print(f"   Modified: {len(data['modified'])}")
        
        # 7. Rollback to v1
        print("\n[7] Rolling back to v1...")
        async with session.post(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/rollback",
            params={"doc_id": "main_prd"},
            json={"version": 1, "reason": "Client wants original simple version"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Rolled back: {data['rolled_back']}")
                print(f"   From v{data['from_version']} to content of v{data['to_version']}")
                print(f"   New current version: {data['new_current']}")
            else:
                print(f"   Response: {resp.status}")
        
        # 8. Verify rollback created v4
        print("\n[8] Verifying rollback created v4...")
        async with session.get(
            f"{BASE_URL}/project/{PROJECT_ID}/document/prd/versions",
            params={"doc_id": "main_prd"}
        ) as resp:
            data = await resp.json()
            print(f"   Versions: {data['versions']}")
            print(f"   Current: {data['current']}")
        
        # 9. Get project history
        print("\n[9] Getting project history...")
        async with session.get(f"{BASE_URL}/project/{PROJECT_ID}/history") as resp:
            data = await resp.json()
            print(f"   Total changes: {data['total_changes']}")
            for entry in data['timeline'][:3]:
                print(f"   - {entry['document_id']} v{entry['version']} by {entry['changed_by']}")
    
    print("\n" + "=" * 60)
    print("E2E TEST COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_versioning())
