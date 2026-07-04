import json
import time
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.zep_service import zep_service
from services.llm_service import llm_service
from config.settings import settings


# -------------------------------
# Pydantic Models
# -------------------------------

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class SessionCreateRequest(BaseModel):
    user_id: str
    first_name: Optional[str] = "Demo"
    last_name: Optional[str] = None
    email: Optional[str] = None


# -------------------------------
# FastAPI App
# -------------------------------

app = FastAPI(
    title="Zep + LLM Backend for Anam",
    description="FastAPI backend that integrates Zep Cloud KG + your LLM for Anam avatar.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# -------------------------------
# Health & Debug Endpoints
# -------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/zep/test-graph")
async def test_graph(q: str = Query("what is Zep?")):
    """
    Simple debug endpoint to verify Zep graph connectivity.
    """
    try:
        nodes = await zep_service.search_graph(
            query=q,
            user_id=settings.zep_docs_user_id,
            limit=3,
            scope="nodes",
        )
        return {"query": q, "results": nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Zep Session Helper Endpoint
# -------------------------------

@app.post("/zep/session")
async def create_zep_session(body: SessionCreateRequest):
    """
    Helper endpoint to create a Zep user + thread (session) for a given user_id.
    You can call this from Streamlit or any client instead of doing it inline.
    """
    try:
        user = await zep_service.create_user(
            user_id=body.user_id,
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
        )

        # 2) Create thread for this user
        session_id = f"session-{body.user_id}"
        thread = await zep_service.create_thread(
            thread_id=session_id,
            user_id=body.user_id,
        )

        return {
            "user": user,
            "thread": thread,
            "session_id": session_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Core: LLM Stream Endpoint for Anam
# -------------------------------

@app.post("/llm/stream")
async def llm_stream(
    payload: ChatRequest,
    session_id: str = Query(..., description="Zep thread/session ID"),
):
    """
    Streaming LLM endpoint with Zep KG integration.
    This is what Anam's customLLMHandler() should call.

    - Expects: JSON body { "messages": [ { "role": "...", "content": "..." }, ... ] }
    - Requires: ?session_id=... query param (thread_id in Zep)
    - Returns: SSE stream with chunks as { "text": "<token or chunk>" }
    """

    messages: List[Message] = payload.messages

    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    # Extract latest user message
    user_message: Optional[str] = None
    for m in reversed(messages):
        if m.role == "user":
            user_message = m.content
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    async def event_generator():
        """
        Async generator that:
        1) Saves the user message to Zep
        2) Queries the Zep Knowledge Graph for docs context
        3) Gets conversation context from Zep
        4) Calls your LLM in streaming mode
        5) Yields SSE 'data: { "text": ... }' lines to the client
        6) Saves the final assistant message back into Zep
        """
        full_response: str = ""

        try:
            print(f"\n{'='*60}")
            print(f"NEW USER MESSAGE for session: {session_id}")
            print(f"Message: {user_message}")
            print(f"{'='*60}")

            # 1) Save user message into Zep thread
            await zep_service.add_message(
                thread_id=session_id,
                role="user",
                content=user_message,
            )
            print("User message saved to Zep thread")

            # 2) Build base system prompt
            system_prompt = """
You are a helpful AI assistant. When provided with relevant information or context below, 
use it to answer the user's question accurately and completely. Always use the information 
provided to give thorough, detailed answers. Be conversational and friendly while being informative.
If the context contains the answer, state it clearly and add relevant details from the context.
""".strip()

            # 3) Zep Knowledge Graph lookup
            print(f"\nQUERYING KNOWLEDGE GRAPH...")
            print(f"   Query: '{user_message}'")
            print(f"   User ID: {settings.zep_docs_user_id}")

            graph_start_time = time.time()
            graph_results = await zep_service.search_graph(
                query=user_message,
                user_id=settings.zep_docs_user_id,
                limit=3,
                scope="nodes",
            )
            graph_end_time = time.time()
            # Convert to milliseconds
            graph_duration = (graph_end_time - graph_start_time) * 1000

            print(
                f"\nKNOWLEDGE GRAPH RESULTS: {len(graph_results)} nodes found")
            print(f"Fetch time: {graph_duration:.2f}ms")

            if graph_results:
                print(f"\nRetrieved nodes:")
                for i, node in enumerate(graph_results, 1):
                    print(f"   {i}. {node.get('name', 'N/A')}")
                    summary_preview = node.get('summary', '')[:100]
                    print(f"      Summary: {summary_preview}...")

                docs_context = "\n\n".join(
                    [f"- {node['name']}: {node['summary']}" for node in graph_results]
                )
                system_prompt += f"\n\n=== RELEVANT INFORMATION ===\n{docs_context}\n\nUse the above information to answer the user's question."
                print(
                    f"\nGRAPH CONTEXT ADDED TO PROMPT: {len(docs_context)} characters")
            else:
                print(
                    f"\nNO GRAPH RESULTS FOUND - LLM will respond without context")

            # 4) Conversation context from this thread
            print(f"\nFETCHING USER CONTEXT for thread: {session_id}")
            user_context = await zep_service.get_user_context(thread_id=session_id)
            if user_context:
                system_prompt += f"\n\n=== CONVERSATION CONTEXT ===\n{user_context}"
                print(f"USER CONTEXT ADDED: {len(user_context)} characters")
            else:
                print(f"No user context available yet (new conversation)")

            # 5) Reformat messages for LLM
            formatted_messages: List[Dict[str, Any]] = [
                {"role": m.role, "content": m.content} for m in messages
            ]

            # 6) Stream from LLM and send SSE chunks
            print(f"\nSTREAMING LLM RESPONSE...")
            print(f"   Total prompt size: {len(system_prompt)} characters")

            chunk_count = 0
            async for chunk in llm_service.stream_chat_completion(
                messages=formatted_messages,
                system_prompt=system_prompt,
            ):
                if not chunk:
                    continue

                chunk_count += 1
                full_response += chunk
                payload = json.dumps({"content": chunk})
                yield f"data: {payload}\n\n"

                if chunk_count % 10 == 0:
                    print(f"   Streamed {chunk_count} chunks so far...")

            print(f"   Total chunks streamed: {chunk_count}")

            # 7) Save assistant message in Zep
            if full_response.strip():
                await zep_service.add_message(
                    thread_id=session_id,
                    role="assistant",
                    content=full_response,
                )
                print(
                    f"\nASSISTANT RESPONSE SAVED: {len(full_response)} characters")
                print(f"{'='*60}\n")

        except Exception as e:
            # On error, stream an error message as SSE
            err_payload = json.dumps({"content": "Error: " + str(e)})
            yield f"data: {err_payload}\n\n"

    # Return a streaming SSE response
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
