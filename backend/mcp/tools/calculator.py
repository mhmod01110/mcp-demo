"""
Calculator tool implementation
"""

from typing import Any, Dict
from .base import BaseTool

class CalculatorTool(BaseTool):
    """Calculator tool for basic arithmetic operations"""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic arithmetic operations (add, subtract, multiply, divide)",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["operation", "a", "b"]
            }
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calculator operation"""
        try:
            operation = arguments["operation"]
            a = float(arguments["a"])
            b = float(arguments["b"])

            operations = {
                "add": lambda x, y: x + y,
                "subtract": lambda x, y: x - y,
                "multiply": lambda x, y: x * y,
                "divide": lambda x, y: x / y if y != 0 else None
            }

            if operation not in operations:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }

            result = operations[operation](a, b)

            if result is None:
                return {
                    "success": False,
                    "error": "Division by zero"
                }

            return {
                "success": True,
                "result": result,
                "operation": operation,
                "operands": {"a": a, "b": b}
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
