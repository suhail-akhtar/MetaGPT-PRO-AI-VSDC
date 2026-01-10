#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : version_manager.py
@Desc    : Track document versions and snapshots
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from metagpt.logs import logger
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.versioning.schemas import DocumentVersion, VersionHistory, ChangeEntry


class VersionManager:
    """Singleton version manager for tracking document versions"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VersionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._histories: Dict[str, Dict[str, VersionHistory]] = {}  # project_id -> doc_id -> history
        self._audit_log: Dict[str, List[ChangeEntry]] = {}  # project_id -> entries
        self._initialized = True
    
    def _get_storage_path(self, project_id: str, doc_type: str = "") -> Path:
        path = DEFAULT_WORKSPACE_ROOT / "projects" / project_id / "versions"
        if doc_type:
            path = path / doc_type
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def _compute_hash(self, content: Union[str, Dict]) -> str:
        """Compute hash of content for comparison"""
        if isinstance(content, dict):
            content = json.dumps(content, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    async def snapshot(
        self,
        project_id: str,
        document_id: str,
        document_type: str,
        content: Union[str, Dict],
        changed_by: str = "System",
        change_reason: str = "",
        changes_summary: List[str] = None
    ) -> DocumentVersion:
        """
        Create a new version snapshot of a document.
        
        Args:
            project_id: Project identifier
            document_id: Document identifier (e.g., "prd", "design", "main.py")
            document_type: Type of document ("prd", "design", "code")
            content: Full document content
            changed_by: Who made the change
            change_reason: Why the change was made
            changes_summary: List of change descriptions
            
        Returns:
            The new DocumentVersion
        """
        # Get or create history
        history = self._get_history(project_id, document_id)
        
        # Determine new version number
        new_version = history.current_version + 1
        parent_version = history.current_version if history.current_version > 0 else None
        
        # Create version
        version = DocumentVersion(
            document_id=document_id,
            document_type=document_type,
            version=new_version,
            content=content,
            content_hash=self._compute_hash(content),
            changed_by=changed_by,
            change_reason=change_reason,
            changes_summary=changes_summary or [],
            parent_version=parent_version
        )
        
        # Save version to disk
        await self._save_version(project_id, version)
        
        # Update history
        history.versions.append(new_version)
        history.current_version = new_version
        history.updated_at = datetime.now()
        
        # Add to audit log
        self._add_audit_entry(project_id, version)
        
        logger.info(f"Snapshot created: {document_id} v{new_version} by {changed_by}")
        return version
    
    def _get_history(self, project_id: str, document_id: str) -> VersionHistory:
        """Get or create version history for a document"""
        if project_id not in self._histories:
            self._histories[project_id] = {}
        
        if document_id not in self._histories[project_id]:
            self._histories[project_id][document_id] = VersionHistory(
                document_id=document_id,
                document_type=""
            )
        
        return self._histories[project_id][document_id]
    
    async def _save_version(self, project_id: str, version: DocumentVersion):
        """Save version to disk"""
        path = self._get_storage_path(project_id, version.document_type)
        doc_path = path / version.document_id
        doc_path.mkdir(parents=True, exist_ok=True)
        
        # Save version file
        version_file = doc_path / f"v{version.version}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version.model_dump(), f, indent=2, default=str)
        
        # Update current pointer
        current_file = doc_path / "current.txt"
        with open(current_file, 'w') as f:
            f.write(str(version.version))
    
    async def get_version(
        self,
        project_id: str,
        document_id: str,
        version: int = None,
        document_type: str = ""
    ) -> Optional[DocumentVersion]:
        """
        Get a specific version of a document.
        If version is None, returns current version.
        """
        # Try to find the document type if not provided
        if not document_type:
            for doc_type in ["prd", "design", "code"]:
                path = self._get_storage_path(project_id, doc_type) / document_id
                if path.exists():
                    document_type = doc_type
                    break
        
        doc_path = self._get_storage_path(project_id, document_type) / document_id
        
        if not doc_path.exists():
            return None
        
        # Get version number
        if version is None:
            current_file = doc_path / "current.txt"
            if current_file.exists():
                version = int(current_file.read_text().strip())
            else:
                return None
        
        # Load version
        version_file = doc_path / f"v{version}.json"
        if not version_file.exists():
            return None
        
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return DocumentVersion(**data)
    
    async def get_versions_list(
        self,
        project_id: str,
        document_id: str,
        document_type: str = ""
    ) -> VersionHistory:
        """Get list of all versions for a document"""
        history = self._get_history(project_id, document_id)
        
        # Also scan disk for versions
        if not document_type:
            for doc_type in ["prd", "design", "code"]:
                path = self._get_storage_path(project_id, doc_type) / document_id
                if path.exists():
                    document_type = doc_type
                    break
        
        if document_type:
            doc_path = self._get_storage_path(project_id, document_type) / document_id
            if doc_path.exists():
                versions = []
                for f in doc_path.glob("v*.json"):
                    try:
                        v = int(f.stem[1:])  # Remove 'v' prefix
                        versions.append(v)
                    except:
                        pass
                
                history.versions = sorted(versions)
                history.document_type = document_type
                
                # Get current
                current_file = doc_path / "current.txt"
                if current_file.exists():
                    history.current_version = int(current_file.read_text().strip())
        
        return history
    
    def _add_audit_entry(self, project_id: str, version: DocumentVersion):
        """Add entry to audit log"""
        if project_id not in self._audit_log:
            self._audit_log[project_id] = []
        
        entry = ChangeEntry(
            document_id=version.document_id,
            document_type=version.document_type,
            version=version.version,
            changed_by=version.changed_by,
            change_reason=version.change_reason,
            changes_summary=", ".join(version.changes_summary) if version.changes_summary else ""
        )
        
        self._audit_log[project_id].append(entry)
    
    def get_audit_log(self, project_id: str, limit: int = 100) -> List[ChangeEntry]:
        """Get audit log entries"""
        entries = self._audit_log.get(project_id, [])
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    async def lock_version(self, project_id: str, document_id: str, version: int) -> bool:
        """Lock a version to prevent modifications"""
        doc_version = await self.get_version(project_id, document_id, version)
        if not doc_version:
            return False
        
        doc_version.locked = True
        await self._save_version(project_id, doc_version)
        logger.info(f"Version locked: {document_id} v{version}")
        return True


# Global singleton
version_manager = VersionManager()
