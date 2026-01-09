# Conversational Requirements Engineering API

## Overview

The Conversation API enables interactive pre-project requirement discussions with an AI Product Manager before the standard MetaGPT workflow begins.

**Base URL:** `http://localhost:8000/v1/conversation`

---

## Endpoints

### Start Conversation

**`POST /start`**

Start a new conversation session with the AI Product Manager.

**Request:**
```json
{
  "initial_idea": "Build a simple todo app"
}
```

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "first_question": "Hi! A todo app sounds great. Let me ask a few questions...",
  "status": "active"
}
```

---

### Send Message

**`POST /message`**

Send a message to the AI and receive a response.

**Request:**
```json
{
  "conversation_id": "conv_abc123",
  "message": "It should be a CLI app with Python"
}
```

**Response:**
```json
{
  "ai_response": "Got it! A Python CLI todo app...",
  "enhanced_requirements": { ... },
  "status": "active",
  "requires_approval": false
}
```

---

### Enhance Requirements

**`POST /enhance`**

Trigger AI enhancement of current requirements.

**Request:**
```json
{
  "conversation_id": "conv_abc123"
}
```

**Response:**
```json
{
  "enhanced_prd": {
    "project_name": "todo_app",
    "core_features": ["Add tasks", "Remove tasks", "List tasks"],
    "user_stories": ["As a user, I want to add tasks..."],
    "platform": "CLI",
    "programming_language": "Python"
  },
  "clarifying_questions": []
}
```

---

### Approve Requirements

**`POST /approve`**

Lock requirements and mark as ready for development.

**Request:**
```json
{
  "conversation_id": "conv_abc123"
}
```

**Response:**
```json
{
  "project_id": "proj_abc123",
  "status": "approved",
  "message": "Requirements approved. Development can now start."
}
```

---

### Get History

**`GET /{conversation_id}/history`**

Retrieve full conversation history.

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "messages": [
    {"role": "user", "content": "Build a todo app", "timestamp": "..."},
    {"role": "assistant", "content": "Great idea! Let me ask...", "timestamp": "..."}
  ],
  "status": "approved",
  "enhanced_requirements": { ... }
}
```

---

## Integration with Project Run

Use `conversation_id` when starting a project to use pre-approved requirements:

```json
POST /v1/company/run
{
  "requirement": "fallback",
  "conversation_id": "conv_abc123",
  "project_name": "my_todo_app",
  "n_round": 5
}
```

---

## WebSocket Streaming

**`WS /stream/{conversation_id}`**

Real-time conversation events.

**Events:**
- `ai_response`: AI message received
- `requirement_update`: Requirements enhanced
- `error`: Error occurred
