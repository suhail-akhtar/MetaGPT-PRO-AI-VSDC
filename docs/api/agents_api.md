# Agent Collaboration API

## Overview

The Agent Collaboration API enables inter-agent messaging, approval workflows, and client injection.

**Base URL:** `http://localhost:8000/v1/agents`

---

## Endpoints

### Get All Conversations

**`GET /conversations`**

```json
{
  "threads": [
    {
      "id": "thread_82bcee6fa516",
      "topic": "Design complete for Calculator...",
      "participants": ["Bob", "Alice"],
      "status": "active",
      "messages": [...]
    }
  ],
  "active_count": 3
}
```

---

### Get Thread Details

**`GET /thread/{thread_id}`**

```json
{
  "thread_id": "thread_82bcee6fa516",
  "topic": "Design complete for Calculator module",
  "participants": ["Bob", "Alice"],
  "messages": [
    {
      "id": "msg_3046a1745faf",
      "from_agent": "Bob",
      "to_agent": "Alice",
      "content": "Design complete. Please review.",
      "message_type": "approval_request",
      "timestamp": "2026-01-10T02:22:45"
    }
  ],
  "status": "active"
}
```

---

### Send Message

**`POST /message`**

```json
// Request
{
  "from_agent": "Bob",
  "to_agent": "Alice",
  "content": "Design complete. Please review and approve.",
  "message_type": "approval_request",
  "requires_response": true,
  "context": { "module": "calculator", "sprint": 1 }
}

// Response
{
  "message_id": "msg_3046a1745faf",
  "thread_id": "thread_82bcee6fa516",
  "delivered": true
}
```

**Message Types:**
- `question` - Ask a question
- `answer` - Reply to question
- `approval_request` - Request approval (creates approval gate)
- `approval_response` - Approve/reject response
- `clarification` - Request clarification
- `handoff` - Handoff between agents
- `notification` - General notification
- `client_message` - Message from client

---

### Get Agent Inbox

**`GET /{agent_name}/inbox`**

```json
{
  "agent_name": "Alice",
  "unread": 2,
  "messages": [
    {
      "id": "msg_3046a1745faf",
      "from_agent": "Bob",
      "content": "Design complete. Please review.",
      "read": false
    }
  ]
}
```

---

### Approve/Reject Request

**`POST /approve`**

```json
// Request
{
  "message_id": "msg_3046a1745faf",
  "approved": true,
  "notes": "Design approved. Proceed with implementation."
}

// Response
{
  "approval_id": "approval_abc123",
  "status": "approved",
  "workflow_resumed": true
}
```

---

### Get Pending Approvals

**`GET /pending?agent=Alice`**

```json
{
  "pending_count": 1,
  "approvals": [
    {
      "id": "approval_abc123",
      "from_agent": "Bob",
      "to_agent": "Alice",
      "description": "Design complete. Please review.",
      "status": "pending"
    }
  ]
}
```

---

### WebSocket: Collaboration Stream

**`WS /stream`**

Connect for real-time collaboration events.

**Events:**
```json
// Initial state
{ "type": "initial_state", "active_threads": 3, "pending_approvals": 1 }

// New message
{ "type": "new_message", "message": {...}, "thread_id": "thread_xyz" }

// Approval requested
{ "type": "approval_requested", "approval_id": "approval_abc", "from": "Bob" }

// Approval granted
{ "type": "approval_granted", "approval_id": "approval_abc", "approved": true }
```

---

## Client Injection

Clients can inject messages into agent conversations:

```json
POST /message
{
  "from_agent": "Client",
  "to_agent": "Alice",
  "content": "Can we add dark mode to the calculator?",
  "message_type": "client_message",
  "context": { "inject_at": "current_sprint" }
}
```

The receiving agent (Alice) will see this in their inbox and can respond.

---

## Agents

| Agent | Role |
|-------|------|
| Alice | Product Manager |
| Bob | Architect |
| Alex | Engineer |
| Client | External user |
