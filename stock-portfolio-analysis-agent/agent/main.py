# ===============================================================================
# IMPORTS AND SETUP
# ===============================================================================

# FastAPI framework for building the web API
from fastapi import FastAPI
from fastapi.responses import StreamingResponse  # For streaming real-time responses to client

# Standard Python libraries
import uuid  
from typing import Any  
import os  
import uvicorn  
import asyncio  

# AG UI core components for agent communication and event handling
from ag_ui.core import (
    RunAgentInput,           
    StateSnapshotEvent,      
    EventType,               
    RunStartedEvent,        
    RunFinishedEvent,        
    TextMessageStartEvent,   
    TextMessageEndEvent,     
    TextMessageContentEvent, 
    ToolCallStartEvent,      
    ToolCallEndEvent,        
    ToolCallArgsEvent,       
    StateDeltaEvent          
)
from ag_ui.encoder import EventEncoder  # Encoder for converting events to streamable format

# Import our custom stock analysis workflow
from stock_analysis import StockAnalysisFlow

# CopilotKit state management
from copilotkit import CopilotKitState

# ===============================================================================
# APPLICATION SETUP
# ===============================================================================

# Initialize FastAPI application instance
app = FastAPI()


# ===============================================================================
# STATE MANAGEMENT
# ===============================================================================

class AgentState(CopilotKitState):
    """
    Agent state class that manages the data throughout the stock analysis workflow.
    
    This class extends CopilotKitState to provide structured state management
    for the stock analysis agent. It tracks:
    - Tool configurations and message history
    - Stock data and analysis arguments
    - Financial information (cash, investments, summaries)
    - UI interaction logs
    
    Inherits from CopilotKitState (which extends langgraph's MessagesState)
    """

    tools: list                    
    messages: list                 
    be_stock_data: Any            
    be_arguments: dict            
    available_cash: int           
    investment_summary: dict      
    tool_logs: list              

# ===============================================================================
# MAIN API ENDPOINT
# ===============================================================================

@app.post("/crewai-agent")
async def crewai_agent(input_data: RunAgentInput):
    """
    Main API endpoint for processing stock analysis requests.
    
    This endpoint:
    1. Receives user input and current state from the frontend
    2. Streams real-time events back to the client during processing
    3. Runs the StockAnalysisFlow workflow asynchronously
    4. Returns results via Server-Sent Events (SSE) streaming
    
    Args:
        input_data (RunAgentInput): Contains user messages, tools, state, thread/run IDs
        
    Returns:
        StreamingResponse: Real-time stream of events during agent execution
    """
    try:

        async def event_generator():
            """
            Asynchronous generator that streams events to the client in real-time.
            
            This function orchestrates the entire stock analysis workflow:
            1. Sets up event streaming infrastructure
            2. Emits initial state and run started events
            3. Launches the StockAnalysisFlow workflow
            4. Streams progress events as they occur
            5. Handles final results (tool calls or text messages)
            6. Emits run completion events
            
            Yields:
                Encoded events for Server-Sent Events (SSE) streaming
            """
            # Step 1: Initialize event streaming infrastructure
            encoder = EventEncoder()  # Converts events to SSE format
            event_queue = asyncio.Queue()  # Queue for events from the workflow

            def emit_event(event):
                """Callback function for the workflow to emit events"""
                event_queue.put_nowait(event)

            # Generate unique identifier for text messages
            # Generate unique identifier for text messages
            message_id = str(uuid.uuid4())

            # Step 2: Emit run started event to notify client that processing has begun
            yield encoder.encode(
                RunStartedEvent(
                    type=EventType.RUN_STARTED,
                    thread_id=input_data.thread_id,  # Conversation thread identifier
                    run_id=input_data.run_id,        # Unique run identifier
                )
            )

            # Step 3: Send initial state snapshot to client
            # This provides the client with current financial state before analysis
            yield encoder.encode(
                StateSnapshotEvent(
                    type=EventType.STATE_SNAPSHOT, 
                    snapshot={
                        "available_cash": input_data.state["available_cash"],        # Current cash balance
                        "investment_summary": input_data.state["investment_summary"], # Previous analysis results
                        "investment_portfolio": input_data.state["investment_portfolio"], # Current holdings
                        "tool_logs": []  # Reset tool logs for new analysis
                    }
                )
            )
            
            # Step 4: Initialize agent state with input data
            state = AgentState(
                tools=input_data.tools,                                      # Available tools
                messages=input_data.messages,                                # Conversation history
                be_stock_data=None,                                         # Will be populated during analysis
                be_arguments=None,                                          # Will be populated during analysis
                available_cash=input_data.state["available_cash"],          # Current cash
                investment_portfolio=input_data.state["investment_portfolio"], # Current portfolio
                tool_logs=[]                                                # Progress tracking
            )
            
            # Step 5: Launch the stock analysis workflow asynchronously
            # This creates a task that runs the StockAnalysisFlow in the background
            agent_task = asyncio.create_task(
                StockAnalysisFlow().kickoff_async(inputs={
                    "state": state,                                          # Agent state
                    "emit_event": emit_event,                               # Event emission callback
                    "investment_portfolio": input_data.state["investment_portfolio"]  # Portfolio data
                })
            )
            
            # Step 6: Event streaming loop - relay events from workflow to client
            chart_data_sent = False  # Track if chart data has been sent
            while True:
                try:
                    # Try to get an event from the queue with a short timeout
                    event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                    
                    # Only stream events that are NOT from the insights stage to prevent flickering
                    # Skip events that might interfere with the completed chart
                    should_stream = True
                    
                    # Check if this is a tool log completion event (indicates allocation stage done)
                    if (hasattr(event, 'delta') and event.delta and 
                        isinstance(event.delta, list) and len(event.delta) > 0 and
                        event.delta[0].get('path') == '/tool_logs' and
                        event.delta[0].get('op') == 'replace' and
                        event.delta[0].get('value') == 'completed'):
                        chart_data_sent = True
                        # Don't stop streaming yet - let the chart data go through first
                    
                    # Check if this is the actual chart tool call being sent
                    if (hasattr(event, 'type') and event.type == EventType.TOOL_CALL_ARGS and
                        hasattr(event, 'delta') and 'render_standard_charts_and_table' in str(event.delta)):
                        # This is the chart data being sent - mark it and allow it through
                        chart_data_sent = True
                        should_stream = True
                    
                    # After chart data is sent, block insights-related events but allow portfolio updates
                    if chart_data_sent and (hasattr(event, 'delta') and event.delta and 
                        isinstance(event.delta, list) and len(event.delta) > 0):
                        # Allow portfolio updates to go through
                        if event.delta[0].get('path') == '/investment_portfolio':
                            should_stream = True
                        # Block insights-related events
                        elif ('insights' in str(event.delta[0]).lower() or 
                              'processing' in str(event.delta[0]).lower() or
                              'extracting' in str(event.delta[0]).lower()):
                            should_stream = False
                    
                    if should_stream:
                        yield encoder.encode(event)  # Stream the event to client
                        
                except asyncio.TimeoutError:
                    # No events in queue - check if workflow is complete
                    if agent_task.done():
                        break  # Exit loop when workflow finishes
                    
                    # If chart data has been sent and workflow is still running (insights stage),
                    # we can break early to make graph interactive while insights generate
                    if chart_data_sent and not agent_task.done():
                        # Minimal delay to ensure chart data is fully processed
                        await asyncio.sleep(0.2)
                        break  # Exit early to make graph interactive

            # Step 7: Clear tool logs after workflow completion
            # This prevents old progress logs from cluttering the UI
            yield encoder.encode(
            StateDeltaEvent(
                type=EventType.STATE_DELTA,
                delta=[
                    {
                        "op": "replace",
                        "path": "/tool_logs",
                        "value": []
                    }
                ]
            )
            )
            
            # Step 8: Handle workflow results based on the final message type
            # Check if the last message is from the assistant (AI agent)
            if state["messages"][-1].role == "assistant":
                
                # Step 8.1: Handle tool call results (charts, data visualizations)
                if state["messages"][-1].tool_calls:
                    # The workflow generated a tool call (e.g., render charts)
                    # Stream tool call events to trigger UI rendering
                    
                    yield encoder.encode(
                        ToolCallStartEvent(
                            type=EventType.TOOL_CALL_START,
                            tool_call_id=state["messages"][-1].tool_calls[0].id,
                            toolCallName=state["messages"][-1]
                            .tool_calls[0]
                            .function.name,
                        )
                    )

                    # Stream the tool call arguments (contains analysis results)
                    yield encoder.encode(
                        ToolCallArgsEvent(
                            type=EventType.TOOL_CALL_ARGS,
                            tool_call_id=state["messages"][-1].tool_calls[0].id,
                            delta=state["messages"][-1]
                            .tool_calls[0]
                            .function.arguments,  # Contains investment summary and insights
                        )
                    )

                    # Signal end of tool call
                    yield encoder.encode(
                        ToolCallEndEvent(
                            type=EventType.TOOL_CALL_END,
                            tool_call_id=state["messages"][-1].tool_calls[0].id,
                        )
                    )
                else:
                    # Step 8.2: Handle text message results (when no analysis was performed)
                    yield encoder.encode(
                        TextMessageStartEvent(
                            type=EventType.TEXT_MESSAGE_START,
                            message_id=message_id,
                            role="assistant",
                        )
                    )

                    # Step 8.2.1: Stream text content if available
                    if state["messages"][-1].content:
                        content = state["messages"][-1].content
                        
                        # Split content into chunks for smooth streaming effect
                        n_parts = 100  # Number of chunks for streaming
                        part_length = max(1, len(content) // n_parts)
                        parts = [content[i:i+part_length] for i in range(0, len(content), part_length)]
                        
                        # Ensure we don't exceed the target number of parts
                        if len(parts) > n_parts:
                            parts = parts[:n_parts-1] + [''.join(parts[n_parts-1:])]
                            
                        # Stream each part with a small delay for smooth typing effect
                        for part in parts:
                            yield encoder.encode(
                                TextMessageContentEvent(
                                    type=EventType.TEXT_MESSAGE_CONTENT,
                                    message_id=message_id,
                                    delta=part,  # Chunk of text content
                                )
                            )
                            await asyncio.sleep(0.05)  # Small delay for typing effect
                    else:
                        # Step 8.2.2: Handle case where no content is available (error scenario)
                        yield encoder.encode(
                            TextMessageContentEvent(
                                type=EventType.TEXT_MESSAGE_CONTENT,
                                message_id=message_id,
                                delta="Something went wrong! Please try again.",
                            )
                        )
                    
                    # Step 8.2.3: Signal end of text message
                    yield encoder.encode(
                        TextMessageEndEvent(
                            type=EventType.TEXT_MESSAGE_END,
                            message_id=message_id,
                        )
                    )

            # Step 9: Emit run finished event to signal completion
            yield encoder.encode(
                RunFinishedEvent(
                    type=EventType.RUN_FINISHED,
                    thread_id=input_data.thread_id,  # Same thread ID from start
                    run_id=input_data.run_id,        # Same run ID from start
                )
            )

    except Exception as e:
        # Step 10: Handle any unexpected errors during processing
        print(e)  # Log error for debugging

    # Step 11: Return streaming response to client
    # Step 11: Return streaming response to client
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ===============================================================================
# SERVER STARTUP AND CONFIGURATION
# ===============================================================================

def main():
    """
    Main function to start the uvicorn server.
    
    This function:
    - Reads the port from environment variables (defaults to 8000)
    - Configures uvicorn server settings
    - Starts the server with hot reload enabled for development
    """
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Start uvicorn server with configuration
    uvicorn.run(
        "main:app",           # Module and app instance
        host="0.0.0.0",      # Listen on all network interfaces
        port=port,           # Port number
        reload=True,         # Enable hot reload for development
    )


if __name__ == "__main__":
    """
    Entry point when script is run directly.
    Starts the FastAPI server using uvicorn.
    """
    main()
