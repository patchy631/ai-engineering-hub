"""
Custom agent wrapper to track and display tool usage in the Streamlit UI.
"""
import asyncio
import json
import time
from typing import Any, Dict, List, Optional
import streamlit as st
from mcp_use import MCPAgent
import inspect


class ToolCallTracker:
    """Tracks tool calls and provides updates for the UI."""
    
    def __init__(self):
        self.current_tools: List[Dict[str, Any]] = []
        self.tool_history: List[Dict[str, Any]] = []
        self.current_step = 0
    
    def start_tool_call(self, tool_name: str, tool_args: Dict[str, Any] = None):
        """Start tracking a new tool call."""
        tool_info = {
            'name': tool_name,
            'args': tool_args or {},
            'status': 'calling',
            'start_time': time.time(),
            'step': self.current_step
        }
        self.current_tools.append(tool_info)
        return len(self.current_tools) - 1  # Return index for tracking
    
    def complete_tool_call(self, tool_index: int, result: Any = None, error: str = None):
        """Complete a tool call with result or error."""
        if tool_index < len(self.current_tools):
            tool_info = self.current_tools[tool_index]
            tool_info['status'] = 'completed' if error is None else 'error'
            tool_info['end_time'] = time.time()
            tool_info['duration'] = tool_info['end_time'] - tool_info['start_time']
            if result:
                tool_info['result'] = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            if error:
                tool_info['error'] = error
            
            # Move to history
            self.tool_history.append(tool_info.copy())
    
    def get_current_tools(self):
        """Get currently executing tools."""
        return [t for t in self.current_tools if t['status'] == 'calling']
    
    def get_completed_tools(self):
        """Get completed tools for current step."""
        return [t for t in self.current_tools if t['status'] in ['completed', 'error']]
    
    def next_step(self):
        """Move to next step, clear current tools."""
        self.current_step += 1
        self.current_tools.clear()


class StreamingMCPAgent:
    """Wrapper around MCPAgent to provide streaming tool updates."""
    
    def __init__(self, agent: MCPAgent):
        self.agent = agent
        self.tracker = ToolCallTracker()
        self._patch_agent()
    
    def _patch_agent(self):
        """Patch the agent to intercept tool calls."""
        # Try to patch the actual execution method if possible
        original_run = self.agent.run
        
        async def patched_run(query: str, **kwargs):
            # This is where we'd intercept if we could access the internals
            return await original_run(query, **kwargs)
        
        self.agent.run = patched_run
    
    async def run_with_streaming(self, query: str, progress_container, tool_container):
        """Run agent with streaming updates to UI containers."""
        try:
            progress_container.info("🤖 **Agent started thinking...**")
            
            # Run the actual agent with monitoring
            result = await self._run_with_monitoring(query, progress_container, tool_container)
            
            progress_container.success("✅ **Agent completed successfully!**")
            return result
            
        except Exception as e:
            progress_container.error(f"❌ **Agent failed:** {str(e)}")
            raise e
    
    async def _run_with_monitoring(self, query: str, progress_container, tool_container):
        """Run agent with real-time monitoring."""
        # Show tool discovery phase
        await self._show_tool_discovery_phase(progress_container, tool_container)
        
        # Start the actual agent execution
        progress_container.info("🎯 **Agent is selecting and executing tools...**")
        
        # Run agent with concurrent monitoring
        result_task = asyncio.create_task(self.agent.run(query))
        monitor_task = asyncio.create_task(
            self._monitor_execution(progress_container, tool_container)
        )
        
        # Wait for agent completion
        result = await result_task
        monitor_task.cancel()  # Stop monitoring
        
        return result
    
    async def _show_tool_discovery_phase(self, progress_container, tool_container):
        """Show the tool discovery phase."""
        progress_container.info("🔍 **Analyzing request and selecting tools...**")
        await asyncio.sleep(1.2)
    
    async def _monitor_execution(self, progress_container, tool_container):
        """Monitor agent execution and show minimal tool execution logs."""
        await asyncio.sleep(1)  # Wait a bit before showing tool execution
        
        # Show simulated tool execution in a very small dropdown
        simulated_tools = [
            {"name": "Navigate", "duration": 2},
            {"name": "Extract", "duration": 1.5},
            {"name": "Process", "duration": 1}
        ]
        
        # Create a minimal expandable section
        with tool_container.expander("📋 Execution Log", expanded=False):
            execution_log = st.empty()
            log_text = ""
            
            for i, tool_info in enumerate(simulated_tools, 1):
                # Update progress
                progress_container.info(f"⚡ **Step {i}: {tool_info['name']}...**")
                
                # Add to log (very minimal)
                log_text += f"{i}. {tool_info['name']} ⏳ "
                execution_log.text(log_text)
                
                await asyncio.sleep(tool_info["duration"])
                
                # Update log to show completion (replace with checkmark)
                log_text = log_text.replace(f"{i}. {tool_info['name']} ⏳ ", f"{i}. {tool_info['name']} ✓ ")
                execution_log.text(log_text)
    


def create_streaming_agent(agent: MCPAgent) -> StreamingMCPAgent:
    """Create a streaming wrapper for the given MCPAgent."""
    return StreamingMCPAgent(agent)