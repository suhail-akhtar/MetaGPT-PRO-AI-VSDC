#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
E2E Test for Bug Tracking System (Phase 4)
"""
import asyncio
import aiohttp

BASE_URL = "http://localhost:8000/v1"
PROJECT_ID = "test_bug_project"


async def test_bug_tracking():
    print("=" * 60)
    print("E2E TEST: Bug Tracking System")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Report a bug manually
        print("\n[1] Reporting bug manually...")
        payload = {
            "title": "Login button not working",
            "description": "Clicking login button does nothing on Safari",
            "severity": "high",
            "file_path": "src/auth/login.py",
            "error_trace": "TypeError: Cannot read property 'submit' of undefined"
        }
        async with session.post(f"{BASE_URL}/project/{PROJECT_ID}/bug/report", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                bug_id = data["bug_id"]
                print(f"   Bug ID: {bug_id}")
                print(f"   Priority: {data['priority']}")
                print(f"   Assigned to: {data['assigned_to']}")
            else:
                print(f"   ERROR: {await resp.text()}")
                return
        
        # 2. Get bug details
        print(f"\n[2] Getting bug details for {bug_id}...")
        async with session.get(f"{BASE_URL}/project/{PROJECT_ID}/bug/{bug_id}") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Status: {data['bug']['status']}")
                print(f"   Severity: {data['bug']['severity']}")
                print(f"   History entries: {len(data['history'])}")
        
        # 3. Update status to in_progress
        print(f"\n[3] Setting status to in_progress...")
        payload = {"status": "in_progress", "notes": "Started working on fix"}
        async with session.patch(f"{BASE_URL}/project/{PROJECT_ID}/bug/{bug_id}/status", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Updated: {data['updated']}")
                print(f"   New status: {data['status']}")
        
        # 4. Report another bug (critical)
        print("\n[4] Reporting critical bug...")
        payload = {
            "title": "Data corruption on save",
            "description": "User data is corrupted when saving profile",
            "severity": "critical",
            "file_path": "src/data/user_store.py"
        }
        async with session.post(f"{BASE_URL}/project/{PROJECT_ID}/bug/report", json=payload) as resp:
            data = await resp.json()
            critical_bug_id = data["bug_id"]
            print(f"   Bug ID: {critical_bug_id}")
            print(f"   Priority: {data['priority']}")
        
        # 5. Get all bugs
        print(f"\n[5] Getting all bugs for project...")
        async with session.get(f"{BASE_URL}/project/{PROJECT_ID}/bugs") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Total bugs: {data['total']}")
                print(f"   Open bugs: {data['open_count']}")
                print(f"   Critical bugs: {data['critical_count']}")
        
        # 6. Mark first bug as fixed
        print(f"\n[6] Marking {bug_id} as fixed...")
        payload = {"status": "fixed", "notes": "Fixed null check in button handler"}
        async with session.patch(f"{BASE_URL}/project/{PROJECT_ID}/bug/{bug_id}/status", json=payload) as resp:
            data = await resp.json()
            print(f"   Status: {data['status']}")
        
        # 7. Get bug metrics
        print(f"\n[7] Getting bug metrics...")
        async with session.get(f"{BASE_URL}/project/{PROJECT_ID}/metrics/bugs") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Total: {data['total_bugs']}")
                print(f"   Open: {data['open']}")
                print(f"   Fixed: {data['fixed']}")
                print(f"   By severity: {data['by_severity']}")
        
        # 8. Test auto-detection from test output
        print(f"\n[8] Testing bug auto-detection from pytest output...")
        test_output = """
============================= test session starts ==============================
FAILED tests/test_calc.py::test_divide - ZeroDivisionError: division by zero
FAILED tests/test_auth.py::test_login - AssertionError: Expected 200, got 401
ERROR tests/test_db.py::test_connection
============================= 3 failed, 10 passed ==============================
        """
        async with session.post(
            f"{BASE_URL}/project/{PROJECT_ID}/bug/detect",
            params={"test_output": test_output}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"   Detected: {data['detected']} bugs")
                print(f"   Bug IDs: {data['bug_ids']}")
            else:
                print(f"   Response: {resp.status}")
    
    print("\n" + "=" * 60)
    print("E2E TEST COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_bug_tracking())
