"""
File operations tool implementation
"""

from typing import Any, Dict
from .base import BaseTool

class FileOpsTool(BaseTool):
    """File operations tool (mock filesystem for demo)"""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="Reads content from a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        )

        # Mock filesystem
        self.mock_files = {
            "config.json": '{"app": "MCP Demo", "version": "1.0", "debug": true}',
            "data.txt": "This is sample data from a file.\nSecond line of data.",
            "notes.md": "# Notes\n\n## Project Ideas\n- Build MCP tools\n- Create UI",
            "users.csv": "id,name,email\n1,John Doe,john@example.com\n2,Jane Smith,jane@example.com"
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file"""
        try:
            path = arguments["path"]
            filename = path.split("/")[-1]

            if filename not in self.mock_files:
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }

            return {
                "success": True,
                "path": path,
                "content": self.mock_files[filename],
                "size": len(self.mock_files[filename])
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }