#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/09
@Author  : MetaGPT-Pro Team
@File    : approval_workflow.py
@Desc    : Handles requirement approval and locks requirements for development
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from metagpt.logs import logger
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.conversation.schemas import ConversationSession, ConversationStatus, EnhancedRequirements


class ApprovalWorkflow:
    """Manages the approval process for requirements"""
    
    def __init__(self, storage_root: Path = None):
        self.storage_root = storage_root or DEFAULT_WORKSPACE_ROOT / "conversations"
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    def _get_session_dir(self, conversation_id: str) -> Path:
        """Get the storage directory for a conversation"""
        session_dir = self.storage_root / conversation_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    async def save_session(self, session: ConversationSession) -> None:
        """Save session state to disk"""
        session_dir = self._get_session_dir(session.id)
        
        # Save messages
        messages_file = session_dir / "messages.json"
        messages_data = [msg.model_dump() for msg in session.messages]
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, indent=2, default=str)
        
        # Save enhanced requirements if present
        if session.enhanced_requirements:
            version_file = session_dir / f"requirements_v{session.version}.json"
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(session.enhanced_requirements.model_dump(), f, indent=2)
        
        # Save metadata
        metadata_file = session_dir / "metadata.json"
        metadata = {
            "id": session.id,
            "initial_idea": session.initial_idea,
            "status": session.status.value,
            "version": session.version,
            "created_at": session.created_at.isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.debug(f"Session {session.id} saved to {session_dir}")
    
    async def load_session(self, conversation_id: str) -> Optional[ConversationSession]:
        """Load session from disk"""
        session_dir = self._get_session_dir(conversation_id)
        metadata_file = session_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load messages
            messages_file = session_dir / "messages.json"
            messages = []
            if messages_file.exists():
                with open(messages_file, 'r', encoding='utf-8') as f:
                    messages_data = json.load(f)
                from metagpt.conversation.schemas import ConversationMessage
                messages = [ConversationMessage(**msg) for msg in messages_data]
            
            # Load latest requirements
            enhanced_requirements = None
            version = metadata.get("version", 1)
            req_file = session_dir / f"requirements_v{version}.json"
            if req_file.exists():
                with open(req_file, 'r', encoding='utf-8') as f:
                    req_data = json.load(f)
                enhanced_requirements = EnhancedRequirements(**req_data)
            
            return ConversationSession(
                id=metadata["id"],
                initial_idea=metadata["initial_idea"],
                messages=messages,
                status=ConversationStatus(metadata["status"]),
                enhanced_requirements=enhanced_requirements,
                version=version,
                created_at=datetime.fromisoformat(metadata["created_at"]),
                updated_at=datetime.fromisoformat(metadata["updated_at"])
            )
        except Exception as e:
            logger.exception(f"Failed to load session {conversation_id}: {e}")
            return None
    
    async def lock_requirements(self, session: ConversationSession) -> str:
        """
        Lock requirements as approved and ready for development.
        
        Args:
            session: The conversation session to approve
            
        Returns:
            Project ID for the approved requirements
        """
        session_dir = self._get_session_dir(session.id)
        
        # Update status
        session.status = ConversationStatus.APPROVED
        session.updated_at = datetime.now()
        
        # Save approved.json (final locked version)
        approved_file = session_dir / "approved.json"
        approved_data = {
            "conversation_id": session.id,
            "approved_at": datetime.now().isoformat(),
            "requirements": session.enhanced_requirements.model_dump() if session.enhanced_requirements else None,
            "original_idea": session.initial_idea,
            "project_name": session.enhanced_requirements.project_name if session.enhanced_requirements else ""
        }
        with open(approved_file, 'w', encoding='utf-8') as f:
            json.dump(approved_data, f, indent=2)
        
        # Save updated session
        await self.save_session(session)
        
        # Generate project ID
        project_id = f"proj_{session.id.replace('conv_', '')}"
        
        logger.info(f"Requirements locked for {session.id} -> {project_id}")
        return project_id
    
    async def get_approved_requirement(self, conversation_id: str) -> Optional[dict]:
        """
        Get the approved requirements for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            Approved requirements dict or None
        """
        session_dir = self._get_session_dir(conversation_id)
        approved_file = session_dir / "approved.json"
        
        if not approved_file.exists():
            return None
        
        try:
            with open(approved_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.exception(f"Failed to load approved requirements: {e}")
            return None
