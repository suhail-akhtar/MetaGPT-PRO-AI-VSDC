#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : schemas.py
@Desc    : Pydantic schemas for Agent Collaboration Layer
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class MessageType(str, Enum):
    """Type of agent message"""
    QUESTION = "question"
    ANSWER = "answer"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"
    CLARIFICATION = "clarification"
    HANDOFF = "handoff"
    NOTIFICATION = "notification"
    CLIENT_MESSAGE = "client_message"


class ThreadStatus(str, Enum):
    """Status of a conversation thread"""
    ACTIVE = "active"
    WAITING_RESPONSE = "waiting_response"
    RESOLVED = "resolved"
    BLOCKED = "blocked"


class ApprovalStatus(str, Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class AgentMessage(BaseModel):
    """A message between agents"""
    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    from_agent: str  # "Alice", "Bob", "Alex", "Client"
    to_agent: str    # Specific agent or "all"
    message_type: MessageType
    content: str
    requires_response: bool = False
    context: Dict[str, Any] = Field(default_factory=dict)  # Related task/sprint/file
    thread_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    read: bool = False
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConversationThread(BaseModel):
    """A thread of related messages"""
    id: str = Field(default_factory=lambda: f"thread_{uuid.uuid4().hex[:12]}")
    topic: str
    participants: List[str] = Field(default_factory=list)
    messages: List[AgentMessage] = Field(default_factory=list)
    status: ThreadStatus = ThreadStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, msg: AgentMessage):
        msg.thread_id = self.id
        self.messages.append(msg)
        self.updated_at = datetime.now()
        if msg.from_agent not in self.participants:
            self.participants.append(msg.from_agent)
        if msg.to_agent != "all" and msg.to_agent not in self.participants:
            self.participants.append(msg.to_agent)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AgentInbox(BaseModel):
    """Inbox for an agent containing unread messages"""
    agent_name: str
    messages: List[AgentMessage] = Field(default_factory=list)
    
    @property
    def unread_count(self) -> int:
        return sum(1 for m in self.messages if not m.read)
    
    def add_message(self, msg: AgentMessage):
        self.messages.append(msg)
    
    def mark_read(self, message_id: str):
        for m in self.messages:
            if m.id == message_id:
                m.read = True
                break


class ApprovalRequest(BaseModel):
    """A pending approval request"""
    id: str = Field(default_factory=lambda: f"approval_{uuid.uuid4().hex[:12]}")
    message_id: str
    from_agent: str
    to_agent: str
    description: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    timeout_hours: int = 24
    
    @property
    def is_expired(self) -> bool:
        from datetime import timedelta
        return datetime.now() > self.created_at + timedelta(hours=self.timeout_hours)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# API Request/Response schemas

class SendMessageRequest(BaseModel):
    """Request to send a message"""
    from_agent: str
    to_agent: str
    content: str
    message_type: MessageType = MessageType.QUESTION
    requires_response: bool = False
    context: Dict[str, Any] = Field(default_factory=dict)
    inject_at: Optional[str] = None  # For client messages


class SendMessageResponse(BaseModel):
    """Response after sending message"""
    message_id: str
    thread_id: str
    delivered: bool


class ApprovalActionRequest(BaseModel):
    """Request to approve/reject"""
    message_id: str
    approved: bool
    notes: str = ""


class ApprovalActionResponse(BaseModel):
    """Response after approval action"""
    approval_id: str
    status: str
    workflow_resumed: bool


class InboxResponse(BaseModel):
    """Response with agent inbox"""
    agent_name: str
    unread: int
    messages: List[AgentMessage]


class ThreadResponse(BaseModel):
    """Response with thread details"""
    thread_id: str
    topic: str
    participants: List[str]
    messages: List[AgentMessage]
    status: str


class ConversationsResponse(BaseModel):
    """Response with all threads"""
    threads: List[ConversationThread]
    active_count: int
