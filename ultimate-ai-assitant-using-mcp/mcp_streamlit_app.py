import streamlit as st
import asyncio
import os
import json
from dotenv import load_dotenv
# from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import mcp_use
import warnings
import base64

# Suppress warnings
warnings.filterwarnings("ignore")
mcp_use.set_debug(0)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MCP-powered Perplexity Clone",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None

if "agent" not in st.session_state:
    st.session_state.agent = None

def reset_chat():
    st.session_state.messages = []
    st.session_state.mcp_client = None
    st.session_state.agent = None

def create_mcp_client(config_dict):
    """Create MCPClient from configuration dictionary."""
    try:
        client = MCPClient.from_dict(config_dict)
        return client
    except Exception as e:
        st.error(f"Error creating MCP client: {str(e)}")
        return None

def create_agent(client):
    """Create MCPAgent with the client."""
    try:
        # Create LLM - you can switch between Ollama and OpenAI
        llm = ChatOpenAI(model="gpt-4o")
        # llm = ChatOllama(model="qwen3:1.7b")
        
        agent = MCPAgent(llm=llm, client=client, max_steps=100)
        return agent
    except Exception as e:
        st.error(f"Error creating agent: {str(e)}")
        return None

async def run_agent_query(agent, query):
    """Run a query through the MCP agent."""
    try:
        result = await agent.run(query)
        return result
    except Exception as e:
        return f"Error running query: {str(e)}"

# Main title
st.markdown("""
    # 100% local Ultimate AI Assistant using mcp-use
""", unsafe_allow_html=True)

st.markdown("Configure your MCP servers and chat with them using natural language!")

# Sidebar for configuration
with st.sidebar:
    st.header("MCP Configuration")
    
    # Configuration text area
    config_text = st.text_area(
        "Enter MCP Configuration (JSON)",
        height=400,
        placeholder='''{
  "mcpServers": {
    "stagehand": {
      "command": "node",
      "args": ["/path/to/mcp-server-browserbase/stagehand/dist/index.js"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "LOCAL_CDP_URL": "http://localhost:9222"
      }
    }
  }
}''',
        help="Enter your MCP server configuration in JSON format"
    )
    
    # Load example configuration
    if st.button("Load Example Config"):
        example_config = {
            "mcpServers": {
                "stagehand": {
                    "command": "node",
                    "args": ["/path/to/mcp-server-browserbase/stagehand/dist/index.js"],
                    "env": {
                        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                        "LOCAL_CDP_URL": "http://localhost:9222",
                        "DOWNLOADS_DIR": "/path/to/downloads/stagehand"
                    }
                },
                "mcp-server-firecrawl": {
                    "command": "npx",
                    "args": ["-y", "firecrawl-mcp"],
                    "env": {
                        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")
                    }
                },
                "ragie": {
                    "command": "npx",
                    "args": ["-y", "@ragieai/mcp-server", "--partition", "default"],
                    "env": {
                        "RAGIE_API_KEY": os.getenv("RAGIE_API_KEY")
                    }
                }
            }
        }
        st.session_state.example_config = json.dumps(example_config, indent=2)
        st.rerun()
    
    # Display example config if loaded
    if 'example_config' in st.session_state:
        st.text_area("Example Configuration", st.session_state.example_config, height=200, disabled=True)
    
    st.divider()
    
    # Activate configuration button
    if st.button("Activate Configuration", type="primary"):
        if config_text.strip():
            try:
                # Parse JSON configuration
                config_dict = json.loads(config_text)
                
                # Create MCP client
                client = create_mcp_client(config_dict)
                if client:
                    st.session_state.mcp_client = client
                    
                    # Create agent
                    agent = create_agent(client)
                    if agent:
                        st.session_state.agent = agent
                        st.success("✅ Configuration activated successfully!")
                        
                        # Show available tools
                        try:
                            tools_info = "Available MCP tools:\n"
                            for server_name, server_info in config_dict.get("mcpServers", {}).items():
                                tools_info += f"- {server_name}\n"
                            st.info(tools_info)
                        except Exception as e:
                            st.warning(f"Could not display tools info: {str(e)}")
                    else:
                        st.error("Failed to create agent")
                else:
                    st.error("Failed to create MCP client")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON configuration: {str(e)}")
            except Exception as e:
                st.error(f"Error activating configuration: {str(e)}")
        else:
            st.warning("Please enter a configuration first")
    
    # Clear button
    if st.button("Clear Chat & Config"):
        reset_chat()
        st.rerun()
    
    # Status indicator
    st.divider()
    st.subheader("Status")
    if st.session_state.mcp_client and st.session_state.agent:
        st.success("✅ MCP Client Active")
        st.success("✅ Agent Ready")
    else:
        st.warning("⚠️ Configuration not activated")

# Main chat interface


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your MCP tools..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if agent is available
    if not st.session_state.agent:
        with st.chat_message("assistant"):
            st.error("Please activate the MCP configuration first!")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    # Run the query asynchronously
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(run_agent_query(st.session_state.agent, prompt))
                    loop.close()
                    
                    # Display result
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("Built using mcp-use and Streamlit") 