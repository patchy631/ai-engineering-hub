import os
import json
import asyncio
import base64
import time
import warnings

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import mcp_use

from styles import inject_css
from agent_wrapper import create_streaming_agent

warnings.filterwarnings("ignore")
load_dotenv()
if os.getenv("DEBUG_MCP", "0") == "1":
    mcp_use.set_debug(1)

st.set_page_config(page_title="Stagehand × mcp-use", page_icon="🕹️", layout="wide")
inject_css()

SAMPLE_CONFIG_STR = """{
  "mcpServers": {
    "stagehand": {
      "command": "python",
      "args": ["stagehand_mcp.py"]
    }
  }
}"""

st.session_state.setdefault("client", None)
st.session_state.setdefault("agent", None)
st.session_state.setdefault("activated", False)
st.session_state.setdefault("tools", [])
st.session_state.setdefault("config_json", "")
st.session_state.setdefault("messages", [])  # [{role, content}]


async def _activate(cfg_dict: dict):
    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(cfg_dict)
    
    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")
    
    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)
    
    return client, [], agent




def handle_activate():
    try:
        cfg = json.loads(st.session_state.config_json)
        client, tools, agent = asyncio.run(_activate(cfg))
        st.session_state.client = client
        st.session_state.tools = tools
        st.session_state.agent = agent
        st.session_state.activated = True
        st.sidebar.success("✅ MCP Configuration activated successfully!")
    except json.JSONDecodeError as e:
        st.session_state.client = None
        st.session_state.tools = []
        st.session_state.agent = None
        st.session_state.activated = False
        st.sidebar.error(f"Invalid JSON configuration: {e}")
    except Exception as e:
        st.session_state.client = None
        st.session_state.tools = []
        st.session_state.agent = None
        st.session_state.activated = False
        st.sidebar.error(f"Failed to activate configuration: {e}")

def handle_clear():
    st.session_state.update(client=None, agent=None, tools=[], activated=False, messages=[])

def _file_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def _render_hero():
    try:
        mu_b64 = _file_b64(os.path.join("assets", "mcp-use.png"))
    except Exception:
        mu_b64 = ""
    st.markdown(
        f"""
        <div class="hero">
          <h1>100% Local MCP Client</h1>
          <p class="subtitle">
            Powered by <img src="data:image/png;base64,{mu_b64}" alt="mcp-use" class="inline-logo" />
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _looks_transient(err_msg: str) -> bool:
    if not err_msg:
        return False
    t = err_msg.lower()
    return ("no session found" in t) or ("429" in t) or ("rate limit" in t) or ("failed to create browserbase session" in t)

def run_agent(agent, prompt) -> str:
    try:
        return asyncio.run(agent.run(prompt)) or "(no response)"
    except Exception as e:
        return f"⚠️ MCP/Agent error: {e}"

async def run_streaming_agent(streaming_agent, prompt, progress_container, tool_container):
    """Run agent with streaming tool updates."""
    try:
        result = await streaming_agent.run_with_streaming(prompt, progress_container, tool_container)
        return result or "(no response)"
    except Exception as e:
        return f"⚠️ MCP/Agent error: {e}"

with st.sidebar:
    st.markdown("## MCP Configuration")
    st.caption("Paste your MCP configuration JSON below")
    st.text_area("MCP Configuration JSON", key="config_json", height=300, placeholder=SAMPLE_CONFIG_STR, label_visibility="collapsed")
    st.button("🚀 Activate Configuration", on_click=handle_activate, type="primary")
    st.button("🧹 Clear All", on_click=handle_clear)

    st.divider()
    if st.session_state.activated:
        st.success("✅ MCP Client Active")
        st.success("✅ Agent Ready")

_render_hero()

# History (static)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Current turn with enhanced tool display
user_input = st.chat_input("Enter your message...")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # Create containers for different parts of the response
        progress_container = st.empty()
        tool_container = st.container()
        result_container = st.empty()
        
        if not (st.session_state.activated and st.session_state.agent):
            result_container.markdown("Please activate the configuration first.")
            assistant_text = "Please activate the configuration first."
        else:
            # Create streaming agent wrapper
            streaming_agent = create_streaming_agent(st.session_state.agent)
            
            # Show initial thinking state
            result_container.markdown('<div class="bubble-opaque">&nbsp;</div>', unsafe_allow_html=True)
            
            # Run with streaming updates
            try:
                assistant_text = asyncio.run(
                    run_streaming_agent(streaming_agent, user_input, progress_container, tool_container)
                )
            except Exception as e:
                assistant_text = f"⚠️ Error running agent: {e}"
                progress_container.error(f"❌ **Agent failed:** {str(e)}")
            
            # Show final result
            result_container.markdown(assistant_text, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
