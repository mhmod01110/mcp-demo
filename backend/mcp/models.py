"""
Data models for MCP
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Tool:
    """Represents an MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class Resource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: str
    mime_type: str

@dataclass
class ToolCall:
    """Represents a tool call from the LLM"""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class ToolResult:
    """Represents the result of a tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None