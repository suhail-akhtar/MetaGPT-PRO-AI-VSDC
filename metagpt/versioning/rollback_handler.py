#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : rollback_handler.py
@Desc    : Handle version rollback operations
"""
from metagpt.logs import logger
from metagpt.versioning.version_manager import version_manager
from metagpt.versioning.schemas import DocumentVersion


class RollbackHandler:
    """Handle rollback operations preserving history"""
    
    async def rollback(
        self,
        project_id: str,
        document_id: str,
        target_version: int,
        reason: str = "Rollback requested",
        rolled_back_by: str = "System"
    ) -> tuple[bool, int]:
        """
        Rollback to a previous version.
        Creates a NEW version with the old content (preserves history).
        
        Args:
            project_id: Project identifier
            document_id: Document to rollback
            target_version: Version to restore
            reason: Why rollback was requested
            rolled_back_by: Who requested the rollback
            
        Returns:
            Tuple of (success, new_version_number)
        """
        # Get the target version
        old_version = await version_manager.get_version(
            project_id, document_id, target_version
        )
        
        if not old_version:
            logger.error(f"Target version {target_version} not found for {document_id}")
            return False, 0
        
        # Get current version for reference
        history = await version_manager.get_versions_list(project_id, document_id)
        current = history.current_version
        
        # Create new version with old content
        new_version = await version_manager.snapshot(
            project_id=project_id,
            document_id=document_id,
            document_type=old_version.document_type,
            content=old_version.content,
            changed_by=rolled_back_by,
            change_reason=f"{reason} (rolled back from v{current} to v{target_version})",
            changes_summary=[f"Restored content from version {target_version}"]
        )
        
        logger.info(
            f"Rollback complete: {document_id} v{current} -> v{new_version.version} "
            f"(content from v{target_version})"
        )
        
        # Notify agents about rollback
        await self._notify_rollback(project_id, document_id, target_version, new_version.version)
        
        return True, new_version.version
    
    async def _notify_rollback(
        self,
        project_id: str,
        document_id: str,
        from_version: int,
        to_version: int
    ):
        """Notify agents about the rollback"""
        try:
            from metagpt.collaboration.agent_messenger import messenger
            from metagpt.collaboration.schemas import MessageType
            
            await messenger.send_message(
                from_agent="VersionManager",
                to_agent="all",
                content=f"📜 ROLLBACK: {document_id} restored to v{from_version} content (now v{to_version})",
                message_type=MessageType.NOTIFICATION,
                context={"project_id": project_id, "document_id": document_id}
            )
        except Exception as e:
            logger.debug(f"Could not notify rollback: {e}")
    
    async def can_rollback(
        self,
        project_id: str,
        document_id: str,
        target_version: int
    ) -> bool:
        """Check if rollback is possible"""
        version = await version_manager.get_version(
            project_id, document_id, target_version
        )
        
        if not version:
            return False
        
        if version.locked:
            logger.warning(f"Cannot rollback to locked version {target_version}")
            return False
        
        return True
