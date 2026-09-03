"""Agent registry for centralized agent management."""
from typing import Dict, List, Optional
from threading import RLock
import structlog

logger = structlog.get_logger(__name__)


class AgentRegistry:
    """Central registry for all agents (Singleton pattern)."""
    
    _instance: Optional['AgentRegistry'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
            cls._instance._dependencies = {}
            cls._instance._lock = RLock()
            logger.info("AgentRegistry initialized")
        return cls._instance
    
    def register(self, agent_id: str, agent, dependencies: Optional[List[str]] = None) -> None:
        """Register an agent with optional dependencies."""
        with self._lock:
            if agent_id in self._agents:
                raise ValueError(f"Agent '{agent_id}' already registered")
            self._agents[agent_id] = agent
            self._dependencies[agent_id] = dependencies or []
        logger.info("Agent registered", agent_id=agent_id, dependencies=dependencies)
    
    def unregister(self, agent_id: str) -> None:
        """Unregister an agent."""
        with self._lock:
            if agent_id not in self._agents:
                raise ValueError(f"Agent '{agent_id}' not found")
            del self._agents[agent_id]
            del self._dependencies[agent_id]
        logger.info("Agent unregistered", agent_id=agent_id)
    
    def get(self, agent_id: str):
        """Get an agent by ID."""
        with self._lock:
            agent = self._agents.get(agent_id)
        if agent is None:
            logger.warning("Agent not found", agent_id=agent_id)
        return agent
    
    def get_by_name(self, name: str):
        """Get an agent by name."""
        with self._lock:
            for agent_id, agent in self._agents.items():
                if hasattr(agent, 'name') and agent.name == name:
                    return agent
        logger.warning("Agent not found by name", name=name)
        return None
    
    def get_all(self) -> Dict:
        """Get all registered agents."""
        with self._lock:
            return self._agents.copy()
    
    def list_agents(self) -> List[str]:
        """List all agent IDs."""
        with self._lock:
            return list(self._agents.keys())
    
    def validate_dependencies(self, agent_id: str) -> bool:
        """Validate that all dependencies are registered."""
        with self._lock:
            dependencies = list(self._dependencies.get(agent_id, []))
            agent_ids = set(self._agents.keys())
        for dep in dependencies:
            if dep not in agent_ids:
                logger.error("Dependency not found", agent_id=agent_id, dependency=dep)
                return False
        return True
    
    def clear(self) -> None:
        """Clear all registered agents (for testing)."""
        with self._lock:
            self._agents.clear()
            self._dependencies.clear()
        logger.info("AgentRegistry cleared")