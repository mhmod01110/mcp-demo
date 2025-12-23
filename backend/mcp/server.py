"""
MCP Server implementation
"""

from typing import Any, Dict, List
from .models import Tool, ToolResult
from .tools.calculator import CalculatorTool
from .tools.weather import WeatherTool
from .tools.file_ops import FileOpsTool
from config import config


class MCPServer:
    """
    MCP Server that manages tools and resources.
    Extensible architecture for adding new tools.
    """

    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        default_tools = [
            CalculatorTool(),
            WeatherTool(
                api_key=config.WEATHER_API_KEY,
                provider=config.WEATHER_PROVIDER
            ),
            FileOpsTool()
        ]

        for tool in default_tools:
            self.register_tool(tool)

    def register_tool(self, tool):
        """Register a new tool with the server"""
        self.tools[tool.name] = tool
        print(f"Registered tool: {tool.name}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for tool in self.tools.values()
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        if name not in self.tools:
            return {
                "success": False,
                "error": f"Tool not found: {name}"
            }

        try:
            tool = self.tools[name]
            result = await tool.execute(arguments)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }