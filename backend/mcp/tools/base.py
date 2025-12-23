"""
Base tool class for MCP tools
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """
    Abstract base class for all MCP tools.
    Inherit from this class to create new tools.
    """

    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given arguments.
        Must return a dict with 'success' key and result data.
        """
        pass

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate arguments against schema (basic implementation)"""
        required = self.input_schema.get("required", [])
        return all(key in arguments for key in required)