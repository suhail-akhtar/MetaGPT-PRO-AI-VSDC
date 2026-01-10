#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : agents.py
@Desc    : API routes for Agent Collaboration
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
from metagpt.collaboration.agent_messenger import messenger
from metagpt.collaboration.approval_gates import approval_gates
from metagpt.collaboration.schemas import (
    MessageType,
    ThreadStatus,
    SendMessageRequest,
    SendMessageResponse,
    ApprovalActionRequest,
    ApprovalActionResponse,
    InboxResponse,
    ThreadResponse,
    ConversationsResponse,
)
from metagpt.logs import logger

router = APIRouter()


@router.get("/conversations", response_model=ConversationsResponse)
async def get_conversations():
    """Get all conversation threads"""
    try:
        threads = messenger.get_threads()
        active_count = len([t for t in threads if t.status == ThreadStatus.ACTIVE])
        
        return ConversationsResponse(
            threads=threads,
            active_count=active_count
        )
    except Exception as e:
        logger.exception(f"Failed to get conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thread/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str):
    """Get a specific conversation thread"""
    thread = messenger.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return ThreadResponse(
        thread_id=thread.id,
        topic=thread.topic,
        participants=thread.participants,
        messages=thread.messages,
        status=thread.status.value
    )


@router.post("/message", response_model=SendMessageResponse)
async def send_message(req: SendMessageRequest):
    """Send a message between agents"""
    try:
        msg_id, thread_id = await messenger.send_message(
            from_agent=req.from_agent,
            to_agent=req.to_agent,
            content=req.content,
            message_type=req.message_type,
            requires_response=req.requires_response,
            context=req.context
        )
        
        return SendMessageResponse(
            message_id=msg_id,
            thread_id=thread_id,
            delivered=True
        )
    except Exception as e:
        logger.exception(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_name}/inbox", response_model=InboxResponse)
async def get_inbox(agent_name: str):
    """Get an agent's inbox"""
    try:
        inbox = messenger.get_inbox(agent_name)
        
        return InboxResponse(
            agent_name=inbox.agent_name,
            unread=inbox.unread_count,
            messages=inbox.messages
        )
    except Exception as e:
        logger.exception(f"Failed to get inbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve", response_model=ApprovalActionResponse)
async def approve_request(req: ApprovalActionRequest):
    """Approve or reject an approval request"""
    try:
        approval_id = approval_gates.resolve_by_message_id(
            message_id=req.message_id,
            approved=req.approved,
            notes=req.notes
        )
        
        if not approval_id:
            raise HTTPException(status_code=404, detail="Approval request not found")
        
        return ApprovalActionResponse(
            approval_id=approval_id,
            status="approved" if req.approved else "rejected",
            workflow_resumed=req.approved
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to process approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending_approvals(agent: str = None):
    """Get pending approval requests"""
    try:
        pending = approval_gates.get_pending(agent)
        return {
            "pending_count": len(pending),
            "approvals": [p.model_dump() for p in pending]
        }
    except Exception as e:
        logger.exception(f"Failed to get pending approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/stream")
async def agent_stream(websocket: WebSocket):
    """WebSocket for real-time agent collaboration events"""
    await websocket.accept()
    messenger.add_websocket(websocket)
    
    try:
        # Send initial state
        threads = messenger.get_threads()
        await websocket.send_json({
            "type": "initial_state",
            "active_threads": len([t for t in threads if t.status == ThreadStatus.ACTIVE]),
            "pending_approvals": len(approval_gates.get_pending())
        })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle any client commands
    except WebSocketDisconnect:
        messenger.remove_websocket(websocket)
    except Exception:
        messenger.remove_websocket(websocket)
