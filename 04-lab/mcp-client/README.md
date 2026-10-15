# Weather Agent - Google ADK with MCP Server

AI agent built with **Google Agent Development Kit (ADK)** that uses tools from a local **MCP server** via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   User Browser  │ ───> │  ADK Web UI      │ ───> │  Weather Agent      │
│   localhost:8000│      │  (Google ADK)    │      │  (Agent with MCP)   │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
                                                             │
                                                             │ Streamable HTTP
                                                             ▼
                                                   ┌─────────────────────┐
                                                   │  MCP Server         │
                                                   │ 127.0.0.1:18085/mcp │
                                                   │  FastMCP + Tools    │
                                                   └─────────────────────┘
                                                             │
                                                             ▼
                                                   ┌─────────────────────┐
                                                   │  WeatherAPI.com     │
                                                   └─────────────────────┘
```

## Features

- **Remote MCP Tools**: Connects to MCP server via Streamable HTTP
- **3 Weather Tools**:
  - `get_current_weather(city)` - Real-time weather conditions
  - `get_forecast(city, days)` - Weather forecast up to 3 days
  - `health_check()` - Server health verification
- **Web Interface**: UI via ADK web
- **Streaming Responses**: Real-time AI responses

## Quick Start

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/getting-started/installation/). Create a [WeatherAPI key](https://www.weatherapi.com/) for live weather results and a [DeepSeek API key](https://platform.deepseek.com/api_keys) for agent chat.

### 1. Start the MCP Server

```powershell
cd 04-lab/mcp-server
uv sync --locked
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Set WEATHERAPI_KEY in .env. PORT is set to 18085 by the template.
uv run python weather.py
```

Keep that terminal open. In a second terminal, from the repository root:

```powershell
cd 04-lab/mcp-client
uv sync --locked
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Set DEEPSEEK_API_KEY in .env. MCP_SERVER_URL and DEEPSEEK_MODEL have defaults.

# Verify MCP tools without calling DeepSeek
uv run python smoke_mcp.py Hanoi
# Or check only MCP discovery and health, without either API key:
uv run python smoke_mcp.py --health-only
```

### 2. Run the Agent

```powershell
uv run adk web
```

### 3. Use the Agent

1. Open browser: http://localhost:8000
2. Select `weather_agent` from dropdown
3. Ask questions like:
   - "What's the weather in Brisbane?"
   - "Give me a 3-day forecast for Tokyo"
   - "How's the weather in New York?"

## Project Structure

```
mcp-client/
├── weather_agent/
│   ├── agent.py           # Main agent with MCP connection
│   └── __init__.py
├── smoke_mcp.py           # MCP health check and live weather smoke test
├── pyproject.toml
├── uv.lock
├── .env.example           # Safe-to-commit configuration template
├── .env                   # Local keys and configuration; do not commit
└── README.md
```

## Configuration

### Agent Configuration

In `weather_agent/agent.py`:

```python
from google.adk.models.lite_llm import LiteLlm

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:18085/mcp")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-chat")

connection_params = StreamableHTTPConnectionParams(
    url=MCP_SERVER_URL,
    timeout=30.0,
)

root_agent = Agent(
    name="weather_agent",
    model=LiteLlm(model=DEEPSEEK_MODEL),
    tools=[weather_tools],
)
```

## Troubleshooting

### Agent won't connect to MCP server

1. **404 errors**: MCP server is not running or wrong port
   - Ensure the MCP server is running on port 18085
   - Check `MCP_SERVER_URL` (env var / `.env`, default `http://127.0.0.1:18085/mcp`)

2. **Connection refused / address already in use**: Server is stopped or the port is occupied
   - Check whether the server is running on port 18085: `netstat -ano | findstr :18085`
   - If you choose another port, update `PORT` in `mcp-server/.env` and the port in `MCP_SERVER_URL` in `mcp-client/.env`

3. **Timeout errors**: Server not started
   - Start the MCP server first, then the ADK client

### MCP Smoke Check

Run `uv run python smoke_mcp.py Hanoi` from this directory to check the MCP
connection and live weather tool before starting the agent. If it fails, make
sure the server is running and that both `.env` files use the same port.

## Environment Variables

Copy `.env.example` to `.env` and set `DEEPSEEK_API_KEY` before starting `adk web`.

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [WeatherAPI](https://www.weatherapi.com/)
