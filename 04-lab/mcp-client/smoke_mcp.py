"""Smoke-test the remote Weather MCP server without calling an LLM."""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


async def main(city: str, health_only: bool) -> None:
    load_dotenv()
    server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:18085/mcp")

    async with streamable_http_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            required_tools = {
                "get_current_weather",
                "get_forecast",
                "health_check",
            }
            missing_tools = required_tools - tool_names
            if missing_tools:
                raise RuntimeError(
                    "MCP server is missing tools: " + ", ".join(sorted(missing_tools))
                )
            print("Tools: " + ", ".join(sorted(tool_names)))

            health = await session.call_tool("health_check", {})
            if health.isError:
                raise RuntimeError(health.content[0].text)
            health_text = "\n".join(
                item.text for item in health.content if hasattr(item, "text")
            )
            if "running" not in health_text.lower():
                raise RuntimeError("Unexpected health check response: " + health_text)
            print("Health: " + health_text)

            if health_only:
                return

            weather = await session.call_tool(
                "get_current_weather", {"city": city}
            )
            weather_text = "\n".join(
                item.text for item in weather.content if hasattr(item, "text")
            ).strip()
            if weather.isError:
                raise RuntimeError(weather_text or "Weather tool returned an error")
            weather_result_lower = weather_text.lower()
            if not weather_text or any(
                message in weather_result_lower
                for message in (
                    "unable to fetch",
                    "weatherapi key not configured",
                )
            ):
                raise RuntimeError(weather_text or "Weather tool returned no data")
            print(weather_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("city", nargs="?", default="Hanoi")
    parser.add_argument(
        "--health-only",
        action="store_true",
        help="check MCP discovery and health without calling WeatherAPI",
    )
    args = parser.parse_args()
    asyncio.run(main(args.city, args.health_only))
