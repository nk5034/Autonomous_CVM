"""Agent memory manager for managing short-term and long-term memory."""
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
import structlog
import time

logger = structlog.get_logger(__name__)


class MemoryEntry(BaseModel):
    """A single memory entry with optional TTL."""
    entry_id: str = Field(..., description="Unique entry ID")
    key: str = Field(..., description="Memory key")
    value: Any = Field(..., description="Memory value")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class AgentMemoryManager:
    """Manage agent memory with short-term and long-term storage."""
    
    def __init__(self):
        self._short_term_memory: Dict[str, MemoryEntry] = {}
        self._long_term_memory: Dict[str, MemoryEntry] = {}
        self._workflow_context: Dict[str, Dict[str, Any]] = {}
        self._memory_counter = 0
    
    def save_short_term(self, key: str, value: Any, tags: Optional[List[str]] = None) -> str:
        """Save to short-term memory (no expiration)."""
        entry_id = f"st_{self._memory_counter}_{int(time.time() * 1000)}"
        self._memory_counter += 1
        
        entry = MemoryEntry(
            entry_id=entry_id,
            key=key,
            value=value,
            tags=tags or []
        )
        
        self._short_term_memory[key] = entry
        logger.info("Saved to short-term memory", key=key, entry_id=entry_id)
        return entry_id
    
    def save_long_term(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: int = 86400,
        tags: Optional[List[str]] = None
    ) -> str:
        """Save to long-term memory with TTL."""
        entry_id = f"lt_{self._memory_counter}_{int(time.time() * 1000)}"
        self._memory_counter += 1
        
        expires_at = (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat()
        
        entry = MemoryEntry(
            entry_id=entry_id,
            key=key,
            value=value,
            tags=tags or [],
            expires_at=expires_at
        )
        
        self._long_term_memory[key] = entry
        logger.info("Saved to long-term memory", key=key, ttl_seconds=ttl_seconds)
        return entry_id
    
    def get_short_term(self, key: str) -> Optional[Any]:
        """Retrieve from short-term memory."""
        entry = self._short_term_memory.get(key)
        if entry:
            logger.info("Retrieved from short-term memory", key=key)
            return entry.value
        logger.warning("Short-term memory miss", key=key)
        return None
    
    def get_long_term(self, key: str) -> Optional[Any]:
        """Retrieve from long-term memory."""
        entry = self._long_term_memory.get(key)
        
        if entry is None:
            logger.warning("Long-term memory miss", key=key)
            return None
        
        # Check if expired
        if entry.expires_at:
            expires = datetime.fromisoformat(entry.expires_at)
            if datetime.now(UTC) > expires:
                del self._long_term_memory[key]
                logger.info("Long-term memory entry expired", key=key)
                return None
        
        logger.info("Retrieved from long-term memory", key=key)
        return entry.value
    
    def set_workflow_context(self, workflow_id: str, context: Dict[str, Any]) -> None:
        """Set workflow context."""
        self._workflow_context[workflow_id] = context
        logger.info("Workflow context set", workflow_id=workflow_id)
    
    def update_workflow_context(self, workflow_id: str, updates: Dict[str, Any]) -> None:
        """Update workflow context."""
        if workflow_id not in self._workflow_context:
            self._workflow_context[workflow_id] = {}
        
        self._workflow_context[workflow_id].update(updates)
        logger.info("Workflow context updated", workflow_id=workflow_id)
    
    def get_workflow_context(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow context."""
        return self._workflow_context.get(workflow_id, {})
    
    def get_by_tags(self, tags: List[str], memory_type: str = "all") -> List[MemoryEntry]:
        """Get memory entries by tags."""
        results = []
        
        if memory_type in ("short_term", "all"):
            results.extend([
                e for e in self._short_term_memory.values()
                if any(tag in e.tags for tag in tags)
            ])
        
        if memory_type in ("long_term", "all"):
            results.extend([
                e for e in self._long_term_memory.values()
                if any(tag in e.tags for tag in tags)
            ])
        
        logger.info("Retrieved memory by tags", tags=tags, count=len(results))
        return results
    
    def cleanup_expired(self) -> int:
        """Remove expired long-term memory entries."""
        now = datetime.now(UTC)
        expired_keys = []
        
        for key, entry in self._long_term_memory.items():
            if entry.expires_at:
                expires = datetime.fromisoformat(entry.expires_at)
                if now > expires:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._long_term_memory[key]
        
        logger.info("Cleaned up expired memory entries", count=len(expired_keys))
        return len(expired_keys)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        self.cleanup_expired()
        
        return {
            "short_term_entries": len(self._short_term_memory),
            "long_term_entries": len(self._long_term_memory),
            "workflow_contexts": len(self._workflow_context),
            "total_memory_size": len(str(self._short_term_memory)) + len(str(self._long_term_memory))
        }
    
    def clear(self) -> None:
        """Clear all memory (for testing)."""
        self._short_term_memory.clear()
        self._long_term_memory.clear()
        self._workflow_context.clear()
        logger.info("Memory cleared")