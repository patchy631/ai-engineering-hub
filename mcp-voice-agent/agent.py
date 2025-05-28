"""
MCP voice agent that routes queries either to Firecrawl web search or to Supabase via MCP.
"""

from __future__ import annotations

import asyncio
import copy
import json
import logging
import os
from typing import Any, Callable, List, Optional

import inspect
from dotenv import load_dotenv
from firecrawl import FirecrawlApp, ScrapeOptions
from pydantic_ai.mcp import MCPServerStdio

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import assemblyai, openai, silero

# ------------------------------------------------------------------------------
# Configuration & Logging
# ------------------------------------------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
SUPABASE_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")

if not FIRECRAWL_API_KEY:
    logger.error("FIRECRAWL_API_KEY is not set in environment.")
    raise EnvironmentError("Please set FIRECRAWL_API_KEY env var.")

if not SUPABASE_TOKEN:
    logger.error("SUPABASE_ACCESS_TOKEN is not set in environment.")
    raise EnvironmentError("Please set SUPABASE_ACCESS_TOKEN env var.")

firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)


def _py_type(schema: dict) -> Any:
    """Convert JSON schema types into Python typing annotations."""
    t = schema.get("type")
    mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "object": dict,
    }

    if isinstance(t, list):
        if "array" in t:
            return List[_py_type(schema.get("items", {}))]
        t = t[0]

    if isinstance(t, str) and t in mapping:
        return mapping[t]
    if t == "array":
        return List[_py_type(schema.get("items", {}))]

    return Any


def schema_to_google_docstring(description: str, schema: dict) -> str:
    """
    Generate a Google-style docstring section from a JSON schema.
    """
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    lines = [description or "", "Args:"]

    for name, prop in props.items():
        t = prop.get("type", "Any")
        if isinstance(t, list):
            if "array" in t:
                subtype = prop.get("items", {}).get("type", "Any")
                py_type = f"List[{subtype.capitalize()}]"
            else:
                py_type = t[0].capitalize()
        elif t == "array":
            subtype = prop.get("items", {}).get("type", "Any")
            py_type = f"List[{subtype.capitalize()}]"
        else:
            py_type = t.capitalize()

        if name not in required:
            py_type = f"Optional[{py_type}]"

        desc = prop.get("description", "")
        lines.append(f"    {name} ({py_type}): {desc}")

    return "\n".join(lines)


@function_tool
async def firecrawl_search(
    context: RunContext,
    query: str,
    limit: int = 5
) -> List[str]:
    """
    Search the web via Firecrawl.

    Args:
        context (RunContext): LiveKit runtime context.
        query (str): Search query string.
        limit (int): Maximum pages to crawl.

    Returns:
        List[str]: Raw page contents.
    """
    url = f"https://www.google.com/search?q={query}"
    logger.debug("Starting Firecrawl for URL: %s (limit=%d)", url, limit)

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: firecrawl_app.crawl_url(
                url,
                limit=limit,
                scrape_options=ScrapeOptions(formats=["text", "markdown"])
            )
        )
        logger.info("Firecrawl returned %d pages", len(result))
        return result
    except Exception as e:
        logger.error("Firecrawl search failed: %s", e, exc_info=True)
        return []


async def build_livekit_tools(server: MCPServerStdio) -> List[Callable]:
    """
    Build LiveKit tools from a Supabase MCP server.
    """
    tools: List[Callable] = []
    all_tools = await server.list_tools()
    logger.info("Found %d MCP tools", len(all_tools))

    for td in all_tools:
        if td.name == "deploy_edge_function":
            logger.warning("Skipping tool %s", td.name)
            continue

        schema = copy.deepcopy(td.parameters_json_schema)
        if td.name == "list_tables":
            props = schema.setdefault("properties", {})
            props["schemas"] = {
                "type": ["array", "null"],
                "items": {"type": "string"},
                "default": []
            }
            schema["required"] = [r for r in schema.get("required", []) if r != "schemas"]

        props = schema.get("properties", {})
        required = set(schema.get("required", []))

        def make_proxy(
            tool_def=td,
            _props=props,
            _required=required,
            _schema=schema
        ) -> Callable:
            async def proxy(context: RunContext, **kwargs):
                # Convert None → [] for array params
                for k, v in list(kwargs.items()):
                    if ((_props[k].get("type") == "array"
                         or "array" in (_props[k].get("type") or []))
                            and v is None):
                        kwargs[k] = []

                response = await server.call_tool(tool_def.name, arguments=kwargs or None)
                if isinstance(response, list):
                    return response
                if hasattr(response, "content") and response.content:
                    text = response.content[0].text
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return text
                return response

            # Build signature from schema
            params = [
                inspect.Parameter("context", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=RunContext)
            ]
            ann = {"context": RunContext}

            for name, ps in _props.items():
                default = ps.get("default", inspect._empty if name in required else None)
                params.append(
                    inspect.Parameter(
                        name,
                        inspect.Parameter.KEYWORD_ONLY,
                        annotation=_py_type(ps),
                        default=default,
                    )
                )
                ann[name] = _py_type(ps)

            proxy.__signature__ = inspect.Signature(params)
            proxy.__annotations__ = ann
            proxy.__name__ = tool_def.name
            proxy.__doc__ = schema_to_google_docstring(tool_def.description or "", _schema)
            return function_tool(proxy)

        tools.append(make_proxy())

    return tools


async def entrypoint(ctx: JobContext) -> None:
    """
    Main entrypoint for the LiveKit agent.
    """
    await ctx.connect()
    server = MCPServerStdio(
        "npx",
        args=["-y", "@supabase/mcp-server-supabase@latest", "--access-token", SUPABASE_TOKEN],
    )
    await server.__aenter__()

    try:
        supabase_tools = await build_livekit_tools(server)
        tools = [firecrawl_search] + supabase_tools

        agent = Agent(
            instructions=(
                "You can either perform live web searches via `firecrawl_search` or "
                "database queries via Supabase MCP tools. "
                "Choose the appropriate tool based on whether the user needs fresh web data "
                "(news, external facts) or internal Supabase data."
            ),
            tools=tools,
        )

        session = AgentSession(
            vad=silero.VAD.load(min_silence_duration=0.1),
            stt=assemblyai.STT(word_boost=["Supabase"]),
            llm=openai.LLM(model="gpt-4o"),
            tts=openai.TTS(voice="ash"),
        )

        await session.start(agent=agent, room=ctx.room)
        await session.generate_reply(instructions="Hello! How can I assist you today?")

        # Keep the session alive until cancelled
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Session cancelled, shutting down.")

    finally:
        await server.__aexit__(None, None, None)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
