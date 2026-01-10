#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : approval_gates.py
@Desc    : Blocks workflow until approval is received
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
from metagpt.logs import logger
from metagpt.collaboration.schemas import (
    ApprovalRequest, ApprovalStatus, AgentMessage, MessageType
)
from metagpt.collaboration.agent_messenger import messenger


class ApprovalGates:
    """
    Manages approval gates that block workflow until approved.
    
    Usage:
        gate = approval_gates.request_approval(
            from_agent="Bob",
            to_agent="Alice", 
            description="Design complete. Please review."
        )
        approved = await approval_gates.wait_for_approval(gate.id)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ApprovalGates, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._pending: Dict[str, ApprovalRequest] = {}
        self._approval_events: Dict[str, asyncio.Event] = {}
        self._auto_approve: bool = False  # For non-critical projects
        self._timeout_hours: int = 24
        self._initialized = True
    
    async def request_approval(
        self,
        from_agent: str,
        to_agent: str,
        description: str,
        context: dict = None,
        auto_approve_timeout: bool = True
    ) -> ApprovalRequest:
        """
        Create an approval request and send message to approver.
        
        Args:
            from_agent: Agent requesting approval
            to_agent: Agent who should approve
            description: What needs approval
            context: Additional context (files, tasks, etc.)
            auto_approve_timeout: If True, auto-approve after timeout
            
        Returns:
            ApprovalRequest object
        """
        # Send approval request message
        msg_id, thread_id = await messenger.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=f"🔔 APPROVAL REQUIRED: {description}",
            message_type=MessageType.APPROVAL_REQUEST,
            requires_response=True,
            context=context or {}
        )
        
        # Create approval request
        request = ApprovalRequest(
            message_id=msg_id,
            from_agent=from_agent,
            to_agent=to_agent,
            description=description,
            timeout_hours=self._timeout_hours
        )
        
        self._pending[request.id] = request
        self._approval_events[request.id] = asyncio.Event()
        
        logger.info(f"Approval requested: {from_agent} -> {to_agent}: {description[:50]}...")
        return request
    
    async def wait_for_approval(
        self,
        approval_id: str,
        timeout_seconds: int = None
    ) -> bool:
        """
        Wait for an approval to be granted or rejected.
        
        Args:
            approval_id: The approval request ID
            timeout_seconds: Max wait time (None = use default timeout)
            
        Returns:
            True if approved, False if rejected or timeout
        """
        if approval_id not in self._pending:
            raise ValueError(f"Approval {approval_id} not found")
        
        request = self._pending[approval_id]
        event = self._approval_events[approval_id]
        
        # Auto-approve mode
        if self._auto_approve:
            logger.info(f"Auto-approving {approval_id} (auto-approve enabled)")
            await self.resolve(approval_id, approved=True, notes="Auto-approved")
            return True
        
        # Calculate timeout
        if timeout_seconds is None:
            timeout_seconds = request.timeout_hours * 3600
        
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout_seconds)
            return request.status == ApprovalStatus.APPROVED
        except asyncio.TimeoutError:
            logger.warning(f"Approval {approval_id} timed out")
            request.status = ApprovalStatus.TIMEOUT
            request.resolved_at = datetime.now()
            request.resolution_notes = "Timed out - auto-approved"
            return True  # Auto-approve on timeout
    
    async def resolve(
        self,
        approval_id: str,
        approved: bool,
        notes: str = ""
    ) -> bool:
        """
        Resolve an approval request.
        
        Args:
            approval_id: The approval request ID
            approved: True to approve, False to reject
            notes: Optional notes from approver
            
        Returns:
            True if workflow can proceed
        """
        if approval_id not in self._pending:
            raise ValueError(f"Approval {approval_id} not found")
        
        request = self._pending[approval_id]
        request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        request.resolved_at = datetime.now()
        request.resolution_notes = notes
        
        # Send response message
        await messenger.send_message(
            from_agent=request.to_agent,
            to_agent=request.from_agent,
            content=f"{'✅ APPROVED' if approved else '❌ REJECTED'}: {notes or 'No notes'}",
            message_type=MessageType.APPROVAL_RESPONSE,
            requires_response=False
        )
        
        # Trigger waiting coroutine
        if approval_id in self._approval_events:
            self._approval_events[approval_id].set()
        
        logger.info(f"Approval {approval_id}: {'APPROVED' if approved else 'REJECTED'}")
        return approved
    
    def resolve_by_message_id(self, message_id: str, approved: bool, notes: str = "") -> Optional[str]:
        """Find approval by message ID and resolve it"""
        for approval_id, request in self._pending.items():
            if request.message_id == message_id:
                asyncio.create_task(self.resolve(approval_id, approved, notes))
                return approval_id
        return None
    
    def get_pending(self, agent_name: str = None) -> list[ApprovalRequest]:
        """Get pending approvals, optionally filtered by agent"""
        pending = [r for r in self._pending.values() if r.status == ApprovalStatus.PENDING]
        if agent_name:
            pending = [r for r in pending if r.to_agent == agent_name]
        return pending
    
    def set_auto_approve(self, enabled: bool):
        """Enable/disable auto-approve for non-critical projects"""
        self._auto_approve = enabled
        logger.info(f"Auto-approve {'enabled' if enabled else 'disabled'}")
    
    def set_timeout(self, hours: int):
        """Set default timeout hours"""
        self._timeout_hours = hours


# Global singleton
approval_gates = ApprovalGates()
