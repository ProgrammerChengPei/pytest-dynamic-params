# Generator registry implementation

from typing import Dict, List, Optional

from .base import GeneratorBase
from ...errors import GeneratorNotFoundError

class GeneratorRegistry:
    """Registry for managing parameter generators"""
    
    def __init__(self):
        """Initialize a generator registry"""
        self._generators: Dict[str, GeneratorBase] = {}
    
    def register(self, name: str, generator: GeneratorBase) -> None:
        """Register a generator
        
        Args:
            name: The name of the generator
            generator: The generator instance
        """
        self._generators[name] = generator
    
    def get(self, name: str) -> GeneratorBase:
        """Get a generator by name
        
        Args:
            name: The name of the generator
            
        Returns:
            The generator instance
            
        Raises:
            GeneratorNotFoundError: If the generator is not found
        """
        if name not in self._generators:
            raise GeneratorNotFoundError(f"Generator '{name}' not found")
        return self._generators[name]
    
    def list(self) -> List[str]:
        """List all registered generators
        
        Returns:
            List of generator names
        """
        return list(self._generators.keys())
    
    def unregister(self, name: str) -> None:
        """Unregister a generator
        
        Args:
            name: The name of the generator to unregister
        """
        if name in self._generators:
            del self._generators[name]
    
    def clear(self) -> None:
        """Clear all registered generators"""
        self._generators.clear()

# Global generator registry instance
registry = GeneratorRegistry()
