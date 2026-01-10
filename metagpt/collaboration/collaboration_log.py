#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : collaboration_log.py
@Desc    : Persists agent conversations to disk
"""
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from metagpt.logs import logger
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.collaboration.schemas import (
    AgentMessage, ConversationThread, AgentInbox, ThreadStatus
)


class CollaborationLog:
    """Persists collaboration data to disk"""
    
    def __init__(self, project_id: str = "default"):
        self.project_id = project_id
        self.storage_root = DEFAULT_WORKSPACE_ROOT / "projects" / project_id / "collaboration"
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    @property
    def threads_dir(self) -> Path:
        path = self.storage_root / "threads"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def inbox_dir(self) -> Path:
        path = self.storage_root / "inbox"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    async def save_thread(self, thread: ConversationThread) -> None:
        """Save a thread to disk"""
        thread_file = self.threads_dir / f"{thread.id}.json"
        
        data = {
            "id": thread.id,
            "topic": thread.topic,
            "participants": thread.participants,
            "messages": [m.model_dump() for m in thread.messages],
            "status": thread.status.value,
            "created_at": thread.created_at.isoformat(),
            "updated_at": thread.updated_at.isoformat()
        }
        
        with open(thread_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.debug(f"Thread saved: {thread.id}")
    
    async def load_thread(self, thread_id: str) -> Optional[ConversationThread]:
        """Load a thread from disk"""
        thread_file = self.threads_dir / f"{thread_id}.json"
        
        if not thread_file.exists():
            return None
        
        try:
            with open(thread_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            thread = ConversationThread(
                id=data["id"],
                topic=data["topic"],
                participants=data["participants"],
                status=ThreadStatus(data["status"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"])
            )
            
            for msg_data in data.get("messages", []):
                msg = AgentMessage(**msg_data)
                thread.messages.append(msg)
            
            return thread
        except Exception as e:
            logger.exception(f"Failed to load thread {thread_id}: {e}")
            return None
    
    async def load_all_threads(self) -> List[ConversationThread]:
        """Load all threads from disk"""
        threads = []
        
        for thread_file in self.threads_dir.glob("*.json"):
            thread_id = thread_file.stem
            thread = await self.load_thread(thread_id)
            if thread:
                threads.append(thread)
        
        return sorted(threads, key=lambda t: t.updated_at, reverse=True)
    
    async def save_inbox(self, inbox: AgentInbox) -> None:
        """Save an agent's inbox to disk"""
        inbox_file = self.inbox_dir / f"{inbox.agent_name.lower()}_inbox.json"
        
        data = {
            "agent_name": inbox.agent_name,
            "messages": [m.model_dump() for m in inbox.messages]
        }
        
        with open(inbox_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def load_inbox(self, agent_name: str) -> Optional[AgentInbox]:
        """Load an agent's inbox from disk"""
        inbox_file = self.inbox_dir / f"{agent_name.lower()}_inbox.json"
        
        if not inbox_file.exists():
            return AgentInbox(agent_name=agent_name)
        
        try:
            with open(inbox_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            inbox = AgentInbox(agent_name=data["agent_name"])
            for msg_data in data.get("messages", []):
                inbox.messages.append(AgentMessage(**msg_data))
            
            return inbox
        except Exception as e:
            logger.exception(f"Failed to load inbox for {agent_name}: {e}")
            return AgentInbox(agent_name=agent_name)
    
    async def record_message(self, message: AgentMessage) -> None:
        """Record a message (append to log)"""
        log_file = self.storage_root / "message_log.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(message.model_dump(), default=str) + "\n")
    
    async def get_message_history(self, limit: int = 100) -> List[AgentMessage]:
        """Get recent message history"""
        log_file = self.storage_root / "message_log.jsonl"
        
        if not log_file.exists():
            return []
        
        messages = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    messages.append(AgentMessage(**json.loads(line)))
                except:
                    pass
        
        return messages[-limit:]
