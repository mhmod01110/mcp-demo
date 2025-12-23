"""
Main FastAPI server for MCP project
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from backend.mcp.server import MCPServer
from backend.mcp.client import MCPClient

app = FastAPI(title="MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mcp_server = MCPServer()
mcp_client = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: Optional[List[dict]] = None

class ToolInfo(BaseModel):
    name: str
    description: str
    input_schema: dict

@app.on_event("startup")
async def startup_event():
    global mcp_client
    mcp_client = MCPClient(api_key=config.OPENAI_API_KEY, server=mcp_server)
    await mcp_client.initialize()
    print(f"MCP Server started with {len(mcp_server.tools)} tools")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/tools", response_model=List[ToolInfo])
async def list_tools():
    tools = await mcp_server.list_tools()
    return tools

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await mcp_client.chat(request.message)
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id or "new",
            tool_calls=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_conversation():
    mcp_client.reset_conversation()
    return {"status": "reset"}

# In backend/server.py, after startup_event
@app.get("/debug/tools")
async def debug_tools():
    return {
        "tools": [tool.name for tool in mcp_server.tools.values()],
        "has_api_key": bool(config.WEATHER_API_KEY)
    }
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = await mcp_client.chat(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
