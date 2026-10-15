# Lab 04 — Weather Agent with Remote MCP Server

A weather agent built with Google ADK that connects to an MCP server via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐   Streamable HTTP    ┌─────────────────┐      REST       ┌─────────────────┐
│   ADK Agent     │ ──────────────────── │   MCP Server    │ ─────────────── │  WeatherAPI.com │
│  (mcp-client)   │ 127.0.0.1:18085/mcp │  (mcp-server)   │                 │                 │
└─────────────────┘                      └─────────────────┘                 └─────────────────┘
```

## Tools

| Tool | Description |
|------|-------------|
| `get_current_weather(city)` | Get current weather conditions for a city |
| `get_forecast(city, days)` | Get weather forecast (1–3 days) |
| `health_check()` | Verify server is running |

## ADK làm gì trong Lab này?

ADK (Agent Development Kit) đóng vai trò **MCP Client** 
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. KẾT NỐI tới MCP Server qua Streamable HTTP                  │
│     StreamableHTTPConnectionParams(url="http://127.0.0.1:18085/mcp") │
│                                                                 │
│  2. KHÁM PHÁ tools tự động (list_tools)                         │
│     McpToolset → tự hỏi server "anh có tool gì?"                │
│     → nhận về: get_current_weather, get_forecast, health_check  │
│                                                                 │
│  3. TRUYỀN tools cho LLM (DeepSeek)                             │
│     Agent(model=LiteLlm("deepseek/deepseek-chat"), ...)         │
│     → DeepSeek biết nó có thể gọi 3 tools trên                  │
│                                                                 │
│  4. ĐIỀU PHỐI vòng lặp Function Calling                         │
│     User hỏi → DeepSeek chọn tool → ADK gọi MCP Server          │
│     → nhận kết quả → đưa lại cho DeepSeek tổng hợp              │
│                                                                 │
│  5. CUNG CẤP giao diện web (adk web)                            │
│     → http://localhost:8000 để chat với agent                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

So với bài 02 (viết client thủ công bằng `mcp.ClientSession`), ADK giúp bạn **không phải viết vòng lặp function calling thủ công** nữa. Toàn bộ luồng list_tools → model quyết định → call_tool → model tổng hợp được ADK xử lý tự động.

## Setup

Open two terminals from the repository root. You need Python 3.12+ and [uv](https://docs.astral.sh/uv/getting-started/installation/). Create API keys for [WeatherAPI](https://www.weatherapi.com/) and [DeepSeek](https://platform.deepseek.com/api_keys). The health-only check needs neither key; the full weather check needs WeatherAPI but does not call an LLM; agent chat needs DeepSeek.

### 1. MCP Server

```bash
cd 04-lab/mcp-server
uv sync --locked
# Copy the template only if .env does not already exist, then set WEATHERAPI_KEY:
# PowerShell: if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# macOS/Linux: test -f .env || cp .env.example .env

# Start the server on port 18085
uv run python weather.py
```

The server will be available at `http://127.0.0.1:18085/mcp`.

### 2. ADK Agent (Client)

```bash
cd 04-lab/mcp-client
uv sync --locked
# Copy the template only if .env does not already exist, then set DEEPSEEK_API_KEY:
# PowerShell: if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# macOS/Linux: test -f .env || cp .env.example .env

# Verify MCP tools without calling DeepSeek
uv run python smoke_mcp.py Hanoi
# To check only MCP discovery and health, without either API key:
uv run python smoke_mcp.py --health-only

# Start ADK web interface
uv run adk web
```

Open http://localhost:8000 in your browser, select `weather_agent`, and ask about the weather.

## Configuration

| Variable | Where | Description |
|----------|-------|-------------|
| `WEATHERAPI_KEY` | mcp-server | API key from weatherapi.com |
| `DEEPSEEK_API_KEY` | mcp-client/.env | DeepSeek API key |
| `DEEPSEEK_MODEL` | mcp-client/.env | LiteLLM model name (default: `deepseek/deepseek-chat`) |
| `PORT` | mcp-server/.env | Local server port (`18085`; if changed, update the client URL to match) |
| `MCP_SERVER_URL` | mcp-client/.env | MCP endpoint the agent connects to (default: `http://127.0.0.1:18085/mcp`; set to your Cloud Run URL + `/mcp` when deployed) |
