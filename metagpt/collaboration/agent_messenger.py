#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : agent_messenger.py
@Desc    : Routes messages between agents with thread management
"""
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime
from fastapi import WebSocket
from metagpt.logs import logger
from metagpt.collaboration.schemas import (
    AgentMessage, MessageType, ConversationThread, 
    ThreadStatus, AgentInbox
)


class AgentMessenger:
    """Singleton messenger for routing agent communications"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentMessenger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._threads: Dict[str, ConversationThread] = {}
        self._inboxes: Dict[str, AgentInbox] = {}
        self._websockets: Set[WebSocket] = set()
        self._message_handlers: Dict[str, callable] = {}
        self._initialized = True
        
        # Initialize default agent inboxes
        for agent in ["Alice", "Bob", "Alex", "Client"]:
            self._inboxes[agent] = AgentInbox(agent_name=agent)
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        message_type: MessageType = MessageType.QUESTION,
        requires_response: bool = False,
        context: dict = None,
        thread_id: str = None
    ) -> tuple[str, str]:
        """
        Send a message from one agent to another.
        
        Returns:
            Tuple of (message_id, thread_id)
        """
        msg = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            requires_response=requires_response,
            context=context or {},
            thread_id=thread_id
        )
        
        # Get or create thread
        if thread_id and thread_id in self._threads:
            thread = self._threads[thread_id]
        else:
            # Create new thread with topic from content
            topic = content[:50] + "..." if len(content) > 50 else content
            thread = ConversationThread(topic=topic)
            self._threads[thread.id] = thread
        
        # Add message to thread
        thread.add_message(msg)
        
        # Deliver to recipient inbox
        if to_agent == "all":
            for inbox in self._inboxes.values():
                if inbox.agent_name != from_agent:
                    inbox.add_message(msg)
        elif to_agent in self._inboxes:
            self._inboxes[to_agent].add_message(msg)
        else:
            # Create inbox for new agent
            self._inboxes[to_agent] = AgentInbox(agent_name=to_agent)
            self._inboxes[to_agent].add_message(msg)
        
        # Broadcast via WebSocket
        await self._broadcast({
            "type": "new_message",
            "message": msg.model_dump(),
            "thread_id": thread.id
        })
        
        # Auto-create approval request if this is an approval request message
        if message_type == MessageType.APPROVAL_REQUEST:
            from metagpt.collaboration.approval_gates import approval_gates
            from metagpt.collaboration.schemas import ApprovalRequest, ApprovalStatus
            
            approval = ApprovalRequest(
                message_id=msg.id,
                from_agent=from_agent,
                to_agent=to_agent,
                description=content
            )
            approval_gates._pending[approval.id] = approval
            import asyncio
            approval_gates._approval_events[approval.id] = asyncio.Event()
            logger.info(f"Auto-created approval request: {approval.id}")
        
        logger.info(f"Message sent: {from_agent} -> {to_agent}: {content[:50]}...")
        return msg.id, thread.id
    
    async def reply(
        self,
        thread_id: str,
        from_agent: str,
        content: str,
        message_type: MessageType = MessageType.ANSWER
    ) -> str:
        """Reply to an existing thread"""
        if thread_id not in self._threads:
            raise ValueError(f"Thread {thread_id} not found")
        
        thread = self._threads[thread_id]
        
        # Find the last message to determine recipient
        last_msg = thread.messages[-1] if thread.messages else None
        to_agent = last_msg.from_agent if last_msg else "all"
        
        msg_id, _ = await self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            message_type=message_type,
            thread_id=thread_id
        )
        
        return msg_id
    
    def get_thread(self, thread_id: str) -> Optional[ConversationThread]:
        """Get a conversation thread by ID"""
        return self._threads.get(thread_id)
    
    def get_threads(self, status: ThreadStatus = None) -> List[ConversationThread]:
        """Get all threads, optionally filtered by status"""
        threads = list(self._threads.values())
        if status:
            threads = [t for t in threads if t.status == status]
        return sorted(threads, key=lambda t: t.updated_at, reverse=True)
    
    def get_inbox(self, agent_name: str) -> AgentInbox:
        """Get inbox for an agent"""
        if agent_name not in self._inboxes:
            self._inboxes[agent_name] = AgentInbox(agent_name=agent_name)
        return self._inboxes[agent_name]
    
    def mark_message_read(self, agent_name: str, message_id: str):
        """Mark a message as read in an agent's inbox"""
        if agent_name in self._inboxes:
            self._inboxes[agent_name].mark_read(message_id)
    
    def resolve_thread(self, thread_id: str):
        """Mark a thread as resolved"""
        if thread_id in self._threads:
            self._threads[thread_id].status = ThreadStatus.RESOLVED
            self._threads[thread_id].updated_at = datetime.now()
    
    # WebSocket management
    def add_websocket(self, ws: WebSocket):
        self._websockets.add(ws)
    
    def remove_websocket(self, ws: WebSocket):
        self._websockets.discard(ws)
    
    async def _broadcast(self, message: dict):
        """Broadcast message to all connected WebSockets"""
        import json
        msg_str = json.dumps(message, default=str)
        for ws in list(self._websockets):
            try:
                await ws.send_text(msg_str)
            except Exception:
                self._websockets.discard(ws)
    
    def register_handler(self, agent_name: str, handler: callable):
        """Register a message handler for an agent"""
        self._message_handlers[agent_name] = handler
    
    async def process_pending_messages(self, agent_name: str):
        """Process pending messages for an agent (call from role)"""
        inbox = self.get_inbox(agent_name)
        handler = self._message_handlers.get(agent_name)
        
        if handler:
            for msg in inbox.messages:
                if not msg.read:
                    await handler(msg)
                    msg.read = True


# Global singleton instance
messenger = AgentMessenger()
