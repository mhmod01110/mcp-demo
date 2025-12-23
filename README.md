# MCP Project - Model Context Protocol Implementation

A full-stack implementation of the Model Context Protocol (MCP) with OpenAI integration, featuring a modern web UI and extensible architecture.

## 🚀 Features

- **MCP Server**: Fully compliant MCP server with tool registration
- **MCP Client**: OpenAI-integrated client with agentic capabilities
- **Web UI**: Modern, responsive chat interface
- **Extensible Architecture**: Easy to add new tools and features
- **Real-time Communication**: WebSocket support for live updates
- **Tool System**: Pluggable tool architecture

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Node.js (optional, for development)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd mcp-project
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## 🚀 Quick Start

1. **Start the backend server**
```bash
python backend/server.py
```

2. **Open the frontend**
- Open `frontend/index.html` in your browser
- Or use a local server:
```bash
cd frontend
python -m http.server 3000
```

3. **Start chatting!**
- The UI will connect to the backend automatically
- Try asking: "What is 25 multiplied by 48?"

## 🏗️ Architecture

### Backend
- **FastAPI**: High-performance web framework
- **MCP Server**: Manages tools and resources
- **MCP Client**: Handles OpenAI communication
- **Tool System**: Modular, extensible tool architecture

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Modern CSS**: Responsive, accessible design
- **WebSocket/REST**: Real-time communication

## 🔧 Adding New Tools

1. **Create tool file** in `backend/mcp/tools/`:

```python
from .base import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="My custom tool",
            input_schema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                },
                "required": ["param"]
            }
        )
    
    async def execute(self, arguments):
        # Implementation here
        return {"result": "success"}
```

2. **Register tool** in `backend/mcp/server.py`:

```python
from .tools.my_tool import MyTool

# In MCPServer.__init__:
self.register_tool(MyTool())
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_server.py

# Run with coverage
pytest --cov=backend tests/
```

## 🔒 Security

- Never commit `.env` file
- Keep API keys secure
- Use environment variables for sensitive data
- Implement rate limiting in production
- Validate all inputs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License

## 🙏 Acknowledgments

- Model Context Protocol specification
- OpenAI API
- FastAPI framework
