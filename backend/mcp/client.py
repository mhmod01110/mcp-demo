"""
MCP Client implementation with OpenAI integration
"""

import json
from typing import Any, Dict, List, Optional
import openai

class MCPClient:
    """
    MCP Client that connects to an MCP server and uses OpenAI for LLM interaction.
    """

    def __init__(self, api_key: str, server):
        self.client = openai.OpenAI(api_key=api_key)
        self.server = server
        self.conversation_history: List[Dict[str, Any]] = []
        self.tools_cache: Optional[List[Dict[str, Any]]] = None

    async def initialize(self):
        """Initialize the client by fetching available tools"""
        self.tools_cache = await self.server.list_tools()
        print(f"Initialized MCP client with {len(self.tools_cache)} tools")

    def _convert_tools_to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert MCP tool format to OpenAI function calling format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            }
            for tool in self.tools_cache
        ]

    async def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Send a message and handle tool calls in an agentic loop.
        """
        
        # Add system message if this is the first message
        if len(self.conversation_history) == 0:
            self.conversation_history.append({
                "role": "system",
                "content": """You are a helpful AI assistant with access to real-time tools.

    IMPORTANT: You have access to these tools and MUST use them when appropriate:
    - get_weather: For ANY weather-related questions, ALWAYS use this tool
    - calculator: For mathematical calculations
    - read_file: For reading file contents

    When a user asks about weather, current conditions, temperature, or forecasts:
    1. DO NOT say you cannot access real-time data
    2. ALWAYS call the get_weather tool
    3. Use the tool's response to answer the question

    Never refuse to get weather information - you have a working weather tool!"""
            })
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                tools=self._convert_tools_to_openai_format(),
                tool_choice="auto"
            )

            message = response.choices[0].message

            # Add assistant's response
            msg_dict = {
                "role": "assistant",
                "content": message.content
            }

            if message.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]

            self.conversation_history.append(msg_dict)

            # Check if there are tool calls
            if not message.tool_calls:
                return message.content or "No response generated"

            # Process tool calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute tool via MCP server
                result = await self.server.call_tool(function_name, function_args)

                # Add tool result to history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        return "Max iterations reached without final answer"

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []