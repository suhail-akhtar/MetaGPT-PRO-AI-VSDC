# Bug Tracking API

## Overview

Auto-detect bugs from test failures, track bug lifecycle, integrate with agent workflow.

**Base URL:** `http://localhost:8000/v1/project/{project_id}`

---

## Endpoints

### List All Bugs

**`GET /bugs?status=open`**

```json
{
  "bugs": [
    {
      "id": "BUG-82ABF7",
      "title": "Login button not working",
      "severity": "high",
      "priority": "P1",
      "status": "assigned",
      "assigned_to": "Alex"
    }
  ],
  "open_count": 5,
  "critical_count": 2,
  "total": 12
}
```

---

### Report Bug Manually

**`POST /bug/report`**

```json
// Request
{
  "title": "Login fails on Safari",
  "description": "Clicking login button does nothing",
  "severity": "high",
  "file_path": "src/auth/login.py",
  "error_trace": "TypeError: Cannot read property..."
}

// Response
{
  "bug_id": "BUG-82ABF7",
  "priority": "P1",
  "assigned_to": "Alex"
}
```

---

### Get Bug Details

**`GET /bug/{bug_id}`**

```json
{
  "bug": {
    "id": "BUG-82ABF7",
    "title": "Login fails",
    "status": "in_progress",
    "assigned_to": "Alex",
    "retry_count": 1
  },
  "history": [
    { "action": "created", "timestamp": "..." },
    { "action": "assigned", "new_value": "Alex" },
    { "action": "status_change", "old_value": "open", "new_value": "in_progress" }
  ]
}
```

---

### Assign Bug

**`POST /bug/{bug_id}/assign`**

```json
// Request
{ "agent": "Alex" }

// Response
{ "assigned": true, "agent": "Alex" }
```

---

### Update Status

**`PATCH /bug/{bug_id}/status`**

```json
// Request
{ "status": "fixed", "notes": "Added null check" }

// Response
{ "updated": true, "status": "fixed" }
```

**Status values:** `open`, `assigned`, `in_progress`, `fixed`, `verified`, `closed`, `wont_fix`

---

### Bug Metrics

**`GET /metrics/bugs`**

```json
{
  "total_bugs": 12,
  "open": 3,
  "fixed": 9,
  "avg_fix_time_hours": 4.2,
  "by_severity": {
    "critical": 1,
    "high": 2,
    "medium": 5,
    "low": 4
  },
  "by_sprint": {
    "sprint_1": 5,
    "sprint_2": 7
  }
}
```

---

### Auto-Detect from Test Output

**`POST /bug/detect?test_output=...`**

Parses pytest/unittest output and creates bugs.

```json
// Response
{
  "detected": 3,
  "bug_ids": ["BUG-AE448A", "BUG-904CDE", "BUG-2672EF"]
}
```

---

### WebSocket: Bug Events

**`WS /bugs/stream`**

```json
// Initial state
{ "type": "initial_state", "total_bugs": 12, "open_bugs": 5 }

// Bug created
{ "type": "bug_created", "bug_id": "BUG-123", "severity": "critical" }

// Bug fixed
{ "type": "bug_fixed", "bug_id": "BUG-123" }
```

---

## Severity & Priority

| Severity | Priority | Action |
|----------|----------|--------|
| critical | P0 | Interrupt current work |
| high | P1 | Add to current sprint |
| medium | P2 | Next sprint |
| low | P3 | Backlog |

---

## Auto-Assignment

| Bug Type | Assigned To |
|----------|-------------|
| Code bugs | Alex (Engineer) |
| Design flaws | Bob (Architect) |
| Requirement issues | Alice (PM) |
