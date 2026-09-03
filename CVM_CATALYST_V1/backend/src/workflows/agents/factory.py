"""Agent factory for creating and managing agent instances."""
from typing import Any, Dict, Optional, Type
import structlog
from src.workflows.agents.registry import AgentRegistry

logger = structlog.get_logger(__name__)


class AgentFactory:
    """Factory for creating agent instances with configuration management."""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self._agent_classes: Dict[str, Type] = {}
        self._default_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_agent_class(
        self, 
        agent_id: str, 
        agent_class: Type, 
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register an agent class and its default configuration."""
        if agent_id in self._agent_classes:
            logger.warning("Agent class already registered, overwriting", agent_id=agent_id)
        
        self._agent_classes[agent_id] = agent_class
        self._default_configs[agent_id] = config or {}
        logger.info("Agent class registered", agent_id=agent_id, agent_class=agent_class.__name__)
    
    def create(
        self, 
        agent_id: str, 
        name: str,
        config_overrides: Optional[Dict[str, Any]] = None,
        register: bool = True
    ) -> Any:
        """Create an agent instance."""
        if agent_id not in self._agent_classes:
            raise ValueError(f"Agent class '{agent_id}' not registered")
        
        agent_class = self._agent_classes[agent_id]
        config = self._default_configs[agent_id].copy()
        
        if config_overrides:
            config.update(config_overrides)
        
        agent = agent_class(name=name, **config)
        
        if register:
            self.registry.register(agent_id, agent)
        
        logger.info("Agent created", agent_id=agent_id, name=name)
        return agent
    
    def create_batch(
        self,
        agent_specs: list,
        register: bool = True
    ) -> Dict[str, Any]:
        """Create multiple agents in batch."""
        agents = {}
        
        for spec in agent_specs:
            agent_id = spec['agent_id']
            name = spec['name']
            config_overrides = spec.get('config_overrides', None)
            
            try:
                agent = self.create(agent_id, name, config_overrides, register)
                agents[agent_id] = agent
            except Exception as e:
                logger.error("Failed to create agent in batch", agent_id=agent_id, error=str(e))
                raise
        
        logger.info("Batch agent creation completed", count=len(agents))
        return agents
    
    def get_registered_classes(self) -> Dict[str, Type]:
        """Get all registered agent classes."""
        return self._agent_classes.copy()