"""Parlant client utilities for demo communication."""
import parlant.sdk as p
from parlant.client import AsyncParlantClient
from typing import Optional
import asyncio
import os


async def create_client(base_url: str = "") -> AsyncParlantClient:
    """Create a Parlant client connection."""
    resolved_base_url = base_url or os.getenv("PARLANT_BASE_URL", "http://127.0.0.1:8800")
    return AsyncParlantClient(base_url=resolved_base_url)


async def create_session(client: AsyncParlantClient, agent_id: str, retries: int = 20, delay: float = 0.6) -> str:
    """Create a new Parlant session with retry logic."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            session = await client.sessions.create(agent_id=agent_id)
            return session.id if hasattr(session, "id") else session["id"]
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(delay)
            delay = min(3.0, delay * 1.5)
    base_url = getattr(client, "_base_url", None) or os.getenv("PARLANT_BASE_URL", "http://127.0.0.1:8800")
    raise last_exc or RuntimeError(f"Failed to create session after {retries} attempts (server at {base_url}?).")


async def send_user_message(client: AsyncParlantClient, session_id: str, message: str) -> int:
    """Send a user message to the Parlant session."""
    event = await client.sessions.create_event(
        session_id=session_id,
        kind="message",
        source="customer",
        message=message,
    )
    return event.offset


async def await_ai_reply(client: AsyncParlantClient, session_id: str, min_offset: int) -> Optional[str]:
    """Wait for and collect all AI agent messages from a Parlant session."""
    all_messages = []
    current_offset = min_offset
    max_polls = 3
    
    for poll_count in range(max_polls):
        try:
            events = await client.sessions.list_events(
                session_id=session_id,
                kinds="message",
                min_offset=current_offset,
                wait_for_data=45,
            )
        except Exception as e:
            if "timeout" in str(e).lower() or "504" in str(e):
                break
            raise
        
        new_messages = []
        max_offset = current_offset - 1
        
        for event in events:
            if event.source == "ai_agent" and event.kind == "message":
                if isinstance(event.data, dict) and event.data.get("message"):
                    new_messages.append(event.data.get("message"))
                    max_offset = max(max_offset, event.offset)
        
        if new_messages:
            all_messages.extend(new_messages)
            current_offset = max_offset + 1
        else:
            break
    
    return "\n\n".join(all_messages) if all_messages else None


async def get_session_reasoning(client: AsyncParlantClient, session_id: str, min_offset: int = 0) -> str:
    """Summarize which guidelines and tools the agent used for this session."""
    guidelines: list[str] = []
    tools_used: list[str] = []
    guideline_details: list[str] = []

    # Get session state for applied guidelines
    try:
        session_info = await client.sessions.retrieve(session_id=session_id)
        agent_states = getattr(session_info, "agent_states", None) or []
        for state in agent_states:
            ids = getattr(state, "applied_guideline_ids", None) or []
            for gid in ids:
                if gid not in guidelines:
                    guidelines.append(gid)
    except Exception:
        pass

    # Scan events for tool calls and guideline details
    try:
        events = await client.sessions.list_events(
            session_id=session_id,
            min_offset=0,
            wait_for_data=0,
        )
        
        for ev in events:
            # Extract guidelines from status events
            if ev.kind == "status" and isinstance(ev.data, dict):
                applied = ev.data.get("applied_guidelines")
                if isinstance(applied, list):
                    for g in applied:
                        if isinstance(g, dict):
                            name = g.get("name")
                            condition = g.get("condition", "")
                            action = g.get("action", "")
                            if name and name not in guidelines:
                                guidelines.append(name)
                            if condition and action:
                                guideline_details.append(f"{name}: {condition} -> {action[:50]}...")
                
                guideline_matches = ev.data.get("guideline_matches")
                if isinstance(guideline_matches, list):
                    for match in guideline_matches:
                        if isinstance(match, dict):
                            gid = match.get("guideline_id")
                            condition = match.get("condition", "")
                            action = match.get("action", "")
                            if gid and gid not in guidelines:
                                guidelines.append(gid)
                            if condition and action:
                                guideline_details.append(f"{gid}: {condition} -> {action[:50]}...")
            
            # Extract tools from tool events
            if ev.kind == "tool" and isinstance(ev.data, dict):
                tool_calls = ev.data.get("tool_calls")
                if isinstance(tool_calls, list):
                    for tool_call in tool_calls:
                        if isinstance(tool_call, dict):
                            name = tool_call.get("tool_id") or tool_call.get("name") or tool_call.get("function", {}).get("name")
                            if name and name not in tools_used:
                                tools_used.append(name)
            
            if ev.kind in ("tool_call", "tool"):
                data = ev.data if isinstance(ev.data, dict) else {}
                name = (
                    data.get("name")
                    or data.get("tool_name")
                    or ((data.get("tool") or {}).get("name") if isinstance(data.get("tool"), dict) else None)
                    or ((data.get("result") or {}).get("tool_name") if isinstance(data.get("result"), dict) else None)
                )
                if name and name not in tools_used:
                    tools_used.append(name)
            
            if ev.kind == "message" and isinstance(ev.data, dict):
                meta = ev.data.get("meta") or {}
                tool = meta.get("tool_name")
                if tool and tool not in tools_used:
                    tools_used.append(tool)
    except Exception:
        pass

    parts: list[str] = []
    
    # Add guidelines if available
    if guideline_details:
        parts.append(f"Guidelines: {'; '.join(guideline_details)}")
    elif guidelines:
        parts.append(f"Guidelines: {', '.join(guidelines)}")
    
    # Infer guidelines from tool usage (following Parlant's design)
    if tools_used and not guideline_details and not guidelines:
        if any("agent_contact" in tool for tool in tools_used):
            parts.append("Guidelines: Policy replacement guideline applied")
        elif any("coverage" in tool for tool in tools_used):
            parts.append("Guidelines: Coverage calculation guideline applied")
        elif any("health" in tool for tool in tools_used):
            parts.append("Guidelines: Health impact assessment guideline applied")
        elif any("application" in tool for tool in tools_used):
            parts.append("Guidelines: Application process guideline applied")
        else:
            parts.append("Guidelines: Structured response guideline applied")
    
    if tools_used:
        parts.append(f"Tools: {', '.join(tools_used)}")
    
    if not guideline_details and not guidelines and not tools_used:
        parts.append("(no tools/guidelines recorded in session data)")
    
    return " | ".join(parts) if parts else "(no explicit tools/guidelines recorded)"




